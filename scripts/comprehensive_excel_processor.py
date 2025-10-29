#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合Excel处理器
处理所有类型的文件：正常Excel、修复Excel、恢复CSV
"""

import os
import sys
import pandas as pd
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def read_excel_with_zipfile(file_path):
    """使用zipfile直接读取Excel文件内容"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            # 读取共享字符串表
            shared_strings = []
            try:
                with zip_file.open('xl/sharedStrings.xml') as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    for si in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                        text_elements = si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                        if text_elements:
                            text = ''.join([elem.text or '' for elem in text_elements])
                            shared_strings.append(text)
                        else:
                            shared_strings.append('')
            except:
                pass
            
            # 读取工作表数据
            with zip_file.open('xl/worksheets/sheet1.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # 解析行数据
                rows = []
                for row in root.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                    row_data = []
                    for cell in row.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        cell_type = cell.get('t', '')
                        value_elem = cell.find('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        
                        if value_elem is not None:
                            value = value_elem.text
                            if cell_type == 's' and value:  # 共享字符串
                                try:
                                    idx = int(value)
                                    if idx < len(shared_strings):
                                        row_data.append(shared_strings[idx])
                                    else:
                                        row_data.append('')
                                except:
                                    row_data.append(value)
                            else:
                                row_data.append(value)
                        else:
                            row_data.append('')
                    
                    if any(cell for cell in row_data):  # 只添加非空行
                        rows.append(row_data)
                
                if rows:
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                    return df
                else:
                    return pd.DataFrame()
                    
    except Exception as e:
        print(f"❌ zipfile读取失败: {str(e)}")
        return pd.DataFrame()

def process_file(file_path):
    """处理单个文件"""
    try:
        print(f"📖 正在处理文件: {file_path}")
        
        df = None
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.csv':
            # 直接读取CSV文件
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                print(f"✅ 使用pandas成功读取CSV文件")
            except:
                try:
                    df = pd.read_csv(file_path, encoding='gbk')
                    print(f"✅ 使用GBK编码成功读取CSV文件")
                except Exception as e:
                    print(f"❌ 无法读取CSV文件: {str(e)}")
                    return pd.DataFrame()
        
        elif file_ext in ['.xlsx', '.xls']:
            # 尝试多种方法读取Excel文件
            error_messages = []
            
            # 方法1: 使用openpyxl引擎
            if df is None:
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
            
            # 方法3: 使用zipfile直接读取
            if df is None:
                try:
                    df = read_excel_with_zipfile(file_path)
                    if not df.empty:
                        print(f"✅ 使用zipfile成功读取文件")
                except Exception as e3:
                    error_messages.append(f"zipfile: {str(e3)}")
            
            # 方法4: 使用pandas默认引擎
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
        return df
        
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {str(e)}")
        return pd.DataFrame()

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
    if "头条号" in platform:
        account_prefix = "头条号-"
    elif "百家号" in platform:
        account_prefix = "百家号-"
    else:
        account_prefix = ""
    
    # 提取账号名称（从文件名中提取）
    account_name = platform.replace("头条号-", "").replace("百家号-", "")
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
            from datetime import datetime
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
    import re
    value_str = re.sub(r'[^\d.-]', '', value_str)
    
    try:
        return int(float(value_str))
    except (ValueError, TypeError):
        return 0

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

def process_all_files():
    """处理所有文件"""
    # 定义要处理的目录
    directories = [
        "scripts/publish_excel",           # 原始Excel文件
        "scripts/publish_excel_fixed",     # 修复的Excel文件
        "scripts/publish_excel_recovered", # 恢复的CSV文件
        "scripts/publish_excel_csv"        # 转换的CSV文件
    ]
    
    all_files = []
    
    # 收集所有文件
    for dir_path in directories:
        dir_obj = Path(dir_path)
        if dir_obj.exists():
            files = list(dir_obj.glob("*.xlsx")) + list(dir_obj.glob("*.xls")) + list(dir_obj.glob("*.csv"))
            all_files.extend(files)
    
    if not all_files:
        print("⚠️ 未找到任何文件")
        return False
    
    print(f"📁 找到 {len(all_files)} 个文件")
    
    all_data = []
    
    for file_path in all_files:
        # 处理文件
        df = process_file(file_path)
        
        if df.empty:
            continue
        
        # 清理数据
        df = clean_dataframe(df)
        
        # 从文件名提取平台信息
        filename = file_path.name
        platform = file_path.stem
        
        # 标准化列
        df = standardize_columns(df, platform)
        
        if df.empty:
            continue
        
        # 清理各个字段
        df['标题'] = df['标题'].apply(clean_title)
        df['发布时间'] = df['发布时间'].apply(clean_publish_time)
        df['阅读量'] = df['阅读量'].apply(clean_numeric_value)
        df['点赞量'] = df['点赞量'].apply(clean_numeric_value)
        df['评论量'] = df['评论量'].apply(clean_numeric_value)
        df['链接'] = df['链接'].fillna("").astype(str).str.strip()
        
        # 移除标题为空的记录
        df = df[df['标题'] != ""]
        
        if not df.empty:
            print(f"✅ 处理后数据: {len(df)} 行")
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
        print("🎉 所有文件处理完成！")
    else:
        print("❌ 处理过程中出现错误")
    
    return success

def main():
    """主函数"""
    print("🚀 综合Excel数据处理工具")
    print("=" * 50)
    print("📁 处理目录:")
    print("  - scripts/publish_excel/ (原始Excel文件)")
    print("  - scripts/publish_excel_fixed/ (修复的Excel文件)")
    print("  - scripts/publish_excel_recovered/ (恢复的CSV文件)")
    print("  - scripts/publish_excel_csv/ (转换的CSV文件)")
    print("📄 输出文件: workspace/data/publish_history_for_calendar.csv")
    print("=" * 50)
    
    try:
        success = process_all_files()
        
        if success:
            print("\n✅ 处理完成！")
            print("📊 数据已更新到 publish_history_for_calendar.csv")
        else:
            print("\n❌ 处理失败！")
            print("请检查错误信息并重试")
            
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        print("请检查文件路径和权限")

if __name__ == "__main__":
    main()
