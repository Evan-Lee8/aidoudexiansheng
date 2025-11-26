import ast
try:
    with open('alarm_clock.py', 'r') as f:
        ast.parse(f.read())
    print("语法检查通过！")
except SyntaxError as e:
    print(f"语法错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")