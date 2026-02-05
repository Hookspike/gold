#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试情绪分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("开始执行测试脚本...")

try:
    from sentiment_analysis import SentimentAnalyzer
    print("成功导入 SentimentAnalyzer")
except Exception as e:
    print(f"导入 SentimentAnalyzer 失败: {e}")
    sys.exit(1)

def test_sentiment_analysis():
    """测试情绪分析功能"""
    print("=" * 60)
    print("测试情绪分析功能")
    print("=" * 60)
    
    try:
        analyzer = SentimentAnalyzer()
        print("成功创建 SentimentAnalyzer 实例")
    except Exception as e:
        print(f"创建 SentimentAnalyzer 实例失败: {e}")
        return
    
    try:
        # 测试负面新闻
        negative_news = "黄金、有色金属板块大面积跌停 湖南黄金等多股跌停"
        print(f"\n测试负面新闻: {negative_news}")
        negative_score = analyzer.analyze_sentiment(negative_news)
        print(f"  VADER 得分: {negative_score['compound']}")
        print(f"  积极情绪: {negative_score['positive']}")
        print(f"  消极情绪: {negative_score['negative']}")
        print(f"  中性情绪: {negative_score['neutral']}")
        print(f"  TextBlob 极性: {negative_score['textblob_polarity']}")
    except Exception as e:
        print(f"测试负面新闻失败: {e}")
    
    try:
        # 测试正面新闻
        positive_news = "黄金价格大幅上涨，创历史新高"
        print(f"\n测试正面新闻: {positive_news}")
        positive_score = analyzer.analyze_sentiment(positive_news)
        print(f"  VADER 得分: {positive_score['compound']}")
        print(f"  积极情绪: {positive_score['positive']}")
        print(f"  消极情绪: {positive_score['negative']}")
        print(f"  中性情绪: {positive_score['neutral']}")
        print(f"  TextBlob 极性: {positive_score['textblob_polarity']}")
    except Exception as e:
        print(f"测试正面新闻失败: {e}")
    
    try:
        # 测试中性新闻
        neutral_news = "黄金市场保持稳定，交易量略有增加"
        print(f"\n测试中性新闻: {neutral_news}")
        neutral_score = analyzer.analyze_sentiment(neutral_news)
        print(f"  VADER 得分: {neutral_score['compound']}")
        print(f"  积极情绪: {neutral_score['positive']}")
        print(f"  消极情绪: {neutral_score['negative']}")
        print(f"  中性情绪: {neutral_score['neutral']}")
        print(f"  TextBlob 极性: {neutral_score['textblob_polarity']}")
    except Exception as e:
        print(f"测试中性新闻失败: {e}")
    
    # 测试实际获取的新闻
    print("\n" + "=" * 60)
    print("测试实际获取的新闻")
    print("=" * 60)
    
    try:
        news_articles = analyzer.fetch_gold_news(days_back=7)
        
        if news_articles:
            print(f"成功获取到 {len(news_articles)} 条新闻")
            for i, article in enumerate(news_articles[:5]):
                title = article.get('title', '')
                print(f"\n新闻 {i+1}: {title}")
                score = analyzer.analyze_sentiment(title)
                print(f"  VADER 得分: {score['compound']}")
                print(f"  积极情绪: {score['positive']}")
                print(f"  消极情绪: {score['negative']}")
                print(f"  中性情绪: {score['neutral']}")
        else:
            print("未获取到任何新闻")
    except Exception as e:
        print(f"测试实际获取的新闻失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_sentiment_analysis()
    except Exception as e:
        print(f"执行测试脚本失败: {e}")

