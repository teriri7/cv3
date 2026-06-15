import requests
from PIL import Image
from io import BytesIO
import pyautogui
import time
import win32clipboard
from win32con import CF_DIB
import pyperclip
import re
from urllib.parse import urljoin

# 将图片以 DIB 格式放入剪贴板
def set_clipboard_image(image):
    with BytesIO() as output:
        image.convert("RGB").save(output, format="BMP")
        bmp_data = output.getvalue()[14:]  # 跳过BMP文件头的14字节
        
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(CF_DIB, bmp_data)
        finally:
            win32clipboard.CloseClipboard()

# 从网页中提取所有 .webp 格式的图片，返回 PIL Image 列表
def fetch_images_from_page(url, retries=3):
    last_error = None
    for attempt in range(retries):
        try:
            # 获取网页内容
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                raise Exception(f"无法获取网页，状态码: {resp.status_code}")
            html = resp.text

            # 提取所有 img 标签的 src 属性
            all_img_urls = re.findall(r'<img[^>]+src="([^"]+)"', html)
            # 只保留以 .webp 结尾的图片链接（忽略大小写）
            webp_urls = [u for u in all_img_urls if u.lower().endswith('.webp')]
            
            if not webp_urls:
                # 网页正常但没有 .webp 图片，返回空列表
                return []

            images = []
            for img_src in webp_urls:
                # 补全相对路径
                full_url = urljoin(url, img_src)
                # 下载图片
                img_resp = requests.get(full_url, timeout=10)
                if img_resp.status_code != 200:
                    raise Exception(f"下载图片失败: {full_url}, 状态码: {img_resp.status_code}")
                img_data = BytesIO(img_resp.content)
                img = Image.open(img_data)
                images.append(img)
            return images
        except Exception as e:
            last_error = e
            print(f"处理网页失败: {e}，正在重试 ({attempt + 1}/{retries})...")
            time.sleep(2)
    
    raise last_error  # 所有重试都失败则抛出异常

# 从 Excel 单元格获取 URL
def get_url_from_excel():
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    return pyperclip.paste().strip()

# 在当前单元格粘贴剪贴板内容
def paste_at_cursor():
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(5)  # 等待粘贴完成

# 写入 "网络错误" 并移动到下一行的链接列
def write_network_error():
    pyautogui.press('right')          # 移到右边单元格
    pyperclip.copy("网络错误")
    pyautogui.hotkey('ctrl', 'v')     # 粘贴文字
    pyautogui.press('down')           # 移到下一行
    pyautogui.press('left')           # 回到左边的 URL 列

# 移动到下一行的链接列（当前光标应在链接列时调用）
def move_to_next_row_link():
    pyautogui.press('down')   # 直接向下移动一行，列位置不变（仍为链接列）

def main():
    while True:
        try:
            target_count = int(input("请输入要处理的链接个数："))
            if target_count <= 0:
                raise ValueError("次数必须为正整数")
            break
        except ValueError as e:
            print(f"输入无效：{e}，请重新输入")

    print("\n10秒后将开始，请将鼠标放在Excel的第一个链接单元格上...")
    time.sleep(10)

    processed = 0

    while processed < target_count:
        url = get_url_from_excel()
        if not url:
            print("未获取到URL，跳过当前行...")
            move_to_next_row_link()   # 直接向下移动一行，保持在链接列
            continue

        print(f"读取到URL: {url}")
        try:
            # 获取网页中的所有 .webp 图片
            images = fetch_images_from_page(url)
        except Exception as e:
            print(f"获取图片失败: {e}，写入'网络错误'并跳过该链接")
            write_network_error()
            processed += 1
            continue

        # 成功获取图片列表（可能为空，即没有 .webp 图片）
        if len(images) == 0:
            print("网页中无 .webp 图片，跳过该链接，移动到下一行")
            move_to_next_row_link()   # 直接从链接列向下移动一行
            processed += 1
            continue

        # 依次向右粘贴每一张图片
        for idx, img in enumerate(images):
            set_clipboard_image(img)
            if idx == 0:
                pyautogui.press('right')   # 第一张：移到链接右边的单元格
            else:
                pyautogui.press('right')   # 后续图片：继续向右移动
            paste_at_cursor()              # 粘贴并等待5秒

        # 全部粘贴完后，光标在最右侧的图片单元格
        # 向左移动图片数量格，回到链接列
        for _ in range(len(images)):
            pyautogui.press('left')
        # 再向下移动一行，到下一行的链接列
        pyautogui.press('down')

        processed += 1
        print(f"已处理 {processed}/{target_count} 个链接")

    print("已达到预定的处理数量，程序结束。")

if __name__ == '__main__':
    main()
