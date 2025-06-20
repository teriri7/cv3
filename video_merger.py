import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import subprocess
import re
from datetime import datetime
import sys
import threading

class VideoMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频合并工具")
        self.root.geometry("700x550")
        self.root.configure(bg='#f0f0f0')
        
        # 设置应用样式
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('Header.TLabel', background='#4a6fa5', foreground='white', font=('Arial', 12, 'bold'))
        self.style.configure('TButton', font=('Arial', 10), background='#4a6fa5')
        self.style.map('TButton', background=[('active', '#3a5a8f')])
        
        # 支持的视频格式
        self.supported_formats = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
        
        # 设置FFmpeg路径
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ffmpeg_path = os.path.join(self.base_dir, "ffmpeg", "bin", "ffmpeg.exe")
        
        # 检查FFmpeg是否存在
        if not os.path.exists(self.ffmpeg_path):
            self.ffmpeg_path = "ffmpeg"  # 尝试使用系统PATH中的ffmpeg
            self.log_message("警告：未找到内置FFmpeg，将尝试使用系统PATH中的ffmpeg")
        
        # 创建GUI组件
        self.create_widgets()
        
        # 设置拖放区域
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.handle_drop)
        
        # 处理状态
        self.processing = False
        self.process_thread = None

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        header = ttk.Label(main_frame, text="视频合并工具", style='Header.TLabel')
        header.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        # FFmpeg信息
        ffmpeg_frame = ttk.Frame(main_frame)
        ffmpeg_frame.pack(fill=tk.X, pady=5)
        
        ffmpeg_info = f"FFmpeg路径: {self.ffmpeg_path}"
        self.ffmpeg_label = ttk.Label(ffmpeg_frame, text=ffmpeg_info, font=('Arial', 9))
        self.ffmpeg_label.pack(side=tk.LEFT)
        
        # 检查按钮
        check_btn = ttk.Button(ffmpeg_frame, text="检查FFmpeg", command=self.check_ffmpeg)
        check_btn.pack(side=tk.RIGHT, padx=5)
        
        # 添加分隔线
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 拖放区域
        drop_frame = ttk.Frame(main_frame)
        drop_frame.pack(fill=tk.X, pady=10)
        
        self.drop_label = tk.Label(
            drop_frame, 
            text="拖放视频文件到这里\n(支持任意数量，将按文件名数字顺序或字母顺序合并)",
            relief="groove", 
            height=8, 
            bg='white',
            fg='#555555',
            font=('Arial', 10),
            justify=tk.CENTER
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)
        
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
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root, 
            variable=self.progress_var, 
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.status_var.set(message)
        self.root.update()

    def check_ffmpeg(self):
        self.log_message("正在检查FFmpeg...")
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 检查输出中是否包含ffmpeg版本信息
            if "ffmpeg version" in result.stdout or "ffmpeg version" in result.stderr:
                version_line = result.stderr.split('\n')[0] if result.stderr else result.stdout.split('\n')[0]
                self.log_message(f"FFmpeg可用: {version_line}")
                messagebox.showinfo("FFmpeg检查", "FFmpeg可用！\n" + version_line)
            else:
                self.log_message("错误：未找到有效的FFmpeg")
                messagebox.showerror("FFmpeg错误", "未找到有效的FFmpeg可执行文件")
        except Exception as e:
            self.log_message(f"检查FFmpeg时出错: {str(e)}")
            messagebox.showerror("FFmpeg错误", f"无法执行FFmpeg:\n{str(e)}")

    def handle_drop(self, event):
        if self.processing:
            self.log_message("警告：当前正在处理中，请等待完成")
            return
            
        files = self.root.tk.splitlist(event.data)
        valid_files = []

        for f in files:
            if os.path.splitext(f)[1].lower() in self.supported_formats:
                valid_files.append(f)
            else:
                self.log_message(f"忽略不支持的文件: {os.path.basename(f)}")

        if len(valid_files) < 1:
            self.log_message("错误：至少需要1个视频文件")
            return
            
        if len(valid_files) < 2:
            self.log_message("错误：需要至少2个视频文件进行合并")
            return
            
        self.log_message(f"开始处理 {len(valid_files)} 个视频文件...")
        
        # 启动合并线程
        self.processing = True
        self.process_thread = threading.Thread(
            target=self.merge_videos, 
            args=(valid_files,),
            daemon=True
        )
        self.process_thread.start()

    def merge_videos(self, file_paths):
        try:
            # 1. 对文件进行排序
            sorted_files = self.sort_files(file_paths)
            self.log_message(f"排序后的文件: {', '.join([os.path.basename(f) for f in sorted_files])}")
            
            # 2. 创建临时文件列表
            list_file_path = self.create_file_list(sorted_files)
            
            # 3. 确定输出路径
            output_dir = os.path.dirname(file_paths[0])
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_path = os.path.join(output_dir, f"merged_video_{timestamp}.mp4")
            
            # 4. 构建FFmpeg命令
            command = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", list_file_path,
                "-c", "copy",  # 直接复制流，不重新编码
                "-y",  # 覆盖输出文件
                output_path
            ]
            
            self.log_message("开始合并视频...")
            self.log_message(f"命令: {' '.join(command)}")
            
            # 5. 执行FFmpeg命令
            self.progress_var.set(0)
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 6. 实时读取输出并更新进度
            for line in process.stdout:
                if "time=" in line:
                    # 解析时间信息来更新进度
                    time_match = re.search(r"time=(\d+:\d+:\d+\.\d+)", line)
                    if time_match:
                        time_str = time_match.group(1)
                        # 简单进度更新（实际应用中需要更复杂的计算）
                        current = self.progress_var.get()
                        if current < 95:  # 防止超过100%
                            self.progress_var.set(current + 0.5)
                
                # 将输出记录到日志
                self.log_message(line.strip())
            
            # 等待进程完成
            process.wait()
            
            # 检查返回码
            if process.returncode == 0:
                self.progress_var.set(100)
                self.log_message(f"视频合并成功！保存路径: {output_path}")
                # 询问用户是否打开所在文件夹
                self.root.after(0, lambda: self.ask_open_folder(output_path))
            else:
                self.log_message(f"视频合并失败，返回码: {process.returncode}")
                messagebox.showerror("错误", f"视频合并失败，返回码: {process.returncode}")
        
        except Exception as e:
            self.log_message(f"处理过程中出错: {str(e)}")
            messagebox.showerror("错误", f"处理过程中发生错误:\n{str(e)}")
        finally:
            # 清理临时文件
            if 'list_file_path' in locals() and os.path.exists(list_file_path):
                try:
                    os.remove(list_file_path)
                    self.log_message(f"已清理临时文件: {list_file_path}")
                except:
                    pass
                    
            self.processing = False
            self.progress_var.set(0)

    def sort_files(self, file_paths):
        """智能排序文件：优先按文件名中的数字排序，否则按字母顺序"""
        def extract_number(filename):
            # 尝试从文件名中提取数字
            base = os.path.basename(filename)
            match = re.search(r'\d+', base)
            return int(match.group()) if match else float('inf')
        
        # 检查所有文件名是否都包含数字
        all_have_numbers = all(re.search(r'\d+', os.path.basename(f)) for f in file_paths)
        
        if all_have_numbers:
            # 如果所有文件都有数字，按数字排序
            return sorted(file_paths, key=extract_number)
        else:
            # 否则按文件名排序
            return sorted(file_paths, key=lambda x: os.path.basename(x))

    def create_file_list(self, file_paths):
        """创建FFmpeg使用的文件列表"""
        list_file_path = os.path.join(os.path.dirname(file_paths[0]), "ffmpeg_concat_list.txt")
        
        with open(list_file_path, 'w', encoding='utf-8') as f:
            for path in file_paths:
                # 转义文件名中的特殊字符
                safe_path = path.replace("'", "'\\''")
                # Windows路径需要转换为正斜杠
                safe_path = safe_path.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")
                
        self.log_message(f"已创建临时文件列表: {list_file_path}")
        return list_file_path

    def ask_open_folder(self, file_path):
        if messagebox.askyesno("操作成功", "视频合并完成！是否打开所在文件夹？"):
            folder_path = os.path.dirname(file_path)
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])

if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = VideoMergerApp(root)
    root.mainloop()
