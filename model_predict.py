# model_predict.py
import os
from glob import glob
import torch
from ultralytics import YOLO

class Predict:
    def __init__(self, model_path='YOLOv8_v8n_2023.11.13.pt', database_util=None, use_gpu=True):
        """
        初始化预测模块

        Args:
            model_path (str): YOLO模型的路径
            database_util (DatabaseUtil): 数据库工具实例
            use_gpu (bool): 是否使用GPU
        """
        self.use_gpu = use_gpu
        self.database_util = database_util

        if use_gpu and torch.cuda.is_available():
            self.device = torch.device('cuda')
            print("使用GPU.")
        else:
            self.device = torch.device('cpu')
            print("使用CPU.")

        self.model = YOLO(model_path).to(self.device)
        self.class_mapping = {0: 'E2', 1: 'J20', 2: 'B2', 3: 'F14', 4: 'Tornado', 5: 'F4', 6: 'B52', 7: 'JAS39', 8: 'Mirage2000'}

    def detect_and_save(self, image_path, username):
        """
        检测图像并保存结果到数据库

        Args:
            image_path (str): 输入图像路径
            username (str): 当前操作用户的用户名
        """
        image_name, extension = os.path.splitext(os.path.basename(image_path))

        # 检测对象
        boxes = self.detect_image(image_path)

        # 遍历检测到的每个物体
        for i, box in enumerate(boxes):
            ymin, xmin, ymax, xmax, confidence, class_pred = box

            # 如果有多个物体被检测到，给图片名添加后缀
            suffix = f"({i + 1})" if len(boxes) > 1 else ""
            image_name_with_suffix = f"{image_name}{suffix}{extension}"

            # 准备 ObjectDetectionResult 数据
            object_detection_data = {
                'Image_Name': image_name_with_suffix,
                'ymin': float(ymin),
                'xmin': float(xmin),
                'ymax': float(ymax),
                'xmax': float(xmax),
                'Username': username  # 添加 username
            }

            # 插入或更新 ObjectDetectionResults 表
            self.database_util.insert_or_update_object_detection(object_detection_data, username)

            # 准备 AircraftDetectionResult 数据
            aircraft_detection_data = {
                'Image_Name': image_name_with_suffix,
                'confidence': float(confidence),
                'class_': str(self.class_mapping[int(class_pred)]),
                'Username': username  # 添加 username
            }

            # 插入或更新 AircraftDetectionResults 表
            self.database_util.insert_or_update_aircraft_detection(aircraft_detection_data, username)

    def detect_image(self, image_path):
        """
        检测单张图像

        Args:
            image_path (str): 输入图像路径

        Returns:
            torch.Tensor: 检测框的信息
        """
        out = self.model.predict(image_path)
        boxes = out[0].boxes.data.cpu().numpy()
        boxes = boxes[:, [1, 0, 3, 2, 4, 5]]  # 重新排序为ymin, xmin, ymax, xmax, conf, class_pred
        return boxes

    def batch_detect_and_save(self, image_folder, username):
        image_paths = glob(os.path.join(image_folder, '*.jpg'))

        for image_path in image_paths:
            try:
                self.detect_and_save(image_path, username)  # 确保传递 username
            except Exception as e:
                print(f"处理图像 {image_path} 时出错: {e}")

