from sentiment_analysis import SentimentAnalyzer

analyzer = SentimentAnalyzer()
news = analyzer.fetch_gold_news(days_back=7)
print(f'获取到 {len(news)} 条新闻\n')

sentiment_df = analyzer.analyze_news_sentiment(news)
print(f'情绪分析完成，共 {len(sentiment_df)} 条\n')

if not sentiment_df.empty:
    print('最重要的3条新闻（按情绪影响排序）：')
    for idx, row in sentiment_df.head(3).iterrows():
        impact = row.get('impact', '中性')
        compound = row['compound']
        print(f'\n[{row["source"]}] {row["publishedAt"]}')
        print(f'标题: {row["title"][:80]}...')
        print(f'影响: {impact} (情绪分数: {compound:.4f})')
