# -*- coding: utf-8 -*-
"""
图片合并工具 — 粉白主题 · Win11 现代风格
"""

import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageOps
import os
from datetime import datetime
import math
import re

# ═══════════════════════════════════════════════════════════════
#  THEME
# ═══════════════════════════════════════════════════════════════
C = {
    'bg':           '#FFF0F3',
    'card':         '#FFFFFF',
    'accent':       '#FF6B9D',
    'accent_dark':  '#E85585',
    'accent_light': '#FFE8EF',
    'text':         '#2D2D3F',
    'text_muted':   '#A0A0B2',
    'border':       '#F0DDE3',
    'input_bg':     '#FDF5F7',
    'input_border': '#E8D5DC',
    'toggle_off':   '#F3EDF0',
    'drop_bg':      '#FFFAFB',
    'drop_border':  '#FFD6E4',
    'drop_hover':   '#FFE0EB',
    'log_bg':       '#FFFAFB',
}

FT   = ('Segoe UI', 15, 'bold')
FS   = ('Segoe UI', 10, 'bold')
FB   = ('Segoe UI', 10)
FB_B = ('Segoe UI', 10, 'bold')
FXS  = ('Segoe UI', 8)
FM   = ('Cascadia Code', 9)

GAP_RGB = (40, 40, 40)


# ═══════════════════════════════════════════════════════════════
#  ROUNDED RECTANGLE HELPER
# ═══════════════════════════════════════════════════════════════
def _rr(c, x1, y1, x2, y2, r, **kw):
    c.create_polygon(
        x1 + r, y1,     x2 - r, y1,
        x2,     y1,     x2,     y1 + r,
        x2,     y2 - r, x2,     y2,
        x2 - r, y2,     x1 + r, y2,
        x1,     y2,     x1,     y2 - r,
        x1,     y1 + r, x1,     y1,
        smooth=True, **kw)


# ═══════════════════════════════════════════════════════════════
#  WIDGETS
# ═══════════════════════════════════════════════════════════════

class ToggleBtn(tk.Label):
    """排序 / 输出格式的分段选择按钮"""
    def __init__(self, parent, text, variable, value, **kw):
        super().__init__(parent, text=text, font=FB, padx=12, pady=4,
                         cursor='hand2', bg=C['toggle_off'],
                         fg=C['text'], **kw)
        self.var, self.val = variable, value
        self.var.trace_add('write', lambda *_: self._sync())
        self.bind('<Button-1>', lambda e: self.var.set(self.val))
        self.bind('<Enter>', self._enter)
        self.bind('<Leave>', lambda e: self._sync())
        self._sync()

    def _sync(self):
        if self.var.get() == self.val:
            self.configure(bg=C['accent'], fg='#FFFFFF')
        else:
            self.configure(bg=C['toggle_off'], fg=C['text'])

    def _enter(self, _):
        if self.var.get() != self.val:
            self.configure(bg=C['accent_light'])


class AutoToggleBtn(tk.Label):
    """智能布局按钮 — cols=0 且 rows=0 时激活"""
    def __init__(self, parent, text, cols_var, rows_var, **kw):
        super().__init__(parent, text=text, font=FB, padx=12, pady=4,
                         cursor='hand2', bg=C['toggle_off'],
                         fg=C['text'], **kw)
        self.cv = cols_var
        self.rv = rows_var
        self.cv.trace_add('write', lambda *_: self._sync())
        self.rv.trace_add('write', lambda *_: self._sync())
        self.bind('<Button-1>', self._click)
        self.bind('<Enter>', self._enter)
        self.bind('<Leave>', lambda e: self._sync())
        self._sync()

    def _click(self, _):
        self.cv.set(0)
        self.rv.set(0)

    def _active(self):
        return self.cv.get() == 0 and self.rv.get() == 0

    def _sync(self):
        a = self._active()
        self.configure(bg=C['accent'] if a else C['toggle_off'],
                       fg='#FFFFFF' if a else C['text'])

    def _enter(self, _):
        if not self._active():
            self.configure(bg=C['accent_light'])


