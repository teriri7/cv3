import sys
import time
import threading
from pynput import keyboard, mouse
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QStyleFactory)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont

class AutoClickerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F键连点器")
        self.setGeometry(300, 300, 450, 350)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QGroupBox {
                background-color: #34495e;
                border: 2px solid #1abc9c;
                border-radius: 10px;
                margin-top: 1ex;
                color: #ecf0f1;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: transparent;
                color: #1abc9c;
            }
            QLabel {
                color: #ecf0f1;
            }
            QLineEdit {
                background-color: #3d566e;
                color: #ecf0f1;
                border: 1px solid #1abc9c;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #1abc9c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QPushButton:pressed {
                background-color: #0d8e72;
            }
            QPushButton#stopButton {
                background-color: #e74c3c;
            }
            QPushButton#stopButton:hover {
                background-color: #c0392b;
            }
            QPushButton#hotkeyButton {
                background-color: #3498db;
            }
            QPushButton#hotkeyButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.init_ui()
        self.clicking = False
        self.hotkey = None
        self.hotkey_listener = None
        self.click_thread = None
        self.keyboard_controller = keyboard.Controller()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 间隔时间设置
        interval_group = QGroupBox("点击间隔设置")
        interval_layout = QVBoxLayout()
        
        interval_row = QHBoxLayout()
        interval_label = QLabel("点击间隔 (秒):")
        self.interval_input = QLineEdit("0.5")
        self.interval_input.setValidator(QApplication.instance().locale().createDoubleValidator(0.01, 10.0, 2))
        interval_row.addWidget(interval_label)
        interval_row.addWidget(self.interval_input)
        
        interval_layout.addLayout(interval_row)
        interval_group.setLayout(interval_layout)
        main_layout.addWidget(interval_group)
        
        # 控制按钮
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout()
        
        self.toggle_button = QPushButton("开始连点")
        self.toggle_button.setObjectName("startButton")
        self.toggle_button.clicked.connect(self.toggle_clicking)
        
        control_layout.addWidget(self.toggle_button)
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # 快捷键设置
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QVBoxLayout()
        
        self.hotkey_button = QPushButton("设置快捷键")
        self.hotkey_button.setObjectName("hotkeyButton")
        self.hotkey_button.clicked.connect(self.start_hotkey_recording)
        
        self.hotkey_label = QLabel("当前快捷键: 未设置")
        self.hotkey_label.setAlignment(Qt.AlignCenter)
        self.hotkey_label.setFont(QFont("Arial", 10))
        
        hotkey_layout.addWidget(self.hotkey_button)
        hotkey_layout.addWidget(self.hotkey_label)
        hotkey_group.setLayout(hotkey_layout)
        main_layout.addWidget(hotkey_group)
        
        # 状态栏
        self.status_label = QLabel("状态: 就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 设置窗口图标
        if hasattr(QStyleFactory, 'create'):
            self.setStyle(QStyleFactory.create('Fusion'))
        
    def toggle_clicking(self):
        self.clicking = not self.clicking
        
        if self.clicking:
            self.toggle_button.setText("停止连点")
            self.toggle_button.setObjectName("stopButton")
            self.toggle_button.setStyleSheet(self.styleSheet())
            self.status_label.setText("状态: 正在连点F键...")
            self.start_clicking()
        else:
            self.toggle_button.setText("开始连点")
            self.toggle_button.setObjectName("startButton")
            self.toggle_button.setStyleSheet(self.styleSheet())
            self.status_label.setText("状态: 已停止")
            self.stop_clicking()
    
    def start_clicking(self):
        if self.click_thread and self.click_thread.is_alive():
            return
            
        try:
            interval = float(self.interval_input.text())
        except ValueError:
            interval = 0.5
            
        self.click_thread = threading.Thread(target=self.click_loop, args=(interval,), daemon=True)
        self.click_thread.start()
    
    def stop_clicking(self):
        self.clicking = False
    
    def click_loop(self, interval):
        while self.clicking:
            self.keyboard_controller.press('f')
            self.keyboard_controller.release('f')
            time.sleep(interval)
    
    def start_hotkey_recording(self):
        self.hotkey_button.setText("正在监听...")
        self.hotkey_button.setEnabled(False)
        self.status_label.setText("状态: 请按下您要设置的快捷键...")
        
        # 在新线程中监听快捷键
        self.hotkey_thread = threading.Thread(target=self.record_hotkey, daemon=True)
        self.hotkey_thread.start()
    
    def record_hotkey(self):
        # 停止现有的监听器
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        # 创建新的监听器
        self.hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+f': self.hotkey_callback,
            '<ctrl>+<shift>+f': self.hotkey_callback,
            '<alt>+f': self.hotkey_callback,
            '<shift>+f': self.hotkey_callback,
            '<ctrl>+f': self.hotkey_callback,
            'f': self.hotkey_callback,
            '<mouse_button4>': self.hotkey_callback,
            '<mouse_button5>': self.hotkey_callback
        })
        
        self.hotkey_listener.start()
        self.hotkey_listener.wait()
    
    def hotkey_callback(self):
        # 获取当前激活的组合键
        current_keys = set()
        for key in [keyboard.Key.ctrl, keyboard.Key.alt, keyboard.Key.shift, keyboard.Key.cmd]:
            if self.keyboard_controller.pressed(key):
                current_keys.add(key)
        
        # 构建快捷键描述
        modifiers = []
        if keyboard.Key.ctrl in current_keys:
            modifiers.append("Ctrl")
        if keyboard.Key.alt in current_keys:
            modifiers.append("Alt")
        if keyboard.Key.shift in current_keys:
            modifiers.append("Shift")
        if keyboard.Key.cmd in current_keys:
            modifiers.append("Cmd")
        
        hotkey_name = "+".join(modifiers) if modifiers else ""
        
        # 检查是否是鼠标侧键
        mouse_listener = mouse.Listener()
        if mouse_listener.button4:
            hotkey_name = "鼠标侧键4"
        elif mouse_listener.button5:
            hotkey_name = "鼠标侧键5"
        
        if not hotkey_name:
            hotkey_name = "F键"
        
        # 更新UI
        self.hotkey = hotkey_name
        self.hotkey_label.setText(f"当前快捷键: {hotkey_name}")
        self.hotkey_button.setText("设置快捷键")
        self.hotkey_button.setEnabled(True)
        self.status_label.setText("状态: 快捷键设置完成")
        
        # 停止监听器
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        # 切换连点状态
        self.toggle_clicking()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置现代感调色板
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(44, 62, 80))
    palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
    palette.setColor(QPalette.Base, QColor(41, 128, 185))
    palette.setColor(QPalette.AlternateBase, QColor(52, 73, 94))
    palette.setColor(QPalette.ToolTipBase, QColor(236, 240, 241))
    palette.setColor(QPalette.ToolTipText, QColor(236, 240, 241))
    palette.setColor(QPalette.Text, QColor(236, 240, 241))
    palette.setColor(QPalette.Button, QColor(26, 188, 156))
    palette.setColor(QPalette.ButtonText, QColor(236, 240, 241))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(41, 128, 185))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = AutoClickerApp()
    window.show()
    sys.exit(app.exec_())
