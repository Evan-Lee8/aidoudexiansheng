import logging
import os

# 配置日志以便查看输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 测试playsound库导入
print("开始测试playsound库导入...")
playsound_available = False
playsound_func = None

try:
    from playsound import playsound as playsound_func
    playsound_available = True
    print("✓ 成功导入playsound库")
    logging.info("成功导入playsound库")
except ImportError:
    print("✗ playsound库未安装")
    logging.warning("playsound库未安装")
except Exception as e:
    print(f"✗ 导入playsound库时发生错误: {e}")
    logging.error(f"导入playsound库时发生错误: {e}")

# 打印playsound可用性状态
print(f"playsound_available = {playsound_available}")
print(f"playsound_func = {playsound_func}")

print("\n测试完成")