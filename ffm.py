import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import threading

class VideoScreenshotTool:
    def __init__(self, root):
        self.root = root
        self.root.title("视频分片截图工具")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # 设置中文字体
        self.font = ('SimHei', 10)
        
        # 创建界面元素
        self.create_widgets()
        
        # 视频文件扩展名列表
        self.VIDEO_EXTS = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']
        
    def create_widgets(self):
        # 主框架
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 介绍标签
        intro_label = tk.Label(main_frame, text="视频分片截图工具", font=('SimHei', 16, 'bold'))
        intro_label.pack(pady=(0, 20))
        
        # 功能说明
        desc_label = tk.Label(main_frame, text="该程序会对当前文件夹内的所有视频文件进行分片截图", font=self.font, wraplength=400)
        desc_label.pack(pady=(0, 10))
        
        # 截图间隔说明
        interval_label = tk.Label(main_frame, text="截图间隔(秒):", font=self.font)
        interval_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.interval_var = tk.StringVar(value="0.5")
        interval_entry = tk.Entry(main_frame, textvariable=self.interval_var, font=self.font, width=10)
        interval_entry.pack(anchor=tk.W)
        
        # 运行按钮
        run_button = tk.Button(main_frame, text="开始截图", font=self.font, 
                              command=self.run_screenshot, bg="#4CAF50", fg="white", 
                              width=15, height=1, cursor="hand2")
        run_button.pack(pady=30)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = tk.Label(main_frame, textvariable=self.status_var, font=self.font, fg="gray")
        status_label.pack(side=tk.BOTTOM, pady=10)
    
    def run_screenshot(self):
        # 获取截图间隔
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("输入错误", "请输入一个有效的正浮点数作为截图间隔！")
            return
        
        # 禁用按钮防止重复点击
        for widget in self.root.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Button):
                    child.config(state=tk.DISABLED)
        self.status_var.set("正在处理...")
        
        # 在新线程中执行截图操作
        threading.Thread(target=self.process_videos, args=(interval,), daemon=True).start()
    
    def process_videos(self, interval):
        try:
            # 获取当前文件夹路径
            current_dir = os.getcwd()
            
            # 获取所有视频文件
            video_files = []
            for file in os.listdir(current_dir):
                if any(file.lower().endswith(ext) for ext in self.VIDEO_EXTS):
                    video_files.append(file)
            
            if not video_files:
                self.status_var.set("就绪")
                messagebox.showinfo("完成", "当前文件夹内未找到视频文件！")
                self.enable_buttons()
                return
            
            total_videos = len(video_files)
            processed = 0
            
            # 处理每个视频文件
            for video_file in video_files:
                try:
                    self.process_single_video(video_file, interval)
                    processed += 1
                    self.status_var.set(f"已处理: {processed}/{total_videos}")
                except Exception as e:
                    print(f"处理视频 {video_file} 时出错: {str(e)}")
            
            self.status_var.set("就绪")
            messagebox.showinfo("完成", f"所有视频处理完成！共处理 {total_videos} 个视频文件。")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            self.status_var.set("就绪")
        finally:
            self.enable_buttons()
    
    def process_single_video(self, video_file, interval):
        # 创建视频对应的文件夹
        video_name = os.path.splitext(video_file)[0]
        output_dir = os.path.join(os.getcwd(), video_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建ffmpeg命令
        cmd = [
            "ffmpeg",
            "-i", os.path.abspath(video_file),
            "-vf", f"fps=1/{interval}",
            os.path.join(output_dir, f"{video_name}_%04d.jpg")
        ]
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg 错误: {result.stderr}")
            raise Exception(f"处理视频时出错: {result.stderr}")
    
    def enable_buttons(self):
        # 重新启用按钮
        for widget in self.root.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, tk.Button):
                    child.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoScreenshotTool(root)
    root.mainloop()    
