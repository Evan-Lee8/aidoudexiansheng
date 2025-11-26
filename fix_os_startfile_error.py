#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解决os.startfile [WinError 15612] 错误的测试脚本
"""

import os
import sys
import subprocess
import time
import logging
import ctypes
from ctypes import wintypes

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_windows_error_message(error_code):
    """获取Windows错误代码对应的描述信息"""
    try:
        kernel32 = ctypes.WinDLL('kernel32')
        kernel32.FormatMessageW.restype = wintypes.DWORD
        buffer = ctypes.create_unicode_buffer(256)
        kernel32.FormatMessageW(
            0x1300,  # FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS
            None,
            error_code,
            0,  # 使用默认语言
            buffer,
            256,
            None
        )
        return buffer.value.strip()
    except Exception as e:
        return f"无法获取错误描述: {e}"

def register_wav_file_association():
    """尝试重新关联WAV文件与Windows Media Player"""
    print("\n🔧 尝试重新关联WAV文件...")
    try:
        # 获取Windows Media Player路径
        wmplayer_path = os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\Program Files (x86)'), 
                                     'Windows Media Player\wmplayer.exe')
        if not os.path.exists(wmplayer_path):
            wmplayer_path = os.path.join(os.environ.get('ProgramFiles', 'C:\Program Files'), 
                                         'Windows Media Player\wmplayer.exe')
        
        if not os.path.exists(wmplayer_path):
            print("❌ 未找到Windows Media Player")
            return False
        
        print(f"✅ 找到Windows Media Player: {wmplayer_path}")
        
        # 使用PowerShell设置文件关联（管理员权限可能需要）
        print("正在尝试设置文件关联...")
        ps_command = f'Start-Process -FilePath "{wmplayer_path}" -ArgumentList "\"{test_file}\"" -WindowStyle Hidden -Wait'
        subprocess.run(['powershell', '-Command', ps_command], shell=False)
        print("✅ 文件关联设置尝试完成")
        return True
    except Exception as e:
        print(f"❌ 文件关联设置失败: {e}")
        return False

def fix_os_startfile_error(file_path):
    """修复os.startfile错误，尝试多种播放方法"""
    print("=" * 70)
    print("解决 os.startfile [WinError 15612] 错误")
    print("=" * 70)
    
    # 验证文件存在
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    print(f"✅ 文件验证通过: {file_path}")
    
    # 方法1: 直接使用指定播放器打开
    print("\n🎵 方法1: 使用Windows Media Player播放")
    try:
        # 尝试找到Windows Media Player
        wmplayer_path = r"C:\Program Files\Windows Media Player\wmplayer.exe"
        if not os.path.exists(wmplayer_path):
            wmplayer_path = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"
        
        if os.path.exists(wmplayer_path):
            print(f"使用Windows Media Player: {wmplayer_path}")
            subprocess.Popen([wmplayer_path, file_path], shell=False)
            print("✓ Windows Media Player 已启动")
            time.sleep(2)
        else:
            print("❌ Windows Media Player 未找到")
    except Exception as e:
        print(f"❌ Windows Media Player 启动失败: {e}")
    
    # 方法2: 使用cmd /c start 命令
    print("\n🎵 方法2: 使用cmd /c start 命令")
    try:
        # 使用转义的双引号
        cmd = f'cmd /c start "" "{file_path}"'
        print(f"执行命令: {cmd}")
        subprocess.Popen(cmd, shell=True)
        print("✓ cmd /c start 命令已执行")
        time.sleep(2)
    except Exception as e:
        print(f"❌ cmd /c start 命令失败: {e}")
    
    # 方法3: 使用PowerShell播放
    print("\n🎵 方法3: 使用PowerShell播放")
    try:
        ps_command = f'Start-Process "{file_path}"'
        print(f"执行PowerShell: {ps_command}")
        subprocess.Popen(['powershell', '-Command', ps_command], shell=False)
        print("✓ PowerShell 命令已执行")
        time.sleep(2)
    except Exception as e:
        print(f"❌ PowerShell 命令失败: {e}")
    
    # 方法4: 使用ShellExecuteW API（高级）
    print("\n🎵 方法4: 使用ShellExecuteW API")
    try:
        # 定义ShellExecuteW函数
        shell32 = ctypes.windll.shell32
        ShellExecuteW = shell32.ShellExecuteW
        ShellExecuteW.argtypes = [wintypes.HWND, ctypes.c_wchar_p, ctypes.c_wchar_p, 
                                 ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int]
        ShellExecuteW.restype = wintypes.HINSTANCE
        
        # 执行ShellExecuteW
        result = ShellExecuteW(None, "open", file_path, None, None, 1)
        
        # 检查结果
        if result > 32:
            print("✓ ShellExecuteW API 调用成功")
        else:
            error_msg = get_windows_error_message(result)
            print(f"❌ ShellExecuteW API 调用失败: 错误码={result}, {error_msg}")
            
    except Exception as e:
        print(f"❌ ShellExecuteW API 调用异常: {e}")
    
    # 方法5: 尝试修复文件关联
    print("\n🔧 方法5: 尝试修复文件关联")
    register_wav_file_association()
    
    # 最后再次尝试os.startfile
    print("\n🎵 最后尝试: 重新运行os.startfile")
    try:
        print(f"执行 os.startfile('{file_path}')")
        os.startfile(file_path)
        print("✓ os.startfile 执行成功！")
    except Exception as e:
        print(f"❌ os.startfile 仍然失败: {e}")
        print("\n📋 错误详情:")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("修复尝试完成！请检查是否有音乐播放器成功启动并播放音乐")
    print("=" * 70)
    print("\n💡 可能的解决方案:")
    print("1. 右键点击.wav文件 -> 打开方式 -> 选择默认程序 -> 勾选'始终使用此应用打开.wav文件'")
    print("2. 确保Windows Media Player或其他音频播放器已正确安装")
    print("3. 运行Windows系统文件检查器: sfc /scannow")
    print("4. 重启Windows Explorer: 任务管理器 -> 结束任务'Windows Explorer' -> 文件 -> 运行新任务 -> 输入'explorer.exe'")
    return True

if __name__ == "__main__":
    # 测试文件路径
    test_file = "C:/Users/Lizhuang/Pictures/wait you class down/wait you class down.wav"
    
    try:
        fix_os_startfile_error(test_file)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("按回车键退出...")
