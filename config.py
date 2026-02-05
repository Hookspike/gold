import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATA_SOURCE = os.getenv('DATA_SOURCE', 'yfinance')
    GOLD_TICKER = os.getenv('GOLD_TICKER', 'XAUUSD=X')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
    DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'demo')
    FINNHUB_KEY = os.getenv('FINNHUB_KEY', '')
    HISTORICAL_DAYS = int(os.getenv('HISTORICAL_DAYS', '365'))
    UPDATE_INTERVAL_HOURS = int(os.getenv('UPDATE_INTERVAL_HOURS', '1'))
    PREDICTION_DAYS = int(os.getenv('PREDICTION_DAYS', '7'))
    MODEL_TYPE = os.getenv('MODEL_TYPE', 'ensemble')
    SENTIMENT_THRESHOLD = float(os.getenv('SENTIMENT_THRESHOLD', '0.1'))
    NEWS_SOURCES = os.getenv('NEWS_SOURCES', 'CNBC,Bloomberg,Reuters,FinancialTimes').split(',')
    CHART_STYLE = os.getenv('CHART_STYLE', 'plotly')
    THEME = os.getenv('THEME', 'dark')
