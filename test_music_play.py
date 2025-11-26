import os
import sys
import time

# 配置基本的打印信息
print("开始测试音乐播放功能...")

# 尝试导入playsound库
playsound_available = False
playsound_func = None

try:
    from playsound import playsound as playsound_func
    playsound_available = True
    print(f"✓ 成功导入playsound库: {playsound_func}")
except ImportError:
    print("✗ playsound库未安装")
except Exception as e:
    print(f"✗ 导入playsound库时发生错误: {e}")

# 定义安全的playsound包装函数（简化版）
def safe_playsound(file_path):
    """安全播放音频文件"""
    if not playsound_available or playsound_func is None:
        print("playsound库不可用")
        return False
    
    file_path = str(file_path)
    print(f"尝试播放: {file_path}")
    
    try:
        playsound_func(file_path)
        print("✓ playsound播放成功")
        return True
    except Exception as e:
        print(f"✗ playsound播放失败: {e}")
        return False

# 测试系统播放器方法
def test_system_player(file_path):
    """测试使用系统播放器播放"""
    file_path = str(file_path)
    print(f"尝试使用系统播放器播放: {file_path}")
    
    try:
        if os.name == 'nt':  # Windows系统
            # 测试改进的subprocess方法
            import subprocess
            print("使用cmd.exe /c start...")
            proc = subprocess.Popen(
                ['cmd.exe', '/c', 'start', '', file_path],
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # 给播放器启动时间
            print("✓ 系统播放器命令已发送")
            return True
        else:
            print("非Windows系统，跳过测试")
            return False
    except Exception as e:
        print(f"✗ 系统播放器失败: {e}")
        return False

# 测试主函数
def main():
    # 使用用户提供的英文音乐文件路径
    test_file = "C:/Users/Lizhuang/Pictures/wait you class down/wait you class down.wav"
    
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return
    
    print(f"找到测试文件: {test_file}")
    print("=" * 50)
    
    # 测试1: 使用playsound播放
    print("测试1: playsound播放")
    safe_playsound(test_file)
    print("=" * 50)
    time.sleep(3)  # 等待播放
    
    # 测试2: 使用系统播放器播放
    print("测试2: 系统播放器播放")
    test_system_player(test_file)
    print("=" * 50)
    
    print("测试完成！请检查播放效果。")

if __name__ == "__main__":
    main()
