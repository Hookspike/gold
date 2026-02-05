import sys
print("开始测试核心功能...")

try:
    from data_fetcher import GoldDataFetcher
    print("✓ 成功导入 GoldDataFetcher")
    
    fetcher = GoldDataFetcher()
    print("✓ 成功创建 GoldDataFetcher 实例")
    
    # 测试数据质量验证
    import pandas as pd
    from datetime import datetime
    
    test_data = pd.DataFrame({
        'Date': [datetime.now()],
        'Open': [2000.0],
        'High': [2010.0],
        'Low': [1990.0],
        'Close': [2000.0],
        'Volume': [100000]
    })
    
    is_valid, quality_score, issues = fetcher.validate_data_quality(test_data)
    print(f"✓ 数据质量验证功能正常")
    print(f"  质量分数: {quality_score}")
    
    print("\n所有核心功能测试通过！")
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
