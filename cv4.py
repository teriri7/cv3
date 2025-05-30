import os
import time
import threading
from tkinter import messagebox
from tkinter import ttk
import ttkbootstrap as ttk
from tkinter import filedialog
from PIL import Image, ImageGrab
import pyautogui
import win32clipboard
from win32con import CF_DIB
from io import BytesIO

class ExcelImageTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel图片工具 v1.0")
        self.root.geometry("400x300")
        
        # 界面主题设置
        self.style = ttk.Style(theme="minty")
        
        # 创建主容器
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(pady=40, expand=True)
        
        # 按钮样式设置
        self.style.configure('success.TButton', font=('微软雅黑', 12))
        self.style.configure('info.TButton', font=('微软雅黑', 12))
        
        # 粘贴图片按钮
        self.paste_btn = ttk.Button(
            self.main_frame,
            text="粘贴图片到Excel",
            style="success.TButton",
            command=self.start_paste_process
        )
        self.paste_btn.pack(pady=10, ipadx=20, ipady=10)
        
        # 下载图片按钮
        self.download_btn = ttk.Button(
            self.main_frame,
            text="下载Excel图片",
            style="info.TButton",
            command=self.start_download_process
        )
        self.download_btn.pack(pady=10, ipadx=20, ipady=10)
        
        # 状态变量
        self.running = False
        self.current_folder = ""
        self.save_folder = ""

    def start_paste_process(self):
        self.current_folder = filedialog.askdirectory(title="选择图片文件夹")
        if not self.current_folder:
            return
        
        messagebox.showinfo("准备粘贴", "请选中Excel起始单元格，5秒后开始粘贴...")
        self.root.after(5000, self.paste_images)

    def start_download_process(self):
        self.save_folder = filedialog.askdirectory(title="选择保存文件夹")
        if not self.save_folder:
            return
        
        messagebox.showinfo("准备下载", "请选中Excel起始单元格，5秒后开始下载...")
        self.root.after(5000, self.download_images)

    def paste_images(self):
        def paste_thread():
            self.running = True
            try:
                image_files = sorted(
                    [f for f in os.listdir(self.current_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
                    key=lambda x: x.lower()
                )
                
                for idx, filename in enumerate(image_files):
                    if not self.running:
                        break
                    
                    path = os.path.join(self.current_folder, filename)
                    try:
                        img = Image.open(path)
                        self.set_clipboard_image(img)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(3)
                        pyautogui.press('down')
                        print(f"已粘贴: {filename}")
                    except Exception as e:
                        print(f"粘贴失败 {filename}: {str(e)}")
                        continue
                
                messagebox.showinfo("完成", "图片粘贴操作已完成！")
            finally:
                self.running = False

        threading.Thread(target=paste_thread, daemon=True).start()

    def download_images(self):
        def download_thread():
            self.running = True
            try:
                index = 1
                while self.running:
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(1)
                    
                    try:
                        img = ImageGrab.grabclipboard()
                        if img is None:
                            messagebox.showwarning("中断", "未检测到图片，操作已中断")
                            self.running = False
                            return
                        
                        output_path = os.path.join(self.save_folder, f"image_{index}.png")
                        img.save(output_path, "PNG")
                        print(f"已保存: {output_path}")
                        index += 1
                        pyautogui.press('down')
                        time.sleep(1)
                    except Exception as e:
                        print(f"下载失败: {str(e)}")
                        continue
                
                messagebox.showinfo("完成", "图片下载操作已完成！")
            finally:
                self.running = False

        threading.Thread(target=download_thread, daemon=True).start()

    @staticmethod
    def set_clipboard_image(image):
        with BytesIO() as output:
            image.convert("RGB").save(output, format="BMP")
            bmp_data = output.getvalue()[14:]
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(CF_DIB, bmp_data)
            finally:
                win32clipboard.CloseClipboard()

if __name__ == "__main__":
    root = ttk.Window()
    app = ExcelImageTool(root)
    root.mainloop()
