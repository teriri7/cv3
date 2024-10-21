import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, UnidentifiedImageError
from tkinter import scrolledtext

# 创建一个png文件夹用于保存转换后的文件
output_dir = "png"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 创建一个函数来将图片转换为PNG
def convert_to_png(file_path):
    try:
        # 使用Pillow库打开图片
        img = Image.open(file_path)
        # 提取文件名（无扩展名）
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        # 保存为PNG格式
        output_path = os.path.join(output_dir, f"{file_name}.png")
        img.save(output_path, "PNG")
        return output_path
    except UnidentifiedImageError:
        log_message(f"错误: 无法识别文件 {file_path}")
        return None

# 当用户拖入文件时调用的函数
def on_drop(event):
    file_paths = root.tk.splitlist(event.data)
    for file_path in file_paths:
        if os.path.isfile(file_path):
            output_path = convert_to_png(file_path)
            if output_path:
                log_message(f"成功: 图片已转换为 {output_path}")

# 日志信息显示
def log_message(message):
    log_area.config(state=tk.NORMAL)  # 使Text控件可编辑
    log_area.insert(tk.END, message + "\n")
    log_area.config(state=tk.DISABLED)  # 禁止用户编辑日志区域
    log_area.yview(tk.END)  # 自动滚动到底部

# 创建TkinterDnD窗口
root = TkinterDnD.Tk()
root.title("图片格式转换器")
root.geometry("600x400")  # 调整窗口大小
root.config(bg='#34495e')

# 添加一个提示标签
label = tk.Label(root, text="请将图片拖入此窗口\n自动转换为PNG格式", bg='#34495e', fg='white', font=('Arial', 20, 'bold'))
label.pack(pady=40)

# 创建一个滚动文本框，用于显示日志信息
log_area = scrolledtext.ScrolledText(root, height=8, bg='#ecf0f1', font=('Arial', 12), state=tk.DISABLED, wrap=tk.WORD)
log_area.pack(fill=tk.BOTH, padx=20, pady=20, expand=True)

# 绑定拖入事件
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# 运行窗口
root.mainloop()
