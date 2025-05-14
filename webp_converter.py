import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import os
from datetime import datetime

class WebPConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WebP转PNG工具")
        self.root.geometry("600x400")

        # 初始化组件
        self.create_widgets()

    def create_widgets(self):
        # 拖放区域
        self.drop_label = tk.Label(self.root, 
                                 text="拖放WebP图片到这里",
                                 relief="groove",
                                 height=10,
                                 width=50)
        self.drop_label.pack(pady=20)

        # 日志显示区域
        self.log_text = tk.Text(self.root, 
                              height=10, 
                              state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 绑定拖放事件
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        valid_files = []

        # 过滤WebP文件
        for f in files:
            if f.lower().endswith('.webp'):
                valid_files.append(f)
            else:
                self.log_message(f"忽略非WebP文件: {os.path.basename(f)}")

        if not valid_files:
            self.log_message("错误：没有有效的WebP文件")
            return

        # 处理每个文件
        for file_path in valid_files:
            try:
                self.convert_webp_to_png(file_path)
            except Exception as e:
                self.log_message(f"转换失败: {os.path.basename(file_path)} - {str(e)}")

    def convert_webp_to_png(self, input_path):
        # 生成输出路径
        base_dir = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_path = os.path.join(
            base_dir, 
            f"{base_name}_converted_{timestamp}.png"
        )

        # 转换并保存图片
        with Image.open(input_path) as img:
            img.save(output_path, "PNG", compress_level=0)

        self.log_message(f"转换成功: {os.path.basename(input_path)}\n"
                        f"生成文件: {os.path.basename(output_path)}")

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = WebPConverterApp(root)
    root.mainloop()
