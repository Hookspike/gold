import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from config import Config

# 尝试导入transformers库，用于使用Erlangshen-Roberta模型
try:
    from transformers import pipeline
    has_transformers = True
except ImportError:
    has_transformers = False
    print("警告: 未安装transformers库，将使用传统方法进行情绪分析")

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.news_sources = Config.NEWS_SOURCES
        self.news_api_key = Config.NEWS_API_KEY
        
    def fetch_gold_news(self, days_back: int = 7) -> List[Dict]:
        news_articles = []
        
        # 优先使用东方财富新闻获取黄金相关新闻
        print(f"开始获取黄金相关新闻 (days_back={days_back})...")
        
        eastmoney_news = self._fetch_eastmoney_news(days_back)
        print(f"从东方财富获取到 {len(eastmoney_news)} 条新闻")
        news_articles.extend(eastmoney_news)
        
        # 如果东方财富获取失败，使用金十数据
        if not news_articles:
            jin10_news = self._fetch_jin10_news(days_back)
            print(f"从金十数据获取到 {len(jin10_news)} 条新闻")
            news_articles.extend(jin10_news)
        
        # 如果金十数据获取失败，使用备用方法获取财经新闻
        if not news_articles:
            backup_news = self._fetch_news_from_sources(['黄金', '美联储', '加息', '通胀', '美元', '贵金属', '央行', '利率'], days_back)
            print(f"从备用数据源获取到 {len(backup_news)} 条新闻")
            news_articles.extend(backup_news)
        
        # 如果备用方法获取失败，再尝试央视新闻
        if not news_articles:
            try:
                import akshare as ak
                
                # 使用AkShare获取央视新闻
                news_df = ak.news_cctv()
                cctv_news = []
                
                if not news_df.empty:
                    # 筛选与黄金相关的新闻
                    gold_keywords = ['黄金', 'gold', 'XAU', '美联储', '加息', '通胀', 'CPI', '非农', '美元', '贵金属', '央行', '利率', '货币政策', '经济数据', '就业数据', '通胀率', '金融市场']
                    
                    for _, row in news_df.iterrows():
                        title = row.get('title', '')
                        content = row.get('content', '')
                        time = row.get('date', '')
                        
                        # 检查是否包含黄金相关关键词
                        if any(keyword in title.lower() or keyword in content.lower() for keyword in gold_keywords):
                            cctv_news.append({
                                'title': title,
                                'description': content,
                                'content': content,
                                'url': '',
                                'publishedAt': time,
                                'source': '央视新闻'
                            })
                
                print(f"从央视新闻获取到 {len(cctv_news)} 条新闻")
                news_articles.extend(cctv_news)
            except Exception as e:
                print(f"使用AkShare获取新闻时出错: {e}")
        
        print(f"总共获取到 {len(news_articles)} 条黄金相关新闻")
        
        # 打印前3条新闻的标题，用于调试
        if news_articles:
            print("\n前3条新闻:")
            for i, article in enumerate(news_articles[:3]):
                print(f"{i+1}. {article.get('title', '无标题')} (来源: {article.get('source', '未知')})")
        
        return news_articles
    
    def _fetch_eastmoney_news(self, days_back: int) -> List[Dict]:
        articles = []
        
        try:
            import akshare as ak
            
            # 使用东方财富新闻接口获取黄金相关新闻
            news_df = ak.stock_news_em(symbol="黄金")
            
            if not news_df.empty:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                
                for _, row in news_df.iterrows():
                    try:
                        title = row.get('新闻标题', '')
                        content = row.get('新闻内容', '')
                        publish_time = row.get('发布时间', '')
                        source = row.get('文章来源', '东方财富')
                        url = row.get('新闻链接', '')
                        
                        # 解析发布时间
                        try:
                            news_time = pd.to_datetime(publish_time)
                        except:
                            news_time = datetime.now()
                        
                        # 检查是否在时间范围内
                        if news_time < cutoff_date:
                            continue
                        
                        articles.append({
                            'title': title,
                            'description': content[:200] + '...' if len(content) > 200 else content,
                            'content': content,
                            'url': url,
                            'publishedAt': news_time.isoformat(),
                            'source': source
                        })
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"从东方财富获取新闻时出错: {e}")
        
        return articles
    
    def _fetch_jin10_news(self, days_back: int) -> List[Dict]:
        articles = []
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # 金十数据快讯页面
            url = 'https://www.jin10.com/'
            
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找快讯数据
                # 金十数据的快讯通常在特定的div或script标签中
                script_tags = soup.find_all('script')
                
                for script in script_tags:
                    script_content = script.string
                    if script_content and 'flashList' in script_content:
                        import re
                        import json
                        
                        try:
                            # 提取JSON数据
                            json_match = re.search(r'flashList\s*=\s*(\[.*?\]);', script_content)
                            if json_match:
                                flash_data = json.loads(json_match.group(1))
                                
                                # 黄金相关关键词
                                gold_keywords = ['黄金', 'gold', 'XAU', '白银', '白银', '贵金属', '美联储', '加息', '降息', '通胀', 'CPI', '非农', '美元', '央行', '利率', '货币政策', '经济数据', '就业数据', '通胀率', '金融市场', '避险', 'ETF', 'SPDR', 'COMEX', '伦敦金', '现货黄金']
                                
                                cutoff_date = datetime.now() - timedelta(days=days_back)
                                
                                for item in flash_data:
                                    try:
                                        content = item.get('content', '')
                                        timestamp = item.get('time', '')
                                        data_id = item.get('id', '')
                                        
                                        # 解析时间戳
                                        if timestamp:
                                            try:
                                                news_time = datetime.fromtimestamp(int(timestamp))
                                            except:
                                                news_time = datetime.now()
                                        else:
                                            news_time = datetime.now()
                                        
                                        # 检查是否在时间范围内
                                        if news_time < cutoff_date:
                                            continue
                                        
                                        # 检查是否包含黄金相关关键词
                                        if any(keyword in content for keyword in gold_keywords):
                                            articles.append({
                                                'title': content[:100] + '...' if len(content) > 100 else content,
                                                'description': content,
                                                'content': content,
                                                'url': f'https://www.jin10.com/flash/{data_id}',
                                                'publishedAt': news_time.isoformat(),
                                                'source': '金十数据'
                                            })
                                    except Exception as e:
                                        continue
                                
                                break
                        except Exception as e:
                            print(f"解析金十数据JSON时出错: {e}")
                            continue
                
                # 如果JSON解析失败，尝试直接解析HTML
                if not articles:
                    flash_items = soup.find_all('div', class_='flash-item')
                    for item in flash_items[:50]:
                        try:
                            content_div = item.find('div', class_='content')
                            time_div = item.find('div', class_='time')
                            
                            if content_div:
                                content = content_div.get_text(strip=True)
                                time_str = time_div.get_text(strip=True) if time_div else ''
                                
                                gold_keywords = ['黄金', 'gold', 'XAU', '白银', '贵金属', '美联储', '加息', '通胀', 'CPI', '非农', '美元', '央行', '利率', '货币政策']
                                
                                if any(keyword in content for keyword in gold_keywords):
                                    articles.append({
                                        'title': content[:100] + '...' if len(content) > 100 else content,
                                        'description': content,
                                        'content': content,
                                        'url': 'https://www.jin10.com/',
                                        'publishedAt': datetime.now().isoformat(),
                                        'source': '金十数据'
                                    })
                        except Exception as e:
                            continue
                
        except Exception as e:
            print(f"从金十数据获取新闻时出错: {e}")
        
        return articles
    
    def _fetch_news_from_sources(self, keywords: List[str], days_back: int) -> List[Dict]:
        articles = []
        
        # 使用国内财经网站作为备用数据源
        search_urls = {
            '新浪财经': 'https://finance.sina.com.cn/roll/',
            '东方财富': 'https://finance.eastmoney.com/news/'
        }
        
        for source, url in search_urls.items():
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    if source == '新浪财经':
                        # 新浪财经新闻抓取
                        items = soup.find_all('a', class_='news-item')
                        for item in items[:15]:
                            title = item.get_text(strip=True)
                            if any(keyword in title for keyword in keywords):
                                articles.append({
                                    'title': title,
                                    'description': '',
                                    'content': '',
                                    'url': item.get('href', ''),
                                    'publishedAt': datetime.now().isoformat(),
                                    'source': '新浪财经'
                                })
                    elif source == '东方财富':
                        # 东方财富新闻抓取
                        items = soup.find_all('a', class_='title')
                        for item in items[:15]:
                            title = item.get_text(strip=True)
                            if any(keyword in title for keyword in keywords):
                                articles.append({
                                    'title': title,
                                    'description': '',
                                    'content': '',
                                    'url': item.get('href', ''),
                                    'publishedAt': datetime.now().isoformat(),
                                    'source': '东方财富'
                                })
            except Exception as e:
                print(f"从 {source} 获取新闻时出错: {e}")
        
        return articles
    
    def analyze_sentiment(self, text: str) -> Dict:
        if not text:
            return {'compound': 0, 'positive': 0, 'negative': 0, 'neutral': 0}
        
        # 中文金融情绪分析词典
        positive_words = {
            '上涨', '大幅上涨', '创历史新高', '新高', '涨停', '利好', '增长', '上升',
            '走强', '强势', '看涨', '上涨趋势', '上涨预期', '提升', '提高', '增加',
            '扩大', '好转', '改善', '复苏', '反弹', '回暖', '景气', '繁荣',
            '强劲', '稳健', '盈利', '利润', '收益', '回报', '牛市', '多头',
            '做多', '买入', '增持', '看好', '乐观', '积极'
        }
        
        negative_words = {
            '下跌', '大幅下跌', '跌停', '利空', '下滑', '下降', '走低', '走弱',
            '弱势', '看跌', '下跌趋势', '下跌预期', '减少', '缩小', '恶化', '衰退',
            '萎缩', '疲软', '低迷', '萧条', '亏损', '损失', '风险', '熊市',
            '空头', '做空', '卖出', '减持', '看空', '悲观', '消极', '跌幅',
            '跌破', '回落', '下挫', '跳水', '暴跌', '阴跌', '下跌', '下滑'
        }
        
        # 计算情绪得分
        positive_count = 0
        negative_count = 0
        
        # 检查长词优先
        for word in sorted(positive_words, key=len, reverse=True):
            if word in text:
                positive_count += text.count(word)
        
        for word in sorted(negative_words, key=len, reverse=True):
            if word in text:
                negative_count += text.count(word)
        
        # 特殊处理：确保负面词汇被正确识别
        if '跌幅' in text or '跌破' in text or '回落' in text:
            negative_count += 1
        
        # 计算得分
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
            'neutral': neutral,
            'textblob_polarity': compound,
            'textblob_subjectivity': 1.0 if total_count > 0 else 0
        }
    
    def analyze_news_sentiment(self, news_articles: List[Dict]) -> pd.DataFrame:
        if not news_articles:
            return pd.DataFrame()
        
        results = []
        for article in news_articles:
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
            sentiment = self.analyze_sentiment(text)
            
            # 判断利好/利空标记
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
                'textblob_polarity': sentiment['textblob_polarity'],
                'textblob_subjectivity': sentiment['textblob_subjectivity'],
                'impact': impact
            })
        
        df = pd.DataFrame(results)
        
        if not df.empty:
            df['publishedAt'] = pd.to_datetime(df['publishedAt'])
            # 按情绪分数绝对值降序排序，最重要的新闻（最利好或最利空）排在前面
            df['sentiment_abs'] = df['compound'].abs()
            df = df.sort_values(['sentiment_abs', 'publishedAt'], ascending=[False, False])
            df = df.drop('sentiment_abs', axis=1)
        
        return df
    
    def calculate_overall_sentiment(self, sentiment_df: pd.DataFrame) -> Dict:
        if sentiment_df.empty:
            return {
                'overall_sentiment': 0,
                'sentiment_label': 'Neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'avg_compound': 0,
                'weighted_sentiment': 0
            }
        
        positive_count = (sentiment_df['compound'] > Config.SENTIMENT_THRESHOLD).sum()
        negative_count = (sentiment_df['compound'] < -Config.SENTIMENT_THRESHOLD).sum()
        neutral_count = len(sentiment_df) - positive_count - negative_count
        
        avg_compound = sentiment_df['compound'].mean()
        
        if avg_compound > 0.1:
            sentiment_label = 'Bullish'
        elif avg_compound < -0.1:
            sentiment_label = 'Bearish'
        else:
            sentiment_label = 'Neutral'
        
        weighted_sentiment = (
            sentiment_df['compound'] * sentiment_df['textblob_subjectivity']
        ).mean()
        
        return {
            'overall_sentiment': avg_compound,
            'sentiment_label': sentiment_label,
            'positive_count': int(positive_count),
            'negative_count': int(negative_count),
            'neutral_count': int(neutral_count),
            'avg_compound': float(avg_compound),
            'weighted_sentiment': float(weighted_sentiment)
        }
    
    def get_sentiment_trend(self, sentiment_df: pd.DataFrame) -> pd.DataFrame:
        if sentiment_df.empty:
            return pd.DataFrame()
        
        sentiment_df['date'] = pd.to_datetime(sentiment_df['publishedAt']).dt.date
        daily_sentiment = sentiment_df.groupby('date').agg({
            'compound': 'mean',
            'positive': 'mean',
            'negative': 'mean',
            'neutral': 'mean'
        }).reset_index()
        
        daily_sentiment['sentiment_trend'] = daily_sentiment['compound'].diff()
        
        return daily_sentiment
    
    def analyze_market_fear_greed(self, price_data: pd.DataFrame) -> Dict:
        if price_data.empty or len(price_data) < 20:
            return {'index': 50, 'label': 'Neutral'}
        
        recent_data = price_data.tail(20)
        
        price_momentum = (recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0] - 1) * 100
        
        volatility = recent_data['Close'].pct_change().std() * 100
        
        if price_momentum > 2 and volatility < 1:
            fear_greed_index = 75
            label = 'Greed'
        elif price_momentum < -2 and volatility > 2:
            fear_greed_index = 25
            label = 'Fear'
        elif price_momentum > 0:
            fear_greed_index = 60
            label = 'Moderate Greed'
        elif price_momentum < 0:
            fear_greed_index = 40
            label = 'Moderate Fear'
        else:
            fear_greed_index = 50
            label = 'Neutral'
        
        return {
            'index': fear_greed_index,
            'label': label,
            'price_momentum': price_momentum,
            'volatility': volatility
        }
    
    def generate_sentiment_report(self, sentiment_df: pd.DataFrame, price_data: pd.DataFrame) -> Dict:
        overall_sentiment = self.calculate_overall_sentiment(sentiment_df)
        sentiment_trend = self.get_sentiment_trend(sentiment_df)
        fear_greed = self.analyze_market_fear_greed(price_data)
        
        recent_trend = sentiment_trend['sentiment_trend'].iloc[-1] if not sentiment_trend.empty and len(sentiment_trend) > 1 else 0
        
        if recent_trend > 0.05:
            trend_direction = 'Improving'
        elif recent_trend < -0.05:
            trend_direction = 'Deteriorating'
        else:
            trend_direction = 'Stable'
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_trend': trend_direction,
            'fear_greed_index': fear_greed,
            'analysis_time': datetime.now().isoformat(),
            'news_count': len(sentiment_df) if not sentiment_df.empty else 0
        }
