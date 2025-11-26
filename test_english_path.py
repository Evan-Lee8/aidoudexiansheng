#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证英文路径音乐文件播放功能
"""

import os
import sys
import logging
import traceback
import subprocess
import time

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_english_path_play():
    """测试英文路径的音乐文件播放"""
    print("=" * 60)
    print("英文路径音乐文件播放测试")
    print("=" * 60)
    
    # 用户提供的英文音乐文件路径
    test_file = "C:/Users/Lizhuang/Pictures/wait you class down/wait you class down.wav"
    
    # 检查文件是否存在
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        print("请确认文件路径是否正确，或文件是否已创建")
        return False
    
    print(f"✅ 找到测试文件: {test_file}")
    print(f"文件路径长度: {len(test_file)} 字符")
    print(f"文件大小: {os.path.getsize(test_file)} 字节")
    
    # 路径验证
    print("\n🔍 路径验证:")
    try:
        # 规范化路径
        norm_path = os.path.normpath(test_file)
        print(f"规范化路径: {norm_path}")
        
        # 检查文件可读性
        if os.access(norm_path, os.R_OK):
            print("文件可读性: ✓ 可读")
        else:
            print("文件可读性: ✗ 不可读")
            return False
    except Exception as e:
        print(f"路径验证失败: {e}")
        return False
    
    # 测试使用cmd.exe播放（Windows系统）
    if os.name == 'nt':
        print("\n🎵 测试使用cmd.exe播放:")
        try:
            print(f"正在尝试播放: {norm_path}")
            subprocess.Popen(
                f'start "" "{norm_path}"',
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("✓ cmd.exe 播放命令已发送")
            print("请检查音乐是否正常播放")
            time.sleep(3)  # 等待播放开始
        except Exception as e:
            print(f"✗ cmd.exe 播放失败: {e}")
            return False
    
    # 测试使用os.startfile（Windows系统）
    if os.name == 'nt':
        print("\n🎵 测试使用os.startfile播放:")
        try:
            print(f"正在尝试播放: {norm_path}")
            os.startfile(norm_path)
            print("✓ os.startfile 播放命令已发送")
            print("请检查音乐是否正常播放")
            time.sleep(3)  # 等待播放开始
        except Exception as e:
            print(f"✗ os.startfile 播放失败: {e}")
    
    print("\n" + "=" * 60)
    print("英文路径测试完成！")
    print("如果音乐能正常播放，说明路径问题已解决")
    print("=" * 60)
    return True

def main():
    try:
        success = test_english_path_play()
        print(f"\n测试结果: {'成功' if success else '失败'}")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        traceback.print_exc()
    finally:
        input("按回车键退出...")

if __name__ == "__main__":
    main()
