import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self, api_key: str = ''):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2'

    def fetch_gold_news(self, query: str = 'gold price', days: int = 7) -> List[Dict]:
        if not self.api_key:
            logger.warning("No News API key provided, using alternative sources")
            return self._fetch_alternative_news(query)
            
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            to_date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'from': from_date,
                'to': to_date,
                'language': 'en',
                'sortBy': 'publishedAt',
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            news_list = []
            for article in articles[:20]:
                news_list.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'url': article.get('url', '')
                })
            
            logger.info(f"Fetched {len(news_list)} news articles")
            return news_list
            
        except Exception as e:
            logger.error(f"Error fetching news from API: {e}")
            return self._fetch_alternative_news(query)

    def _fetch_alternative_news(self, query: str) -> List[Dict]:
        try:
            url = f"https://www.google.com/search?q={query}&tbm=nws"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            news_list = []
            for item in soup.find_all('div', class_='Gx5Zad')[:10]:
                title_elem = item.find('div', class_='JheGif')
                source_elem = item.find('div', class_='MgUUmf')
                time_elem = item.find('span', class_='WG9SHc')
                
                if title_elem:
                    news_list.append({
                        'title': title_elem.get_text(strip=True),
                        'description': '',
                        'source': source_elem.get_text(strip=True) if source_elem else 'Unknown',
                        'published_at': time_elem.get_text(strip=True) if time_elem else '',
                        'url': ''
                    })
            
            logger.info(f"Fetched {len(news_list)} news articles from alternative source")
            return news_list
            
        except Exception as e:
            logger.error(f"Error fetching alternative news: {e}")
            return []

    def fetch_market_sentiment_indicators(self) -> Dict:
        try:
            url = 'https://www.investing.com/commodities/gold-historical-data'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            sentiment_data = {
                'fear_greed_index': self._get_fear_greed_index(),
                'market_mood': 'neutral',
                'timestamp': datetime.now().isoformat()
            }
            
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error fetching sentiment indicators: {e}")
            return {}

    def _get_fear_greed_index(self) -> float:
        try:
            url = 'https://api.alternative.me/fng/'
            response = requests.get(url, timeout=10)
            data = response.json()
            return float(data['data'][0]['value'])
        except:
            return 50.0
