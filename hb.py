import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image
import os
from datetime import datetime

class ImageMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片合并工具")
        self.root.geometry("600x400")

        # 支持的图片格式
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.webp')
        self.max_images = 4

        # 创建GUI组件
        self.create_widgets()

    def create_widgets(self):
        # 拖放区域
        self.drop_label = tk.Label(self.root, text="拖放图片到这里 (最多4张)", 
                                relief="groove", height=10, width=50)
        self.drop_label.pack(pady=20)

        # 日志显示区域
        self.log_text = tk.Text(self.root, height=10, state='disabled')
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

        for f in files:
            if os.path.splitext(f)[1].lower() in self.supported_formats:
                valid_files.append(f)
            else:
                self.log_message(f"忽略不支持的文件: {os.path.basename(f)}")

        if len(valid_files) < 1:
            self.log_message("错误：至少需要1张图片")
            return
        if len(valid_files) > self.max_images:
            self.log_message(f"错误：最多支持{self.max_images}张图片")
            valid_files = valid_files[:self.max_images]

        self.log_message(f"开始处理 {len(valid_files)} 张图片...")
        try:
            output_path = self.merge_images(valid_files)
            self.log_message(f"合并成功！保存路径: {output_path}")
        except Exception as e:
            self.log_message(f"处理出错: {str(e)}")

    def merge_images(self, file_paths):
        images = []
        heights = []
        widths = []

        for path in file_paths:
            img = Image.open(path)
            images.append(img)
            widths.append(img.width)
            heights.append(img.height)

        base_height = images[0].height
        resized_images = []
        for img in images:
            w_percent = base_height / float(img.height)
            new_width = int(float(img.width) * float(w_percent))
            resized = img.resize((new_width, base_height), Image.LANCZOS)
            resized_images.append(resized)

        total_width = sum(img.width for img in resized_images)
        merged_img = Image.new('RGB', (total_width, base_height))

        x_offset = 0
        for img in resized_images:
            merged_img.paste(img, (x_offset, 0))
            x_offset += img.width

        # 获取第一个图片所在目录
        output_dir = os.path.dirname(file_paths[0])
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"merged_{timestamp}.jpg"
        output_path = os.path.join(output_dir, output_filename)
        
        # 设置质量为100
        merged_img.save(output_path, quality=100, subsampling=0)
        return output_path

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = ImageMergerApp(root)
    root.mainloop()
