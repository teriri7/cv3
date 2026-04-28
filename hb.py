# -*- coding: utf-8 -*-
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
        self.root.geometry("910x670")
        self.root.configure(bg='#f4f7fb')
        self.root.resizable(True, True)
        
        # 设置应用样式
        self.setup_styles()
        
        # 支持的图片格式
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
        self.max_images = 100
        
        # 状态变量 —— 默认改为自动
        self.merge_mode = tk.StringVar(value="auto")
        self.output_format = tk.StringVar(value="jpg")
        self.sort_by_time = tk.BooleanVar(value=True)
        
        # 创建界面
        self.create_widgets()
        self.setup_drag_highlight()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        self.root.configure(bg='#f4f7fb')
        style.configure('TFrame', background='#f4f7fb')
        style.configure('TLabelframe', background='#f4f7fb', foreground='#2c3e50', font=('Segoe UI', 10))
        style.configure('TLabelframe.Label', background='#f4f7fb', foreground='#2c3e50', font=('Segoe UI', 10, 'bold'))
        style.configure('Header.TLabel', background='#5a9bd5', foreground='white', 
                       font=('Segoe UI', 13, 'bold'), padding=10)
        style.configure('Accent.TButton', background='#5a9bd5', foreground='white', 
                       font=('Segoe UI', 10), padding=5)
        style.map('Accent.TButton',
                 background=[('active', '#4a8bc5'), ('pressed', '#3a7bb5')])
        style.configure('TRadiobutton', background='#f4f7fb', font=('Segoe UI', 10), foreground='#2c3e50')
        style.configure('TLabel', background='#f4f7fb', foreground='#2c3e50', font=('Segoe UI', 9))
        style.configure('Log.TFrame', relief='solid', borderwidth=1, background='#ffffff')
        
    def create_widgets(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        header = ttk.Label(main_container, text="🖼️ 图片合并工具", style='Header.TLabel')
        header.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        control_card = ttk.Frame(main_container, relief='flat')
        control_card.pack(fill=tk.X, pady=5)
        
        # 排序方式
        sort_frame = ttk.LabelFrame(control_card, text="排序方式", padding=8)
        sort_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(sort_frame, text="📅 按修改时间 (精确到毫秒)", 
                       variable=self.sort_by_time, value=True).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(sort_frame, text="🔤 按文件名 (数字/字母顺序)", 
                       variable=self.sort_by_time, value=False).pack(side=tk.LEFT, padx=10)
        
        # 合并模式与输出格式
        settings_frame = ttk.Frame(control_card)
        settings_frame.pack(fill=tk.X, pady=8)
        
        mode_frame = ttk.LabelFrame(settings_frame, text="合并模式", padding=8)
        mode_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        modes = [
            ("🤖 自动 (智能布局)", "auto"),
            ("➡️ 横向合并", "horizontal"),
            ("🟫 网格合并 (2×n)", "grid2"),
            ("📊 网格合并 (3×n)", "grid3"),
            ("🗂️ 网格合并 (4×n)", "grid4")
        ]
        for text, value in modes:
            ttk.Radiobutton(mode_frame, text=text, variable=self.merge_mode, 
                           value=value).pack(side=tk.LEFT, padx=3)
        
        format_frame = ttk.LabelFrame(settings_frame, text="输出格式", padding=8)
        format_frame.pack(side=tk.RIGHT, fill=tk.X)
        ttk.Radiobutton(format_frame, text="JPG (高质量)", variable=self.output_format, 
                       value="jpg").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(format_frame, text="PNG (无损)", variable=self.output_format, 
                       value="png").pack(side=tk.LEFT, padx=8)
        
        # 拖放区域
        drop_frame = ttk.Frame(main_container)
        drop_frame.pack(fill=tk.BOTH, expand=True, pady=12)
        self.drop_label = tk.Label(
            drop_frame,
            text="📂 拖放图片或文件夹至此\n(支持格式: JPG, PNG, WEBP, BMP)",
            relief="groove",
            bg='#ffffff',
            fg='#7f8c8d',
            font=('Segoe UI', 11),
            bd=2,
            highlightthickness=0
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True, ipady=30)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        
        # 日志区域
        log_container = ttk.LabelFrame(main_container, text="操作日志", padding=5)
        log_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        self.log_text = tk.Text(
            log_container,
            height=8,
            state='disabled',
            bg='#ffffff',
            fg='#2c3e50',
            font=('Consolas', 9),
            wrap=tk.WORD,
            relief='flat',
            borderwidth=0
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(log_container, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        info_label = ttk.Label(main_container, 
            text="✨ 合并后的图片保存在第一张图片所在文件夹，保持原始画质\n✨ 分隔线厚度 = 最终画布最长边 × 0.2% (网格中仅在有相邻图片处绘制，交叉处自动填充黑线)",
            font=('Segoe UI', 8), foreground='#7f8c8d')
        info_label.pack(pady=(8, 0))

    def setup_drag_highlight(self):
        def on_enter(e):
            self.drop_label.config(bg='#eef4fc', fg='#5a9bd5')
        def on_leave(e):
            self.drop_label.config(bg='#ffffff', fg='#7f8c8d')
        self.drop_label.bind("<Enter>", on_enter)
        self.drop_label.bind("<Leave>", on_leave)

    def log_message(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = "✅" if "成功" in message else "⚠️" if "忽略" in message or "警告" in message else "📌"
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{timestamp}] {prefix} {message}\n")
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
            self.log_message("至少需要 1 张有效图片")
            return
        valid_files = self.sort_files(valid_files)
        if len(valid_files) > self.max_images:
            self.log_message(f"图片数量超过上限 {self.max_images}，仅处理前 {self.max_images} 张")
            valid_files = valid_files[:self.max_images]
        mode_names = {
            "auto": "自动 (智能布局)",
            "horizontal": "横向合并",
            "grid2": "网格合并 (2×n)",
            "grid3": "网格合并 (3×n)",
            "grid4": "网格合并 (4×n)"
        }
        sort_desc = "按修改时间(升序)" if self.sort_by_time.get() else "按文件名排序"
        self.log_message(f"开始处理 {len(valid_files)} 张图片 | 排序: {sort_desc}")
        self.log_message(f"合并模式: {mode_names[self.merge_mode.get()]}")
        self.log_message(f"输出格式: {self.output_format.get().upper()}")
        try:
            output_path = self.merge_images(valid_files)
            self.log_message(f"合并成功！文件保存至: {output_path}")
        except Exception as e:
            self.log_message(f"处理出错: {str(e)}", level="ERROR")

    def sort_files(self, file_paths):
        if self.sort_by_time.get():
            file_paths.sort(key=lambda x: os.path.getmtime(x))
            return file_paths
        else:
            if self.all_files_numeric(file_paths):
                file_paths.sort(key=lambda x: self.extract_number(os.path.basename(x)))
            else:
                file_paths.sort(key=lambda x: os.path.basename(x))
            return file_paths

    def all_files_numeric(self, file_paths):
        for path in file_paths:
            name = os.path.splitext(os.path.basename(path))[0]
            if not re.match(r'^\d+$', name):
                return False
        return True

    def extract_number(self, filename):
        name = os.path.splitext(filename)[0]
        return int(name) if name.isdigit() else 0

    def determine_auto_mode(self, images):
        """自动选择合并模式：只要存在竖屏图片（高>宽）则横向合并，否则网格2列合并"""
        for img in images:
            if img.height > img.width:
                return "horizontal"
        return "grid2"

    def merge_images(self, file_paths):
        images = []
        for path in file_paths:
            img = Image.open(path)
            if self.output_format.get() == "png" and img.mode != "RGBA":
                img = img.convert("RGBA")
            images.append(img)
        mode = self.merge_mode.get()
        if mode == "auto":
            actual_mode = self.determine_auto_mode(images)
            mode_names = {
                "horizontal": "横向合并",
                "grid2": "网格合并 (2×n)"
            }
            self.log_message(f"自动选择布局: {mode_names[actual_mode]}")
        else:
            actual_mode = mode
        
        if actual_mode == "horizontal":
            return self.merge_horizontal(images, file_paths, mode=actual_mode)
        elif actual_mode == "grid2":
            return self.merge_grid(images, file_paths, columns=2, mode=actual_mode)
        elif actual_mode == "grid3":
            return self.merge_grid(images, file_paths, columns=3, mode=actual_mode)
        elif actual_mode == "grid4":
            return self.merge_grid(images, file_paths, columns=4, mode=actual_mode)
        else:
            raise ValueError("未知的合并模式")

    def merge_horizontal(self, images, file_paths, mode="horizontal"):
        if not images:
            raise ValueError("没有图片可合并")
        # 统一高度
        target_height = max(img.height for img in images)
        resized_images = []
        for img in images:
            ratio = target_height / img.height
            new_width = int(img.width * ratio)
            resized = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
            resized_images.append(resized)
        
        # 初步计算总宽（无分隔线）
        total_width_no_sep = sum(img.width for img in resized_images)
        # 分隔线厚度 = 最长边 × 0.2%
        max_side = max(total_width_no_sep, target_height)
        sep_thick = max(1, int(max_side * 0.002))
        
        total_width = total_width_no_sep + sep_thick * (len(resized_images) - 1)
        
        bg_color = (255, 255, 255) if self.output_format.get() == "jpg" else (0, 0, 0, 0)
        if self.output_format.get() == "png":
            merged = Image.new('RGBA', (total_width, target_height), bg_color)
        else:
            merged = Image.new('RGB', (total_width, target_height), bg_color)
        
        x_offset = 0
        for i, img in enumerate(resized_images):
            merged.paste(img, (x_offset, 0))
            x_offset += img.width
            if i < len(resized_images) - 1:
                line_color = (0, 0, 0, 255) if self.output_format.get() == "png" else (0, 0, 0)
                # 绘制垂直黑线区域
                for w in range(sep_thick):
                    for y in range(target_height):
                        merged.putpixel((x_offset + w, y), line_color)
                x_offset += sep_thick
        return self.save_image(merged, file_paths[0], mode=mode)

    def merge_grid(self, images, file_paths, columns, mode="grid"):
        if not images:
            raise ValueError("没有图片可合并")
        rows = math.ceil(len(images) / columns)
        # 单元格基准尺寸（最大宽高）
        cell_w = max(img.width for img in images)
        cell_h = max(img.height for img in images)
        
        # 初步画布尺寸（无分隔线）
        canvas_w_no_sep = columns * cell_w
        canvas_h_no_sep = rows * cell_h
        max_side_no_sep = max(canvas_w_no_sep, canvas_h_no_sep)
        sep_thick = max(1, int(max_side_no_sep * 0.002))
        
        total_width = columns * cell_w + (columns - 1) * sep_thick
        total_height = rows * cell_h + (rows - 1) * sep_thick
        
        bg_color = (255, 255, 255) if self.output_format.get() == "jpg" else (0, 0, 0, 0)
        if self.output_format.get() == "png":
            merged = Image.new('RGBA', (total_width, total_height), bg_color)
        else:
            merged = Image.new('RGB', (total_width, total_height), bg_color)
        
        # 存储每个单元格的图片对象（填充后）
        placed_images = [[None] * columns for _ in range(rows)]
        for idx, img in enumerate(images):
            row = idx // columns
            col = idx % columns
            padded = ImageOps.pad(img, (cell_w, cell_h),
                                 color='white' if self.output_format.get() == "jpg" else (0, 0, 0, 0),
                                 method=Image.Resampling.LANCZOS)
            placed_images[row][col] = padded
        
        # 放置图片
        for row in range(rows):
            for col in range(columns):
                if placed_images[row][col] is not None:
                    x = col * (cell_w + sep_thick)
                    y = row * (cell_h + sep_thick)
                    merged.paste(placed_images[row][col], (x, y))
        
        line_color = (0, 0, 0, 255) if self.output_format.get() == "png" else (0, 0, 0)
        
        # 1. 先绘制所有垂直分隔线（存在相邻图片时绘制）
        for row in range(rows):
            for col in range(columns - 1):
                if placed_images[row][col] is not None or placed_images[row][col+1] is not None:
                    line_x = (col + 1) * cell_w + col * sep_thick
                    y_start = row * (cell_h + sep_thick)
                    y_end = y_start + cell_h
                    for w in range(sep_thick):
                        for y in range(y_start, y_end):
                            merged.putpixel((line_x + w, y), line_color)
        
        # 2. 绘制所有水平分隔线（存在相邻图片时绘制）
        for row in range(rows - 1):
            for col in range(columns):
                if placed_images[row][col] is not None or placed_images[row+1][col] is not None:
                    line_y = (row + 1) * cell_h + row * sep_thick
                    x_start = col * (cell_w + sep_thick)
                    x_end = x_start + cell_w
                    for h in range(sep_thick):
                        for x in range(x_start, x_end):
                            merged.putpixel((x, line_y + h), line_color)
        
        # 3. 交叉点区域强制涂黑，确保完全覆盖
        for col in range(columns - 1):
            for row in range(rows - 1):
                v_line_x = (col + 1) * cell_w + col * sep_thick
                h_line_y = (row + 1) * cell_h + row * sep_thick
                for dx in range(sep_thick):
                    for dy in range(sep_thick):
                        set_x = v_line_x + dx
                        set_y = h_line_y + dy
                        if 0 <= set_x < total_width and 0 <= set_y < total_height:
                            merged.putpixel((set_x, set_y), line_color)
        
        return self.save_image(merged, file_paths[0], mode=mode)

    def save_image(self, image, reference_path, mode=None):
        output_dir = os.path.dirname(reference_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        actual_mode = mode if mode is not None else self.merge_mode.get()
        mode_short = {
            "horizontal": "horiz",
            "grid2": "grid2",
            "grid3": "grid3",
            "grid4": "grid4",
            "auto": "auto"    # 实际不会用到，占位
        }.get(actual_mode, "merged")
        fmt = self.output_format.get()
        filename = f"merged_{mode_short}_{timestamp}.{fmt}"
        filepath = os.path.join(output_dir, filename)
        if fmt == "jpg":
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(filepath, quality=100, subsampling=0, optimize=False)
        else:
            if image.mode != "RGBA":
                image = image.convert("RGBA")
            image.save(filepath, format="PNG", compress_level=0)
        return filepath

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = ImageMergerApp(root)
    root.mainloop()
