import unittest
import pyautogui
import time
from tkinter import Tk
from threading import Thread
from GUI import ObjectDetectionGUI

class TestObjectDetectionGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 设置测试类的初始化，创建Tkinter窗口和ObjectDetectionGUI实例
        cls.root = Tk()
        cls.root.title("测试")
        cls.app = ObjectDetectionGUI(cls.root, background_image_path='path_to_your_background_image.jpg')
        # 在另一个线程中运行Tkinter事件循环
        cls.thread = Thread(target=cls.root.mainloop)
        cls.thread.start()
        time.sleep(1)  # 等待窗口加载

    @classmethod
    def tearDownClass(cls):
        # 测试类结束时，关闭Tkinter窗口和等待线程结束
        cls.root.quit()
        cls.thread.join()

    def test_login_functionality(self):
        # 测试登录功能
        # 注意：这里需要具体定位到用户名和密码输入框的位置
        pyautogui.click(x=100, y=100)  # 模拟点击用户名输入框的位置
        pyautogui.write('root')  # 输入用户名
        pyautogui.click(x=100, y=150)  # 模拟点击密码输入框的位置
        pyautogui.write('12345678')  # 输入密码
        pyautogui.click(x=150, y=200)  # 模拟点击登录按钮的位置
        time.sleep(1)
        # 在这里添加检查登录后的状态，如角色等的断言

if __name__ == '__main__':
    # 运行单元测试
    unittest.main()
