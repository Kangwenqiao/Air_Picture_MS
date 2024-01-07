# models.py
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ObjectDetectionResult(Base):
    __tablename__ = 'ObjectDetectionResults'

    Image_Name = Column(String(255), primary_key=True)  # 图像名称，主键
    ymin = Column(Float)  # 检测结果的最小 Y 坐标
    xmin = Column(Float)  # 检测结果的最小 X 坐标
    ymax = Column(Float)  # 检测结果的最大 Y 坐标
    xmax = Column(Float)  # 检测结果的最大 X 坐标
    Username = Column(String(255))  # 与检测结果关联的用户名

class AircraftDetectionResult(Base):
    __tablename__ = 'AircraftDetectionResults'

    Image_Name = Column(String(255), primary_key=True)  # 图像名称，主键
    confidence = Column(Float)  # 飞机检测的置信度
    class_ = Column(String(10))  # 检测到的飞机的类别
    Username = Column(String(255))  # 与飞机检测结果关联的用户名

class User(Base):
    __tablename__ = 'Users'

    Username = Column(String(255), primary_key=True)  # 用户名，主键
    Password = Column(String(255))  # 用户密码
    Role = Column(String(10))  # 用户角色（例如，管理员、普通用户）

# 创建数据库引擎
engine = create_engine('mysql+mysqlconnector://root:2003Kangwenqiao@localhost/database_base')

# 创建模型对应的表
Base.metadata.create_all(engine)
