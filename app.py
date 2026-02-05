import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
from data_fetcher import GoldDataFetcher
from technical_analysis import TechnicalAnalyzer
from sentiment_analysis import SentimentAnalyzer
from predictor import GoldPricePredictor
from config import Config

st.set_page_config(
    page_title="黄金价格预测系统",
    page_icon="🥇",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600)
def load_data():
    fetcher = GoldDataFetcher()
    df = fetcher.get_latest_data()
    return df

@st.cache_data(ttl=1800)
def analyze_technical(df):
    analyzer = TechnicalAnalyzer()
    return analyzer.calculate_all_indicators(df)

@st.cache_data(ttl=1800)
def analyze_sentiment():
    analyzer = SentimentAnalyzer()
    news = analyzer.fetch_gold_news()
    sentiment_df = analyzer.analyze_news_sentiment(news)
    return sentiment_df

def plot_price_chart(df, title="黄金价格走势"):
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=df['Date'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    ))
    
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['SMA_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='orange', width=1)
        ))
    
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['SMA_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='blue', width=1)
        ))
    
    if 'BB_High' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['BB_High'],
            mode='lines',
            name='BB Upper',
            line=dict(color='gray', width=0.5, dash='dash'),
            fill=None
        ))
    
    if 'BB_Low' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['BB_Low'],
            mode='lines',
            name='BB Lower',
            line=dict(color='gray', width=0.5, dash='dash'),
            fill='tonexty',
            fillcolor='rgba(128,128,128,0.1)'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='日期',
        yaxis_title='价格 (USD)',
        template='plotly_dark',
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def plot_indicators(df):
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('RSI', 'MACD', '成交量'),
        vertical_spacing=0.05,
        row_heights=[0.33, 0.33, 0.34]
    )
    
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['RSI'],
            mode='lines',
            name='RSI',
            line=dict(color='purple')
        ), row=1, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
    
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MACD'],
            mode='lines',
            name='MACD',
            line=dict(color='blue')
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MACD_Signal'],
            mode='lines',
            name='Signal',
            line=dict(color='orange')
        ), row=2, col=1)
    
    fig.add_trace(go.Bar(
        x=df['Date'],
        y=df['Volume'],
        name='Volume',
        marker_color='rgba(0, 100, 255, 0.5)'
    ), row=3, col=1)
    
    fig.update_layout(
        template='plotly_dark',
        height=600,
        showlegend=True
    )
    
    return fig

def plot_predictions(predictions):
    if not predictions.get('success'):
        return None
    
    dates = []
    prices = []
    current_date = datetime.now()
    current_price = predictions['current_price']
    
    dates.append(current_date)
    prices.append(current_price)
    
    for day in range(1, len(predictions['predictions']) + 1):
        day_key = f'day_{day}'
        if day_key in predictions['predictions']:
            pred_date = current_date + timedelta(days=day)
            pred_price = predictions['predictions'][day_key]['predicted_price']
            dates.append(pred_date)
            prices.append(pred_price)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines+markers',
        name='预测价格',
        line=dict(color='gold', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=[dates[0]],
        y=[prices[0]],
        mode='markers',
        name='当前价格',
        marker=dict(color='red', size=12, symbol='circle')
    ))
    
    trend_color = 'green' if predictions['trend'] == 'Bullish' else 'red' if predictions['trend'] == 'Bearish' else 'gray'
    
    fig.update_layout(
        title=f"黄金价格预测 - 趋势: {predictions['trend']}",
        xaxis_title='日期',
        yaxis_title='预测价格 (USD)',
        template='plotly_dark',
        height=400
    )
    
    return fig

