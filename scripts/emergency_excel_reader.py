#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急Excel文件读取器
使用最底层的方法读取有问题的Excel文件
"""

import os
import sys
import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path

def read_excel_with_zipfile(file_path):
    """使用zipfile直接读取Excel文件内容"""
    try:
        print(f"🔍 尝试使用zipfile读取: {file_path}")
        
        # Excel文件实际上是一个zip文件
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
                print("⚠️ 无法读取共享字符串表")
            
            # 读取工作表数据
            try:
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
                        # 创建DataFrame
                        df = pd.DataFrame(rows[1:], columns=rows[0])
                        print(f"✅ 成功读取 {len(df)} 行数据")
                        return df
                    else:
                        print("⚠️ 没有找到数据行")
                        return pd.DataFrame()
                        
            except Exception as e:
                print(f"❌ 读取工作表失败: {str(e)}")
                return pd.DataFrame()
                
    except Exception as e:
        print(f"❌ zipfile读取失败: {str(e)}")
        return pd.DataFrame()

def process_problematic_files():
    """处理有问题的Excel文件"""
    excel_dir = Path("scripts/publish_excel")
    output_dir = Path("scripts/publish_excel_recovered")
    output_dir.mkdir(exist_ok=True)
    
    # 有问题的文件列表
    problematic_files = [
        "头条-观察室.xlsx",
        "头条-AGI观察室.xlsx", 
        "头条-看山先生.xlsx",
        "头条-漫游指南.xlsx"
    ]
    
    print("🚀 开始恢复有问题的Excel文件...")
    print("=" * 50)
    
    success_count = 0
    
    for filename in problematic_files:
        file_path = excel_dir / filename
        if file_path.exists():
            print(f"\n📖 处理文件: {filename}")
            
            # 尝试使用zipfile读取
            df = read_excel_with_zipfile(file_path)
            
            if not df.empty:
                # 保存为CSV
                csv_path = output_dir / (filename.replace('.xlsx', '.csv'))
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"✅ 数据已保存到: {csv_path}")
                success_count += 1
            else:
                print(f"❌ 无法恢复文件: {filename}")
    
    print("\n" + "=" * 50)
    print(f"✅ 恢复完成！成功处理 {success_count} 个文件")
    print(f"📁 恢复的数据保存在: {output_dir}")

def main():
    """主函数"""
    process_problematic_files()

if __name__ == "__main__":
    main()
