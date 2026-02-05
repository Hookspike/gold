import sys
from datetime import datetime
from sentiment_analysis import SentimentAnalyzer

def test_jin10_news():
    print("=" * 60)
    print("测试金十数据新闻抓取功能")
    print("=" * 60)
    
    analyzer = SentimentAnalyzer()
    
    print(f"\n开始获取新闻数据...")
    news = analyzer.fetch_gold_news(days_back=7)
    
    print(f"\n获取到 {len(news)} 条新闻")
    
    if news:
        print(f"\n新闻来源统计:")
        source_count = {}
        for item in news:
            source = item.get('source', '未知')
            source_count[source] = source_count.get(source, 0) + 1
        
        for source, count in source_count.items():
            print(f"  {source}: {count} 条")
        
        print(f"\n分析新闻情绪...")
        sentiment_df = analyzer.analyze_news_sentiment(news)
        
        if not sentiment_df.empty:
            print(f"\n情绪分析结果:")
            print(f"  总新闻数: {len(sentiment_df)}")
            print(f"  平均情绪分数: {sentiment_df['compound'].mean():.4f}")
            
            if 'impact' in sentiment_df.columns:
                impact_count = sentiment_df['impact'].value_counts()
                print(f"\n利好/利空统计:")
                for impact, count in impact_count.items():
                    print(f"  {impact}: {count} 条")
            
            print(f"\n最新新闻 (前5条):")
            for idx, row in sentiment_df.head(5).iterrows():
                print(f"\n  [{row['source']}] {row['publishedAt']}")
                print(f"  标题: {row['title'][:80]}...")
                if 'impact' in sentiment_df.columns:
                    print(f"  影响: {row['impact']}")
                print(f"  情绪分数: {row['compound']:.4f}")
            
            print(f"\n黄金相关关键词匹配统计:")
            gold_keywords = ['黄金', 'gold', 'XAU', '白银', '贵金属', '美联储', '加息', '通胀', 'CPI', '非农', '美元', '央行', '利率', '货币政策']
            keyword_matches = {}
            for keyword in gold_keywords:
                count = sum(1 for item in news if keyword in item.get('title', '') or keyword in item.get('content', ''))
                if count > 0:
                    keyword_matches[keyword] = count
            
            for keyword, count in sorted(keyword_matches.items(), key=lambda x: x[1], reverse=True):
                print(f"  {keyword}: {count} 次")
            
            print(f"\n✓ 测试成功！")
        else:
            print(f"\n✗ 情绪分析失败：返回空DataFrame")
    else:
        print(f"\n✗ 未获取到新闻数据")
        print(f"  可能原因：")
        print(f"  1. 金十数据网站访问受限")
        print(f"  2. 网络连接问题")
        print(f"  3. 网站结构变化导致抓取失败")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_jin10_news()
