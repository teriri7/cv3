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
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 默认模型名称
        self.default_model = "gemini-2.5-pro-thinking"
        
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
        
        # 模型设置
        model_frame = ttk.Frame(top_frame)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        model_label = ttk.Label(model_frame, text="模型名称:")
        model_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.model_entry = ttk.Entry(model_frame, font=("微软雅黑", 10))
        self.model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_entry.insert(0, self.default_model)  # 设置默认模型
        
        # Prompt设置区域
        prompt_frame = ttk.LabelFrame(self.root, text="Prompt设置", padding=10)
        prompt_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 短Prompt
        short_prompt_label = ttk.Label(prompt_frame, text="短Prompt:")
        short_prompt_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.short_prompt_text = scrolledtext.ScrolledText(
            prompt_frame, 
            wrap=tk.WORD, 
            height=4,
            font=("微软雅黑", 9)
        )
        self.short_prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        # 设置短prompt默认内容
        self.short_prompt_text.insert(tk.END, "用户将上传图片，请根据每张图片中的客观内容和设计内容，对图片进行描述。
图片详细描述，200字以内，需要较为简洁但是又尽可能描述画面具体客观内容。
一定要写的（客观内容部分，表达顺序不按下列固定）
1、主体属性、人种（精准到国级、偶尔写人种）、性别、年龄（中年、16岁）
3、主体角度、主体动作、角色间的动作关系
4、构图、景别（如近景，中景，特写）、观众视角（俯瞰、低视角）
5、环境信息
6、风格体裁（写实有时可以默认不写，有时可以写，非写实风格一定要写）
根据画面重点选择性写的（设计内容部分，控制下面内容输出的概率，保证下面的内容有50%左右的概率来写或者不写）
1、情景概括
2、具体长相（三角眼、高颧骨、方下巴）、身份或气质（性感、高冷、甜美、冷酷）、穿着、发型、角色情绪（忧郁、激动、平静）
3、色调、色偏（如白平衡偏青、画面暗部偏红）、灰度或对比度（如log灰色调、中性灰色调、画面偏灰、强对比度）
4、整体画面氛围（烘托出压抑的氛围）
5、氛围、材质质感（如小牛皮纹理质感、胶片颗粒感、皮肤粗糙、雨水反光）
6、特殊艺术处理方式（如浅景深、双重曝光、过曝、延时摄影、暗角等）
输出格式：自然语言描述，语言要流畅、有画面感，不要附加任何解释、说明、标签或非描述内容等冗余开场，仅输出自然语言。内容信息一定要准确。表达方式要有各种各样的、不是特别专业的表达方式，以口语话的方法描述画面内容，不要使用专业的词汇来描述画面，例如中景景别可以写为：露出腰部以上，景深可以写为：画面较为模糊，之类的这种话术，带入小白的视角来描述画面，直接输出一整段的文本，不需要进行分段。
参考格式示例1：重点是别墅上的灯光装饰，夜晚场景中，两层别墅外墙被蓝紫渐变灯光装饰，露台木质地面上，一位穿浅紫上衣的女人和穿深灰西装的男人并肩坐，手持玻璃杯交谈；左侧穿深蓝上衣的女人坐单人椅微笑倾听；右侧穿浅蓝上衣的男人坐躺椅看手机。露台旁泳池泛蓝光，周围绿植在暖光下更繁茂，房屋窗户透出暖黄灯光（描述画面内容，没有设计词）
参考格式示例2：短发年轻女子穿着黄色T恤，挎着一个大黑包，手上端着一只白碗，跪伏在自动步道上，好像在观察着右边玻璃里的自己。（简单画面内容，情景概括）
参考格式示例3：特写镜头，特写人物的表情，柜台后伙计约二十岁，站在柜台后，一手摸着后脑勺，表情困惑，身上裹着浅色粗布棉袄，阳光斜斜地照在柜台的桌面上。微微抬头向外张望，眉头微蹙，背景为民国时期的咸亨酒店，店内冷清，油画写实风格暗黑。高清画质，大师级作品。（基本的画面内容，简单的设计信息）
参考格式示例4：空荡的公交站，路灯下雨水如断线珍珠。站台顶棚的边缘不断滴下水珠，形成雨帘。地面的积水倒映着路灯和人物的破碎倒影。低饱和度冷色调。主光源来自头顶的路灯，在人物身上形成顶光，照亮雨丝却让面部表情半明半暗，增强故事感。（描述画面，有设计词）")
        
        # 长Prompt
        long_prompt_label = ttk.Label(prompt_frame, text="长Prompt:")
        long_prompt_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.long_prompt_text = scrolledtext.ScrolledText(
            prompt_frame, 
            wrap=tk.WORD, 
            height=6,
            font=("微软雅黑", 9)
        )
        self.long_prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        # 设置长prompt默认内容
        self.long_prompt_text.insert(tk.END, "用户将上传图片，请根据每张图片中的客观内容和设计内容，对图片进行描述。
图片详细描述，250到400字以内，需要尽可能描述画面具体客观内容和设计内容。（包括以下部分）
1、情景概括
2、主体属性、人种（精准到国级、偶尔写人种）、性别、年龄（中年、16岁）
3、具体长相（三角眼、高颧骨、方下巴）、身份或气质（性感、高冷、甜美、冷酷）、穿着、发型、角色情绪（忧郁、激动、平静）
4、主体角度（朝向画面哪边）、主体位置（位于画面的哪个地方）、主体动作、角色间的动作关系
5、构图、景别（如中景，近景，特写等）、观众视角（俯瞰、低视角等）
6、环境信息
7、风格体裁（写实有时可以默认不写，有时可以写，非写实风格一定要写）
8、色调、色偏（如白平衡偏青、画面暗部偏红）、灰度或对比度（如log灰色调、中性灰色调、画面偏灰、强对比度）
9、整体画面氛围（烘托出压抑的氛围）
10、氛围、材质质感（如小牛皮纹理质感、胶片颗粒感、皮肤粗糙、雨水反光）
11、特殊艺术处理方式（如浅景深、双重曝光、过曝、延时摄影、暗角等）
输出格式：自然语言描述，语言要流畅、有画面感，不要附加任何解释、说明、标签或非描述内容等冗余开场，不要写有电影感的氛围，戏剧性的画面，像是电影的截图或者一帧，这些无意义的内容，仅输出自然语言。内容信息一定要准确。直接输出一整段的文本，不需要进行分段。
参考格式示例1：画面中心位置上(构图）是一位中年（年龄）西方女性（人种和性别），卷曲的黑发扎成马尾（发型），带着银色耳环，身穿蓝色短袖制服带白色边饰，她侧身对镜头面向画面左侧（主体角度），站立在一扇大窗户旁，窗户悬挂着轻薄的白色窗帘。她两臂抬起，右手轻轻握住窗帘（主体动作），目光温柔地望向窗外，神情沉思。她后面靠近画面右侧的背景中有一个高大的深棕色木质书架，上面整齐摆放着各种颜色的书籍，书架旁还有一部分模糊的白色窗帘（环境信息），增添了室内温馨且富有文化气息的氛围。柔和的自然光透过窗户洒入室内，映照出她的侧脸，营造出宁静沉静的情绪。画面采用中心构图，中景，低角度轻微仰视拍摄，色调柔和（色调），突出平和而舒适的环境。
参考格式示例2：一位年轻的亚洲男性（年龄、人种和性别）站在盛开的樱花树下。他留着棕色微卷短发，三七分刘海（发型），嘴角和下巴有黑色的胡茬，身着深色外套，内搭浅棕色T恤，外套敞开着。他身体侧向画面左侧，脸部正对镜头（主体角度），头部略微偏向画面右侧，眼眶湿润似乎蓄有泪水，眼神直视前方，目光清澈专注，嘴唇微抿，表情略带忧郁、沉思（角色情绪），似乎在思考着什么。背景是模糊的粉白色樱花和深色的树干（环境信息），沐浴在柔和的自然光中。中景（景别），平视视角（观众视角），偏重心构图，主体位于画面中心偏左(构图），浅景深，背景虚化以突出人物。光线柔和，面部有自然阴影，营造出宁静的春日氛围。画面色调整体偏柔和的暖色调（色调），给人一种静谧的感觉。
参考格式示例3：画面左侧(构图）一只浅棕色毛发略显杂乱的狗（主体属性），戴着深棕色项圈，略微侧对镜头（主体角度）站立露出身体，黄色的眼睛平静地看画面右前方。一只带有关节的浅黄色木质纹理的金属机械手从上方轻轻抚摸着狗的耳朵（角色间动作关系）。狗身旁是有机械结构的腿部装置，颜色为黑灰色，带有金属部件，结构复杂且有磨损痕迹。光线从正面照射，背景是带有白色竖条纹的灰色地面和白色地面，地面有交错的光影，显示为室外环境（环境信息）。近景（景别），平视视角（观众视角），科幻风格，狗与机械腿部晰对焦，背景略微模糊，柔和的冷色调光线（色调），营造出一种略带末世感又充满温情的对比氛围。")
        
        # 开始按钮
        self.start_btn = ttk.Button(
            self.root, 
            text="开始识别", 
            command=self.start_analysis_thread,
            width=15
        )
        self.start_btn.pack(pady=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="处理日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
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
            
            # 获取用户输入的模型名称
            model_name = self.model_entry.get().strip()
            if not model_name:
                self.log("模型名称不能为空")
                messagebox.showerror("错误", "模型名称不能为空")
                return
            
            # 获取用户输入的两个prompt
            short_prompt = self.short_prompt_text.get("1.0", tk.END).strip()
            long_prompt = self.long_prompt_text.get("1.0", tk.END).strip()
            
            if not short_prompt or not long_prompt:
                self.log("短prompt和长prompt都不能为空")
                messagebox.showerror("错误", "短prompt和长prompt都不能为空")
                return
            
            image_files = self.get_image_files()
            if not image_files:
                self.log("当前文件夹中未找到任何图片文件")
                messagebox.showinfo("提示", "当前文件夹中未找到任何图片文件")
                return
            
            self.log(f"找到 {len(image_files)} 张图片，开始识别...")
            self.log(f"使用模型: {model_name}")
            
            # 处理结果
            results = []
            results.append(f"图片识别结果 - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            results.append(f"使用模型: {model_name}\n")
            results.append("=" * 80 + "\n")
            
            # 依次处理每张图片
            for i, image_file in enumerate(image_files, 1):
                self.log(f"正在处理第 {i}/{len(image_files)} 张: {image_file}")
                
                # 先用短prompt分析
                self.log(f"使用短prompt分析第 {i} 张图片...")
                short_result = self.analyze_image(image_file, short_prompt, model_name)
                
                # 再用长prompt分析
                self.log(f"使用长prompt分析第 {i} 张图片...")
                long_result = self.analyze_image(image_file, long_prompt, model_name)
                
                # 保存结果
                results.append(f"【图片 {i}】{image_file}\n")
                if short_result:
                    results.append(f"短prompt分析结果:\n{short_result}\n")
                else:
                    results.append("短prompt分析失败\n")
                    
                if long_result:
                    results.append(f"长prompt分析结果:\n{long_result}\n")
                else:
                    results.append("长prompt分析失败\n")
                    
                results.append("-" * 80 + "\n")
                self.log(f"第 {i} 张图片分析完成")
            
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
        """获取当前文件夹下的所有图片文件，包括jfif格式"""
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.jfif')
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
        """根据文件后缀获取MIME类型，增加jfif类型"""
        ext = image_path.lower().split('.')[-1]
        mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'bmp': 'image/bmp',
            'webp': 'image/webp',
            'jfif': 'image/jpeg'  # jfif使用jpeg的MIME类型
        }
        return mime_map.get(ext, 'image/jpeg')
    
    def analyze_image(self, image_path, prompt, model_name):
        """分析图片，接收prompt和model参数"""
        base64_image = self.encode_image(image_path)
        if not base64_image:
            return None
    
        mime_type = self.get_mime_type(image_path)
        
        payload = {
            "model": model_name,  # 使用传入的模型名称
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 30000  
        }
    
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"  
        }
    
        try:
            # 发送请求到中转API
            response = requests.post(API_BASE_URL, json=payload, headers=headers, timeout=120)
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
