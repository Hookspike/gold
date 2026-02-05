from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from data_fetcher import GoldDataFetcher
from technical_analysis import TechnicalAnalyzer
from sentiment_analysis import SentimentAnalyzer
from predictor import GoldPricePredictor
from config import Config
import pandas as pd
from datetime import datetime
import threading
import time
import psutil
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gold_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

data_cache = {
    'price_data': None,
    'technical_data': None,
    'sentiment_data': None,
    'predictions': None,
    'last_update': None
}

# 性能监控数据
performance_metrics = {
    'update_count': 0,
    'last_update_duration': 0,
    'api_call_count': 0,
    'error_count': 0,
    'start_time': datetime.now()
}

def update_data():
    start_time = time.time()
    logger.info("开始更新数据...")
    
    try:
        fetcher = GoldDataFetcher()
        tech_analyzer = TechnicalAnalyzer()
        sentiment_analyzer = SentimentAnalyzer()
        predictor = GoldPricePredictor()
        
        df = fetcher.get_latest_data()
        
        # 获取新闻和情绪分析
        news = sentiment_analyzer.fetch_gold_news()
        sentiment_df = sentiment_analyzer.analyze_news_sentiment(news)
        sentiment_score = sentiment_df['compound'].mean() if not sentiment_df.empty else 0
        
        # 初始化默认值
        df_tech = pd.DataFrame()
        predictions = {'success': False, 'error': 'No data available'}
        support_resistance = {'support': [], 'resistance': []}
        overall_sentiment = {'avg_compound': 0, 'positive_count': 0, 'negative_count': 0, 'neutral_count': 0}
        fear_greed = {'index': 50, 'label': 'Neutral'}
        
        if not df.empty:
            df_tech = tech_analyzer.calculate_all_indicators(df)
            
            predictor.train(df, sentiment_score)
            predictions = predictor.ensemble_predict(df, Config.PREDICTION_DAYS, sentiment_score)
            
            support_resistance = tech_analyzer.get_support_resistance(df_tech)
            
            overall_sentiment = sentiment_analyzer.calculate_overall_sentiment(sentiment_df)
            fear_greed = sentiment_analyzer.analyze_market_fear_greed(df)
        
        # 确保初始化所有必要的键
        data_cache['price_data'] = df.to_dict('records') if not df.empty else []
        data_cache['technical_data'] = df_tech.to_dict('records') if not df_tech.empty else []
        data_cache['sentiment_data'] = sentiment_df.to_dict('records') if not sentiment_df.empty else []
        data_cache['predictions'] = predictions
        data_cache['support_resistance'] = support_resistance
        data_cache['overall_sentiment'] = overall_sentiment
        data_cache['fear_greed'] = fear_greed
        data_cache['realtime_price'] = fetcher.fetch_realtime_price()
        data_cache['last_update'] = datetime.now().isoformat()
        
        # 更新性能指标
        duration = time.time() - start_time
        performance_metrics['update_count'] += 1
        performance_metrics['last_update_duration'] = duration
        
        logger.info(f"数据更新完成，耗时: {duration:.2f}秒")
        
    except Exception as e:
        logger.error(f"数据更新失败: {e}", exc_info=True)
        performance_metrics['error_count'] += 1
        raise

def background_updater():
    while True:
        try:
            update_data()
            time.sleep(Config.UPDATE_INTERVAL_HOURS * 3600)
        except Exception as e:
            logger.error(f"后台更新出错: {e}", exc_info=True)
            time.sleep(300)

