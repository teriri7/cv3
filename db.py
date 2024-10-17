import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import os
import threading

# 读取链接函数
def read_links(file_name):
    with open(file_name, 'r') as f:
        return [line.strip() for line in f.readlines()]

# 刷新图片显示
def refresh_images():
    global current_index
    loading_feedback()  # 添加加载提示
    if current_index < len(links1) and current_index < len(links2):
        thread1 = threading.Thread(target=load_image_in_thread, args=(1, image_label1, links1[current_index], "1.txt"))
        thread2 = threading.Thread(target=load_image_in_thread, args=(2, image_label2, links2[current_index], "2.txt"))
        thread1.start()
        thread2.start()
    else:
        messagebox.showwarning("Warning", "图片处理完成")
    reset_feedback()  # 恢复按钮状态

# 在线程中加载图片
def load_image_in_thread(side, label, link, file_name):
    try:
        response = requests.get(link)
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((300, 300), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        # 使用 Tkinter 的 after 方法让主线程更新图片
        root.after(0, lambda: update_image(label, photo))
        
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", f"Failed to load image from {file_name}: {str(e)}"))

# 更新图片（必须在主线程中调用）
def update_image(label, photo):
    label.config(image=photo)
    label.image = photo  # 保持引用，防止被垃圾回收

# 写入out.txt
def write_to_file(action):
    global current_index
    if current_index < len(links1) and current_index < len(links2):
        with open("out.txt", "a", encoding="utf-8") as f:
            f.write(f"{action}\n")
        current_index += 1
        refresh_images()
    else:
        messagebox.showinfo("Info", "All images processed.")

# 换衣服
def change_clothes():
    write_to_file("穿衣（指定的衣服穿模特身上）")

# 换背景
def change_background():
    write_to_file("换背景（带人模特图换背景）")

# 其他操作
def other_action():
    write_to_file("其他")

# 读取当前处理的行号
def read_current_index():
    if os.path.exists("out.txt"):
        with open("out.txt", "r", encoding="utf-8") as f:
            return len(f.readlines())
    return 0

# 加载反馈
def loading_feedback():
    clothes_button.config(text="加载中...", state="disabled")
    background_button.config(text="加载中...", state="disabled")
    other_button.config(text="加载中...", state="disabled")
    refresh_button.config(text="加载中...", state="disabled")

# 恢复反馈
def reset_feedback():
    clothes_button.config(text="换衣服", state="normal")
    background_button.config(text="换背景", state="normal")
    other_button.config(text="其他", state="normal")
    refresh_button.config(text="刷新", state="normal")

# 创建主窗口
root = tk.Tk()
root.title("图片场景判断")
root.geometry("800x600")  # 增大窗口尺寸

# 读取图片链接
links1 = read_links("1.txt")
links2 = read_links("2.txt")

# 初始化当前处理的行号
current_index = read_current_index()

# 图片显示框
image_label1 = tk.Label(root)
image_label2 = tk.Label(root)

# 使用 grid 布局来安排图片和按钮
image_label1.grid(row=0, column=0, padx=20, pady=20)
image_label2.grid(row=0, column=1, padx=20, pady=20)

# 按钮区
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=2, pady=30)

# 使用 ttk 美化按钮，并放大按钮
style = ttk.Style()
style.configure('TButton', font=('Arial', 14), padding=10)  # 设置按钮的字体大小和内边距

refresh_button = ttk.Button(button_frame, text="刷新", command=refresh_images, style='TButton')
refresh_button.grid(row=0, column=0, padx=10)

clothes_button = ttk.Button(button_frame, text="换衣服", command=change_clothes, style='TButton')
clothes_button.grid(row=0, column=1, padx=10)

background_button = ttk.Button(button_frame, text="换背景", command=change_background, style='TButton')
background_button.grid(row=0, column=2, padx=10)

other_button = ttk.Button(button_frame, text="其他", command=other_action, style='TButton')
other_button.grid(row=0, column=3, padx=10)

# 显示初始图片
refresh_images()

# 运行主循环
root.mainloop()
