# sdes_gui.py - S-DES 算法图形界面

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sdes
import brute_force
import sys

# 设置高DPI感知，解决字体模糊问题
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass


class SDesGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("S-DES 加解密工具")
        self.root.geometry("900x800")
        self.root.resizable(True, True)
        
        # 设置现代化主题
        self.setup_style()
        
        # 设置窗口图标和样式
        self.root.configure(bg='#f8f9fa')
        
        # 创建主容器
        main_container = tk.Frame(root, bg='#f8f9fa')
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 创建标题
        title_frame = tk.Frame(main_container, bg='#f8f9fa')
        title_frame.pack(fill="x", pady=(0, 15))
        
        title_label = tk.Label(
            title_frame, 
            text="S-DES 加密算法工具", 
            font=("Microsoft YaHei", 20, "bold"),
            fg='#333333',
            bg='#f8f9fa'
        )
        title_label.pack()

        # 创建标签页控件
        self.tab_control = ttk.Notebook(main_container, style="Custom.TNotebook")

        # 创建加解密标签页
        crypto_tab = tk.Frame(self.tab_control, bg='#ffffff')
        self.tab_control.add(crypto_tab, text="🔒 加解密")

        # 创建暴力破解标签页
        brute_tab = tk.Frame(self.tab_control, bg='#ffffff')
        self.tab_control.add(brute_tab, text="🔓 暴力破解")

        self.tab_control.pack(expand=1, fill="both")

        # 初始化各个界面
        self.init_crypto_tab(crypto_tab)
        self.init_brute_tab(brute_tab)
    
    def setup_style(self):
        """设置现代化样式"""
        style = ttk.Style()
        
        # 设置主题
        style.theme_use('clam')
        
        # 自定义Notebook样式
        style.configure("Custom.TNotebook", 
                       background='#f5f5f5',
                       borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                       padding=[20, 12],
                       background='#ffffff',
                       foreground='#666666',
                       font=("Microsoft YaHei", 12, "bold"))
        style.map("Custom.TNotebook.Tab",
                 background=[('selected', '#ffffff'),
                           ('active', '#f0f0f0')])
        
        # 自定义LabelFrame样式
        style.configure("Custom.TLabelframe",
                       background='#ffffff',
                       borderwidth=0,
                       relief="flat")
        style.configure("Custom.TLabelframe.Label",
                       background='#ffffff',
                       foreground='#333333',
                       font=("Microsoft YaHei", 12, "bold"))
        
        # 自定义Entry样式
        style.configure("Custom.TEntry",
                       fieldbackground='white',
                       borderwidth=1,
                       relief="solid",
                       padding=[8, 6])
        
        # 自定义Spinbox样式
        style.configure("Custom.TSpinbox",
                       fieldbackground='white',
                       borderwidth=1,
                       relief="solid",
                       padding=[8, 6])

    def init_crypto_tab(self, parent):
        """初始化加解密标签页"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(parent, text="输入数据", style="Custom.TLabelframe")
        input_frame.pack(fill="x", expand=True, padx=20, pady=15)

        # 明文/密文输入
        input_label = tk.Label(
            input_frame, 
            text="输入内容：", 
            font=("Microsoft YaHei", 12, "bold"),
            fg='#333333',
            bg='#ffffff'
        )
        input_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        
        # 输入文本框容器
        text_container = tk.Frame(input_frame, bg='#ffffff')
        text_container.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.input_text = scrolledtext.ScrolledText(
            text_container, 
            height=4, 
            width=50,
            font=("Consolas", 12, "bold"),
            bg='white',
            fg='#333333',
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.input_text.pack(fill="both", expand=True)
        
        # 添加占位符文本
        self.input_text.insert("1.0", "请输入要加密/解密的内容...")
        self.input_text.config(fg='#999999')
        self.input_text.bind("<FocusIn>", self.on_input_focus_in)
        self.input_text.bind("<FocusOut>", self.on_input_focus_out)

        # 密钥输入区域
        key_label = tk.Label(
            input_frame, 
            text="密钥 (10位二进制)：", 
            font=("Microsoft YaHei", 12, "bold"),
            fg='#333333',
            bg='#ffffff'
        )
        key_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.key_entry = ttk.Entry(
            input_frame, 
            width=35, 
            style="Custom.TEntry",
            font=("Consolas", 13, "bold")
        )
        self.key_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # 示例提示
        example_label = tk.Label(
            input_frame,
            text="示例：1100110011",
            font=("Microsoft YaHei", 10),
            fg='#666666',
            bg='#ffffff'
        )
        example_label.grid(row=2, column=1, padx=10, pady=(0, 10), sticky="w")

        # 模式选择区域
        mode_label = tk.Label(
            input_frame, 
            text="处理模式：", 
            font=("Microsoft YaHei", 12, "bold"),
            fg='#333333',
            bg='#ffffff'
        )
        mode_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.mode_var = tk.StringVar(value="binary")
        mode_frame = tk.Frame(input_frame, bg='#ffffff')
        mode_frame.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # 创建自定义样式的单选按钮
        self.binary_radio = tk.Radiobutton(
            mode_frame, 
            text="二进制模式", 
            variable=self.mode_var, 
            value="binary",
            font=("Microsoft YaHei", 12, "bold"),
            fg='#2196F3',
            bg='#ffffff',
            selectcolor='#2196F3',
            activebackground='#ffffff',
            command=self.update_mode_style
        )
        self.binary_radio.pack(side=tk.LEFT, padx=15)
        
        self.ascii_radio = tk.Radiobutton(
            mode_frame, 
            text="ASCII模式", 
            variable=self.mode_var, 
            value="ascii",
            font=("Microsoft YaHei", 12),
            fg='#333333',
            bg='#ffffff',
            selectcolor='#2196F3',
            activebackground='#ffffff',
            command=self.update_mode_style
        )
        self.ascii_radio.pack(side=tk.LEFT, padx=15)

        # 创建按钮区域
        button_frame = tk.Frame(parent, bg='#ffffff')
        button_frame.pack(fill="x", expand=True, padx=20, pady=15)
        
        # 按钮容器
        btn_container = tk.Frame(button_frame, bg='#ffffff')
        btn_container.pack(expand=True)

        encrypt_btn = tk.Button(
            btn_container,
            text="加密",
            command=self.encrypt,
            font=("Microsoft YaHei", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2"
        )
        encrypt_btn.pack(side=tk.LEFT, padx=8)
        encrypt_btn.bind("<Enter>", lambda e: encrypt_btn.config(bg='#45a049'))
        encrypt_btn.bind("<Leave>", lambda e: encrypt_btn.config(bg='#4CAF50'))

        decrypt_btn = tk.Button(
            btn_container,
            text="解密",
            command=self.decrypt,
            font=("Microsoft YaHei", 12, "bold"),
            bg='#2196F3',
            fg='white',
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2"
        )
        decrypt_btn.pack(side=tk.LEFT, padx=8)
        decrypt_btn.bind("<Enter>", lambda e: decrypt_btn.config(bg='#1976D2'))
        decrypt_btn.bind("<Leave>", lambda e: decrypt_btn.config(bg='#2196F3'))

        clear_btn = tk.Button(
            btn_container,
            text="清空",
            command=self.clear_fields,
            font=("Microsoft YaHei", 12, "bold"),
            bg='#757575',
            fg='white',
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=8)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg='#616161'))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg='#757575'))

        # 创建输出区域
        output_frame = ttk.LabelFrame(parent, text="输出结果", style="Custom.TLabelframe")
        output_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            height=5, 
            width=50, 
            state="disabled",
            font=("Consolas", 12, "bold"),
            bg='#f8f9fa',
            fg='#333333',
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)

        # 配置列权重
        input_frame.columnconfigure(1, weight=1)
        
        # 初始化样式
        self.update_mode_style()

    def init_brute_tab(self, parent):
        """初始化暴力破解标签页"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(parent, text="明密文对输入", style="Custom.TLabelframe")
        input_frame.pack(fill="x", expand=True, padx=20, pady=15)

        # 说明标签
        info_label = tk.Label(
            input_frame,
            text="每行输入一个明密文对，格式：明文(8位) 密文(8位)",
            font=("Microsoft YaHei", 11, "bold"),
            fg='#666666',
            bg='#ffffff'
        )
        info_label.grid(row=0, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        # 多行输入
        self.brute_pairs = scrolledtext.ScrolledText(
            input_frame, 
            height=5, 
            width=50,
            font=("Consolas", 12, "bold"),
            bg='white',
            fg='#333333',
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.brute_pairs.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        # 示例文本
        example_label = tk.Label(
            input_frame, 
            text="示例: 10101010 00110011", 
            font=("Microsoft YaHei", 10),
            fg='#666666',
            bg='#ffffff'
        )
        example_label.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        # 线程选择区域
        thread_label = tk.Label(
            input_frame, 
            text="线程数：", 
            font=("Microsoft YaHei", 12, "bold"),
            fg='#333333',
            bg='#ffffff'
        )
        thread_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.thread_var = tk.IntVar(value=4)
        self.thread_spin = ttk.Spinbox(
            input_frame, 
            from_=1, to=32, 
            width=8, 
            textvariable=self.thread_var,
            style="Custom.TSpinbox",
            font=("Consolas", 12, "bold")
        )
        self.thread_spin.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # 性能提示
        perf_label = tk.Label(
            input_frame,
            text="建议不超过CPU核心数",
            font=("Microsoft YaHei", 11, "bold"),
            fg='#999999',
            bg='#ffffff'
        )
        perf_label.grid(row=3, column=2, padx=10, pady=10, sticky="w")

        # 创建按钮区域
        button_frame = tk.Frame(parent, bg='#ffffff')
        button_frame.pack(fill="x", expand=True, padx=20, pady=15)
        
        btn_container = tk.Frame(button_frame, bg='#ffffff')
        btn_container.pack(expand=True)

        start_btn = tk.Button(
            btn_container,
            text="开始破解",
            command=self.run_brute_force,
            font=("Microsoft YaHei", 12, "bold"),
            bg='#f44336',
            fg='white',
            relief="flat",
            padx=25,
            pady=8,
            cursor="hand2"
        )
        start_btn.pack(side=tk.LEFT, padx=8)
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg='#d32f2f'))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg='#f44336'))

        clear_btn = tk.Button(
            btn_container,
            text="清空",
            command=self.clear_brute_fields,
            font=("Microsoft YaHei", 12, "bold"),
            bg='#757575',
            fg='white',
            relief="flat",
            padx=25,
            pady=6,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=8)
        clear_btn.bind("<Enter>", lambda e: clear_btn.config(bg='#616161'))
        clear_btn.bind("<Leave>", lambda e: clear_btn.config(bg='#757575'))

        # 创建结果区域
        result_frame = ttk.LabelFrame(parent, text="破解结果", style="Custom.TLabelframe")
        result_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self.brute_result_text = scrolledtext.ScrolledText(
            result_frame, 
            height=10, 
            width=50, 
            state="disabled",
            font=("Consolas", 12, "bold"),
            bg='#f8f9fa',
            fg='#333333',
            relief="solid",
            borderwidth=1,
            wrap=tk.WORD
        )
        self.brute_result_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 配置列权重
        input_frame.columnconfigure(0, weight=1)

    def on_input_focus_in(self, event):
        """输入框获得焦点时清除占位符"""
        if self.input_text.get("1.0", tk.END).strip() == "请输入要加密/解密的内容...":
            self.input_text.delete("1.0", tk.END)
            self.input_text.config(fg='#333333')

    def on_input_focus_out(self, event):
        """输入框失去焦点时显示占位符"""
        if not self.input_text.get("1.0", tk.END).strip():
            self.input_text.insert("1.0", "请输入要加密/解密的内容...")
            self.input_text.config(fg='#999999')


    def update_mode_style(self):
        """更新模式选择按钮的样式"""
        if self.mode_var.get() == "binary":
            # 选中二进制模式
            self.binary_radio.config(
                fg='#2196F3',
                font=("Microsoft YaHei", 12, "bold"),
                selectcolor='#2196F3'
            )
            self.ascii_radio.config(
                fg='#333333',
                font=("Microsoft YaHei", 12),
                selectcolor='white'
            )
        else:
            # 选中ASCII模式
            self.ascii_radio.config(
                fg='#2196F3',
                font=("Microsoft YaHei", 12, "bold"),
                selectcolor='#2196F3'
            )
            self.binary_radio.config(
                fg='#333333',
                font=("Microsoft YaHei", 12),
                selectcolor='white'
            )

    def encrypt(self):
        """加密功能"""
        input_str = self.input_text.get("1.0", tk.END).strip()
        key = self.key_entry.get().strip()
        mode = self.mode_var.get()

        # 检查占位符文本
        if input_str == "请输入要加密/解密的内容...":
            messagebox.showwarning("提示", "请输入要加密的内容！")
            return

        if not key or len(key) != 10 or not all(bit in "01" for bit in key):
            messagebox.showerror("错误", "密钥必须是 10 位二进制！")
            return

        try:
            if mode == "binary":
                if not all(bit in "01" for bit in input_str.replace(" ", "")):
                    messagebox.showerror("错误", "二进制输入只能包含 0 和 1！")
                    return
                # 移除空格并确保是8位的倍数
                input_str = input_str.replace(" ", "")
                if len(input_str) % 8 != 0:
                    messagebox.showerror("错误", "二进制输入长度必须是 8 的倍数！")
                    return

                result = ""
                for i in range(0, len(input_str), 8):
                    block = input_str[i:i + 8]
                    result += sdes.encrypt(block, key) + " "
                result = result.strip()
            else:
                # ASCII模式：输出为原始 ASCII 密文（可能不可见/乱码）
                result = sdes.encrypt_text(input_str, key)

            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", result)
            self.output_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("错误", f"加密失败：{str(e)}")

    def decrypt(self):
        """解密功能"""
        input_str = self.input_text.get("1.0", tk.END).strip()
        key = self.key_entry.get().strip()
        mode = self.mode_var.get()

        # 检查占位符文本
        if input_str == "请输入要加密/解密的内容...":
            messagebox.showwarning("提示", "请输入要解密的内容！")
            return

        if not key or len(key) != 10 or not all(bit in "01" for bit in key):
            messagebox.showerror("错误", "密钥必须是 10 位二进制！")
            return

        try:
            if mode == "binary":
                if not all(bit in "01 " for bit in input_str):
                    messagebox.showerror("错误", "二进制输入只能包含 0、1 和空格！")
                    return
                # 移除空格并确保是8位的倍数
                input_str = input_str.replace(" ", "")
                if len(input_str) % 8 != 0:
                    messagebox.showerror("错误", "二进制输入长度必须是 8 的倍数！")
                    return

                result = ""
                for i in range(0, len(input_str), 8):
                    block = input_str[i:i + 8]
                    result += sdes.decrypt(block, key) + " "
                result = result.strip()
            else:
                # ASCII模式：输入为原始 ASCII 密文，输出为可读明文
                result_text = sdes.decrypt_text(input_str, key)
                result = result_text

            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", result)
            self.output_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror("错误", f"解密失败：{str(e)}")

    def run_brute_force(self):
        """执行暴力破解（支持多对 + 多线程）"""
        raw = self.brute_pairs.get("1.0", tk.END).strip()
        if not raw:
            messagebox.showerror("错误", "请输入至少一行明密文对！")
            return

        pairs = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                messagebox.showerror("错误", f"格式错误: '{line}'，应为: PT CT")
                return
            pt, ct = parts
            if len(pt) != 8 or len(ct) != 8 or not all(b in "01" for b in pt+ct):
                messagebox.showerror("错误", f"位串错误: '{line}'，PT/CT 均需为8位二进制")
                return
            pairs.append((pt, ct))

        threads = max(1, int(self.thread_var.get()))

        # 显示正在破解
        self.brute_result_text.config(state="normal")
        self.brute_result_text.delete("1.0", tk.END)
        self.brute_result_text.insert("1.0", f"正在破解（{len(pairs)} 对, {threads} 线程）...\n")
        self.brute_result_text.config(state="disabled")
        self.root.update()

        # 执行暴力破解
        matched_keys, elapsed_time = brute_force.brute_force_multi(pairs, threads=threads)

        # 显示结果
        self.brute_result_text.config(state="normal")
        self.brute_result_text.delete("1.0", tk.END)
        self.brute_result_text.insert("1.0", f"完成，耗时: {elapsed_time:.4f} 秒\n")
        self.brute_result_text.insert(tk.END, f"找到的匹配密钥数量: {len(matched_keys)}\n\n")

        if matched_keys:
            self.brute_result_text.insert(tk.END, "匹配的密钥:\n")
            for k in matched_keys:
                self.brute_result_text.insert(tk.END, f"- {k}\n")
            # 验证
            self.brute_result_text.insert(tk.END, "\n验证:\n")
            for k in matched_keys:
                ok = all(sdes.encrypt(pt, k) == ct for pt, ct in pairs)
                self.brute_result_text.insert(tk.END, f"{k} -> {'成功' if ok else '失败'}\n")
        else:
            self.brute_result_text.insert(tk.END, "未找到匹配的密钥。")

        self.brute_result_text.config(state="disabled")

    def clear_fields(self):
        """清空输入输出字段"""
        self.input_text.config(state="normal")
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", "请输入要加密/解密的内容...")
        self.input_text.config(fg='#999999', state="normal")
        self.key_entry.delete(0, tk.END)
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")

    def clear_brute_fields(self):
        """清空暴力破解字段"""
        self.brute_pairs.delete("1.0", tk.END)
        self.brute_result_text.config(state="normal")
        self.brute_result_text.delete("1.0", tk.END)
        self.brute_result_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = SDesGUI(root)
    root.mainloop()