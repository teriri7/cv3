import os
import subprocess

# 配置截图间隔时间（单位：秒）
interval = 0.5

# 当前文件夹路径
current_dir = os.getcwd()

# 视频文件的扩展名
video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv']

# 遍历当前文件夹中的所有文件
for file in os.listdir(current_dir):
    # 检查是否是视频文件
    if any(file.lower().endswith(ext) for ext in video_extensions):
        video_path = os.path.join(current_dir, file)
        video_name, _ = os.path.splitext(file)

        # 创建以视频名命名的文件夹
        output_folder = os.path.join(current_dir, video_name)
        os.makedirs(output_folder, exist_ok=True)

        # 构造 FFmpeg 命令
        output_pattern = os.path.join(output_folder, "frame_%04d.jpg")
        ffmpeg_command = [
            "ffmpeg", "-i", video_path,
            "-vf", f"fps={1/interval}",
            output_pattern
        ]

        # 执行命令
        print(f"正在处理视频：{file}")
        subprocess.run(ffmpeg_command)

print("所有视频处理完成！")
