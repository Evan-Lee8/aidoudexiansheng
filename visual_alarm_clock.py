#!/usr/bin/env python3
"""
可视化闹钟应用 - 内置播放器版本
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import time
import threading
import os
import logging
import pygame
import math


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='visual_alarm_clock.log'
)

class VisualAlarmClock:
    """可视化闹钟应用类"""
    
    def __init__(self, root):
        """初始化应用"""
        self.root = root
        self.root.title("可视化闹钟")
        self.root.geometry("900x800")
        self.root.resizable(True, True)  # 允许调整窗口大小
        
        # 设置窗口图标（如果有）
        # self.root.iconbitmap("icon.ico")
        
        # 设置背景色
        self.root.configure(bg="#f8f9fa")
        
        # 配置主题
        self.configure_theme()
        
        # 初始化内置播放器
        self.player = self._initialize_player()
        
        # 闹钟状态
        self.alarms = []
        self.next_alarm = None
        self.is_ringing = False
        self.ringing_alarm = None
        
        # 日程状态
        self.schedules = []
        self.next_schedule = None
        self.is_schedule_reminding = False
        self.reminding_schedule = None
        
        # 当前选择的铃声
        self.current_ringtone = "默认铃声"
        self.ringtone_path = None
        
        # 创建界面
        self.create_widgets()
        
        # 启动时钟更新
        self.update_clock()
        
        # 启动闹钟检查线程
        self.alarm_thread = threading.Thread(target=self._check_alarms, daemon=True)
        self.alarm_thread.start()
        
        # 启动日程检查线程
        self.schedule_thread = threading.Thread(target=self._check_schedules, daemon=True)
        self.schedule_thread.start()
    
    def configure_theme(self):
        """配置应用主题"""
        # 设置样式
        self.style = ttk.Style()
        
        # 设置主题为clam，提供更好的样式支持
        self.style.theme_use("clam")
        
        # 主色调
        primary_color = "#3498db"
        secondary_color = "#2ecc71"
        accent_color = "#e74c3c"
        bg_color = "#f8f9fa"
        text_color = "#2c3e50"
        light_text = "#7f8c8d"
        
        # 配置整体样式
        self.style.configure(
            "TFrame",
            background=bg_color
        )
        
        # 标签样式
        self.style.configure(
            "TLabel",
            font=(
                "Segoe UI",
                12
            ),
            foreground=text_color,
            background=bg_color
        )
        
        # 按钮样式
        self.style.configure(
            "TButton",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            padding=8,
            background=primary_color,
            foreground="white",
            borderwidth=1,
            relief="flat"
        )
        self.style.map(
            "TButton",
            background=[("active", primary_color + "99"), ("pressed", primary_color + "77")],
            foreground=[("active", "white"), ("pressed", "white")]
        )
        
        # 时钟样式
        self.style.configure(
            "Clock.TLabel",
            font=(
                "Segoe UI",
                48,
                "bold"
            ),
            foreground=primary_color
        )
        
        # 日期样式
        self.style.configure(
            "Date.TLabel",
            font=(
                "Segoe UI",
                16
            ),
            foreground=light_text
        )
        
        # 标题样式
        self.style.configure(
            "Title.TLabel",
            font=(
                "Segoe UI",
                28,
                "bold"
            ),
            foreground=text_color
        )
        
        # 标签框架样式
        self.style.configure(
            "TLabelframe",
            background=bg_color,
            foreground=text_color,
            font=("Segoe UI", 14, "bold")
        )
        self.style.configure(
            "TLabelframe.Label",
            background=bg_color,
            foreground=text_color
        )
        
        # 笔记本样式
        self.style.configure(
            "TNotebook",
            background=bg_color
        )
        self.style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 14, "bold"),
            padding=10,
            background=bg_color,
            foreground=light_text
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", primary_color), ("active", bg_color)],
            foreground=[("selected", "white"), ("active", text_color)]
        )
        
        # 树形视图样式
        self.style.configure(
            "Treeview",
            font=("Segoe UI", 11),
            background="white",
            foreground=text_color,
            rowheight=25,
            fieldbackground="white"
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 12, "bold"),
            background=primary_color,
            foreground="white",
            padding=8
        )
        self.style.map(
            "Treeview.Heading",
            background=[("active", primary_color + "99")]
        )
        self.style.map(
            "Treeview",
            background=[("selected", primary_color + "22")],
            foreground=[("selected", text_color)]
        )
        
        # 滚动条样式
        self.style.configure(
            "Vertical.TScrollbar",
            background=primary_color,
            troughcolor=bg_color,
            arrowcolor="white"
        )
        self.style.map(
            "Vertical.TScrollbar",
            background=[("active", primary_color + "99")]
        )
    
    def _initialize_player(self):
        """初始化内置音频播放器"""
        try:
            pygame.mixer.init()
            logging.info("内置音频播放器初始化成功")
            return pygame.mixer
        except Exception as e:
            logging.error(f"内置音频播放器初始化失败: {e}")
            messagebox.showerror("错误", "内置音频播放器初始化失败")
            return None
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建笔记本控件（Tab）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建闹钟Tab
        self.alarm_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.alarm_tab, text="闹钟")
        self._create_alarm_widgets()
        
        # 创建日程Tab
        self.schedule_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_tab, text="日程")
        self._create_schedule_widgets()
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="#27ae60")
        status_label.pack(pady=10)
    
    def _create_alarm_widgets(self):
        """创建闹钟相关的界面组件"""
        # 标题
        title_label = ttk.Label(self.alarm_tab, text="闹钟", style="Title.TLabel")
        title_label.pack(pady=20)
        
        # 主要内容框架
        main_content = ttk.Frame(self.alarm_tab)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 顶部区域：时钟显示
        top_frame = ttk.Frame(main_content)
        top_frame.pack(fill=tk.X, pady=10)
        
        # 时钟样式选择
        style_frame = ttk.Frame(top_frame)
        style_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(style_frame, text="时钟样式:", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.clock_style_var = tk.StringVar(value="digital")
        
        radio_container = ttk.Frame(style_frame)
        radio_container.pack(side=tk.LEFT, padx=10)
        
        digital_radio = ttk.Radiobutton(radio_container, text="数字时钟", variable=self.clock_style_var, value="digital", command=self._switch_clock_style)
        digital_radio.pack(side=tk.LEFT, padx=10)
        
        analog_radio = ttk.Radiobutton(radio_container, text="表盘时钟", variable=self.clock_style_var, value="analog", command=self._switch_clock_style)
        analog_radio.pack(side=tk.LEFT, padx=10)
        
        # 时钟显示区域
        clock_container = ttk.Frame(top_frame, padding=20, relief="groove")
        clock_container.pack(fill=tk.X, pady=15)
        
        # 日期显示
        self.date_label = ttk.Label(clock_container, text="", style="Date.TLabel")
        self.date_label.pack(pady=5)
        
        # 数字时钟显示
        self.digital_clock_frame = ttk.Frame(clock_container)
        self.digital_clock_frame.pack()
        self.time_label = ttk.Label(self.digital_clock_frame, text="", style="Clock.TLabel")
        self.time_label.pack(pady=10)
        
        # 表盘时钟显示
        self.analog_clock_frame = ttk.Frame(clock_container)
        self.analog_clock_frame.pack()
        self.analog_clock_canvas = tk.Canvas(self.analog_clock_frame, width=250, height=250, bg="white", relief="solid", borderwidth=1)
        self.analog_clock_canvas.pack(pady=10)
        self.analog_clock_frame.pack_forget()  # 默认隐藏表盘时钟
        
        # 倒计时显示
        countdown_frame = ttk.LabelFrame(top_frame, text="下次闹钟", padding=15)
        countdown_frame.pack(fill=tk.X, pady=15)
        
        self.countdown_label = ttk.Label(countdown_frame, text="无设置的闹钟", font=("Segoe UI", 18, "bold"), foreground="#3498db")
        self.countdown_label.pack(pady=15)
        
        # 中间区域：闹钟设置和列表
        middle_frame = ttk.Frame(main_content)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 左侧：闹钟设置
        settings_frame = ttk.LabelFrame(middle_frame, text="设置闹钟", padding=20)
        settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)
        
        # 时间选择
        time_frame = ttk.Frame(settings_frame)
        time_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(time_frame, text="时间:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 小时选择
        self.hour_var = tk.IntVar(value=datetime.datetime.now().hour)
        hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.hour_var, width=7, font=("Segoe UI", 14))
        hour_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(time_frame, text=":", font=("Segoe UI", 14, "bold")).grid(row=0, column=2, padx=5, pady=5)
        
        # 分钟选择
        self.minute_var = tk.IntVar(value=datetime.datetime.now().minute)
        minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.minute_var, width=7, font=("Segoe UI", 14))
        minute_spinbox.grid(row=0, column=3, padx=5, pady=5)
        
        # 标签
        label_frame = ttk.Frame(settings_frame)
        label_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(label_frame, text="标签:", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.label_var = tk.StringVar(value="我的闹钟")
        label_entry = ttk.Entry(label_frame, textvariable=self.label_var, font=("Segoe UI", 14))
        label_entry.pack(fill=tk.X, pady=5)
        
        # 铃声选择
        ringtone_frame = ttk.LabelFrame(settings_frame, text="铃声设置", padding=15)
        ringtone_frame.pack(fill=tk.X, pady=15)
        
        ringtone_select = ttk.Frame(ringtone_frame)
        ringtone_select.pack(fill=tk.X, pady=5)
        
        ttk.Label(ringtone_select, text="铃声:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        ringtone_options = ["默认铃声", "本地音乐"]
        self.ringtone_var = tk.StringVar(value="默认铃声")
        ringtone_combo = ttk.Combobox(ringtone_select, textvariable=self.ringtone_var, values=ringtone_options, state="readonly", width=15, font=("Segoe UI", 11))
        ringtone_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ringtone_combo.bind("<<ComboboxSelected>>", self._on_ringtone_change)
        
        # 浏览按钮
        button_row = ttk.Frame(ringtone_frame)
        button_row.pack(fill=tk.X, pady=10)
        
        self.browse_button = ttk.Button(button_row, text="浏览...", command=self._browse_ringtone, state=tk.DISABLED, width=10)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        # 预览按钮
        self.preview_button = ttk.Button(button_row, text="预览", command=self._preview_ringtone, width=10)
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        # 音量控制
        volume_frame = ttk.Frame(ringtone_frame)
        volume_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(volume_frame, text="音量:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=5)
        
        volume_control = ttk.Frame(volume_frame)
        volume_control.pack(fill=tk.X, pady=5)
        
        self.volume_var = tk.DoubleVar(value=0.7)
        volume_scale = ttk.Scale(volume_control, from_=0.1, to=1.0, variable=self.volume_var, orient=tk.HORIZONTAL, length=150)
        volume_scale.pack(side=tk.LEFT, padx=5)
        
        self.volume_label = ttk.Label(volume_control, text="70%", width=6, font=("Segoe UI", 11, "bold"))
        self.volume_label.pack(side=tk.LEFT, padx=8)
        
        # 绑定音量变化
        self.volume_var.trace_add("write", self._on_volume_change)
        
        # 按钮区域
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="设置闹钟", command=self._set_alarm).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="取消所有闹钟", command=self._cancel_all_alarms).pack(fill=tk.X, pady=5)
        
        # 右侧：闹钟列表
        alarms_frame = ttk.LabelFrame(middle_frame, text="已设置的闹钟", padding=15)
        alarms_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        
        # 创建Treeview来显示闹钟列表
        columns = ("id", "time", "label", "ringtone", "volume")
        self.alarm_tree = ttk.Treeview(alarms_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题
        self.alarm_tree.heading("id", text="ID")
        self.alarm_tree.heading("time", text="时间")
        self.alarm_tree.heading("label", text="标签")
        self.alarm_tree.heading("ringtone", text="铃声")
        self.alarm_tree.heading("volume", text="音量")
        
        # 设置列宽
        self.alarm_tree.column("id", width=50, anchor=tk.CENTER)
        self.alarm_tree.column("time", width=120, anchor=tk.CENTER)
        self.alarm_tree.column("label", width=150, anchor=tk.W)
        self.alarm_tree.column("ringtone", width=150, anchor=tk.W)
        self.alarm_tree.column("volume", width=80, anchor=tk.CENTER)
        
        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(alarms_frame, orient=tk.VERTICAL, command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.alarm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 闹钟列表操作按钮
        list_button_frame = ttk.Frame(alarms_frame, padding=10)
        list_button_frame.pack(fill=tk.X)
        
        button_container = ttk.Frame(list_button_frame)
        button_container.pack(fill=tk.X)
        
        ttk.Button(button_container, text="删除选中闹钟", command=self._delete_selected_alarm).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(button_container, text="刷新列表", command=self._refresh_alarm_list).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def _create_schedule_widgets(self):
        """创建日程相关的界面组件"""
        # 标题
        title_label = ttk.Label(self.schedule_tab, text="日程管理", style="Title.TLabel")
        title_label.pack(pady=20)
        
        # 主要内容框架
        main_content = ttk.Frame(self.schedule_tab)
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧：添加日程
        left_frame = ttk.LabelFrame(main_content, text="添加日程", padding=20)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5)
        
        # 日期选择
        date_frame = ttk.Frame(left_frame)
        date_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(date_frame, text="日期:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 年选择
        self.schedule_year_var = tk.IntVar(value=datetime.datetime.now().year)
        year_spinbox = ttk.Spinbox(date_frame, from_=2020, to=2030, textvariable=self.schedule_year_var, width=8, font=("Segoe UI", 13))
        year_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(date_frame, text="年", font=("Segoe UI", 12)).grid(row=0, column=2, padx=0, pady=5)
        
        # 月选择
        self.schedule_month_var = tk.IntVar(value=datetime.datetime.now().month)
        month_spinbox = ttk.Spinbox(date_frame, from_=1, to=12, textvariable=self.schedule_month_var, width=6, font=("Segoe UI", 13))
        month_spinbox.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(date_frame, text="月", font=("Segoe UI", 12)).grid(row=0, column=4, padx=0, pady=5)
        
        # 日选择
        self.schedule_day_var = tk.IntVar(value=datetime.datetime.now().day)
        day_spinbox = ttk.Spinbox(date_frame, from_=1, to=31, textvariable=self.schedule_day_var, width=6, font=("Segoe UI", 13))
        day_spinbox.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(date_frame, text="日", font=("Segoe UI", 12)).grid(row=0, column=6, padx=0, pady=5)
        
        # 时间选择
        time_frame = ttk.Frame(left_frame)
        time_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(time_frame, text="时间:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 小时选择
        self.schedule_hour_var = tk.IntVar(value=datetime.datetime.now().hour)
        hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.schedule_hour_var, width=6, font=("Segoe UI", 13))
        hour_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(time_frame, text=":", font=("Segoe UI", 13, "bold")).grid(row=0, column=2, padx=5, pady=5)
        
        # 分钟选择
        self.schedule_minute_var = tk.IntVar(value=datetime.datetime.now().minute)
        minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.schedule_minute_var, width=6, font=("Segoe UI", 13))
        minute_spinbox.grid(row=0, column=3, padx=5, pady=5)
        
        # 日程标题
        title_frame = ttk.Frame(left_frame)
        title_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(title_frame, text="标题:", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.schedule_title_var = tk.StringVar(value="我的日程")
        title_entry = ttk.Entry(title_frame, textvariable=self.schedule_title_var, font=("Segoe UI", 13))
        title_entry.pack(fill=tk.X, pady=5)
        
        # 日程内容
        content_frame = ttk.Frame(left_frame)
        content_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(content_frame, text="内容:", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=5)
        self.schedule_content_text = tk.Text(content_frame, height=6, font=("Segoe UI", 13), relief="solid", borderwidth=1)
        self.schedule_content_text.pack(fill=tk.X, pady=5)
        
        # 提醒设置
        reminder_frame = ttk.Frame(left_frame)
        reminder_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(reminder_frame, text="提前提醒:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        reminder_options = ["不提醒", "5分钟前", "10分钟前", "30分钟前", "1小时前", "1天前"]
        self.reminder_var = tk.StringVar(value="5分钟前")
        reminder_combo = ttk.Combobox(reminder_frame, textvariable=self.reminder_var, values=reminder_options, state="readonly", width=18, font=("Segoe UI", 12))
        reminder_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 按钮区域
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="添加日程", command=self._add_schedule).pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="取消所有日程", command=self._cancel_all_schedules).pack(fill=tk.X, pady=5)
        
        # 右侧：日程列表
        right_frame = ttk.LabelFrame(main_content, text="已添加的日程", padding=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)
        
        # 创建Treeview来显示日程列表
        columns = ("id", "datetime", "title", "content", "reminder")
        self.schedule_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=12)
        
        # 设置列标题
        self.schedule_tree.heading("id", text="ID")
        self.schedule_tree.heading("datetime", text="日期时间")
        self.schedule_tree.heading("title", text="标题")
        self.schedule_tree.heading("content", text="内容")
        self.schedule_tree.heading("reminder", text="提醒设置")
        
        # 设置列宽
        self.schedule_tree.column("id", width=50, anchor=tk.CENTER)
        self.schedule_tree.column("datetime", width=160, anchor=tk.CENTER)
        self.schedule_tree.column("title", width=150, anchor=tk.W)
        self.schedule_tree.column("content", width=200, anchor=tk.W)
        self.schedule_tree.column("reminder", width=120, anchor=tk.CENTER)
        
        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.schedule_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 日程列表操作按钮
        list_button_frame = ttk.Frame(right_frame, padding=15)
        list_button_frame.pack(fill=tk.X)
        
        button_container = ttk.Frame(list_button_frame)
        button_container.pack(fill=tk.X)
        
        ttk.Button(button_container, text="删除选中日程", command=self._delete_selected_schedule).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(button_container, text="刷新列表", command=self._refresh_schedule_list).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def update_clock(self):
        """更新时钟显示"""
        now = datetime.datetime.now()
        
        # 更新日期
        date_str = now.strftime("%Y年%m月%d日 %A")
        self.date_label.config(text=date_str)
        
        # 更新数字时钟
        time_str = now.strftime("%H:%M:%S")
        self.time_label.config(text=time_str)
        
        # 更新表盘时钟
        self._draw_analog_clock(now)
        
        # 更新倒计时
        self._update_countdown()
        
        # 每秒更新一次
        self.root.after(1000, self.update_clock)
    
    def _switch_clock_style(self):
        """切换时钟样式"""
        style = self.clock_style_var.get()
        if style == "digital":
            self.digital_clock_frame.pack()
            self.analog_clock_frame.pack_forget()
        else:
            self.digital_clock_frame.pack_forget()
            self.analog_clock_frame.pack()
    
    def _draw_analog_clock(self, now):
        """绘制表盘时钟"""
        # 清空画布
        self.analog_clock_canvas.delete("all")
        
        # 画布中心坐标
        center_x = 100
        center_y = 100
        radius = 90
        
        # 绘制表盘
        self.analog_clock_canvas.create_oval(center_x - radius, center_y - radius, 
                                           center_x + radius, center_y + radius, 
                                           fill="white", outline="black", width=2)
        
        # 绘制刻度
        for i in range(12):
            angle = i * 30  # 每个小时刻度间隔30度
            radian = math.radians(angle - 90)  # 转换为弧度，-90度使0点在顶部
            
            # 长刻度（小时）
            start_x = center_x + (radius - 20) * math.cos(radian)
            start_y = center_y + (radius - 20) * math.sin(radian)
            end_x = center_x + radius * math.cos(radian)
            end_y = center_y + radius * math.sin(radian)
            
            # 绘制刻度线
            self.analog_clock_canvas.create_line(start_x, start_y, end_x, end_y, width=2)
            
            # 绘制小时数字
            num_x = center_x + (radius - 35) * math.cos(radian)
            num_y = center_y + (radius - 35) * math.sin(radian)
            self.analog_clock_canvas.create_text(num_x, num_y, text=str(i if i != 0 else 12), font=("Segoe UI", 12, "bold"))
        
        # 绘制分钟刻度
        for i in range(60):
            if i % 5 != 0:  # 跳过小时刻度
                angle = i * 6  # 每个分钟刻度间隔6度
                radian = math.radians(angle - 90)  # 转换为弧度，-90度使0点在顶部
                
                start_x = center_x + (radius - 15) * math.cos(radian)
                start_y = center_y + (radius - 15) * math.sin(radian)
                end_x = center_x + radius * math.cos(radian)
                end_y = center_y + radius * math.sin(radian)
                
                # 绘制刻度线
                self.analog_clock_canvas.create_line(start_x, start_y, end_x, end_y, width=1)
        
        # 获取当前时间
        hour = now.hour % 12
        minute = now.minute
        second = now.second
        
        # 计算指针角度
        hour_angle = (hour + minute / 60 + second / 3600) * 30 - 90  # 每小时30度，-90度使0点在顶部
        minute_angle = (minute + second / 60) * 6 - 90  # 每分钟6度，-90度使0点在顶部
        second_angle = second * 6 - 90  # 每秒6度，-90度使0点在顶部
        
        # 转换为弧度
        hour_radian = math.radians(hour_angle)
        minute_radian = math.radians(minute_angle)
        second_radian = math.radians(second_angle)
        
        # 绘制时针
        hour_length = radius * 0.5
        hour_x = center_x + hour_length * math.cos(hour_radian)
        hour_y = center_y + hour_length * math.sin(hour_radian)
        self.analog_clock_canvas.create_line(center_x, center_y, hour_x, hour_y, width=4, fill="black")
        
        # 绘制分针
        minute_length = radius * 0.7
        minute_x = center_x + minute_length * math.cos(minute_radian)
        minute_y = center_y + minute_length * math.sin(minute_radian)
        self.analog_clock_canvas.create_line(center_x, center_y, minute_x, minute_y, width=3, fill="black")
        
        # 绘制秒针
        second_length = radius * 0.8
        second_x = center_x + second_length * math.cos(second_radian)
        second_y = center_y + second_length * math.sin(second_radian)
        self.analog_clock_canvas.create_line(center_x, center_y, second_x, second_y, width=2, fill="red")
        
        # 绘制中心点
        self.analog_clock_canvas.create_oval(center_x - 5, center_y - 5, center_x + 5, center_y + 5, fill="black")
    
    def _update_countdown(self):
        """更新下次闹钟倒计时"""
        if not self.next_alarm:
            self.countdown_label.config(text="无设置的闹钟")
            return
        
        now = datetime.datetime.now()
        time_diff = self.next_alarm - now
        
        if time_diff.total_seconds() <= 0:
            self.countdown_label.config(text="闹钟正在响铃!")
            return
        
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        countdown_str = f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒"
        self.countdown_label.config(text=f"下次闹钟: {countdown_str}")
    
    def _add_schedule(self):
        """添加日程"""
        try:
            # 获取日期时间
            year = self.schedule_year_var.get()
            month = self.schedule_month_var.get()
            day = self.schedule_day_var.get()
            hour = self.schedule_hour_var.get()
            minute = self.schedule_minute_var.get()
            
            # 创建日程时间
            schedule_time = datetime.datetime(year, month, day, hour, minute, 0)
            
            # 获取其他信息
            title = self.schedule_title_var.get()
            content = self.schedule_content_text.get("1.0", tk.END).strip()
            reminder = self.reminder_var.get()
            
            # 计算提醒时间
            reminder_time = self._calculate_reminder_time(schedule_time, reminder)
            
            # 创建日程对象
            schedule = {
                "id": len(self.schedules) + 1,
                "time": schedule_time,
                "title": title,
                "content": content,
                "reminder": reminder,
                "reminder_time": reminder_time
            }
            
            # 添加到日程列表
            self.schedules.append(schedule)
            
            # 更新下次日程
            self._update_next_schedule()
            
            # 更新状态
            time_str = schedule_time.strftime("%Y-%m-%d %H:%M")
            self.status_var.set(f"日程已添加: {time_str} - {title}")
            
            # 刷新日程列表
            self._refresh_schedule_list()
            
            logging.info(f"日程已添加: {time_str} - {title}")
            messagebox.showinfo("成功", f"日程已添加到 {time_str}")
            
        except Exception as e:
            logging.error(f"添加日程失败: {e}")
            messagebox.showerror("错误", f"添加日程失败: {e}")
    
    def _calculate_reminder_time(self, schedule_time, reminder):
        """根据提醒设置计算实际提醒时间"""
        if reminder == "不提醒":
            return None
        elif reminder == "5分钟前":
            return schedule_time - datetime.timedelta(minutes=5)
        elif reminder == "10分钟前":
            return schedule_time - datetime.timedelta(minutes=10)
        elif reminder == "30分钟前":
            return schedule_time - datetime.timedelta(minutes=30)
        elif reminder == "1小时前":
            return schedule_time - datetime.timedelta(hours=1)
        elif reminder == "1天前":
            return schedule_time - datetime.timedelta(days=1)
        else:
            return None
    
    def _update_next_schedule(self):
        """更新下次日程"""
        if not self.schedules:
            self.next_schedule = None
            return
        
        # 找到最近的日程提醒时间
        upcoming_schedules = []
        now = datetime.datetime.now()
        
        for schedule in self.schedules:
            if schedule["reminder_time"] and schedule["reminder_time"] > now:
                upcoming_schedules.append(schedule["reminder_time"])
        
        if upcoming_schedules:
            self.next_schedule = min(upcoming_schedules)
        else:
            self.next_schedule = None
    
    def _refresh_schedule_list(self):
        """刷新日程列表显示"""
        # 清空现有数据
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        # 添加所有日程到列表
        for schedule in self.schedules:
            datetime_str = schedule["time"].strftime("%Y-%m-%d %H:%M")
            content = schedule["content"] if len(schedule["content"]) <= 20 else schedule["content"][:20] + "..."
            
            self.schedule_tree.insert("", tk.END, values=(schedule["id"], datetime_str, schedule["title"], content, schedule["reminder"]))
    
    def _delete_selected_schedule(self):
        """删除选中的日程"""
        selected_item = self.schedule_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择要删除的日程")
            return
        
        # 获取选中日程的ID
        selected_id = int(self.schedule_tree.item(selected_item)['values'][0])
        
        # 找到并删除日程
        for schedule in self.schedules:
            if schedule["id"] == selected_id:
                self.schedules.remove(schedule)
                break
        
        # 更新下次日程
        self._update_next_schedule()
        
        # 刷新日程列表
        self._refresh_schedule_list()
        
        # 更新状态
        self.status_var.set(f"日程ID {selected_id} 已删除")
        logging.info(f"日程ID {selected_id} 已删除")
        messagebox.showinfo("成功", f"日程ID {selected_id} 已删除")
    
    def _cancel_all_schedules(self):
        """取消所有日程"""
        if self.schedules:
            self.schedules = []
            self.next_schedule = None
            self.status_var.set("所有日程已取消")
            
            # 刷新日程列表
            self._refresh_schedule_list()
            
            logging.info("所有日程已取消")
            messagebox.showinfo("成功", "所有日程已取消")
        else:
            messagebox.showinfo("提示", "没有添加的日程")
    
    def _check_schedules(self):
        """检查日程是否需要提醒"""
        while True:
            if self.schedules and not self.is_schedule_reminding:
                now = datetime.datetime.now()
                for schedule in self.schedules:
                    if schedule["reminder_time"] and now >= schedule["reminder_time"]:
                        # 日程提醒
                        self._remind_schedule(schedule)
                        break
            
            time.sleep(1)
    
    def _remind_schedule(self, schedule):
        """日程提醒"""
        self.is_schedule_reminding = True
        self.reminding_schedule = schedule
        
        logging.info(f"日程提醒: {schedule['time'].strftime('%Y-%m-%d %H:%M')} - {schedule['title']}")
        
        # 创建提醒窗口
        self._create_schedule_reminder_window()
        
        # 更新状态
        self.status_var.set(f"日程提醒: {schedule['title']}")
    
    def _create_schedule_reminder_window(self):
        """创建日程提醒窗口"""
        self.reminder_window = tk.Toplevel(self.root)
        self.reminder_window.title("日程提醒")
        self.reminder_window.geometry("400x300")
        self.reminder_window.attributes("-topmost", True)
        
        # 设置窗口样式
        self.reminder_window.configure(bg="#3498db")
        
        # 提醒信息
        info_frame = ttk.Frame(self.reminder_window, padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text="日程提醒!", style="Title.TLabel").pack(pady=20)
        ttk.Label(info_frame, text=f"标题: {self.reminding_schedule['title']}").pack(pady=10)
        ttk.Label(info_frame, text=f"时间: {self.reminding_schedule['time'].strftime('%Y-%m-%d %H:%M')}").pack(pady=10)
        
        # 内容显示
        content_frame = ttk.Frame(info_frame)
        content_frame.pack(fill=tk.X, pady=10)
        ttk.Label(content_frame, text="内容:").pack(anchor=tk.W)
        content_text = tk.Text(content_frame, height=5, width=40, font=("Segoe UI", 12))
        content_text.insert(tk.END, self.reminding_schedule['content'])
        content_text.config(state=tk.DISABLED)
        content_text.pack(fill=tk.X)
        
        # 按钮
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(pady=20, fill=tk.X)
        
        ttk.Button(button_frame, text="关闭", command=self._close_schedule_reminder).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(button_frame, text="稍后提醒", command=lambda: self._snooze_schedule(5)).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    def _close_schedule_reminder(self):
        """关闭日程提醒"""
        self.is_schedule_reminding = False
        
        if hasattr(self, "reminder_window"):
            self.reminder_window.destroy()
        
        self.status_var.set("日程提醒已关闭")
        logging.info("日程提醒已关闭")
    
    def _snooze_schedule(self, minutes):
        """日程稍后提醒"""
        if not self.reminding_schedule:
            return
        
        # 关闭当前提醒
        self._close_schedule_reminder()
        
        # 找到原日程
        original_schedule = None
        for schedule in self.schedules:
            if schedule["id"] == self.reminding_schedule["id"]:
                original_schedule = schedule
                break
        
        if original_schedule:
            # 更新提醒时间
            original_schedule["reminder_time"] = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            
            # 更新下次日程
            self._update_next_schedule()
            
            # 更新状态
            self.status_var.set(f"日程将在{minutes}分钟后再次提醒: {original_schedule['title']}")
            logging.info(f"日程稍后提醒: {original_schedule['title']}")
    
    def _on_ringtone_change(self, event):
        """处理铃声选择变化"""
        ringtone_type = self.ringtone_var.get()
        if ringtone_type == "本地音乐":
            self.browse_button.config(state=tk.NORMAL)
        else:
            self.browse_button.config(state=tk.DISABLED)
            self.ringtone_path = None
    
    def _browse_ringtone(self):
        """浏览并选择本地音乐文件"""
        file_path = filedialog.askopenfilename(
            title="选择铃声文件",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.ogg *.flac *.m4a *.wma *.aac *.mid *.midi"),
                ("MP3文件", "*.mp3"),
                ("WAV文件", "*.wav"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.ringtone_path = file_path
            filename = os.path.basename(file_path)
            self.ringtone_var.set(f"本地音乐: {filename}")
    
    def _preview_ringtone(self):
        """预览选中的铃声"""
        if not self.player:
            messagebox.showerror("错误", "内置播放器不可用")
            return
        
        try:
            self.player.stop()
            
            if self.ringtone_var.get() == "默认铃声":
                # 使用Pygame生成默认铃声
                # 创建一个简单的旋律
                import numpy as np
                import pygame
                
                # 设置音频参数
                sample_rate = 44100
                duration = 0.5  # 持续时间(秒)
                frequency = 1000  # 频率(Hz)
                
                # 生成音频数据
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                note = 0.5 * np.sin(2 * np.pi * frequency * t)
                
                # 创建另一个高一点的音符
                frequency2 = 1200
                note2 = 0.5 * np.sin(2 * np.pi * frequency2 * t)
                
                # 合并音符
                sound_data = np.concatenate((note, note2))
                
                # 转换为16位整数
                sound_data = np.int16(sound_data * 32767)
                
                # 创建Pygame Sound对象
                sound = pygame.mixer.Sound(buffer=sound_data.tobytes(), channels=1, frequency=sample_rate, size=-16)
                
                # 播放铃声
                sound.set_volume(self.volume_var.get())
                sound.play()
            elif self.ringtone_path:
                # 播放本地音乐
                self.player.music.load(self.ringtone_path)
                self.player.music.set_volume(self.volume_var.get())
                self.player.music.play(0)
                
                # 10秒后自动停止预览
                self.root.after(10000, lambda: self.player.music.stop())
        except Exception as e:
            logging.error(f"预览铃声失败: {e}")
            messagebox.showerror("错误", f"预览铃声失败: {e}")
    
    def _on_volume_change(self, *args):
        """处理音量变化"""
        volume = self.volume_var.get()
        volume_percent = int(volume * 100)
        self.volume_label.config(text=f"{volume_percent}%")
    
    def _set_alarm(self):
        """设置闹钟"""
        try:
            # 获取时间
            hour = self.hour_var.get()
            minute = self.minute_var.get()
            label = self.label_var.get()
            
            # 创建闹钟时间
            now = datetime.datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # 如果设置的时间已经过去，则设置为明天
            if alarm_time <= now:
                alarm_time += datetime.timedelta(days=1)
            
            # 创建闹钟对象
            alarm = {
                "id": len(self.alarms) + 1,
                "time": alarm_time,
                "label": label,
                "ringtone": self.ringtone_var.get(),
                "ringtone_path": self.ringtone_path,
                "volume": self.volume_var.get()
            }
            
            # 添加到闹钟列表
            self.alarms.append(alarm)
            
            # 更新下次闹钟
            self._update_next_alarm()
            
            # 更新状态
            time_str = alarm_time.strftime("%H:%M")
            self.status_var.set(f"闹钟已设置: {time_str} - {label}")
            
            # 刷新闹钟列表
            self._refresh_alarm_list()
            
            logging.info(f"闹钟已设置: {time_str} - {label}")
            messagebox.showinfo("成功", f"闹钟已设置为 {time_str}")
            
        except Exception as e:
            logging.error(f"设置闹钟失败: {e}")
            messagebox.showerror("错误", f"设置闹钟失败: {e}")
    
    def _update_next_alarm(self):
        """更新下次闹钟"""
        if not self.alarms:
            self.next_alarm = None
            return
        
        # 找到最近的闹钟
        self.alarms.sort(key=lambda x: x["time"])
        self.next_alarm = self.alarms[0]["time"]
    
    def _refresh_alarm_list(self):
        """刷新闹钟列表显示"""
        # 清空现有数据
        for item in self.alarm_tree.get_children():
            self.alarm_tree.delete(item)
        
        # 添加所有闹钟到列表
        for alarm in self.alarms:
            time_str = alarm["time"].strftime("%Y-%m-%d %H:%M")
            volume = f"{int(alarm['volume'] * 100)}%"
            
            # 如果铃声是本地音乐，只显示文件名
            ringtone = alarm["ringtone"]
            if ringtone.startswith("本地音乐:"):
                ringtone = os.path.basename(alarm["ringtone_path"])
            
            self.alarm_tree.insert("", tk.END, values=(alarm["id"], time_str, alarm["label"], ringtone, volume))
    
    def _delete_selected_alarm(self):
        """删除选中的闹钟"""
        selected_item = self.alarm_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择要删除的闹钟")
            return
        
        # 获取选中闹钟的ID
        selected_id = int(self.alarm_tree.item(selected_item)['values'][0])
        
        # 找到并删除闹钟
        for alarm in self.alarms:
            if alarm["id"] == selected_id:
                self.alarms.remove(alarm)
                break
        
        # 更新下次闹钟
        self._update_next_alarm()
        
        # 刷新闹钟列表
        self._refresh_alarm_list()
        
        # 更新状态
        self.status_var.set(f"闹钟ID {selected_id} 已删除")
        logging.info(f"闹钟ID {selected_id} 已删除")
        messagebox.showinfo("成功", f"闹钟ID {selected_id} 已删除")
    
    def _cancel_all_alarms(self):
        """取消所有闹钟"""
        if self.alarms:
            self.alarms = []
            self.next_alarm = None
            self.status_var.set("所有闹钟已取消")
            
            # 刷新闹钟列表
            self._refresh_alarm_list()
            
            logging.info("所有闹钟已取消")
            messagebox.showinfo("成功", "所有闹钟已取消")
        else:
            messagebox.showinfo("提示", "没有设置的闹钟")
    
    def _check_alarms(self):
        """检查闹钟是否响铃"""
        while True:
            if self.alarms and not self.is_ringing:
                now = datetime.datetime.now()
                for alarm in self.alarms:
                    if now >= alarm["time"]:
                        # 闹钟响铃
                        self._ring_alarm(alarm)
                        
                        # 从列表中移除已响铃的闹钟
                        self.alarms.remove(alarm)
                        
                        # 更新下次闹钟
                        self._update_next_alarm()
                        
                        # 刷新闹钟列表
                        self.root.after(0, self._refresh_alarm_list)
                        break
            
            time.sleep(1)
    
    def _ring_alarm(self, alarm):
        """闹钟响铃"""
        self.is_ringing = True
        self.ringing_alarm = alarm
        
        logging.info(f"闹钟响铃: {alarm['time'].strftime('%H:%M')} - {alarm['label']}")
        
        # 创建响铃窗口
        self._create_ringing_window()
        
        try:
            if not self.player:
                # 如果Pygame播放器不可用，使用简单的音效
                messagebox.showerror("错误", "内置播放器不可用")
                self._stop_alarm()
            else:
                # 使用内置Pygame播放器
                self.player.stop()
                
                if alarm["ringtone"] == "默认铃声":
                    # 使用Pygame生成默认铃声
                    import numpy as np
                    import pygame
                    
                    # 设置音频参数
                    sample_rate = 44100
                    duration = 0.3  # 持续时间(秒)
                    
                    # 创建旋律
                    frequencies = [1000, 1200, 1000, 800]  # 音符频率
                    sounds = []
                    
                    for freq in frequencies:
                        # 生成音频数据
                        t = np.linspace(0, duration, int(sample_rate * duration), False)
                        note = 0.5 * np.sin(2 * np.pi * freq * t)
                        
                        # 转换为16位整数
                        sound_data = np.int16(note * 32767)
                        
                        # 创建Pygame Sound对象
                        sound = pygame.mixer.Sound(buffer=sound_data.tobytes(), channels=1, frequency=sample_rate, size=-16)
                        sounds.append(sound)
                    
                    # 循环播放旋律直到停止
                    while self.is_ringing:
                        for sound in sounds:
                            if not self.is_ringing:
                                break
                            sound.set_volume(alarm["volume"])
                            sound.play()
                            time.sleep(duration)
                        if self.is_ringing:
                            time.sleep(0.2)  # 短暂停顿
                elif alarm["ringtone_path"]:
                    # 播放本地音乐
                    self.player.music.load(alarm["ringtone_path"])
                    self.player.music.set_volume(alarm["volume"])
                    self.player.music.play(-1)  # 循环播放
        except Exception as e:
            logging.error(f"响铃失败: {e}")
            messagebox.showerror("错误", f"响铃失败: {e}")
    
    def _create_ringing_window(self):
        """创建响铃窗口"""
        self.ringing_window = tk.Toplevel(self.root)
        self.ringing_window.title("闹钟响铃")
        self.ringing_window.geometry("400x300")
        self.ringing_window.attributes("-topmost", True)
        
        # 设置窗口样式
        self.ringing_window.configure(bg="#e74c3c")
        
        # 响铃信息
        info_frame = ttk.Frame(self.ringing_window, padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(info_frame, text="闹钟响铃!", style="Title.TLabel").pack(pady=20)
        ttk.Label(info_frame, text=self.ringing_alarm["label"]).pack(pady=10)
        
        # 按钮
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(pady=20, fill=tk.X)
        
        ttk.Button(button_frame, text="停止", command=self._stop_alarm).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(button_frame, text="贪睡5分钟", command=lambda: self._snooze_alarm(5)).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    def _stop_alarm(self):
        """停止闹钟"""
        self.is_ringing = False
        
        if self.player:
            self.player.music.stop()
        
        if hasattr(self, "ringing_window"):
            self.ringing_window.destroy()
        
        self.status_var.set("闹钟已停止")
        logging.info("闹钟已停止")
    
    def _snooze_alarm(self, minutes):
        """贪睡功能"""
        if not self.ringing_alarm:
            return
        
        # 停止当前响铃
        self._stop_alarm()
        
        # 创建贪睡闹钟
        now = datetime.datetime.now()
        snooze_time = now + datetime.timedelta(minutes=minutes)
        
        snooze_alarm = self.ringing_alarm.copy()
        snooze_alarm["id"] = len(self.alarms) + 1
        snooze_alarm["time"] = snooze_time
        snooze_alarm["label"] = f"贪睡 - {self.ringing_alarm['label']}"
        
        # 添加到闹钟列表
        self.alarms.append(snooze_alarm)
        self._update_next_alarm()
        
        # 更新状态
        time_str = snooze_time.strftime("%H:%M")
        self.status_var.set(f"贪睡闹钟已设置: {time_str}")
        logging.info(f"贪睡闹钟已设置: {time_str} - {self.ringing_alarm['label']}")

# 导入winsound库用于模拟默认铃声


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VisualAlarmClock(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"应用程序错误: {e}")
        messagebox.showerror("错误", f"应用程序发生错误: {e}")
