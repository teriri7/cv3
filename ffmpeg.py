import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import threading
import sys

class VideoScreenshotTool:
    def __init__(self, root):
        self.root = root
        self.root.title("视频分片截图工具")
        self.root.geometry("550x450")  # 增加高度以容纳新选项
        self.root.resizable(False, False)
        
        # 设置现代主题颜色
        self.bg_color = "#f5f5f5"
        self.primary_color = "#2196F3"
        self.secondary_color = "#FF9800"
        self.success_color = "#4CAF50"
        self.error_color = "#f44336"
        
        # 设置中文字体
        self.font = ('Microsoft YaHei', 10)
        self.title_font = ('Microsoft YaHei', 16, 'bold')
        
        # 配置根窗口背景
        self.root.configure(bg=self.bg_color)
        
        # 设置ffmpeg路径
        self.ffmpeg_path = self.get_ffmpeg_path()
        
        # 视频文件扩展名列表
        self.VIDEO_EXTS = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp']
        
        # 创建界面元素
        self.create_widgets()
        
        # 检查ffmpeg可用性
        self.check_ffmpeg()
    
    def get_ffmpeg_path(self):
        """获取ffmpeg路径，优先使用本地路径"""
        local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg
        else:
            # 如果本地路径不存在，尝试使用系统环境变量中的ffmpeg
            return "ffmpeg"
    
    def check_ffmpeg(self):
        """检查ffmpeg是否可用"""
        try:
            # 使用UTF-8编码运行命令，避免编码错误
            result = subprocess.run([self.ffmpeg_path, "-version"], 
                                  capture_output=True, text=True, timeout=5, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                version_match = re.search(r"ffmpeg version (\S+)", result.stdout)
                version = version_match.group(1) if version_match else "未知版本"
                self.ffmpeg_status_var.set(f"✓ FFmpeg可用 ({version})")
                self.ffmpeg_status_label.config(fg=self.success_color)
                return True
            else:
                self.ffmpeg_status_var.set("✗ FFmpeg检查失败")
                self.ffmpeg_status_label.config(fg=self.error_color)
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self.ffmpeg_status_var.set(f"✗ FFmpeg不可用: {str(e)}")
            self.ffmpeg_status_label.config(fg=self.error_color)
            return False
    
    def create_widgets(self):
        # 主框架 - 使用现代卡片式设计
        main_frame = tk.Frame(self.root, padx=25, pady=20, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        intro_label = tk.Label(title_frame, text="视频分片截图工具", 
                              font=self.title_font, bg=self.bg_color, fg="#333333")
        intro_label.pack()
        
        # 功能说明卡片
        desc_card = tk.Frame(main_frame, bg="white", relief="flat", bd=1, 
                           highlightbackground="#e0e0e0", highlightthickness=1)
        desc_card.pack(fill=tk.X, pady=(0, 15))
        
        desc_label = tk.Label(desc_card, text="该程序会对当前文件夹内的所有视频文件进行分片截图，每个视频文件会生成一个对应的文件夹存放截图。", 
                             font=self.font, bg="white", wraplength=500, justify=tk.LEFT)
        desc_label.pack(padx=15, pady=12)
        
        # 设置区域卡片
        settings_card = tk.Frame(main_frame, bg="white", relief="flat", bd=1,
                               highlightbackground="#e0e0e0", highlightthickness=1)
        settings_card.pack(fill=tk.X, pady=(0, 15))
        
        # 截图间隔设置
        interval_frame = tk.Frame(settings_card, bg="white")
        interval_frame.pack(fill=tk.X, padx=15, pady=12)
        
        interval_label = tk.Label(interval_frame, text="截图间隔(秒):", 
                                 font=self.font, bg="white", width=12, anchor=tk.W)
        interval_label.pack(side=tk.LEFT)
        
        self.interval_var = tk.StringVar(value="0.5")
        interval_entry = tk.Entry(interval_frame, textvariable=self.interval_var, 
                                 font=self.font, width=8, relief="solid", bd=1)
        interval_entry.pack(side=tk.LEFT)
        
        # 输出格式设置
        format_frame = tk.Frame(settings_card, bg="white")
        format_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
        
        format_label = tk.Label(format_frame, text="输出格式:", 
                               font=self.font, bg="white", width=12, anchor=tk.W)
        format_label.pack(side=tk.LEFT)
        
        self.format_var = tk.StringVar(value="jpg")
        format_jpg = tk.Radiobutton(format_frame, text="JPG", variable=self.format_var, 
                                   value="jpg", font=self.font, bg="white", anchor=tk.W)
        format_jpg.pack(side=tk.LEFT, padx=(0, 10))
        
        format_png = tk.Radiobutton(format_frame, text="PNG", variable=self.format_var, 
                                   value="png", font=self.font, bg="white", anchor=tk.W)
        format_png.pack(side=tk.LEFT)
        
        # HDR处理选项
        hdr_frame = tk.Frame(settings_card, bg="white")
        hdr_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
        
        hdr_label = tk.Label(hdr_frame, text="HDR处理:", 
                            font=self.font, bg="white", width=12, anchor=tk.W)
        hdr_label.pack(side=tk.LEFT)
        
        self.hdr_mode = tk.StringVar(value="auto")
        hdr_auto = tk.Radiobutton(hdr_frame, text="自动检测", variable=self.hdr_mode, 
                                 value="auto", font=self.font, bg="white", anchor=tk.W)
        hdr_auto.pack(side=tk.LEFT, padx=(0, 10))
        
        hdr_force = tk.Radiobutton(hdr_frame, text="强制HDR转SDR", variable=self.hdr_mode, 
                                  value="force", font=self.font, bg="white", anchor=tk.W)
        hdr_force.pack(side=tk.LEFT, padx=(0, 10))
        
        hdr_none = tk.Radiobutton(hdr_frame, text="禁用", variable=self.hdr_mode, 
                                 value="none", font=self.font, bg="white", anchor=tk.W)
        hdr_none.pack(side=tk.LEFT)
        
        # FFmpeg状态显示
        ffmpeg_frame = tk.Frame(settings_card, bg="white")
        ffmpeg_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
        
        ffmpeg_label = tk.Label(ffmpeg_frame, text="FFmpeg状态:", 
                               font=self.font, bg="white", width=12, anchor=tk.W)
        ffmpeg_label.pack(side=tk.LEFT)
        
        self.ffmpeg_status_var = tk.StringVar(value="检查中...")
        self.ffmpeg_status_label = tk.Label(ffmpeg_frame, textvariable=self.ffmpeg_status_var, 
                                           font=self.font, bg="white", anchor=tk.W)
        self.ffmpeg_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=15)
        
        self.run_button = tk.Button(button_frame, text="开始截图", font=self.font, 
                                   command=self.run_screenshot, bg=self.primary_color, 
                                   fg="white", width=15, height=1, cursor="hand2",
                                   activebackground="#1976D2", activeforeground="white",
                                   relief="flat", bd=0)
        self.run_button.pack()
        
        # 状态栏
        status_frame = tk.Frame(main_frame, bg="#e0e0e0", height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = tk.Label(status_frame, textvariable=self.status_var, 
                               font=('Microsoft YaHei', 9), bg="#e0e0e0", fg="#666666")
        status_label.pack(side=tk.LEFT, padx=10)
    
    def run_screenshot(self):
        # 先检查ffmpeg是否可用
        if not self.check_ffmpeg():
            messagebox.showerror("FFmpeg错误", 
                               "FFmpeg不可用，请确保ffmpeg/bin/ffmpeg.exe存在于程序目录中，或者系统PATH中有ffmpeg。")
            return
        
        # 获取截图间隔
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError("间隔必须为正数")
        except ValueError as e:
            messagebox.showerror("输入错误", "请输入一个有效的正浮点数作为截图间隔！")
            return
        
        # 禁用按钮防止重复点击
        self.run_button.config(state=tk.DISABLED, bg="#BDBDBD")
        self.status_var.set("正在处理...")
        
        # 获取HDR处理模式和输出格式
        hdr_mode = self.hdr_mode.get()
        output_format = self.format_var.get()
        
        # 在新线程中执行截图操作
        threading.Thread(target=self.process_videos, args=(interval, hdr_mode, output_format), daemon=True).start()
    
    def process_videos(self, interval, hdr_mode, output_format):
        try:
            # 获取当前文件夹路径
            current_dir = os.getcwd()
            
            # 获取所有视频文件
            video_files = []
            for file in os.listdir(current_dir):
                file_path = os.path.join(current_dir, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in self.VIDEO_EXTS):
                    video_files.append(file)
            
            if not video_files:
                self.root.after(0, lambda: self.status_var.set("就绪"))
                self.root.after(0, lambda: messagebox.showinfo("完成", "当前文件夹内未找到视频文件！"))
                self.root.after(0, self.enable_buttons)
                return
            
            total_videos = len(video_files)
            processed = 0
            
            # 处理每个视频文件
            for video_file in video_files:
                try:
                    success = self.process_single_video(video_file, interval, hdr_mode, output_format)
                    if success:
                        processed += 1
                    self.root.after(0, lambda: self.status_var.set(f"已处理: {processed}/{total_videos}"))
                except Exception as e:
                    print(f"处理视频 {video_file} 时出错: {str(e)}")
                    # 在GUI线程中显示错误
                    error_msg = f"处理视频 {video_file} 时出错: {str(e)}"
                    self.root.after(0, lambda msg=error_msg: messagebox.showerror("处理错误", msg))
            
            self.root.after(0, lambda: self.status_var.set("就绪"))
            self.root.after(0, lambda: messagebox.showinfo("完成", f"视频处理完成！共处理 {processed}/{total_videos} 个视频文件。"))
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("错误", msg))
            self.root.after(0, lambda: self.status_var.set("就绪"))
        finally:
            self.root.after(0, self.enable_buttons)
    
    def detect_hdr_video(self, video_file):
        """检测视频是否为HDR格式"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", os.path.abspath(video_file),
                "-hide_banner"
            ]
            # 使用UTF-8编码运行命令，避免编码错误
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # 检查输出中是否包含HDR相关特征
            stderr = result.stderr.lower()
            hdr_indicators = [
                "bt.2020", "rec.2020",  # HDR色彩空间
                "pq", "smpte st 2084",   # PQ传输函数
                "hlg", "arib-std-b67",   # HLG传输函数
                "hdr10", "hdr10+",       # HDR格式
                "dolby vision"           # 杜比视界
            ]
            
            return any(indicator in stderr for indicator in hdr_indicators)
        except:
            return False
    
    def process_single_video(self, video_file, interval, hdr_mode, output_format):
        # 创建视频对应的文件夹
        video_name = os.path.splitext(video_file)[0]
        # 清理文件夹名称，移除非法字符
        video_name = re.sub(r'[<>:"/\\|?*]', '_', video_name)
        output_dir = os.path.join(os.getcwd(), video_name)
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建基础ffmpeg命令
        cmd = [self.ffmpeg_path, "-i", os.path.abspath(video_file)]
        
        # 处理HDR视频
        is_hdr = False
        if hdr_mode != "none":
            is_hdr = self.detect_hdr_video(video_file)
            if is_hdr:
                print(f"检测到HDR视频: {video_file}")
        
        # 根据HDR模式和处理结果构建滤镜
        if (hdr_mode == "force" or (hdr_mode == "auto" and is_hdr)):
            # HDR转SDR的滤镜链
            vf_filter = (
                f"fps=1/{interval},"
                "zscale=t=linear:npl=100,format=gbrpf32le,"
                "zscale=p=bt709,tonemap=hable:param=1.0,"
                "zscale=t=bt709:m=bt709:r=pc,format=yuv420p"
            )
            cmd.extend(["-vf", vf_filter])
            print(f"应用HDR转SDR处理: {video_file}")
        else:
            # 普通截图
            cmd.extend(["-vf", f"fps=1/{interval}"])
        
        # 根据输出格式设置参数
        if output_format == "jpg":
            cmd.extend(["-q:v", "2"])  # JPG质量参数 (2-31, 2为最高质量)
        else:  # PNG格式
            cmd.extend(["-compression_level", "6"])  # PNG压缩级别 (0-9, 0为无压缩)
        
        # 添加输出文件名
        output_pattern = os.path.join(output_dir, f"{video_name}_%04d.{output_format}")
        cmd.append(output_pattern)
        
        # 执行命令 - 使用UTF-8编码避免解码错误
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
            # 检查是否有已知的错误信息
            error_msg = result.stderr
            if "Invalid data found" in error_msg:
                error_msg = "视频文件格式可能损坏或不支持"
            elif "Permission denied" in error_msg:
                error_msg = "没有文件访问权限"
            elif "No such file or directory" in error_msg:
                error_msg = "视频文件不存在或路径错误"
                
            print(f"FFmpeg 错误: {error_msg}")
            raise Exception(f"处理视频时出错: {error_msg}")
        
        return True
    
    def enable_buttons(self):
        # 重新启用按钮
        self.run_button.config(state=tk.NORMAL, bg=self.primary_color)
        self.status_var.set("就绪")

if __name__ == "__main__":
    # 设置DPI感知，改善高DPI显示器的显示效果
    if os.name == 'nt':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    
    root = tk.Tk()
    app = VideoScreenshotTool(root)
    root.mainloop()
