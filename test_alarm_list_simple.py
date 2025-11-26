#!/usr/bin/env python3
"""
简单测试闹钟列表功能
"""
import sys
import os
import time
import logging
import tkinter as tk

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='test_alarm_list_simple.log'
)

class TestAlarmList:
    """测试闹钟列表功能的类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("测试闹钟列表")
        self.root.geometry("800x800")
        
        # 导入VisualAlarmClock类
        from visual_alarm_clock import VisualAlarmClock
        self.app = VisualAlarmClock(self.root)
        
        # 测试结果
        self.results = []
    
    def run_tests(self):
        """运行所有测试"""
        print("开始测试闹钟列表功能...")
        
        # 测试1: 设置第一个闹钟
        self.test_set_first_alarm()
        
        # 测试2: 设置第二个闹钟
        self.test_set_second_alarm()
        
        # 测试3: 检查闹钟数量
        self.test_alarm_count()
        
        # 测试4: 刷新闹钟列表
        self.test_refresh_list()
        
        # 测试5: 删除一个闹钟
        self.test_delete_alarm()
        
        # 测试6: 检查剩余闹钟数量
        self.test_remaining_alarm_count()
        
        # 显示测试结果
        self.show_results()
        
        # 关闭窗口
        self.root.after(2000, self.root.destroy)
        
        # 运行主循环
        self.root.mainloop()
        
        # 返回测试是否全部通过
        return all(result["success"] for result in self.results)
    
    def test_set_first_alarm(self):
        """测试设置第一个闹钟"""
        print("测试设置第一个闹钟...")
        
        try:
            self.app.hour_var.set(9)
            self.app.minute_var.set(30)
            self.app.label_var.set("测试闹钟1")
            self.app.volume_var.set(0.7)
            
            # 调用设置闹钟方法
            self.app._set_alarm()
            
            # 等待设置完成
            time.sleep(1)
            
            self.results.append({"name": "设置第一个闹钟", "success": True})
            print("✓ 成功设置第一个闹钟")
            
        except Exception as e:
            self.results.append({"name": "设置第一个闹钟", "success": False, "error": str(e)})
            print(f"✗ 设置第一个闹钟失败: {e}")
    
    def test_set_second_alarm(self):
        """测试设置第二个闹钟"""
        print("测试设置第二个闹钟...")
        
        try:
            self.app.hour_var.set(10)
            self.app.minute_var.set(0)
            self.app.label_var.set("测试闹钟2")
            self.app.volume_var.set(0.5)
            
            # 调用设置闹钟方法
            self.app._set_alarm()
            
            # 等待设置完成
            time.sleep(1)
            
            self.results.append({"name": "设置第二个闹钟", "success": True})
            print("✓ 成功设置第二个闹钟")
            
        except Exception as e:
            self.results.append({"name": "设置第二个闹钟", "success": False, "error": str(e)})
            print(f"✗ 设置第二个闹钟失败: {e}")
    
    def test_alarm_count(self):
        """测试闹钟数量"""
        print("测试闹钟数量...")
        
        try:
            if len(self.app.alarms) == 2:
                self.results.append({"name": "检查闹钟数量", "success": True})
                print("✓ 闹钟数量正确 (2个)")
            else:
                self.results.append({"name": "检查闹钟数量", "success": False, "error": f"期望2个闹钟，实际{len(self.app.alarms)}个"})
                print(f"✗ 闹钟数量不正确，期望2个，实际{len(self.app.alarms)}个")
                
        except Exception as e:
            self.results.append({"name": "检查闹钟数量", "success": False, "error": str(e)})
            print(f"✗ 检查闹钟数量失败: {e}")
    
    def test_refresh_list(self):
        """测试刷新闹钟列表"""
        print("测试刷新闹钟列表...")
        
        try:
            self.app._refresh_alarm_list()
            
            # 检查Treeview中的项目数量
            tree_items = self.app.alarm_tree.get_children()
            if len(tree_items) == 2:
                self.results.append({"name": "刷新闹钟列表", "success": True})
                print("✓ 闹钟列表显示正确 (2个项目)")
            else:
                self.results.append({"name": "刷新闹钟列表", "success": False, "error": f"期望2个列表项目，实际{len(tree_items)}个"})
                print(f"✗ 闹钟列表显示不正确，期望2个项目，实际{len(tree_items)}个")
                
        except Exception as e:
            self.results.append({"name": "刷新闹钟列表", "success": False, "error": str(e)})
            print(f"✗ 刷新闹钟列表失败: {e}")
    
    def test_delete_alarm(self):
        """测试删除闹钟"""
        print("测试删除闹钟...")
        
        try:
            tree_items = self.app.alarm_tree.get_children()
            if tree_items:
                # 选中第一个项目
                self.app.alarm_tree.selection_set(tree_items[0])
                
                # 调用删除方法
                self.app._delete_selected_alarm()
                
                # 等待删除完成
                time.sleep(1)
                
                self.results.append({"name": "删除选中闹钟", "success": True})
                print("✓ 成功删除选中的闹钟")
            else:
                self.results.append({"name": "删除选中闹钟", "success": False, "error": "没有可删除的闹钟项目"})
                print("✗ 删除闹钟失败: 没有可删除的闹钟项目")
                
        except Exception as e:
            self.results.append({"name": "删除选中闹钟", "success": False, "error": str(e)})
            print(f"✗ 删除闹钟失败: {e}")
    
    def test_remaining_alarm_count(self):
        """测试剩余闹钟数量"""
        print("测试剩余闹钟数量...")
        
        try:
            if len(self.app.alarms) == 1:
                self.results.append({"name": "检查剩余闹钟数量", "success": True})
                print("✓ 剩余闹钟数量正确 (1个)")
            else:
                self.results.append({"name": "检查剩余闹钟数量", "success": False, "error": f"期望1个闹钟，实际{len(self.app.alarms)}个"})
                print(f"✗ 剩余闹钟数量不正确，期望1个，实际{len(self.app.alarms)}个")
                
        except Exception as e:
            self.results.append({"name": "检查剩余闹钟数量", "success": False, "error": str(e)})
            print(f"✗ 检查剩余闹钟数量失败: {e}")
    
    def show_results(self):
        """显示测试结果"""
        print("\n" + "=" * 50)
        print("闹钟列表功能测试结果")
        print("=" * 50)
        
        for result in self.results:
            status = "✓ 通过" if result["success"] else "✗ 失败"
            print(f"{result['name']}: {status}")
            if not result["success"] and "error" in result:
                print(f"  错误: {result['error']}")
        
        print("=" * 50)
        
        if all(result["success"] for result in self.results):
            print("\n✓ 所有测试通过！")
        else:
            print("\n✗ 部分测试失败！")

def main():
    """主测试函数"""
    logging.info("=" * 60)
    logging.info("开始测试闹钟列表功能")
    logging.info("=" * 60)
    
    # 创建测试实例
    tester = TestAlarmList()
    
    # 运行测试
    success = tester.run_tests()
    
    logging.info("=" * 60)
    if success:
        logging.info("所有测试通过")
        print("\n所有测试通过！")
    else:
        logging.error("部分测试失败")
        print("\n部分测试失败！")
    
    return success

if __name__ == "__main__":
    main()
