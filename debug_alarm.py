import traceback
import sys

# 调试脚本来捕获完整的错误信息
try:
    import alarm_clock
    # 导入成功，现在运行主函数
    alarm_clock.main()
except Exception as e:
    print("\n=== 错误详情 ===")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}")
    print("\n错误堆栈:")
    traceback.print_exc()
    print("================\n")
    sys.exit(1)