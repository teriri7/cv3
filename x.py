import os
import base64
import time
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# 配置参数
API_KEY = "sk-NVQd4Tw4UnoEzIqtiUbeXFsXCAQv8QmeMdGljaIq9s2NIpdf"  # 替换为你的中转API密钥
API_BASE_URL = "https://newapi.pockgo.com/v1/chat/completions"  # 中转API地址（兼容OpenAI格式）

class ImageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片分析工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 12))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        
        # 创建界面组件
        self.create_widgets()
        
        # 确保中文显示正常
        self.root.option_add("*Font", "微软雅黑 10")
    
    def create_widgets(self):
        # 顶部框架
        top_frame = ttk.Frame(self.root, padding=20)
        top_frame.pack(fill=tk.X)
        
        # 标题
        title_label = ttk.Label(top_frame, text="图片自动分析工具", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)
        
        # 开始按钮
        self.start_btn = ttk.Button(
            top_frame, 
            text="开始识别", 
            command=self.start_analysis_thread,
            width=15
        )
        self.start_btn.pack(pady=20)
        
        # 日志区域
        log_frame = ttk.Frame(self.root, padding=(20, 0, 20, 20))
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_label = ttk.Label(log_frame, text="处理日志:")
        log_label.pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            height=10,
            font=("微软雅黑", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.log_text.config(state=tk.DISABLED)
    
    def log(self, message):
        """在日志区域显示消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # 滚动到最后
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()  # 刷新界面
    
    def start_analysis_thread(self):
        """启动分析线程，避免界面卡顿"""
        self.start_btn.config(state=tk.DISABLED)
        self.log("开始处理图片...")
        
        # 在新线程中执行分析任务
        thread = threading.Thread(target=self.perform_analysis)
        thread.daemon = True
        thread.start()
    
    def perform_analysis(self):
        """执行图片分析"""
        try:
            if not API_KEY or API_KEY == "请在此处填写你的API密钥":
                self.log("请先在程序中填写你的API密钥")
                messagebox.showerror("错误", "请先在程序中填写你的API密钥")
                return
            
            image_files = self.get_image_files()
            if not image_files:
                self.log("当前文件夹中未找到任何图片文件")
                messagebox.showinfo("提示", "当前文件夹中未找到任何图片文件")
                return
            
            self.log(f"找到 {len(image_files)} 张图片，开始识别...")
            
            # 处理结果
            results = []
            results.append(f"图片识别结果 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            results.append("=" * 50 + "\n")
            
            # 依次处理每张图片
            for i, image_file in enumerate(image_files, 1):
                self.log(f"正在处理第 {i}/{len(image_files)} 张: {image_file}")
                result = self.analyze_image(image_file)
                
                if result:
                    results.append(f"【图片 {i}】{image_file}\n")
                    results.append(f"{result}\n")
                    results.append("-" * 50 + "\n")
                    self.log(f"第 {i} 张图片识别完成")
                else:
                    results.append(f"【图片 {i}】{image_file} - 识别失败\n")
                    results.append("-" * 50 + "\n")
                    self.log(f"第 {i} 张图片识别失败")
            
            # 保存结果
            output_filename = f"image_analysis_results_{time.strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.writelines(results)
                self.log(f"所有图片处理完成，结果已保存至 {output_filename}")
                messagebox.showinfo("完成", f"所有图片处理完成，结果已保存至 {output_filename}")
            except Exception as e:
                error_msg = f"保存结果失败: {e}"
                self.log(error_msg)
                messagebox.showerror("错误", error_msg)
                
        except Exception as e:
            error_msg = f"处理过程中发生错误: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("错误", error_msg)
        finally:
            self.start_btn.config(state=tk.NORMAL)
    
    def get_image_files(self):
        """获取当前文件夹下的所有图片文件"""
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        return [f for f in os.listdir('.') if f.lower().endswith(image_extensions)]
    
    def encode_image(self, image_path):
        """将图片编码为base64格式"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            error_msg = f"读取图片 {image_path} 失败: {e}"
            self.log(error_msg)
            return None
    
    def get_mime_type(self, image_path):
        """根据文件后缀获取MIME类型"""
        ext = image_path.lower().split('.')[-1]
        mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp'
        }
        return mime_map.get(ext, 'image/jpeg')
    
    def analyze_image(self, image_path):
        """通过中转API分析图片"""
        base64_image = self.encode_image(image_path)
        if not base64_image:
            return None
    
        mime_type = self.get_mime_type(image_path)
        prompt = """用户将上传图片，请根据每张图片中的客观内容和设计内容，对图片进行描述。
图片详细描述，400到500词左右，尽可能描述画面具体客观内容和设计内容细节。
注意：客观内容主要包括主体的长相、动作、位于画面的位置、朝向画面的角度、姿态、环境、风格体裁、主体年龄、人种、发型、身材、服装造型、五官特征、神情、情绪状态；设计内容主要包括画面构图、景别、观众视角、对焦点（景深）、色调、亮度、饱和度、光照角度、光质、画面风格、情绪、氛围、清晰程度。
输出格式：自然语言描述，语言要流畅、有画面感，不要附加任何解释、说明、标签或非描述内容等冗余开场，仅输出自然语言。我们要做的是内容信息一定要准确。表达方式要有各种各样的、不是特别专业的表达方式，以口语话的方法描述画面内容，不要使用专业的词汇来描述画面，直接输出一整段的文本，不需要进行分段。
参考格式示例：这幅画面给人的第一印象是强烈的对比感和超现实主义的神秘氛围,它巧妙地结合了废墟的萧瑟与奇幻的瑰丽,整个画面的色彩设计是绝对的主导者,它采用了极端的冷暖色调搭配,主体外部环境几乎被一种深邃、压抑的蓝绿色或暗青色所统治,像是永恒的深夜或深海之中,几乎所有细节都沉浸在浓重的阴影里,这种冷色调奠定了压抑且孤寂的基调,然而,画面的核心焦点,那道巨大的古老门廊中央,却喷薄出极度饱和且梦幻的粉紫色光芒,这是核心的暖色调,这种戏剧性的色彩冲突瞬间吸引了所有目光,营造出强烈的视觉冲击。从纯画面情景来看,画面中央嘉立着一座体量巨大、古老且残破不堪的东方风格木质门楼,它的屋顶瓦片缺损严重,木结构也多处断裂,屋顶边缘参差不齐,暗示着它经历了一场巨大的灾难或漫长的时间侵蚀,它的残破感与周围环境的阴暗融为一体,突出了"废墟"的主题,门楼的两侧延伸出低矮的围墙和建筑残骸,这些墙体由粗糙的石砖或泥土砌成,表面有着明显的风化痕迹,进一步加深了画面的荒凉感,在门楼的前方和四周,散落着大量不规则形状的巨大乱石和建筑碎块,这些前景元素增强了画面的空间深度,并让观众感受到地面的崎岖不平,整个地面似乎有一层薄薄的积水,这层水面至关重要,它成为了天然的镜子,将门廊中喷涌出的粉紫色光芒清晰地反射出来,这种水面倒影的处理极大地提升了画面的光影质感和魔幻气息,让"内发光"的光源效果显得更加真实和强烈。再聚焦到门楼的核心区域两扇已经敞开的门板之间,展现的不是背后的景色,而是一片非物质化的、闪耀着光芒的"能量场"或"传送门",这片核心光源是极其复杂的的渐变色,从明亮的蓝紫色过渡到高饱和度的粉红色,仿佛是扭曲的星云或另一个维度空间的晚霞,其中能清晰地观察到无数微小的、闪烁的白色光点,它们像是漂浮的星辰,让这个"洞口"充满了无限的可能和奇幻魅力,这种超自然光源强劲有力,它将周围残破的木质门框、门楼的底部以及地面的积水都染上了一层荧光般的粉紫色溢光,形成了极佳的光影对比和环境光效果,从画面设计词的角度来看,画面的构图设计采用了中央对称的布局,将巨大的门楼置于画面中心,营造出宏大且庄重的仪式感,而两侧的废墟向外延伸,增强了画面的宽阔感和景深。最后,画面右侧中景的位置,是一个背对观众的女性身影,她是画面的主体人物和叙事焦点,她穿着一件浅色的短裤和一件深色但质地柔软的上衣,留着一头过肩长发,她正坚定地向前迈步,身体略微前倾,整个姿态都指向那道发光的门,显示出一种义无反顾的决绝和急切,她被放置在构图的右侧,平衡了门楼巨大的体量,她的存在赋予了整个场景强烈的叙事性和代入感,让"跨越"成为了画面的的核心主题,人物身上的光线处理也很精妙,她迎着门内的光,因此她身体的侧面和边缘都被染上了一层柔和的粉紫色轮廓光,进一步将她与周围冰冷的废墟环境区分开来,整体而言,这个画面在艺术风格上带有明显的日系动漫或奇幻插画的精致感,它通过冷暖色的极端对比、废墟与奇幻元素的融合、以及人物坚定的动作,共同讲述了一个关于冒险、未知和希望的磅礴故事,它成功地将"遗弃"和"重生"这两种截然不同的情绪融合在了一起。"""
        
        # 构造符合OpenAI格式的请求体（兼容中转API）
        payload = {
            "model": "gemini-3-pro-preview-11-2025",  # 中转API支持的模型（根据实际支持的模型修改）
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 300  # 限制回复长度
        }
    
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"  # 中转API的认证方式
        }
    
        try:
            # 发送请求到中转API，超时时间改为60秒
            response = requests.post(API_BASE_URL, json=payload, headers=headers, timeout=60)
            response.raise_for_status()  # 抛出HTTP错误状态码
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            error_msg = f"分析图片 {image_path} 失败: {str(e)}"
            self.log(error_msg)
            return None

def main():
    # 安装依赖（如果未安装）
    try:
        import requests
    except ImportError:
        print("正在安装必要依赖...")
        os.system("pip install requests")
        import requests
    
    # 创建并运行GUI
    root = tk.Tk()
    app = ImageAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
