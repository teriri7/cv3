import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageOps
import os
from datetime import datetime
import math

class ImageMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片合并工具")
        self.root.geometry("650x550")
        self.root.configure(bg='#f0f0f0')
        
        # 设置应用样式
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('Header.TLabel', background='#4a6fa5', foreground='white', font=('Arial', 12, 'bold'))
        self.style.configure('TRadiobutton', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), background='#4a6fa5')
        self.style.map('TButton', background=[('active', '#3a5a8f')])
        
        # 支持的图片格式
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.webp')
        self.merge_mode = tk.StringVar(value="horizontal")  # 默认为横向合并
        self.output_format = tk.StringVar(value="jpg")  # 默认为jpg格式

        # 创建GUI组件
        self.create_widgets()

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        header = ttk.Label(main_frame, text="图片合并工具", style='Header.TLabel')
        header.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # 合并模式选择区域
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(mode_frame, text="选择合并方式:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            mode_frame, text="横向合并 (一行排列)", 
            variable=self.merge_mode, value="horizontal"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            mode_frame, text="方形合并 (每行2张)", 
            variable=self.merge_mode, value="square"
        ).pack(side=tk.LEFT, padx=10)
        
        # 输出格式选择区域
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(format_frame, text="选择输出格式:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            format_frame, text="JPG", 
            variable=self.output_format, value="jpg"
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Radiobutton(
            format_frame, text="PNG", 
            variable=self.output_format, value="png"
        ).pack(side=tk.LEFT, padx=10)
        
        # 添加分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 拖放区域
        drop_frame = ttk.Frame(main_frame)
        drop_frame.pack(fill=tk.X, pady=10)
        
        self.drop_label = tk.Label(
            drop_frame, 
            text="拖放图片到这里 (支持任意数量)", 
            relief="groove", 
            height=8, 
            width=50,
            bg='white',
            fg='#555555',
            font=('Arial', 10)
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)
        
        # 绑定拖放事件
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        
        # 添加分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 日志显示区域
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(log_frame, text="操作日志:").pack(anchor=tk.W, pady=(0, 5))
        
        self.log_text = tk.Text(
            log_frame, 
            height=10, 
            state='disabled',
            bg='white',
            fg='#333333',
            font=('Arial', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.status_var.set(message)
        self.root.update()

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
            
        selected_mode = self.merge_mode.get()
        selected_format = self.output_format.get()
        
        self.log_message(f"开始处理 {len(valid_files)} 张图片...")
        self.log_message(f"合并模式: {'横向合并' if selected_mode == 'horizontal' else '方形合并 (每行2张)'}")
        self.log_message(f"输出格式: {selected_format.upper()}")
        
        try:
            output_path = self.merge_images(valid_files, selected_mode, selected_format)
            self.log_message(f"合并成功！保存路径: {output_path}")
        except Exception as e:
            self.log_message(f"处理出错: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")

    def merge_images(self, file_paths, mode, output_format):
        if mode == "horizontal":
            return self.merge_horizontal(file_paths, output_format)
        elif mode == "square":
            return self.merge_square(file_paths, output_format)
    
    def merge_horizontal(self, file_paths, output_format):
        images = []
        max_height = 0
        
        # 第一遍：加载所有图片并找到最大高度
        for path in file_paths:
            img = Image.open(path)
            images.append(img)
            if img.height > max_height:
                max_height = img.height
        
        # 调整所有图片到相同高度
        resized_images = []
        for img in images:
            w_percent = max_height / float(img.height)
            new_width = int(float(img.width) * float(w_percent))
            resized = img.resize((new_width, max_height), Image.LANCZOS)
            resized_images.append(resized)
        
        # 计算总宽度
        total_width = sum(img.width for img in resized_images)
        
        # 根据输出格式决定背景色
        if output_format == "png":
            # PNG支持透明，使用RGBA模式
            merged_img = Image.new('RGBA', (total_width, max_height), (255, 255, 255, 0))
        else:
            # JPG不支持透明，使用白色背景
            merged_img = Image.new('RGB', (total_width, max_height), (255, 255, 255))
        
        # 拼接图片
        x_offset = 0
        for img in resized_images:
            merged_img.paste(img, (x_offset, 0))
            x_offset += img.width
            
        return self.save_image(merged_img, file_paths[0], output_format)
    
    def merge_square(self, file_paths, output_format):
        images = []
        max_width = 0
        max_height = 0
        
        # 第一遍：加载所有图片并找到最大宽度和高度
        for path in file_paths:
            img = Image.open(path)
            images.append(img)
            if img.width > max_width:
                max_width = img.width
            if img.height > max_height:
                max_height = img.height
        
        # 计算网格尺寸
        cols = 2  # 每行2张图片
        rows = math.ceil(len(images) / cols)
        
        # 计算总尺寸
        total_width = max_width * cols
        total_height = max_height * rows
        
        # 根据输出格式决定背景色
        if output_format == "png":
            # PNG支持透明，使用RGBA模式
            merged_img = Image.new('RGBA', (total_width, total_height), (255, 255, 255, 0))
        else:
            # JPG不支持透明，使用白色背景
            merged_img = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        
        # 将图片放置到网格中
        for i, img in enumerate(images):
            # 计算位置
            row = i // cols
            col = i % cols
            x = col * max_width
            y = row * max_height
            
            # 调整图片大小以适应网格单元格
            resized_img = ImageOps.pad(img, (max_width, max_height), color='white', method=Image.LANCZOS)
            merged_img.paste(resized_img, (x, y))
            
        return self.save_image(merged_img, file_paths[0], output_format)
    
    def save_image(self, image, reference_path, output_format):
        # 获取第一个图片所在目录
        output_dir = os.path.dirname(reference_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 根据合并模式生成文件名
        mode = self.merge_mode.get()
        if mode == "horizontal":
            mode_str = "horizontal"
        else:
            mode_str = "grid"
        
        output_filename = f"merged_{mode_str}_{timestamp}.{output_format}"
        output_path = os.path.join(output_dir, output_filename)
        
        # 根据输出格式设置保存参数
        if output_format == "png":
            # PNG保存
            image.save(output_path, format="PNG")
        else:
            # JPG保存，设置质量为100
            image.save(output_path, format="JPEG", quality=100, subsampling=0)
            
        return output_path

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = ImageMergerApp(root)
    root.mainloop()
