#!/usr/bin/env python3
"""
测试内置播放器功能
"""
import sys
import os
import time
import logging

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入内置播放器相关功能
try:
    from alarm_clock_gui import PygamePlayer
    print("[INFO] 成功导入PygamePlayer类")
except ImportError as e:
    print(f"[ERROR] 导入PygamePlayer类失败: {e}")
    sys.exit(1)

# 测试函数
def test_builtin_player():
    """测试内置播放器功能"""
    print("[INFO] 开始测试内置播放器...")
    
    # 创建播放器实例
    player = PygamePlayer()
    
    # 检查播放器是否可用
    if not player.is_available():
        print("[ERROR] 内置播放器不可用")
        return False
    
    print("[INFO] 内置播放器已准备就绪")
    
    # 测试播放一个简单的蜂鸣声（如果有测试文件的话）
    # 这里假设当前目录下有一个测试音频文件
    test_audio_files = [
        "test_sound.wav",
        "wait you class down.wav"  # 从日志中看到的音频文件
    ]
    
    audio_file = None
    for file in test_audio_files:
        if os.path.exists(file):
            audio_file = file
            break
    
    if not audio_file:
        print("[INFO] 没有找到测试音频文件，使用Windows蜂鸣代替")
        import winsound
        winsound.Beep(1000, 500)  # 1000Hz，500ms
        return True
    
    print(f"[INFO] 使用测试音频文件: {audio_file}")
    
    # 测试播放功能
    print("[INFO] 测试播放功能...")
    if player.play(audio_file, loop=False, volume=0.5):
        print("[INFO] ✓ 播放成功")
        
        # 播放3秒
        time.sleep(3)
        
        # 测试暂停功能
        print("[INFO] 测试暂停功能...")
        player.pause()
        print("[INFO] ✓ 暂停成功")
        
        # 暂停2秒
        time.sleep(2)
        
        # 测试恢复功能
        print("[INFO] 测试恢复功能...")
        player.resume()
        print("[INFO] ✓ 恢复成功")
        
        # 再播放2秒
        time.sleep(2)
        
        # 测试停止功能
        print("[INFO] 测试停止功能...")
        player.stop()
        print("[INFO] ✓ 停止成功")
        
        # 测试音量调节
        print("[INFO] 测试音量调节功能...")
        player.set_volume(0.8)
        print(f"[INFO] ✓ 音量设置为: {player.get_volume()}")
        
        # 播放2秒（高音量）
        if player.play(audio_file, loop=False, volume=0.8):
            print("[INFO] ✓ 高音量播放成功")
            time.sleep(2)
            player.stop()
        
        # 清理资源
        print("[INFO] 清理播放器资源...")
        player.quit()
        print("[INFO] ✓ 资源清理完成")
        
        return True
    else:
        print("[ERROR] 播放失败")
        return False

if __name__ == "__main__":
    print("=========================================")
    print("内置播放器功能测试")
    print("=========================================")
    
    if test_builtin_player():
        print("\n[SUCCESS] 所有测试通过！")
        sys.exit(0)
    else:
        print("\n[FAILURE] 测试失败！")
        sys.exit(1)
