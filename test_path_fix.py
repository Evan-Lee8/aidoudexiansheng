#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证Windows路径处理和编码修复
"""

import os
import sys
import logging
import traceback

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 尝试导入playsound
playsound_available = False
playsound_func = None
try:
    from playsound import playsound as playsound_func
    playsound_available = True
    logging.info("已成功导入playsound库")
except ImportError:
    logging.warning("playsound库不可用，将使用系统播放器")

def safe_playsound(file_path):
    """安全播放音频文件，支持Windows路径处理"""
    if not playsound_available:
        logging.warning("playsound库不可用")
        return False
    
    file_path = str(file_path)
    print(f"[DEBUG] 尝试播放: {file_path}")
    
    # Windows特定的路径处理
    if os.name == 'nt':
        # 尝试1：直接使用原始路径
        try:
            playsound_func(file_path)
            print("[DEBUG] ✓ 音频播放成功 - 原始路径")
            return True
        except Exception as e:
            print(f"[DEBUG] 原始路径处理失败: {e}")
            
        # 尝试2：使用Unicode路径
        try:
            # 确保路径是Unicode字符串
            unicode_path = str(file_path)
            playsound_func(unicode_path)
            print("[DEBUG] ✓ 音频播放成功 - Unicode路径")
            return True
        except Exception as e:
            print(f"[DEBUG] Unicode路径处理失败: {e}")
            
        # 尝试3：规范化路径
        try:
            import pathlib
            norm_path = str(pathlib.Path(file_path).resolve())
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
    
    # 所有尝试都失败
    print(f"[DEBUG] 无法使用playsound播放音频文件: {file_path}")
    return False

def try_alternative_play(file_path):
    """尝试使用多种系统方法播放音频文件"""
    try:
        file_path = str(file_path)
        print(f"[DEBUG] 尝试使用系统播放器播放: {file_path}")
        
        if os.name == 'nt':  # Windows系统
            import subprocess, ctypes
            
            # 规范化路径
            norm_path = os.path.normpath(file_path)
            print(f"[DEBUG] 规范化路径: {norm_path}")
            
            # 测试所有播放方案
            methods = [
                ('cmd.exe', lambda: subprocess.Popen(
                    f'start "" "{norm_path}"',
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )),
                ('PowerShell', lambda: subprocess.Popen(
                    ['powershell.exe', '-Command', f'Start-Process -FilePath "{norm_path}"'],
                    shell=False,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )),
                ('ShellExecuteW', lambda: ctypes.windll.shell32.ShellExecuteW(
                    None, "open", norm_path, None, None, 1
                )),
                ('os.startfile', lambda: os.startfile(norm_path))
            ]
            
            for method_name, play_func in methods:
                try:
                    play_func()
                    print(f"[DEBUG] ✓ 系统播放器启动成功 - {method_name}")
                    return True
                except Exception as e:
                    print(f"[DEBUG] {method_name}方案失败: {e}")
    except Exception as e:
        print(f"[DEBUG] 系统播放错误: {e}")
    
    return False

def main():
    print("=" * 60)
    print("Windows路径处理和编码修复测试")
    print("=" * 60)
    
    # 使用用户提供的英文音乐文件路径
    test_file = "C:/Users/Lizhuang/Pictures/wait you class down/wait you class down.wav"
    
    # 检查文件是否存在
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        print("请确认文件路径是否正确")
        return
    
    print(f"✅ 找到测试文件: {test_file}")
    print(f"文件路径长度: {len(test_file)} 字符")
    print(f"文件大小: {os.path.getsize(test_file)} 字节")
    
    # 测试路径编码
    print("\n🔍 测试路径编码处理:")
    try:
        # 测试UTF-8编码
        utf8_path = test_file.encode('utf-8').decode('utf-8')
        print(f"UTF-8 编码/解码: ✓ 成功")
        
        # 测试文件访问
        if os.access(test_file, os.R_OK):
            print(f"文件可读性: ✓ 可读")
        else:
            print(f"文件可读性: ✗ 不可读")
    except Exception as e:
        print(f"路径编码测试失败: {e}")
    
    # 测试1: 使用修复后的safe_playsound
    print("\n🎵 测试1: 使用修复后的safe_playsound")
    if playsound_available:
        success = safe_playsound(test_file)
        print(f"测试结果: {'✓ 成功' if success else '✗ 失败'}")
    else:
        print("跳过测试: playsound库不可用")
    
    # 测试2: 使用多方案系统播放器
    print("\n🎵 测试2: 使用多方案系统播放器")
    success = try_alternative_play(test_file)
    print(f"测试结果: {'✓ 成功' if success else '✗ 失败'}")
    
    # 测试3: 直接使用os.startfile（Windows特有）
    if os.name == 'nt':
        print("\n🎵 测试3: 直接使用os.startfile")
        try:
            os.startfile(test_file)
            print("测试结果: ✓ 成功")
        except Exception as e:
            print(f"测试结果: ✗ 失败 - {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("请检查是否能正常播放音乐")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        traceback.print_exc()
    finally:
        input("按回车键退出...")
