import pandas as pd
import numpy as np
from ta import add_all_ta_features
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import MFIIndicator
from typing import Dict, List

class TechnicalAnalyzer:
    def __init__(self):
        self.indicators = {}
    
    def calculate_moving_averages(self, df: pd.DataFrame, periods: List[int] = [5, 10, 20, 50, 200]) -> pd.DataFrame:
        if df.empty:
            return df
        
        for period in periods:
            df[f'SMA_{period}'] = SMAIndicator(close=df['Close'], window=period).sma_indicator()
            df[f'EMA_{period}'] = EMAIndicator(close=df['Close'], window=period).ema_indicator()
        
        df['MA_Cross_Signal'] = 0
        if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
            df.loc[df['SMA_20'] > df['SMA_50'], 'MA_Cross_Signal'] = 1
            df.loc[df['SMA_20'] < df['SMA_50'], 'MA_Cross_Signal'] = -1
        
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        if df.empty:
            return df
        
        rsi = RSIIndicator(close=df['Close'], window=period)
        df['RSI'] = rsi.rsi()
        
        df['RSI_Signal'] = 0
        df.loc[df['RSI'] > 70, 'RSI_Signal'] = -1
        df.loc[df['RSI'] < 30, 'RSI_Signal'] = 1
        
        return df
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        if df.empty:
            return df
        
        macd = MACD(close=df['Close'], window_fast=fast, window_slow=slow, window_sign=signal)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Diff'] = macd.macd_diff()
        
        df['MACD_Cross_Signal'] = 0
        df.loc[df['MACD'] > df['MACD_Signal'], 'MACD_Cross_Signal'] = 1
        df.loc[df['MACD'] < df['MACD_Signal'], 'MACD_Cross_Signal'] = -1
        
        return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        if df.empty:
            return df
        
        bb = BollingerBands(close=df['Close'], window=period, window_dev=std_dev)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Mid'] = bb.bollinger_mavg()
        df['BB_Low'] = bb.bollinger_lband()
        df['BB_Width'] = bb.bollinger_wband()
        df['BB_Pct'] = bb.bollinger_pband()
        
        df['BB_Signal'] = 0
        df.loc[df['Close'] < df['BB_Low'], 'BB_Signal'] = 1
        df.loc[df['Close'] > df['BB_High'], 'BB_Signal'] = -1
        
        return df
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        if df.empty:
            return df
        
        stoch = StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'], 
                                     window=k_period, smooth_window=d_period)
        df['Stoch_K'] = stoch.stoch()
        df['Stoch_D'] = stoch.stoch_signal()
        
        df['Stoch_Signal'] = 0
        df.loc[df['Stoch_K'] < 20, 'Stoch_Signal'] = 1
        df.loc[df['Stoch_K'] > 80, 'Stoch_Signal'] = -1
        
        return df
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        if df.empty:
            return df
        
        atr = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=period)
        df['ATR'] = atr.average_true_range()
        
        df['ATR_Pct'] = (df['ATR'] / df['Close']) * 100
        
        return df
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        
        # 确保数据按日期排序
        df = df.sort_values('Date')
        
        # 计算各个技术指标
        df = self.calculate_moving_averages(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_stochastic(df)
        df = self.calculate_atr(df)
        
        # 计算综合信号
        df['Overall_Signal'] = (
            df['MA_Cross_Signal'].fillna(0) * 0.2 +
            df['RSI_Signal'].fillna(0) * 0.2 +
            df['MACD_Cross_Signal'].fillna(0) * 0.2 +
            df['BB_Signal'].fillna(0) * 0.2 +
            df['Stoch_Signal'].fillna(0) * 0.2
        )
        
        # 智能填充NaN值，避免所有指标都显示为0
        # 对于移动平均线，使用最近的有效值
        for col in df.columns:
            if col.startswith('SMA_') or col.startswith('EMA_'):
                df[col] = df[col].ffill().bfill().fillna(df['Close'])
        
        # 对于RSI，使用默认值50（中性）
        df['RSI'] = df['RSI'].fillna(50)
        
        # 对于MACD，使用0（中性）
        df['MACD'] = df['MACD'].fillna(0)
        df['MACD_Signal'] = df['MACD_Signal'].fillna(0)
        df['MACD_Diff'] = df['MACD_Diff'].fillna(0)
        
        # 对于布林带，使用基于收盘价的默认值
        df['BB_Mid'] = df['BB_Mid'].fillna(df['Close'])
        df['BB_High'] = df['BB_High'].fillna(df['Close'] * 1.02)
        df['BB_Low'] = df['BB_Low'].fillna(df['Close'] * 0.98)
        df['BB_Width'] = df['BB_Width'].fillna(2)
        df['BB_Pct'] = df['BB_Pct'].fillna(0.5)
        
        # 对于随机指标，使用默认值50（中性）
        df['Stoch_K'] = df['Stoch_K'].fillna(50)
        df['Stoch_D'] = df['Stoch_D'].fillna(50)
        
        # 对于ATR，使用基于价格范围的默认值
        df['ATR'] = df['ATR'].fillna((df['High'] - df['Low']).mean())
        df['ATR_Pct'] = df['ATR_Pct'].fillna(((df['High'] - df['Low']).mean() / df['Close']) * 100)
        
        # 对于信号值，使用0（中性）
        signal_cols = ['MA_Cross_Signal', 'RSI_Signal', 'MACD_Cross_Signal', 'BB_Signal', 'Stoch_Signal']
        for col in signal_cols:
            df[col] = df[col].fillna(0)
        
        # 最后填充任何剩余的NaN值
        numeric_columns = df.select_dtypes(include=['number']).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        return df
    
    def get_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        if df.empty:
            return {}
        
        recent_df = df.tail(window)
        
        support_levels = []
        resistance_levels = []
        
        for i in range(2, len(recent_df) - 2):
            if (recent_df.iloc[i]['Low'] < recent_df.iloc[i-1]['Low'] and 
                recent_df.iloc[i]['Low'] < recent_df.iloc[i-2]['Low'] and
                recent_df.iloc[i]['Low'] < recent_df.iloc[i+1]['Low'] and
                recent_df.iloc[i]['Low'] < recent_df.iloc[i+2]['Low']):
                support_levels.append(recent_df.iloc[i]['Low'])
            
            if (recent_df.iloc[i]['High'] > recent_df.iloc[i-1]['High'] and 
                recent_df.iloc[i]['High'] > recent_df.iloc[i-2]['High'] and
                recent_df.iloc[i]['High'] > recent_df.iloc[i+1]['High'] and
                recent_df.iloc[i]['High'] > recent_df.iloc[i+2]['High']):
                resistance_levels.append(recent_df.iloc[i]['High'])
        
        current_price = df.iloc[-1]['Close']
        
        # 如果没有找到支撑和阻力位，使用基于移动平均线和价格范围的默认值
        if not support_levels:
            # 计算基于价格范围的支撑位
            price_range = recent_df['High'].max() - recent_df['Low'].min()
            support_levels = [
                current_price - price_range * 0.3,
                current_price - price_range * 0.6,
                current_price - price_range * 0.9
            ]
        
        if not resistance_levels:
            # 计算基于价格范围的阻力位
            price_range = recent_df['High'].max() - recent_df['Low'].min()
            resistance_levels = [
                current_price + price_range * 0.3,
                current_price + price_range * 0.6,
                current_price + price_range * 0.9
            ]
        
        return {
            'support': sorted(set(support_levels))[-3:] if support_levels else [],
            'resistance': sorted(set(resistance_levels))[:3] if resistance_levels else [],
            'current_price': current_price
        }
