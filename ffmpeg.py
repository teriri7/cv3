import os
import re
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import threading
import sys
from datetime import datetime

class VideoScreenshotTool:
    def __init__(self, root):
        self.root = root
        self.root.title("视频分片截图工具")
        self.root.geometry("550x500")
        self.root.resizable(False, False)
        
        self.bg_color = "#f5f5f5"
        self.primary_color = "#2196F3"
        self.secondary_color = "#FF9800"
        self.success_color = "#4CAF50"
        self.error_color = "#f44336"
        
        self.font = ('Microsoft YaHei', 10)
        self.title_font = ('Microsoft YaHei', 16, 'bold')
        
        self.root.configure(bg=self.bg_color)
        
        self.ffmpeg_path = self.get_ffmpeg_path()
        
        self.VIDEO_EXTS = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp']
        
        self.create_widgets()
        
        self.check_ffmpeg()
    
    def get_ffmpeg_path(self):
        local_ffmpeg = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg
        else:
            return "ffmpeg"
    
    def check_ffmpeg(self):
        try:
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
        main_frame = tk.Frame(self.root, padx=25, pady=20, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        intro_label = tk.Label(title_frame, text="视频分片截图工具", 
                              font=self.title_font, bg=self.bg_color, fg="#333333")
        intro_label.pack()
        
        desc_card = tk.Frame(main_frame, bg="white", relief="flat", bd=1, 
                           highlightbackground="#e0e0e0", highlightthickness=1)
        desc_card.pack(fill=tk.X, pady=(0, 15))
        
        desc_label = tk.Label(desc_card, text="该程序会对当前文件夹内的所有视频文件进行分片截图，每个视频文件会生成一个对应的文件夹存放截图。", 
                             font=self.font, bg="white", wraplength=500, justify=tk.LEFT)
        desc_label.pack(padx=15, pady=12)
        
        settings_card = tk.Frame(main_frame, bg="white", relief="flat", bd=1,
                               highlightbackground="#e0e0e0", highlightthickness=1)
        settings_card.pack(fill=tk.X, pady=(0, 15))
        
        interval_frame = tk.Frame(settings_card, bg="white")
        interval_frame.pack(fill=tk.X, padx=15, pady=12)
        
        interval_label = tk.Label(interval_frame, text="截图间隔(秒):", 
                                 font=self.font, bg="white", width=12, anchor=tk.W)
        interval_label.pack(side=tk.LEFT)
        
        self.interval_var = tk.StringVar(value="0.5")
        interval_entry = tk.Entry(interval_frame, textvariable=self.interval_var, 
                                 font=self.font, width=8, relief="solid", bd=1)
        interval_entry.pack(side=tk.LEFT)
        
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
        
        dolby_frame = tk.Frame(settings_card, bg="white")
        dolby_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
        
        dolby_label = tk.Label(dolby_frame, text="杜比音频处理:", 
                              font=self.font, bg="white", width=12, anchor=tk.W)
        dolby_label.pack(side=tk.LEFT)
        
        self.dolby_mode = tk.StringVar(value="auto")
        dolby_auto = tk.Radiobutton(dolby_frame, text="自动移除", variable=self.dolby_mode, 
                                   value="auto", font=self.font, bg="white", anchor=tk.W)
        dolby_auto.pack(side=tk.LEFT, padx=(0, 10))
        
        dolby_keep = tk.Radiobutton(dolby_frame, text="保留音频", variable=self.dolby_mode, 
                                   value="keep", font=self.font, bg="white", anchor=tk.W)
        dolby_keep.pack(side=tk.LEFT, padx=(0, 10))
        
        dolby_remove = tk.Radiobutton(dolby_frame, text="强制移除", variable=self.dolby_mode, 
                                     value="remove", font=self.font, bg="white", anchor=tk.W)
        dolby_remove.pack(side=tk.LEFT)
        
        ffmpeg_frame = tk.Frame(settings_card, bg="white")
        ffmpeg_frame.pack(fill=tk.X, padx=15, pady=(0, 12))
        
        ffmpeg_label = tk.Label(ffmpeg_frame, text="FFmpeg状态:", 
                               font=self.font, bg="white", width=12, anchor=tk.W)
        ffmpeg_label.pack(side=tk.LEFT)
        
        self.ffmpeg_status_var = tk.StringVar(value="检查中...")
        self.ffmpeg_status_label = tk.Label(ffmpeg_frame, textvariable=self.ffmpeg_status_var, 
                                           font=self.font, bg="white", anchor=tk.W)
        self.ffmpeg_status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=15)
        
        self.run_button = tk.Button(button_frame, text="开始截图", font=self.font, 
                                   command=self.run_screenshot, bg=self.primary_color, 
                                   fg="white", width=15, height=1, cursor="hand2",
                                   activebackground="#1976D2", activeforeground="white",
                                   relief="flat", bd=0)
        self.run_button.pack()
        
        status_frame = tk.Frame(main_frame, bg="#e0e0e0", height=25)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="就绪")
        status_label = tk.Label(status_frame, textvariable=self.status_var, 
                               font=('Microsoft YaHei', 9), bg="#e0e0e0", fg="#666666")
        status_label.pack(side=tk.LEFT, padx=10)
    
    def run_screenshot(self):
        if not self.check_ffmpeg():
            messagebox.showerror("FFmpeg错误", 
                               "FFmpeg不可用，请确保ffmpeg/bin/ffmpeg.exe存在于程序目录中，或者系统PATH中有ffmpeg。")
            return
        
        try:
            interval = float(self.interval_var.get())
            if interval <= 0:
                raise ValueError("间隔必须为正数")
        except ValueError as e:
            messagebox.showerror("输入错误", "请输入一个有效的正浮点数作为截图间隔！")
            return
        
        self.run_button.config(state=tk.DISABLED, bg="#BDBDBD")
        self.status_var.set("正在处理...")
        
        hdr_mode = self.hdr_mode.get()
        output_format = self.format_var.get()
        dolby_mode = self.dolby_mode.get()
        
        current_date = datetime.now().strftime("%m%d")
        
        threading.Thread(target=self.process_videos, args=(interval, hdr_mode, output_format, dolby_mode, current_date), daemon=True).start()
    
    def process_videos(self, interval, hdr_mode, output_format, dolby_mode, current_date):
        try:
            current_dir = os.getcwd()
            
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
            
            for video_file in video_files:
                try:
                    success = self.process_single_video(video_file, interval, hdr_mode, output_format, dolby_mode, current_date)
                    if success:
                        processed += 1
                    self.root.after(0, lambda: self.status_var.set(f"已处理: {processed}/{total_videos}"))
                except Exception as e:
                    print(f"处理视频 {video_file} 时出错: {str(e)}")
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
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", os.path.abspath(video_file),
                "-hide_banner"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            stderr = result.stderr.lower()
            hdr_indicators = [
                "bt.2020", "rec.2020",
                "pq", "smpte st 2084",
                "hlg", "arib-std-b67",
                "hdr10", "hdr10+",
                "dolby vision"
            ]
            
            return any(indicator in stderr for indicator in hdr_indicators)
        except:
            return False
    
    def detect_dolby_audio(self, video_file):
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", os.path.abspath(video_file),
                "-hide_banner"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            stderr = result.stderr.lower()
            dolby_indicators = [
                "truehd", "dolby atmos", "dolby truehd", "e-ac-3", "atmos"
            ]
            
            return any(indicator in stderr for indicator in dolby_indicators)
        except:
            return False
    
    def process_single_video(self, video_file, interval, hdr_mode, output_format, dolby_mode, current_date):
        video_name = os.path.splitext(video_file)[0]
        video_name = re.sub(r'[<>:"/\\|?*]', '_', video_name)
        output_dir = os.path.join(os.getcwd(), video_name)
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [self.ffmpeg_path, "-i", os.path.abspath(video_file)]
        
        has_dolby_audio = self.detect_dolby_audio(video_file)
        remove_audio = False
        
        if dolby_mode == "auto" and has_dolby_audio:
            remove_audio = True
            print(f"检测到杜比音频，自动移除音频: {video_file}")
        elif dolby_mode == "remove":
            remove_audio = True
            print(f"强制移除音频: {video_file}")
        
        if remove_audio:
            cmd.extend(["-map", "0:v:0"])
        
        is_hdr = False
        if hdr_mode != "none":
            is_hdr = self.detect_hdr_video(video_file)
            if is_hdr:
                print(f"检测到HDR视频: {video_file}")
        
        if (hdr_mode == "force" or (hdr_mode == "auto" and is_hdr)):
            vf_filter = (
                f"fps=1/{interval},"
                "zscale=t=linear:npl=100,format=gbrpf32le,"
                "zscale=p=bt709,tonemap=hable:param=1.0,"
                "zscale=t=bt709:m=bt709:r=pc,format=yuv420p"
            )
            cmd.extend(["-vf", vf_filter])
            print(f"应用HDR转SDR处理: {video_file}")
        else:
            cmd.extend(["-vf", f"fps=1/{interval}"])
        
        if output_format == "jpg":
            cmd.extend(["-q:v", "2"])
        else:
            cmd.extend(["-compression_level", "6"])
        
        output_pattern = os.path.join(output_dir, f"{video_name}_%04d_{current_date}.{output_format}")
        cmd.append(output_pattern)
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
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
        self.run_button.config(state=tk.NORMAL, bg=self.primary_color)
        self.status_var.set("就绪")

if __name__ == "__main__":
    if os.name == 'nt':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    
    root = tk.Tk()
    app = VideoScreenshotTool(root)
    root.mainloop()
