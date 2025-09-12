#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件到日历发布历史处理器
专门处理 publish_excel/ 目录下的Excel文件，写入到 publish_history_for_calendar.csv
支持去重和增量更新
"""

import os
import sys
import pandas as pd
from datetime import datetime
import re
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def clean_dataframe(df):
    """清理DataFrame数据"""
    if df.empty:
        return df
    
    # 移除完全空白的行
    df = df.dropna(how='all')
    
    # 清理列名
    df.columns = df.columns.str.strip()
    
    return df

def standardize_columns(df, platform):
    """标准化列名和数据结构"""
    if df.empty:
        return df
    
    # 根据平台确定账号名称前缀
    if "头条" in platform:
        account_prefix = "头条号-"
    elif "百家号" in platform:
        account_prefix = "百家号-"
    else:
        account_prefix = ""
    
    # 提取账号名称（从文件名中提取）
    account_name = platform.replace("头条-", "").replace("百家号-", "")
    full_account_name = account_prefix + account_name
    
    # 创建标准化的DataFrame
    standardized_df = pd.DataFrame()
    
    # 根据不同的列名模式进行映射
    column_mapping = {
        # 标题相关
        '标题': ['标题', 'title', 'Title', '文章标题', '文章名'],
        '发布时间': ['发布时间', 'publish_time', 'PublishTime', '发布时间', '日期', 'Date'],
        '阅读量': ['阅读量', 'read_count', 'ReadCount', '阅读数', '阅读', 'views'],
        '点赞量': ['点赞量', 'like_count', 'LikeCount', '点赞数', '点赞', 'likes'],
        '评论量': ['评论量', 'comment_count', 'CommentCount', '评论数', '评论', 'comments'],
        '链接': ['链接', 'link', 'Link', 'URL', 'url', '文章链接']
    }
    
    # 尝试映射列
    for target_col, possible_cols in column_mapping.items():
        found_col = None
        for col in possible_cols:
            if col in df.columns:
                found_col = col
                break
        
        if found_col:
            standardized_df[target_col] = df[found_col]
        else:
            # 如果找不到对应列，创建空列
            standardized_df[target_col] = ""
    
    # 添加账号名称列
    standardized_df['账号名称'] = full_account_name
    
    # 确保所有必需的列都存在
    required_columns = ['标题', '账号名称', '发布时间', '阅读量', '点赞量', '评论量', '链接']
    for col in required_columns:
        if col not in standardized_df.columns:
            standardized_df[col] = ""
    
    # 只保留需要的列，确保顺序
    standardized_df = standardized_df[required_columns]
    
    return standardized_df

def clean_title(title):
    """清理标题"""
    if pd.isna(title) or title == "":
        return ""
    
    title = str(title).strip()
    # 移除多余的引号
    title = title.strip('"').strip("'")
    # 限制长度
    if len(title) > 100:
        title = title[:100] + "..."
    
    return title

def clean_publish_time(time_str):
    """清理和标准化发布时间"""
    if pd.isna(time_str) or time_str == "":
        return ""
    
    time_str = str(time_str).strip()
    
    # 尝试解析不同的时间格式
    time_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y',
        '%d/%m/%Y %H:%M:%S',
        '%d/%m/%Y'
    ]
    
    for fmt in time_formats:
        try:
            dt = datetime.strptime(time_str, fmt)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
    
    # 如果所有格式都失败，返回原字符串
    return time_str

def clean_numeric_value(value):
    """清理数值字段"""
    if pd.isna(value) or value == "":
        return 0
    
    # 转换为字符串并清理
    value_str = str(value).strip()
    
    # 移除非数字字符（保留负号和小数点）
    value_str = re.sub(r'[^\d.-]', '', value_str)
    
    try:
        return int(float(value_str))
    except (ValueError, TypeError):
        return 0

def process_excel_file(file_path):
    """处理单个Excel文件"""
    try:
        print(f"📖 正在处理文件: {file_path}")
        
        # 读取Excel文件，处理可能的格式问题
        df = None
        error_messages = []
        
        # 方法1: 使用openpyxl引擎
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            print(f"✅ 使用openpyxl成功读取文件")
        except Exception as e1:
            error_messages.append(f"openpyxl: {str(e1)}")
        
        # 方法2: 使用xlrd引擎
        if df is None:
            try:
                df = pd.read_excel(file_path, engine='xlrd')
                print(f"✅ 使用xlrd成功读取文件")
            except Exception as e2:
                error_messages.append(f"xlrd: {str(e2)}")
        
        # 方法3: 尝试读取为CSV（如果是Excel格式的CSV）
        if df is None:
            try:
                # 先尝试读取第一个工作表
                import openpyxl
                wb = openpyxl.load_workbook(file_path, data_only=True)
                ws = wb.active
                
                # 将数据转换为DataFrame
                data = []
                for row in ws.iter_rows(values_only=True):
                    if any(cell is not None for cell in row):  # 跳过完全空白的行
                        data.append(row)
                
                if data:
                    df = pd.DataFrame(data[1:], columns=data[0])  # 第一行作为列名
                    print(f"✅ 使用openpyxl data_only模式成功读取文件")
            except Exception as e3:
                error_messages.append(f"openpyxl data_only: {str(e3)}")
        
        # 方法4: 尝试使用pandas的默认引擎
        if df is None:
            try:
                df = pd.read_excel(file_path)
                print(f"✅ 使用pandas默认引擎成功读取文件")
            except Exception as e4:
                error_messages.append(f"pandas默认: {str(e4)}")
        
        # 如果所有方法都失败
        if df is None:
            print(f"❌ 无法读取文件 {file_path}")
            print(f"   尝试的方法: {', '.join(error_messages)}")
            return pd.DataFrame()
        
        if df.empty:
            print(f"⚠️ 文件 {file_path} 为空，跳过")
            return pd.DataFrame()
        
        print(f"📊 原始数据: {len(df)} 行")
        
        # 清理数据
        df = clean_dataframe(df)
        
        # 从文件名提取平台信息
        filename = os.path.basename(file_path)
        platform = os.path.splitext(filename)[0]
        
        # 标准化列
        df = standardize_columns(df, platform)
        
        if df.empty:
            print(f"⚠️ 标准化后数据为空，跳过")
            return pd.DataFrame()
        
        # 清理各个字段
        df['标题'] = df['标题'].apply(clean_title)
        df['发布时间'] = df['发布时间'].apply(clean_publish_time)
        df['阅读量'] = df['阅读量'].apply(clean_numeric_value)
        df['点赞量'] = df['点赞量'].apply(clean_numeric_value)
        df['评论量'] = df['评论量'].apply(clean_numeric_value)
        df['链接'] = df['链接'].fillna("").astype(str).str.strip()
        
        # 移除标题为空的记录
        df = df[df['标题'] != ""]
        
        print(f"✅ 处理后数据: {len(df)} 行")
        
        return df
        
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {str(e)}")
        return pd.DataFrame()

def remove_duplicate_records(df):
    """移除重复记录"""
    if df.empty:
        return df
        
    # 创建唯一标识符
    df['unique_key'] = df['标题'] + '|' + df['发布时间'] + '|' + df['账号名称'] + '|' + df['链接']
    
    # 移除重复记录，保留最新的数据
    df = df.drop_duplicates(subset=['unique_key'], keep='last')
    
    # 移除临时列
    df = df.drop('unique_key', axis=1)
    
    return df

def create_unique_id(df):
    """创建统一的唯一标识符"""
    if df.empty:
        return df
    df['unique_id'] = df['标题'] + '|' + df['发布时间'] + '|' + df['账号名称']
    return df

def update_calendar_csv(excel_data):
    """更新日历发布历史CSV文件"""
    csv_path = project_root / "workspace" / "data" / "publish_history_for_calendar.csv"
    
    # 确保目录存在
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果文件不存在或为空，则初始化
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        columns = ["标题", "账号名称", "发布时间", "阅读量", "点赞量", "评论量", "链接"]
        empty_df = pd.DataFrame(columns=columns)
        empty_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print("📝 创建新的CSV文件")
    
    # 读取现有数据
    try:
        existing_df = pd.read_csv(csv_path, encoding="utf-8-sig")
        if existing_df.empty:
            print("📝 现有数据为空，直接保存新数据")
            combined_df = excel_data
        else:
            print(f"📚 现有数据: {len(existing_df)} 条")
            
            # 为两个数据集创建统一的唯一标识符
            existing_df = create_unique_id(existing_df)
            excel_data = create_unique_id(excel_data)
            
            # 找出需要新增的记录
            new_records = excel_data[~excel_data['unique_id'].isin(existing_df['unique_id'])]
            print(f"➕ 发现 {len(new_records)} 条新记录")
            
            # 找出需要更新的记录
            existing_records = excel_data[excel_data['unique_id'].isin(existing_df['unique_id'])]
            print(f"🔄 发现 {len(existing_records)} 条需要更新的记录")
            
            if not existing_records.empty:
                # 更新已存在的记录
                for _, new_row in existing_records.iterrows():
                    mask = existing_df['unique_id'] == new_row['unique_id']
                    existing_df.loc[mask, ['阅读量', '点赞量', '评论量']] = [
                        new_row['阅读量'], 
                        new_row['点赞量'], 
                        new_row['评论量']
                    ]
                print("✅ 已更新现有记录的数据")
            
            # 合并新记录和更新后的旧记录
            if not new_records.empty:
                # 移除unique_id列
                new_records = new_records.drop('unique_id', axis=1)
                existing_df = existing_df.drop('unique_id', axis=1)
                combined_df = pd.concat([existing_df, new_records], ignore_index=True)
                print(f"🔗 合并后共 {len(combined_df)} 条记录")
            else:
                combined_df = existing_df.drop('unique_id', axis=1)
                print("ℹ️ 没有新记录需要添加")
                
    except pd.errors.EmptyDataError:
        print("📝 现有数据为空，直接保存新数据")
        combined_df = excel_data
    
    # 最终去重
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['标题', '发布时间', '账号名称'], keep='last')
    after_dedup = len(combined_df)
    
    if before_dedup != after_dedup:
        print(f"🧹 最终去重：移除 {before_dedup - after_dedup} 条重复记录")
    
    # 使用自定义去重函数进行最终清理
    before_final_dedup = len(combined_df)
    combined_df = remove_duplicate_records(combined_df)
    after_final_dedup = len(combined_df)
    
    if before_final_dedup != after_final_dedup:
        print(f"🧽 最终清理：移除 {before_final_dedup - after_final_dedup} 条重复记录")
    
    # 按发布时间排序
    if not combined_df.empty:
        combined_df['发布时间'] = pd.to_datetime(combined_df['发布时间'], errors='coerce')
        combined_df = combined_df.sort_values('发布时间', ascending=False)
        combined_df['发布时间'] = combined_df['发布时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # 保存数据
    combined_df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"💾 数据已保存到 {csv_path}，共 {len(combined_df)} 条记录")
    
    return True

def process_all_excel_files():
    """处理所有Excel文件"""
    excel_dir = project_root / "scripts" / "publish_excel"
    
    if not excel_dir.exists():
        print(f"❌ Excel目录不存在: {excel_dir}")
        return False
    
    # 获取所有Excel文件
    excel_files = list(excel_dir.glob("*.xlsx")) + list(excel_dir.glob("*.xls"))
    
    if not excel_files:
        print("⚠️ 未找到Excel文件")
        return False
    
    print(f"📁 找到 {len(excel_files)} 个Excel文件")
    
    all_data = []
    
    for excel_file in excel_files:
        df = process_excel_file(excel_file)
        if not df.empty:
            all_data.append(df)
    
    if not all_data:
        print("⚠️ 没有有效的数据")
        return False
    
    # 合并所有数据
    combined_data = pd.concat(all_data, ignore_index=True)
    print(f"📊 合并后总数据: {len(combined_data)} 条")
    
    # 去重
    combined_data = remove_duplicate_records(combined_data)
    print(f"🔍 去重后数据: {len(combined_data)} 条")
    
    # 更新CSV文件
    success = update_calendar_csv(combined_data)
    
    if success:
        print("🎉 所有Excel文件处理完成！")
    else:
        print("❌ 处理过程中出现错误")
    
    return success

def main():
    """主函数"""
    print("🚀 开始处理Excel文件...")
    print("=" * 50)
    
    success = process_all_excel_files()
    
    print("=" * 50)
    if success:
        print("✅ 处理完成！")
    else:
        print("❌ 处理失败！")
    
    return success

if __name__ == "__main__":
    main()
