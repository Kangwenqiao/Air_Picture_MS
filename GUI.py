# GUI.py
import os
import re
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk
from tkinter import filedialog, messagebox, simpledialog, ttk

from databaseutil import DatabaseUtil
from model_predict import Predict


class ObjectDetectionGUI:
    IMAGE_DIRECTORY = "datasets/train/images"  # 设置您的图片目录

    def __init__(self, root, background_image_path):
        self.root = root
        root.title("对象检测")
        root.geometry("800x600")  # 可以根据需要调整窗口大小
        self.background_image_path = background_image_path
        self.background_image = None
        self.background_photo = None
        self.canvas = tk.Canvas(root, bg='black')
        self.canvas.pack(fill="both", expand=True)

        self.database_util = DatabaseUtil()
        self.predictor = Predict(database_util=self.database_util)

        self.user_role = None  # 新增：用户角色，默认为空
        self.user = None  # 初始化 user 属性
        self.show_login_window()  # 先显示登录窗口

    def show_login_window(self):
        # 显示登录窗口
        login_window = tk.Toplevel(self.root)
        login_window.title("登录")
        login_window.geometry("300x200")
        tk.Label(login_window, text="用户名:").pack(pady=5)
        username_entry = tk.Entry(login_window)
        username_entry.pack(pady=5)
        tk.Label(login_window, text="密码:").pack(pady=5)
        password_entry = tk.Entry(login_window, show="*")
        password_entry.pack(pady=5)
        ttk.Button(login_window, text="登录", command=lambda: self.login(username_entry.get(), password_entry.get())).pack(pady=10)

    def login(self, username, password):
        # 用户登录验证
        user = self.database_util.check_user_credentials(username, password)
        if user:
            self.user = user  # 设置 user 属性
            self.user_role = user['Role']
            self.setup_ui()
            self.update_background()
        else:
            messagebox.showerror("错误", "用户名或密码错误")

    def setup_ui(self):
        if not self.user_role:  # 检查用户角色
            return

        self.canvas.bind('<Configure>', self.resize_background)

        frame = tk.Frame(self.canvas, bg='#000000', bd=2, relief='groove')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        frame.config(bg="white", highlightbackground="gray", highlightcolor="gray", highlightthickness=1, bd=0)
        # 管理员专有功能
        if self.user_role == 'Admin':
            ttk.Button(frame, text="调节透明度", command=self.adjust_opacity).pack(padx=10, pady=5)
            ttk.Button(frame, text="清除指定飞机类型数据", command=self.clear_aircraft_data).pack(padx=10, pady=5)
            ttk.Button(frame, text="修改检测结果", command=self.modify_detection_results).pack(padx=10, pady=5)
            ttk.Button(frame, text="清空数据库", command=self.clear_database).pack(padx=10, pady=5)
            ttk.Button(frame, text="添加用户", command=self.create_add_user_window).pack(padx=10, pady=5)
            ttk.Button(frame, text="导出数据到CSV", command=self.export_data_to_csv).pack(padx=10, pady=5)
            ttk.Button(frame, text="显示飞机类型数量", command=self.show_aircraft_counts).pack(padx=10, pady=5)
        else:
            ttk.Button(frame, text="调节透明度", command=self.adjust_opacity).pack(padx=10, pady=5)
            ttk.Button(frame, text="选择图片", command=self.select_file).pack(padx=10, pady=5)
            ttk.Button(frame, text="选择文件夹", command=self.select_folder).pack(padx=10, pady=5)
            ttk.Button(frame, text="显示飞机类型数量", command=self.show_aircraft_counts).pack(padx=10, pady=5)
            ttk.Button(frame, text="根据图片名称查询", command=self.query_by_image_name).pack(padx=10, pady=5)
            ttk.Button(frame, text="导出数据到CSV", command=self.export_data_to_csv).pack(padx=10, pady=5)
            ttk.Button(frame, text="显示指定类型飞机图片", command=self.display_aircraft_image).pack(padx=10, pady=5)

        self.status_label = tk.Label(frame, text="", fg="white", bg='black')
        self.status_label.pack(padx=10, pady=5)

    def update_background(self):
        # 更新背景图像
        self.background_image = Image.open(self.background_image_path)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, image=self.background_photo, anchor='nw')

    def resize_background(self, event):
        # 调整窗口大小时重置背景大小
        new_width = event.width
        new_height = event.height
        self.background_image = self.background_image.resize((new_width, new_height), Image.ANTIALIAS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.canvas.create_image(0, 0, image=self.background_photo, anchor='nw')

    def select_file(self):
        # 选择单个文件
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.status_label.config(text=f"已选择文件: {file_path}")

            current_username = self.user['Username']
            self.predictor.detect_and_save(file_path, current_username)  # 传递 username

            messagebox.showinfo("完成", "检测完成，并已将结果保存到数据库。")

    def select_folder(self):
        # 选择文件夹
        folder_path = filedialog.askdirectory()
        if folder_path and self.user:  # 检查用户是否已登录
            self.status_label.config(text=f"已选择文件夹: {folder_path}")

            current_username = self.user['Username']
            self.predictor.batch_detect_and_save(folder_path, current_username)  # 传递 username

            messagebox.showinfo("完成", "检测完成，并已将结果保存到数据库。")
        elif not self.user:
            messagebox.showerror("错误", "未登录用户")

    def show_aircraft_counts(self):
        # 显示飞机类型数量
        counts = self.database_util.print_aircraft_types_counts()
        messagebox.showinfo("飞机类型数量", counts)

    def clear_aircraft_data(self):
        # 清除指定飞机类型数据
        aircraft_type = simpledialog.askstring("输入", "请输入要清除的飞机类型:")
        if aircraft_type:
            self.database_util.clear_aircraft_data_by_type(aircraft_type)
            messagebox.showinfo("操作完成", "数据已清除。")

    def clear_database(self):
        # 清空数据库
        self.database_util.clear_database()
        messagebox.showinfo("操作完成", "数据库已清空。")

    def query_by_image_name(self):
        # 根据图片名称查询
        image_name = simpledialog.askstring("输入", "请输入图片名称:")
        if image_name:
            aircraft_types = self.database_util.query_by_image_name(image_name)
            messagebox.showinfo("查询结果", f"图片 {image_name} 中检测到的飞机类型: {aircraft_types}")

    def display_aircraft_image(self):
        # 显示指定类型飞机图片
        aircraft_type = simpledialog.askstring("输入", "请输入飞机类型:")
        if aircraft_type:
            result = self.database_util.get_random_image_by_aircraft_type(aircraft_type)
            if result:
                image_name, ymin, xmin, ymax, xmax, class_name, confidence = result
                self.show_image_with_box(image_name, ymin, xmin, ymax, xmax, class_name, confidence)
            else:
                messagebox.showinfo("信息", "未找到该类型的飞机图片。")

    def show_image_with_box(self, image_name, ymin, xmin, ymax, xmax, class_name, confidence):
        # 在图像上显示检测结果
        image_path = os.path.join(self.IMAGE_DIRECTORY, image_name)

        # 删除括号及其内容
        image_path = re.sub(r"\([^)]*\)", "", image_path)

        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        # 绘制边界框
        draw.rectangle([(xmin, ymin), (xmax, ymax)], outline="red", width=2)

        # 添加识别参数标签
        label = f"{class_name} ({confidence:.2f})"

        # 设置字体大小和类型
        font_size = 16  # 字体大小
        font = ImageFont.truetype("arial.ttf", font_size)

        text_size = draw.textsize(label, font=font)
        draw.rectangle([(xmin, ymin - text_size[1]), (xmin + text_size[0], ymin)], fill="red")
        draw.text((xmin, ymin - text_size[1]), label, fill="white", font=font)

        image.show()

    def adjust_opacity(self):
        # 调整透明度窗口
        opacity_window = tk.Toplevel(self.root)
        opacity_window.title("调整透明度")
        opacity_window.geometry("300x100")

        tk.Label(opacity_window, text="调整透明度:").pack(pady=5)

        opacity_scale = tk.Scale(opacity_window, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL,
                                 command=self.set_opacity)
        opacity_scale.set(self.root.attributes('-alpha'))  # 设置当前透明度为滑块的初始值
        opacity_scale.pack(pady=5)

    def set_opacity(self, value):
        # 设置透明度
        self.root.attributes('-alpha', float(value))

    def create_add_user_window(self):
        # 创建添加用户窗口
        add_user_window = tk.Toplevel(self.root)
        add_user_window.title("添加用户")
        add_user_window.geometry("300x250")  # 增加窗口高度以容纳新按钮

        tk.Label(add_user_window, text="用户名:").pack(pady=5)
        username_entry = tk.Entry(add_user_window)
        username_entry.pack(pady=5)

        tk.Label(add_user_window, text="密码:").pack(pady=5)
        password_entry = tk.Entry(add_user_window, show="*")
        password_entry.pack(pady=5)

        tk.Label(add_user_window, text="角色:").pack(pady=5)
        role_var = tk.StringVar(value="User")
        role_option = ttk.OptionMenu(add_user_window, role_var, "User", "Admin", "User")
        role_option.pack(pady=5)

        add_button = ttk.Button(add_user_window, text="添加用户", command=lambda: self.add_user(username_entry.get(), password_entry.get(), role_var.get()))
        add_button.pack(pady=10)

        # 添加一个确定按钮来关闭窗口
        confirm_button = ttk.Button(add_user_window, text="确定", command=add_user_window.destroy)
        confirm_button.pack(pady=10)

    def add_user(self, username, password, role):
        # 添加用户
        # 此处应包含密码加密逻辑
        self.database_util.add_user(username, password, role)
        messagebox.showinfo("完成", "用户添加成功")
        # 可以在这里添加逻辑以关闭添加用户窗口，如果需要

    def modify_detection_results(self):
        # 修改检测结果
        image_name = simpledialog.askstring("输入", "请输入要修改的图片名称:")
        if image_name:
            # 以下值应根据实际情况进行修改
            new_ymin = simpledialog.askfloat("输入", "请输入新的 ymin:")
            new_xmin = simpledialog.askfloat("输入", "请输入新的 xmin:")
            new_ymax = simpledialog.askfloat("输入", "请输入新的 ymax:")
            new_xmax = simpledialog.askfloat("输入", "请输入新的 xmax:")
            new_confidence = simpledialog.askfloat("输入", "请输入新的置信度:")
            new_class = simpledialog.askstring("输入", "请输入新的飞机类型:")

            self.database_util.update_detection_results(image_name, new_ymin, new_xmin, new_ymax, new_xmax,
                                                        new_confidence, new_class)
            messagebox.showinfo("信息", "检测结果已更新.")

    def export_data_to_csv(self):
        # 请求输入要导出其数据的用户名
        username = simpledialog.askstring("导出数据", "输入用户名:")
        if username:
            # 请求输入保存CSV的文件路径
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV文件", "*.csv")])
            if file_path:
                self.database_util.export_to_csv(username, file_path)
                messagebox.showinfo("导出成功", f"数据成功导出到 {file_path}")
            else:
                messagebox.showwarning("导出取消", "导出操作已取消。")

