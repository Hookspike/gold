import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_fetcher import GoldDataFetcher

def test_data_quality_validation():
    print("=" * 60)
    print("测试数据质量验证功能")
    print("=" * 60)
    
    fetcher = GoldDataFetcher()
    
    # 测试1: 空数据
    print("\n测试1: 空数据")
    empty_df = pd.DataFrame()
    is_valid, quality_score, issues = fetcher.validate_data_quality(empty_df)
    print(f"结果: is_valid={is_valid}, quality_score={quality_score}")
    print(f"问题: {issues}")
    
    # 测试2: 正常数据
    print("\n测试2: 正常数据")
    dates = pd.date_range(end=datetime.now(), periods=100)
    normal_data = pd.DataFrame({
        'Date': dates,
        'Open': [2000 + i * 0.5 for i in range(100)],
        'High': [2010 + i * 0.5 for i in range(100)],
        'Low': [1990 + i * 0.5 for i in range(100)],
        'Close': [2000 + i * 0.5 for i in range(100)],
        'Volume': [100000 for _ in range(100)]
    })
    is_valid, quality_score, issues = fetcher.validate_data_quality(normal_data)
    print(f"结果: is_valid={is_valid}, quality_score={quality_score}")
    print(f"问题: {issues}")
    
    # 测试3: 包含缺失值的数据
    print("\n测试3: 包含缺失值的数据")
    missing_data = normal_data.copy()
    missing_data.loc[10:15, 'Close'] = np.nan
    missing_data.loc[20:22, 'High'] = np.nan
    is_valid, quality_score, issues = fetcher.validate_data_quality(missing_data)
    print(f"结果: is_valid={is_valid}, quality_score={quality_score}")
    print(f"问题: {issues}")
    
    # 测试4: 价格逻辑错误的数据
    print("\n测试4: 价格逻辑错误的数据")
    invalid_data = normal_data.copy()
    invalid_data.loc[5, 'High'] = 1900  # High < Open
    invalid_data.loc[10, 'Low'] = 2100   # Low > Close
    is_valid, quality_score, issues = fetcher.validate_data_quality(invalid_data)
    print(f"结果: is_valid={is_valid}, quality_score={quality_score}")
    print(f"问题: {issues}")
    
    # 测试5: 异常价格的数据
    print("\n测试5: 异常价格的数据")
    abnormal_data = normal_data.copy()
    abnormal_data.loc[5, 'Close'] = -100  # 负价格
    abnormal_data.loc[10, 'Close'] = 150000  # 异常高价
    is_valid, quality_score, issues = fetcher.validate_data_quality(abnormal_data)
    print(f"结果: is_valid={is_valid}, quality_score={quality_score}")
    print(f"问题: {issues}")
    
    # 测试6: 数据量不足
    print("\n测试6: 数据量不足")
    small_data = normal_data.head(5)
    is_valid, quality_score, issues = fetcher.validate_data_quality(small_data)
    print(f"结果: is_valid={is_valid}, quality_score={quality_score}")
    print(f"问题: {issues}")
    
    print("\n" + "=" * 60)
    print("数据质量验证功能测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_data_quality_validation()
