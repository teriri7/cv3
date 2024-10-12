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
    with BytesIO() as output:
        image.convert("RGB").save(output, format="BMP")
        bmp_data = output.getvalue()[14:]  # 跳过BMP文件头的14字节
        
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(CF_DIB, bmp_data)
        finally:
            win32clipboard.CloseClipboard()

# 下载图片并复制到剪贴板，增加重试机制
def download_and_copy_image(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)  # 设置超时
            if response.status_code != 200:
                raise Exception(f"无法下载图片，状态码: {response.status_code}")

            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            set_clipboard_image(img)
            print("图片成功复制到剪贴板")
            return True
        except Exception as e:
            print(f"下载或复制图片时出错: {e}，正在重试 ({attempt + 1}/{retries})...")
            time.sleep(2)  # 等待 2 秒后重试

    return False  # 所有重试都失败

# 从 Excel 单元格获取 URL
def get_url_from_excel():
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    return pyperclip.paste().strip()

# 粘贴图片到Excel并移动到下一行
def paste_image():
    pyautogui.press('right')
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(5)
    pyautogui.press('down')
    pyautogui.press('left')

# 写入 "网络错误" 到 Excel
def write_network_error():
    pyautogui.press('right')  # 移动到右边单元格
    pyperclip.copy("网络错误")  # 复制"网络错误"到剪贴板
    pyautogui.hotkey('ctrl', 'v')  # 粘贴到单元格
    pyautogui.press('down')  # 向下移动一行
    pyautogui.press('left')  # 返回到左边的URL单元格

def skip_to_next_row():
    pyautogui.press('down')

def main():
    while True:
        try:
            target_paste_count = int(input("请输入要粘贴的次数："))
            if target_paste_count <= 0:
                raise ValueError("次数必须为正整数")
            break
        except ValueError as e:
            print(f"输入无效：{e}，请重新输入")

    print("""
    10秒后将开始，请将鼠标放在Excel的目标单元格上...

    EEEEEEEEEEE  PPPPPPPPP   RRRRRRRRR    OOOOOOOO
    E            P       P   R       R   O        O
    E            P       P   R       R   O        O
    EEEEEEEEEEE  PPPPPPPPP   RRRRRRRRR    O        O
    E            P           R    R      O        O
    E            P           R     R     O        O
    EEEEEEEEEEE  P           R      R     OOOOOOOO
    """)

    time.sleep(10)

    current_paste_count = 0

    while current_paste_count < target_paste_count:
        url = get_url_from_excel()
        if not url:
            print("未获取到URL，跳过当前行...")
            skip_to_next_row()
            continue

        print(f"读取到URL: {url}")
        success = download_and_copy_image(url)

        if success:
            paste_image()
            current_paste_count += 1
            print(f"已粘贴 {current_paste_count}/{target_paste_count} 次")
        else:
            print(f"未能成功下载图片，写入'网络错误'并跳过当前行...")
            write_network_error()  # 写入 "网络错误" 并跳过当前行

    print("已达到预定的粘贴次数，程序结束。")

if __name__ == '__main__':
    main()
