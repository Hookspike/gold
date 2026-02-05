import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import requests
import json
import time
import os
from config import Config

class GoldDataFetcher:
    def __init__(self):
        self.ticker = Config.GOLD_TICKER
        self.historical_days = Config.HISTORICAL_DAYS
        self.max_retries = 3
        self.retry_delay = 2
        
        self.alpha_vantage_key = Config.ALPHA_VANTAGE_KEY if hasattr(Config, 'ALPHA_VANTAGE_KEY') else 'demo'
        self.finnhub_key = Config.FINNHUB_KEY if hasattr(Config, 'FINNHUB_KEY') else ''
        
        # 优化数据源优先级
        self.data_sources = [
            'sina',      # 优先级1：实时数据
            'akshare',   # 优先级2：国内数据源
            'kitco',     # 优先级3：专业黄金数据
            'investing', # 优先级4：国际数据源
            'yfinance'   # 优先级5：备用数据源
        ]
        
        # 本地缓存配置
        self.cache_dir = 'data_cache'
        self.cache_file = os.path.join(self.cache_dir, 'gold_price_cache.csv')
        self.cache_expiry_hours = 24
        
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def validate_data_quality(self, df: pd.DataFrame) -> tuple:
        """
        验证数据质量
        
        返回: (is_valid, quality_score, issues)
        - is_valid: 数据是否有效
        - quality_score: 质量分数 (0-100)
        - issues: 发现的问题列表
        """
        if df.empty:
            return False, 0, ['数据为空']
        
        issues = []
        quality_score = 100
        
        # 检查数据完整性
        required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            issues.append(f'缺少必要列: {", ".join(missing_cols)}')
            quality_score -= 30
        
        # 检查缺失值比例
        if not df.empty:
            null_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
            if null_ratio > 0.1:  # 超过10%缺失值
                issues.append(f'缺失值过多: {null_ratio*100:.1f}%')
                quality_score -= 20
            elif null_ratio > 0.05:  # 超过5%缺失值
                issues.append(f'缺失值较多: {null_ratio*100:.1f}%')
                quality_score -= 10
        
        # 检查价格合理性
        if 'Close' in df.columns:
            if (df['Close'] <= 0).any():
                issues.append('存在非正价格')
                quality_score -= 20
            
            if (df['Close'] > 100000).any():
                issues.append('存在异常高价')
                quality_score -= 15
            
            # 检查价格波动是否合理
            price_changes = df['Close'].pct_change().abs()
            if (price_changes > 0.5).any():  # 单日波动超过50%
                issues.append('存在异常价格波动')
                quality_score -= 10
        
        # 检查价格逻辑关系
        if all(col in df.columns for col in ['High', 'Low', 'Open', 'Close']):
            # High应该 >= Open, Close
            invalid_high = (df['High'] < df['Open']) | (df['High'] < df['Close'])
            if invalid_high.any():
                issues.append(f'存在{invalid_high.sum()}条数据最高价低于开盘价或收盘价')
                quality_score -= 10
            
            # Low应该 <= Open, Close
            invalid_low = (df['Low'] > df['Open']) | (df['Low'] > df['Close'])
            if invalid_low.any():
                issues.append(f'存在{invalid_low.sum()}条数据最低价高于开盘价或收盘价')
                quality_score -= 10
        
        # 检查数据量
        if len(df) < 10:
            issues.append(f'数据量不足: 仅{len(df)}条')
            quality_score -= 15
        
        # 检查日期连续性
        if 'Date' in df.columns and len(df) > 1:
            date_diffs = df['Date'].diff().dt.days
            if date_diffs.max() > 7:  # 存在超过7天的间隔
                issues.append('数据存在较大时间间隔')
                quality_score -= 5
        
        # 确保质量分数在0-100之间
        quality_score = max(0, min(100, quality_score))
        
        is_valid = quality_score >= 60  # 质量分数达到60分以上才认为有效
        
        return is_valid, quality_score, issues
    
    def fetch_historical_data(self, period: Optional[str] = None) -> pd.DataFrame:
        if period is None:
            period = self.historical_days
        
        # 首先检查本地缓存
        cached_df = self._load_from_cache()
        if not cached_df.empty:
            is_valid, quality_score, issues = self.validate_data_quality(cached_df)
            if is_valid:
                print(f"使用缓存的真实数据 (质量分数: {quality_score})")
                return cached_df
            else:
                print(f"缓存数据质量不足 (质量分数: {quality_score})，重新获取")
        
        # 尝试从外部数据源获取（排除模拟数据）
        real_sources = [source for source in self.data_sources if source != 'mock']
        best_df = pd.DataFrame()
        best_quality_score = 0
        
        for source in real_sources:
            try:
                print(f"尝试使用数据源: {source}")
                df = self._fetch_from_source(source, period)
                
                if not df.empty:
                    # 验证数据质量
                    is_valid, quality_score, issues = self.validate_data_quality(df)
                    
                    if is_valid:
                        print(f"成功从 {source} 获取数据 (质量分数: {quality_score})")
                        
                        # 如果质量分数更高，则替换当前最佳数据
                        if quality_score > best_quality_score:
                            best_df = df
                            best_quality_score = quality_score
                            
                            # 如果质量分数很高，直接使用
                            if quality_score >= 90:
                                break
                    else:
                        print(f"{source} 数据质量不足: {', '.join(issues)}")
            except Exception as e:
                print(f"从 {source} 获取数据失败: {e}")
                continue
        
        # 如果找到了高质量数据，缓存并返回
        if not best_df.empty:
            print(f"使用最佳数据源，质量分数: {best_quality_score}")
            self._save_to_cache(best_df)
            return best_df
        
        print("所有真实数据源均失败，返回空数据...")
        return pd.DataFrame()
    
    def _fetch_from_source(self, source: str, period: int) -> pd.DataFrame:
        if source == 'akshare':
            return self._fetch_akshare(period)
        elif source == 'kitco':
            return self._fetch_from_kitco(period)
        elif source == 'investing':
            return self._fetch_from_investing(period)
        elif source == 'alpha_vantage':
            return self._fetch_alpha_vantage(period)
        elif source == 'finnhub':
            return self._fetch_finnhub(period)
        elif source == 'yfinance':
            return self._fetch_yfinance(period)
        elif source == 'mock':
            return self._generate_mock_data()
        
        return pd.DataFrame()
    
    def _fetch_akshare(self, period: int) -> pd.DataFrame:
        try:
            import akshare as ak
            
            # 获取COMEX黄金的历史数据
            gold_df = ak.futures_foreign_hist(symbol="GC")
            
            if gold_df.empty:
                raise ValueError("AkShare 黄金数据为空")
            
            # 确保数据格式正确
            gold_df = gold_df.sort_values('日期')
            gold_df = gold_df.tail(period)
            
            # 重命名列以匹配系统需求
            gold_df = gold_df.rename(columns={
                '日期': 'Date',
                '开盘': 'Open',
                '最高': 'High',
                '最低': 'Low',
                '收盘': 'Close',
                '成交量': 'Volume'
            })
            
            # 确保所有必要列存在
            required_cols = ['Date', 'Open', 'High', 'Low', 'Close']
            for col in required_cols:
                if col not in gold_df.columns:
                    raise ValueError(f"缺少必要列: {col}")
            
            # 转换日期格式
            gold_df['Date'] = pd.to_datetime(gold_df['Date'])
            
            # 添加Volume列如果不存在
            if 'Volume' not in gold_df.columns:
                gold_df['Volume'] = 0
            
            return gold_df
            
        except Exception as e:
            print(f"AkShare 错误: {e}")
            return pd.DataFrame()
    
    def _fetch_alpha_vantage(self, period: int) -> pd.DataFrame:
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': 'XAUUSD',
                'outputsize': 'full',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (Daily)' not in data:
                raise ValueError("Alpha Vantage API返回数据格式错误")
            
            time_series = data['Time Series (Daily)']
            df_data = []
            
            for date, values in list(time_series.items())[:period]:
                df_data.append({
                    'Date': datetime.strptime(date, '%Y-%m-%d'),
                    'Open': float(values['1. open']),
                    'High': float(values['2. high']),
                    'Low': float(values['3. low']),
                    'Close': float(values['4. close']),
                    'Volume': int(values['5. volume']) if '5. volume' in values else 0
                })
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('Date')
            return df
            
        except Exception as e:
            print(f"Alpha Vantage 错误: {e}")
            return pd.DataFrame()
    
    def _fetch_finnhub(self, period: int) -> pd.DataFrame:
        if not self.finnhub_key or self.finnhub_key == '':
            return pd.DataFrame()
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            
            url = "https://finnhub.io/api/v1/forex/candle"
            params = {
                'symbol': 'OANDA:XAUUSD',
                'resolution': 'D',
                'from': int(start_date.timestamp()),
                'to': int(end_date.timestamp()),
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 's' not in data or data['s'] != 'ok':
                raise ValueError("Finnhub API返回错误")
            
            df_data = []
            for candle in data['c']:
                df_data.append({
                    'Date': datetime.fromtimestamp(candle['t']),
                    'Open': candle['o'],
                    'High': candle['h'],
                    'Low': candle['l'],
                    'Close': candle['c'],
                    'Volume': candle['v']
                })
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('Date')
            return df
            
        except Exception as e:
            print(f"Finnhub 错误: {e}")
            return pd.DataFrame()
    
    def _fetch_yfinance(self, period: int) -> pd.DataFrame:
        try:
            import yfinance as yf
            
            gold = yf.Ticker('GC=F')
            df = gold.history(period=f"{period}d")
            
            if df.empty:
                gold = yf.Ticker('GLD')
                df = gold.history(period=f"{period}d")
            
            if df.empty:
                raise ValueError("yFinance 数据为空")
            
            df.reset_index(inplace=True)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            elif 'Datetime' in df.columns:
                df['Date'] = pd.to_datetime(df['Datetime'])
            
            df = df.sort_values('Date')
            
            required_cols = ['Open', 'High', 'Low', 'Close']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"缺少必要列: {col}")
            
            if 'Volume' not in df.columns:
                df['Volume'] = 0
            
            return df
            
        except Exception as e:
            print(f"yFinance 错误: {e}")
            return pd.DataFrame()
    
    def _fetch_from_kitco(self, period: int) -> pd.DataFrame:
        try:
            import json
            
            # Kitco API URL for gold prices
            url = "https://www.kitco.com/graph/kitco-gold.json"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if 'gold' in data and 'prices' in data['gold']:
                    prices = data['gold']['prices']
                    df_data = []
                    
                    for price_data in prices:
                        if len(price_data) >= 5:
                            timestamp = price_data[0]
                            open_price = price_data[1]
                            high_price = price_data[2]
                            low_price = price_data[3]
                            close_price = price_data[4]
                            
                            date = datetime.fromtimestamp(timestamp / 1000)
                            
                            df_data.append({
                                'Date': date,
                                'Open': open_price,
                                'High': high_price,
                                'Low': low_price,
                                'Close': close_price,
                                'Volume': 0
                            })
                    
                    df = pd.DataFrame(df_data)
                    df = df.sort_values('Date')
                    
                    # 限制数据量
                    if len(df) > period:
                        df = df.tail(period)
                    
                    return df
            
        except Exception as e:
            print(f"Kitco 错误: {e}")
            return pd.DataFrame()
    
    def _fetch_from_investing(self, period: int) -> pd.DataFrame:
        try:
            from bs4 import BeautifulSoup
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period)
            
            url = f"https://www.investing.com/commodities/gold-historical-data"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table', {'data-test': 'historical-data-table'})
            if not table:
                raise ValueError("无法找到数据表")
            
            rows = table.find_all('tr')[1:]
            df_data = []
            
            for row in rows[:period]:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    date_str = cols[0].text.strip()
                    price = cols[1].text.strip().replace(',', '')
                    open_p = cols[2].text.strip().replace(',', '')
                    high = cols[3].text.strip().replace(',', '')
                    low = cols[4].text.strip().replace(',', '')
                    
                    try:
                        df_data.append({
                            'Date': datetime.strptime(date_str, '%m/%d/%Y'),
                            'Close': float(price),
                            'Open': float(open_p),
                            'High': float(high),
                            'Low': float(low),
                            'Volume': 0
                        })
                    except:
                        continue
            
            df = pd.DataFrame(df_data)
            df = df.sort_values('Date')
            return df
            
        except Exception as e:
            print(f"Investing.com 错误: {e}")
            return pd.DataFrame()
    
    def _generate_mock_data(self) -> pd.DataFrame:
        base_price = 2650.0
        dates = pd.date_range(end=datetime.now(), periods=self.historical_days)
        
        np.random.seed(int(datetime.now().timestamp()))
        
        data = []
        for i, date in enumerate(dates):
            price_change = np.random.normal(0, 0.008)
            open_price = base_price * (1 + price_change)
            close_price = open_price * (1 + np.random.normal(0, 0.004))
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.0015)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.0015)))
            volume = np.random.randint(50000, 150000)
            
            data.append({
                'Date': date,
                'Open': round(open_price, 2),
                'High': round(high_price, 2),
                'Low': round(low_price, 2),
                'Close': round(close_price, 2),
                'Volume': volume
            })
            
            base_price = close_price
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        print(f"已生成 {len(df)} 条模拟数据")
        return df
    
    def _fetch_realtime_from_source(self, source: str) -> Dict:
        if source == 'sina':
            return self._fetch_realtime_sina()
        elif source == 'alpha_vantage':
            return self._fetch_realtime_alpha_vantage()
        elif source == 'finnhub':
            return self._fetch_realtime_finnhub()
        elif source == 'yfinance':
            return self._fetch_realtime_yfinance()
        elif source == 'mock':
            return {}
        
        return {}
    
    def fetch_realtime_price(self) -> Dict:
        for source in self.data_sources:
            try:
                price_data = self._fetch_realtime_from_source(source)
                if price_data and price_data.get('price', 0) > 0:
                    print(f"成功从 {source} 获取实时价格")
                    return price_data
            except Exception as e:
                print(f"从 {source} 获取实时价格失败: {e}")
                continue
        
        print("使用最新历史数据作为实时价格")
        df = self.fetch_historical_data()
        if not df.empty:
            latest = df.iloc[-1]
            return {
                'price': float(latest['Close']),
                'change': float(latest['Close'] - latest['Open']),
                'change_percent': float(((latest['Close'] - latest['Open']) / latest['Open']) * 100),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'timestamp': datetime.now().isoformat()
            }
        
        print("警告：无法获取任何价格数据，返回默认值")
        return {
            'price': 2000.0,
            'change': 0.0,
            'change_percent': 0.0,
            'high': 2000.0,
            'low': 2000.0,
            'volume': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _fetch_realtime_alpha_vantage(self) -> Dict:
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'XAUUSD',
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Global Quote' not in data:
                raise ValueError("Alpha Vantage 实时数据格式错误")
            
            quote = data['Global Quote']
            price = float(quote['05. price'])
            change = float(quote['09. change'])
            change_percent = float(quote['10. change percent'].replace('%', ''))
            
            return {
                'price': price,
                'change': change,
                'change_percent': change_percent,
                'high': price,
                'low': price,
                'volume': 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Alpha Vantage 实时价格错误: {e}")
            return {}
    
    def _fetch_realtime_finnhub(self) -> Dict:
        if not self.finnhub_key or self.finnhub_key == '':
            return {}
        
        try:
            url = "https://finnhub.io/api/v1/quote"
            params = {
                'symbol': 'OANDA:XAUUSD',
                'token': self.finnhub_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'c' not in data:
                raise ValueError("Finnhub 实时数据格式错误")
            
            current = data['c']
            previous_close = data['pc'] if 'pc' in data else current
            
            return {
                'price': current,
                'change': current - previous_close,
                'change_percent': ((current - previous_close) / previous_close * 100) if previous_close > 0 else 0,
                'high': data['h'] if 'h' in data else current,
                'low': data['l'] if 'l' in data else current,
                'volume': 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Finnhub 实时价格错误: {e}")
            return {}
    
    def _fetch_realtime_sina(self) -> Dict:
        try:
            url = "http://hq.sinajs.cn/list=hf_XAU"
            headers = {
                "Referer": "https://finance.sina.com.cn/"
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                # 返回的数据格式是：var hq_str_hf_XAU="最新价,涨跌幅,买价,卖价,..."
                text = response.text
                
                # 解析字符串
                content = text.split('"')[1]
                data_list = content.split(',')
                
                # 提取核心字段
                current_price = float(data_list[0])  # 最新价
                buy_price = float(data_list[2]) if data_list[2] else current_price  # 买价
                sell_price = float(data_list[3]) if data_list[3] else current_price  # 卖价
                
                # 提取今日最高和最低价格
                day_high = current_price
                day_low = current_price
                change_percent = 0.0
                
                # 检查是否有更多字段
                if len(data_list) > 4:
                    try:
                        # 今日最高价格
                        if data_list[4]:
                            day_high = float(data_list[4])
                        # 今日最低价格
                        if len(data_list) > 5 and data_list[5]:
                            day_low = float(data_list[5])
                        # 计算涨跌幅
                        if day_high > day_low:
                            change_percent = ((current_price - day_low) / day_low) * 100
                    except:
                        pass
                
                return {
                    'price': current_price,
                    'change': 0.0,  # 新浪接口没有直接提供涨跌额
                    'change_percent': change_percent,
                    'high': day_high,
                    'low': day_low,
                    'volume': 0,
                    'timestamp': datetime.now().isoformat()
                }
            
            return {}
            
        except Exception as e:
            print(f"新浪财经实时价格错误: {e}")
            return {}
    
    def _fetch_realtime_yfinance(self) -> Dict:
        try:
            import yfinance as yf
            
            for ticker in ['GC=F', 'GLD']:
                try:
                    gold = yf.Ticker(ticker)
                    info = gold.info
                    
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                    if current_price > 0:
                        return {
                            'price': current_price,
                            'change': info.get('previousClose', 0) - current_price,
                            'change_percent': ((current_price - info.get('previousClose', 0)) / info.get('previousClose', 1)) * 100,
                            'high': info.get('dayHigh', current_price),
                            'low': info.get('dayLow', current_price),
                            'volume': info.get('volume', 0),
                            'timestamp': datetime.now().isoformat()
                        }
                except:
                    continue
            
            return {}
            
        except Exception as e:
            print(f"yFinance 实时价格错误: {e}")
            return {}
    
    def fetch_intraday_data(self, interval: str = '1h') -> pd.DataFrame:
        try:
            import yfinance as yf
            
            for ticker in ['GC=F', 'GLD']:
                try:
                    gold = yf.Ticker(ticker)
                    df = gold.history(period='5d', interval=interval)
                    
                    if not df.empty:
                        df.reset_index(inplace=True)
                        if 'Datetime' in df.columns:
                            df['Datetime'] = pd.to_datetime(df['Datetime'])
                        elif 'Date' in df.columns:
                            df['Datetime'] = pd.to_datetime(df['Date'])
                        
                        df = df.sort_values('Datetime')
                        return df
                except:
                    continue
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"获取日内数据时出错: {e}")
            return pd.DataFrame()
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        
        df['Daily_Return'] = df['Close'].pct_change() * 100
        df['Log_Return'] = np.log(df['Close'] / df['Close'].shift(1))
        df['High_Low_Range'] = ((df['High'] - df['Low']) / df['Low']) * 100
        
        # 清理NaN值
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        return df
    
    def get_latest_data(self) -> pd.DataFrame:
        df = self.fetch_historical_data()
        if not df.empty:
            df = self.calculate_returns(df)
            
            # 检查历史数据是否包含今天的数据
            today = datetime.now().strftime('%Y-%m-%d')
            latest_date = df['Date'].max().strftime('%Y-%m-%d')
            
            if latest_date != today:
                # 获取实时价格
                realtime_data = self.fetch_realtime_price()
                if realtime_data and realtime_data.get('price', 0) > 0:
                    # 添加今天的数据到历史数据中
                    today_data = {
                        'Date': datetime.now(),
                        'Open': realtime_data.get('price', 0),
                        'High': realtime_data.get('high', realtime_data.get('price', 0)),
                        'Low': realtime_data.get('low', realtime_data.get('price', 0)),
                        'Close': realtime_data.get('price', 0),
                        'Volume': realtime_data.get('volume', 0)
                    }
                    today_df = pd.DataFrame([today_data])
                    df = pd.concat([df, today_df], ignore_index=True)
                    df = self.calculate_returns(df)
                    print(f"已添加今天({today})的数据到历史数据中")
        return df
    
    def fetch_multiple_tickers(self, tickers: List[str]) -> Dict[str, pd.DataFrame]:
        data = {}
        for ticker in tickers:
            try:
                temp_ticker = self.ticker
                self.ticker = ticker
                df = self.fetch_historical_data()
                if not df.empty:
                    data[ticker] = df
                self.ticker = temp_ticker
            except Exception as e:
                print(f"获取 {ticker} 数据时出错: {e}")
        return data
    
    def _load_from_cache(self) -> pd.DataFrame:
        """从本地缓存加载数据"""
        if not os.path.exists(self.cache_file):
            return pd.DataFrame()
        
        try:
            # 检查缓存文件的修改时间
            cache_mtime = os.path.getmtime(self.cache_file)
            cache_age_hours = (datetime.now().timestamp() - cache_mtime) / 3600
            
            if cache_age_hours > self.cache_expiry_hours:
                print("缓存已过期")
                return pd.DataFrame()
            
            # 加载缓存数据
            df = pd.read_csv(self.cache_file)
            if not df.empty and 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                return df
        except Exception as e:
            print(f"从缓存加载数据失败: {e}")
        
        return pd.DataFrame()
    
    def _save_to_cache(self, df: pd.DataFrame) -> None:
        """将数据保存到本地缓存"""
        if not df.empty:
            try:
                df.to_csv(self.cache_file, index=False)
                print(f"数据已缓存到 {self.cache_file}")
            except Exception as e:
                print(f"保存数据到缓存失败: {e}")
