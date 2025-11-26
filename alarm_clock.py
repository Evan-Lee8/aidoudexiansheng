import time
import datetime
import winsound
import sys
import traceback
from typing import Optional, Dict, Any

# 配置常量
APP_NAME = "专业闹钟程序"
APP_VERSION = "v1.0"
MAX_RETRIES = 3
DEFAULT_SOUND_DURATION = 3

# 颜色和样式常量（Windows命令提示符可能不支持所有颜色）
COLORS = {
    "success": "✅ ",
    "error": "❌ ",
    "warning": "⚠️ ",
    "info": "ℹ️  ",
    "question": "❓ "
}

# 错误码定义
ERROR_CODES = {
    "INVALID_TIME_FORMAT": 1001,
    "TIME_OUT_OF_RANGE": 1002,
    "USER_CANCELLED": 1003,
    "UNEXPECTED_ERROR": 1004,
    "AUDIO_PLAYBACK_ERROR": 1005,
    "TIME_INPUT_ERROR": 1006,
    "MODE_INPUT_ERROR": 1007,
    "FATAL_ERROR": 1008
}

class AlarmClockError(Exception):
    """闹钟程序自定义异常基类"""
    def __init__(self, code: int, message: Optional[str] = None, original_exception: Optional[Exception] = None):
        self.code = code
        self.message = message or f"错误码 {code}"
        self.original_exception = original_exception
        super().__init__(f"错误码 {code}: {self.message}")

