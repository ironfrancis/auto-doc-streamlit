#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号数据获取示例
展示如何使用update_wechat_data_from_excel函数获取不同公众号的数据
"""

from app.utils.wechat_data_processor import update_wechat_data_from_excel

def get_agi_observation_data():
    """获取AGI观察室的数据"""
    print("=== 获取AGI观察室数据 ===")
    update_wechat_data_from_excel(
        begin_date="20250609", 
        end_date="20250818", 
        token="254511315",  # 需要替换为实际的token
        account_name="AGI观察室"
    )

def get_agi_revelation_data():
    """获取AGI启示录的数据"""
    print("=== 获取AGI启示录数据 ===")
    update_wechat_data_from_excel(
        begin_date="20250609", 
        end_date="20250818", 
        token="254511315",  # 需要替换为实际的token
        account_name="AGI启示录"
    )

def get_ai_world_data():
    """获取AI万象志的数据"""
    print("=== 获取AI万象志数据 ===")
    update_wechat_data_from_excel(
        begin_date="20250609", 
        end_date="20250818", 
        token="254511315",  # 需要替换为实际的token
        account_name="AI万象志"
    )

def get_ai_tour_guide_data():
    """获取人工智能漫游指南的数据"""
    print("=== 获取人工智能漫游指南数据 ===")
    update_wechat_data_from_excel(
        begin_date="20250609", 
        end_date="20250818", 
        token="254511315",  # 需要替换为实际的token
        account_name="人工智能漫游指南"
    )

def get_custom_account_data(begin_date, end_date, token, account_name, cookies=None):
    """获取自定义公众号的数据
    
    Args:
        begin_date (str): 开始日期，格式：YYYYMMDD
        end_date (str): 结束日期，格式：YYYYMMDD
        token (str): 微信公众平台的token
        account_name (str): 公众号名称
        cookies (str): 可选的cookie字符串
    """
    print(f"=== 获取{account_name}数据 ===")
    update_wechat_data_from_excel(
        begin_date=begin_date,
        end_date=end_date,
        token=token,
        cookies=cookies,
        account_name=account_name
    )

if __name__ == "__main__":
    # 示例1：获取AGI观察室数据（使用默认参数）
    print("示例1：获取AGI观察室数据")
    # get_agi_observation_data()
    
    # 示例2：获取AGI启示录数据
    print("\n示例2：获取AGI启示录数据")
    # get_agi_revelation_data()
    
    # 示例3：获取AI万象志数据
    print("\n示例3：获取AI万象志数据")
    # get_ai_world_data()
    
    # 示例4：获取人工智能漫游指南数据
    print("\n示例4：获取人工智能漫游指南数据")
    # get_ai_tour_guide_data()
    
    # 示例5：获取自定义公众号数据
    print("\n示例5：获取自定义公众号数据")
    # get_custom_account_data(
    #     begin_date="20250601",
    #     end_date="20250831",
    #     token="your_token_here",
    #     account_name="你的公众号名称",
    #     cookies="your_cookies_here"
    # )
    
    print("\n注意：")
    print("1. 每个公众号需要不同的token（从微信公众平台获取）")
    print("2. 可能需要不同的cookies（如果登录状态不同）")
    print("3. 可以设置不同的时间范围（根据实际发布情况）")
    print("4. 取消注释相应的函数调用来实际执行")
