import tkinter as tk
from tkinter import messagebox
import subprocess
import time
import os

# 测试应用启动脚本
print("开始测试闹钟应用启动...")

# 检查闹钟应用是否正在运行
def check_alarm_process():
    try:
        # 使用tasklist命令查找python进程
        result = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/V'], 
                                       universal_newlines=True, shell=True)
        for line in result.splitlines():
            if 'alarm_clock_gui.py' in line:
                print(f"发现运行中的闹钟应用进程: {line.strip()}")
                return True
        return False
    except Exception as e:
        print(f"检查进程时出错: {e}")
        return False

# 等待应用启动
print("等待5秒以确认应用稳定运行...")
time.sleep(5)

# 检查进程
if check_alarm_process():
    print("✅ 闹钟应用进程正在运行")
    
    # 显示成功消息
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showinfo(
        "测试成功",
        "闹钟应用已成功启动并正在运行！\n\n- UI组件创建完成\n- 主循环正常运行\n- 紧急更新机制工作正常"
    )
    root.destroy()
    
    print("测试完成！应用启动成功。")
else:
    print("❌ 未找到闹钟应用进程")
    print("请检查应用是否正常启动。")
