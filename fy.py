import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
import requests
import os

# 生成翻译请求的签名
def generate_sign(query, appid, salt, secret_key):
    sign_str = appid + query + str(salt) + secret_key
    md5 = hashlib.md5()
    md5.update(sign_str.encode('utf-8'))
    return md5.hexdigest()

def translate(query, from_lang, to_lang):
    appid = '20241024002184374'
    secret_key = '2KmdnLteDW7wHsFT_U54'
    salt = 114514
    sign = generate_sign(query, appid, salt, secret_key)
    url = f"http://api.fanyi.baidu.com/api/trans/vip/translate?q={query}&from={from_lang}&to={to_lang}&appid={appid}&salt={salt}&sign={sign}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)  # 设置超时
        response.raise_for_status()  # 检查是否有请求错误
        result = response.json()
        
        # 检查是否包含 'trans_result' 键
        if 'trans_result' in result:
            return result['trans_result'][0]['dst']
        else:
            messagebox.showerror("Error", f"Translation API error: {result}")
            return None
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to translate: {e}")
        return None


# 批量翻译并写入新文件
def batch_translate(file_path, from_lang, to_lang):
    output_path = f"{os.path.splitext(file_path)[0]}-{to_lang}.txt"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        translated_lines = []
        for line in lines:
            line = line.strip()
            if line:  # 跳过空行
                translated_line = translate(line, from_lang, to_lang)
                translated_lines.append(translated_line + '\n')
            else:
                translated_lines.append('\n')  # 保留空行

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(translated_lines)

        messagebox.showinfo("Translation Complete", f"Translated file saved as: {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error in batch translation: {e}")

# GUI 界面设计
class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("中英互译翻译程序")
        self.root.geometry("500x200")
        self.root.config(bg="#f7f7f9")
        
        # 使用ttk风格
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=10)
        style.configure("TLabel", font=("Arial", 14), background="#f7f7f9")

        self.from_lang = "zh"
        self.to_lang = "en"

        # 显示翻译方向标签
        self.label_from = ttk.Label(root, text="zh", font=("Arial", 14))
        self.label_from.grid(row=0, column=0, padx=40, pady=20)
        
        self.label_to = ttk.Label(root, text="en", font=("Arial", 14))
        self.label_to.grid(row=0, column=2, padx=40, pady=20)

        # 中间的转换箭头按钮
        self.switch_button = ttk.Button(root, text="⇆", command=self.switch_languages)
        self.switch_button.grid(row=0, column=1, pady=10)

        # 翻译按钮
        self.translate_button = ttk.Button(root, text="选择txt文件进行翻译", command=self.select_file)
        self.translate_button.grid(row=1, column=1, pady=20)

    # 交换语言标签和翻译方向
    def switch_languages(self):
        if self.from_lang == "zh":
            self.from_lang = "en"
            self.to_lang = "zh"
            self.label_from.config(text="en")
            self.label_to.config(text="zh")
        else:
            self.from_lang = "zh"
            self.to_lang = "en"
            self.label_from.config(text="zh")
            self.label_to.config(text="en")

    # 选择文件进行翻译
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            batch_translate(file_path, self.from_lang, self.to_lang)

# 启动应用
if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
