from sentiment_analysis import SentimentAnalyzer
import pandas as pd

analyzer = SentimentAnalyzer()
news = analyzer.fetch_gold_news(days_back=7)
print(f'获取到 {len(news)} 条新闻\n')

if news:
    print('新闻详情:')
    for i, item in enumerate(news[:5], 1):
        print(f'\n{i}. [{item["source"]}] {item["publishedAt"]}')
        print(f'   标题: {item["title"]}')
        print(f'   内容: {item["content"][:150]}...' if len(item["content"]) > 150 else f'   内容: {item["content"]}')

print('\n' + '='*60)
sentiment_df = analyzer.analyze_news_sentiment(news)
print(f'\n情绪分析结果:')
print(f'总新闻数: {len(sentiment_df)}')
print(f'平均情绪分数: {sentiment_df["compound"].mean():.4f}')
print(f'最大情绪分数: {sentiment_df["compound"].max():.4f}')
print(f'最小情绪分数: {sentiment_df["compound"].min():.4f}')

if 'impact' in sentiment_df.columns:
    impact_count = sentiment_df['impact'].value_counts()
    print(f'\n利好/利空统计:')
    for impact, count in impact_count.items():
        print(f'  {impact}: {count} 条')
