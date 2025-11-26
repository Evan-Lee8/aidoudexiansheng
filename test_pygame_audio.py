import pygame
import numpy as np
import time

# 初始化Pygame音频
pygame.mixer.init()

print("测试Pygame音频生成功能...")

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

try:
    # 创建Pygame Sound对象
    sound = pygame.mixer.Sound(buffer=sound_data.tobytes(), channels=1, frequency=sample_rate, size=-16)
    
    # 播放铃声
    print("播放测试铃声...")
    sound.set_volume(0.5)
    sound.play()
    
    # 等待播放完成
    time.sleep(duration * 2)
    
    print("测试完成！Pygame音频功能正常工作。")
except Exception as e:
    print(f"测试失败: {e}")
finally:
    # 清理资源
    pygame.mixer.quit()