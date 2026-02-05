#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新闻获取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentiment_analysis import SentimentAnalyzer


def test_news_fetcher():
    """测试新闻获取功能"""
    print("=" * 60)
    print("测试新闻获取功能")
    print("=" * 60)
    
    analyzer = SentimentAnalyzer()
    
    # 测试获取新闻
    print("\n1. 测试获取黄金相关新闻...")
    news_articles = analyzer.fetch_gold_news(days_back=7)
    
    print(f"获取到的新闻数量: {len(news_articles)}")
    
    if news_articles:
        print("\n2. 测试新闻情绪分析...")
        sentiment_df = analyzer.analyze_news_sentiment(news_articles)
        
        print(f"情绪分析结果数量: {len(sentiment_df)}")
        
        if not sentiment_df.empty:
            print("\n3. 测试综合情绪计算...")
            overall_sentiment = analyzer.calculate_overall_sentiment(sentiment_df)
            
            print("综合情绪分析结果:")
            print(f"  综合情绪得分: {overall_sentiment['overall_sentiment']}")
            print(f"  情绪标签: {overall_sentiment['sentiment_label']}")
            print(f"  积极新闻数: {overall_sentiment['positive_count']}")
            print(f"  消极新闻数: {overall_sentiment['negative_count']}")
            print(f"  中性新闻数: {overall_sentiment['neutral_count']}")
            print(f"  平均情绪得分: {overall_sentiment['avg_compound']}")
            print(f"  加权情绪得分: {overall_sentiment['weighted_sentiment']}")
            
            print("\n4. 查看前5条新闻的情绪分析结果...")
            for i, row in sentiment_df.head(5).iterrows():
                print(f"\n新闻 {i+1}:")
                print(f"  标题: {row['title']}")
                print(f"  来源: {row['source']}")
                print(f"  发布时间: {row['publishedAt']}")
                print(f"  情绪得分: {row['compound']}")
                print(f"  积极情绪: {row['positive']}")
                print(f"  消极情绪: {row['negative']}")
                print(f"  中性情绪: {row['neutral']}")
                print(f"  影响: {row['impact']}")
        else:
            print("⚠️  情绪分析结果为空")
    else:
        print("⚠️  未获取到任何新闻")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_news_fetcher()
