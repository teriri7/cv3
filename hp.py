import sys
import os
import time
import ctypes
import subprocess
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                            QSpinBox, QMessageBox, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QCursor
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

# 资源路径处理函数
def resource_path(relative_path):
    """获取资源的绝对路径，处理打包后的情况"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class BlackScreenThread(QThread):
    """黑屏线程，用于在后台运行黑屏操作"""
    finished = pyqtSignal()
    
    def __init__(self, duration_minutes=0):
        super().__init__()
        self.duration_minutes = duration_minutes
        self.running = True
        
    def run(self):
        """运行黑屏线程"""
        if self.duration_minutes > 0:
            # 运行指定时间
            time.sleep(self.duration_minutes * 60)
            self.running = False
            self.finished.emit()
        else:
            # 无限运行，直到被外部停止
            while self.running:
                time.sleep(1)
    
    def stop(self):
        """停止黑屏线程"""
        self.running = False
        self.finished.emit()

class MainWindow(QMainWindow):
    """主窗口，提供操作选项"""
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("黑屏模拟工具")
        self.setGeometry(300, 300, 400, 300)
        
        # 创建中央窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # 创建标题标签
        self.title_label = QLabel("黑屏模拟工具")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        self.main_layout.addWidget(self.title_label)
        
        # 创建功能选择区域
        self.create_function_buttons()
        
        # 创建时间选择区域
        self.create_time_selection()
        
        # 创建系统操作区域
        self.create_system_operations()
        
        # 创建状态栏
        self.statusBar().showMessage("就绪")
        
        # 初始化黑屏线程
        self.black_screen_thread = None
        self.black_screen_window = None
        
        # 创建系统托盘
        self.create_system_tray()
    
    def create_function_buttons(self):
        """创建功能按钮区域"""
        # 创建主功能按钮
        self.main_buttons_layout = QVBoxLayout()
        
        self.start_button = QPushButton("进入黑屏模式")
        self.start_button.setStyleSheet("font-size: 16px; padding: 10px; margin: 10px;")
        self.start_button.clicked.connect(self.start_black_screen)
        
        self.main_buttons_layout.addWidget(self.start_button)
        self.main_layout.addLayout(self.main_buttons_layout)
    
    def create_time_selection(self):
        """创建时间选择区域"""
        self.time_layout = QHBoxLayout()
        
        self.time_label = QLabel("黑屏持续时间:")
        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(0, 1440)  # 0-24小时
        self.time_spinbox.setSingleStep(5)
        self.time_spinbox.setValue(0)  # 默认0分钟（无限期）
        
        self.time_unit = QLabel("分钟")
        
        self.time_layout.addWidget(self.time_label)
        self.time_layout.addWidget(self.time_spinbox)
        self.time_layout.addWidget(self.time_unit)
        self.time_layout.addStretch()
        
        self.main_layout.addLayout(self.time_layout)
    
    def create_system_operations(self):
        """创建系统操作区域"""
        self.system_layout = QVBoxLayout()
        
        self.system_label = QLabel("黑屏结束后:")
        self.system_layout.addWidget(self.system_label)
        
        self.system_options = QComboBox()
        self.system_options.addItems([
            "保持黑屏状态",
            "返回主界面",
            "进入系统睡眠",
            "关闭计算机"
        ])
        self.system_layout.addWidget(self.system_options)
        
        # 启动系统操作按钮
        self.system_action_button = QPushButton("执行系统操作")
        self.system_action_button.setStyleSheet("margin: 10px;")
        self.system_action_button.clicked.connect(self.perform_system_action)
        self.system_layout.addWidget(self.system_action_button)
        
        self.main_layout.addLayout(self.system_layout)
    
    def create_system_tray(self):
        """创建系统托盘图标和菜单"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("application-x-executable"))
        
        # 创建托盘菜单
        self.tray_menu = QMenu()
        
        self.show_action = QAction("显示主界面", self)
        self.show_action.triggered.connect(self.show)
        
        self.exit_action = QAction("退出程序", self)
        self.exit_action.triggered.connect(self.close_app)
        
        self.tray_menu.addAction(self.show_action)
        self.tray_menu.addAction(self.exit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
    
    def start_black_screen(self):
        """开始黑屏模式"""
        # 获取选择的时间
        duration_minutes = self.time_spinbox.value()
        
        # 获取视频文件路径（使用资源路径函数）
        video_path = resource_path("black_video.mp4")
        
        # 创建黑屏窗口
        self.black_screen_window = BlackScreenWindow(video_path, duration_minutes)
        
        # 连接完成信号
        self.black_screen_window.finished.connect(self.on_black_screen_finished)
        
        # 显示黑屏窗口
        self.black_screen_window.show()
        
        # 隐藏主窗口
        self.hide()
    
    def perform_system_action(self):
        """执行系统操作"""
        option = self.system_options.currentIndex()
        
        if option == 0:
            # 保持黑屏状态
            self.start_black_screen()
        elif option == 1:
            # 返回主界面
            pass  # 已经在主界面
        elif option == 2:
            # 进入系统睡眠
            self.system_sleep()
        elif option == 3:
            # 关闭计算机
            self.shutdown_computer()
    
    def system_sleep(self):
        """使系统进入睡眠状态"""
        if sys.platform == 'win32':
            ctypes.windll.powrprof.SetSuspendState(0, 1, 0)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['pmset', 'displaysleepnow'])
        elif sys.platform.startswith('linux'):
            subprocess.run(['systemctl', 'suspend'])
    
    def shutdown_computer(self):
        """关闭计算机"""
        reply = QMessageBox.question(self, '确认', 
                                     "确定要关闭计算机吗?",
                                     QMessageBox.Yes | QMessageBox.No, 
                                     QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if sys.platform == 'win32':
                subprocess.run(['shutdown', '/s', '/t', '10'])
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['shutdown', '-h', 'now'])
            elif sys.platform.startswith('linux'):
                subprocess.run(['shutdown', '-h', 'now'])
    
    def on_black_screen_finished(self):
        """黑屏模式结束时的处理"""
        # 显示主窗口
        self.show()
        
        # 获取选择的系统操作
        option = self.system_options.currentIndex()
        
        if option == 2:
            # 进入系统睡眠
            self.system_sleep()
        elif option == 3:
            # 关闭计算机
            self.shutdown_computer()
    
    def close_app(self):
        """关闭应用程序"""
        # 确保所有线程都停止
        if self.black_screen_thread and self.black_screen_thread.isRunning():
            self.black_screen_thread.stop()
        
        # 退出应用程序
        QApplication.quit()

