import requests

url = "http://hq.sinajs.cn/list=hf_XAU"
headers = {
    "Referer": "https://finance.sina.com.cn/"
}

try:
    response = requests.get(url, headers=headers, timeout=5)
    if response.status_code == 200:
        print("Response status:", response.status_code)
        print("Full response:", response.text)
        
        # 解析字符串
        content = response.text.split('"')[1]
        data_list = content.split(',')
        
        print("\nParsed data:")
        for i, item in enumerate(data_list):
            print(f"Index {i}: {item}")
    else:
        print("Failed to get data:", response.status_code)
except Exception as e:
    print(f"Error: {e}")