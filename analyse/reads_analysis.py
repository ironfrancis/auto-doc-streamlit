#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章发布历史数据分析脚本

这个脚本用于分析文章发布历史数据，包括阅读量、点赞量等指标的分析。
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

print("✅ 导入库完成")

def load_publish_history():
    """尝试从多个可能的路径加载文章发布历史数据"""
    
    # 可能的文件路径列表
    possible_paths = [
        # 从当前脚本目录的相对路径
        '../workspace/data/publish_history_for_calendar.csv',
        '../workspace/publish_history_for_calendar.csv',
        
        # 从项目根目录的路径
        '../../workspace/data/publish_history_for_calendar.csv',
        '../../workspace/publish_history_for_calendar.csv',
        
        # 从当前工作目录的路径
        'workspace/data/publish_history_for_calendar.csv',
        'workspace/publish_history_for_calendar.csv',
        
        # 绝对路径（基于项目根目录）
        '/Users/xuchao/Projects/Auto-doc-streamlit/workspace/data/publish_history_for_calendar.csv',
        '/Users/xuchao/Projects/Auto-doc-streamlit/workspace/publish_history_for_calendar.csv'
    ]
    
    # 尝试读取文件
    for path in possible_paths:
        if os.path.exists(path):
            try:
                print(f"✅ 成功找到文件: {path}")
                df = pd.read_csv(path, encoding='utf-8-sig')
                print(f"📊 成功加载数据，共 {len(df)} 条记录")
                print(f"📋 数据列名: {list(df.columns)}")
                return df, path
            except Exception as e:
                print(f"❌ 读取文件失败 {path}: {str(e)}")
                continue
    
    # 如果所有路径都失败，显示当前目录信息
    print("❌ 无法找到 publish_history_for_calendar.csv 文件")
    print(f"📍 当前工作目录: {os.getcwd()}")
    print(f"📁 当前脚本目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 列出当前目录内容
    print("\n📂 当前目录内容:")
    try:
        for item in os.listdir('.'):
            if os.path.isdir(item):
                print(f"📁 {item}/")
            else:
                print(f"📄 {item}")
    except Exception as e:
        print(f"无法列出目录内容: {e}")
    
    # 尝试列出上级目录内容
    try:
        parent_dir = os.path.dirname(os.path.abspath('.'))
        print(f"\n📂 上级目录 ({parent_dir}) 内容:")
        for item in os.listdir(parent_dir):
            if os.path.isdir(item):
                print(f"📁 {item}/")
            else:
                print(f"📄 {item}")
    except Exception as e:
        print(f"无法列出上级目录内容: {e}")
    
    return None, None

def analyze_data(df):
    """分析数据的基本信息"""
    if df is None:
        print("❌ 没有数据可供分析")
        return
    
    print("\n📊 数据基本信息:")
    print(f"数据形状: {df.shape}")
    print(f"数据列名: {list(df.columns)}")
    
    # 检查必要的列是否存在
    required_columns = ['标题', '发布时间', '阅读量', '点赞量', '评论量', '账号名称']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"⚠️ 缺少必要的列: {missing_columns}")
    else:
        print("✅ 所有必要的列都存在")
    
    # 数据预览
    print("\n📋 数据前5行:")
    print(df.head())
    
    # 数值列统计
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        print("\n🔍 数值列统计摘要:")
        print(df[numeric_columns].describe())
    
    # 账号分布
    if '账号名称' in df.columns:
        print("\n📈 账号分布:")
        account_counts = df['账号名称'].value_counts()
        print(account_counts)
    
    # 时间处理
    if '发布时间' in df.columns:
        df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
        df['发布日期'] = df['发布时间'].dt.date
        print(f"\n📅 数据时间范围: {df['发布时间'].min()} 到 {df['发布时间'].max()}")

def check_data_quality(df):
    """检查数据质量"""
    if df is None:
        return
    
    print("\n🔍 数据质量检查:")
    
    # 检查缺失值
    print("\n📊 缺失值统计:")
    missing_data = df.isnull().sum()
    missing_percentage = (missing_data / len(df)) * 100
    missing_df = pd.DataFrame({
        '缺失数量': missing_data,
        '缺失百分比': missing_percentage
    })
    missing_rows = missing_df[missing_df['缺失数量'] > 0]
    if len(missing_rows) > 0:
        print(missing_rows)
    else:
        print("✅ 没有缺失值")
    
    # 检查重复数据
    print(f"\n🔄 重复行数量: {df.duplicated().sum()}")
    
    # 检查数据范围
    if '阅读量' in df.columns:
        print(f"\n📖 阅读量范围: {df['阅读量'].min()} - {df['阅读量'].max()}")
        print(f"📖 阅读量中位数: {df['阅读量'].median()}")
        
    if '点赞量' in df.columns:
        print(f"👍 点赞量范围: {df['点赞量'].min()} - {df['点赞量'].max()}")
        print(f"👍 点赞量中位数: {df['点赞量'].median()}")
        
    if '评论量' in df.columns:
        print(f"💬 评论量范围: {df['评论量'].min()} - {df['评论量'].max()}")
        print(f"💬 评论量中位数: {df['评论量'].median()}")

