import mysql.connector
import random

# SQL 命令
INSERT_OBJECT_DETECTION_QUERY = "INSERT INTO ObjectDetectionResults (Image_Name, ymin, xmin, ymax, xmax) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ymin=VALUES(ymin), xmin=VALUES(xmin), ymax=VALUES(ymax), xmax=VALUES(xmax)"
INSERT_AIRCRAFT_DETECTION_QUERY = "INSERT INTO AircraftDetectionResults (Image_Name, confidence, class) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE confidence=VALUES(confidence), class=VALUES(class)"
CLEAR_OBJECT_DETECTION_QUERY = "DELETE FROM ObjectDetectionResults"
CLEAR_AIRCRAFT_DETECTION_QUERY = "DELETE FROM AircraftDetectionResults"
QUERY_BY_IMAGE_NAME_QUERY = "SELECT class FROM AircraftDetectionResults WHERE Image_Name = %s"
SELECT_AIRCRAFT_COUNT_BY_TYPE_QUERY = "SELECT class, COUNT(*) as count FROM AircraftDetectionResults GROUP BY class"
SELECT_AIRCRAFT_IMAGES_BY_TYPE_QUERY = "SELECT Image_Name FROM AircraftDetectionResults WHERE class = %s"
DELETE_OBJECT_BY_IMAGE_NAME_QUERY = "DELETE FROM ObjectDetectionResults WHERE Image_Name = %s"
DELETE_AIRCRAFT_BY_TYPE_QUERY = "DELETE FROM AircraftDetectionResults WHERE class = %s"

# 查询语句
SELECT_IMAGE_AND_AIRCRAFT_INFO_QUERY = """
    SELECT o.Image_Name, o.ymin, o.xmin, o.ymax, o.xmax, a.class, a.confidence
    FROM ObjectDetectionResults AS o
    INNER JOIN AircraftDetectionResults AS a ON o.Image_Name = a.Image_Name
    WHERE a.class = %s
"""

# 更新 ObjectDetectionResults 表
UPDATE_OBJECT_QUERY = """
    UPDATE ObjectDetectionResults
    SET ymin = %s, xmin = %s, ymax = %s, xmax = %s
    WHERE Image_Name = %s
"""

# 更新 AircraftDetectionResults 表
UPDATE_AIRCRAFT_QUERY = """
    UPDATE AircraftDetectionResults
    SET confidence = %s, class = %s
    WHERE Image_Name = %s
"""

class DatabaseUtil:
    def __init__(self):
        # 数据库配置
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '2003Kangwenqiao',
            'database': 'database_base'
        }
        # 连接数据库
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()



    def insert_or_update_object_detection(self, detection_data):
        try:
            # 插入或更新 ObjectDetectionResults 表
            self.cursor.execute(INSERT_OBJECT_DETECTION_QUERY, (
                detection_data['Image_Name'],
                detection_data['ymin'],
                detection_data['xmin'],
                detection_data['ymax'],
                detection_data['xmax']
            ))
            self.conn.commit()
        except Exception as e:
            print(f"插入或更新 ObjectDetectionResults 时出错: {e}")

    def insert_or_update_aircraft_detection(self, aircraft_data):
        try:
            # 插入或更新 AircraftDetectionResults 表
            self.cursor.execute(INSERT_AIRCRAFT_DETECTION_QUERY, (
                aircraft_data['Image_Name'],
                aircraft_data['confidence'],
                aircraft_data['class_']
            ))
            self.conn.commit()
        except Exception as e:
            print(f"插入或更新 AircraftDetectionResults 时出错: {e}")

    def print_aircraft_types_counts(self):
        try:
            # 查询不同飞机类型的数量
            self.cursor.execute(SELECT_AIRCRAFT_COUNT_BY_TYPE_QUERY)
            results = self.cursor.fetchall()
            return '\n'.join([f"Aircraft Type: {result[0]}, Count: {result[1]}" for result in results])
        except Exception as e:
            print(f"获取飞机类型数量时出错：{e}")
            return ""

    def clear_aircraft_data_by_type(self, aircraft_type):
        try:
            # 从 AircraftDetectionResults 表中获取图片名称
            self.cursor.execute(SELECT_AIRCRAFT_IMAGES_BY_TYPE_QUERY, (aircraft_type,))
            aircraft_images = [result[0] for result in self.cursor.fetchall()]

            # 从 ObjectDetectionResults 表中删除相应的行
            for image_name in aircraft_images:
                self.cursor.execute(DELETE_OBJECT_BY_IMAGE_NAME_QUERY, (image_name,))

            # 从 AircraftDetectionResults 表中删除相应的行
            self.cursor.execute(DELETE_AIRCRAFT_BY_TYPE_QUERY, (aircraft_type,))

            self.conn.commit()
            print(f"已清除飞机类型为 {aircraft_type} 的数据。")

        except Exception as e:
            print(f"清除飞机类型数据时出错：{e}")

    def clear_database(self):
        try:
            # 清空数据库表
            self.cursor.execute(CLEAR_OBJECT_DETECTION_QUERY)
            self.cursor.execute(CLEAR_AIRCRAFT_DETECTION_QUERY)
            self.conn.commit()
        except Exception as e:
            print(f"清空数据库时出错: {e}")

    def query_by_image_name(self, image_name):
        try:
            # 根据图片名称查询飞机类型
            self.cursor.execute(QUERY_BY_IMAGE_NAME_QUERY, (image_name,))
            results = self.cursor.fetchall()
            aircraft_types = [result[0] for result in results]
            return ', '.join(aircraft_types) if aircraft_types else "未检测到飞机。"
        except Exception as e:
            print(f"根据图片名称查询时出错: {e}")
            return ""

    def get_random_image_by_aircraft_type(self, aircraft_type):
        try:
            # 执行查询
            self.cursor.execute(SELECT_IMAGE_AND_AIRCRAFT_INFO_QUERY, (aircraft_type,))
            results = self.cursor.fetchall()
            return random.choice(results) if results else None
        except Exception as e:
            print(f"查询飞机类型图片时出错: {e}")
            return None

    def update_detection_results(self, image_name, ymin, xmin, ymax, xmax, confidence, aircraft_class):
        try:
            # 更新 ObjectDetectionResults 表
            self.cursor.execute(UPDATE_OBJECT_QUERY, (ymin, xmin, ymax, xmax, image_name))

            # 更新 AircraftDetectionResults 表
            self.cursor.execute(UPDATE_AIRCRAFT_QUERY, (confidence, aircraft_class, image_name))

            self.conn.commit()
        except Exception as e:
            print(f"更新检测结果时出错: {e}")

        # 添加登录验证功能

    def check_user_credentials(self, username, password):
        try:
            query = "SELECT * FROM Users WHERE Username = %s AND Password = %s"
            self.cursor.execute(query, (username, password))
            result = self.cursor.fetchone()
            return {'Username': result[0], 'Role': result[2]} if result else None
        except Exception as e:
            print(f"登录时出错: {e}")
            return None

    def add_user(self, username, password, role):
        try:
            query = "INSERT INTO Users (Username, Password, Role) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (username, password, role))
            self.conn.commit()
            print("用户已成功添加")
        except Exception as e:
            print(f"添加用户时出错: {e}")

    def close_connection(self):
        try:
            self.conn.close()
        except Exception as e:
            print(f"关闭连接时出错: {e}")