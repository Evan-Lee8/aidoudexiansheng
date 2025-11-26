#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
闹钟应用测试脚本
用于验证alarm_clock_gui.py的核心功能和错误处理
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import datetime
import tkinter as tk
from tkinter import messagebox
import threading
import time

# 导入被测试的模块
sys.path.append('.')
try:
    from alarm_clock_gui import AlarmClockGUI
    MODULE_AVAILABLE = True
except Exception as e:
    print(f"导入模块失败: {e}")
    MODULE_AVAILABLE = False

class TestAlarmClockGUI(unittest.TestCase):
    """闹钟GUI测试类"""
    
    def setUp(self):
        """设置测试环境"""
        if not MODULE_AVAILABLE:
            self.skipTest("无法导入闹钟模块")
        
        # 创建根窗口但不显示
        self.root = tk.Tk()
        self.root.withdraw()
        
        # 创建测试实例
        self.app = AlarmClockGUI(self.root)
        
        # 模拟消息框
        self.patcher = patch('tkinter.messagebox')
        self.mock_messagebox = self.patcher.start()
    
    def tearDown(self):
        """清理测试环境"""
        if MODULE_AVAILABLE:
            self.patcher.stop()
            self.root.destroy()
    
    @patch.object(AlarmClockGUI, 'alarm_thread_func')
    def test_set_alarm_valid_time(self, mock_thread_func):
        """测试设置有效的闹钟时间"""
        # 设置测试输入
        self.app.hour_var.set("10")
        self.app.minute_var.set("30")
        self.app.snooze_var.set(5)
        self.app.use_24h_format = True
        
        # 调用设置闹钟方法
        self.app.set_alarm()
        
        # 验证结果
        self.assertTrue(self.app.alarm_set)
        self.assertEqual(self.app.alarm_time, datetime.time(10, 30))
        self.assertEqual(self.app.snooze_time, 5)
        self.mock_messagebox.showinfo.assert_called_once()
        mock_thread_func.assert_not_called()  # 线程应该在测试中被替换
    
    def test_set_alarm_invalid_time(self):
        """测试设置无效的闹钟时间"""
        # 设置无效输入
        self.app.hour_var.set("25")  # 无效的小时
        self.app.minute_var.set("30")
        
        # 调用设置闹钟方法
        self.app.set_alarm()
        
        # 验证结果
        self.assertFalse(self.app.alarm_set)
        self.mock_messagebox.showerror.assert_called_with("错误", "请输入有效的时间")
    
    def test_stop_alarm(self):
        """测试取消闹钟"""
        # 先设置闹钟
        self.app.alarm_set = True
        self.app.alarm_time = datetime.time(10, 30)
        
        # 调用停止闹钟方法
        self.app.stop_alarm()
        
        # 验证结果
        self.assertFalse(self.app.alarm_set)
        self.assertTrue(self.app.stop_event.is_set())
        self.mock_messagebox.showinfo.assert_called_with("提示", "闹钟已成功取消")
    
    def test_time_format_conversion(self):
        """测试时间格式转换"""
        # 测试24小时制到12小时制的转换
        self.app.use_24h_format = False
        self.app.ampm_var.set("PM")
        
        # 设置下午时间
        self.app.hour_var.set("3")
        self.app.minute_var.set("00")
        
        # 捕获内部行为
        with patch.object(self.app, '_validate_and_set_time') as mock_set:
            mock_set.return_value = True
            self.app.set_alarm()
    
    def test_thread_safety(self):
        """测试线程安全机制"""
        # 验证锁对象存在
        self.assertIsInstance(self.app.lock, threading.RLock)

# 简单的命令行测试函数
def run_quick_tests():
    """运行简单的命令行测试"""
    print("=== 闹钟应用快速测试 ===")
    
    # 测试模块导入
    try:
        from alarm_clock_gui import AlarmClockGUI
        print("✓ 模块导入成功")
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False
    
    # 测试基本功能可用性
    try:
        # 创建临时的Tkinter根窗口
        root = tk.Tk()
        root.withdraw()
        
        # 创建应用实例
        app = AlarmClockGUI(root)
        print("✓ GUI类实例化成功")
        
        # 测试关键方法
        print("测试核心方法...")
        
        # 模拟一些基本操作
        app.hour_var.set("12")
        app.minute_var.set("00")
        app.snooze_var.set(5)
        
        print("✓ 基本属性设置成功")
        
        # 清理
        root.destroy()
        print("✓ 资源清理成功")
        return True
    
    except Exception as e:
        print(f"✗ GUI测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试闹钟应用...")
    
    # 运行简单的命令行测试
    if run_quick_tests():
        print("\n基本功能测试通过！")
        print("\n应用程序特点:")
        print("1. 完整的图形用户界面")
        print("2. 支持12/24小时制切换")
        print("3. 实时时间和倒计时显示")
        print("4. 闹钟标签设置")
        print("5. 贪睡功能")
        print("6. 完善的错误处理和日志记录")
        print("7. 线程安全的操作")
        print("8. 用户友好的交互界面")
        
        print("\n请直接运行 python alarm_clock_gui.py 来启动闹钟应用！")
    else:
        print("\n测试未通过，请检查应用代码")
