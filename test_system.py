#!/usr/bin/env python3
# 系统功能测试脚本

import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_api_endpoint(endpoint):
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n=== 测试 {endpoint} ===")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"返回数据类型: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"返回键值: {list(data.keys())}")
                    # 检查关键数据
                    if 'price' in data:
                        print(f"黄金价格: {data['price']}")
                    if 'sentiment' in data:
                        print(f"情绪指数: {data['sentiment']}")
                    if 'predictions' in data:
                        print(f"预测数据条数: {len(data['predictions'])}")
                    if 'technical' in data:
                        print(f"技术指标条数: {len(data['technical'])}")
                elif isinstance(data, list):
                    print(f"返回数据条数: {len(data)}")
                    if data:
                        print(f"第一条数据: {json.dumps(data[0], ensure_ascii=False)[:200]}...")
                
                print("✓ API测试通过")
                return True
            except json.JSONDecodeError:
                print("✗ 返回数据不是有效的JSON")
                print(f"返回内容: {response.text[:200]}...")
                return False
        else:
            print(f"✗ API返回错误状态码: {response.status_code}")
            print(f"错误信息: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"✗ 请求失败: {e}")
        return False

def main():
    """测试所有API端点"""
    print("开始系统功能测试...")
    print(f"测试地址: {BASE_URL}")
    print("=" * 50)
    
    endpoints = [
        '/api/price',           # 黄金价格
        '/api/sentiment',       # 市场情绪
        '/api/predictions',     # 价格预测
        '/api/technical',       # 技术指标
        '/api/support-resistance',  # 支撑阻力位
        '/api/summary'          # 市场总结
    ]
    
    results = []
    for endpoint in endpoints:
        success = test_api_endpoint(endpoint)
        results.append((endpoint, success))
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    for endpoint, success in results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"{endpoint}: {status}")
    
    # 检查整体状态
    all_success = all([success for _, success in results])
    if all_success:
        print("\n🎉 所有API测试通过！")
    else:
        print("\n⚠️  部分API测试失败，请检查系统配置")

if __name__ == '__main__':
    main()