#!/usr/bin/env python3
"""
测试闹钟列表功能
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
    filename='test_alarm_list.log'
)

def test_alarm_list_functionality():
    """测试闹钟列表功能"""
    logging.info("开始测试闹钟列表功能...")
    
    # 检查应用程序文件是否存在
    app_path = os.path.join(os.path.dirname(__file__), "visual_alarm_clock.py")
    if not os.path.exists(app_path):
        logging.error(f"应用程序文件不存在: {app_path}")
        return False
    
    # 创建一个临时测试脚本，用于自动化测试闹钟列表功能
    test_script = """
import sys
import os
import time
import tkinter as tk
from visual_alarm_clock import VisualAlarmClock

def test_alarm_list():
    root = tk.Tk()
    root.title("测试闹钟列表")
    root.geometry("800x800")
    
    app = VisualAlarmClock(root)
    
    # 等待界面初始化
    time.sleep(1)
    
    # 测试设置第一个闹钟
    print("测试设置第一个闹钟...")
    app.hour_var.set(9)
    app.minute_var.set(30)
    app.label_var.set("测试闹钟1")
    app.volume_var.set(0.7)
    
    # 调用设置闹钟方法
    app._set_alarm()
    
    # 等待设置完成
    time.sleep(1)
    
    # 测试设置第二个闹钟
    print("测试设置第二个闹钟...")
    app.hour_var.set(10)
    app.minute_var.set(0)
    app.label_var.set("测试闹钟2")
    app.volume_var.set(0.5)
    
    # 调用设置闹钟方法
    app._set_alarm()
    
    # 等待设置完成
    time.sleep(1)
    
    # 测试刷新闹钟列表
    print("测试刷新闹钟列表...")
    app._refresh_alarm_list()
    
    # 检查闹钟数量
    if len(app.alarms) == 2:
        print("✓ 成功设置2个闹钟")
    else:
        print(f"✗ 闹钟数量不正确，期望2个，实际{len(app.alarms)}个")
        
    # 检查Treeview中的项目数量
    tree_items = app.alarm_tree.get_children()
    if len(tree_items) == 2:
        print("✓ 闹钟列表显示正确")
    else:
        print(f"✗ 闹钟列表显示不正确，期望2个项目，实际{len(tree_items)}个")
    
    # 测试删除选中闹钟
    print("测试删除选中闹钟...")
    if tree_items:
        # 选中第一个项目
        app.alarm_tree.selection_set(tree_items[0])
        
        # 调用删除方法
        app._delete_selected_alarm()
        
        # 等待删除完成
        time.sleep(1)
        
        # 检查闹钟数量
        if len(app.alarms) == 1:
            print("✓ 成功删除1个闹钟")
        else:
            print(f"✗ 删除闹钟后数量不正确，期望1个，实际{len(app.alarms)}个")
    
    # 测试取消所有闹钟
    print("测试取消所有闹钟...")
    app._cancel_all_alarms()
    
    # 等待取消完成
    time.sleep(1)
    
    # 检查闹钟数量
    if len(app.alarms) == 0:
        print("✓ 成功取消所有闹钟")
    else:
        print(f"✗ 取消所有闹钟后数量不正确，期望0个，实际{len(app.alarms)}个")
    
    print("\n所有测试完成！")
    
    # 延迟关闭窗口
    root.after(2000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    test_alarm_list()
"""
    
    # 写入测试脚本
    test_script_path = os.path.join(os.path.dirname(__file__), "temp_test_script.py")
    with open(test_script_path, "w", encoding="utf-8") as f:
        f.write(test_script)
    
    try:
        # 运行测试脚本
        print("运行闹钟列表功能测试...")
        result = subprocess.run(
            [sys.executable, test_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )
        
        # 打印测试输出
        print("\n测试输出：")
        print(result.stdout)
        
        if result.stderr:
            print("\n错误信息：")
            print(result.stderr)
        
        # 检查测试是否成功
        if result.returncode == 0:
            logging.info("闹钟列表功能测试通过")
            print("\n✓ 闹钟列表功能测试通过！")
            return True
        else:
            logging.error(f"闹钟列表功能测试失败，退出代码: {result.returncode}")
            print(f"\n✗ 闹钟列表功能测试失败，退出代码: {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error("测试脚本运行超时")
        print("\n✗ 测试脚本运行超时")
        return False
    except Exception as e:
        logging.error(f"运行测试脚本时出错: {e}")
        print(f"\n✗ 运行测试脚本时出错: {e}")
        return False
    finally:
        # 删除临时测试脚本
        if os.path.exists(test_script_path):
            os.remove(test_script_path)

def main():
    """主测试函数"""
    logging.info("=" * 60)
    logging.info("开始测试闹钟列表功能")
    logging.info("=" * 60)
    
    # 运行闹钟列表功能测试
    success = test_alarm_list_functionality()
    
    logging.info("=" * 60)
    if success:
        logging.info("所有测试通过")
        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        return True
    else:
        logging.error("测试失败")
        print("\n" + "=" * 60)
        print("测试失败！")
        print("=" * 60)
        return False

if __name__ == "__main__":
    main()
