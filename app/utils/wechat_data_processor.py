#!/usr/bin/env python3
"""
微信公众号数据处理工具
统一处理微信公众号的Excel文件和URL信息获取
"""

import pandas as pd
import os
import sys
import requests
import re
from datetime import datetime
from typing import Dict, List, Optional


def load_csv_path():
    """从CSV文件加载数据"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # 如果__file__不可用，使用当前工作目录
        current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)

    CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(current_dir)),
                            "workspace", "data", "publish_history.csv")
    return CSV_PATH

def append_record_to_csv(df: pd.DataFrame):
    try:
        _old_df = pd.read_csv(load_csv_path())
    except:
        _old_df = pd.DataFrame()

    # 处理日期列，将YYYYMMDD格式转换为YYYY-MM-DD
    if '发表时间' in df.columns:
        df['发表时间'] = pd.to_datetime(df['发表时间'].astype(str), format='%Y%m%d').dt.strftime('%Y-%m-%d')

    # 处理所有数值列，保留3位小数
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = df[col].round(3)

    # 处理公众号名称，从第一个有效的URL获取公众号名称并应用到所有行
    if '内容url' in df.columns:
        first_valid_url = df['内容url'].dropna().iloc[0] if not df['内容url'].dropna().empty else None
        account_name = parser_gzh_url(first_valid_url)['公众号名称'] if first_valid_url else None
        df['账号名称'] = account_name
    # 合并新旧数据并去重
    merged_df = pd.concat([_old_df, df], ignore_index=True)
    merged_df.drop_duplicates(inplace=True)
    merged_df.to_csv(load_csv_path(), index=False)

def parser_gzh_url(url: str) -> Dict[str, str]:
    """解析微信公众号URL并获取文章信息"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 公众号名称
        nickname = re.search(r'var nickname = htmlDecode\("(.*?)"\)', response.text)
        # 发布时间
        create_time = re.search(r"var createTime = '(.*?)'", response.text)
        return {
            '公众号名称': nickname.group(1) if nickname else None,
            '发布时间': create_time.group(1) if create_time else None
        }
    except Exception as e:
        print(f"解析URL失败: {e}")
        return None

# 获取access_token
def get_access_token():
    appid = "wx84124e3eadbed3d4"
    app_secret = "4e760d68a258c2ee5ed3d5177c97c5b0"
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={app_secret}'
    response = requests.get(url)
    data = response.json()
    print(data)
    return data.get('access_token')

# 获取图文统计数据
def get_article_stats(access_token, begin_date, end_date):
    url = f'https://api.weixin.qq.com/datacube/getarticletotal?access_token={access_token}'
    data = {
        "begin_date": begin_date,
        "end_date": end_date
    }
    response = requests.post(url, json=data)
    return response.json()

if __name__ == '__main__':
    # test_df = pd.read_excel("agi启示录7.xls")
    # print(test_df)
    # append_record_to_csv(test_df)

    # path = "/Users/xuchao/Downloads/公众号发布记录截止7月/"
    # for file in os.listdir(path):
    #     if file.endswith(".xls") or file.endswith(".xlsx"):
    #         print(file)
    #         df = pd.read_excel(os.path.join(path, file))
    #         print(df)
    #         append_record_to_csv(df)
    # # dict = parser_gzh_url(url="http://mp.weixin.qq.com/s?__biz=Mzk5MDY3NjYxMA==&mid=2247483701&idx=1&sn=1a1fe31523fcc5d31aee5a565cfb1080&chksm=c5e252d8f295dbce81f3b33ffc758ff73b9a67a329d9038b1d234b86e3129d3a0d5a49e66a92#rd")
    # # print(dict)

    # print(get_article_stats())
    appid = "wx84124e3eadbed3d4"
    app_secret = "4e760d68a258c2ee5ed3d5177c97c5b0"
    ai_wanxiang_token = "94_2TycVLSNiTxY-zoGP-_6NVansjAP11ZUFSf9XjhbX3QKMESQHXx1LT8Qy6V6t0JZ2C7qz2G5g7qcISoAFcdZgPj1su7-Pbarsp8drOBEt8E_qfNvft48x1bXMQUEEVcADAXXO"
    # print(get_access_token())
    print(get_article_stats(access_token=ai_wanxiang_token, begin_date="2025-07-01", end_date="2025-08-01"))