def log_message(level: str, message: str, show_icon: bool = True) -> None:
    """统一的日志记录函数"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    icon = COLORS.get(level.lower(), "") if show_icon else ""
    
    if level.lower() == "error":
        prefix = f"[{timestamp}] ERROR: {icon}"
        print(f"{prefix}{message}", file=sys.stderr)
    else:
        prefix = f"[{timestamp}] {level.upper()}: {icon}"
        print(f"{prefix}{message}")

def get_valid_time_input(prompt="请输入时间（格式 HH:MM，如 07:30）：") -> Optional[str]:
    """
    获取并验证时间输入（已优化的错误处理）
    :param prompt: 提示信息
    :return: 格式化的时间字符串 "HH:MM" 或 None（用户选择退出）
    """
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            user_input = input(prompt).strip()
            
            # 支持退出命令
            if user_input.lower() in ['exit', 'quit', 'q', '退出', '取消']:
                log_message("info", "用户取消输入")
                return None
                
            # 验证格式
            if ':' not in user_input or len(user_input.split(':')) != 2:
                log_message("error", "格式错误！请使用 HH:MM 格式。")
                raise AlarmClockError(1001, "时间格式必须为 HH:MM")
                
            target_hour, target_minute = map(int, user_input.split(":"))
            
            # 验证范围
            if not (0 <= target_hour < 24 and 0 <= target_minute < 60):
                log_message("error", "时间无效！请确保小时在0-23之间，分钟在0-59之间。")
                raise AlarmClockError(1002, "时间值超出有效范围")
                
            # 格式化为标准格式
            formatted_time = f"{target_hour:02d}:{target_minute:02d}"
            log_message("success", f"成功设置时间: {formatted_time}", show_icon=False)
            return formatted_time
            
        except ValueError:
            log_message("error", "输入错误！请输入有效的数字。")
        except AlarmClockError:
            pass  # 错误已经记录，继续重试
        except Exception as e:
            log_message("error", f"发生意外错误: {str(e)}")
            traceback.print_exc(file=sys.stderr)
        
        retries += 1
        remaining = MAX_RETRIES - retries
        if remaining > 0:
            log_message("warning", f"还有 {remaining} 次重试机会")
    
    log_message("error", "达到最大重试次数，请重新启动程序")
    return None

def get_valid_boolean_input(prompt="请选择（y/n，默认n）：", default=False) -> Optional[bool]:
    """
    获取并验证布尔值输入（已优化的错误处理）
    :param prompt: 提示信息
    :param default: 默认值
    :return: True/False 或 None（用户选择退出）
    """
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            user_input = input(prompt).strip().lower()
            
            # 支持退出命令
            if user_input.lower() in ['exit', 'quit', 'q', '退出', '取消']:
                log_message("info", "用户取消输入")
                return None
                
            # 空输入使用默认值
            if not user_input:
                log_message("info", f"使用默认值: {'是' if default else '否'}", show_icon=False)
                return default
                
            # 有效输入
            if user_input in ['y', 'yes', '1', 'true']:
                log_message("success", "选择: 是", show_icon=False)
                return True
            elif user_input in ['n', 'no', '0', 'false']:
                log_message("success", "选择: 否", show_icon=False)
                return default
                
            # 无效输入
            retries += 1
            remaining = MAX_RETRIES - retries
            log_message("error", "无效的选择！请输入 y/n 或按Enter使用默认值。")
            if remaining > 0:
                log_message("warning", f"还有 {remaining} 次重试机会")
                
        except Exception as e:
            log_message("error", f"发生意外错误: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            retries += 1
    
    log_message("error", "达到最大重试次数，使用默认值")
    return default

def play_alarm_sound(duration=DEFAULT_SOUND_DURATION):
    """
    播放闹钟铃声
    :param duration: 铃声持续时间（秒）
    :raises AlarmClockError: 当音频播放失败时
    """
    log_message("info", f"🔔 正在响铃 {duration} 秒...", show_icon=False)
    
    try:
        # 使用Windows蜂鸣音
        frequency = 2500  # 频率(Hz)
        delay = 500  # 每次蜂鸣的持续时间(毫秒)
        pause = 100  # 蜂鸣间隔(毫秒)
        
        iterations = duration * 1000 // (delay + pause)
        
        # 显示响铃进度
        for i in range(iterations):
            try:
                winsound.Beep(frequency, delay)
                time.sleep(pause / 1000)
                
                # 显示响铃进度
                progress = (i + 1) / iterations
                progress_bar = update_progress_bar(progress, length=20)
                print(f"\r🔊 响铃中... {progress_bar}", end="", flush=True)
                
            except Exception as e:
                # 单个蜂鸣失败不应中断整个过程
                log_message("warning", f"蜂鸣音播放失败: {str(e)}", show_icon=False)
        
        print()  # 换行
        log_message("success", "铃声播放完成")
        
    except Exception as e:
        log_message("error", f"音频播放系统错误: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        raise AlarmClockError(1005, "铃声播放失败", original_exception=e)
    
    # 可选：使用音乐文件
    # playsound("alarm_music.mp3")  # 替换为你的音乐文件路径

def get_valid_time_input(prompt="请输入时间（格式 HH:MM，如 07:30）："):
    """获取并验证时间输入"""
    while True:
        user_input = input(prompt).strip()
        
        # 支持退出命令
        if user_input.lower() in ['exit', 'quit', 'q']:
            return None
            
        try:
            # 验证格式
            if ':' not in user_input or len(user_input.split(':')) != 2:
                print("❌ 格式错误！请使用 HH:MM 格式。")
                continue
                
            target_hour, target_minute = map(int, user_input.split(":"))
            
            # 验证范围
            if not (0 <= target_hour < 24 and 0 <= target_minute < 60):
                print("❌ 时间无效！请确保小时在0-23之间，分钟在0-59之间。")
                continue
                
            # 格式化为标准格式（如 7:30 -> 07:30）
            return f"{target_hour:02d}:{target_minute:02d}"
            
        except ValueError:
            print("❌ 输入错误！请输入有效的数字。")

def get_valid_boolean_input(prompt="请选择（y/n，默认n）：", default=False):
    """获取并验证布尔值输入"""
    while True:
        user_input = input(prompt).strip().lower()
        
        # 支持退出命令
        if user_input.lower() in ['exit', 'quit', 'q']:
            return None
            
        # 空输入使用默认值
        if not user_input:
            return default
            
        # 有效输入
        if user_input in ['y', 'yes', '1', 'true']:
            return True
        elif user_input in ['n', 'no', '0', 'false']:
            return default
            
        # 无效输入
        print("❌ 无效的选择！请输入 y/n 或按Enter使用默认值。")

def calculate_time_remaining(target_hour, target_minute):
    """计算距离目标时间的剩余时间"""
    now = datetime.datetime.now()
    current_time = now.replace(second=0, microsecond=0)
    
    # 创建今天的目标时间
    target_datetime = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # 如果目标时间已过，则设置为明天
    if target_datetime <= current_time:
        target_datetime += datetime.timedelta(days=1)
    
    # 计算剩余时间
    remaining = target_datetime - now
    total_seconds = remaining.total_seconds()
    
    # 转换为小时、分钟、秒
    hours, remainder = divmod(int(total_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return hours, minutes, seconds, total_seconds

def update_progress_bar(progress, length=30):
    """生成并返回进度条字符串"""
    filled_length = int(length * progress)
    bar = '█' * filled_length + '-' * (length - filled_length)
    percentage = progress * 100
    return f'[{bar}] {percentage:.1f}%'

def alarm(alarm_time: str, repeat: bool = False, sound_duration: int = DEFAULT_SOUND_DURATION) -> None:
    """
    闹钟主函数
    :param alarm_time: 闹钟时间，格式为 "HH:MM"（24小时制）
    :param repeat: 是否循环提醒（True=每小时重复，False=仅一次）
    :param sound_duration: 铃声持续时间（秒）
    """
    try:
        # 解析目标时间
        target_hour, target_minute = map(int, alarm_time.split(":"))
        
        mode_text = "循环模式" if repeat else "单次模式"
        log_message("success", f"闹钟已设置：{alarm_time} ({mode_text})")
        log_message("info", "提示：按 Ctrl+C 随时退出程序", show_icon=False)
        print("="*60)
        
        # 计算初始总等待时间（用于进度条）
        _, _, _, initial_total_seconds = calculate_time_remaining(target_hour, target_minute)
        
        log_message("info", "闹钟已启动，开始监控时间...", show_icon=False)
        
        while True:
            try:
                # 获取当前时间和剩余时间
                now = datetime.datetime.now()
                status_time = now.strftime("%H:%M:%S")
                hours, minutes, seconds, total_seconds = calculate_time_remaining(target_hour, target_minute)
                
                # 计算进度百分比（基于当前周期）
                if initial_total_seconds > 0:
                    progress = 1 - (total_seconds / initial_total_seconds)
                    progress = max(0, min(1, progress))  # 确保进度在0-1之间
                    progress_bar = update_progress_bar(progress)
                else:
                    progress_bar = update_progress_bar(1.0)
                
                # 生成剩余时间显示
                if hours > 0:
                    remaining_text = f"剩余 {hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    remaining_text = f"剩余 {minutes:02d}:{seconds:02d}"
                
                # 实时更新状态行
                status_line = f"\r⏱️  当前: {status_time} | 🎯 目标: {alarm_time} | {remaining_text} | {progress_bar}"
                print(status_line, end="", flush=True)
                
                # 检查是否到达目标时间
                current_hour, current_minute = now.hour, now.minute
                if current_hour == target_hour and current_minute == target_minute:
                    print("\n")
                    log_message("success", "🎉 闹钟时间到！")
                    
                    try:
                        play_alarm_sound(sound_duration)  # 播放铃声
                    except AlarmClockError as e:
                        log_message("error", f"铃声播放失败: {e.message}")
                        log_message("warning", "将继续执行闹钟程序...")
                    
                    if not repeat:
                        log_message("info", "✅ 闹钟已关闭")
                        break  # 单次模式：响铃后退出
                    else:
                        log_message("info", "🔄 循环模式：重置进度，下一次提醒将在1小时后")
                        print("="*60)
                        # 重置进度计算的总时间为3600秒
                        initial_total_seconds = 3600
                        # 等待1小时后再次提醒
                        # 每10秒更新一次进度显示
                        for i in range(360):
                            time.sleep(10)
                            # 更新进度条
                            progress = (i + 1) / 360
                            progress_bar = update_progress_bar(progress)
                            remaining_seconds = 3600 - (i + 1) * 10
                            rem_minutes, rem_seconds = divmod(remaining_seconds, 60)
                            status_line = f"\r🔄 等待下次提醒 | 剩余 {rem_minutes:02d}:{rem_seconds:02d} | {progress_bar}"
                            print(status_line, end="", flush=True)
                
                # 每1秒更新一次（更好的实时性）
                time.sleep(1)
                
            except AlarmClockError as e:
                log_message("error", f"闹钟运行错误: {e.message}")
                log_message("warning", "将尝试继续运行...")
                time.sleep(5)  # 暂停5秒后继续
            except Exception as e:
                log_message("error", f"发生意外错误: {str(e)}")
                traceback.print_exc(file=sys.stderr)
                log_message("warning", "将尝试继续运行...")
                time.sleep(5)  # 暂停5秒后继续
    
    except KeyboardInterrupt:
        print("\n")
        log_message("info", "⏹️  闹钟已手动关闭")
        log_message("info", "正在准备退出程序...", show_icon=False)
    except Exception as e:
        print("\n")
        log_message("error", f"严重错误: {str(e)}")
        traceback.print_exc(file=sys.stderr)

def show_welcome_screen():
    """显示专业的欢迎界面"""
    # 清屏（跨平台兼容的简单实现）
    print("\n" * 2)
    
    # 欢迎界面
    welcome_banner = """    ====================================================
    ||                                                ||
    ||              🎯  专业闹钟程序 v1.0              ||
    ||                                                ||
    ====================================================
    """
    
    print(welcome_banner)
    print("【功能介绍】")
    print("• 支持设置24小时制精确闹钟时间")
    print("• 提供单次提醒和每小时循环提醒模式")
    print("• Windows系统蜂鸣音提醒（可配置为音乐文件）")
    print("• 实时时间监控和状态显示")
    print("• 完善的错误处理和用户友好界面")
    print("\n" + "="*60)
    print("提示：按 Ctrl+C 随时退出程序")
    print("="*60 + "\n")

def main():
    """
    主程序入口
    """
    try:
        # 显示欢迎界面
        show_welcome_screen()
        
        log_message("info", "准备配置闹钟设置...", show_icon=False)
        
        # 获取闹钟时间
        print("\n请设置闹钟时间：")
        try:
            alarm_time = get_valid_time_input("请输入闹钟时间（格式 HH:MM，如 07:30）：")
            if alarm_time is None:
                log_message("info", "程序将退出", show_icon=False)
                return ERROR_CODES["USER_CANCELLED"]
        except AlarmClockError as e:
            log_message("error", f"时间设置失败: {e.message}")
            log_message("info", "程序将退出", show_icon=False)
            return e.code
        except KeyboardInterrupt:
            log_message("info", "\n用户取消操作，程序将退出", show_icon=False)
            return ERROR_CODES["USER_CANCELLED"]
        
        # 获取是否循环提醒
        print("\n请选择提醒模式：")
        try:
            repeat = get_valid_boolean_input("是否启用循环提醒（每小时重复）？", default=False)
            if repeat is None:
                log_message("info", "程序将退出", show_icon=False)
                return ERROR_CODES["USER_CANCELLED"]
        except AlarmClockError as e:
            log_message("error", f"提醒模式设置失败: {e.message}")
            log_message("info", "程序将退出", show_icon=False)
            return e.code
        except KeyboardInterrupt:
            log_message("info", "\n用户取消操作，程序将退出", show_icon=False)
            return ERROR_CODES["USER_CANCELLED"]
        
        # 获取铃声持续时间
        print("\n请设置铃声持续时间：")
        sound_duration = DEFAULT_SOUND_DURATION  # 默认值
        for attempt in range(MAX_RETRIES):
            try:
                user_input = input("请输入铃声持续时间（秒）[默认: 3]: ")
                if not user_input.strip():
                    # 使用默认值
                    log_message("info", f"使用默认铃声持续时间: {DEFAULT_SOUND_DURATION}秒", show_icon=False)
                    break
                    
                sound_duration = int(user_input)
                if sound_duration <= 0:
                    raise ValueError("铃声持续时间必须大于0秒")
                if sound_duration > 60:
                    log_message("warning", "铃声持续时间较长，建议不超过60秒")
                break  # 输入有效，退出循环
            except ValueError as e:
                remaining_attempts = MAX_RETRIES - attempt - 1
                log_message("error", f"无效的输入: {str(e)}")
                if remaining_attempts > 0:
                    log_message("info", f"请重试，还有{remaining_attempts}次机会", show_icon=False)
                else:
                    log_message("warning", f"超过最大重试次数，使用默认值: {DEFAULT_SOUND_DURATION}秒")
        
        log_message("success", "✅ 所有配置已完成，即将启动闹钟")
        print("="*60)
        
        # 启动闹钟
        alarm(alarm_time=alarm_time, repeat=repeat, sound_duration=sound_duration)
        
        # 程序结束
        print("="*60)
        log_message("success", "感谢使用闹钟程序！")
        return 0  # 成功退出
    
    except KeyboardInterrupt:
        print("\n")
        log_message("info", "用户中断操作，程序已终止")
        return ERROR_CODES["USER_CANCELLED"]
    except AlarmClockError as e:
        log_message("error", f"闹钟程序错误: {e.message}")
        return e.code
    except Exception as e:
        log_message("error", f"程序异常终止: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        return ERROR_CODES["UNEXPECTED_ERROR"]

# 添加全局退出处理函数
def handle_program_exit():
    """
    处理程序退出，确保资源正确释放
    """
    try:
        log_message("info", "正在清理资源...", show_icon=False)
        # 这里可以添加需要清理的资源，如关闭文件、停止服务等
        # 由于我们使用的是标准库，目前没有特殊需要清理的资源
        time.sleep(0.5)  # 给用户一点视觉反馈的时间
        log_message("info", "\n👋 程序已安全退出")
    except Exception as e:
        print(f"\n清理资源时出错: {str(e)}")

# 注册退出处理器（仅在支持的环境中）
import atexit
try:
    atexit.register(handle_program_exit)
except Exception:
    # 如果注册失败，静默忽略
    pass

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        # 最后的异常捕获，确保程序能够正常退出
        print(f"\n致命错误: {str(e)}")
        sys.exit(ERROR_CODES["FATAL_ERROR"])