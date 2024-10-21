import os
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, UnidentifiedImageError
from tkinter import messagebox

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
        messagebox.showerror("错误", f"无法识别文件: {file_path}")
        return None

# 当用户拖入文件时调用的函数
def on_drop(event):
    file_paths = root.tk.splitlist(event.data)
    for file_path in file_paths:
        if os.path.isfile(file_path):
            output_path = convert_to_png(file_path)
            if output_path:
                messagebox.showinfo("成功", f"图片已转换为PNG: {output_path}")

# 创建TkinterDnD窗口
root = TkinterDnD.Tk()
root.title("图片格式转换器")
root.geometry("400x300")
root.config(bg='#2c3e50')

# 添加一个提示标签
label = tk.Label(root, text="请将图片拖入此窗口\n自动转换为PNG格式", bg='#2c3e50', fg='white', font=('Arial', 16))
label.pack(pady=80)

# 绑定拖入事件
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# 运行窗口
root.mainloop()
