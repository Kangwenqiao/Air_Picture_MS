# 导入 SQLAlchemy 中所需的模块和类
import csv
import random
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 从 'models' 模块导入模型定义（假设其中包含 ObjectDetectionResult、User 和 AircraftDetectionResult 的定义）
from models import ObjectDetectionResult, User, AircraftDetectionResult

# 创建声明性类定义的基类
Base = declarative_base()

# DatabaseUtil 类用于数据库操作
class DatabaseUtil:
    def __init__(self):
        # 设置数据库引擎，连接到 MySQL 数据库
        self.engine = create_engine('mysql+mysqlconnector://root:2003Kangwenqiao@localhost/database_base')

        # 使用 Base.metadata.create_all(self.engine) 创建定义在 Base 中的表
        Base.metadata.create_all(self.engine)

        # 创建与数据库引擎绑定的 sessionmaker，用于生成数据库会话
        self.Session = sessionmaker(bind=self.engine)

        # 利用 sessionmaker 创建新的数据库会话
        self.session = self.Session()

    # 插入或更新 ObjectDetectionResults 表
    def insert_or_update_object_detection(self, detection_data, username):
        try:
            detection_data['Username'] = username
            self.session.merge(ObjectDetectionResult(**detection_data))
            self.session.commit()
        except Exception as e:
            print(f"插入或更新 ObjectDetectionResults 时出错: {e}")

    # 插入或更新 AircraftDetectionResults 表
    def insert_or_update_aircraft_detection(self, aircraft_data, username):
        try:
            aircraft_data['Username'] = username
            self.session.merge(AircraftDetectionResult(**aircraft_data))
            self.session.commit()
        except Exception as e:
            print(f"插入或更新 AircraftDetectionResults 时出错: {e}")

    # 打印不同飞机类型的数量
    def print_aircraft_types_counts(self):
        try:
            results = self.session.query(AircraftDetectionResult.class_, func.count('*').label('count')).group_by(
                AircraftDetectionResult.class_).all()
            return '\n'.join([f"Aircraft Type: {result.class_}, Count: {result.count}" for result in results])
        except Exception as e:
            print(f"获取飞机类型数量时出错：{e}")
            return ""

    # 清除指定飞机类型的数据
    def clear_aircraft_data_by_type(self, aircraft_type):
        try:
            # 从 AircraftDetectionResults 表中获取图片名称
            aircraft_images = [result.Image_Name for result in self.session.query(AircraftDetectionResult).filter_by(
                class_=aircraft_type).all()]

            # 从 ObjectDetectionResults 表中删除相应的行
            for image_name in aircraft_images:
                self.session.query(ObjectDetectionResult).filter_by(Image_Name=image_name).delete()

            # 从 AircraftDetectionResults 表中删除相应的行
            self.session.query(AircraftDetectionResult).filter_by(class_=aircraft_type).delete()

            self.session.commit()
            print(f"已清除飞机类型为 {aircraft_type} 的数据。")

        except Exception as e:
            print(f"清除飞机类型数据时出错：{e}")

    # 清空数据库表
    def clear_database(self):
        try:
            self.session.query(ObjectDetectionResult).delete()
            self.session.query(AircraftDetectionResult).delete()
            self.session.commit()
        except Exception as e:
            print(f"清空数据库时出错: {e}")

    # 根据图片名称查询飞机类型
    def query_by_image_name(self, image_name):
        try:
            results = self.session.query(AircraftDetectionResult.class_).filter_by(Image_Name=image_name).all()
            aircraft_types = [result.class_ for result in results]
            return ', '.join(aircraft_types) if aircraft_types else "未检测到飞机。"
        except Exception as e:
            print(f"根据图片名称查询时出错: {e}")
            return ""


    # 获取指定飞机类型的随机图片信息
    def get_random_image_by_aircraft_type(self, aircraft_type):
        try:
            results = self.session.query(ObjectDetectionResult.Image_Name, ObjectDetectionResult.ymin,
                                         ObjectDetectionResult.xmin, ObjectDetectionResult.ymax,
                                         ObjectDetectionResult.xmax, AircraftDetectionResult.class_,
                                         AircraftDetectionResult.confidence).join(
                AircraftDetectionResult, ObjectDetectionResult.Image_Name == AircraftDetectionResult.Image_Name).filter(
                AircraftDetectionResult.class_ == aircraft_type).all()

            return random.choice(results) if results else None
        except Exception as e:
            print(f"查询飞机类型图片时出错: {e}")
            return None

    # 更新检测结果
    def update_detection_results(self, image_name, ymin, xmin, ymax, xmax, confidence, aircraft_class):
        try:
            self.session.query(ObjectDetectionResult).filter_by(Image_Name=image_name).update(
                {'ymin': ymin, 'xmin': xmin, 'ymax': ymax, 'xmax': xmax})

            self.session.query(AircraftDetectionResult).filter_by(Image_Name=image_name).update(
                {'confidence': confidence, 'class_': aircraft_class})

            self.session.commit()
        except Exception as e:
            print(f"更新检测结果时出错: {e}")

    # 检查用户凭据
    def check_user_credentials(self, username, password):
        try:
            result = self.session.query(User).filter_by(Username=username, Password=password).first()
            return {'Username': result.Username, 'Role': result.Role} if result else None
        except Exception as e:
            print(f"登录时出错: {e}")
            return None

    # 添加用户
    def add_user(self, username, password, role):
        try:
            new_user = User(Username=username, Password=password, Role=role)
            self.session.add(new_user)
            self.session.commit()
            print("用户已成功添加")
        except Exception as e:
            print(f"添加用户时出错: {e}")

    def export_to_csv(self, username, file_path):
        try:
            results = self.session.query(
                ObjectDetectionResult.Image_Name, ObjectDetectionResult.ymin,
                ObjectDetectionResult.xmin, ObjectDetectionResult.ymax,
                ObjectDetectionResult.xmax, AircraftDetectionResult.class_
            ).join(
                AircraftDetectionResult,
                ObjectDetectionResult.Image_Name == AircraftDetectionResult.Image_Name
            ).filter(
                ObjectDetectionResult.Username == username
            ).all()

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Image_Name', 'ymin', 'xmin', 'ymax', 'xmax', 'class_'])
                for row in results:
                    writer.writerow(row)

            print("数据成功导出到", file_path)
        except Exception as e:
            print(f"导出数据到CSV时出错: {e}")

    # 关闭数据库连接
    def close_connection(self):
        try:
            self.session.close()
        except Exception as e:
            print(f"关闭连接时出错: {e}")
