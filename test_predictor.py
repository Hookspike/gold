from data_fetcher import GoldDataFetcher
from predictor import GoldPricePredictor
from sentiment_analysis import SentimentAnalyzer

fetcher = GoldDataFetcher()
predictor = GoldPricePredictor()
sentiment_analyzer = SentimentAnalyzer()

df = fetcher.get_latest_data()
print(f"获取到 {len(df)} 条价格数据")

if not df.empty:
    print(f"数据列: {df.columns.tolist()}")
    print(f"最后一条数据: {df.iloc[-1].to_dict()}")
    
    news = sentiment_analyzer.fetch_gold_news()
    sentiment_df = sentiment_analyzer.analyze_news_sentiment(news)
    sentiment_score = sentiment_df['compound'].mean() if not sentiment_df.empty else 0
    print(f"情绪分数: {sentiment_score}")
    
    train_result = predictor.train(df, sentiment_score)
    print(f"训练结果: {train_result}")
    
    if train_result.get('success'):
        predict_result = predictor.ensemble_predict(df, 7, sentiment_score)
        print(f"预测结果: {predict_result}")
        print(f"预测keys: {list(predict_result.get('predictions', {}).keys())}")
