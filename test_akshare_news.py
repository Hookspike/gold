import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def test_akshare_news():
    print("=" * 60)
    print("测试AkShare新闻接口")
    print("=" * 60)
    
    gold_keywords = ['黄金', 'gold', 'XAU', '白银', '贵金属', '美联储', '加息', '通胀', 'CPI', '非农', '美元', '央行', '利率', '货币政策', '经济数据', '就业数据', '通胀率', '金融市场', '避险', 'ETF', 'SPDR', 'COMEX', '伦敦金', '现货黄金']
    
    # 测试1: 东方财富新闻
    print("\n1. 测试东方财富新闻接口...")
    try:
        news_df = ak.stock_news_em(symbol="黄金")
        print(f"   获取到 {len(news_df)} 条新闻")
        if not news_df.empty:
            print(f"   列名: {news_df.columns.tolist()}")
            print(f"   前3条新闻:")
            for idx, row in news_df.head(3).iterrows():
                print(f"     - {row.get('新闻标题', row.get('title', 'N/A'))}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试2: 百度财经新闻
    print("\n2. 测试百度财经新闻接口...")
    try:
        news_df = ak.news_economic_baidu()
        print(f"   获取到 {len(news_df)} 条新闻")
        if not news_df.empty:
            print(f"   列名: {news_df.columns.tolist()}")
            print(f"   前3条新闻:")
            for idx, row in news_df.head(3).iterrows():
                print(f"     - {row.get('新闻标题', row.get('title', 'N/A'))}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试3: 央视新闻
    print("\n3. 测试央视新闻接口...")
    try:
        news_df = ak.news_cctv()
        print(f"   获取到 {len(news_df)} 条新闻")
        if not news_df.empty:
            print(f"   列名: {news_df.columns.tolist()}")
            # 筛选黄金相关新闻
            filtered_news = news_df[
                news_df['title'].str.contains('|'.join(gold_keywords), case=False, na=False) |
                news_df['content'].str.contains('|'.join(gold_keywords), case=False, na=False)
            ]
            print(f"   黄金相关新闻: {len(filtered_news)} 条")
            if not filtered_news.empty:
                print(f"   前3条黄金新闻:")
                for idx, row in filtered_news.head(3).iterrows():
                    print(f"     - {row.get('title', 'N/A')}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 测试4: 财联社新闻
    print("\n4. 测试财联社新闻接口...")
    try:
        news_df = ak.news_cl_cn()
        print(f"   获取到 {len(news_df)} 条新闻")
        if not news_df.empty:
            print(f"   列名: {news_df.columns.tolist()}")
            # 筛选黄金相关新闻
            if 'title' in news_df.columns:
                filtered_news = news_df[
                    news_df['title'].str.contains('|'.join(gold_keywords), case=False, na=False)
                ]
                print(f"   黄金相关新闻: {len(filtered_news)} 条")
                if not filtered_news.empty:
                    print(f"   前3条黄金新闻:")
                    for idx, row in filtered_news.head(3).iterrows():
                        print(f"     - {row.get('title', 'N/A')}")
    except Exception as e:
        print(f"   失败: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_akshare_news()