@app.route('/api/health')
def health_check():
    """
    系统健康检查API
    返回系统各组件的健康状态和性能指标
    """
    try:
        # 检查数据缓存状态
        cache_status = {
            'price_data': len(data_cache.get('price_data', [])) > 0,
            'technical_data': len(data_cache.get('technical_data', [])) > 0,
            'sentiment_data': len(data_cache.get('sentiment_data', [])) > 0,
            'predictions': data_cache.get('predictions') is not None,
            'last_update': data_cache.get('last_update')
        }
        
        # 检查各服务状态
        services_status = {
            'data_fetcher': True,
            'predictor': True,
            'sentiment_analyzer': True,
            'technical_analyzer': True
        }
        
        # 计算系统运行时间
        uptime = (datetime.now() - performance_metrics['start_time']).total_seconds()
        uptime_hours = uptime / 3600
        
        # 获取系统资源使用情况
        try:
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            cpu_percent = psutil.cpu_percent(interval=1)
        except:
            memory_usage = 0
            cpu_percent = 0
        
        # 判断整体健康状态
        all_services_healthy = all(services_status.values())
        cache_fresh = cache_status['last_update'] is not None
        recent_update = False
        
        if cache_fresh:
            try:
                last_update_time = pd.to_datetime(cache_status['last_update'])
                time_since_update = (datetime.now() - last_update_time).total_seconds()
                recent_update = time_since_update < 7200  # 2小时内更新过
            except:
                recent_update = False
        
        overall_status = 'healthy' if (all_services_healthy and recent_update) else 'degraded'
        
        health_data = {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'uptime_hours': round(uptime_hours, 2),
            'services': services_status,
            'cache': cache_status,
            'performance': {
                'update_count': performance_metrics['update_count'],
                'last_update_duration': round(performance_metrics['last_update_duration'], 2),
                'api_call_count': performance_metrics['api_call_count'],
                'error_count': performance_metrics['error_count'],
                'memory_usage_mb': round(memory_usage, 2),
                'cpu_percent': cpu_percent
            },
            'data_quality': {
                'price_data_count': len(data_cache.get('price_data', [])),
                'sentiment_data_count': len(data_cache.get('sentiment_data', [])),
                'predictions_available': data_cache.get('predictions') is not None
            }
        }
        
        return jsonify(health_data)
    
    except Exception as e:
        logger.error(f"健康检查失败: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/price')
def get_price_data():
    performance_metrics['api_call_count'] += 1
    if data_cache['price_data'] is None:
        update_data()
    return jsonify({
        'success': True,
        'data': data_cache['price_data'],
        'last_update': data_cache['last_update']
    })

@app.route('/api/realtime')
def get_realtime_price():
    performance_metrics['api_call_count'] += 1
    if data_cache['realtime_price'] is None:
        update_data()
    return jsonify({
        'success': True,
        'data': data_cache['realtime_price'],
        'last_update': data_cache['last_update']
    })

@app.route('/api/technical')
def get_technical_data():
    performance_metrics['api_call_count'] += 1
    if data_cache['technical_data'] is None:
        update_data()
    return jsonify({
        'success': True,
        'data': data_cache['technical_data'],
        'last_update': data_cache['last_update']
    })

@app.route('/api/sentiment')
def get_sentiment_data():
    performance_metrics['api_call_count'] += 1
    if data_cache['sentiment_data'] is None:
        update_data()
    return jsonify({
        'success': True,
        'data': data_cache['sentiment_data'],
        'overall': data_cache['overall_sentiment'],
        'fear_greed': data_cache['fear_greed'],
        'last_update': data_cache['last_update']
    })

@app.route('/api/predictions')
def get_predictions():
    performance_metrics['api_call_count'] += 1
    if data_cache['predictions'] is None:
        update_data()
    
    predictions_data = data_cache['predictions']
    actual_predictions = predictions_data.get('predictions', {}) if isinstance(predictions_data, dict) else {}
    
    return jsonify({
        'success': True,
        'data': {
            'predictions': actual_predictions,
            'current_price': data_cache.get('realtime_price', {}).get('price', 0),
            'trend': 'Bullish' if data_cache.get('overall_sentiment', {}).get('avg_compound', 0) > 0.1 else 'Bearish' if data_cache.get('overall_sentiment', {}).get('avg_compound', 0) < -0.1 else 'Neutral'
        },
        'last_update': data_cache['last_update']
    })

@app.route('/api/support-resistance')
def get_support_resistance():
    performance_metrics['api_call_count'] += 1
    if data_cache['support_resistance'] is None:
        update_data()
    return jsonify({
        'success': True,
        'data': data_cache['support_resistance'],
        'last_update': data_cache['last_update']
    })

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    try:
        update_data()
        return jsonify({
            'success': True,
            'message': '数据刷新成功',
            'last_update': data_cache['last_update']
        })
    except Exception as e:
        logger.error(f"数据刷新失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/summary')
def get_summary():
    performance_metrics['api_call_count'] += 1
    if data_cache['price_data'] is None:
        update_data()
    
    latest_price = data_cache['price_data'][-1] if data_cache['price_data'] else {}
    latest_tech = data_cache['technical_data'][-1] if data_cache['technical_data'] else {}
    realtime_price = data_cache['realtime_price'] or {}
    
    return jsonify({
        'success': True,
        'data': {
            'current_price': realtime_price.get('price', latest_price.get('Close', 0)),
            'high': realtime_price.get('high', latest_price.get('High', 0)),
            'low': realtime_price.get('low', latest_price.get('Low', 0)),
            'volume': realtime_price.get('volume', latest_price.get('Volume', 0)),
            'rsi': latest_tech.get('RSI', 0),
            'macd': latest_tech.get('MACD', 0),
            'overall_signal': latest_tech.get('Overall_Signal', 0),
            'sentiment': data_cache['overall_sentiment'],
            'fear_greed': data_cache['fear_greed'],
            'predictions': data_cache['predictions'],
            'realtime': realtime_price
        },
        'last_update': data_cache['last_update']
    })

if __name__ == '__main__':
    print("正在初始化数据...")
    update_data()
    
    print("启动后台数据更新线程...")
    updater_thread = threading.Thread(target=background_updater, daemon=True)
    updater_thread.start()
    
    print("=" * 60)
    print("🥇 黄金价格预测系统 - 后端服务")
    print("=" * 60)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: http://localhost:5000")
    print(f"前端地址: http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
