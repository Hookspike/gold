#!/usr/bin/env python3
# 测试新闻数据获取和筛选效果

import akshare as ak

def test_news_fetch():
    print('测试央视新闻数据获取...')
    
    try:
        # 获取央视新闻
        news_df = ak.news_cctv()
        
        print(f'获取到 {len(news_df)} 条新闻')
        print('\n数据列名:', news_df.columns.tolist())
        
        if not news_df.empty:
            print('\n所有新闻标题:')
            for i, row in news_df.iterrows():
                title = row.get('title', '')
                content = row.get('content', '')
                print(f'\n{title}')
                print(f'内容摘要: {content[:100]}...')
            
            # 测试黄金关键词筛选
            print('\n测试黄金关键词筛选:')
            gold_keywords = ['黄金', 'gold', 'XAU', '美联储', '加息', '通胀', 'CPI', '非农', '美元', '贵金属', '央行', '利率', '货币政策', '经济数据', '就业数据', '通胀率', '金融市场']
            
            filtered_news = []
            for _, row in news_df.iterrows():
                title = row.get('title', '')
                content = row.get('content', '')
                
                # 检查是否包含黄金相关关键词
                matched_keywords = [keyword for keyword in gold_keywords if keyword in title.lower() or keyword in content.lower()]
                if matched_keywords:
                    filtered_news.append({
                        'title': title,
                        'content': content,
                        'time': row.get('date', ''),
                        'matched_keywords': matched_keywords
                    })
            
            print(f'筛选后找到 {len(filtered_news)} 条与黄金相关的新闻')
            if filtered_news:
                print('\n筛选结果:')
                for news in filtered_news:
                    print(f'\n标题: {news["title"]}')
                    print(f'匹配关键词: {news["matched_keywords"]}')
                    print(f'时间: {news["time"]}')
            else:
                print('未找到与黄金相关的新闻')
                
                # 尝试更广泛的筛选
                print('\n尝试更广泛的财经关键词筛选:')
                financial_keywords = ['经济', '金融', '市场', '政策', '数据']
                
                financial_news = []
                for _, row in news_df.iterrows():
                    title = row.get('title', '')
                    content = row.get('content', '')
                    
                    if any(keyword in title.lower() or keyword in content.lower() for keyword in financial_keywords):
                        financial_news.append({
                            'title': title,
                            'content': content
                        })
                
                print(f'找到 {len(financial_news)} 条财经相关新闻')
                if financial_news:
                    print('\n财经新闻:')
                    for news in financial_news:
                        print(f'- {news["title"]}')
        
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_news_fetch()