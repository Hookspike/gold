import requests
import time

def get_realtime_gold():
    # 新浪财经的实时接口
    # list=hf_XAU 代表伦敦金 (Spot Gold)
    # list=hf_GC  代表COMEX黄金期货
    url = "http://hq.sinajs.cn/list=hf_XAU"
    
    headers = {
        "Referer": "https://finance.sina.com.cn/"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # 返回的数据格式是：var hq_str_hf_XAU="最新价,涨跌幅,买价,卖价,..."
            text = response.text
            
            # 解析字符串
            content = text.split('"')[1]
            data_list = content.split(',')
            
            # 提取核心字段 (不同品种字段位置可能微调，通常第0个是最新价)
            current_price = float(data_list[0]) # 最新价
            # data_list[1] 通常是涨跌幅(%)，有时候可能是空值，视具体品种
            # data_list[2] 买价
            # data_list[3] 卖价
            # data_list[12] 只有日期，没有具体的秒级时间，时间通常取系统当前时间
            
            return {
                "symbol": "伦敦金(XAUUSD)",
                "price": current_price,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        print(f"Error: {e}")
        return None

# 模拟实时获取（每3秒刷新一次）
print("开始监控金价 (按 Ctrl+C 停止)...")
while True:
    data = get_realtime_gold()
    if data:
        print(f"[{data['timestamp']}] 现价: {data['price']}")
    time.sleep(3)