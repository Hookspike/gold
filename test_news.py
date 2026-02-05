#!/usr/bin/env python3
# 测试新闻数据获取和筛选

import akshare as ak

def test_news_fetch():
    print('测试AkShare新闻数据获取...')
    
    try:
        # 获取东方财富股票新闻
        news_df = ak.stock_news_em()
        
        print(f'获取到 {len(news_df)} 条新闻')
        print('\n数据列名:', news_df.columns.tolist())
        
        if not news_df.empty:
            print('\n前5条新闻详细信息:')
            for i, row in news_df.iterrows():
                if i < 5:
                    print(f'\n新闻 {i+1}:')
                    print(f'关键词: {row.get("关键词", "")}')
                    print(f'新闻标题: {row.get("新闻标题", "")}')
                    print(f'新闻内容: {row.get("新闻内容", "")[:100]}...')
                    print(f'发布时间: {row.get("发布时间", "")}')
                    print(f'文章来源: {row.get("文章来源", "")}')
                    print(f'新闻链接: {row.get("新闻链接", "")}')
            
            # 测试黄金关键词筛选
            print('\n测试黄金关键词筛选:')
            gold_keywords = ['黄金', 'gold', 'XAU', '美联储', '加息', '通胀', 'CPI', '非农', '美元']
            
            filtered_news = []
            for _, row in news_df.iterrows():
                title = row.get('新闻标题', '')
                content = row.get('新闻内容', '')
                
                # 检查是否包含黄金相关关键词
                if any(keyword in title.lower() or keyword in content.lower() for keyword in gold_keywords):
                    filtered_news.append({
                        'title': title,
                        'content': content,
                        'time': row.get('发布时间', ''),
                        'url': row.get('新闻链接', '')
                    })
            
            print(f'筛选后找到 {len(filtered_news)} 条与黄金相关的新闻')
            if filtered_news:
                print('\n筛选结果:')
                for news in filtered_news:
                    print(f'标题: {news["title"]}')
                    print(f'时间: {news["time"]}')
                    print()
            else:
                print('未找到与黄金相关的新闻')
                print('\n所有新闻标题:')
                for _, row in news_df.iterrows():
                    print(f'- {row.get("新闻标题", "")}')
        
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_news_fetch()