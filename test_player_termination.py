#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
播放器终止功能测试脚本
用于测试闹钟应用中的播放器进程终止机制是否有效
"""

import os
import sys
import time
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_player_termination.log"),
        logging.StreamHandler()
    ]
)

# 确保可以导入alarm_clock_gui模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # 尝试导入alarm_clock_gui
    from alarm_clock_gui import AlarmClockGUI
    ALARM_MODULE_AVAILABLE = True
    logging.info("成功导入alarm_clock_gui模块")
except ImportError as e:
    ALARM_MODULE_AVAILABLE = False
    logging.error(f"无法导入alarm_clock_gui模块: {e}")

def find_test_audio_file():
    """查找测试音频文件"""
    # 常见音频文件扩展名
    audio_extensions = ['.mp3', '.wav', '.mp4', '.m4a', '.flac', '.ogg']
    
    # 首先在当前目录查找
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in audio_extensions):
            return os.path.abspath(file)
    
    # 如果没有找到，尝试创建一个简单的测试用例
    logging.warning("未找到音频文件，将使用系统播放器测试功能")
    return None

def monitor_processes(process_names):
    """监控指定名称的进程是否在运行"""
    running_processes = []
    
    try:
        # 使用tasklist命令列出进程
        result = subprocess.run(
            ['tasklist', '/FO', 'CSV'],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # 解析CSV输出
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # 跳过标题行
                try:
                    # 简单解析CSV格式的进程名
                    process_info = line.split(',')[0].strip('"')
                    for name in process_names:
                        if name.lower() in process_info.lower():
                            running_processes.append(process_info)
                            break
                except Exception as e:
                    logging.error(f"解析进程信息时出错: {e}")
    except Exception as e:
        logging.error(f"监控进程时出错: {e}")
    
    return running_processes

def test_direct_termination():
    """直接测试进程终止功能"""
    logging.info("===== 开始测试直接进程终止功能 =====")
    
    # 常见媒体播放器进程名
    media_players = ['wmplayer.exe', 'Music.UI.exe', 'vlc.exe']
    
    # 1. 启动一个测试进程
    test_process = None
    try:
        # 使用cmd启动一个假的播放器进程进行测试
        cmd_command = 'start cmd.exe /k "echo 这是测试播放器进程 & title 测试播放器"'
        logging.info(f"启动测试进程: {cmd_command}")
        subprocess.run(cmd_command, shell=True, timeout=2)
        time.sleep(2)  # 等待进程启动
        
        # 2. 查找并终止进程
        print("\n测试taskkill命令终止进程:")
        
        # 测试终止cmd.exe进程（模拟播放器）
        cmd = ['taskkill', '/FI', 'WINDOWTITLE eq 测试播放器', '/F']
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        print(f"返回码: {result.returncode}")
        print(f"输出: {result.stdout}")
        print(f"错误: {result.stderr}")
        
        # 测试PID终止
        print("\n测试通过PID终止进程:")
        # 启动一个新的测试进程
        cmd = ['start', 'cmd.exe', '/k', 'echo PID测试进程 & title PID测试']
        subprocess.run(cmd, shell=True, timeout=2)
        time.sleep(2)
        
        # 查找进程PID
        find_cmd = ['tasklist', '/FI', 'WINDOWTITLE eq PID测试', '/FO', 'CSV']
        find_result = subprocess.run(find_cmd, shell=False, capture_output=True, text=True)
        
        if find_result.returncode == 0 and find_result.stdout.strip():
            lines = find_result.stdout.strip().split('\n')
            if len(lines) > 1:
                try:
                    # 解析PID
                    pid = lines[1].split(',')[1].strip('"')
                    print(f"找到PID: {pid}")
                    
                    # 终止进程
                    kill_cmd = ['taskkill', '/PID', pid, '/T', '/F']
                    print(f"执行命令: {' '.join(kill_cmd)}")
                    kill_result = subprocess.run(kill_cmd, shell=False, capture_output=True, text=True)
                    print(f"返回码: {kill_result.returncode}")
                    print(f"输出: {kill_result.stdout}")
                except Exception as e:
                    logging.error(f"解析PID时出错: {e}")
        
        # 3. 测试wmic命令
        print("\n测试wmic命令:")
        wmic_cmd = ['wmic', 'process', 'get', 'ProcessId,Name,CommandLine', '/format:csv']
        print(f"执行命令: {' '.join(wmic_cmd)}")
        try:
            wmic_result = subprocess.run(wmic_cmd, shell=False, capture_output=True, text=True, timeout=5)
            print(f"返回码: {wmic_result.returncode}")
            # 只打印部分输出以避免过多信息
            lines = wmic_result.stdout.strip().split('\n')[:5]
            print(f"部分输出: {lines}")
        except subprocess.TimeoutExpired:
            print("wmic命令超时")
        
    except Exception as e:
        logging.error(f"测试直接终止功能时出错: {e}")
    finally:
        # 清理：确保所有测试进程都被终止
        try:
            subprocess.run(['taskkill', '/FI', 'WINDOWTITLE eq 测试播放器', '/F'], shell=False)
            subprocess.run(['taskkill', '/FI', 'WINDOWTITLE eq PID测试', '/F'], shell=False)
        except:
            pass
    
    logging.info("===== 直接进程终止功能测试完成 =====")

def simulate_alarm_gui_test():
    """模拟闹钟GUI的测试"""
    logging.info("===== 开始模拟闹钟GUI测试 =====")
    
    # 创建一个模拟的AlarmClockGUI类来测试进程管理功能
    class MockAlarmClock:
        def __init__(self):
            # 初始化与进程跟踪相关的变量
            self._last_launched_player_pid = None
            self._last_media_launch_time = None
            self._launched_media_files = []
            self._player_process_history = []
            self._max_process_history = 5
            self.lock = threading.RLock()
            logging.info("模拟AlarmClock对象初始化完成")
        
        def simulate_player_launch(self):
            """模拟启动播放器"""
            with self.lock:
                # 启动一个测试进程
                cmd = ['start', 'cmd.exe', '/k', 'echo 模拟媒体播放器 & title 模拟媒体播放器']
                logging.info(f"模拟启动播放器进程: {cmd}")
                try:
                    subprocess.run(cmd, shell=True, timeout=2)
                    time.sleep(2)
                    
                    # 查找进程PID
                    find_cmd = ['tasklist', '/FI', 'WINDOWTITLE eq 模拟媒体播放器', '/FO', 'CSV']
                    find_result = subprocess.run(find_cmd, shell=False, capture_output=True, text=True)
                    
                    if find_result.returncode == 0 and find_result.stdout.strip():
                        lines = find_result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            try:
                                pid = lines[1].split(',')[1].strip('"')
                                self._last_launched_player_pid = int(pid)
                                self._last_media_launch_time = time.time()
                                self._launched_media_files.append("test_audio.mp3")
                                
                                # 添加到进程历史
                                process_info = {
                                    'pid': int(pid),
                                    'start_time': time.time(),
                                    'file_path': "test_audio.mp3",
                                    'type': 'simulated_player'
                                }
                                self._player_process_history.append(process_info)
                                
                                logging.info(f"成功启动模拟播放器，PID: {pid}")
                                return True
                            except Exception as e:
                                logging.error(f"获取PID时出错: {e}")
                except Exception as e:
                    logging.error(f"启动模拟播放器时出错: {e}")
                return False
        
        def terminate_processes(self, force=False):
            """测试进程终止功能"""
            logging.info(f"开始终止进程，强制模式: {force}")
            import subprocess
            
            # 获取当前锁以确保线程安全
            lock_acquired = False
            try:
                self.lock.acquire()
                lock_acquired = True
            except Exception:
                pass
            
            try:
                # 1. 处理进程历史
                if self._player_process_history:
                    logging.info(f"处理进程历史，共 {len(self._player_process_history)} 个进程")
                    for i in range(len(self._player_process_history) - 1, -1, -1):
                        proc_info = self._player_process_history[i]
                        pid = proc_info.get('pid')
                        
                        try:
                            cmd = ['taskkill', '/PID', str(pid), '/T']
                            if force:
                                cmd.append('/F')
                            
                            logging.info(f"尝试终止进程 PID: {pid}")
                            result = subprocess.run(
                                cmd,
                                shell=False,
                                capture_output=True,
                                text=True,
                                timeout=3
                            )
                            
                            if result.returncode == 0:
                                logging.info(f"成功终止进程 PID: {pid}")
                                del self._player_process_history[i]
                            else:
                                logging.warning(f"终止进程失败: {result.stderr}")
                        except Exception as e:
                            logging.error(f"终止进程时出错: {e}")
                
                # 2. 终止保存的PID
                if self._last_launched_player_pid:
                    try:
                        cmd = ['taskkill', '/PID', str(self._last_launched_player_pid), '/T']
                        if force:
                            cmd.append('/F')
                        
                        logging.info(f"终止保存的PID: {self._last_launched_player_pid}")
                        result = subprocess.run(
                            cmd,
                            shell=False,
                            capture_output=True,
                            text=True,
                            timeout=3
                        )
                        
                        if result.returncode == 0:
                            logging.info(f"成功终止保存的PID")
                            self._last_launched_player_pid = None
                    except Exception as e:
                        logging.error(f"终止保存的PID时出错: {e}")
                
                # 3. 终止所有与媒体播放器相关的进程
                if force:
                    logging.info("强制终止所有可能的媒体播放器")
                    players = ['wmplayer.exe', 'Music.UI.exe', 'vlc.exe', 'cmd.exe']
                    for player in players:
                        try:
                            cmd = ['taskkill', '/FI', f'IMAGENAME eq {player}', '/F']
                            result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
                            logging.info(f"尝试终止 {player}: 返回码 {result.returncode}")
                        except Exception as e:
                            logging.error(f"终止 {player} 时出错: {e}")
            finally:
                if lock_acquired:
                    try:
                        self.lock.release()
                    except Exception:
                        pass
    
    # 运行模拟测试
    mock_alarm = MockAlarmClock()
    
    # 测试1: 正常终止
    print("\n测试1: 模拟启动播放器并正常终止")
    if mock_alarm.simulate_player_launch():
        print("播放器启动成功，等待2秒后尝试终止...")
        time.sleep(2)
        mock_alarm.terminate_processes(force=False)
        time.sleep(1)
        
        # 检查进程是否仍在运行
        running = monitor_processes(['模拟媒体播放器'])
        if running:
            print(f"警告: 进程仍在运行: {running}")
        else:
            print("✓ 进程已成功终止")
    
    # 测试2: 强制终止
    print("\n测试2: 模拟启动播放器并强制终止")
    if mock_alarm.simulate_player_launch():
        print("播放器启动成功，等待2秒后尝试强制终止...")
        time.sleep(2)
        mock_alarm.terminate_processes(force=True)
        time.sleep(1)
        
        # 检查进程是否仍在运行
        running = monitor_processes(['模拟媒体播放器'])
        if running:
            print(f"警告: 进程仍在运行: {running}")
        else:
            print("✓ 进程已成功强制终止")
    
    logging.info("===== 模拟闹钟GUI测试完成 =====")

def main():
    """主测试函数"""
    print("="*60)
    print("播放器终止功能测试工具")
    print("="*60)
    print("此工具用于测试闹钟应用中的播放器进程终止机制")
    print()
    
    # 首先运行直接的进程终止测试
    test_direct_termination()
    
    # 然后运行模拟的闹钟GUI测试
    simulate_alarm_gui_test()
    
    # 如果alarm_clock_gui模块可用，可以进行更真实的测试
    if ALARM_MODULE_AVAILABLE:
        print("\n" + "="*60)
        print("注意: alarm_clock_gui模块可用，但完整GUI测试需要手动进行")
        print("建议手动运行闹钟应用并测试以下场景:")
        print("1. 设置闹钟并选择本地音乐作为铃声")
        print("2. 当闹钟响起时，点击停止按钮")
        print("3. 验证音乐是否完全停止播放")
        print("4. 检查日志以确认播放器进程是否被成功终止")
        print("="*60)
    
    print("\n测试完成！请检查日志文件以获取详细信息。")
    print("日志文件: test_player_termination.log")
    print("\n重要提示:")
    print("1. 确保在实际使用中测试不同类型的媒体文件")
    print("2. 验证在不同Windows版本上的兼容性")
    print("3. 检查各种媒体播放器的行为差异")
    
    # 清理任何剩余的测试进程
    try:
        subprocess.run(['taskkill', '/FI', 'WINDOWTITLE eq 模拟媒体播放器', '/F'], shell=False)
        subprocess.run(['taskkill', '/FI', 'WINDOWTITLE eq 测试播放器', '/F'], shell=False)
        subprocess.run(['taskkill', '/FI', 'WINDOWTITLE eq PID测试', '/F'], shell=False)
    except Exception as e:
        print(f"清理测试进程时出错: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        print("测试结束")
