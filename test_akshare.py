import akshare as ak

print('测试AkShare黄金数据获取...')
try:
    gold_df = ak.futures_foreign_hist(symbol='GC')
    print(f'数据获取成功，行数: {len(gold_df)}')
    print(gold_df.tail())
except Exception as e:
    print(f'错误: {e}')

print('\n测试AkShare新闻数据获取...')
try:
    news_df = ak.stock_news_em()
    print(f'新闻数据获取成功，行数: {len(news_df)}')
    print(news_df.tail())
except Exception as e:
    print(f'错误: {e}')