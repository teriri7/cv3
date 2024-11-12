import tkinter as tk
from tkinter import messagebox
import os
import pickle
import textwrap
import chardet  # 自动检测编码

class BookReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("小说阅读器")
        self.root.geometry("400x660")
        self.root.resizable(False, False)
        self.current_page = 0
        self.lines_per_page = 20
        self.content = ""
        self.current_book = ""
        self.line_width = 20  # 每行字符数限制

        # 加载阅读进度
        self.load_progress()

        # 设置阅读背景颜色
        self.background_color = "#fffaf0"  # 统一的浅色背景
        self.root.config(bg=self.background_color)

        # 初始化小说列表
        self.book_listbox = tk.Listbox(
            root, font=("Arial", 12), bg=self.background_color, selectbackground="#d2b48c", bd=0, highlightthickness=0
        )
        self.book_listbox.place(relx=0.05, rely=0.1, relwidth=0.9, relheight=0.8)
        self.book_listbox.bind("<<ListboxSelect>>", self.load_book)

        # 加载小说列表
        self.load_books()

    def load_books(self):
        book_folder = os.path.join(os.getcwd(), "book")
        if not os.path.exists(book_folder):
            messagebox.showerror("错误", "未找到'book'文件夹")
            return

        books = [f for f in os.listdir(book_folder) if f.endswith(".txt")]
        if not books:
            messagebox.showinfo("信息", "book文件夹中没有txt文件")
            return

        for book in books:
            self.book_listbox.insert(tk.END, book)

    def load_book(self, event):
        selection = self.book_listbox.curselection()
        if not selection:
            return
        self.current_book = self.book_listbox.get(selection[0])
        book_path = os.path.join(os.getcwd(), "book", self.current_book)

        try:
            with open(book_path, "rb") as file:  # 以二进制模式打开文件
                raw_data = file.read()
                detected_encoding = chardet.detect(raw_data)['encoding']  # 检测编码

            # 使用检测到的编码读取内容
            with open(book_path, "r", encoding=detected_encoding) as file:
                self.content = file.readlines()
            
            self.current_page = self.load_page_progress(self.current_book)
            self.book_listbox.place_forget()  # 隐藏小说列表框
            self.show_text_area()  # 显示阅读区域
            self.show_page()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件：{e}")

    def show_text_area(self):
        # 创建文本显示区域，使用相同的背景色并去掉边框
        self.text_area = tk.Label(
            self.root,
            wraplength=350,
            font=("Arial", 14),
            bg=self.background_color,
            fg="#333",
            anchor="nw",
            justify="left"
        )
        self.text_area.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        # 绑定鼠标事件
        self.text_area.bind("<Button-1>", self.next_page)  # 左键下一页
        self.text_area.bind("<Button-3>", self.previous_page)  # 右键上一页

    def show_page(self):
        start = self.current_page * self.lines_per_page
        end = start + self.lines_per_page
        raw_page_content = "".join(self.content[start:end])

        # 使用 textwrap 模块对内容进行自动换行，确保每行完整显示
        wrapped_content = "\n".join(textwrap.fill(line, width=self.line_width) for line in raw_page_content.splitlines())

        # 显示当前页内容
        self.text_area.config(text=wrapped_content)
        self.root.update()

    def next_page(self, event=None):
        if (self.current_page + 1) * self.lines_per_page < len(self.content):
            self.current_page += 1
            self.show_page()
            self.save_progress()

    def previous_page(self, event=None):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_page()
            self.save_progress()

    def save_progress(self):
        # 保存当前书籍的页码进度
        with open("reading_progress.pkl", "wb") as f:
            progress_data = {self.current_book: self.current_page}
            pickle.dump(progress_data, f)

    def load_progress(self):
        # 尝试加载上次的阅读进度
        if os.path.exists("reading_progress.pkl"):
            with open("reading_progress.pkl", "rb") as f:
                self.progress_data = pickle.load(f)
        else:
            self.progress_data = {}

    def load_page_progress(self, book_name):
        # 返回上次的页码或0
        return self.progress_data.get(book_name, 0)

root = tk.Tk()
app = BookReaderApp(root)
root.mainloop()
