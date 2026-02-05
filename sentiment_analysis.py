import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from config import Config

class SentimentAnalyzer:
    def __init__(self):
        self.news_sources = Config.NEWS_SOURCES
        self.news_api_key = Config.NEWS_API_KEY
        
    def fetch_gold_news(self, days_back: int = 7) -> List[Dict]:
        news_articles = []
        
        try:
            import akshare as ak
            
            print(f"开始获取黄金相关新闻 (days_back={days_back})...")
            
            gold_keywords = ['黄金', 'gold', 'XAU', '白银', '白银', '贵金属', '美联储', '加息', '降息', '通胀', 'CPI', '非农', '美元', '美元指数', '央行', '利率', '货币政策', '经济数据', '就业数据', '通胀率', '金融市场', '避险', '风险']
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            try:
                news_df = ak.stock_news_em(symbol="黄金")
                if not news_df.empty:
                    for _, row in news_df.iterrows():
                        article_date = pd.to_datetime(row.get('新闻时间', datetime.now()))
                        if article_date >= cutoff_date:
                            news_articles.append({
                                'title': row.get('新闻标题', ''),
                                'description': row.get('新闻内容', '')[:200],
                                'content': row.get('新闻内容', ''),
                                'url': row.get('新闻链接', ''),
                                'publishedAt': row.get('新闻时间', ''),
                                'source': '东方财富'
                            })
            except Exception as e:
                print(f"从东方财富获取新闻时出错: {e}")
            
            try:
                news_df = ak.news_jin10()
                if not news_df.empty:
                    for _, row in news_df.iterrows():
                        article_date = pd.to_datetime(row.get('datetime', datetime.now()))
                        if article_date >= cutoff_date:
                            title = row.get('title', '')
                            content = row.get('content', '')
                            if any(keyword in title.lower() or keyword in content.lower() for keyword in gold_keywords):
                                news_articles.append({
                                    'title': title,
                                    'description': content[:200] if content else '',
                                    'content': content,
                                    'url': '',
                                    'publishedAt': row.get('datetime', ''),
                                    'source': '金十数据'
                                })
            except Exception as e:
                print(f"从金十数据获取新闻时出错: {e}")
            
            try:
                news_df = ak.stock_news_em(symbol="贵金属")
                if not news_df.empty:
                    for _, row in news_df.iterrows():
                        article_date = pd.to_datetime(row.get('新闻时间', datetime.now()))
                        if article_date >= cutoff_date:
                            news_articles.append({
                                'title': row.get('新闻标题', ''),
                                'description': row.get('新闻内容', '')[:200],
                                'content': row.get('新闻内容', ''),
                                'url': row.get('新闻链接', ''),
                                'publishedAt': row.get('新闻时间', ''),
                                'source': '东方财富-贵金属'
                            })
            except Exception as e:
                print(f"从东方财富获取贵金属新闻时出错: {e}")
            
            print(f"总共获取到 {len(news_articles)} 条黄金相关新闻")
            
            if news_articles:
                print("\n前3条新闻:")
                for i, article in enumerate(news_articles[:3]):
                    print(f"{i+1}. {article.get('title', '无标题')} (来源: {article.get('source', '未知')})")
            
        except Exception as e:
            print(f"获取新闻时出错: {e}")
        
        return news_articles
    
    def analyze_sentiment(self, text: str) -> Dict:
        positive_words = [
            '上涨', '增长', '利好', '强劲', '突破', '创新高', '涨', '升', '攀升',
            '积极', '乐观', '看好', '买入', '增持', '推荐', '牛市', '反弹',
            '复苏', '繁荣', '稳定', '走高', '拉升', '上涨', '上涨', '上涨'
        ]
        
        negative_words = [
            '下跌', '下降', '利空', '疲软', '跌破', '创新低', '跌', '降', '回落',
            '消极', '悲观', '看空', '卖出', '减持', '熊市', '调整',
            '衰退', '萧条', '动荡', '走低', '打压', '下跌', '下跌', '下跌'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if '跌幅' in text or '跌破' in text or '回落' in text:
            negative_count += 1
        
        total_count = positive_count + negative_count
        if total_count > 0:
            compound = (positive_count - negative_count) / total_count
            positive = positive_count / total_count
            negative = negative_count / total_count
            neutral = 0
        else:
            compound = 0
            positive = 0
            negative = 0
            neutral = 1
        
        return {
            'compound': compound,
            'positive': positive,
            'negative': negative,
            'neutral': neutral
        }
    
    def analyze_news_sentiment(self, news_articles: List[Dict]) -> pd.DataFrame:
        if not news_articles:
            return pd.DataFrame()
        
        results = []
        for article in news_articles:
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
            sentiment = self.analyze_sentiment(text)
            
            compound_score = sentiment['compound']
            if compound_score > 0.15:
                impact = '利好'
            elif compound_score < -0.15:
                impact = '利空'
            else:
                impact = '中性'
            
            results.append({
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'publishedAt': article.get('publishedAt', ''),
                'source': article.get('source', ''),
                'compound': sentiment['compound'],
                'positive': sentiment['positive'],
                'negative': sentiment['negative'],
                'neutral': sentiment['neutral'],
                'impact': impact
            })
        
        return pd.DataFrame(results)
    
    def calculate_overall_sentiment(self, sentiment_df: pd.DataFrame) -> Dict:
        if sentiment_df.empty:
            return {
                'overall_score': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'sentiment_label': '中性'
            }
        
        overall_score = sentiment_df['compound'].mean()
        positive_count = len(sentiment_df[sentiment_df['compound'] > 0.15])
        negative_count = len(sentiment_df[sentiment_df['compound'] < -0.15])
        neutral_count = len(sentiment_df) - positive_count - negative_count
        
        if overall_score > 0.15:
            sentiment_label = '乐观'
        elif overall_score < -0.15:
            sentiment_label = '悲观'
        else:
            sentiment_label = '中性'
        
        return {
            'overall_score': overall_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_label': sentiment_label
        }
    
    def analyze_market_fear_greed(self, df: pd.DataFrame) -> Dict:
        """
        基于价格数据计算恐惧贪婪指数
        """
        try:
            if df.empty or len(df) < 5:
                return {'index': 50, 'label': '中性'}
            
            df = df.copy()
            df = df.sort_values('date')
            
            df['returns'] = df['close'].pct_change()
            df['volatility'] = df['returns'].rolling(window=5).std()
            
            last_return = df['returns'].iloc[-1]
            last_volatility = df['volatility'].iloc[-1]
            
            avg_return = df['returns'].mean()
            avg_volatility = df['volatility'].mean()
            
            momentum_score = 50
            if last_return > avg_return:
                momentum_score = 50 + (last_return - avg_return) * 1000
            else:
                momentum_score = 50 + (last_return - avg_return) * 1000
            
            momentum_score = max(0, min(100, momentum_score))
            
            volatility_score = 50
            if last_volatility < avg_volatility:
                volatility_score = 50 + (avg_volatility - last_volatility) * 1000
            else:
                volatility_score = 50 - (last_volatility - avg_volatility) * 1000
            
            volatility_score = max(0, min(100, volatility_score))
            
            fear_greed_index = (momentum_score * 0.6 + volatility_score * 0.4)
            fear_greed_index = max(0, min(100, fear_greed_index))
            
            if fear_greed_index >= 75:
                label = '贪婪'
            elif fear_greed_index >= 55:
                label = '乐观'
            elif fear_greed_index >= 45:
                label = '中性'
            elif fear_greed_index >= 25:
                label = '恐惧'
            else:
                label = '极度恐惧'
            
            return {
                'index': round(fear_greed_index, 2),
                'label': label
            }
        except Exception as e:
            print(f"计算恐惧贪婪指数时出错: {e}")
            return {'index': 50, 'label': '中性'}
