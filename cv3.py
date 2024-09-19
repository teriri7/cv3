import requests
from PIL import Image
from io import BytesIO
import pyautogui
import time
import win32clipboard
from win32con import CF_DIB
import pyperclip

# 将图片以 DIB 格式放入剪贴板
def set_clipboard_image(image):
    # 将图片转换为DIB格式
    with BytesIO() as output:
        image.convert("RGB").save(output, format="BMP")
        bmp_data = output.getvalue()[14:]  # 跳过BMP文件头的14字节
        
        # 打开剪贴板
        win32clipboard.OpenClipboard()
        try:
            # 清空剪贴板
            win32clipboard.EmptyClipboard()
            # 将数据设置到剪贴板
            win32clipboard.SetClipboardData(CF_DIB, bmp_data)
        finally:
            # 关闭剪贴板
            win32clipboard.CloseClipboard()

# 下载图片并将其复制到剪贴板
def download_and_copy_image(url):
    try:
        # 下载图片
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"无法下载图片，状态码: {response.status_code}")

        # 加载图片
        img_data = BytesIO(response.content)
        img = Image.open(img_data)

        # 将图片设置到剪贴板
        set_clipboard_image(img)
        print("图片成功复制到剪贴板")
    except Exception as e:
        print(f"下载或复制图片时出错: {e}")

# 从 Excel 单元格获取 URL
def get_url_from_excel():
    pyautogui.hotkey('ctrl', 'c')  # 模拟Ctrl + C复制URL
    time.sleep(1)  # 等待剪贴板数据加载
    return pyperclip.paste().strip()  # 从剪贴板获取文本内容并去除空白

# 模拟粘贴图片到Excel并移动到下一行
def paste_image():
    pyautogui.press('right')  # 先向右移动到图片单元格
    pyautogui.hotkey('ctrl', 'v')  # 模拟Ctrl + V粘贴图片
    time.sleep(5)  # 等待图片上传
    pyautogui.press('down')  # 向下移动一行
    pyautogui.press('left')  # 向左移动回到URL单元格

def skip_to_next_row():
    pyautogui.press('down')  # 向下移动一行
   # pyautogui.press('left')  # 向左移动回到URL单元格

def main():
    print("10秒后将开始，请将鼠标放在Excel的目标单元格上...")
    time.sleep(10)  # 给予10秒准备时间

    # 循环操作
    while True:
        # 获取当前单元格的URL
        url = get_url_from_excel()
        if not url:
            print("未获取到URL，跳过当前行...")
            skip_to_next_row()  # URL为空，跳过当前行
            continue
        
        print(f"读取到URL: {url}")
        download_and_copy_image(url)  # 下载图片并复制到剪贴板
        paste_image()  # 粘贴图片并移动单元格

if __name__ == '__main__':
    main()
