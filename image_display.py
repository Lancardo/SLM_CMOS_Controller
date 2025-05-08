import sys
import os
import time
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QFileDialog, QLabel, QComboBox, QMessageBox,
                           QHBoxLayout, QLineEdit, QCheckBox, QGroupBox, QSpinBox,
                           QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QScreen, QPixmap
from PIL import Image
import gxipy as gx  # 导入相机SDK

class CameraManager:
    """管理相机连接和拍照功能的类"""
    def __init__(self):
        self.device_manager = None
        self.camera = None
        self.is_initialized = False
        self.exposure_time = 10000.0  # 默认曝光时间
        self.save_path = "captured_images"  # 默认保存路径
        self.image_counter = 0  # 添加图片计数器
        self.temp_images = []  # 临时存储拍摄的图片路径
        
        # 确保保存路径存在
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
            
    def initialize(self):
        """初始化相机连接"""
        try:
            # 创建设备管理器
            self.device_manager = gx.DeviceManager()
            dev_num, dev_info_list = self.device_manager.update_device_list()
            
            if dev_num == 0:
                print("未找到相机设备")
                return False
                
            # 打开第一个设备
            self.camera = self.device_manager.open_device_by_index(1)
            
            # 设置触发模式为软触发
            self.camera.TriggerMode.set(gx.GxSwitchEntry.ON)
            self.camera.TriggerSource.set(gx.GxTriggerSourceEntry.SOFTWARE)
            
            # 设置曝光时间
            self.camera.ExposureTime.set(self.exposure_time)
            
            # 启动数据采集
            self.camera.stream_on()
            
            self.is_initialized = True
            # 重置计数器和临时图片列表
            self.image_counter = 0
            self.temp_images = []
            return True
            
        except Exception as e:
            print(f"相机初始化错误: {str(e)}")
            return False
    
    def set_exposure_time(self, exposure_time):
        """设置相机曝光时间"""
        if self.is_initialized and self.camera:
            try:
                self.exposure_time = float(exposure_time)
                self.camera.ExposureTime.set(self.exposure_time)
                return True
            except Exception as e:
                print(f"设置曝光时间错误: {str(e)}")
                return False
        return False
    
    def capture_image(self):
        """拍摄一张照片并保存"""
        if not self.is_initialized or not self.camera:
            return None
            
        try:
            # 发送软触发命令
            self.camera.TriggerSoftware.send_command()
            
            # 获取原始图像
            raw_image = self.camera.data_stream[0].get_image()
            if raw_image is None:
                print("获取图像失败")
                return None
                
            # 判断相机类型（彩色或单色）
            if self.camera.PixelColorFilter.is_implemented():
                # 彩色相机
                rgb_image = raw_image.convert("RGB")
                numpy_image = rgb_image.get_numpy_array()
                img = Image.fromarray(numpy_image, 'RGB')
            else:
                # 单色相机
                numpy_image = raw_image.get_numpy_array()
                img = Image.fromarray(numpy_image, 'L')
                
            # 生成临时文件名和保存路径
            file_path = os.path.join(self.save_path, f"temp_{self.image_counter}.jpg")
            self.temp_images.append(file_path)
            
            # 保存图像
            img.save(file_path)
            print(f"照片已临时保存: {file_path}")
            
            self.image_counter += 1
            return file_path
            
        except Exception as e:
            print(f"拍照错误: {str(e)}")
            return None
            
    def finalize_images(self, total_images):
        """完成图片拍摄后，重命名最后N张有效图片"""
        try:
            # 确保临时图片列表中至少有total_images张图片
            if len(self.temp_images) < total_images:
                print("警告：临时图片数量少于预期")
                return
                
            # 获取最后total_images张图片
            valid_images = self.temp_images[-total_images:]
            
            # 删除多余的临时图片
            for img_path in self.temp_images[:-total_images]:
                try:
                    os.remove(img_path)
                    print(f"删除多余的图片: {img_path}")
                except:
                    print(f"无法删除图片: {img_path}")
            
            # 重命名有效图片
            for i, old_path in enumerate(valid_images):
                new_path = os.path.join(self.save_path, f"{i}.jpg")
                try:
                    # 如果目标文件已存在，先删除
                    if os.path.exists(new_path):
                        os.remove(new_path)
                    os.rename(old_path, new_path)
                    print(f"重命名图片: {old_path} -> {new_path}")
                except:
                    print(f"重命名图片失败: {old_path}")
            
            # 清空临时图片列表
            self.temp_images = []
            
        except Exception as e:
            print(f"处理图片错误: {str(e)}")
    
    def close(self):
        """关闭相机连接"""
        if self.is_initialized and self.camera:
            try:
                # 停止数据采集
                self.camera.stream_off()
                # 关闭设备
                self.camera.close_device()
                self.is_initialized = False
            except Exception as e:
                print(f"关闭相机错误: {str(e)}")