class GridNumBtn(tk.Label):
    """网格数量按钮 1-10"""
    def __init__(self, parent, number, cols_var, rows_var, group, **kw):
        super().__init__(parent, text=str(number), font=FB_B, width=3,
                         bg=C['input_bg'], fg=C['text'],
                         cursor='hand2', **kw)
        self.num = number
        self.cv  = cols_var
        self.rv  = rows_var
        self.grp = group
        self.cv.trace_add('write', lambda *_: self._sync())
        self.rv.trace_add('write', lambda *_: self._sync())
        self.bind('<Button-1>', self._click)
        self.bind('<Enter>', self._enter)
        self.bind('<Leave>', lambda e: self._sync())
        self._sync()

    def _click(self, _):
        if self.grp == 'col':
            if self.cv.get() == self.num:
                self.cv.set(0)
            else:
                self.cv.set(self.num)
                self.rv.set(0)
        else:
            if self.rv.get() == self.num:
                self.rv.set(0)
            else:
                self.rv.set(self.num)
                self.cv.set(0)

    def _active(self):
        v = self.cv if self.grp == 'col' else self.rv
        return v.get() == self.num

    def _sync(self):
        a = self._active()
        self.configure(bg=C['accent'] if a else C['input_bg'],
                       fg='#FFFFFF' if a else C['text'])

    def _enter(self, _):
        if not self._active():
            self.configure(bg=C['accent_light'])


# ═══════════════════════════════════════════════════════════════
#  APPLICATION
# ═══════════════════════════════════════════════════════════════

class ImageMergerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("图片合并工具")
        self.root.geometry("960x720")
        self.root.minsize(900, 660)
        self.root.configure(bg=C['bg'])

        self.supported_formats = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
        self.max_images = 100

        self.output_format = tk.StringVar(value='jpg')
        self.sort_by_time  = tk.BooleanVar(value=True)
        self.grid_cols     = tk.IntVar(value=0)
        self.grid_rows     = tk.IntVar(value=0)

        self._build_ui()

    # ══════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════
    def _build_ui(self):
        main = tk.Frame(self.root, bg=C['bg'])
        main.pack(fill='both', expand=True, padx=16, pady=12)

        self._hdr = tk.Canvas(main, bg=C['bg'], height=48,
                              highlightthickness=0)
        self._hdr.pack(fill='x', pady=(0, 10))
        self._hdr.bind('<Configure>',
                       lambda e: self._paint_hdr(e.width, e.height))

        self._build_card(main)
        self._build_drop(main)
        self._build_log(main)

        tk.Label(main,
                 text="✨ 合并后保存在第一张图片所在文件夹   "
                      "✨ 分隔间距 = 最终画布最长边 × 0.2%   "
                      "✨ JPG 背景深灰 / PNG 背景透明",
                 font=FXS, fg=C['text_muted'], bg=C['bg']
                 ).pack(anchor='w', pady=(4, 0))

    def _paint_hdr(self, w, h):
        c = self._hdr
        c.delete('all')
        _rr(c, 2, 2, w - 2, h - 2, 14, fill=C['accent'], outline='')
        c.create_text(w // 2, h // 2,
                      text="🌸  图片合并工具", fill='#FFFFFF', font=FT)

    def _build_card(self, parent):
        outer = tk.Frame(parent, bg=C['bg'])
        outer.pack(fill='x', pady=(0, 6))
        card = tk.Frame(outer, bg=C['card'], highlightthickness=1,
                        highlightbackground=C['border'])
        card.pack(fill='x', padx=4, pady=4)
        inner = tk.Frame(card, bg=C['card'])
        inner.pack(fill='x', padx=14, pady=10)

        # ── Row 1: 排序方式 + 输出格式 ──
        r1 = tk.Frame(inner, bg=C['card'])
        r1.pack(fill='x', pady=(0, 6))
        tk.Label(r1, text="排序方式", font=FS, fg=C['text'],
                 bg=C['card']).pack(side='left')
        ToggleBtn(r1, "📅 按修改时间",
                  self.sort_by_time, True).pack(side='left', padx=(8, 2))
        ToggleBtn(r1, "🔤 按文件名",
                  self.sort_by_time, False).pack(side='left', padx=2)
        tk.Frame(r1, bg=C['card'], width=28).pack(side='left')
        tk.Label(r1, text="输出格式", font=FS, fg=C['text'],
                 bg=C['card']).pack(side='left')
        ToggleBtn(r1, "JPG (压缩至20m)",
                  self.output_format, 'jpg').pack(side='left', padx=(8, 2))
        ToggleBtn(r1, "PNG (无损)",
                  self.output_format, 'png').pack(side='left', padx=2)

        tk.Frame(inner, bg=C['border'], height=1).pack(fill='x', pady=6)

        # ── Row 2: 合并模式 + 智能布局 ──
        r2 = tk.Frame(inner, bg=C['card'])
        r2.pack(fill='x', pady=(0, 6))
        tk.Label(r2, text="合并模式", font=FS, fg=C['text'],
                 bg=C['card']).pack(side='left')
        AutoToggleBtn(r2, "🤖 智能布局",
                      self.grid_cols, self.grid_rows
                      ).pack(side='left', padx=(8, 0))

        # ── Row 3: 横向多少张图片 ──
        r3 = tk.Frame(inner, bg=C['card'])
        r3.pack(fill='x', pady=(4, 2))
        tk.Label(r3, text="横向多少张图片", font=FS, fg=C['text'],
                 bg=C['card']).pack(side='left')
        for i in range(1, 11):
            GridNumBtn(r3, i, self.grid_cols, self.grid_rows, 'col'
                       ).pack(side='left', padx=2, pady=2)

        # ── Row 4: 竖向多少张图片 ──
        r4 = tk.Frame(inner, bg=C['card'])
        r4.pack(fill='x', pady=(2, 4))
        tk.Label(r4, text="竖向多少张图片", font=FS, fg=C['text'],
                 bg=C['card']).pack(side='left')
        for i in range(1, 11):
            GridNumBtn(r4, i, self.grid_cols, self.grid_rows, 'row'
                       ).pack(side='left', padx=2, pady=2)

    # ── drop zone ─────────────────────────────────────────────
    def _build_drop(self, parent):
        frame = tk.Frame(parent, bg=C['bg'])
        frame.pack(fill='both', expand=True, pady=(0, 6))
        self.drop_cv = tk.Canvas(frame, bg=C['bg'], highlightthickness=0)
        self.drop_cv.pack(fill='both', expand=True)
        self.drop_cv.bind('<Configure>',
                          lambda e: self._paint_drop(e.width, e.height))
        self.drop_cv.drop_target_register(DND_FILES)
        self.drop_cv.dnd_bind('<<Drop>>', self.handle_drop)
        self.drop_cv.bind('<Enter>', lambda e: self._drop_hov_set(True))
        self.drop_cv.bind('<Leave>', lambda e: self._drop_hov_set(False))
        self._drop_hov = False

    def _paint_drop(self, w, h):
        c = self.drop_cv
        c.delete('all')
        fill = C['drop_hover'] if self._drop_hov else C['drop_bg']
        bdr  = C['accent']    if self._drop_hov else C['drop_border']
        _rr(c, 3, 3, w - 3, h - 3, 18,
            fill=fill, outline=bdr, width=2, dash=(10, 5))
        fs = min(12, max(9, h // 18))
        c.create_text(w // 2, h // 2 - fs,
                      text="📂  拖放图片或文件夹至此",
                      fill=C['text'] if self._drop_hov else C['text_muted'],
                      font=('Segoe UI', fs))
        c.create_text(w // 2, h // 2 + fs + 2,
                      text="支持格式: JPG · PNG · WEBP · BMP",
                      fill=C['text_muted'],
                      font=('Segoe UI', max(8, fs - 2)))

    def _drop_hov_set(self, entering):
        self._drop_hov = entering
        self._paint_drop(self.drop_cv.winfo_width(),
                         self.drop_cv.winfo_height())

    # ── log ───────────────────────────────────────────────────
    def _build_log(self, parent):
        outer = tk.Frame(parent, bg=C['bg'])
        outer.pack(fill='both', expand=True, pady=(0, 4))
        card = tk.Frame(outer, bg=C['card'], highlightthickness=1,
                        highlightbackground=C['border'])
        card.pack(fill='both', expand=True, padx=4, pady=4)
        tk.Label(card, text="操作日志", font=FS, fg=C['text'],
                 bg=C['card']).pack(anchor='w', padx=12, pady=(8, 2))
        lf = tk.Frame(card, bg=C['log_bg'])
        lf.pack(fill='both', expand=True, padx=10, pady=(0, 8))
        self.log_text = tk.Text(lf, height=5, state='disabled',
                                bg=C['log_bg'], fg=C['text'], font=FM,
                                wrap='word', relief='flat', bd=0,
                                selectbackground=C['accent_light'],
                                selectforeground=C['text'],
                                insertbackground=C['accent'])
        self.log_text.pack(side='left', fill='both', expand=True)
        sb = tk.Scrollbar(lf, command=self.log_text.yview,
                          bg=C['bg'], troughcolor=C['log_bg'],
                          relief='flat', bd=0)
        sb.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=sb.set)

    # ══════════════════════════════════════════════════════════
    #  LOG HELPER
    # ══════════════════════════════════════════════════════════
    def log_message(self, message, level="INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        pfx = ("✅" if "成功" in message
               else "⚠️" if "忽略" in message or "警告" in message
               else "📌")
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"[{ts}] {pfx} {message}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    # ══════════════════════════════════════════════════════════
    #  DRAG & DROP
    # ══════════════════════════════════════════════════════════
    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        valid = []
        for f in files:
            if os.path.splitext(f)[1].lower() in self.supported_formats:
                valid.append(f)
            else:
                self.log_message(f"忽略不支持的文件: {os.path.basename(f)}")
        if not valid:
            self.log_message("至少需要 1 张有效图片")
            return
        valid = self.sort_files(valid)
        if len(valid) > self.max_images:
            self.log_message(
                f"超过上限 {self.max_images} 张，仅处理前 {self.max_images} 张")
            valid = valid[:self.max_images]

        gc, gr = self.grid_cols.get(), self.grid_rows.get()
        sd = "按修改时间(升序)" if self.sort_by_time.get() else "按文件名"
        if gc > 0:
            md = f"横向 {gc} 张"
        elif gr > 0:
            md = f"竖向 {gr} 张"
        else:
            md = "智能布局"

        self.log_message(f"处理 {len(valid)} 张图片 | 排序: {sd}")
        self.log_message(
            f"模式: {md} | 格式: {self.output_format.get().upper()}")
        try:
            path = self.merge_images(valid)
            self.log_message(f"合并成功！保存至: {path}")
        except Exception as e:
            self.log_message(f"处理出错: {e}", level="ERROR")

    # ══════════════════════════════════════════════════════════
    #  SORTING
    # ══════════════════════════════════════════════════════════
    def sort_files(self, fps):
        if self.sort_by_time.get():
            fps.sort(key=lambda x: os.path.getmtime(x))
        else:
            names = [os.path.splitext(os.path.basename(p))[0] for p in fps]
            if all(re.match(r'^\d+$', n) for n in names):
                fps.sort(key=lambda x: int(
                    os.path.splitext(os.path.basename(x))[0]))
            else:
                fps.sort(key=lambda x: os.path.basename(x))
        return fps

    # ══════════════════════════════════════════════════════════
    #  MERGE — 智能布局 + 网格
    # ══════════════════════════════════════════════════════════
    #
    #  智能布局规则：
    #    1 张          → 1 列（单张直接输出）
    #    2-4 张 竖屏    → 全部排一行（竖屏图片横向拼接）
    #    2-4 张 横屏/方  → 两列网格
    #    5 张及以上      → 四列网格
    #
    #  用户手动选了"横向多少张"或"竖向多少张"时
    #  覆盖智能布局
    #
    def merge_images(self, file_paths):
        images = []
        for p in file_paths:
            img = Image.open(p)
            if self.output_format.get() == 'png':
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
            else:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
            images.append(img)

        n  = len(images)
        gc = self.grid_cols.get()
        gr = self.grid_rows.get()

        if gc > 0:
            cols = gc
        elif gr > 0:
            cols = max(1, math.ceil(n / gr))
        else:
            # ── 智能布局 ──
            if n <= 1:
                cols = 1
            elif n <= 4:
                # 存在竖屏图片 → 全部排一行；否则两列网格
                has_portrait = any(img.height > img.width for img in images)
                cols = n if has_portrait else 2
            else:
                cols = 4

        rows = math.ceil(n / cols)
        self.log_message(f"网格布局: {cols}列 × {rows}行")
        return self._merge_grid(images, file_paths, cols)

    def _merge_grid(self, images, fps, cols):
        if not images:
            raise ValueError("没有图片可合并")

        n    = len(images)
        rows = math.ceil(n / cols)
        cell_w = max(img.width  for img in images)
        cell_h = max(img.height for img in images)

        gap = max(1, int(max(cols * cell_w, rows * cell_h) * 0.002))
        tw  = cols * cell_w + (cols - 1) * gap
        th  = rows * cell_h + (rows - 1) * gap

        is_jpg = self.output_format.get() == 'jpg'
        if is_jpg:
            merged    = Image.new('RGB', (tw, th), GAP_RGB)
            pad_color = GAP_RGB
        else:
            merged    = Image.new('RGBA', (tw, th), (0, 0, 0, 0))
            pad_color = (0, 0, 0, 0)

        for idx, img in enumerate(images):
            r, c = idx // cols, idx % cols
            padded = ImageOps.pad(
                img, (cell_w, cell_h),
                color=pad_color,
                method=Image.Resampling.LANCZOS)
            merged.paste(padded,
                         (c * (cell_w + gap), r * (cell_h + gap)))

        return self.save_image(merged, fps[0])

    # ══════════════════════════════════════════════════════════
    #  COMPRESSION — 三阶段策略
    # ══════════════════════════════════════════════════════════
    def save_jpg_with_limit(self, img, fp, limit_mb=20):
        limit = limit_mb * 1024 * 1024
        ow, oh = img.size

        def _save(q, sc=1.0):
            t = (img if sc >= 0.999
                 else img.resize((max(1, int(ow * sc)),
                                  max(1, int(oh * sc))),
                                 Image.Resampling.LANCZOS))
            t.save(fp, format='JPEG', quality=q, optimize=True)
            return os.path.getsize(fp)

        # Phase 1a: quality=95
        sz = _save(95)
        if sz <= limit:
            self.log_message(
                f"JPG: quality=95, 无需压缩 ({sz / 1048576:.1f}MB)")
            return

        # Phase 1b: 二分 [80, 94]
        lo, hi, bq, bs = 80, 94, -1, float('inf')
        while lo <= hi:
            mid = (lo + hi) // 2
            sz = _save(mid)
            if sz <= limit:
                bq, bs = mid, sz
                lo = mid + 1
            else:
                hi = mid - 1

        if bq >= 80:
            bs = _save(bq)
            if bs >= limit * 0.70:
                self.log_message(
                    f"JPG: quality={bq}, {ow}x{oh}, "
                    f"{bs / 1048576:.1f}MB")
                return

            # Phase 1.5: 更高画质 + 缩分辨率
            hq = min(bq + 1, 95)
            self.log_message(
                f"quality={bq} 仅 {bs / 1048576:.1f}MB，"
                f"尝试 quality={hq} + 缩小分辨率...")

            sz = _save(hq)
            if sz <= limit:
                self.log_message(
                    f"JPG: quality={hq}, {ow}x{oh}, "
                    f"{sz / 1048576:.1f}MB")
                return

            sl, sh, bsc = 50, 98, -1
            while sl <= sh:
                sm = (sl + sh) // 2
                sz = _save(hq, sm / 100.0)
                if sz <= limit:
                    bsc = sm
                    sl = sm + 1
                else:
                    sh = sm - 1

            if bsc >= 50:
                sz = _save(hq, bsc / 100.0)
                nw = max(1, int(ow * bsc / 100))
                nh = max(1, int(oh * bsc / 100))
                self.log_message(
                    f"JPG: quality={hq}, 缩放{bsc}%"
                    f"({nw}x{nh}), {sz / 1048576:.1f}MB")
                return

            _save(bq)
            self.log_message(
                f"JPG: quality={bq}, {ow}x{oh}, "
                f"{bs / 1048576:.1f}MB")
            return

        # Phase 2: quality=80 仍超限 → 缩分辨率
        self.log_message("quality=80 仍超限，开始缩小分辨率...")
        sl, sh, bsc = 50, 98, -1
        while sl <= sh:
            sm = (sl + sh) // 2
            sz = _save(80, sm / 100.0)
            if sz <= limit:
                bsc = sm
                sl = sm + 1
            else:
                sh = sm - 1

        if bsc >= 50:
            sz = _save(80, bsc / 100.0)
            nw = max(1, int(ow * bsc / 100))
            nh = max(1, int(oh * bsc / 100))
            self.log_message(
                f"JPG: quality=80, 缩放{bsc}%"
                f"({nw}x{nh}), {sz / 1048576:.1f}MB")
            return

        sz = _save(80, 0.50)
        self.log_message(f"警告: 已缩至50%，{sz / 1048576:.1f}MB")

    def save_png_with_limit(self, img, fp, limit_mb=20):
        limit = limit_mb * 1024 * 1024
        ow, oh = img.size

        def _save(cl, sc=1.0):
            t = (img if sc >= 0.999
                 else img.resize((max(1, int(ow * sc)),
                                  max(1, int(oh * sc))),
                                 Image.Resampling.LANCZOS))
            t.save(fp, format='PNG', compress_level=cl)
            return os.path.getsize(fp)

        sz = _save(6)
        if sz <= limit:
            self.log_message(
                f"PNG: compress_level=6 ({sz / 1048576:.1f}MB)")
            return

        sz = _save(9)
        if sz <= limit:
            self.log_message(
                f"PNG: compress_level=9 ({sz / 1048576:.1f}MB)")
            return

        self.log_message(
            "PNG compress_level=9 仍超限，开始缩小分辨率...")
        sl, sh, bsc = 50, 98, -1
        while sl <= sh:
            sm = (sl + sh) // 2
            sz = _save(9, sm / 100.0)
            if sz <= limit:
                bsc = sm
                sl = sm + 1
            else:
                sh = sm - 1

        if bsc >= 50:
            sz = _save(9, bsc / 100.0)
            nw = max(1, int(ow * bsc / 100))
            nh = max(1, int(oh * bsc / 100))
            self.log_message(
                f"PNG: 缩放{bsc}%({nw}x{nh}), "
                f"{sz / 1048576:.1f}MB")
            return

        sz = _save(9, 0.50)
        self.log_message(f"警告: 已缩至50%，{sz / 1048576:.1f}MB")

    # ── 统一保存入口 ──────────────────────────────────────────
    def save_image(self, image, ref_path):
        out_dir = os.path.dirname(ref_path)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        gc = self.grid_cols.get()
        gr = self.grid_rows.get()
        if gc > 0:
            layout = f'c{gc}'
        elif gr > 0:
            layout = f'r{gr}'
        else:
            layout = 'auto'
        fmt = self.output_format.get()
        fp = os.path.join(out_dir, f"merged_{layout}_{ts}.{fmt}")

        if fmt == 'jpg':
            if image.mode != 'RGB':
                image = image.convert('RGB')
            self.save_jpg_with_limit(image, fp)
        else:
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            self.save_png_with_limit(image, fp)
        return fp


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    root = TkinterDnD.Tk()
    app = ImageMergerApp(root)
    root.mainloop()