class BlackScreenWindow(QMainWindow):
    """黑屏窗口，用于显示黑色视频"""
    finished = pyqtSignal()
    
    def __init__(self, video_path, duration_minutes=0):
        super().__init__()
        
        # 视频文件路径
        self.video_path = video_path
        self.duration_minutes = duration_minutes
        
        # 防止系统进入睡眠状态
        self.prevent_sleep()
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框窗口
        self.setWindowState(Qt.WindowFullScreen)     # 全屏显示
        
        # 设置背景为黑色
        self.setStyleSheet("background-color: black;")
        
        # 隐藏鼠标指针
        self.setCursor(Qt.BlankCursor)
        
        # 创建视频播放器
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.setCentralWidget(self.video_widget)
        self.media_player.setVideoOutput(self.video_widget)
        
        # 加载黑色视频
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
        
        # 设置定时器以保持系统活跃
        self.timer = QTimer()
        self.timer.timeout.connect(self.keep_alive)
        self.timer.start(5000)  # 每5秒触发一次
        
        # 播放视频
        self.media_player.play()
        
        # 如果设置了持续时间，创建定时器
        if self.duration_minutes > 0:
            self.duration_timer = QTimer()
            self.duration_timer.timeout.connect(self.close)
            self.duration_timer.start(self.duration_minutes * 60 * 1000)
    
    def prevent_sleep(self):
        """防止系统进入睡眠状态"""
        if sys.platform == 'win32':
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)  # ES_CONTINUOUS | ES_DISPLAY_REQUIRED
    
    def keep_alive(self):
        """保持系统活跃"""
        if sys.platform == 'win32':
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
    
    def keyPressEvent(self, event):
        """按ESC键退出黑屏模式"""
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def closeEvent(self, event):
        """关闭窗口时的处理"""
        # 恢复系统设置
        if sys.platform == 'win32':
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)  # ES_CONTINUOUS
        
        # 停止视频播放
        self.media_player.stop()
        
        # 发送完成信号
        self.finished.emit()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
