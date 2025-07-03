import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageOps
import os
from datetime import datetime
import math

class ImageMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片合并工具")
        self.root.geometry("600x500")
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
        self.max_images = 12  # 增加最大图片数量以支持网格合并
        self.merge_mode = tk.StringVar(value="horizontal")  # 默认为横向合并

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
            mode_frame, text="横向合并", 
            variable=self.merge_mode, value="horizontal"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            mode_frame, text="方形合并 (2×2)", 
            variable=self.merge_mode, value="square"
        ).pack(side=tk.LEFT, padx=5)
        
        # 添加新的网格合并选项
        ttk.Radiobutton(
            mode_frame, text="网格合并 (3×n)", 
            variable=self.merge_mode, value="grid3"
        ).pack(side=tk.LEFT, padx=5)
        
        # 添加分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 拖放区域
        drop_frame = ttk.Frame(main_frame)
        drop_frame.pack(fill=tk.X, pady=10)
        
        self.drop_label = tk.Label(
            drop_frame, 
            text="拖放图片到这里 (最多12张)",
            relief="groove", 
            height=8, 
            width=50,
            bg='white',
            fg='#555555',
            font=('Arial', 10)  # 修复语法错误：移除多余的括号
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
            "square": "方形合并 (2×2)",
            "grid3": "网格合并 (3×n)"
        }
        
        # 检查不同模式下的图片数量要求
        if selected_mode == "square":
            if len(valid_files) != 4:
                self.log_message("错误：方形合并需要恰好4张图片")
                return
        elif selected_mode == "grid3":
            if len(valid_files) < 3:
                self.log_message("错误：网格合并至少需要3张图片")
                return
        elif len(valid_files) > self.max_images:
            self.log_message(f"错误：最多支持{self.max_images}张图片")
            valid_files = valid_files[:self.max_images]

        self.log_message(f"开始处理 {len(valid_files)} 张图片...")
        self.log_message(f"合并模式: {mode_names[selected_mode]}")
        
        try:
            output_path = self.merge_images(valid_files, selected_mode)
            self.log_message(f"合并成功！保存路径: {output_path}")
        except Exception as e:
            self.log_message(f"处理出错: {str(e)}")

    def merge_images(self, file_paths, mode):
        images = []
        for path in file_paths:
            img = Image.open(path)
            images.append(img)
        
        if mode == "horizontal":
            return self.merge_horizontal(images, file_paths)
        elif mode == "square":
            return self.merge_square(images, file_paths)
        elif mode == "grid3":
            return self.merge_grid3(images, file_paths)
    
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
        
        # 创建新图片
        merged_img = Image.new('RGB', (total_width, max_height), (255, 255, 255))
        
        # 拼接图片
        x_offset = 0
        for img in resized_images:
            merged_img.paste(img, (x_offset, 0))
            x_offset += img.width
            
        return self.save_image(merged_img, file_paths[0])
    
    def merge_square(self, images, file_paths):
        # 计算网格中每个单元格的大小
        cell_width = max(img.width for img in images)
        cell_height = max(img.height for img in images)
        
        # 创建2x2网格
        grid_width = cell_width * 2
        grid_height = cell_height * 2
        
        # 创建新图片
        merged_img = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
        
        # 将图片放置到网格中
        positions = [
            (0, 0),             # 第一行第一列
            (cell_width, 0),    # 第一行第二列
            (0, cell_height),   # 第二行第一列
            (cell_width, cell_height)  # 第二行第二列
        ]
        
        for i, img in enumerate(images):
            # 调整图片大小以适应网格单元格
            resized_img = ImageOps.pad(img, (cell_width, cell_height), color='white', method=Image.LANCZOS)
            merged_img.paste(resized_img, positions[i])
            
        return self.save_image(merged_img, file_paths[0])
    
    def merge_grid3(self, images, file_paths):
        # 计算网格的行数（每行3张图片）
        num_images = len(images)
        rows = math.ceil(num_images / 3)
        
        # 计算所有图片的最大宽度和高度
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        # 创建网格图片
        grid_width = max_width * 3
        grid_height = max_height * rows
        
        merged_img = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))
        
        # 按顺序放置图片
        for i, img in enumerate(images):
            # 计算当前图片的位置
            row = i // 3
            col = i % 3
            
            # 计算坐标
            x = col * max_width
            y = row * max_height
            
            # 调整图片大小以适应网格单元格
            resized_img = ImageOps.pad(img, (max_width, max_height), color='white', method=Image.LANCZOS)
            merged_img.paste(resized_img, (x, y))
            
        return self.save_image(merged_img, file_paths[0])
    
    def save_image(self, image, reference_path):
        # 获取第一个图片所在目录
        output_dir = os.path.dirname(reference_path)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 根据模式生成文件名
        mode_names = {
            "horizontal": "horizontal",
            "square": "square",
            "grid3": "grid3"
        }
        mode = self.merge_mode.get()
        output_filename = f"merged_{mode_names[mode]}_{timestamp}.jpg"
        
        output_path = os.path.join(output_dir, output_filename)
        
        # 设置质量为100
        image.save(output_path, quality=100, subsampling=0)
        return output_path

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = ImageMergerApp(root)
    root.mainloop()
