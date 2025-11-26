import ast
import sys

# 简单的语法检查脚本
filename = 'alarm_clock.py'
try:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 尝试解析代码以检查语法错误
    ast.parse(content)
    print(f"✅ 文件 '{filename}' 的语法正确")
    
except SyntaxError as e:
    print(f"❌ 语法错误在 {filename}:{e.lineno}:{e.offset}")
    print(f"  {e.text}")
    print(f"  {'^' * (e.offset - 1)} 这里有错误")
    print(f"  错误信息: {e.msg}")
except Exception as e:
    print(f"❌ 读取或解析文件时出错: {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    print("\n语法检查完成")