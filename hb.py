import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageOps
import os
from datetime import datetime
import math
import re

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
        self.max_images = 100  # 设置一个较高的上限避免内存问题
        self.merge_mode = tk.StringVar(value="horizontal")  # 默认为横向合并
        self.output_format = tk.StringVar(value="jpg")  # 默认输出格式为JPG

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
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(mode_frame, text="选择合并方式:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            mode_frame, text="横向合并", 
            variable=self.merge_mode, value="horizontal"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            mode_frame, text="网格合并 (2×n)", 
            variable=self.merge_mode, value="square"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            mode_frame, text="网格合并 (3×n)", 
            variable=self.merge_mode, value="grid3"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            mode_frame, text="网格合并 (4×n)", 
            variable=self.merge_mode, value="grid4"
        ).pack(side=tk.LEFT, padx=5)
        
        # 输出格式选择区域
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="输出格式:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Radiobutton(
            format_frame, text="JPG", 
            variable=self.output_format, value="jpg"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            format_frame, text="PNG", 
            variable=self.output_format, value="png"
        ).pack(side=tk.LEFT, padx=5)
        
        # 添加分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 拖放区域
        drop_frame = ttk.Frame(main_frame)
        drop_frame.pack(fill=tk.X, pady=10)
        
        self.drop_label = tk.Label(
            drop_frame, 
            text="拖放图片到这里",
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
            height=8, 
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
            
        selected_mode = self.merge_mode.get()
        mode_names = {
            "horizontal": "横向合并",
            "square": "网格合并 (2×n)",
            "grid3": "网格合并 (3×n)",
            "grid4": "网格合并 (4×n)"
        }
        
        # 检查不同模式下的图片数量要求
        if selected_mode == "grid4" and len(valid_files) < 1:
            self.log_message("错误：网格合并(4×n)至少需要1张图片")
            return
        
        # 排序图片：如果所有文件名都是纯数字，则按数字排序，否则按文件名排序
        if self.all_files_numeric(valid_files):
            valid_files.sort(key=lambda x: self.extract_number(os.path.basename(x)))
            self.log_message("已按文件名数字顺序排序图片")
        else:
            valid_files.sort(key=lambda x: os.path.basename(x))
            self.log_message("已按文件名顺序排序图片")
        
        # 限制最大图片数量以避免内存问题
        if len(valid_files) > self.max_images:
            self.log_message(f"警告：图片数量超过{self.max_images}张，只处理前{self.max_images}张")
            valid_files = valid_files[:self.max_images]

        self.log_message(f"开始处理 {len(valid_files)} 张图片...")
        self.log_message(f"合并模式: {mode_names[selected_mode]}")
        self.log_message(f"输出格式: {self.output_format.get().upper()}")
        
        try:
            output_path = self.merge_images(valid_files, selected_mode)
            self.log_message(f"合并成功！保存路径: {output_path}")
        except Exception as e:
            self.log_message(f"处理出错: {str(e)}")

    def all_files_numeric(self, file_paths):
        """检查所有文件名是否都是纯数字（不含扩展名）"""
        for path in file_paths:
            filename = os.path.splitext(os.path.basename(path))[0]
            if not re.match(r'^\d+$', filename):
                return False
        return True

    def extract_number(self, filename):
        """从文件名中提取数字（不含扩展名）"""
        name = os.path.splitext(filename)[0]
        return int(name) if name.isdigit() else 0

    def merge_images(self, file_paths, mode):
        images = []
        for path in file_paths:
            img = Image.open(path)
            # 如果输出格式是PNG，确保图片有alpha通道
            if self.output_format.get() == "png" and img.mode != "RGBA":
                img = img.convert("RGBA")
            images.append(img)
        
        if mode == "horizontal":
            return self.merge_horizontal(images, file_paths)
        elif mode == "square":
            return self.merge_square(images, file_paths)
        elif mode == "grid3":
            return self.merge_grid(images, file_paths, 3)
        elif mode == "grid4":
            return self.merge_grid(images, file_paths, 4)
    
    def merge_horizontal(self, images, file_paths):
        # 计算所有图片的最大高度
        max_height = max(img.height for img in images)
        
        # 调整所有图片到相同高度
        resized_images = []
        for img in images:
            w_percent = max_height / float(img.height)
            new_width = int(float(img.width) * float(w_percent))
            resized = img.resize((new_width, max_height), Image.LANCZOS)
            resized_images.append(resized)
        
        # 计算总宽度
        total_width = sum(img.width for img in resized_images)
        
        # 根据输出格式创建新图片
        output_format = self.output_format.get()
        if output_format == "png":
            merged_img = Image.new('RGBA', (total_width, max_height), (0, 0, 0, 0))
        else:
            merged_img = Image.new('RGB', (total_width, max_height), (255, 255, 255))
        
        # 拼接图片
        x_offset = 0
        for img in resized_images:
            merged_img.paste(img, (x_offset, 0))
            x_offset += img.width
            
        return self.save_image(merged_img, file_paths[0])
    
    def merge_square(self, images, file_paths):
        # 计算网格中每个单元格的大小
        cell_width = max(img.width for img in images) if images else 100
        cell_height = max(img.height for img in images) if images else 100
        
        # 创建2x2网格
        grid_width = cell_width * 2
        grid_height = cell_height * 2
        
        # 根据输出格式创建新图片
        output_format = self.output_format.get()
        if output_format == "png":
            merged_img = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))
        else:
            merged_img = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
        
        # 将图片放置到网格中
        positions = [
            (0, 0),             # 第一行第一列
            (cell_width, 0),    # 第一行第二列
            (0, cell_height),   # 第二行第一列
            (cell_width, cell_height)  # 第二行第二列
        ]
        
        for i in range(min(len(images), 4)):
            # 调整图片大小以适应网格单元格
            resized_img = ImageOps.pad(images[i], (cell_width, cell_height), 
                                       color='white' if output_format == "jpg" else (0, 0, 0, 0), 
                                       method=Image.LANCZOS)
            merged_img.paste(resized_img, positions[i])
            
        return self.save_image(merged_img, file_paths[0])
    
    def merge_grid(self, images, file_paths, columns):
        """通用的网格合并方法"""
        if not images:
            raise ValueError("没有图片可合并")
            
        # 计算网格的行数
        num_images = len(images)
        rows = math.ceil(num_images / columns)
        
        # 计算所有图片的最大宽度和高度
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # 创建网格图片
        grid_width = max_width * columns
        grid_height = max_height * rows
        
        # 根据输出格式创建新图片
        output_format = self.output_format.get()
        if output_format == "png":
            merged_img = Image.new('RGBA', (grid_width, grid_height), (0, 0, 0, 0))
        else:
            merged_img = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
        
        # 按顺序放置图片
        for i, img in enumerate(images):
            # 计算当前图片的位置
            row = i // columns
            col = i % columns
            
            # 计算坐标
            x = col * max_width
            y = row * max_height
            
            # 调整图片大小以适应网格单元格
            resized_img = ImageOps.pad(img, (max_width, max_height), 
                                      color='white' if output_format == "jpg" else (0, 0, 0, 0), 
                                      method=Image.LANCZOS)
            merged_img.paste(resized_img, (x, y))
            
        return self.save_image(merged_img, file_paths[0])
    
    def save_image(self, image, reference_path):
        # 获取第一个图片所在目录
        output_dir = os.path.dirname(reference_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 根据模式和格式生成文件名
        mode_names = {
            "horizontal": "horizontal",
            "square": "square",
            "grid3": "grid3",
            "grid4": "grid4"
        }
        mode = self.merge_mode.get()
        format_ext = self.output_format.get()
        output_filename = f"merged_{mode_names[mode]}_{timestamp}.{format_ext}"
        
        output_path = os.path.join(output_dir, output_filename)
        
        # 保存图片
        if format_ext == "jpg":
            # 确保图片是RGB模式
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(output_path, quality=100, subsampling=0)
        else:  # PNG格式
            # 确保图片是RGBA模式
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            image.save(output_path, format="PNG")
            
        return output_path

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = ImageMergerApp(root)
    root.mainloop()
