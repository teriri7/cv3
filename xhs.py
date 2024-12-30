import os
import tkinter as tk
from tkinter import simpledialog
import requests
from bs4 import BeautifulSoup

def main():
    # 弹出窗口让用户输入 cookie
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    cookie = simpledialog.askstring("输入 Cookie", "请输入您的 Cookie:")
    if not cookie:
        print("Cookie 不能为空！")
        return

    # 读取 xhs.txt 文件中的链接
    if not os.path.exists("xhs.txt"):
        print("当前目录下未找到 xhs.txt 文件！")
        return

    with open("xhs.txt", "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file if line.strip()]

    if not urls:
        print("xhs.txt 文件中没有有效链接！")
        return

    # 创建保存视频的文件夹
    save_folder = "xhs"
    os.makedirs(save_folder, exist_ok=True)

    # 请求头
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://bytedance.larkoffice.com/",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "cookie": cookie,
    }

    # 处理每个链接
    for url in urls:
        try:
            print(f"正在处理: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # 解析 HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # 提取视频链接
            video_tag = soup.find("meta", attrs={"name": "og:video"})
            video_url = video_tag["content"] if video_tag else None

            # 提取视频标题
            title_tag = soup.find("meta", attrs={"name": "og:title"})
            title = title_tag["content"] if title_tag else "未命名视频"

            if video_url and title:
                # 生成合法的文件名
                safe_title = "".join(c for c in title if c.isalnum() or c in " .-_()").strip()
                file_name = f"{safe_title}.mp4"
                file_path = os.path.join(save_folder, file_name)

                # 下载视频
                print(f"正在下载: {title}")
                video_response = requests.get(video_url, stream=True, timeout=30)
                video_response.raise_for_status()

                with open(file_path, "wb") as video_file:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        video_file.write(chunk)

                print(f"视频已保存: {file_path}")
            else:
                print(f"未找到视频或标题: {url}")

        except Exception as e:
            print(f"处理链接时出错: {url}, 错误: {e}")

if __name__ == "__main__":
    main()
