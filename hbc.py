# -*- coding: utf-8 -*-
"""
Excel 网页图片自动提取与拼图工具 (Win11 现代磨砂风格版)
- 支持选择：向左侧 / 向右侧单元格粘贴
- 筛选规则：提取 Tool Result 产物预览图片
- 合并规则：保持原始前后顺序、智能网格排版、20MB JPG 智能压缩
"""

import io
import math
import os
import re
import tempfile
import threading
import time
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageOps
import pyautogui
import pyperclip
import requests
from bs4 import BeautifulSoup
import win32clipboard

# ═══════════════════════════════════════════════════════════════
#  WIN11 MICA / FROSTED GLASS PALETTE
# ═══════════════════════════════════════════════════════════════
THEME = {
    'bg':           '#F0F3F8',       # 磨砂灰蓝底色
    'card_bg':      '#FFFFFF',       # 悬浮白卡片
    'card_border':  '#E2E8F0',       # 卡片细描边
    'accent':       '#0067C0',       # Win11 标志蓝
    'accent_hover': '#00539C',       # 悬浮深蓝
    'accent_light': '#E8F2FA',       # 浅蓝激活底色
    'danger':       '#E11D48',       # 终止警示红
    'danger_hover': '#BE123C',
    'text_main':    '#0F172A',       # 主标题与文本
    'text_muted':   '#64748B',       # 次要说明文本
    'input_bg':     '#F8FAFC',       # 输入框背景
    'input_border': '#CBD5E1',       # 输入框边框
    'toggle_off':   '#F1F5F9',       # 未选胶囊背景
    'log_bg':       '#F8FAFC',       # 日志容器底色
}

F_TITLE = ('Segoe UI', 13, 'bold')
F_BODY  = ('Segoe UI', 10)
F_BODY_B= ('Segoe UI', 10, 'bold')
F_SMALL = ('Segoe UI', 8)
F_MONO  = ('Cascadia Code', 9)

GAP_RGB = (40, 40, 40)


