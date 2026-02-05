#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试新闻获取功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def test_akshare():
    """测试AkShare模块是否安装"""
    try:
        import akshare as ak
        print("✅ AkShare模块已安装")
        return True
    except ImportError as e:
        print(f"❌ AkShare模块未安装: {e}")
        return False


def test_jin10():
    """测试金十数据是否可访问"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = 'https://www.jin10.com/'
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ 金十数据可访问")
            return True
        else:
            print(f"❌ 金十数据访问失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 金十数据访问出错: {e}")
        return False


def test_sina_finance():
    """测试新浪财经是否可访问"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        url = 'https://finance.sina.com.cn/roll/'
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ 新浪财经可访问")
            return True
        else:
            print(f"❌ 新浪财经访问失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 新浪财经访问出错: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("测试新闻数据源")
    print("=" * 60)
    
    test_akshare()
    test_jin10()
    test_sina_finance()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