class ImageDisplayWindow(QWidget):
    def __init__(self, image_list=None, interval=5000, camera_manager=None, enable_camera=False, single_image_mode=False, progress_bar=None):
        super().__init__()
        # 设置窗口无边框
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建状态标签（显示当前图片序号）
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 5px;
                border-radius: 5px;
                font-size: 16px;
            }
        """)
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.setContentsMargins(10, 10, 10, 0)
        
        # 创建图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 添加部件到主布局
        main_layout.addLayout(status_layout)
        main_layout.addWidget(self.image_label)
        self.setLayout(main_layout)

        # 设置图片列表和计时器
        self.image_list = image_list or []
        self.current_image_index = -1
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_image)
        
        # 相机管理器和启用标志
        self.camera_manager = camera_manager
        self.enable_camera = enable_camera
        
        # 单张图片模式标志
        self.single_image_mode = single_image_mode
        
        # 进度条引用
        self.progress_bar = progress_bar
        
        # 如果有图片，开始播放
        if self.image_list:
            # 如果启用了相机，先拍摄一张照片
            if self.enable_camera and self.camera_manager and self.camera_manager.is_initialized:
                self.camera_manager.capture_image()
                
            self.timer.start(interval)
            self.next_image()
        
    def display_image(self, image_path):
        # 显示图片
        pixmap = QPixmap(image_path)
        screen_size = self.size()
        scaled_pixmap = pixmap.scaled(screen_size, 
                                    Qt.AspectRatioMode.IgnoreAspectRatio,
                                    Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        
        # 更新状态标签和进度条
        total_images = len(self.image_list)
        current_index = self.current_image_index + 1
        
        if self.single_image_mode:
            self.status_label.setText("单张图片显示模式")
            if self.progress_bar:
                self.progress_bar.setValue(1)
                self.progress_bar.setFormat("1/1")
        else:
            self.status_label.setText(f"当前显示: {current_index}/{total_images}")
            if self.progress_bar:
                self.progress_bar.setValue(current_index)
                self.progress_bar.setFormat(f"{current_index}/{total_images}")

    def next_image(self):
        if not self.image_list:
            return
            
        # 如果启用了相机，在显示下一张图片之前拍摄照片
        if self.enable_camera and self.camera_manager and self.camera_manager.is_initialized:
            self.camera_manager.capture_image()
        
        self.current_image_index += 1
        
        # 如果是单张图片模式，永远显示第一张图片
        if self.single_image_mode:
            self.current_image_index = 0
            self.display_image(self.image_list[0])
            return
        
        # 如果已经显示完所有图片
        if self.current_image_index >= len(self.image_list):
            self.timer.stop()
            # 如果启用了相机，处理拍摄的图片
            if self.enable_camera and self.camera_manager and self.camera_manager.is_initialized:
                self.camera_manager.finalize_images(len(self.image_list))
                # 重置相机计数器
                self.camera_manager.image_counter = 0
                self.camera_manager.temp_images = []
            self.close()
            return
            
        self.display_image(self.image_list[self.current_image_index])
        
    def keyPressEvent(self, event):
        # 按ESC键退出全屏
        if event.key() == Qt.Key.Key_Escape:
            self.timer.stop()
            # 如果启用了相机，处理拍摄的图片
            if self.enable_camera and self.camera_manager and self.camera_manager.is_initialized:
                if not self.single_image_mode:  # 只在非单张图片模式下处理图片
                    self.camera_manager.finalize_images(len(self.image_list))
                # 重置相机计数器
                self.camera_manager.image_counter = 0
                self.camera_manager.temp_images = []
            self.close()

    def show_fullscreen(self):
        """显示单张图片"""
        if not self.selected_image_path:
            return
            
        # 创建新的全屏窗口
        self.fullscreen_window = ImageDisplayWindow(
            [self.selected_image_path], 
            camera_manager=self.camera_manager,
            enable_camera=self.camera_checkbox.isChecked(),
            single_image_mode=True,
            progress_bar=self.progress_bar
        )
        
        # 移动到选定的显示器
        current_screen_index = self.screen_combo.currentIndex()
        screen = QApplication.screens()[current_screen_index]
        self.fullscreen_window.move(screen.geometry().topLeft())
        self.fullscreen_window.show()

    def start_slideshow(self):
        """开始幻灯片播放"""
        if not self.image_list:
            return

        try:
            # 获取间隔时间（毫秒）
            interval = int(self.interval_input.text())
            if interval <= 0:
                raise ValueError("间隔时间必须大于0")
        except ValueError as e:
            QMessageBox.warning(self, "输入错误", "请输入有效的时间间隔（毫秒）")
            return

        # 创建新的全屏窗口
        self.fullscreen_window = ImageDisplayWindow(
            self.image_list, 
            interval, 
            camera_manager=self.camera_manager,
            enable_camera=self.camera_checkbox.isChecked(),
            single_image_mode=False,
            progress_bar=self.progress_bar
        )
        
        # 移动到选定的显示器
        current_screen_index = self.screen_combo.currentIndex()
        screen = QApplication.screens()[current_screen_index]
        self.fullscreen_window.move(screen.geometry().topLeft())
        self.fullscreen_window.show()
    
    def closeEvent(self, event):
        """窗口关闭时关闭相机连接"""
        self.camera_manager.close()
        super().closeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片显示器")
        self.setGeometry(100, 100, 600, 500)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 添加SLM设置提示标签
        slm_notice = QLabel("重要：使用前，请将SLM设置为拓展屏幕，分辨率1080p，缩放100%")
        slm_notice.setStyleSheet("color: red; font-weight: bold; padding: 5px; background-color: #FFE4E1;")
        slm_notice.setWordWrap(True)
        main_layout.addWidget(slm_notice)
        
        # 添加图片顺序提示标签
        notice_label = QLabel("注意：选择文件夹时，图片必须使用数字命名（从0开始），将按数字从小到大顺序播放")
        notice_label.setStyleSheet("color: blue; font-weight: bold;")
        notice_label.setWordWrap(True)
        main_layout.addWidget(notice_label)
        
        # 创建主面板
        main_panel_widget = QWidget()
        main_panel = QVBoxLayout(main_panel_widget)
        
        # 创建选择图片按钮
        self.select_button = QPushButton("选择单张图片")
        self.select_button.clicked.connect(self.select_image)
        main_panel.addWidget(self.select_button)

        # 创建选择文件夹按钮
        self.select_folder_button = QPushButton("选择图片文件夹")
        self.select_folder_button.clicked.connect(self.select_folder)
        main_panel.addWidget(self.select_folder_button)

        # 创建时间间隔输入框
        interval_widget = QWidget()
        interval_layout = QHBoxLayout(interval_widget)
        interval_layout.addWidget(QLabel("播放间隔（毫秒）："))
        self.interval_input = QLineEdit()
        self.interval_input.setText("5000")
        self.interval_input.setPlaceholderText("请输入播放间隔（毫秒）")
        interval_layout.addWidget(self.interval_input)
        main_panel.addWidget(interval_widget)
        
        # 创建显示器选择下拉框
        self.screen_combo = QComboBox()
        self.update_screen_list()
        main_panel.addWidget(QLabel("选择显示器:"))
        main_panel.addWidget(self.screen_combo)
        
        # 创建相机控制面板
        camera_group = QGroupBox("相机控制")
        camera_layout = QVBoxLayout()
        
        # 相机开关
        self.camera_checkbox = QCheckBox("启用相机")
        self.camera_checkbox.toggled.connect(self.toggle_camera)
        camera_layout.addWidget(self.camera_checkbox)
        
        # 相机曝光时间设置
        exposure_widget = QWidget()
        exposure_layout = QHBoxLayout(exposure_widget)
        exposure_layout.addWidget(QLabel("曝光时间(μs):"))
        self.exposure_input = QSpinBox()
        self.exposure_input.setRange(1, 1000000)
        self.exposure_input.setValue(10000)
        self.exposure_input.setSingleStep(1000)
        exposure_layout.addWidget(self.exposure_input)
        self.exposure_set_button = QPushButton("设置")
        self.exposure_set_button.clicked.connect(self.set_camera_exposure)
        self.exposure_set_button.setEnabled(False)
        exposure_layout.addWidget(self.exposure_set_button)
        camera_layout.addWidget(exposure_widget)
        
        # 相机状态标签
        self.camera_status_label = QLabel("相机状态: 未连接")
        camera_layout.addWidget(self.camera_status_label)
        
        camera_group.setLayout(camera_layout)
        main_panel.addWidget(camera_group)
        
        # 创建进度显示组
        progress_group = QGroupBox("播放进度")
        progress_layout = QVBoxLayout()
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)  # 显示进度文本
        self.progress_bar.setFormat("0/0")  # 初始显示格式
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_panel.addWidget(progress_group)
        
        # 创建显示按钮
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        self.display_button = QPushButton("显示单张图片")
        self.display_button.clicked.connect(self.show_fullscreen)
        self.display_button.setEnabled(False)
        button_layout.addWidget(self.display_button)

        self.slideshow_button = QPushButton("开始幻灯片播放")
        self.slideshow_button.clicked.connect(self.start_slideshow)
        self.slideshow_button.setEnabled(False)
        button_layout.addWidget(self.slideshow_button)
        main_panel.addWidget(button_widget)
        
        # 创建状态标签
        self.status_label = QLabel()
        main_panel.addWidget(self.status_label)
        
        # 添加弹性空间
        main_panel.addStretch()
        
        # 创建签名标签
        signature_label = QLabel("@RuiboLan")
        signature_label.setStyleSheet("color: gray; font-style: italic;")
        main_panel.addWidget(signature_label)
        
        # 将主面板添加到主布局
        main_layout.addWidget(main_panel_widget)
        
        self.selected_image_path = None
        self.image_folder_path = None
        self.image_list = []
        
        # 创建相机管理器
        self.camera_manager = CameraManager()
        
    def update_screen_list(self):
        self.screen_combo.clear()
        screens = QApplication.screens()
        for i, screen in enumerate(screens):
            geometry = screen.geometry()
            self.screen_combo.addItem(f"显示器 {i+1} ({geometry.width()}x{geometry.height()})")
            
    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_name:
            self.selected_image_path = file_name
            self.display_button.setEnabled(True)
            self.check_resolution(file_name)
            # 更新进度条
            self.progress_bar.setMaximum(1)
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("0/1")

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择图片文件夹"
        )
        
        if folder_path:
            self.image_folder_path = folder_path
            # 获取文件夹中的所有图片文件
            image_files = [f for f in os.listdir(folder_path) 
                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
                         and f.split('.')[0].isdigit()]
            
            # 按文件名数字排序
            image_files.sort(key=lambda x: int(x.split('.')[0]))
            
            # 构建完整路径列表
            self.image_list = [os.path.join(folder_path, f) for f in image_files]
            
            if self.image_list:
                self.slideshow_button.setEnabled(True)
                self.check_resolution(self.image_list[0])
                # 更新进度条
                total_images = len(self.image_list)
                self.progress_bar.setMaximum(total_images)
                self.progress_bar.setValue(0)
                self.progress_bar.setFormat(f"0/{total_images}")
                self.status_label.setText(f"已找到 {total_images} 张图片")
            else:
                self.status_label.setText("文件夹中没有找到有效的图片文件")
                self.slideshow_button.setEnabled(False)
                self.progress_bar.setValue(0)
                self.progress_bar.setFormat("0/0")

    def check_resolution(self, image_path):
        if not image_path:
            return
            
        # 获取图片分辨率
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            
        # 获取选中显示器的分辨率
        current_screen_index = self.screen_combo.currentIndex()
        screen = QApplication.screens()[current_screen_index]
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        # 检查分辨率是否匹配
        if img_width != screen_width or img_height != screen_height:
            self.status_label.setText(
                f"警告：图片分辨率 ({img_width}x{img_height}) "
                f"与显示器分辨率 ({screen_width}x{screen_height}) 不匹配！"
            )
            self.status_label.setStyleSheet("color: red")
        else:
            self.status_label.setText("分辨率匹配正常")
            self.status_label.setStyleSheet("color: green")
    
    def toggle_camera(self, checked):
        """启用或禁用相机"""
        if checked:
            # 尝试初始化相机
            if self.camera_manager.initialize():
                self.camera_status_label.setText("相机状态: 已连接")
                self.exposure_set_button.setEnabled(True)
            else:
                self.camera_checkbox.setChecked(False)
                self.camera_status_label.setText("相机状态: 连接失败")
                QMessageBox.warning(self, "相机错误", "无法连接到相机，请检查连接")
        else:
            # 关闭相机
            self.camera_manager.close()
            self.camera_status_label.setText("相机状态: 未连接")
            self.exposure_set_button.setEnabled(False)
    
    def set_camera_exposure(self):
        """设置相机曝光时间"""
        if self.camera_manager.is_initialized:
            exposure = self.exposure_input.value()
            if self.camera_manager.set_exposure_time(exposure):
                self.status_label.setText(f"已设置相机曝光时间为 {exposure}μs")
            else:
                self.status_label.setText("设置曝光时间失败")
                self.status_label.setStyleSheet("color: red")
            
    def show_fullscreen(self):
        if not self.selected_image_path:
            return
            
        # 创建新的全屏窗口
        self.fullscreen_window = ImageDisplayWindow(
            [self.selected_image_path], 
            camera_manager=self.camera_manager,
            enable_camera=self.camera_checkbox.isChecked(),
            single_image_mode=True,
            progress_bar=self.progress_bar
        )
        
        # 移动到选定的显示器
        current_screen_index = self.screen_combo.currentIndex()
        screen = QApplication.screens()[current_screen_index]
        self.fullscreen_window.move(screen.geometry().topLeft())
        self.fullscreen_window.show()

    def start_slideshow(self):
        if not self.image_list:
            return

        try:
            # 获取间隔时间（毫秒）
            interval = int(self.interval_input.text())
            if interval <= 0:
                raise ValueError("间隔时间必须大于0")
        except ValueError as e:
            QMessageBox.warning(self, "输入错误", "请输入有效的时间间隔（毫秒）")
            return

        # 创建新的全屏窗口
        self.fullscreen_window = ImageDisplayWindow(
            self.image_list, 
            interval, 
            camera_manager=self.camera_manager,
            enable_camera=self.camera_checkbox.isChecked(),
            single_image_mode=False,
            progress_bar=self.progress_bar
        )
        
        # 移动到选定的显示器
        current_screen_index = self.screen_combo.currentIndex()
        screen = QApplication.screens()[current_screen_index]
        self.fullscreen_window.move(screen.geometry().topLeft())
        self.fullscreen_window.show()
    
    def closeEvent(self, event):
        """窗口关闭时关闭相机连接"""
        self.camera_manager.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 