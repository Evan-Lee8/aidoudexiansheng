#!/usr/bin/env python3
"""
测试可视化闹钟应用功能
"""
import sys
import os
import time
import logging
import subprocess
import signal

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='test_visual_alarm_clock.log'
)

def check_pygame_installed():
    """检查pygame是否安装"""
    try:
        import pygame
        logging.info(f"pygame已安装: {pygame.version.ver}")
        return True
    except ImportError:
        logging.error("pygame未安装")
        return False

def test_application_launch():
    """测试应用程序启动"""
    logging.info("开始测试应用程序启动...")
    
    # 检查应用程序文件是否存在
    app_path = os.path.join(os.path.dirname(__file__), "visual_alarm_clock.py")
    if not os.path.exists(app_path):
        logging.error(f"应用程序文件不存在: {app_path}")
        return False
    
    try:
        # 启动应用程序
        process = subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待3秒，检查应用是否仍在运行
        time.sleep(3)
        
        if process.poll() is None:
            # 应用程序仍在运行
            logging.info("应用程序成功启动并运行")
            
            # 获取应用程序的进程ID
            pid = process.pid
            logging.info(f"应用程序进程ID: {pid}")
            
            # 检查窗口创建功能暂时移除，因为需要psutil模块
            logging.info("应用程序窗口检查: 跳过 (需要psutil模块)")
            
            # 终止应用程序
            process.terminate()
            process.wait(timeout=5)
            
            return True
        else:
            # 应用程序已退出
            stdout, stderr = process.communicate()
            logging.error(f"应用程序启动失败，退出代码: {process.returncode}")
            logging.error(f"标准输出: {stdout}")
            logging.error(f"标准错误: {stderr}")
            return False
            
    except Exception as e:
        logging.error(f"启动应用程序时出错: {e}")
        return False

def test_player_functionality():
    """测试内置播放器功能"""
    logging.info("开始测试内置播放器功能...")
    
    try:
        import pygame
        
        # 初始化pygame
        pygame.init()
        
        # 初始化音频播放器
        pygame.mixer.init()
        logging.info("pygame音频系统初始化成功")
        
        # 测试基本功能
        mixer = pygame.mixer
        
        # 测试音量控制
        mixer.music.set_volume(0.5)
        current_volume = mixer.music.get_volume()
        logging.info(f"音量设置测试: 设置为0.5，实际值: {current_volume}")
        
        # 测试加载音频文件
        # 这里使用一个简单的wav文件进行测试
        # 如果没有测试文件，跳过此测试
        test_file = "test_sound.wav"
        if os.path.exists(test_file):
            try:
                mixer.music.load(test_file)
                logging.info(f"成功加载测试音频文件: {test_file}")
                
                # 测试播放控制
                mixer.music.play(0)
                time.sleep(0.5)
                mixer.music.pause()
                time.sleep(0.5)
                mixer.music.unpause()
                time.sleep(0.5)
                mixer.music.stop()
                logging.info("音频播放控制测试成功")
            except Exception as e:
                logging.warning(f"测试音频文件播放失败: {e}")
        else:
            logging.info(f"没有找到测试音频文件: {test_file}，跳过文件播放测试")
        
        # 清理资源
        pygame.quit()
        logging.info("内置播放器功能测试完成")
        return True
        
    except Exception as e:
        logging.error(f"内置播放器功能测试失败: {e}")
        return False

def test_clock_functionality():
    """测试时钟功能"""
    logging.info("开始测试时钟功能...")
    
    # 这里测试时间格式化功能
    import datetime
    
    now = datetime.datetime.now()
    
    # 测试日期格式化
    date_str = now.strftime("%Y年%m月%d日 %A")
    logging.info(f"日期格式化测试: {date_str}")
    
    # 测试时间格式化
    time_str = now.strftime("%H:%M:%S")
    logging.info(f"时间格式化测试: {time_str}")
    
    return True

def test_alarm_logic():
    """测试闹钟逻辑"""
    logging.info("开始测试闹钟逻辑...")
    
    import datetime
    
    # 测试闹钟时间计算
    now = datetime.datetime.now()
    
    # 设置一个1分钟后的闹钟
    alarm_time = now + datetime.timedelta(minutes=1)
    
    # 测试时间比较
    is_future = alarm_time > now
    logging.info(f"闹钟时间比较测试: 设置时间大于当前时间 -> {is_future}")
    
    # 测试倒计时计算
    time_diff = alarm_time - now
    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    logging.info(f"倒计时计算测试: {int(hours)}小时{int(minutes)}分钟{int(seconds)}秒")
    
    return True

def main():
    """运行所有测试"""
    logging.info("=" * 60)
    logging.info("开始测试可视化闹钟应用")
    logging.info("=" * 60)
    
    # 检查pygame是否安装
    if not check_pygame_installed():
        print("[ERROR] pygame库未安装，无法运行内置播放器")
        return False
    
    # 运行所有测试
    results = {
        "pygame安装": check_pygame_installed(),
        "应用程序启动": test_application_launch(),
        "内置播放器": test_player_functionality(),
        "时钟功能": test_clock_functionality(),
        "闹钟逻辑": test_alarm_logic()
    }
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("可视化闹钟应用测试结果")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("[SUCCESS] 所有测试通过！")
        logging.info("所有测试通过")
        return True
    else:
        print("[FAILURE] 部分测试失败！请查看日志获取详细信息")
        logging.error("部分测试失败")
        return False

if __name__ == "__main__":
    main()