# ═══════════════════════════════════════════════════════════════
#  CUSTOM ROUNDED WIDGETS
# ═══════════════════════════════════════════════════════════════
def draw_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    """绘制平滑圆角矩形"""
    points = [
        x1 + r, y1,     x2 - r, y1,
        x2,     y1,     x2,     y1 + r,
        x2,     y2 - r, x2,     y2,
        x2 - r, y2,     x1 + r, y2,
        x1,     y2,     x1,     y2 - r,
        x1,     y1 + r, x1,     y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class ModernPillToggle(tk.Label):
    """Win11 风格胶囊单选按钮"""
    def __init__(self, parent, text, variable, value, **kwargs):
        super().__init__(
            parent, text=text, font=F_BODY, padx=14, pady=5,
            cursor='hand2', bg=THEME['toggle_off'], fg=THEME['text_main'],
            **kwargs
        )
        self.var = variable
        self.val = value
        self.var.trace_add('write', lambda *_: self._sync())
        self.bind('<Button-1>', lambda e: self.var.set(self.val))
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', lambda e: self._sync())
        self._sync()

    def _sync(self):
        if self.var.get() == self.val:
            self.configure(bg=THEME['accent'], fg='#FFFFFF', font=F_BODY_B)
        else:
            self.configure(bg=THEME['toggle_off'], fg=THEME['text_main'], font=F_BODY)

    def _on_enter(self, _):
        if self.var.get() != self.val:
            self.configure(bg=THEME['accent_light'])


class ModernButton(tk.Canvas):
    """Win11 圆角拟物按钮"""
    def __init__(self, parent, text, command=None, style="primary", width=180, height=38):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0)
        self.command = command
        self.text = text
        self.style = style
        self.w, self.h = width, height
        self.is_hover = False

        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self._redraw()

    def _redraw(self):
        self.delete('all')
        if self.style == "primary":
            bg = THEME['accent_hover'] if self.is_hover else THEME['accent']
            fg = '#FFFFFF'
        else:
            bg = THEME['danger_hover'] if self.is_hover else THEME['danger']
            fg = '#FFFFFF'

        draw_rounded_rect(self, 2, 2, self.w - 2, self.h - 2, 10, fill=bg, outline='')
        self.create_text(self.w // 2, self.h // 2, text=self.text, fill=fg, font=F_BODY_B)

    def _on_enter(self, _):
        self.is_hover = True
        self.config(cursor='hand2')
        self._redraw()

    def _on_leave(self, _):
        self.is_hover = False
        self._redraw()

    def _on_click(self, _):
        if self.command:
            self.command()


# ═══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════
class ExcelImageExtractorTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel 网页图片合并提取工具")
        self.root.geometry("540x680")
        self.root.minsize(500, 620)
        self.root.configure(bg=THEME['bg'])

        self.running = False
        self.paste_direction = tk.StringVar(value='right')  # 'left' 或 'right'

        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self.root, bg=THEME['bg'])
        container.pack(fill='both', expand=True, padx=18, pady=16)

        # ── 标题栏 ──
        header = tk.Frame(container, bg=THEME['bg'])
        header.pack(fill='x', pady=(0, 10))
        tk.Label(header, text="✨ Excel 智能图片提取合并", font=F_TITLE, fg=THEME['text_main'], bg=THEME['bg']).pack(side='left')
        tk.Label(header, text="Win11 Modern", font=F_SMALL, fg=THEME['text_muted'], bg=THEME['bg']).pack(side='right', pady=(4, 0))

        # ── 配置卡片 (Frosted Card) ──
        card = tk.Frame(container, bg=THEME['card_bg'], highlightthickness=1, highlightbackground=THEME['card_border'])
        card.pack(fill='x', pady=(0, 12))
        inner_card = tk.Frame(card, bg=THEME['card_bg'], padx=16, pady=14)
        inner_card.pack(fill='x')

        # 1. 行数输入
        r1 = tk.Frame(inner_card, bg=THEME['card_bg'])
        r1.pack(fill='x', pady=(0, 10))
        tk.Label(r1, text="处理行数", font=F_BODY_B, fg=THEME['text_main'], bg=THEME['card_bg']).pack(side='left')
        self.entry_count = tk.Entry(
            r1, width=10, font=F_BODY, justify='center',
            bg=THEME['input_bg'], fg=THEME['text_main'],
            highlightthickness=1, highlightbackground=THEME['input_border'], relief='flat'
        )
        self.entry_count.insert(0, "10")
        self.entry_count.pack(side='left', padx=(14, 0))

        # 分割线
        tk.Frame(inner_card, bg=THEME['card_border'], height=1).pack(fill='x', pady=(2, 10))

        # 2. 粘贴方向选择 (左侧 / 右侧)
        r2 = tk.Frame(inner_card, bg=THEME['card_bg'])
        r2.pack(fill='x', pady=(0, 6))
        tk.Label(r2, text="粘贴方向", font=F_BODY_B, fg=THEME['text_main'], bg=THEME['card_bg']).pack(side='left')
        ModernPillToggle(r2, "👉 粘贴到右侧单元格", self.paste_direction, 'right').pack(side='left', padx=(14, 6))
        ModernPillToggle(r2, "👈 粘贴到左侧单元格", self.paste_direction, 'left').pack(side='left', padx=2)

        # ── 按钮区域 ──
        btn_box = tk.Frame(container, bg=THEME['bg'])
        btn_box.pack(fill='x', pady=(0, 12))
        self.start_btn = ModernButton(btn_box, "🚀 开始自动化提取并粘贴", command=self.start_extract_process, style="primary", width=320, height=40)
        self.start_btn.pack(side='left', padx=(0, 10))

        self.stop_btn = ModernButton(btn_box, "⏹ 停止", command=self.stop_process, style="danger", width=100, height=40)
        self.stop_btn.pack(side='left')

        # ── 日志控制台卡片 ──
        log_card = tk.Frame(container, bg=THEME['card_bg'], highlightthickness=1, highlightbackground=THEME['card_border'])
        log_card.pack(fill='both', expand=True, pady=(0, 6))

        log_head = tk.Frame(log_card, bg=THEME['card_bg'], padx=12, pady=8)
        log_head.pack(fill='x')
        tk.Label(log_head, text="运行日志", font=F_BODY_B, fg=THEME['text_main'], bg=THEME['card_bg']).pack(side='left')

        log_inner = tk.Frame(log_card, bg=THEME['log_bg'], padx=8, pady=8)
        log_inner.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        self.log_text = tk.Text(
            log_inner, font=F_MONO, bg=THEME['log_bg'], fg=THEME['text_main'],
            wrap='word', relief='flat', bd=0, state='disabled'
        )
        self.log_text.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(log_inner, command=self.log_text.yview, relief='flat', bd=0)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)

        self.log("系统就绪，请选中 Excel 包含链接的首个单元格后点击开始。")

    def log(self, message):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"[{ts}] {message}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def start_extract_process(self):
        try:
            count = int(self.entry_count.get())
            if count <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("参数错误", "请输入大于 0 的有效整数处理行数！")
            return

        direction_label = "右侧" if self.paste_direction.get() == 'right' else "左侧"
        self.log(f"已启动任务 | 计划处理 {count} 行 | 目标方向: {direction_label}")
        messagebox.showinfo("准备执行", f"已设为粘贴到【{direction_label}】单元格。\n请在 5 秒内切换并激活 Excel 中的起始单元格！")
        self.root.after(5000, lambda: self.run_batch_extract(count))

    def stop_process(self):
        self.running = False
        self.log("⚠️ 已发送停止指令，当前行处理完毕后将退出。")

    # ──────────────────────────────────────────────────────────
    #  图片链接提取 (严格顺序 + Tool Result 匹配)
    # ──────────────────────────────────────────────────────────
    def extract_image_urls_from_html(self, html_text):
        soup = BeautifulSoup(html_text, 'html.parser')
        img_urls = []

        # 优先级提取 Tool Result 区域的产物图
        target_imgs = soup.select('.tool-calls img.clickable-img')
        if not target_imgs:
            target_imgs = soup.select('.tool-calls img')
        if not target_imgs:
            target_imgs = soup.select('img.clickable-img')

        for img in target_imgs:
            src = img.get('src') or img.get('data-src')
            if src and src.strip():
                src_clean = src.strip()
                if src_clean not in img_urls:
                    img_urls.append(src_clean)

        # 正则备用
        if not img_urls:
            raw_matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html_text)
            for url in raw_matches:
                url_clean = url.strip()
                if url_clean and url_clean not in img_urls:
                    img_urls.append(url_clean)

        return img_urls

    # ──────────────────────────────────────────────────────────
    #  智能合并管线 (继承自 hb.py 布局规则)
    # ──────────────────────────────────────────────────────────
    def merge_images_pipeline(self, img_pil_list):
        if not img_pil_list:
            return None

        images = [img.convert('RGB') if img.mode != 'RGB' else img for img in img_pil_list]
        n = len(images)

        # hb.py 智能布局规则
        if n <= 1:
            cols = 1
        elif n <= 4:
            has_portrait = any(img.height > img.width for img in images)
            cols = n if has_portrait else 2
        else:
            cols = 4

        rows = math.ceil(n / cols)
        cell_w = max(img.width for img in images)
        cell_h = max(img.height for img in images)

        # 0.2% 边距规则
        gap = max(1, int(max(cols * cell_w, rows * cell_h) * 0.002))
        tw = cols * cell_w + (cols - 1) * gap
        th = rows * cell_h + (rows - 1) * gap

        merged = Image.new('RGB', (tw, th), GAP_RGB)

        for idx, img in enumerate(images):
            r, c = idx // cols, idx % cols
            padded = ImageOps.pad(img, (cell_w, cell_h), color=GAP_RGB, method=Image.Resampling.LANCZOS)
            merged.paste(padded, (c * (cell_w + gap), r * (cell_h + gap)))

        return self.compress_jpg(merged, limit_mb=20)

    # ──────────────────────────────────────────────────────────
    #  JPG 20MB 压缩策略 (二分质量 + LANCZOS 缩放)
    # ──────────────────────────────────────────────────────────
    def compress_jpg(self, img, limit_mb=20):
        limit = limit_mb * 1024 * 1024
        ow, oh = img.size

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            temp_path = tmp_file.name

        def _save(q, sc=1.0):
            t = (img if sc >= 0.999
                 else img.resize((max(1, int(ow * sc)), max(1, int(oh * sc))), Image.Resampling.LANCZOS))
            t.save(temp_path, format='JPEG', quality=q, optimize=True)
            return os.path.getsize(temp_path)

        try:
            if _save(95) <= limit:
                return Image.open(temp_path).copy()

            lo, hi, bq = 80, 94, 80
            while lo <= hi:
                mid = (lo + hi) // 2
                if _save(mid) <= limit:
                    bq = mid
                    lo = mid + 1
                else:
                    hi = mid - 1

            if _save(bq) <= limit:
                return Image.open(temp_path).copy()

            sl, sh, bsc = 50, 98, 50
            while sl <= sh:
                sm = (sl + sh) // 2
                if _save(80, sm / 100.0) <= limit:
                    bsc = sm
                    sl = sm + 1
                else:
                    sh = sm - 1

            _save(80, bsc / 100.0)
            return Image.open(temp_path).copy()
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def set_image_to_clipboard(self, pil_image):
        output = io.BytesIO()
        pil_image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]  # 去掉 14 字节 BMP 文件头转为 DIB
        output.close()

        for _ in range(5):
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                return True
            except Exception:
                time.sleep(0.1)
        return False

    def get_url_from_cell(self):
        pyperclip.copy("")
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.3)
        return pyperclip.paste().strip()

    # ──────────────────────────────────────────────────────────
    #  核心遍历与方向路由
    # ──────────────────────────────────────────────────────────
    def run_batch_extract(self, total_count):
        def worker():
            self.running = True
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            target_dir = self.paste_direction.get()

            try:
                for idx in range(total_count):
                    if not self.running:
                        self.log("任务已终止。")
                        break

                    url = self.get_url_from_cell()
                    self.log(f"[{idx + 1}/{total_count}] 链接: {url[:45]}..." if len(url) > 45 else f"[{idx + 1}/{total_count}] 链接: {url}")

                    if not url.startswith(('http://', 'https://')):
                        self.log(f"[{idx + 1}/{total_count}] ⚠️ 单元格非有效链接，下移一行")
                        pyautogui.press('down')
                        time.sleep(0.2)
                        continue

                    # 1. 抓取图片链接
                    img_urls = []
                    try:
                        resp = requests.get(url, headers=headers, timeout=12)
                        resp.encoding = resp.apparent_encoding
                        if resp.status_code == 200:
                            img_urls = self.extract_image_urls_from_html(resp.text)
                    except Exception as e:
                        self.log(f"请求失败: {e}")

                    # 2. 下载并拼图
                    merged_img = None
                    if img_urls:
                        self.log(f"[{idx + 1}/{total_count}] 抓取到 {len(img_urls)} 张图片，合并中...")
                        downloaded = []
                        for u in img_urls:
                            try:
                                r = requests.get(u, headers=headers, timeout=15)
                                if r.status_code == 200:
                                    downloaded.append(Image.open(io.BytesIO(r.content)))
                            except Exception as e:
                                self.log(f"下载失败: {e}")

                        if downloaded:
                            merged_img = self.merge_images_pipeline(downloaded)

                    # 3. 按方向选择移动并粘贴
                    move_to_target = 'right' if target_dir == 'right' else 'left'
                    move_back      = 'left'  if target_dir == 'right' else 'right'

                    pyautogui.press(move_to_target)
                    time.sleep(0.2)

                    if merged_img:
                        if self.set_image_to_clipboard(merged_img):
                            pyautogui.hotkey('ctrl', 'v')
                            time.sleep(0.4)
                            self.log(f"[{idx + 1}/{total_count}] ✅ 拼图已粘贴到{target_dir.upper()}侧单元格")
                        else:
                            self.log(f"[{idx + 1}/{total_count}] ❌ 写入剪贴板失败")
                    else:
                        self.log(f"[{idx + 1}/{total_count}] ⚠️ 未生成有效拼图")

                    # 4. 回到原链接列并下移一行
                    pyautogui.press(move_back)
                    time.sleep(0.1)
                    pyautogui.press('down')
                    time.sleep(0.3)

                self.log("🎉 全部任务已顺利执行完毕！")
                messagebox.showinfo("完成", "所有任务处理完成！")
            finally:
                self.running = False

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelImageExtractorTool(root)
    root.mainloop()
