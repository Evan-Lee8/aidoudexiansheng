import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import datetime
import time
import threading
import winsound
import sys
import os
import traceback
import logging
import os

# 尝试导入pygame库用于内置音频播放
pygame_available = False
print("[DEBUG] 尝试导入pygame库...")
try:
    import pygame
    pygame_available = True
    print(f"[DEBUG] ✓ 成功导入pygame库: {pygame.version.ver}")
    logging.info(f"成功导入pygame库: {pygame.version.ver}")
except ImportError:
    print("[DEBUG] ✗ pygame库未安装")
    logging.warning("pygame库未安装，将使用备用音频播放方式")
except Exception as e:
    print(f"[DEBUG] ✗ 导入pygame库时发生错误: {e}")
    logging.error(f"导入pygame库时发生未预期的错误: {e}")

print(f"[DEBUG] pygame_available = {pygame_available}")
# 尝试导入playsound库，如果不可用则使用备用方案
playsound_available = False
playsound_func = None
print("[DEBUG] 尝试导入playsound库...")
try:
    # 直接导入playsound库到不同的变量名以避免冲突
    from playsound import playsound as playsound_func
    playsound_available = True
    print(f"[DEBUG] ✓ 成功导入playsound库: {playsound_func}")
    logging.info(f"成功导入playsound库: {playsound_func}")
except ImportError:
    # 库未安装的情况
    print("[DEBUG] ✗ playsound库未安装")
    logging.warning("playsound库未安装，本地音乐播放功能可能受限")
except Exception as e:
    # 其他导入错误
    print(f"[DEBUG] ✗ 导入playsound库时发生错误: {e}")
    logging.error(f"导入playsound库时发生未预期的错误: {e}")

# 打印playsound状态以便调试
print(f"[DEBUG] playsound_available = {playsound_available}")
print(f"[DEBUG] playsound_func = {playsound_func}")

# 创建一个安全的playsound包装函数
def safe_playsound(file_path):
    """安全播放音频文件，处理中文路径问题"""
    if not playsound_available or playsound_func is None:
        raise ImportError("playsound库未安装或不可用")
    
    # 确保路径是字符串并规范化
    file_path = str(file_path)
    print(f"[DEBUG] 尝试播放音频文件: {file_path}")
    
    # 尝试多种编码方式处理Windows中文路径
    if os.name == 'nt':
        # Windows系统的编码处理
        # 1. 首先尝试使用原始路径
        try:
            playsound_func(file_path)
            print("[DEBUG] ✓ 音频播放成功 - 原始路径")
            return True
        except UnicodeDecodeError:
            print("[DEBUG] 原始路径UnicodeDecodeError，尝试GBK编码处理...")
            
        # 2. 尝试使用系统默认编码（GBK）处理路径
        try:
            # 在Python 3中，确保路径是正确的Unicode
            # Windows系统下直接传递Unicode路径
            playsound_func(file_path)
            print("[DEBUG] ✓ 音频播放成功 - Unicode路径")
            return True
        except Exception as e:
            print(f"[DEBUG] Unicode路径处理失败: {e}")
            
        # 3. 尝试不同的路径表示方式
        try:
            # 使用os.path.normpath确保路径格式正确
            norm_path = os.path.normpath(file_path)
            print(f"[DEBUG] 尝试规范化路径: {norm_path}")
            playsound_func(norm_path)
            print("[DEBUG] ✓ 音频播放成功 - 规范化路径")
            return True
        except Exception as e:
            print(f"[DEBUG] 规范化路径处理失败: {e}")
    else:
        # 非Windows系统，直接尝试
        try:
            playsound_func(file_path)
            print("[DEBUG] ✓ 音频播放成功")
            return True
        except Exception as e:
            print(f"[DEBUG] 非Windows系统播放失败: {e}")
    
    # 所有尝试都失败，抛出详细的错误
    error_msg = f"无法播放音频文件: {file_path}"
    print(f"[DEBUG] {error_msg}")
    raise RuntimeError(error_msg)

# 实现内置播放器类
class PygamePlayer:
    """
    使用pygame实现的内置音频播放器
    支持播放、暂停、停止、循环播放等功能
    """
    
    def __init__(self):
        self._is_initialized = False
        self._current_sound = None
        self._is_playing = False
        self._is_paused = False
        self._loop = False
        self._volume = 1.0  # 音量范围0.0-1.0
        self._lock = threading.RLock()
        
        if pygame_available:
            self._initialize_pygame()
    
    def _initialize_pygame(self):
        """初始化pygame音频系统"""
        try:
            pygame.mixer.init()
            self._is_initialized = True
            print("[DEBUG] ✓ pygame音频系统初始化成功")
            logging.info("pygame音频系统初始化成功")
        except Exception as e:
            print(f"[DEBUG] ✗ pygame音频系统初始化失败: {e}")
            logging.error(f"pygame音频系统初始化失败: {e}")
            self._is_initialized = False
    
    def play(self, file_path, loop=False, volume=1.0):
        """
        播放音频文件
        :param file_path: 音频文件路径
        :param loop: 是否循环播放
        :param volume: 音量(0.0-1.0)
        :return: 是否播放成功
        """
        with self._lock:
            try:
                # 确保pygame已初始化
                if not self._is_initialized:
                    self._initialize_pygame()
                    if not self._is_initialized:
                        return False
                
                # 停止当前播放的音频
                self.stop()
                
                # 确保路径是字符串并规范化
                file_path = str(file_path)
                norm_path = os.path.normpath(file_path)
                
                # 加载音频文件
                self._current_sound = pygame.mixer.Sound(norm_path)
                
                # 设置音量
                self._volume = max(0.0, min(1.0, volume))
                self._current_sound.set_volume(self._volume)
                
                # 设置循环
                self._loop = loop
                loops = -1 if loop else 0
                
                # 开始播放
                self._current_sound.play(loops=loops)
                self._is_playing = True
                self._is_paused = False
                
                print(f"[DEBUG] ✓ pygame播放器开始播放: {norm_path} (循环: {loop}, 音量: {volume})")
                logging.info(f"pygame播放器开始播放: {norm_path} (循环: {loop}, 音量: {volume})")
                return True
                
            except Exception as e:
                print(f"[DEBUG] ✗ pygame播放器播放失败: {e}")
                logging.error(f"pygame播放器播放失败: {e}")
                self._is_playing = False
                self._is_paused = False
                self._current_sound = None
                return False
    
    def pause(self):
        """暂停播放"""
        with self._lock:
            if self._is_playing and not self._is_paused and self._current_sound:
                pygame.mixer.pause()
                self._is_paused = True
                print("[DEBUG] ✓ pygame播放器暂停播放")
                logging.info("pygame播放器暂停播放")
    
    def resume(self):
        """恢复播放"""
        with self._lock:
            if self._is_playing and self._is_paused and self._current_sound:
                pygame.mixer.unpause()
                self._is_paused = False
                print("[DEBUG] ✓ pygame播放器恢复播放")
                logging.info("pygame播放器恢复播放")
    
    def stop(self):
        """停止播放"""
        with self._lock:
            if self._is_playing or self._is_paused:
                pygame.mixer.stop()
                self._is_playing = False
                self._is_paused = False
                self._current_sound = None
                print("[DEBUG] ✓ pygame播放器停止播放")
                logging.info("pygame播放器停止播放")
    
    def set_volume(self, volume):
        """
        设置音量
        :param volume: 音量(0.0-1.0)
        """
        with self._lock:
            self._volume = max(0.0, min(1.0, volume))
            if self._current_sound:
                self._current_sound.set_volume(self._volume)
                print(f"[DEBUG] ✓ pygame播放器音量设置为: {self._volume}")
                logging.info(f"pygame播放器音量设置为: {self._volume}")
    
    def get_volume(self):
        """
        获取当前音量
        :return: 当前音量(0.0-1.0)
        """
        with self._lock:
            return self._volume
    
    def is_playing(self):
        """
        检查是否正在播放
        :return: 是否正在播放
        """
        with self._lock:
            if not self._is_playing:
                return False
                
            # 更新播放状态
            if self._current_sound:
                channels = pygame.mixer.find_channel(True)
                if not channels.get_busy() and not self._loop:
                    self._is_playing = False
                    self._current_sound = None
                    
            return self._is_playing
    
    def is_paused(self):
        """
        检查是否暂停
        :return: 是否暂停
        """
        with self._lock:
            return self._is_paused
    
    def is_available(self):
        """
        检查播放器是否可用
        :return: 播放器是否可用
        """
        with self._lock:
            return pygame_available and self._is_initialized
    
    def quit(self):
        """
        清理pygame资源并退出
        """
        with self._lock:
            try:
                # 停止当前播放
                self.stop()
                
                # 清理pygame mixer资源
                if pygame_available and self._is_initialized:
                    pygame.mixer.quit()
                    self._is_initialized = False
                    print("[DEBUG] ✓ pygame音频系统已退出")
                    logging.info("pygame音频系统已退出")
            except Exception as e:
                print(f"[DEBUG] ✗ 退出pygame音频系统时出错: {e}")
                logging.error(f"退出pygame音频系统时出错: {e}")

# 创建全局播放器实例
global_player = PygamePlayer()

# 配置日志
print("[DEBUG] 配置日志系统...")
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='alarm_clock.log',
        filemode='a'
    )
    print("[DEBUG] 日志系统配置成功")
    # 测试日志写入
    logging.info("=== 应用程序启动 ===")
    logging.info(f"playsound库状态: 可用={playsound_available}, 函数={playsound_func}")
except Exception as e:
    print(f"[DEBUG] 日志配置失败: {e}")

# 全局异常处理
def handle_unexpected_error(exctype, value, tb):
    error_info = ''.join(traceback.format_exception(exctype, value, tb))
    logging.error(f"未捕获的异常: {error_info}")
    # 在GUI中显示错误消息
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showerror(
        "应用程序错误",
        f"发生未预期的错误:\n\n{str(value)}\n\n详细信息已记录到日志文件。"
    )
    root.destroy()

# 设置全局异常处理器
sys.excepthook = handle_unexpected_error

class AlarmClockGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("闹钟应用")
        self.root.geometry("650x1000")  # 减小窗口大小以提高稳定性
        self.root.minsize(650, 1000)  # 设置合适的最小尺寸
        self.root.resizable(True, True)  # 允许用户调整窗口大小
        self.root.configure(bg="#f0f0f0")
        
        print("[DEBUG] 初始化GUI对象...")
        logging.info("=== GUI初始化开始 ===")
        
        # 添加强大的主循环保护
        def emergency_update():
            try:
                print("[DEBUG] 紧急更新: 应用程序仍在运行")
                # 确保窗口没有被关闭
                if self.root.winfo_exists():
                    self.root.after(2000, emergency_update)  # 更频繁的更新
            except Exception as e:
                print(f"[DEBUG] 紧急更新错误: {e}")
        
        # 保存紧急更新函数引用
        self.emergency_update_func = emergency_update
        # 启动紧急更新循环
        self.root.after(1000, emergency_update)
        
        # 用于生成唯一闹钟ID的计数器
        self.alarm_id_counter = 1
        logging.info("闹钟应用初始化")
        logging.info(f"应用启动时playsound状态: available={playsound_available}")
        
        # 设置中文字体
        self.font_config = {
            "title": ("SimHei", 24, "bold"),
            "clock": ("SimHei", 48, "bold"),
            "label": ("SimHei", 12),
            "button": ("SimHei", 10, "bold")
        }
        
        # 铃声类型枚举和设置
        self.RINGTONE_TYPES = {
            "默认铃声": (1000, 800),  # 频率(Hz), 持续时间(ms)
            "蜂鸣提醒": (1500, 400),
            "系统提示音": (800, 600),
            "轻柔铃声": (600, 1000)
        }
        # 本地音乐文件路径
        self.local_music_path = None
        
        # 闹钟相关变量
        self.alarms = []  # 存储多个闹钟的列表，每个闹钟是一个字典
        self.alarm_thread = None
        self.stop_event = threading.Event()
        self.current_alarm_label = ""
        self.use_24h_format = True
        self.snooze_time = 1  # 默认贪睡1分钟
        self.is_ringing = False
        self.ringing_window = None
        self.player_process = None
        self._music_playing = False  # 标记本地音乐是否正在播放
        self.lock = threading.RLock()  # 用于线程安全操作的锁
        self.preview_thread = None
        self.is_previewing = False
        self.player_process = None  # 播放器进程引用
        # 为兼容旧代码添加初始化
        self.alarm_set = False  # 闹钟是否设置
        self.alarm_time = None  # 闹钟时间
        self.alarm_label = ""  # 闹钟标签
        logging.info("初始化变量完成，闹钟列表已创建")
        
        # 记录日志
        logging.info("闹钟应用启动")
        # 重置事件
        self.stop_event.clear()
        
        # 进程跟踪和监控相关变量
        self._last_launched_player_pid = None
        self._last_media_launch_time = None
        self._launched_media_files = []
        self._player_process_history = []  # 保存启动的播放器进程历史
        self._max_process_history = 5  # 最大保存的进程历史数量
        logging.info("进程跟踪变量初始化完成")
        
        # 创建界面布局
        self.create_widgets()
        logging.info("UI组件创建完成")
        
        # 启动实时时间更新
        self.update_clock()
        logging.info("时钟更新线程启动")
        
        # 设置窗口关闭时的处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        print("[DEBUG] 开始创建UI组件...")
        
        # 标题
        print("[DEBUG] 创建标题组件...")
        title_frame = ttk.Frame(self.root, padding=10)
        title_frame.pack(fill="x", pady=(10, 2))
        
        title_label = ttk.Label(title_frame, text="闹钟应用", font=self.font_config["title"])
        title_label.pack()
        print("[DEBUG] 标题组件创建完成")
        
        # 实时时间显示
        print("[DEBUG] 创建时钟显示组件...")
        clock_frame = ttk.LabelFrame(self.root, text="当前时间", padding=10)
        clock_frame.pack(pady=(8, 2), padx=20, fill="x")
        
        # 日期显示
        self.date_label = ttk.Label(clock_frame, text="", font=self.font_config["label"])
        self.date_label.pack(pady=3)
        
        # 时间显示
        self.clock_label = ttk.Label(clock_frame, text="", font=self.font_config["clock"])
        self.clock_label.pack(pady=5)
        print("[DEBUG] 时钟显示组件创建完成")
        
        # 倒计时显示
        print("[DEBUG] 创建倒计时显示组件...")
        countdown_frame = ttk.LabelFrame(self.root, text="距离下次闹钟", padding=10)
        countdown_frame.pack(pady=(8, 2), padx=20, fill="x")
        
        
        self.countdown_label = ttk.Label(countdown_frame, text="无设置的闹钟", font=self.font_config["label"])
        self.countdown_label.pack(pady=5)
        print("[DEBUG] 倒计时显示组件创建完成")
        
        # 闹钟列表框架
        print("[DEBUG] 创建闹钟列表框架...")
        list_frame = ttk.LabelFrame(self.root, text="设置的闹钟列表", padding=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(8, 2))
        
        # 列表操作按钮
        list_actions_frame = ttk.Frame(list_frame)
        list_actions_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Button(list_actions_frame, text="按时间排序", command=self.sort_alarms_by_time).pack(side="left", padx=5)
        ttk.Button(list_actions_frame, text="按标签排序", command=self.sort_alarms_by_label).pack(side="left", padx=5)
        
        # 创建Treeview来显示闹钟列表
        print("[DEBUG] 创建Treeview组件...")
        columns = ("id", "time", "label", "snooze", "actions")
        self.alarm_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=6)
        
        # 设置列标题和排序
        self.alarm_tree.heading("id", text="ID")
        self.alarm_tree.heading("time", text="时间", command=self.sort_alarms_by_time)
        self.alarm_tree.heading("label", text="标签", command=self.sort_alarms_by_label)
        self.alarm_tree.heading("snooze", text="贪睡(分钟)")
        self.alarm_tree.heading("actions", text="操作")
        
        # 设置列宽
        self.alarm_tree.column("id", width=50, anchor="center")
        self.alarm_tree.column("time", width=100, anchor="center")
        self.alarm_tree.column("label", width=220, anchor="w")
        self.alarm_tree.column("snooze", width=100, anchor="center")
        self.alarm_tree.column("actions", width=150, anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscroll=scrollbar.set)
        
        # 布局Treeview和滚动条
        self.alarm_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        print("[DEBUG] 闹钟列表组件创建完成")
        
        # 时间格式切换
        format_frame = ttk.Frame(self.root)
        format_frame.pack(fill="x", padx=50, pady=5)
        
        self.format_var = tk.BooleanVar(value=True)
        format_check = ttk.Checkbutton(format_frame, text="使用24小时制", variable=self.format_var, 
                                      command=self.toggle_time_format)
        format_check.pack(anchor="w")
        
        # 闹钟时间设置
        setting_frame = ttk.LabelFrame(self.root, text="设置闹钟时间", padding=10)
        setting_frame.pack(fill="x", padx=20, pady=(8, 2))
        
        # 小时选择
        hour_frame = ttk.Frame(setting_frame)
        hour_frame.pack(side="left", padx=10, pady=10)
        
        ttk.Label(hour_frame, text="小时:", font=self.font_config["label"]).pack()
        self.hour_var = tk.StringVar()
        self.hour_combo = ttk.Combobox(hour_frame, textvariable=self.hour_var, width=5, font=self.font_config["label"])
        self.update_hour_values()
        self.hour_combo.current(datetime.datetime.now().hour if self.use_24h_format else 
                              (datetime.datetime.now().hour % 12 if datetime.datetime.now().hour % 12 != 0 else 12))
        self.hour_combo.pack()
        
        # 分钟选择
        minute_frame = ttk.Frame(setting_frame)
        minute_frame.pack(side="left", padx=10, pady=10)
        
        ttk.Label(minute_frame, text="分钟:", font=self.font_config["label"]).pack()
        self.minute_var = tk.StringVar()
        minute_combo = ttk.Combobox(minute_frame, textvariable=self.minute_var, width=5, font=self.font_config["label"])
        minute_combo['values'] = [f"{i:02d}" for i in range(60)]
        minute_combo.current(datetime.datetime.now().minute)
        minute_combo.pack()
        
        # AM/PM选择
        self.ampm_frame = ttk.Frame(setting_frame)
        self.ampm_frame.pack(side="left", padx=10, pady=10)
        
        ttk.Label(self.ampm_frame, text="时段:", font=self.font_config["label"]).pack()
        self.ampm_var = tk.StringVar(value="AM")
        self.ampm_combo = ttk.Combobox(self.ampm_frame, textvariable=self.ampm_var, width=5, font=self.font_config["label"])
        self.ampm_combo['values'] = ["AM", "PM"]
        self.ampm_combo.current(0 if datetime.datetime.now().hour < 12 else 1)
        self.ampm_combo.pack()
        
        # 闹钟标签设置
        label_frame = ttk.LabelFrame(self.root, text="闹钟标签", padding=10)
        label_frame.pack(fill="x", padx=20, pady=(8, 2))
        
        ttk.Label(label_frame, text="标签:", font=self.font_config["label"]).pack(side="left", padx=10)
        self.label_entry = ttk.Entry(label_frame, width=30, font=self.font_config["label"])
        self.label_entry.pack(side="left", padx=10, fill="x", expand=True)
        self.label_entry.insert(0, "")  # 默认空标签
        
        # 贪睡设置
        snooze_frame = ttk.LabelFrame(self.root, text="贪睡设置", padding=10)
        snooze_frame.pack(fill="x", padx=20, pady=(8, 2))
        
        ttk.Label(snooze_frame, text="贪睡时间:", font=self.font_config["label"]).pack(side="left", padx=10)
        self.snooze_var = tk.IntVar(value=5)
        snooze_spin = ttk.Spinbox(snooze_frame, from_=1, to=60, increment=1, textvariable=self.snooze_var, width=5)
        snooze_spin.pack(side="left", padx=5)
        ttk.Label(snooze_frame, text="分钟", font=self.font_config["label"]).pack(side="left", padx=5)
        
        # 铃声选择
        ringtone_frame = ttk.LabelFrame(self.root, text="铃声设置", padding=10)
        ringtone_frame.pack(fill="x", padx=20, pady=(8, 2))
        
        # 定义铃声类型选项
        self.ringtone_var = tk.StringVar(value="默认铃声")
        ttk.Label(ringtone_frame, text="选择铃声:", font=self.font_config["label"]).pack(side="left", padx=10)
        self.ringtone_combo = ttk.Combobox(ringtone_frame, textvariable=self.ringtone_var, width=15, state="normal")
        self.ringtone_combo['values'] = ["默认铃声", "蜂鸣提醒", "系统提示音", "轻柔铃声", "本地音乐"]
        self.ringtone_combo.current(0)
        self.ringtone_combo.pack(side="left", padx=5)
        
        # 添加浏览本地音乐按钮
        self.browse_button = ttk.Button(ringtone_frame, text="浏览...", command=self.browse_local_music, state="disabled")
        self.browse_button.pack(side="left", padx=5)
        
        # 显示选择的本地音乐文件名
        self.music_file_label = ttk.Label(ringtone_frame, text="", font=self.font_config["label"])
        self.music_file_label.pack(side="left", padx=5, fill="x", expand=True)
        
        # 绑定铃声选择变化事件
        self.ringtone_var.trace_add("write", self.on_ringtone_change)
        
        # 预览按钮
        ttk.Button(ringtone_frame, text="预览", command=self.preview_ringtone).pack(side="left", padx=10)
        
        # 内置闹钟设置
        builtin_alarm_frame = ttk.LabelFrame(self.root, text="内置闹钟预设", padding=10)
        builtin_alarm_frame.pack(fill="x", padx=20, pady=(8, 2))
        
        # 内置闹钟类型选项
        builtin_alarm_label = ttk.Label(builtin_alarm_frame, text="选择内置闹钟:", font=self.font_config["label"])
        builtin_alarm_label.pack(side="left", padx=10)
        
        self.builtin_alarm_var = tk.StringVar(value="")
        self.builtin_alarm_combo = ttk.Combobox(builtin_alarm_frame, textvariable=self.builtin_alarm_var, width=20, state="readonly")
        self.builtin_alarm_combo['values'] = ["", "工作日起床闹钟", "周末起床闹钟", "午餐提醒", "下午茶提醒", "晚餐提醒", "睡前提醒"]
        self.builtin_alarm_combo.current(0)
        self.builtin_alarm_combo.pack(side="left", padx=5)
        
        # 快速设置内置闹钟按钮
        self.quick_set_button = ttk.Button(builtin_alarm_frame, text="快速设置", command=self.quick_set_builtin_alarm)
        self.quick_set_button.pack(side="left", padx=10)
        
        # 按钮区域
        print("[DEBUG] 创建按钮区域...")
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=15, fill="x")
        # 居中按钮
        button_center_frame = ttk.Frame(button_frame)
        button_center_frame.pack(anchor="center")
        
        self.set_button = ttk.Button(button_center_frame, text="设置闹钟", command=self.set_alarm, width=15)
        self.set_button.pack(side="left", padx=10)
        
        self.stop_button = ttk.Button(button_center_frame, text="取消闹钟", command=self.stop_alarm, width=15, state="disabled")
        self.stop_button.pack(side="left", padx=10)
        print("[DEBUG] 按钮区域创建完成")
        
        # 状态显示
        print("[DEBUG] 创建状态显示...")
        self.status_var = tk.StringVar(value="就绪")
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=50, pady=10)
        
        ttk.Label(status_frame, text="状态:", font=self.font_config["label"]).pack(side="left")
        ttk.Label(status_frame, textvariable=self.status_var, font=self.font_config["label"]).pack(side="left", padx=5)
        print("[DEBUG] UI组件创建完成")
    
    def toggle_time_format(self):
        """切换12小时制和24小时制"""
        self.use_24h_format = self.format_var.get()
        self.update_hour_values()
        
        # 更新AM/PM控件的可见性
        if self.use_24h_format:
            self.ampm_frame.pack_forget()
        else:
            self.ampm_frame.pack(side="left", padx=10, pady=10)
    
    def update_hour_values(self):
        """更新小时下拉框的值"""
        if self.use_24h_format:
            self.hour_combo['values'] = [f"{i:02d}" for i in range(24)]
        else:
            self.hour_combo['values'] = [f"{i:02d}" for i in range(1, 13)]
    
    def on_ringtone_change(self, *args):
        """处理铃声选择变化"""
        selected_ringtone = self.ringtone_var.get()
        # 如果选择了本地音乐，则启用浏览按钮
        if selected_ringtone == "本地音乐":
            self.browse_button.config(state="normal")
        else:
            self.browse_button.config(state="disabled")
            # 清除本地音乐路径
            self.local_music_path = None
            self.music_file_label.config(text="")
    
    def browse_local_music(self):
        """浏览并选择本地音乐文件"""
        # 定义支持的音频文件类型和扩展名
        AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.wma', '.aac', '.mid', '.midi'}
        audio_types = [
            ("音频文件", "*.mp3 *.wav *.ogg *.flac *.m4a *.wma *.aac *.mid *.midi"),
            ("MP3文件", "*.mp3"),
            ("WAV文件", "*.wav"),
            ("所有文件", "*.*")
        ]
        
        try:
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title="选择本地音乐文件",
                filetypes=audio_types,
                defaultextension=".mp3"
            )
            
            if file_path:
                # 基本文件存在性和可读性检查
                if not os.path.isfile(file_path):
                    messagebox.showerror("错误", "文件不存在，请选择有效音频文件")
                    return
                
                if not os.access(file_path, os.R_OK):
                    messagebox.showerror("错误", "无法读取文件，请检查文件权限")
                    return
                
                # 检查文件扩展名
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in AUDIO_EXTENSIONS:
                    response = messagebox.askyesno(
                        "警告", 
                        f"所选文件格式({file_ext})可能不受支持，是否继续使用？"
                    )
                    if not response:
                        return
                
                # 检查文件大小（限制为50MB）
                max_size = 50 * 1024 * 1024  # 50MB
                file_size = os.path.getsize(file_path)
                if file_size > max_size:
                    response = messagebox.askyesno(
                        "警告", 
                        f"所选文件大小({self.format_size(file_size)})超过推荐大小(50MB)，可能导致播放延迟，是否继续使用？"
                    )
                    if not response:
                        return
                
                # 通过所有验证，设置文件路径
                self.local_music_path = file_path
                file_name = os.path.basename(file_path)
                self.music_file_label.config(text=file_name)
                logging.info(f"已选择本地音乐文件: {file_name} ({self.format_size(file_size)})")
                
                # 提示用户
                # 总是显示成功消息，不显示playsound未安装的提示（因为库已安装）
                messagebox.showinfo("成功", f"已选择音乐文件：{file_name}\n点击预览按钮可试听")
                    
        except PermissionError:
            logging.warning("没有权限访问所选文件")
            messagebox.showerror("权限错误", "没有权限访问所选文件，请选择其他文件")
        except FileNotFoundError:
            logging.warning("找不到所选文件")
            messagebox.showerror("文件错误", "找不到所选文件")
        except Exception as e:
            logging.error(f"浏览本地音乐时出错: {e}")
            messagebox.showerror("错误", f"选择文件时出错: {str(e)}")
    
    def format_size(self, size_bytes):
        """格式化文件大小为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} GB"
    
    def preview_ringtone(self):
        """预览选择的铃声"""
        # 如果正在预览，先停止
        if self.is_previewing:
            self.is_previewing = False
            return
        
        try:
            selected_ringtone = self.ringtone_var.get()
            
            # 设置预览状态
            self.is_previewing = True
            
            # 在单独线程中播放铃声预览
            def preview_thread_func():
                try:
                    if selected_ringtone == "本地音乐":
                        # 检查本地音乐路径是否存在
                        if not self.local_music_path:
                            error_msg = "请先浏览并选择本地音乐文件"
                            print(f"预览铃声错误: {error_msg}")
                            logging.error(f"预览铃声错误: {error_msg}")
                            # 在主线程中显示错误消息
                            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
                            return
                            
                        # 检查文件是否存在
                        if not os.path.isfile(self.local_music_path):
                            error_msg = f"选择的音乐文件不存在: {self.local_music_path}"
                            print(f"预览铃声错误: {error_msg}")
                            logging.error(f"预览铃声错误: {error_msg}")
                            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
                            return
                            
                        # 预览本地音乐
                        logging.info(f"正在预览本地音乐: {self.local_music_path}")
                        # 优先使用系统播放器，因为测试表明它在Windows上处理中文路径更可靠
                        logging.info("优先使用系统播放器播放音频")
                        system_play_success = self.try_alternative_play(self.local_music_path)
                        
                        # 如果系统播放器失败，并且playsound可用，再尝试使用playsound
                        if not system_play_success and playsound_available and playsound_func is not None:
                            try:
                                logging.info("系统播放器失败，尝试使用playsound")
                                safe_playsound(self.local_music_path)
                            except Exception as e:
                                detailed_error = f"使用playsound播放失败: {str(e)}"
                                print(f"预览铃声时出错: {detailed_error}")
                                logging.error(f"预览铃声时出错: {detailed_error}")
                    else:
                        # 预览默认铃声
                        frequency, duration = self.RINGTONE_TYPES.get(selected_ringtone, (1000, 800))
                        logging.info(f"正在预览铃声: {selected_ringtone} (频率: {frequency}Hz)")
                        # 播放预览铃声（短版本）
                        for _ in range(2):  # 播放两次
                            if not self.is_previewing:
                                break
                            try:
                                winsound.Beep(frequency, duration)
                                time.sleep(0.2)  # 短暂间隔
                            except Exception as e:
                                error_msg = f"播放铃声蜂鸣音失败: {str(e)}"
                                print(error_msg)
                                logging.error(error_msg)
                                self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
                                break
                except Exception as e:
                    error_details = f"预览铃声时出错: {str(e)}"
                    print(error_details)
                    logging.error(error_details)
                    # 获取完整的异常堆栈信息以帮助调试
                    stack_trace = traceback.format_exc()
                    logging.error(f"预览铃声异常堆栈: {stack_trace}")
                    self.root.after(0, lambda: messagebox.showerror("错误", error_details))
                finally:
                    self.is_previewing = False
            
            # 启动预览线程
            self.preview_thread = threading.Thread(target=preview_thread_func)
            self.preview_thread.daemon = True
            self.preview_thread.start()
            
        except Exception as e:
            error_details = f"启动铃声预览失败: {str(e)}"
            print(error_details)
            logging.error(error_details)
            stack_trace = traceback.format_exc()
            logging.error(f"启动预览线程异常堆栈: {stack_trace}")
            messagebox.showerror("错误", error_details)
            self.is_previewing = False
    
    def _check_if_program_exists(self, program_name):
        """检查程序是否存在于系统PATH中"""
        try:
            # 在Windows上，检查可执行文件是否存在于PATH中
            import subprocess
            # 使用where命令查找程序
            result = subprocess.run(
                ['where', program_name],
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[DEBUG] 检查程序 {program_name} 是否存在时出错: {e}")
            return False
    
    def _terminate_recent_media_players(self, force=False):
        """终止最近启动的媒体播放器进程，增强版支持进程跟踪和监控，优化版"""
        try:
            import subprocess, time, os
            print(f"[DEBUG] 尝试终止最近启动的媒体播放器, 强制模式: {force}")
            
            # 定义终止进程的辅助函数，避免代码重复
            def terminate_process_by_pid(pid, process_info=""):
                try:
                    # 使用taskkill命令终止进程，添加/T参数终止整个进程树
                    command = ['taskkill', '/PID', str(pid), '/T']
                    if force:
                        command.append('/F')  # 强制终止
                    
                    print(f"[DEBUG] 尝试终止进程 {process_info}PID={pid}")
                    result = subprocess.run(
                        command,
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=3  # 设置超时以避免卡住
                    )
                    
                    success = result.returncode == 0
                    if success:
                        print(f"[DEBUG] ✓ 成功终止进程 {process_info}PID={pid}")
                    else:
                        print(f"[DEBUG] 终止进程 {process_info}PID={pid} 失败: {result.stderr}")
                    return success
                except subprocess.TimeoutExpired:
                    print(f"[DEBUG] 终止进程 {process_info}PID={pid} 超时")
                    return False
                except Exception as e:
                    print(f"[DEBUG] 终止进程 {process_info}PID={pid} 时出错: {e}")
                    return False
            
            # 获取当前锁以确保线程安全
            lock_acquired = False
            try:
                if hasattr(self, 'lock'):
                    self.lock.acquire()
                    lock_acquired = True
            except Exception:
                pass
            
            try:
                # 终止计数器
                total_terminated = 0
                
                # 1. 优先处理进程历史记录中的所有进程
                if hasattr(self, '_player_process_history') and self._player_process_history:
                    print(f"[DEBUG] 处理进程历史记录，共有 {len(self._player_process_history)} 个进程")
                    # 逆序遍历，优先终止最新的进程
                    for i in range(len(self._player_process_history) - 1, -1, -1):
                        proc_info = self._player_process_history[i]
                        pid = proc_info.get('pid')
                        proc_type = proc_info.get('type', 'unknown')
                        file_path = proc_info.get('file_path', 'unknown')
                        
                        process_info = f"[类型={proc_type}, 文件={file_path}] "
                        if terminate_process_by_pid(pid, process_info):
                            total_terminated += 1
                        
                        # 无论成功与否，都从历史记录中移除
                        try:
                            del self._player_process_history[i]
                        except:
                            pass
                
                # 2. 如果有保存的播放器PID，直接终止
                if hasattr(self, '_last_launched_player_pid') and self._last_launched_player_pid:
                    if terminate_process_by_pid(self._last_launched_player_pid, "[保存的播放器] "):
                        total_terminated += 1
                    self._last_launched_player_pid = None  # 无论成功与否都重置
                
                # 3. 根据启动时间终止最近创建的媒体播放器进程
                if hasattr(self, '_last_media_launch_time') and self._last_media_launch_time:
                    # 扩展的媒体播放器进程名列表，按使用频率排序
                    media_players = [
                        'wmplayer.exe', 'Music.UI.exe', 'vlc.exe', 'potplayer.exe', 
                        'foobar2000.exe', 'itunes.exe', 'mplayer.exe', 'winamp.exe',
                        'spotify.exe', 'deezer.exe', 'aimp.exe', 'audacious.exe',
                        'groove.exe', 'msedgewebview2.exe', 'mplayer2.exe',
                        'GrooveMusic.exe', 'audacity.exe', 'mediaplayer.exe',
                        'chrome.exe', 'firefox.exe', 'opera.exe', 'safari.exe'  # 添加浏览器可能播放音频
                    ]
                    
                    # 统计终止成功的进程数
                    players_terminated = 0
                    
                    for player in media_players:
                        try:
                            # 使用tasklist查找进程信息
                            result = subprocess.run(
                                ['tasklist', '/FI', f'IMAGENAME eq {player}', '/FO', 'CSV'],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=1.5  # 略微降低超时
                            )
                            
                            if result.returncode == 0 and result.stdout.strip():
                                # 解析CSV输出
                                lines = result.stdout.strip().split('\n')
                                for line in lines[1:]:  # 跳过标题行
                                    try:
                                        # 尝试解析行，提取PID
                                        import csv
                                        reader = csv.reader([line])
                                        row = next(reader)
                                        if len(row) >= 2:
                                            pid = row[1]
                                            print(f"[DEBUG] 发现运行中的播放器进程: {player} (PID: {pid})")
                                            
                                            if terminate_process_by_pid(pid, f"[{player}] "):
                                                players_terminated += 1
                                                total_terminated += 1
                                    except Exception as parse_error:
                                        print(f"[DEBUG] 解析进程信息时出错: {parse_error}")
                        except Exception as e:
                            print(f"[DEBUG] 查找和终止 {player} 时出错: {e}")
                    
                    if players_terminated > 0:
                        print(f"[DEBUG] 成功终止了 {players_terminated} 个媒体播放器进程")
                
                # 4. 如果有记录的媒体文件路径，尝试终止与这些文件相关的进程
                if hasattr(self, '_launched_media_files') and self._launched_media_files:
                    print(f"[DEBUG] 尝试终止与最近播放文件相关的进程")
                    recent_files = list(set(self._launched_media_files))  # 去重
                    file_processes_terminated = 0
                    
                    for file_path in recent_files:
                        if not file_path or not os.path.exists(file_path):
                            continue
                            
                        filename = os.path.basename(file_path)
                        print(f"[DEBUG] 检查与文件 {filename} 相关的进程")
                        
                        try:
                            # 使用wmic通过命令行参数查找与文件相关的进程
                            cmd = f'wmic process where "CommandLine like \"%{filename}%\"" get ProcessId,Name'
                            result = subprocess.run(
                                ['powershell.exe', '-Command', cmd],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                timeout=2.0
                            )
                            
                            # 解析输出
                            lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                            for line in lines:
                                line_parts = line.strip().split()
                                if line_parts and line_parts[0].isdigit():
                                    pid = line_parts[0]
                                    proc_name = ' '.join(line_parts[1:]) if len(line_parts) > 1 else 'unknown'
                                    
                                    if terminate_process_by_pid(pid, f"[{proc_name}, 文件={filename}] "):
                                        file_processes_terminated += 1
                                        total_terminated += 1
                        except Exception as file_error:
                            print(f"[DEBUG] 处理文件 {file_path} 时出错: {file_error}")
                    
                    if file_processes_terminated > 0:
                        print(f"[DEBUG] 成功终止了 {file_processes_terminated} 个与媒体文件相关的进程")
                    
                    # 清空已处理的文件列表
                    self._launched_media_files.clear()
                
                # 5. 强制模式下，使用通配符终止所有可能的音频播放相关进程
                if force:
                    print("[DEBUG] 强制模式: 尝试终止所有音频播放相关进程")
                    wildcard_terminated = 0
                    
                    try:
                        # 优化的通配符终止策略
                        wildcard_patterns = ['*player*', '*music*', '*media*', '*sound*', '*audio*']
                        
                        # 执行通配符查找
                        for pattern in wildcard_patterns:
                            try:
                                # 使用PowerShell查找匹配的进程
                                ps_command = f"Get-Process | Where-Object {{ $_.ProcessName -like '{pattern}' }} | Select-Object -ExpandProperty Id"
                                result = subprocess.run(
                                    ['powershell.exe', '-Command', ps_command],
                                    shell=False,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    timeout=2
                                )
                                
                                # 解析PID列表
                                pids = []
                                for line in result.stdout.strip().split('\n'):
                                    if line.strip().isdigit():
                                        pids.append(line.strip())
                                
                                # 终止找到的进程
                                for pid in pids:
                                    try:
                                        # 强制终止进程树
                                        subprocess.run(
                                            ['taskkill', '/PID', pid, '/T', '/F'],
                                            shell=False,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            timeout=1
                                        )
                                        print(f"[DEBUG] ✓ 强制终止通配符匹配的进程 PID: {pid}")
                                        wildcard_terminated += 1
                                        total_terminated += 1
                                    except Exception:
                                        pass
                            except Exception as pattern_error:
                                print(f"[DEBUG] 通配符查找 {pattern} 时出错: {pattern_error}")
                    except Exception as e:
                        print(f"[DEBUG] 执行兜底终止逻辑时出错: {e}")
                    
                    if wildcard_terminated > 0:
                        print(f"[DEBUG] 强制模式下成功终止了 {wildcard_terminated} 个通配符匹配的进程")
                    
                    # 最后尝试终止所有可能的媒体播放器（作为兜底方案）
                    print("[DEBUG] 强制模式: 尝试终止所有常见媒体播放器")
                    common_players = ['wmplayer.exe', 'Music.UI.exe', 'vlc.exe', 'potplayer.exe', 'foobar2000.exe', 'mplayer.exe', 'itunes.exe']
                    
                    for player in common_players:
                        try:
                            subprocess.run(
                                ['taskkill', '/IM', player, '/F'],
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE
                            )
                            print(f"[DEBUG] 已尝试强制终止 {player}")
                        except Exception as e:
                            print(f"[DEBUG] 强制终止 {player} 时出错: {e}")
                
                # 6. 清理所有相关状态
                # 重置音乐播放状态
                if hasattr(self, '_music_playing'):
                    self._music_playing = False
                    print("[DEBUG] 已重置音乐播放标志")
                
                # 重置媒体启动时间
                if hasattr(self, '_last_media_launch_time'):
                    self._last_media_launch_time = None
                
                print(f"[DEBUG] 媒体播放器终止操作完成，总共终止了 {total_terminated} 个进程")
                
                # 返回是否成功终止了任何进程
                return total_terminated > 0
                
            finally:
                # 确保释放锁
                if lock_acquired and hasattr(self, 'lock'):
                    try:
                        self.lock.release()
                    except Exception:
                        pass
        
        except Exception as e:
            print(f"[ERROR] 终止媒体播放器时发生错误: {e}")
            logging.error(f"终止媒体播放器时发生错误: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def try_alternative_play(self, file_path):
        """尝试使用系统默认播放器播放音频文件，增强Windows路径处理和异常处理，优先返回可控制的进程引用"""
        try:
            # 确保路径是字符串并规范化
            file_path = str(file_path)
            print(f"[DEBUG] 尝试使用系统播放器播放: {file_path}")
            logging.info(f"尝试使用系统默认播放器播放: {file_path}")
            
            # 确保路径存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                print(f"[ERROR] {error_msg}")
                raise FileNotFoundError(error_msg)
            
            # 规范化路径
            norm_path = os.path.normpath(file_path)
            print(f"[DEBUG] 规范化路径: {norm_path}")
            
            if os.name == 'nt':  # Windows系统
                import subprocess, ctypes
                
                # 优先使用直接创建子进程的方式，以便后续可以控制和终止
                # 方案1: 使用subprocess直接启动常见媒体播放器
                common_players = [
                    # 尝试使用Windows Media Player
                    ('wmplayer.exe', f'/play /close "{norm_path}"'),
                    # 尝试使用Groove Music
                    ('Music.UI.exe', f'"{norm_path}"'),
                ]
                
                for player_name, args in common_players:
                    try:
                        # 检查播放器是否存在
                        if self._check_if_program_exists(player_name):
                            # 构建命令
                            command = [player_name] + args.split() if ' ' in args else [player_name, args]
                            print(f"[DEBUG] 尝试直接启动播放器: {player_name} {args}")
                            
                            # 不使用shell=True以获得更好的进程控制
                            process = subprocess.Popen(
                                command,
                                shell=False,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                close_fds=True
                            )
                            print(f"[DEBUG] ✓ 成功启动播放器 {player_name}")
                            return process
                    except Exception as player_error:
                        print(f"[DEBUG] 启动{player_name}失败: {player_error}")
                
                # 方案2: 使用PowerShell，但配置为可控制的方式
                try:
                    # 使用PowerShell启动并获取进程信息
                    ps_command = f'$proc = Start-Process -FilePath "{norm_path}" -PassThru; Start-Sleep -Milliseconds 100; $proc.Id'
                    process = subprocess.Popen(
                        ['powershell.exe', '-Command', ps_command],
                        shell=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # 等待进程ID输出
                    stdout, stderr = process.communicate(timeout=2)
                    if stdout.strip() and process.returncode == 0:
                        # 保存PowerShell进程和启动的媒体播放器PID
                        player_pid = int(stdout.strip())
                        print(f"[DEBUG] ✓ PowerShell启动成功，播放器PID: {player_pid}")
                        # 保存播放器PID以便后续终止
                        if hasattr(self, '_last_launched_player_pid'):
                            self._last_launched_player_pid = player_pid
                        else:
                            self._last_launched_player_pid = player_pid
                        return process
                except Exception as ps_error:
                    print(f"[DEBUG] PowerShell方案失败: {ps_error}")
                
                # 方案3: 使用cmd.exe但带上/P参数以返回进程ID
                try:
                    process = subprocess.Popen(
                        ['cmd.exe', '/c', f'start "" /WAIT "{norm_path}"'],
                        shell=False
                    )
                    print("[DEBUG] ✓ cmd.exe启动成功")
                    return process
                except Exception as cmd_error:
                    print(f"[DEBUG] cmd.exe方案失败: {cmd_error}")
                
                # 最后才尝试无法直接控制的方式
                # 记录当前时间，以便后续通过进程创建时间识别
                self._last_media_launch_time = time.time()
                
                # 方案4: ShellExecuteW
                try:
                    result = ctypes.windll.shell32.ShellExecuteW(
                        None,
                        "open",
                        norm_path,
                        None,
                        None,
                        1  # SW_SHOWNORMAL
                    )
                    if result > 32:  # ShellExecuteW成功返回值大于32
                        print("[DEBUG] ✓ ShellExecuteW启动成功")
                        # 创建一个伪进程对象用于跟踪
                        class PseudoProcess:
                            def __init__(self, parent):
                                self.parent = parent
                                self.returncode = None
                            
                            def poll(self):
                                # 这个进程无法直接轮询状态
                                return None
                            
                            def terminate(self):
                                # 使用备用方式终止
                                self.parent._terminate_recent_media_players()
                                return 0
                            
                            def kill(self):
                                # 强制终止
                                self.parent._terminate_recent_media_players(force=True)
                                return 0
                        
                        return PseudoProcess(self)
                except Exception as shell_error:
                    print(f"[DEBUG] ShellExecuteW方案失败: {shell_error}")
                
                # 方案5: os.startfile
                try:
                    os.startfile(norm_path)
                    print("[DEBUG] ✓ os.startfile启动成功")
                    # 返回相同的伪进程对象
                    class PseudoProcess:
                        def __init__(self, parent):
                            self.parent = parent
                            self.returncode = None
                        
                        def poll(self):
                            return None
                        
                        def terminate(self):
                            self.parent._terminate_recent_media_players()
                            return 0
                        
                        def kill(self):
                            self.parent._terminate_recent_media_players(force=True)
                            return 0
                    
                    return PseudoProcess(self)
                except Exception as startfile_error:
                    print(f"[DEBUG] os.startfile方案失败: {startfile_error}")
                    raise
            else:
                # 非Windows系统的备用方案
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                process = subprocess.Popen([opener, file_path])
                return process
                
        except Exception as e:
            error_msg = f"播放失败: {str(e)}"
            print(f"[ERROR] {error_msg}")
            logging.error(error_msg)
            raise
            
        except Exception as e:
            detailed_error = f"使用系统播放器播放失败: {str(e)}"
            print(detailed_error)
            logging.error(detailed_error)
            # 在主线程中显示错误消息
            self.root.after(0, lambda: messagebox.showerror("错误", detailed_error))
    
    def update_clock(self):
        """更新实时时间显示和倒计时"""
        try:
            now = datetime.datetime.now()
            
            # 更新日期显示
            date_str = now.strftime("%Y年%m月%d日 %A")
            # 中文星期转换
            weekdays = {"Monday":"星期一", "Tuesday":"星期二", "Wednesday":"星期三", 
                        "Thursday":"星期四", "Friday":"星期五", "Saturday":"星期六", "Sunday":"星期日"}
            for en, zh in weekdays.items():
                date_str = date_str.replace(en, zh)
            self.date_label.config(text=date_str)
            
            # 更新时间显示
            if self.use_24h_format:
                current_time = now.strftime("%H:%M:%S")
            else:
                current_time = now.strftime("%I:%M:%S %p")
            self.clock_label.config(text=current_time)
            
            # 更新倒计时显示
            with self.lock:
                if self.alarms:  # 检查是否有设置的闹钟
                    try:
                        # 找到下一个要触发的闹钟
                        now_time = now.time()
                        next_alarm = None
                        next_alarm_label = ""
                        next_alarm_delay = float('inf')
                        
                        for alarm in self.alarms:
                            alarm_time = alarm['time']
                            # 计算与当前时间的差异
                            diff = (alarm_time.hour - now_time.hour) * 3600 + \
                                   (alarm_time.minute - now_time.minute) * 60 + \
                                   (alarm_time.second - now_time.second)
                            
                            # 如果闹钟时间已过，计算明天的时间差
                            if diff <= 0:
                                diff += 24 * 3600
                            
                            # 找到最近的闹钟
                            if diff < next_alarm_delay:
                                next_alarm_delay = diff
                                next_alarm = alarm_time
                                next_alarm_label = alarm.get('label', '')
                        
                        if next_alarm:
                            # 计算具体的天、时、分、秒
                            days = next_alarm_delay // (24 * 3600)
                            remaining = next_alarm_delay % (24 * 3600)
                            hours, remainder = divmod(remaining, 3600)
                            minutes, seconds = divmod(remainder, 60)
                            
                            # 格式化倒计时显示
                            if days > 0:
                                countdown_text = f"{days}天 {hours:02d}小时 {minutes:02d}分钟 {seconds:02d}秒"
                            else:
                                countdown_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                            
                            # 如果闹钟有标签，显示标签
                            if next_alarm_label:
                                display_text = f"{countdown_text} ({next_alarm_label})"
                            else:
                                display_text = countdown_text
                            
                            self.countdown_label.config(text=display_text)
                            
                            # 当倒计时小于30分钟时，改变颜色提醒
                            if next_alarm_delay < 30 * 60:
                                self.countdown_label.config(foreground="red")
                            else:
                                self.countdown_label.config(foreground="black")
                    except Exception as e:
                        logging.error(f"更新倒计时时出错: {e}")
                        self.countdown_label.config(text="计算倒计时时出错", foreground="red")
                else:
                    self.countdown_label.config(text="无设置的闹钟", foreground="black")
            
            # 安排下一次更新
            self.root.after(1000, self.update_clock)
        except Exception as e:
            logging.error(f"更新时钟时发生错误: {e}")
            # 尝试重新启动时钟更新
            try:
                self.root.after(1000, self.update_clock)
            except:
                pass
    
    def set_alarm(self):
        """设置闹钟"""
        try:
            with self.lock:
                # 获取用户输入
                try:
                    hour = int(self.hour_var.get())
                    minute = int(self.minute_var.get())
                    snooze = self.snooze_var.get()
                except (ValueError, tk.TclError) as e:
                    logging.warning(f"无效的时间输入: {e}")
                    messagebox.showerror("输入错误", "请输入有效的数字")
                    return
                
                # 验证贪睡时间范围
                if snooze < 1 or snooze > 60:
                    messagebox.showerror("错误", "贪睡时间必须在1-60分钟之间")
                    return
                
                # 处理12小时制
                if not self.use_24h_format:
                    if self.ampm_var.get() not in ["AM", "PM"]:
                        messagebox.showerror("错误", "请选择有效的时段 (AM/PM)")
                        return
                    
                    if self.ampm_var.get() == "PM" and hour < 12:
                        hour += 12
                    elif self.ampm_var.get() == "AM" and hour == 12:
                        hour = 0
                
                # 验证时间范围
                if not (0 <= hour < 24 and 0 <= minute < 60):
                    messagebox.showerror("错误", "请输入有效的时间")
                    return
                
                # 获取当前日期
                now = datetime.datetime.now()
                # 设置闹钟时间
                alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # 如果设置的时间已过，则设置为明天
                if alarm_time <= now:
                    alarm_time += datetime.timedelta(days=1)
                
                # 获取闹钟标签
                alarm_label = self.label_entry.get().strip()
                
                # 格式化显示时间
                if self.use_24h_format:
                    time_str = alarm_time.strftime("%H:%M")
                else:
                    time_str = alarm_time.strftime("%I:%M %p")
                
                # 创建闹钟对象
                alarm = {
                    'id': self.alarm_id_counter,
                    'time': alarm_time,
                    'label': alarm_label,
                    'snooze': snooze,
                    'ringtone': self.ringtone_var.get(),  # 添加铃声设置
                    'local_music_path': self.local_music_path if self.ringtone_var.get() == "本地音乐" else None,  # 保存本地音乐路径
                    'enabled': True,
                    'created_at': datetime.datetime.now()
                }
                self.alarm_id_counter += 1
                
                # 添加到闹钟列表
                with self.lock:
                    self.alarms.append(alarm)
                    logging.info(f"添加闹钟: ID={alarm['id']}, 时间={time_str}, 标签='{alarm_label or '无'}', 贪睡={snooze}分钟")
                
                # 更新最近设置的闹钟（保持向后兼容）
                self.alarm_time = datetime.time(hour, minute)
                self.alarm_label = alarm_label
                self.snooze_time = snooze
                self.alarm_set = True
                
                # 更新状态
                status_text = f"闹钟已设置: {time_str} ({alarm_label})"
                message_text = f"闹钟已成功添加\n时间: {time_str}\n标签: {alarm_label or '无'}\n贪睡时间: {snooze}分钟\n\n当前已设置 {len(self.alarms)} 个闹钟"
                
                # 更新闹钟列表显示
                self.root.after(0, self.update_alarm_list_display)
                logging.info(f"添加闹钟: ID={alarm['id']}, 时间={time_str}，标签: {alarm_label or '无'}")
                
                # 保持按钮状态（允许添加更多闹钟）
                self.stop_button.config(state="normal")
                
                # 如果没有运行中的闹钟线程，则启动
                if not self.alarm_thread or not self.alarm_thread.is_alive():
                    # 重置停止事件
                    self.stop_event.clear()
                    
                    try:
                        self.alarm_thread = threading.Thread(target=self.alarm_thread_func, daemon=True)
                        self.alarm_thread.start()
                    except Exception as e:
                        logging.error(f"启动闹钟线程失败: {e}")
                        messagebox.showerror("错误", "启动闹钟线程失败，请重试")
                        # 移除失败的闹钟
                        self.alarms.pop()
                        return
                
                messagebox.showinfo("成功", message_text)
        except Exception as e:
            logging.error(f"设置闹钟时发生错误: {e}")
            messagebox.showerror("错误", f"设置闹钟时发生错误: {str(e)}")
    
    def stop_alarm(self, alarm_id=None):
        """停止闹钟 - 可以取消特定闹钟或所有闹钟
        
        Args:
            alarm_id: 要取消的闹钟ID，如果为None则取消所有闹钟
        """
        try:
            with self.lock:
                if alarm_id is None:
                    # 取消所有闹钟
                    if not self.alarms:
                        messagebox.showinfo("闹钟取消", "没有设置任何闹钟")
                        return
                    
                    # 保存取消前的闹钟数量用于日志
                    count = len(self.alarms)
                    
                    # 停止闹钟线程
                    if self.alarm_thread and self.alarm_thread.is_alive():
                        self.stop_event.set()
                        try:
                            self.alarm_thread.join(timeout=1.0)
                        except Exception:
                            logging.error("等待闹钟线程停止时发生错误")
                    
                    # 清空闹钟列表
                    self.alarms.clear()
                    logging.info(f"所有闹钟已取消，共 {count} 个")
                    message_text = f"所有闹钟已成功取消\n共 {count} 个闹钟"
                else:
                    # 取消特定闹钟
                    removed = False
                    removed_time = None
                    removed_label = None
                    for i, alarm in enumerate(self.alarms):
                        if alarm['id'] == alarm_id:
                            removed_time = alarm['time'].strftime("%H:%M")
                            removed_label = alarm['label'] or "无标签"
                            self.alarms.pop(i)
                            removed = True
                            logging.info(f"闹钟已取消: ID={alarm_id}, 时间={removed_time}, 标签={removed_label}")
                            message_text = f"闹钟已成功取消\nID: {alarm_id}\n时间: {removed_time}\n标签: {removed_label}"
                            break
                    
                    if not removed:
                        messagebox.showinfo("闹钟取消", f"未找到ID为 {alarm_id} 的闹钟")
                        return
                    
                    # 如果没有闹钟了，停止线程
                    if not self.alarms and self.alarm_thread and self.alarm_thread.is_alive():
                        self.stop_event.set()
                        try:
                            self.alarm_thread.join(timeout=1.0)
                        except Exception:
                            logging.error("等待闹钟线程停止时发生错误")
                
                # 重置闹钟状态
                self.alarm_set = False
                self.stop_event.set()
                
                # 更新UI
                # 重启闹钟线程以处理剩余的闹钟
                if self.alarm_thread and self.alarm_thread.is_alive():
                    self.stop_event.set()
                    try:
                        self.alarm_thread.join(timeout=1.0)
                    except Exception:
                        logging.error("等待闹钟线程停止时发生错误")
                
                if self.alarms:
                    self.stop_event.clear()
                    self.alarm_thread = threading.Thread(target=self.alarm_thread_func, daemon=True)
                    self.alarm_thread.start()
                
                # 更新闹钟列表显示
                self.root.after(0, self.update_alarm_list_display)
                
                # 如果正在响铃，停止响铃
                if self.is_ringing:
                    self.is_ringing = False
                    if hasattr(self, 'ringing_window') and self.ringing_window:
                        self.ringing_window.destroy()
                        self.ringing_window = None
                
                # 更新按钮状态
                self.set_button.config(state="normal")
                if not self.alarms:
                    self.stop_button.config(state="disabled")
                
                messagebox.showinfo("提示", message_text)
                
        except Exception as e:
            logging.error(f"取消闹钟时发生错误: {str(e)}")
            messagebox.showerror("错误", f"取消闹钟时发生错误: {str(e)}")
    
    def quick_set_builtin_alarm(self):
        """快速设置内置闹钟"""
        try:
            builtin_alarm_type = self.builtin_alarm_var.get()
            if not builtin_alarm_type:
                messagebox.showinfo("提示", "请选择一个内置闹钟类型")
                return
            
            # 获取当前时间
            now = datetime.datetime.now()
            alarm_time = None
            alarm_label = builtin_alarm_type
            snooze = 5  # 默认贪睡5分钟
            
            # 根据内置闹钟类型设置时间
            if builtin_alarm_type == "工作日起床闹钟":
                # 周一至周五的早上7:30
                alarm_time = now.replace(hour=7, minute=30, second=0, microsecond=0)
                # 如果今天是工作日且时间已过，设置为明天
                if now.weekday() < 5 and alarm_time <= now:
                    alarm_time += datetime.timedelta(days=1)
                # 如果今天是周末，设置为下周一
                elif now.weekday() >= 5:
                    days_until_monday = (7 - now.weekday()) % 7 or 7
                    alarm_time += datetime.timedelta(days=days_until_monday)
                    
            elif builtin_alarm_type == "周末起床闹钟":
                # 周六和周日的早上9:00
                alarm_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
                # 如果今天是周末且时间已过，设置为下周日
                if now.weekday() >= 5 and alarm_time <= now:
                    if now.weekday() == 5:  # 周六
                        alarm_time += datetime.timedelta(days=1)
                    else:  # 周日
                        alarm_time += datetime.timedelta(days=6)
                # 如果今天是工作日，设置为这个周六
                elif now.weekday() < 5:
                    days_until_saturday = (5 - now.weekday()) % 7 or 7
                    alarm_time += datetime.timedelta(days=days_until_saturday)
                    
            elif builtin_alarm_type == "午餐提醒":
                # 每天中午12:00
                alarm_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
                if alarm_time <= now:
                    alarm_time += datetime.timedelta(days=1)
                    
            elif builtin_alarm_type == "下午茶提醒":
                # 每天下午15:30
                alarm_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
                if alarm_time <= now:
                    alarm_time += datetime.timedelta(days=1)
                    
            elif builtin_alarm_type == "晚餐提醒":
                # 每天晚上18:30
                alarm_time = now.replace(hour=18, minute=30, second=0, microsecond=0)
                if alarm_time <= now:
                    alarm_time += datetime.timedelta(days=1)
                    
            elif builtin_alarm_type == "睡前提醒":
                # 每天晚上22:30
                alarm_time = now.replace(hour=22, minute=30, second=0, microsecond=0)
                if alarm_time <= now:
                    alarm_time += datetime.timedelta(days=1)
            
            if alarm_time is None:
                messagebox.showerror("错误", "无法设置内置闹钟时间")
                return
            
            # 创建闹钟对象
            with self.lock:
                alarm = {
                    'id': self.alarm_id_counter,
                    'time': alarm_time,
                    'label': alarm_label,
                    'snooze': snooze,
                    'ringtone': self.ringtone_var.get(),
                    'local_music_path': self.local_music_path if self.ringtone_var.get() == "本地音乐" else None,
                    'enabled': True,
                    'created_at': datetime.datetime.now()
                }
                self.alarm_id_counter += 1
                
                # 添加到闹钟列表
                self.alarms.append(alarm)
                
                # 更新最近设置的闹钟（保持向后兼容）
                self.alarm_time = alarm_time.time()
                self.alarm_label = alarm_label
                self.snooze_time = snooze
                self.alarm_set = True
                
                # 格式化显示时间
                if self.use_24h_format:
                    time_str = alarm_time.strftime("%H:%M")
                else:
                    time_str = alarm_time.strftime("%I:%M %p")
                
                # 更新状态
                status_text = f"内置闹钟已设置: {time_str} ({alarm_label})"
                message_text = f"内置闹钟已成功添加\n时间: {time_str}\n标签: {alarm_label}\n贪睡时间: {snooze}分钟\n\n当前已设置 {len(self.alarms)} 个闹钟"
                
                # 更新闹钟列表显示
                self.root.after(0, self.update_alarm_list_display)
                
                # 如果没有运行中的闹钟线程，则启动
                if not self.alarm_thread or not self.alarm_thread.is_alive():
                    # 重置停止事件
                    self.stop_event.clear()
                    
                    try:
                        self.alarm_thread = threading.Thread(target=self.alarm_thread_func, daemon=True)
                        self.alarm_thread.start()
                    except Exception as e:
                        logging.error(f"启动闹钟线程失败: {e}")
                        messagebox.showerror("错误", "启动闹钟线程失败，请重试")
                        # 移除失败的闹钟
                        self.alarms.pop()
                        return
                
                messagebox.showinfo("成功", message_text)
                
                # 重置内置闹钟选择
                self.builtin_alarm_var.set("")
                self.builtin_alarm_combo.current(0)
                
        except Exception as e:
            logging.error(f"快速设置内置闹钟时发生错误: {e}")
            messagebox.showerror("错误", f"快速设置内置闹钟时发生错误: {str(e)}")
    
    def alarm_thread_func(self):
        """闹钟线程函数 - 支持多个闹钟"""
        try:
            logging.info("闹钟线程已启动")
            
            while not self.stop_event.is_set():
                try:
                    now = datetime.datetime.now()
                    triggered_alarms = []
                    
                    with self.lock:
                        # 复制闹钟列表以避免在迭代时修改
                        current_alarms = self.alarms.copy()
                    
                    # 检查哪些闹钟需要触发
                    for alarm in current_alarms:
                        if alarm['enabled'] and now >= alarm['time']:
                            triggered_alarms.append(alarm)
                    
                    # 处理触发的闹钟
                    if triggered_alarms:
                        logging.info(f"发现 {len(triggered_alarms)} 个需要触发的闹钟")
                        
                        for alarm in triggered_alarms:
                            logging.info(f"闹钟触发: ID={alarm['id']}, 时间={alarm['time'].strftime('%H:%M')}, 标签='{alarm['label'] or '无'}'")
                            
                            # 设置当前闹钟信息（保存完整的闹钟信息）
                            self.current_alarm_label = alarm['label']
                            self.snooze_time = alarm['snooze']
                            self.current_alarm_ringtone = alarm['ringtone']
                            # 保存本地音乐路径，即使闹钟被移除也能访问
                            self.current_alarm_local_music = alarm.get('local_music_path', None)
                            
                            # 播放闹钟声音（在主线程中执行GUI相关操作）
                            self.root.after(0, self.play_alarm_sound)
                            
                            # 从列表中移除已触发的闹钟（单次闹钟）
                            with self.lock:
                                for i, a in enumerate(self.alarms):
                                    if a['id'] == alarm['id']:
                                        self.alarms.pop(i)
                                        logging.info(f"已从列表中移除触发的闹钟 ID={alarm['id']}")
                                        break
                            
                            # 更新闹钟列表显示
                            self.root.after(0, self.update_alarm_list_display)
                    
                    # 检查是否需要更新倒计时
                    next_alarm = None
                    with self.lock:
                        # 找到下一个要触发的闹钟
                        enabled_alarms = [a for a in self.alarms if a['enabled']]
                        if enabled_alarms:
                            next_alarm = min(enabled_alarms, key=lambda x: x['time'])
                    
                    if next_alarm:
                        # 更新最近设置的闹钟（保持向后兼容）
                        next_alarm_time = next_alarm['time'].time()
                        with self.lock:
                            self.alarm_time = next_alarm_time
                            self.alarm_label = next_alarm['label']
                            self.alarm_set = True
                    else:
                        # 没有设置的闹钟
                        with self.lock:
                            self.alarm_set = False
                        break  # 没有闹钟了，退出循环
                        
                except Exception as e:
                    logging.error(f"闹钟线程中的错误: {e}")
                
                time.sleep(1)
        except Exception as e:
            logging.error(f"闹钟线程异常: {e}")
        finally:
            logging.info("闹钟线程已退出")
    
    def _sound_play_thread(self):
        """声音播放线程函数，实现进程引用保存和重复调用防护"""
        try:
            # 获取当前闹钟的铃声设置
            ringtone = getattr(self, 'current_alarm_ringtone', '默认铃声')
            print(f"[DEBUG] 开始播放闹钟声音: {ringtone}")
            
            # 确保只有一个播放线程在运行，先停止已存在的播放器进程
            with self.lock:
                # 如果已有播放器进程在运行，先停止它
                if hasattr(self, 'player_process') and self.player_process:
                    try:
                        print("[DEBUG] 发现已有播放器进程在运行，先停止它")
                        self.player_process.terminate()
                        import platform
                        import subprocess
                        if platform.system() == 'Windows':
                            subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.player_process.pid)])
                        self.player_process = None
                    except Exception as proc_error:
                        print(f"[DEBUG] 停止已有播放器进程时出错: {proc_error}")
            
            # 检查是否为本地音乐
            is_local_music = False
            local_music_path = None
            
            # 优先使用保存的当前闹钟本地音乐路径（即使闹钟已被移除）
            if ringtone == "本地音乐":
                local_music_path = getattr(self, 'current_alarm_local_music', None)
                if local_music_path:
                    is_local_music = True
                    print(f"[DEBUG] 使用保存的闹钟本地音乐路径: {local_music_path}")
            
            # 如果没有保存的路径，尝试从alarm列表中找到匹配的闹钟并获取本地音乐路径
            if not is_local_music and ringtone == "本地音乐":
                with self.lock:
                    for alarm in self.alarms:
                        if alarm.get('ringtone') == ringtone and alarm.get('local_music_path'):
                            local_music_path = alarm['local_music_path']
                            is_local_music = True
                            print(f"[DEBUG] 从闹钟列表获取本地音乐路径: {local_music_path}")
                            break
            
            # 最后，如果找不到，尝试使用当前设置的本地音乐路径
            if not is_local_music and ringtone == "本地音乐" and hasattr(self, 'local_music_path') and self.local_music_path:
                is_local_music = True
                local_music_path = self.local_music_path
                print(f"[DEBUG] 使用当前设置的本地音乐路径: {local_music_path}")
            
            # 循环播放声音，直到停止事件被设置或is_ringing为False
            while self.is_ringing and not self.stop_event.is_set():
                # 检查进程是否仍在运行，如果不在运行再创建新进程
                with self.lock:
                    if hasattr(self, 'player_process') and self.player_process:
                        try:
                            # 轮询进程状态，不阻塞
                            if self.player_process.poll() is not None:
                                print("[DEBUG] 播放器进程已结束")
                                self.player_process = None
                        except Exception:
                            self.player_process = None
                
                # 只有在没有播放器进程运行时才创建新进程
                if not getattr(self, 'player_process', None):
                    if is_local_music and local_music_path:
                        # 验证文件是否存在
                        if not os.path.exists(local_music_path):
                            print(f"[ERROR] 音乐文件不存在: {local_music_path}")
                            logging.error(f"音乐文件不存在: {local_music_path}")
                            # 使用默认铃声作为后备
                            frequency, duration = self.RINGTONE_TYPES.get('默认铃声', (1000, 800))
                            winsound.Beep(frequency, duration)
                            time.sleep(0.2)
                            continue
                        
                        # 播放本地音乐
                        try:
                            print(f"[DEBUG] 尝试播放本地音乐: {local_music_path}")
                            
                            norm_path = os.path.normpath(local_music_path)
                            
                            # 优先使用内置播放器（如果pygame可用）
                            if 'global_player' in globals() and global_player and global_player.is_available():
                                print(f"[DEBUG] 使用内置播放器播放: {norm_path}")
                                
                                # 使用内置播放器播放音乐
                                global_player.play(norm_path, loops=-1, volume=1.0)
                                
                                # 等待直到音乐停止或被中断
                                while self.is_ringing and not self.stop_event.is_set():
                                    if not global_player.is_playing():
                                        print("[DEBUG] 内置播放器播放结束，重新开始")
                                        global_player.play(norm_path, loops=-1, volume=1.0)
                                    time.sleep(0.5)
                            else:
                                # 如果内置播放器不可用，回退到系统播放器
                                print(f"[DEBUG] 使用系统播放器播放: {norm_path}")
                                
                                # 使用try_alternative_play函数进行播放并保存进程引用
                                if hasattr(self, 'try_alternative_play'):
                                    # 记录播放开始时间
                                    current_time = time.time()
                                    self._last_media_launch_time = current_time
                                    self._launched_media_files.append(norm_path)
                                    
                                    play_result = self.try_alternative_play(norm_path)
                                    with self.lock:
                                        # 重置音乐播放状态
                                        self.player_process = None
                                        self._music_playing = False
                                        
                                        # 保存进程引用或标记音乐播放状态
                                        if hasattr(play_result, 'poll'):
                                            self.player_process = play_result
                                            # 记录PID
                                            self._last_launched_player_pid = play_result.pid
                                            # 保存到进程历史
                                            process_info = {
                                                'pid': play_result.pid,
                                                'start_time': current_time,
                                                'file_path': norm_path,
                                                'type': 'direct_process'
                                            }
                                            self._player_process_history.append(process_info)
                                            # 限制历史记录大小
                                            if len(self._player_process_history) > self._max_process_history:
                                                self._player_process_history.pop(0)
                                            print(f"[DEBUG] 保存播放器进程PID: {play_result.pid}")
                                        elif isinstance(play_result, dict) and 'pid' in play_result:
                                            # 如果返回的是包含PID信息的字典
                                            self._last_launched_player_pid = play_result['pid']
                                            # 保存到进程历史
                                            process_info = {
                                                'pid': play_result['pid'],
                                                'start_time': current_time,
                                                'file_path': norm_path,
                                                'type': play_result.get('type', 'unknown')
                                            }
                                            self._player_process_history.append(process_info)
                                            # 限制历史记录大小
                                            if len(self._player_process_history) > self._max_process_history:
                                                self._player_process_history.pop(0)
                                            print(f"[DEBUG] 保存播放器进程PID (来自字典): {play_result['pid']}")
                                        elif play_result is not None:
                                            # 如果返回True或其他非None值，设置标志
                                            self._music_playing = True
                                            print("[DEBUG] 设置音乐播放标志")
                                        else:
                                            print("[DEBUG] 播放失败，尝试其他方式")
                                            self.player_process = None
                                    # 对于系统播放器播放，等待音乐播放更长时间
                                    # 这里设置为300秒，足够让大多数音乐片段播放较长时间
                                    time.sleep(300)  # 增加等待时间，让本地音乐能够持续播放
                                else:
                                    # 如果没有try_alternative_play，使用_play_with_system_player
                                    play_result = self._play_with_system_player(norm_path)
                                    with self.lock:
                                        if hasattr(play_result, 'poll'):
                                            self.player_process = play_result
                                        else:
                                            self._music_playing = True
                                            self.player_process = None
                                    time.sleep(300)  # 增加等待时间，让本地音乐能够持续播放
                            
                            # 不再尝试playsound，因为测试表明它在Windows上处理中文路径有问题
                        except Exception as e:
                            print(f"[DEBUG] 播放本地音乐时发生异常: {e}")
                            logging.error(f"播放本地音乐时出错: {e}")
                            
                            # 如果本地音乐播放失败，使用默认铃声作为后备
                            frequency, duration = self.RINGTONE_TYPES.get('默认铃声', (1000, 800))
                            winsound.Beep(frequency, duration)
                            time.sleep(0.2)
                    else:
                        # 播放默认铃声
                        frequency, duration = self.RINGTONE_TYPES.get(ringtone, (1000, 800))
                        winsound.Beep(frequency, duration)
                        if self.is_ringing and not self.stop_event.is_set():
                            time.sleep(0.2)  # 短暂暂停后再次播放
                else:
                    # 如果有播放器进程正在运行，等待一段时间再检查
                    time.sleep(1)
        except Exception as e:
            logging.error(f"播放闹钟声音时出错: {e}")
        finally:
            # 确保播放器进程被清理
            try:
                with self.lock:
                    if hasattr(self, 'player_process') and self.player_process:
                        try:
                            print("[DEBUG] 线程结束时清理播放器进程")
                            self.player_process.terminate()
                            import platform
                            import subprocess
                            if platform.system() == 'Windows':
                                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.player_process.pid)])
                        except Exception as cleanup_error:
                            print(f"[DEBUG] 清理播放器进程时出错: {cleanup_error}")
                        self.player_process = None
                # 确保is_ringing设置为False
                if self.is_ringing:
                    self.is_ringing = False
            except Exception:
                pass
    
    def play_alarm_sound(self):
        """播放闹钟声音（循环播放直到停止）"""
        try:
            # 在锁的保护下设置is_ringing
            with self.lock:
                self.is_ringing = True
                # 确保current_alarm_ringtone有默认值
                if not hasattr(self, 'current_alarm_ringtone'):
                    self.current_alarm_ringtone = '默认铃声'
            
            # 在主线程中创建响铃窗口
            self.create_ringing_window()
            
            # 创建并启动声音播放线程
            sound_thread = threading.Thread(target=self._sound_play_thread, daemon=True)
            sound_thread.start()
            
        except Exception as e:
            logging.error(f"启动闹钟响铃时出错: {e}")
            with self.lock:
                self.is_ringing = False
            messagebox.showerror("错误", "启动闹钟响铃失败")
    
    def create_ringing_window(self):
        """创建闹钟响铃时的窗口"""
        try:
            if self.ringing_window:
                try:
                    self.ringing_window.destroy()
                except:
                    pass
                self.ringing_window = None
            
            self.ringing_window = tk.Toplevel(self.root)
            self.ringing_window.title("闹钟响了！")
            self.ringing_window.geometry("450x350")  # 增大窗口尺寸
            self.ringing_window.minsize(450, 350)  # 设置最小尺寸
            self.ringing_window.configure(bg="#ffcccc")
            self.ringing_window.attributes("-topmost", True)  # 置顶显示
            self.ringing_window.attributes("-alpha", 0.95)  # 稍微透明，更醒目
            
            # 窗口关闭时不执行默认关闭操作
            self.ringing_window.protocol("WM_DELETE_WINDOW", lambda: None)
            
            # 添加窗口震动效果，更醒目
            def shake_window():
                try:
                    if not self.is_ringing or not self.ringing_window:
                        return
                    
                    x, y = self.ringing_window.winfo_x(), self.ringing_window.winfo_y()
                    for _ in range(2):
                        self.ringing_window.geometry(f"+{x+10}+{y}")
                        self.ringing_window.update()
                        time.sleep(0.05)
                        self.ringing_window.geometry(f"+{x-10}+{y}")
                        self.ringing_window.update()
                        time.sleep(0.05)
                    self.ringing_window.geometry(f"+{x}+{y}")
                    
                    if self.is_ringing and self.ringing_window:
                        self.ringing_window.after(500, shake_window)
                except:
                    pass
            
            # 启动震动效果
            shake_window()
            
            # 创建内容框架
            ring_content_frame = ttk.Frame(self.ringing_window, padding=15)
            ring_content_frame.pack(fill="both", expand=True)
            ring_content_frame.configure(borderwidth=0)
            
            # 显示闹钟信息
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            info_text = f"闹钟时间到！\n当前时间: {current_time}"
            info_label = ttk.Label(ring_content_frame, text=info_text, font=("SimHei", 16, "bold"), justify="center")
            info_label.pack(pady=15)
            
            # 闹钟标签显示
            if self.alarm_label:
                label_label = ttk.Label(ring_content_frame, text="标签:", font=("SimHei", 12))
                label_label.pack(anchor="center", pady=3)
                
                alarm_label_display = ttk.Label(ring_content_frame, text=self.alarm_label, 
                                              font=("SimHei", 14), wraplength=400)
                alarm_label_display.pack(anchor="center", pady=3)
            
            # 按钮框架
            button_frame = ttk.Frame(ring_content_frame)
            button_frame.pack(fill="x", pady=20)
            
            # 居中按钮
            button_center_frame = ttk.Frame(button_frame)
            button_center_frame.pack(anchor="center")
            
            # 停止按钮
            stop_button = ttk.Button(button_center_frame, text="停止闹钟", command=self.stop_ringing, width=12)
            stop_button.pack(side="left", padx=10)
            
            # 关闭闹钟按钮
            close_button = ttk.Button(button_center_frame, text="关闭闹钟", command=self.close_alarm, width=12)
            close_button.pack(side="left", padx=10)
            
            # 贪睡按钮
            snooze_button = ttk.Button(button_center_frame, text=f"贪睡 {self.snooze_time} 分钟", command=self.snooze_alarm, width=15)
            snooze_button.pack(side="left", padx=10)
            
            logging.info("闹钟响铃窗口已创建")
        except Exception as e:
            logging.error(f"创建响铃窗口时出错: {e}")
            messagebox.showerror("错误", "显示闹钟窗口失败")
    
    def stop_ringing(self):
        """停止闹钟响铃 - 增强版，使用结构化分层终止策略确保播放器被正确关闭"""
        print("[DEBUG] 停止闹钟响铃 - 开始执行结构化分层终止策略")
        try:
            import time, os
            
            with self.lock:
                # 立即设置状态标志，防止并发操作
                self.is_ringing = False
                self._music_playing = False
                
                # 销毁响铃窗口
                if self.ringing_window:
                    try:
                        self.ringing_window.destroy()
                        print("[DEBUG] 响铃窗口已销毁")
                    except Exception as e:
                        print(f"[DEBUG] 销毁响铃窗口时出错: {e}")
                        logging.error(f"销毁响铃窗口时出错: {e}")
                    self.ringing_window = None
                
                # 终止阶段0: 停止内置播放器（如果正在使用）
                try:
                    if 'global_player' in globals() and global_player:
                        print("[DEBUG] 停止内置播放器")
                        global_player.stop()
                        print("[DEBUG] 内置播放器已停止")
                except Exception as e:
                    print(f"[ERROR] 停止内置播放器时出错: {e}")
                
                # 终止阶段1: 处理直接保存的播放器进程
                try:
                    self._terminate_direct_player_process()
                except Exception as e:
                    print(f"[ERROR] 执行直接播放器进程终止时出错: {e}")
                
                # 终止阶段2: 调用优化后的终止媒体播放器方法
                try:
                    print("[DEBUG] 执行增强版媒体播放器终止方法")
                    
                    # 收集当前播放的音乐文件信息（如果有）
                    self._collect_playing_media_files()
                    
                    # 首先尝试普通终止模式
                    standard_success = self._terminate_recent_media_players(force=False)
                    
                    # 添加短暂延迟让系统有时间响应终止请求
                    if standard_success:
                        print("[DEBUG] 标准终止模式已成功执行，给予系统响应时间")
                        time.sleep(0.15)  # 略微减少延迟以提高响应速度
                    
                    # 强制终止作为备用策略
                    print("[DEBUG] 执行强制终止模式以确保所有进程停止")
                    force_success = self._terminate_recent_media_players(force=True)
                    
                    print(f"[DEBUG] 终止操作完成 - 标准模式: {'成功' if standard_success else '未成功'}, 强制模式: {'成功' if force_success else '未成功'}")
                except Exception as e:
                    print(f"[ERROR] 执行媒体播放器终止时出错: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 终止阶段3: 最终兜底 - 针对特定媒体文件的进程终止
                try:
                    self._terminate_processes_by_media_file()
                except Exception as e:
                    print(f"[ERROR] 执行文件关联进程终止时出错: {e}")
                
                # 全面清理所有相关状态
                self._reset_all_alarm_states()
                
                # 恢复主窗口状态
                try:
                    self.root.deiconify()  # 显示主窗口（如果被隐藏）
                    self.root.update()  # 更新界面
                    print("[DEBUG] 主窗口状态已恢复")
                except Exception as e:
                    print(f"[DEBUG] 恢复主窗口状态时出错: {e}")
                
                # 重置闹钟UI
                try:
                    self.reset_alarm_ui()
                    print("[DEBUG] 闹钟UI已重置")
                except Exception as e:
                    print(f"[DEBUG] 重置闹钟UI时出错: {e}")
                
                print("[DEBUG] 闹钟停止操作已完成")
                logging.info("闹钟已成功停止")
                return True
                
        except Exception as e:
            print(f"[ERROR] 停止闹钟时发生未预期错误: {e}")
            import traceback
            traceback.print_exc()
            logging.error(f"停止闹钟时发生未预期错误: {e}")
            
            # 即使出错也要尝试清理基本状态
            try:
                with self.lock:
                    self._reset_all_alarm_states()
            except:
                pass
                
            # 显示错误消息
            try:
                messagebox.showerror("错误", "停止闹钟失败，请尝试手动关闭播放器")
            except:
                pass
            return False
    
    def _terminate_direct_player_process(self):
        """专门处理直接保存的播放器进程，提取为单独方法以提高可维护性"""
        print("[DEBUG] 处理直接保存的播放器进程")
        if hasattr(self, 'player_process') and self.player_process:
            try:
                # 检查进程是否仍然存活
                if self.player_process.poll() is None:
                    print(f"[DEBUG] 发现存活的播放器进程，尝试终止 PID: {self.player_process.pid}")
                    
                    # 尝试正常终止
                    try:
                        self.player_process.terminate()
                        
                        # 尝试使用taskkill更可靠地终止进程树（Windows专用）
                        try:
                            import subprocess
                            result = subprocess.run(
                                ['taskkill', '/F', '/T', '/PID', str(self.player_process.pid)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=2.0
                            )
                            print(f"[DEBUG] 已尝试taskkill终止进程树，结果: {'成功' if result.returncode == 0 else '失败'}")
                        except Exception as kill_error:
                            print(f"[DEBUG] taskkill执行异常: {kill_error}")
                            
                            # 如果taskkill失败且进程仍在运行，尝试强制终止
                            if self.player_process.poll() is None:
                                try:
                                    self.player_process.kill()
                                    print("[DEBUG] 已执行直接kill操作")
                                except Exception:
                                    pass
                    except Exception as term_error:
                        print(f"[DEBUG] 进程终止过程出错: {term_error}")
                
                # 无论如何都重置player_process引用
                self.player_process = None
                print("[DEBUG] 播放器进程引用已重置")
                
            except Exception as e:
                print(f"[DEBUG] 处理播放器进程时发生错误: {e}")
                self.player_process = None
    
    def _collect_playing_media_files(self):
        """收集当前可能正在播放的媒体文件信息，提供给终止方法"""
        print("[DEBUG] 收集可能正在播放的媒体文件信息")
        
        # 确保_launched_media_files列表存在
        if not hasattr(self, '_launched_media_files'):
            self._launched_media_files = []
        
        # 从当前响铃的闹钟获取音乐文件
        if hasattr(self, 'current_ringing_alarm_id') and self.current_ringing_alarm_id:
            if hasattr(self, 'alarms_data'):
                for alarm in self.alarms_data:
                    if alarm.get('id') == self.current_ringing_alarm_id:
                        sound_file = alarm.get('sound_file')
                        if sound_file and os.path.exists(sound_file) and sound_file not in self._launched_media_files:
                            self._launched_media_files.append(sound_file)
                            print(f"[DEBUG] 添加闹钟声音文件到跟踪列表: {sound_file}")
                        break
        
        # 检查local_music_path
        if hasattr(self, 'local_music_path') and self.local_music_path:
            if os.path.exists(self.local_music_path) and self.local_music_path not in self._launched_media_files:
                self._launched_media_files.append(self.local_music_path)
                print(f"[DEBUG] 添加本地音乐文件到跟踪列表: {self.local_music_path}")
    
    def _terminate_processes_by_media_file(self):
        """针对特定媒体文件的进程终止作为最后兜底方案"""
        print("[DEBUG] 执行文件关联进程终止（兜底方案）")
        
        # 获取可能的音乐文件路径
        music_files = []
        
        # 从当前响铃的闹钟获取
        if hasattr(self, 'current_ringing_alarm_id') and self.current_ringing_alarm_id:
            if hasattr(self, 'alarms_data'):
                for alarm in self.alarms_data:
                    if alarm.get('id') == self.current_ringing_alarm_id:
                        sound_file = alarm.get('sound_file')
                        if sound_file and os.path.exists(sound_file):
                            music_files.append(sound_file)
                        break
        
        # 添加local_music_path（如果有）
        if hasattr(self, 'local_music_path') and self.local_music_path and os.path.exists(self.local_music_path):
            if self.local_music_path not in music_files:
                music_files.append(self.local_music_path)
        
        # 处理每个找到的音乐文件
        for music_file in music_files:
            try:
                filename = os.path.basename(music_file)
                print(f"[DEBUG] 查找与文件 {filename} 相关的进程")
                
                # 使用PowerShell查找相关进程
                import subprocess
                ps_command = f"Get-WmiObject -Class Win32_Process | Where-Object {{ $_.CommandLine -like \"*{filename}*\" }} | Select-Object -ExpandProperty ProcessId"
                result = subprocess.run(
                    ['powershell.exe', '-Command', ps_command],
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=1.5
                )
                
                # 解析PID并终止
                for line in result.stdout.strip().split('\n'):
                    pid_str = line.strip()
                    if pid_str.isdigit():
                        pid = pid_str
                        print(f"[DEBUG] 发现关联进程 PID: {pid}，尝试终止")
                        try:
                            subprocess.run(
                                ['taskkill', '/PID', pid, '/F', '/T'],
                                shell=False,
                                timeout=1.0
                            )
                            print(f"[DEBUG] ✓ 已尝试终止文件关联进程 PID: {pid}")
                        except Exception:
                            pass
            except Exception as e:
                print(f"[DEBUG] 处理文件 {music_file} 关联进程时出错: {e}")
    
    def _reset_all_alarm_states(self):
        """全面重置所有闹钟和播放器相关状态"""
        print("[DEBUG] 执行全面状态重置")
        
        # 重置状态标志
        self.is_ringing = False
        if hasattr(self, '_music_playing'):
            self._music_playing = False
            print("[DEBUG] 音乐播放标志已重置")
        
        # 清除当前响铃的闹钟ID
        if hasattr(self, 'current_ringing_alarm_id'):
            self.current_ringing_alarm_id = None
            print("[DEBUG] 当前响铃闹钟ID已清除")
        
        # 清除播放器跟踪信息
        if hasattr(self, '_last_launched_player_pid'):
            self._last_launched_player_pid = None
            print("[DEBUG] 最后启动播放器PID已清除")
        
        # 重置媒体启动时间
        if hasattr(self, '_last_media_launch_time'):
            self._last_media_launch_time = None
            print("[DEBUG] 媒体启动时间已重置")
        
        # 清空媒体文件列表
        if hasattr(self, '_launched_media_files'):
            self._launched_media_files.clear()
            print("[DEBUG] 已清空媒体文件列表")
        
        # 清空进程历史
        if hasattr(self, '_player_process_history'):
            self._player_process_history.clear()
            print("[DEBUG] 已清空进程历史记录")
            
        print("[DEBUG] 所有闹钟相关状态已重置")
        
        # 所有终止逻辑已被新的结构化方法替换
        # 请查看上面的_terminate_direct_player_process、_terminate_recent_media_players等方法
        pass
    
    def close_alarm(self):
        """完全关闭闹钟（停止响铃并确保闹钟不再响起）"""
        try:
            # 先调用stop_ringing停止响铃
            self.stop_ringing()
            
            # 确保所有相关状态都被重置
            with self.lock:
                # 如果有当前触发的闹钟，确保它不会再次响起
                self.alarm_set = False
                self.alarm_time = None
                self.current_alarm_label = ""
                
                # 从列表中移除已触发的单次闹钟
                # 注意：实际上alarm_thread_func已经处理了移除，但这里再次确保
                logging.info("闹钟已完全关闭")
        except Exception as e:
            logging.error(f"关闭闹钟时出错: {e}")
            messagebox.showerror("错误", "关闭闹钟失败")
    
    def snooze_alarm(self):
        """贪睡功能"""
        try:
            with self.lock:
                self.is_ringing = False
                
                if self.ringing_window:
                    try:
                        self.ringing_window.destroy()
                    except Exception as e:
                        logging.error(f"销毁响铃窗口时出错: {e}")
                    self.ringing_window = None
                
                # 计算贪睡后的时间
                now = datetime.datetime.now()
                snooze_datetime = now + datetime.timedelta(minutes=self.snooze_time)
                
                # 创建新的贪睡闹钟
                snooze_alarm = {
                    'id': self.alarm_id_counter,
                    'time': snooze_datetime,
                    'label': self.current_alarm_label + " (贪睡)",
                    'snooze': self.snooze_time,
                    'enabled': True,
                    'created_at': datetime.datetime.now()
                }
                self.alarm_id_counter += 1
                
                # 添加到闹钟列表
                self.alarms.append(snooze_alarm)
                
                # 保持向后兼容
                self.alarm_time = snooze_datetime.time()
                self.alarm_label = snooze_alarm['label']
                self.alarm_set = True
                
                # 更新状态和列表
                self.status_var.set(f"贪睡中... 将在 {self.snooze_time} 分钟后再次提醒")
                self.root.after(0, self.update_alarm_list_display)
                logging.info(f"闹钟已贪睡: {self.snooze_time}分钟")
                
                # 重置停止事件并启动闹钟线程
                self.stop_event.clear()
                if self.alarm_thread and self.alarm_thread.is_alive():
                    try:
                        self.alarm_thread.join(timeout=1.0)
                    except Exception as e:
                        logging.error(f"等待线程结束时出错: {e}")
                
                try:
                    self.alarm_thread = threading.Thread(target=self.alarm_thread_func, daemon=True)
                    self.alarm_thread.start()
                except Exception as e:
                    logging.error(f"启动贪睡线程失败: {e}")
                    messagebox.showerror("错误", "设置贪睡失败，请重试")
                    self.reset_alarm_ui()
        except Exception as e:
            logging.error(f"设置贪睡时出错: {e}")
            messagebox.showerror("错误", "设置贪睡失败")
    
    def show_alarm_notification(self):
        """显示闹钟通知（现在通过单独的窗口处理）"""
        # 这个函数现在已经不需要了，因为我们使用单独的窗口来显示闹钟提醒
        pass
    
    def edit_alarm(self, alarm_id):
        """编辑闹钟信息"""
        try:
            # 查找要编辑的闹钟
            alarm_to_edit = None
            for alarm in self.alarms:
                if alarm['id'] == alarm_id:
                    alarm_to_edit = alarm
                    break
            
            if not alarm_to_edit:
                messagebox.showwarning("错误", f"未找到闹钟 ID={alarm_id}")
                return
            
            # 创建编辑窗口
            edit_window = tk.Toplevel(self.root)
            edit_window.title("编辑闹钟")
            edit_window.geometry("350x250")
            edit_window.resizable(False, False)
            edit_window.configure(bg="#f0f0f0")
            edit_window.attributes("-topmost", True)
            
            # 标签输入
            ttk.Label(edit_window, text="标签:", background="#f0f0f0").grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
            label_var = tk.StringVar(value=alarm_to_edit['label'])
            label_entry = ttk.Entry(edit_window, textvariable=label_var, width=30)
            label_entry.grid(row=0, column=1, padx=20, pady=(20, 5))
            
            # 贪睡时间输入
            ttk.Label(edit_window, text="贪睡时间(分钟):", background="#f0f0f0").grid(row=1, column=0, sticky="w", padx=20, pady=5)
            snooze_var = tk.StringVar(value=str(alarm_to_edit['snooze']))
            snooze_entry = ttk.Entry(edit_window, textvariable=snooze_var, width=10)
            snooze_entry.grid(row=1, column=1, padx=20, pady=5, sticky="w")
            
            # 按钮区域
            button_frame = ttk.Frame(edit_window)
            button_frame.grid(row=2, column=0, columnspan=2, pady=20)
            
            def save_changes():
                try:
                    # 验证贪睡时间
                    snooze = int(snooze_var.get())
                    if snooze < 1 or snooze > 60:
                        messagebox.showerror("错误", "贪睡时间必须在1-60分钟之间")
                        return
                    
                    # 保存更改
                    with self.lock:
                        alarm_to_edit['label'] = label_var.get().strip()
                        alarm_to_edit['snooze'] = snooze
                    
                    logging.info(f"已编辑闹钟 ID={alarm_id}, 新标签='{label_var.get()}', 新贪睡时间={snooze}分钟")
                    messagebox.showinfo("成功", "闹钟信息已更新")
                    
                    # 更新显示
                    self.root.after(0, self.update_alarm_list_display)
                    edit_window.destroy()
                except ValueError:
                    messagebox.showerror("错误", "请输入有效的贪睡时间")
            
            ttk.Button(button_frame, text="保存", command=save_changes).pack(side="left", padx=10)
            ttk.Button(button_frame, text="取消", command=edit_window.destroy).pack(side="left", padx=10)
            
        except Exception as e:
            logging.error(f"编辑闹钟时出错: {e}")
            messagebox.showerror("错误", f"编辑闹钟时出错: {str(e)}")
    
    def sort_alarms_by_time(self):
        """按时间排序闹钟"""
        self.alarms.sort(key=lambda x: x['time'])
        self.update_alarm_list_display()
        logging.info("闹钟列表已按时间排序")
    
    def sort_alarms_by_label(self):
        """按标签排序闹钟"""
        self.alarms.sort(key=lambda x: x['label'] or "")
        self.update_alarm_list_display()
        logging.info("闹钟列表已按标签排序")
    
    def update_alarm_list_display(self):
        """更新闹钟列表的显示"""
        try:
            # 清空现有列表
            for item in self.alarm_tree.get_children():
                self.alarm_tree.delete(item)
            
            # 获取当前闹钟列表的副本以确保线程安全
            with self.lock:
                current_alarms = self.alarms.copy()
            
            # 添加当前设置的所有闹钟
            for alarm in current_alarms:  # 不再默认排序，使用当前顺序
                try:
                    time_str = alarm['time'].strftime("%H:%M")
                    label = alarm['label'] if alarm['label'] else "无标签"
                    
                    # 插入行
                    item = self.alarm_tree.insert("", "end", values=(alarm['id'], time_str, label, alarm['snooze'], ""))
                    
                    # 创建操作按钮框架
                    button_frame = ttk.Frame(self.alarm_tree)
                    
                    # 编辑按钮
                    edit_button = ttk.Button(
                        button_frame, 
                        text="编辑", 
                        width=5,
                        command=lambda a_id=alarm['id']: self.edit_alarm(a_id)
                    )
                    edit_button.pack(side="left", padx=2)
                    
                    # 删除按钮
                    delete_button = ttk.Button(
                        button_frame, 
                        text="删除", 
                        width=5,
                        command=lambda a_id=alarm['id']: self.stop_alarm(a_id)
                    )
                    delete_button.pack(side="left", padx=2)
                    
                    # 由于window_create方法不可用，改为显示操作文本
                    self.alarm_tree.set(item, "actions", "编辑 | 删除")
                    
                    # 添加点击事件处理
                    def on_tree_click(event):
                        region = self.alarm_tree.identify_region(event.x, event.y)
                        if region == "cell":
                            column = self.alarm_tree.identify_column(event.x)
                            item = self.alarm_tree.identify_row(event.y)
                            if column == "#5":  # actions列
                                x, y, width, height = self.alarm_tree.bbox(item, column)
                                if event.x - x < width/2:
                                    # 点击左侧 - 编辑
                                    a_id = int(self.alarm_tree.item(item, "values")[0])
                                    self.edit_alarm(a_id)
                                else:
                                    # 点击右侧 - 删除
                                    a_id = int(self.alarm_tree.item(item, "values")[0])
                                    self.stop_alarm(a_id)
                    
                    # 只绑定一次点击事件
                    if not hasattr(self.alarm_tree, '_click_bound'):
                        self.alarm_tree.bind('<ButtonRelease-1>', on_tree_click)
                        self.alarm_tree._click_bound = True
                except Exception as e:
                    logging.error(f"更新单个闹钟显示时出错: ID={alarm.get('id', 'unknown')}, 错误={str(e)}")
            
            # 更新状态和按钮
            with self.lock:
                alarm_count = len(self.alarms)
            
            if alarm_count > 0:
                self.status_var.set(f"已设置 {alarm_count} 个闹钟")
                self.stop_button.config(state="normal")
            else:
                self.status_var.set("就绪")
                self.stop_button.config(state="disabled")
                self.countdown_label.config(text="无设置的闹钟", foreground="black")
            
            logging.debug(f"成功更新闹钟列表显示，当前显示 {alarm_count} 个闹钟")
            
        except Exception as e:
            error_msg = f"更新闹钟列表显示时发生错误: {str(e)}"
            logging.error(error_msg)
            # 不显示错误弹窗，避免影响用户体验
    
    def reset_alarm_ui(self):
        """重置闹钟UI状态"""
        self.update_alarm_list_display()
    
    def on_closing(self):
        """窗口关闭时的处理"""
        try:
            logging.info("应用程序正在关闭...")
            
            # 停止所有闹钟活动
            with self.lock:
                self.stop_event.set()
                self.is_ringing = False
                self.alarm_set = False
                
                if self.ringing_window:
                    try:
                        self.ringing_window.destroy()
                    except:
                        pass
            
            # 清理内置播放器资源
            try:
                if 'global_player' in globals() and global_player:
                    print("[DEBUG] 清理内置播放器资源")
                    global_player.stop()
                    global_player.quit()
                    print("[DEBUG] 内置播放器资源已清理")
            except Exception as e:
                print(f"[ERROR] 清理内置播放器时出错: {e}")
            
            # 等待线程结束
            if self.alarm_thread and self.alarm_thread.is_alive():
                try:
                    self.alarm_thread.join(timeout=1.0)
                except:
                    pass
            
            logging.info("应用程序已关闭")
            self.root.destroy()
        except Exception as e:
            logging.error(f"关闭应用程序时出错: {e}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        print("[DEBUG] 启动主应用...")
        root = tk.Tk()
        # 确保中文显示正常
        root.option_add("*Font", "SimHei 10")
        
        app = AlarmClockGUI(root)
        
        # 紧急更新循环已在初始化时启动
        
        print("[DEBUG] 进入主循环...")
        root.mainloop()
    except Exception as e:
        print(f"[CRITICAL] 应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        # 显示错误对话框
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("启动错误", f"应用程序无法启动:\n\n{str(e)}")
        error_root.destroy()
