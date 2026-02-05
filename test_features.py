from data_fetcher import GoldDataFetcher
from predictor import GoldPricePredictor

fetcher = GoldDataFetcher()
predictor = GoldPricePredictor()

df = fetcher.get_latest_data()
print(f"原始数据: {len(df)} 条")
print(f"数据列: {df.columns.tolist()}")

sentiment_score = 0
feature_df = predictor.prepare_features(df, sentiment_score)
print(f"\n特征工程后: {len(feature_df)} 条")
print(f"特征列: {feature_df.columns.tolist() if not feature_df.empty else 'None'}")

if not feature_df.empty:
    print(f"\n最后一条特征数据:")
    print(feature_df.iloc[-1].to_dict())