def analyze_account_performance(df):
    """分析账号表现"""
    if df is None or '账号名称' not in df.columns:
        print("❌ 无法分析账号表现，缺少必要数据")
        return
    
    print("\n📊 账号表现分析:")
    
    # 按账号分组计算统计信息
    account_stats = df.groupby('账号名称').agg({
        '标题': 'count',  # 文章数量
        '阅读量': ['mean', 'sum', 'median'],  # 阅读量统计
        '点赞量': ['mean', 'sum', 'median'],  # 点赞量统计
        '评论量': ['mean', 'sum', 'median']   # 评论量统计
    }).round(2)
    
    # 重命名列名
    account_stats.columns = [
        '文章数量', '平均阅读量', '总阅读量', '阅读量中位数',
        '平均点赞量', '总点赞量', '点赞量中位数',
        '平均评论量', '总评论量', '评论量中位数'
    ]
    
    print("\n📈 账号综合表现:")
    print(account_stats)
    
    # 按总阅读量排序
    print("\n🏆 按总阅读量排序的账号:")
    top_reads = account_stats.sort_values('总阅读量', ascending=False)
    print(top_reads)
    
    # 按平均阅读量排序
    print("\n📊 按平均阅读量排序的账号:")
    top_avg_reads = account_stats.sort_values('平均阅读量', ascending=False)
    print(top_avg_reads)

def analyze_time_trends(df):
    """分析时间趋势"""
    if df is None or '发布时间' not in df.columns:
        print("❌ 无法分析时间趋势，缺少必要数据")
        return
    
    print("\n📅 时间趋势分析:")
    
    # 按日期分组计算统计信息
    daily_stats = df.groupby('发布日期').agg({
        '标题': 'count',  # 文章数量
        '阅读量': 'sum',  # 总阅读量
        '点赞量': 'sum',  # 总点赞量
        '评论量': 'sum'   # 总评论量
    }).reset_index()
    
    daily_stats.columns = ['日期', '文章数量', '总阅读量', '总点赞量', '总评论量']
    
    print("\n📊 每日发布统计:")
    print(daily_stats.head(10))
    
    # 绘制时间趋势图
    plt.figure(figsize=(15, 10))
    
    # 子图1：文章数量趋势
    plt.subplot(2, 2, 1)
    plt.plot(daily_stats['日期'], daily_stats['文章数量'], marker='o', linewidth=2, markersize=4)
    plt.title('每日文章发布数量趋势')
    plt.xlabel('日期')
    plt.ylabel('文章数量')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 子图2：阅读量趋势
    plt.subplot(2, 2, 2)
    plt.plot(daily_stats['日期'], daily_stats['总阅读量'], marker='s', linewidth=2, markersize=4, color='orange')
    plt.title('每日总阅读量趋势')
    plt.xlabel('日期')
    plt.ylabel('总阅读量')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 子图3：点赞量趋势
    plt.subplot(2, 2, 3)
    plt.plot(daily_stats['日期'], daily_stats['总点赞量'], marker='^', linewidth=2, markersize=4, color='green')
    plt.title('每日总点赞量趋势')
    plt.xlabel('日期')
    plt.ylabel('总点赞量')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # 子图4：评论量趋势
    plt.subplot(2, 2, 4)
    plt.plot(daily_stats['日期'], daily_stats['总评论量'], marker='d', linewidth=2, markersize=4, color='red')
    plt.title('每日总评论量趋势')
    plt.xlabel('日期')
    plt.ylabel('总评论量')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def load_from_manual_path(file_path):
    """从手动指定的路径加载数据"""
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"✅ 成功从手动路径加载数据: {file_path}")
            print(f"📊 数据形状: {df.shape}")
            return df
        else:
            print(f"❌ 文件不存在: {file_path}")
            return None
    except Exception as e:
        print(f"❌ 读取文件失败: {str(e)}")
        return None

def main():
    """主函数"""
    print("🚀 开始分析文章发布历史数据...")
    
    # 加载数据
    df, file_path = load_publish_history()
    
    if df is not None:
        print(f"\n🎉 数据加载成功！文件路径: {file_path}")
        
        # 分析数据
        analyze_data(df)
        check_data_quality(df)
        analyze_account_performance(df)
        analyze_time_trends(df)
        
    else:
        print("\n💡 请检查文件路径或手动指定正确的文件路径")
        print("\n📁 常见的文件路径:")
        print("1. 相对路径: '../workspace/data/publish_history_for_calendar.csv'")
        print("2. 绝对路径: '/Users/xuchao/Projects/Auto-doc-streamlit/workspace/data/publish_history_for_calendar.csv'")
        print("3. 当前目录: './workspace/data/publish_history_for_calendar.csv'")
        
        print("\n💡 如果需要手动指定路径，请使用:")
        print("manual_df = load_from_manual_path('/path/to/your/publish_history_for_calendar.csv')")

if __name__ == "__main__":
    main()