def plot_sentiment(sentiment_df):
    if sentiment_df.empty:
        return None
    
    fig = go.Figure()
    
    colors = ['green' if x > 0 else 'red' if x < 0 else 'gray' for x in sentiment_df['compound']]
    
    fig.add_trace(go.Bar(
        x=sentiment_df['publishedAt'],
        y=sentiment_df['compound'],
        name='情绪指数',
        marker_color=colors
    ))
    
    fig.add_hline(y=0.1, line_dash="dash", line_color="green", annotation_text="积极阈值")
    fig.add_hline(y=-0.1, line_dash="dash", line_color="red", annotation_text="消极阈值")
    
    fig.update_layout(
        title='市场情绪分析',
        xaxis_title='日期',
        yaxis_title='情绪指数',
        template='plotly_dark',
        height=400
    )
    
    return fig

def main():
    st.title("🥇 黄金价格预测走势系统")
    st.markdown("---")
    
    with st.sidebar:
        st.header("⚙️ 设置")
        
        prediction_days = st.slider("预测天数", 1, 30, 7)
        
        show_indicators = st.multiselect(
            "显示技术指标",
            ['SMA', 'RSI', 'MACD', 'Bollinger Bands', 'Stochastic'],
            default=['SMA', 'RSI', 'MACD', 'Bollinger Bands']
        )
        
        refresh_data = st.button("🔄 刷新数据")
        
        st.markdown("---")
        st.markdown("### 📊 系统信息")
        st.info(f"数据源: {Config.DATA_SOURCE}\n股票代码: {Config.GOLD_TICKER}")
    
    if refresh_data or 'data_loaded' not in st.session_state:
        with st.spinner("正在加载数据..."):
            df = load_data()
            st.session_state['data_loaded'] = True
            st.session_state['df'] = df
    else:
        df = st.session_state.get('df', pd.DataFrame())
    
    if df.empty:
        st.error("无法加载黄金数据，请检查网络连接或配置")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_price = df['Close'].iloc[-1]
        price_change = df['Close'].iloc[-1] - df['Close'].iloc[-2]
        price_change_pct = (price_change / df['Close'].iloc[-2]) * 100
        
        st.metric(
            "当前价格",
            f"${current_price:.2f}",
            f"{price_change_pct:+.2f}%"
        )
    
    with col2:
        high_price = df['High'].iloc[-1]
        low_price = df['Low'].iloc[-1]
        st.metric("今日最高", f"${high_price:.2f}")
    
    with col3:
        volume = df['Volume'].iloc[-1]
        st.metric("成交量", f"{volume:,.0f}")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 价格走势", "🔬 技术分析", "📰 情绪分析", "🔮 价格预测"])
    
    with tab1:
        st.subheader("黄金价格走势图")
        fig_price = plot_price_chart(df)
        st.plotly_chart(fig_price, use_container_width=True)
        
        st.subheader("价格统计")
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        with stats_col1:
            st.metric("30天平均", f"${df['Close'].tail(30).mean():.2f}")
        with stats_col2:
            st.metric("52周最高", f"${df['High'].max():.2f}")
        with stats_col3:
            st.metric("52周最低", f"${df['Low'].min():.2f}")
    
    with tab2:
        st.subheader("技术指标分析")
        
        with st.spinner("计算技术指标..."):
            df_tech = analyze_technical(df)
        
        fig_indicators = plot_indicators(df_tech)
        st.plotly_chart(fig_indicators, use_container_width=True)
        
        st.subheader("技术指标详情")
        
        latest_rsi = df_tech['RSI'].iloc[-1] if 'RSI' in df_tech.columns else 0
        latest_macd = df_tech['MACD'].iloc[-1] if 'MACD' in df_tech.columns else 0
        latest_signal = df_tech['Overall_Signal'].iloc[-1] if 'Overall_Signal' in df_tech.columns else 0
        
        tech_col1, tech_col2, tech_col3 = st.columns(3)
        with tech_col1:
            rsi_status = "超买" if latest_rsi > 70 else "超卖" if latest_rsi < 30 else "中性"
            st.metric("RSI", f"{latest_rsi:.2f}", rsi_status)
        with tech_col2:
            macd_status = "看涨" if latest_macd > 0 else "看跌"
            st.metric("MACD", f"{latest_macd:.4f}", macd_status)
        with tech_col3:
            signal_status = "买入" if latest_signal > 0.3 else "卖出" if latest_signal < -0.3 else "持有"
            st.metric("综合信号", f"{latest_signal:.2f}", signal_status)
        
        analyzer = TechnicalAnalyzer()
        support_resistance = analyzer.get_support_resistance(df_tech)
        
        st.subheader("支撑位和阻力位")
        sr_col1, sr_col2 = st.columns(2)
        with sr_col1:
            st.write("**支撑位:**")
            for level in support_resistance.get('support', []):
                st.write(f"  - ${level:.2f}")
        with sr_col2:
            st.write("**阻力位:**")
            for level in support_resistance.get('resistance', []):
                st.write(f"  - ${level:.2f}")
    
    with tab3:
        st.subheader("市场情绪分析")
        
        with st.spinner("分析市场情绪..."):
            sentiment_df = analyze_sentiment()
        
        if not sentiment_df.empty:
            fig_sentiment = plot_sentiment(sentiment_df)
            st.plotly_chart(fig_sentiment, use_container_width=True)
            
            analyzer = SentimentAnalyzer()
            overall = analyzer.calculate_overall_sentiment(sentiment_df)
            
            sentiment_col1, sentiment_col2, sentiment_col3 = st.columns(3)
            with sentiment_col1:
                st.metric("情绪指数", f"{overall['avg_compound']:.3f}", overall['sentiment_label'])
            with sentiment_col2:
                st.metric("积极新闻", overall['positive_count'])
            with sentiment_col3:
                st.metric("消极新闻", overall['negative_count'])
            
            st.subheader("最新新闻")
            for idx, row in sentiment_df.head(5).iterrows():
                sentiment_emoji = "📈" if row['compound'] > 0 else "📉" if row['compound'] < 0 else "➡️"
                st.write(f"{sentiment_emoji} **{row['title']}**")
                st.write(f"   来源: {row['source']} | 情绪: {row['compound']:.3f}")
                st.write(f"   [阅读更多]({row['url']})")
                st.markdown("---")
        else:
            st.warning("暂无情绪数据")
    
    with tab4:
        st.subheader("价格预测")
        
        with st.spinner("训练模型并预测..."):
            predictor = GoldPricePredictor()
            
            sentiment_score = 0
            if not sentiment_df.empty:
                sentiment_score = sentiment_df['compound'].mean()
            
            train_result = predictor.train(df, sentiment_score)
            
            if train_result['success']:
                predictions = predictor.ensemble_predict(df, prediction_days, sentiment_score)
                
                if predictions['success']:
                    fig_pred = plot_predictions(predictions)
                    st.plotly_chart(fig_pred, use_container_width=True)
                    
                    st.subheader("预测详情")
                    pred_df = pd.DataFrame(predictions['predictions']).T
                    pred_df.index = [f"第{i}天" for i in range(1, len(pred_df) + 1)]
                    st.dataframe(pred_df, use_container_width=True)
                    
                    st.subheader("预测总结")
                    st.write(f"**当前价格:** ${predictions['current_price']:.2f}")
                    st.write(f"**预测趋势:** {predictions['trend']}")
                    
                    confidence = predictor.calculate_confidence_interval(predictions)
                    if confidence:
                        st.write(f"**置信区间 (95%):**")
                        for day_key, conf in confidence.items():
                            st.write(f"  {day_key}: ${conf['lower_bound']:.2f} - ${conf['upper_bound']:.2f}")
                    
                    feature_importance = predictor.get_feature_importance()
                    if feature_importance:
                        st.subheader("特征重要性")
                        importance_df = pd.DataFrame.from_dict(feature_importance, orient='index', columns=['重要性'])
                        importance_df = importance_df.head(10)
                        st.bar_chart(importance_df)
                else:
                    st.error(f"预测失败: {predictions.get('error', '未知错误')}")
            else:
                st.error(f"模型训练失败: {train_result.get('error', '未知错误')}")

if __name__ == "__main__":
    main()
