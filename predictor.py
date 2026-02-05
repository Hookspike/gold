import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class GoldPricePredictor:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame, sentiment_score: float = 0) -> pd.DataFrame:
        if df.empty or len(df) < 10:
            return pd.DataFrame()
        
        feature_df = df.copy()
        
        feature_df['Price_Change'] = feature_df['Close'].pct_change()
        feature_df['Volume_Change'] = feature_df['Volume'].pct_change()
        feature_df['High_Low_Ratio'] = feature_df['High'] / feature_df['Low']
        feature_df['Open_Close_Ratio'] = feature_df['Open'] / feature_df['Close']
        
        # 根据数据量动态调整滞后特征
        max_lag = min(10, len(feature_df) // 3)
        lags_to_use = [lag for lag in [1, 2, 3, 5, 10] if lag <= max_lag]
        
        for lag in lags_to_use:
            feature_df[f'Close_Lag_{lag}'] = feature_df['Close'].shift(lag)
            feature_df[f'Return_Lag_{lag}'] = feature_df['Price_Change'].shift(lag)
        
        # 根据数据量动态调整移动平均窗口
        ma_windows = []
        if len(feature_df) >= 5:
            ma_windows.append(5)
        if len(feature_df) >= 10:
            ma_windows.append(10)
        if len(feature_df) >= 20:
            ma_windows.append(20)
        if len(feature_df) >= 50:
            ma_windows.append(50)
        
        for window in ma_windows:
            feature_df[f'MA_{window}'] = feature_df['Close'].rolling(window=window).mean()
        
        # MA差异特征
        if 'MA_5' in feature_df.columns:
            feature_df['MA_5_Diff'] = (feature_df['Close'] - feature_df['MA_5']) / feature_df['MA_5']
        if 'MA_20' in feature_df.columns:
            feature_df['MA_20_Diff'] = (feature_df['Close'] - feature_df['MA_20']) / feature_df['MA_20']
        
        # RSI特征
        rsi_window = min(14, len(feature_df) // 2)
        delta = feature_df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
        rs = gain / loss
        feature_df['RSI'] = 100 - (100 / (1 + rs))
        
        # 波动率特征
        vol_window = min(20, len(feature_df) // 2)
        feature_df['Volatility'] = feature_df['Close'].rolling(window=vol_window).std()
        
        feature_df['Sentiment_Score'] = sentiment_score
        
        feature_df = feature_df.dropna()
        
        return feature_df
    
    def select_features(self, df: pd.DataFrame) -> List[str]:
        exclude_cols = ['Date', 'Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 
                       'Daily_Return', 'Log_Return', 'High_Low_Range']
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        return feature_cols
    
    def train(self, df: pd.DataFrame, sentiment_score: float = 0) -> Dict:
        feature_df = self.prepare_features(df, sentiment_score)
        
        if feature_df.empty or len(feature_df) < 10:
            print(f"数据量不足（{len(feature_df) if not feature_df.empty else 0}条），跳过训练")
            self.is_trained = False
            return {'success': False, 'error': 'Insufficient data for training'}
        
        self.feature_columns = self.select_features(feature_df)
        
        X = feature_df[self.feature_columns].values
        y = feature_df['Close'].values
        
        X_scaled = self.scaler.fit_transform(X)
        
        # 根据数据量调整测试集大小
        test_size = max(0.2, min(0.5, 5 / len(feature_df)))
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=42, shuffle=False
        )
        
        results = {}
        for name, model in self.models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                r2 = r2_score(y_test, y_pred)
                
                results[name] = {
                    'mae': mae,
                    'rmse': rmse,
                    'r2': r2,
                    'model': model
                }
            except Exception as e:
                print(f"训练 {name} 模型时出错: {e}")
                results[name] = {'error': str(e)}
        
        self.is_trained = True
        
        return {
            'success': True,
            'results': results,
            'feature_count': len(self.feature_columns),
            'training_samples': len(X_train)
        }
    
    def predict(self, df: pd.DataFrame, days_ahead: int = 7, sentiment_score: float = 0) -> Dict:
        if not self.is_trained:
            return {'success': False, 'error': 'Model not trained yet'}
        
        feature_df = self.prepare_features(df, sentiment_score)
        
        if feature_df.empty:
            return {'success': False, 'error': 'Insufficient data for prediction'}
        
        predictions = {}
        current_features = feature_df[self.feature_columns].iloc[-1:].values
        current_price = df['Close'].iloc[-1]
        
        for day in range(1, days_ahead + 1):
            day_predictions = []
            
            for name, model in self.models.items():
                try:
                    pred = model.predict(current_features)[0]
                    day_predictions.append(pred)
                except:
                    day_predictions.append(current_price)
            
            avg_prediction = np.mean(day_predictions)
            predictions[f'day_{day}'] = {
                'predicted_price': float(avg_prediction),
                'price_change': float(avg_prediction - current_price),
                'price_change_percent': float((avg_prediction - current_price) / current_price * 100),
                'date': (pd.Timestamp.now() + pd.Timedelta(days=day)).strftime('%Y-%m-%d')
            }
            
            current_price = avg_prediction
        
        trend = 'Neutral'
        if predictions['day_1']['price_change_percent'] > 0.5:
            trend = 'Bullish'
        elif predictions['day_1']['price_change_percent'] < -0.5:
            trend = 'Bearish'
        
        return {
            'success': True,
            'predictions': predictions,
            'trend': trend,
            'current_price': float(df['Close'].iloc[-1]),
            'prediction_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def ensemble_predict(self, df: pd.DataFrame, days_ahead: int = 7, 
                       sentiment_score: float = 0, weights: Dict[str, float] = None) -> Dict:
        if weights is None:
            weights = {
                'random_forest': 0.4,
                'gradient_boosting': 0.4,
                'linear_regression': 0.2
            }
        
        base_prediction = self.predict(df, days_ahead, sentiment_score)
        
        if not base_prediction['success']:
            # 如果模型训练失败，使用简单的趋势预测
            return self._simple_predict(df, days_ahead, sentiment_score)
        
        feature_df = self.prepare_features(df, sentiment_score)
        current_features = feature_df[self.feature_columns].iloc[-1:].values
        current_price = df['Close'].iloc[-1]
        
        weighted_predictions = {}
        
        for day in range(1, days_ahead + 1):
            weighted_pred = 0
            for name, model in self.models.items():
                try:
                    pred = model.predict(current_features)[0]
                    weighted_pred += pred * weights.get(name, 0.33)
                except:
                    weighted_pred += current_price * weights.get(name, 0.33)
            
            # 验证预测结果是否合理
            if weighted_pred <= 0 or weighted_pred > current_price * 10 or weighted_pred < current_price * 0.1:
                print(f"预测价格异常（{weighted_pred:.2f}），使用简单预测方法")
                return self._simple_predict(df, days_ahead, sentiment_score)
            
            weighted_predictions[f'day_{day}'] = {
                'predicted_price': float(weighted_pred),
                'price_change': float(weighted_pred - current_price),
                'price_change_percent': float((weighted_pred - current_price) / current_price * 100),
                'date': (pd.Timestamp.now() + pd.Timedelta(days=day)).strftime('%Y-%m-%d')
            }
        
        trend = 'Neutral'
        if weighted_predictions['day_1']['price_change_percent'] > 0.5:
            trend = 'Bullish'
        elif weighted_predictions['day_1']['price_change_percent'] < -0.5:
            trend = 'Bearish'
        
        return {
            'success': True,
            'predictions': weighted_predictions,
            'trend': trend,
            'current_price': float(current_price),
            'weights_used': weights,
            'prediction_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _simple_predict(self, df: pd.DataFrame, days_ahead: int = 7, 
                      sentiment_score: float = 0) -> Dict:
        """改进的趋势预测方法，提高情绪分析权重"""
        if df.empty:
            return {'success': False, 'error': 'No data available'}
        
        current_price = df['Close'].iloc[-1]
        
        # 计算多种移动平均趋势，更全面地分析趋势
        trends = []
        if len(df) >= 3:
            ma3 = df['Close'].tail(3).mean()
            trends.append((current_price - ma3) / ma3 * 100)
        if len(df) >= 5:
            ma5 = df['Close'].tail(5).mean()
            trends.append((current_price - ma5) / ma5 * 100)
        if len(df) >= 10:
            ma10 = df['Close'].tail(10).mean()
            trends.append((current_price - ma10) / ma10 * 100)
        
        # 计算平均趋势
        trend = sum(trends) / len(trends) if trends else 0
        
        # 提高情绪分析对预测的影响权重
        # 增加情绪调整因子的权重
        sentiment_adjustment = sentiment_score * 5  # 从2增加到5
        
        # 考虑价格的均值回归
        # 计算历史价格的平均值作为回归目标
        if len(df) >= 20:
            historical_avg = df['Close'].tail(20).mean()
            mean_reversion = (historical_avg - current_price) / historical_avg * 2  # 均值回归因子
        else:
            mean_reversion = 0
        
        # 综合计算日变化率
        # 趋势占40%，情绪占40%，均值回归占20%
        daily_change = (trend * 0.4 + sentiment_adjustment * 0.4 + mean_reversion * 0.2) / 100
        
        # 限制每日变化率的范围，避免极端预测
        max_daily_change = 0.02  # 最大每日变化率2%
        daily_change = max(-max_daily_change, min(max_daily_change, daily_change))
        
        predictions = {}
        for day in range(1, days_ahead + 1):
            # 考虑趋势的衰减，随着时间推移，趋势影响逐渐减弱
            decay_factor = 1 - (day - 1) * 0.1  # 每天衰减10%
            decay_factor = max(0.5, decay_factor)  # 最低保持50%的影响
            
            # 计算预测价格，考虑趋势衰减
            predicted_price = current_price * (1 + daily_change * day * decay_factor)
            
            predictions[f'day_{day}'] = {
                'predicted_price': float(predicted_price),
                'price_change': float(predicted_price - current_price),
                'price_change_percent': float((predicted_price - current_price) / current_price * 100),
                'date': (pd.Timestamp.now() + pd.Timedelta(days=day)).strftime('%Y-%m-%d')
            }
        
        # 判断趋势
        trend_label = 'Neutral'
        if daily_change > 0.003:
            trend_label = 'Bullish'
        elif daily_change < -0.003:
            trend_label = 'Bearish'
        
        return {
            'success': True,
            'predictions': predictions,
            'trend': trend_label,
            'current_price': float(current_price),
            'prediction_method': 'enhanced_simple_trend',
            'trend_factor': trend,
            'sentiment_factor': sentiment_adjustment,
            'mean_reversion_factor': mean_reversion,
            'prediction_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_feature_importance(self) -> Dict:
        if not self.is_trained:
            return {}
        
        importance = {}
        
        rf_model = self.models['random_forest']
        if hasattr(rf_model, 'feature_importances_'):
            for feature, imp in zip(self.feature_columns, rf_model.feature_importances_):
                importance[feature] = float(imp)
        
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    def calculate_confidence_interval(self, predictions: Dict, confidence: float = 0.95) -> Dict:
        if not predictions.get('success'):
            return {}
        
        z_score = 1.96 if confidence == 0.95 else 1.645
        
        confidence_predictions = {}
        
        for day_key, pred_data in predictions['predictions'].items():
            price = pred_data['predicted_price']
            std_dev = abs(price * 0.02)
            
            margin = z_score * std_dev
            
            confidence_predictions[day_key] = {
                'predicted_price': price,
                'lower_bound': price - margin,
                'upper_bound': price + margin,
                'margin': margin,
                'confidence': confidence
            }
        
        return confidence_predictions
