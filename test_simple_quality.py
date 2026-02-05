import pandas as pd
import numpy as np
from datetime import datetime
from data_fetcher import GoldDataFetcher

print("开始测试数据质量验证功能...")

fetcher = GoldDataFetcher()

# 创建测试数据
dates = pd.date_range(end=datetime.now(), periods=100)
test_data = pd.DataFrame({
    'Date': dates,
    'Open': [2000 + i * 0.5 for i in range(100)],
    'High': [2010 + i * 0.5 for i in range(100)],
    'Low': [1990 + i * 0.5 for i in range(100)],
    'Close': [2000 + i * 0.5 for i in range(100)],
    'Volume': [100000 for _ in range(100)]
})

is_valid, quality_score, issues = fetcher.validate_data_quality(test_data)

print(f"数据质量验证结果:")
print(f"  是否有效: {is_valid}")
print(f"  质量分数: {quality_score}")
print(f"  发现问题: {issues}")

print("\n测试完成！")
