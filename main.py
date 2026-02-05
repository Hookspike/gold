#!/usr/bin/env python3

from data_fetcher import GoldDataFetcher
from technical_analysis import TechnicalAnalyzer
from sentiment_analysis import SentimentAnalyzer
from predictor import GoldPricePredictor
from config import Config
import pandas as pd
from datetime import datetime

def main():
    print("=" * 60)
    print("🥇 黄金价格预测走势系统")
    print("=" * 60)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"数据源: {Config.DATA_SOURCE}")
    print(f"股票代码: {Config.GOLD_TICKER}")
    print("=" * 60)
    print()
    
    print("📊 正在获取黄金价格数据...")
    fetcher = GoldDataFetcher()
    df = fetcher.get_latest_data()
    
    if df.empty:
        print("❌ 无法获取数据，请检查网络连接或配置")
        return
    
    print(f"✅ 成功获取 {len(df)} 条历史数据")
    print(f"   数据范围: {df['Date'].min().strftime('%Y-%m-%d')} 至 {df['Date'].max().strftime('%Y-%m-%d')}")
    print()
    
    print("💰 当前价格信息:")
    realtime = fetcher.fetch_realtime_price()
    if realtime:
        print(f"   当前价格: ${realtime.get('price', 0):.2f}")
        print(f"   日内变化: {realtime.get('change_percent', 0):+.2f}%")
        print(f"   今日最高: ${realtime.get('high', 0):.2f}")
        print(f"   今日最低: ${realtime.get('low', 0):.2f}")
    print()
    
    print("🔬 正在计算技术指标...")
    tech_analyzer = TechnicalAnalyzer()
    df_tech = tech_analyzer.calculate_all_indicators(df)
    print("✅ 技术指标计算完成")
    print()
    
    print("📈 技术分析结果:")
    latest = df_tech.iloc[-1]
    print(f"   RSI: {latest.get('RSI', 0):.2f}")
    print(f"   MACD: {latest.get('MACD', 0):.4f}")
    print(f"   SMA 20: ${latest.get('SMA_20', 0):.2f}")
    print(f"   SMA 50: ${latest.get('SMA_50', 0):.2f}")
    print(f"   综合信号: {latest.get('Overall_Signal', 0):.2f}")
    print()
    
    support_resistance = tech_analyzer.get_support_resistance(df_tech)
    print("🎯 支撑位和阻力位:")
    print(f"   支撑位: {[f'${x:.2f}' for x in support_resistance.get('support', [])]}")
    print(f"   阻力位: {[f'${x:.2f}' for x in support_resistance.get('resistance', [])]}")
    print()
    
    print("📰 正在分析市场情绪...")
    sentiment_analyzer = SentimentAnalyzer()
    news = sentiment_analyzer.fetch_gold_news()
    sentiment_df = sentiment_analyzer.analyze_news_sentiment(news)
    
    if not sentiment_df.empty:
        print(f"✅ 成功分析 {len(sentiment_df)} 条新闻")
        overall = sentiment_analyzer.calculate_overall_sentiment(sentiment_df)
        print()
        print("😊 市场情绪分析结果:")
        print(f"   情绪指数: {overall['avg_compound']:.3f}")
        print(f"   情绪标签: {overall['sentiment_label']}")
        print(f"   积极新闻: {overall['positive_count']} 条")
        print(f"   消极新闻: {overall['negative_count']} 条")
        print(f"   中性新闻: {overall['neutral_count']} 条")
        print()
        
        fear_greed = sentiment_analyzer.analyze_market_fear_greed(df)
        print("😨 恐惧贪婪指数:")
        print(f"   指数: {fear_greed['index']}")
        print(f"   状态: {fear_greed['label']}")
        print()
    else:
        print("⚠️  暂无情绪数据")
        print()
    
    print("🔮 正在训练预测模型...")
    predictor = GoldPricePredictor()
    
    sentiment_score = sentiment_df['compound'].mean() if not sentiment_df.empty else 0
    train_result = predictor.train(df, sentiment_score)
    
    if train_result['success']:
        print("✅ 模型训练完成")
        print(f"   训练样本数: {train_result['training_samples']}")
        print(f"   特征数量: {train_result['feature_count']}")
        print()
        
        print("📊 模型性能:")
        for model_name, metrics in train_result['results'].items():
            if 'error' not in metrics:
                print(f"   {model_name}:")
                print(f"      MAE: {metrics['mae']:.4f}")
                print(f"      RMSE: {metrics['rmse']:.4f}")
                print(f"      R²: {metrics['r2']:.4f}")
        print()
        
        print("🎯 价格预测:")
        predictions = predictor.ensemble_predict(df, Config.PREDICTION_DAYS, sentiment_score)
        
        if predictions['success']:
            print(f"   当前价格: ${predictions['current_price']:.2f}")
            print(f"   预测趋势: {predictions['trend']}")
            print()
            print("   未来7天预测:")
            for day_key, pred in predictions['predictions'].items():
                print(f"      {day_key}: ${pred['predicted_price']:.2f} "
                      f"({pred['price_change_percent']:+.2f}%)")
            print()
            
            confidence = predictor.calculate_confidence_interval(predictions)
            if confidence:
                print("   95% 置信区间:")
                for day_key, conf in confidence.items():
                    print(f"      {day_key}: ${conf['lower_bound']:.2f} - ${conf['upper_bound']:.2f}")
            print()
            
            feature_importance = predictor.get_feature_importance()
            if feature_importance:
                print("🔍 重要特征 (前5):")
                for i, (feature, importance) in enumerate(list(feature_importance.items())[:5], 1):
                    print(f"   {i}. {feature}: {importance:.4f}")
        else:
            print(f"❌ 预测失败: {predictions.get('error', '未知错误')}")
    else:
        print(f"❌ 模型训练失败: {train_result.get('error', '未知错误')}")
    
    print()
    print("=" * 60)
    print("分析完成！")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
