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
        self.root.geometry("450x600")
        self.root.resizable(True, True)
        
        # 配置主题
        self.configure_theme()
        
        # 初始化内置播放器
        self.player = self._initialize_player()
        
        # 闹钟状态
        self.alarms = []
        self.next_alarm = None
        self.is_ringing = False
        self.ringing_alarm = None
        
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
    
    def configure_theme(self):
        """配置应用主题"""
        # 设置样式
        self.style = ttk.Style()
        self.style.configure(
            "TLabel",
            font=(
                "Segoe UI",
                8
            ),
            foreground="#333"
        )
        self.style.configure(
            "TButton",
            font=(
                "Segoe UI",
                5
            ),
            padding=6
        )
        self.style.configure(
            "Clock.TLabel",
            font=(
                "Segoe UI",
                5,
                "bold"
            ),
            foreground="#2c3e50"
        )
        self.style.configure(
            "Date.TLabel",
            font=(
                "Segoe UI",
                12
            ),
            foreground="#7f8c8d"
        )
        self.style.configure(
            "Title.TLabel",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            foreground="#2c3e50"
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
        
        # 标题
        title_label = ttk.Label(main_frame, text="闹钟", style="Title.TLabel")
        title_label.pack(pady=20)
        
        # 时钟显示
        clock_frame = ttk.Frame(main_frame)
        clock_frame.pack(pady=20)
        
        self.date_label = ttk.Label(clock_frame, text="", style="Date.TLabel")
        self.date_label.pack()
        
        self.time_label = ttk.Label(clock_frame, text="", style="Clock.TLabel")
        self.time_label.pack()
        
        # 倒计时显示
        countdown_frame = ttk.LabelFrame(main_frame, text="下次闹钟", padding=10)
        countdown_frame.pack(fill=tk.X, pady=10)
        
        self.countdown_label = ttk.Label(countdown_frame, text="无设置的闹钟", font=("Segoe UI", 14))
        self.countdown_label.pack(pady=10)
        
        # 闹钟设置
        settings_frame = ttk.LabelFrame(main_frame, text="设置闹钟", padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 时间选择
        time_frame = ttk.Frame(settings_frame)
        time_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(time_frame, text="时间:").grid(row=0, column=0, padx=5, pady=5)
        
        # 小时选择
        self.hour_var = tk.IntVar(value=datetime.datetime.now().hour)
        hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.hour_var, width=5, font=("Segoe UI", 12))
        hour_spinbox.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(time_frame, text=":").grid(row=0, column=2, padx=5, pady=5)
        
        # 分钟选择
        self.minute_var = tk.IntVar(value=datetime.datetime.now().minute)
        minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.minute_var, width=5, font=("Segoe UI", 12))
        minute_spinbox.grid(row=0, column=3, padx=5, pady=5)
        
        # 标签
        self.label_var = tk.StringVar(value="我的闹钟")
        ttk.Label(settings_frame, text="标签:").pack(anchor=tk.W, pady=5)
        label_entry = ttk.Entry(settings_frame, textvariable=self.label_var, font=("Segoe UI", 12))
        label_entry.pack(fill=tk.X, pady=5)
        
        # 铃声选择
        ringtone_frame = ttk.Frame(settings_frame)
        ringtone_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(ringtone_frame, text="铃声:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        ringtone_options = ["默认铃声", "本地音乐"]
        self.ringtone_var = tk.StringVar(value="默认铃声")
        ringtone_combo = ttk.Combobox(ringtone_frame, textvariable=self.ringtone_var, values=ringtone_options, state="readonly")
        ringtone_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ringtone_combo.bind("<<ComboboxSelected>>", self._on_ringtone_change)
        
        # 浏览按钮
        self.browse_button = ttk.Button(ringtone_frame, text="浏览...", command=self._browse_ringtone, state=tk.DISABLED)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        
        # 预览按钮
        self.preview_button = ttk.Button(ringtone_frame, text="预览", command=self._preview_ringtone)
        self.preview_button.grid(row=0, column=3, padx=5, pady=5)
        
        # 音量控制
        volume_frame = ttk.Frame(settings_frame)
        volume_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(volume_frame, text="音量:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.volume_var = tk.DoubleVar(value=0.7)
        volume_scale = ttk.Scale(volume_frame, from_=0.1, to=1.0, variable=self.volume_var, orient=tk.HORIZONTAL, length=200)
        volume_scale.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        self.volume_label = ttk.Label(volume_frame, text="70%")
        self.volume_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 绑定音量变化
        self.volume_var.trace_add("write", self._on_volume_change)
        
        # 按钮区域
        button_frame = ttk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="设置闹钟", command=self._set_alarm).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(button_frame, text="取消所有闹钟", command=self._cancel_all_alarms).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # 闹钟列表
        alarms_frame = ttk.LabelFrame(main_frame, text="已设置的闹钟", padding=10)
        alarms_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建Treeview来显示闹钟列表
        columns = ("id", "time", "label", "ringtone", "volume")
        self.alarm_tree = ttk.Treeview(alarms_frame, columns=columns, show="headings", height=5)
        
        # 设置列标题
        self.alarm_tree.heading("id", text="ID")
        self.alarm_tree.heading("time", text="时间")
        self.alarm_tree.heading("label", text="标签")
        self.alarm_tree.heading("ringtone", text="铃声")
        self.alarm_tree.heading("volume", text="音量")
        
        # 设置列宽
        self.alarm_tree.column("id", width=30, anchor=tk.CENTER)
        self.alarm_tree.column("time", width=80, anchor=tk.CENTER)
        self.alarm_tree.column("label", width=120, anchor=tk.W)
        self.alarm_tree.column("ringtone", width=120, anchor=tk.W)
        self.alarm_tree.column("volume", width=40, anchor=tk.CENTER)
        
        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(alarms_frame, orient=tk.VERTICAL, command=self.alarm_tree.yview)
        self.alarm_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.alarm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 闹钟列表操作按钮
        list_button_frame = ttk.Frame(alarms_frame, padding=10)
        list_button_frame.pack(fill=tk.X)
        
        ttk.Button(list_button_frame, text="删除选中闹钟", command=self._delete_selected_alarm).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(list_button_frame, text="刷新列表", command=self._refresh_alarm_list).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 状态显示
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="#27ae60")
        status_label.pack(pady=10)
    
    def update_clock(self):
        """更新时钟显示"""
        now = datetime.datetime.now()
        
        # 更新日期
        date_str = now.strftime("%Y年%m月%d日 %A")
        self.date_label.config(text=date_str)
        
        # 更新时间
        time_str = now.strftime("%H:%M:%S")
        self.time_label.config(text=time_str)
        
        # 更新倒计时
        self._update_countdown()
        
        # 每秒更新一次
        self.root.after(1000, self.update_clock)
    
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
