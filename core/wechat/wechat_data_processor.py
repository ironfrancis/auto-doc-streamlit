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

# ==================== 常量定义 ====================

# 默认Cookie字符串（从配置中获取，避免硬编码）
DEFAULT_COOKIES = ('ua_id=EAtVm2ev26Kq3ThqAAAAAFyRhWwF4BhMScasWLyd-t8=; '
                  'wxuin=50334049658256; mm_lang=zh_CN; pgv_pvid=359119330; '
                  'pac_uid=0_brFmT1T24Tfsj; omgid=0_brFmT1T24Tfsj; '
                  '_qimei_uuid42=197100b3414100bfaa5e8fceb40e86c7be307514e7; '
                  '_qimei_fingerprint=214613bddb67bad1c823a4f2d9092a28; '
                  '_qimei_h38=aa6a924eaa5e8fceb40e86c70300000ae19710; '
                  '_qimei_q36=; _clck=3988754792|1|fyk|0; '
                  'rand_info=CAESINY2emaJHl+WaxqcPCHRDCVpI5XSPRzVSxmgACB53XqD; '
                  'slave_bizuin=3567454006; data_bizuin=3567454006; '
                  'bizuin=3567454006; '
                  'data_ticket=a2ut46/7AVTah/CdRezkqOLR9oXX+7COezyAVCznUIMKlK4hpJLeuFjQ/dAqe; '
                  'slave_sid=cTNWSGhWTjc2VURWQkJEMHZJYmR5R2UzeVZYdFZEYkY5RXNGNVg2NEtHWmx0RHlNWF9NelAxYUl3Q1NjSzlueWF0ckN5Y0xxNjV3b0ZSYnJMQ19peU5ibEZCaXY5YWt2b24xWUtzeVFjbVcwNUhxTk1INzAwTXZzYTM2V1dMSXN6N09sNVR0Q2puM3dkU3Vy; '
                  'slave_user=gh_6c0ac84a33d4; '
                  'xid=e29ebedeab47344bd0219f27104961cf; '
                  '_clsk=1c6ac7o|1755552972677|6|1|mp.weixin.qq.com/weheat-agent/payload/record')

# 微信公众号账号列表
WECHAT_ACCOUNTS = ['AGI观察室', 'AGI启示录', 'AI 万象志', '人工智能漫游指南']

# 列名映射配置
COLUMN_MAPPING = {
    '内容标题': '标题',
    '发表时间': '发布时间',
    '总阅读人数': '阅读量',
    '总分享人数': '分享量',
    '内容url': '链接'
}

# ==================== 公共工具函数 ====================

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

def get_calendar_csv_path():
    """获取日历CSV文件路径"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    return os.path.join(
        os.path.dirname(parent_dir),
        "workspace", "data", "publish_history_for_calendar.csv"
    )

def convert_excel_date(date_val):
    """转换Excel中的日期格式（如20250815）为标准日期格式"""
    if pd.isna(date_val):
        return pd.NaT
    # 如果是整数格式（如20250815），转换为日期
    if isinstance(date_val, (int, float, pd.Int64Dtype)) and date_val > 100000000:
        date_str = str(int(date_val))
        if len(date_str) == 8:  # YYYYMMDD格式
            try:
                return pd.to_datetime(date_str, format='%Y%m%d')
            except:
                pass
    # 尝试常规的日期解析
    return pd.to_datetime(date_val, errors='coerce')

def map_wechat_columns(df: pd.DataFrame) -> pd.DataFrame:
    """映射微信公众号列名"""
    if '内容标题' not in df.columns:
        return df
    
    # 重命名列
    df_mapped = df.rename(columns=COLUMN_MAPPING)
    
    # 添加缺失的列
    if '点赞量' not in df_mapped.columns:
        df_mapped['点赞量'] = 0.0
    if '评论量' not in df_mapped.columns:
        df_mapped['评论量'] = 0.0
    
    return df_mapped

def determine_account_name(row, default_account='AGI观察室'):
    """根据链接判断账号名称"""
    link = str(row.get('链接', ''))
    if 'mp.weixin.qq.com' in link:
        return default_account
    else:
        return '头条号-看山先生_AI信息差'

def merge_csv_data(new_df: pd.DataFrame, csv_path: str, subset_cols: List[str] = None) -> pd.DataFrame:
    """合并CSV数据的通用函数"""
    try:
        # 读取现有数据
        existing_df = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"现有CSV文件包含 {len(existing_df)} 行数据")
        
        # 检查是否有重复的列名
        if len(existing_df.columns) != len(set(existing_df.columns)):
            print("检测到重复列名，清理数据...")
            existing_df = existing_df.loc[:, ~existing_df.columns.duplicated()]
            
    except (FileNotFoundError, pd.errors.EmptyDataError):
        existing_df = pd.DataFrame()
        print("创建新的CSV文件")
    
    # 合并数据
    merged_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # 去重
    if subset_cols:
        merged_df = merged_df.drop_duplicates(subset=subset_cols, keep='first')
    else:
        merged_df = merged_df.drop_duplicates()
    
    return merged_df

# ==================== 数据获取函数 ====================

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

def get_wechat_data_cube(begin_date: str, end_date: str, token: str, cookies: str = None) -> Dict:
    """
    获取微信公众号数据统计信息
    
    Args:
        begin_date (str): 开始日期，格式：YYYYMMDD，如：20250719
        end_date (str): 结束日期，格式：YYYYMMDD，如：20250818
        token (str): 微信公众平台的token
        cookies (str): 可选的cookie字符串，如果不提供则使用默认headers
    
    Returns:
        Dict: 包含响应数据的字典
    """
    url = 'https://mp.weixin.qq.com/misc/datacubequery'
    
    # 构建查询参数
    params = {
        'action': 'query_download',
        'busi': '3',
        'tmpl': '19',
        'args': f'{{"begin_date":{begin_date},"end_date":{end_date}}}',
        'token': token,
        'lang': 'zh_CN'
    }
    
    # 默认headers
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'priority': 'u=0, i',
        'referer': f'https://mp.weixin.qq.com/misc/appmsganalysis?action=all&token={token}&lang=zh_CN',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
    }
    
    # 如果提供了cookies，则添加到headers中
    if cookies:
        headers['Cookie'] = cookies
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 检查响应内容类型
        content_type = response.headers.get('content-type', '')
        
        # 尝试检测编码
        if response.encoding == 'ISO-8859-1':
            try:
                response.encoding = 'utf-8'
            except:
                pass
        
        # 优先检查是否是Excel文件（二进制数据）
        if (not content_type or content_type == 'bytes' or 
            'excel' in content_type.lower() or 'xls' in content_type.lower() or 'xlsx' in content_type.lower()):
            
            # 检查响应内容是否是二进制数据
            if isinstance(response.content, bytes) and len(response.content) > 100:
                try:
                    content_str = response.content.decode('latin1', errors='ignore')
                    # 检查Excel文件特征
                    if ('Root Entry' in content_str or 'Workbook' in content_str or 'xl/' in content_str or 
                        'ÐÏà¡±á' in content_str or 'þÿ' in content_str):
                        return {
                            'success': True,
                            'data': response.content,
                            'status_code': response.status_code,
                            'content_type': 'application/vnd.ms-excel',
                            'is_excel': True,
                            'encoding': 'binary'
                        }
                except:
                    pass
        
        if 'application/json' in content_type:
            try:
                json_data = response.json()
                return {
                    'success': True,
                    'data': json_data,
                    'status_code': response.status_code,
                    'content_type': content_type
                }
            except Exception as e:
                return {
                    'success': True,
                    'data': response.text,
                    'status_code': response.status_code,
                    'content_type': content_type,
                    'json_parse_error': str(e)
                }
        elif 'text/html' in content_type:
            return {
                'success': True,
                'data': response.text,
                'status_code': response.status_code,
                'content_type': content_type,
                'is_html': True,
                'encoding': response.encoding
            }
        elif 'text/csv' in content_type or 'csv' in content_type:
            return {
                'success': True,
                'data': response.text,
                'status_code': response.status_code,
                'content_type': content_type,
                'is_csv': True,
                'encoding': response.encoding
            }
        else:
            # 其他类型的响应
            if isinstance(response.content, bytes) and len(response.content) > 100:
                try:
                    content_str = response.content.decode('latin1', errors='ignore')
                    if 'Root Entry' in content_str or 'Workbook' in content_str or 'xl/' in content_str:
                        return {
                            'success': True,
                            'data': response.content,
                            'status_code': response.status_code,
                            'content_type': 'application/vnd.ms-excel',
                            'is_excel': True,
                            'encoding': 'binary'
                        }
                except:
                    pass
            
            return {
                'success': True,
                'data': response.text,
                'status_code': response.status_code,
                'content_type': content_type,
                'encoding': response.encoding
            }
            
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'请求失败: {str(e)}',
            'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'未知错误: {str(e)}'
        }

def get_wechat_data_cube_with_default_cookies(begin_date: str, end_date: str, token: str) -> Dict:
    """使用默认cookies获取微信公众号数据统计信息"""
    return get_wechat_data_cube(begin_date, end_date, token, DEFAULT_COOKIES)

# ==================== 数据更新函数 ====================

def append_record_to_csv(df: pd.DataFrame):
    """追加记录到CSV文件"""
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

def update_publish_history_csv(df: pd.DataFrame):
    """更新publish_history.csv文件"""
    try:
        if '内容标题' not in df.columns:
            print("Excel文件列名不匹配，无法更新publish_history.csv")
            return
        
        # 映射列名
        df_mapped = map_wechat_columns(df)
        
        # 添加账号名称列
        csv_path = load_csv_path()
        try:
            existing_df = pd.read_csv(csv_path, encoding='utf-8-sig')
            if '账号名称' in existing_df.columns:
                first_account = existing_df['账号名称'].dropna().iloc[0] if not existing_df['账号名称'].dropna().empty else 'AGI观察室'
            else:
                first_account = 'AGI观察室'
        except:
            first_account = 'AGI观察室'
        
        df_mapped['账号名称'] = first_account
        
        # 选择需要的列
        required_columns = ['标题', '发布时间', '阅读量', '分享量', '链接', '账号名称']
        df_mapped = df_mapped[required_columns]
        
        # 处理时间格式
        if '发布时间' in df_mapped.columns:
            df_mapped['发布时间'] = pd.to_datetime(df_mapped['发布时间'].astype(str), format='%Y%m%d', errors='coerce')
        
        # 合并数据
        merged_df = merge_csv_data(df_mapped, csv_path, ['标题', '账号名称'])
        
        # 清理数据，只保留必要的列
        if '内容标题' in merged_df.columns:
            final_columns = ['内容标题', '发表时间', '总阅读人数', '总阅读次数', '总分享人数', '总分享次数', 
                           '阅读后关注人数', '送达人数', '公众号消息阅读次数', '送达阅读率', 
                           '首次分享次数', '分享产生阅读次数', '首次分享率', '每次分享带来阅读次数', 
                           '阅读完成率', '内容url', '账号名称']
            merged_df = merged_df[final_columns]
        
        # 保存
        merged_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"成功更新publish_history.csv，总行数: {len(merged_df)}")
        
    except Exception as e:
        print(f"更新publish_history.csv失败: {e}")

def update_calendar_csv(df: pd.DataFrame):
    """更新publish_history_for_calendar.csv文件"""
    try:
        if '内容标题' not in df.columns:
            print("Excel文件列名不匹配，无法更新publish_history_for_calendar.csv")
            return
        
        # 映射列名
        df_mapped = map_wechat_columns(df)
        
        # 添加账号名称列
        df_mapped['账号名称'] = df_mapped.apply(
            lambda row: determine_account_name(row, 'AGI观察室'), axis=1
        )
        
        # 选择需要的列
        required_columns = ['标题', '账号名称', '发布时间', '阅读量', '点赞量', '评论量', '链接', '分享量']
        df_mapped = df_mapped[required_columns]
        
        # 处理时间格式
        df_mapped['发布时间'] = df_mapped['发布时间'].apply(convert_excel_date)
        
        # 合并数据
        calendar_csv_path = get_calendar_csv_path()
        merged_df = merge_csv_data(df_mapped, calendar_csv_path, ['标题', '账号名称'])
        
        # 重新生成index列
        merged_df = merged_df.reset_index(drop=True)
        merged_df.index.name = 'index'
        
        # 保存
        merged_df.to_csv(calendar_csv_path, index=True, encoding='utf-8-sig')
        print(f"成功更新publish_history_for_calendar.csv，总行数: {len(merged_df)}")
        
    except Exception as e:
        print(f"更新publish_history_for_calendar.csv失败: {e}")

# ==================== 数据同步函数 ====================

def sync_wechat_to_calendar():
    """将微信公众号数据同步到publish_history_for_calendar.csv"""
    try:
        # 读取微信公众号数据
        wechat_csv_path = load_csv_path()
        if not os.path.exists(wechat_csv_path):
            print(f"微信公众号数据文件不存在: {wechat_csv_path}")
            return False
        
        wechat_df = pd.read_csv(wechat_csv_path, encoding='utf-8')
        if wechat_df.empty:
            print("微信公众号数据为空")
            return False
        
        # 读取日历数据文件
        calendar_csv_path = get_calendar_csv_path()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(calendar_csv_path), exist_ok=True)
        
        # 如果日历文件不存在，创建空的
        if not os.path.exists(calendar_csv_path):
            calendar_columns = ["标题", "账号名称", "发布时间", "阅读量", "点赞量", "评论量", "链接"]
            calendar_df = pd.DataFrame(columns=calendar_columns)
            calendar_df.to_csv(calendar_csv_path, index=False, encoding='utf-8-sig')
        
        # 读取现有日历数据
        try:
            calendar_df = pd.read_csv(calendar_csv_path, encoding='utf-8-sig')
        except pd.errors.EmptyDataError:
            calendar_columns = ["标题", "账号名称", "发布时间", "阅读量", "点赞量", "评论量", "链接"]
            calendar_df = pd.DataFrame(columns=calendar_columns)
        
        # 字段映射：微信公众号 -> 日历格式
        wechat_df['发表时间'] = pd.to_datetime(wechat_df['发表时间'], errors='coerce')
        wechat_df = wechat_df.dropna(subset=['发表时间'])
        
        # 创建映射后的数据
        mapped_data = []
        for _, row in wechat_df.iterrows():
            mapped_row = {
                '标题': row['内容标题'] if pd.notna(row['内容标题']) else '',
                '账号名称': row['账号名称'] if pd.notna(row['账号名称']) else '',
                '发布时间': row['发表时间'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['发表时间']) else '',
                '阅读量': int(row['总阅读人数']) if pd.notna(row['总阅读人数']) else 0,
                '点赞量': 0,
                '评论量': 0,
                '链接': row['内容url'] if pd.notna(row['内容url']) else ''
            }
            mapped_data.append(mapped_row)
        
        # 转换为DataFrame
        mapped_df = pd.DataFrame(mapped_data)
        
        # 合并数据，避免重复
        if not calendar_df.empty:
            calendar_df['发布时间'] = pd.to_datetime(calendar_df['发布时间'], errors='coerce')
            
            # 找出新增的文章（基于标题和发布时间）
            existing_articles = set()
            for _, row in calendar_df.iterrows():
                if pd.notna(row['标题']) and pd.notna(row['发布时间']):
                    existing_articles.add((row['标题'], row['发布时间'].strftime('%Y-%m-%d %H:%M:%S')))
            
            # 过滤出新文章
            new_articles = []
            for _, row in mapped_df.iterrows():
                if (row['标题'], row['发布时间']) not in existing_articles:
                    new_articles.append(row)
            
            if new_articles:
                new_df = pd.DataFrame(new_articles)
                combined_df = pd.concat([calendar_df, new_df], ignore_index=True)
                print(f"新增 {len(new_articles)} 篇微信公众号文章到日历")
            else:
                combined_df = calendar_df
                print("没有新的微信公众号文章需要添加")
        else:
            combined_df = mapped_df
            print(f"添加 {len(mapped_df)} 篇微信公众号文章到日历")
        
        # 保存合并后的数据
        combined_df.to_csv(calendar_csv_path, index=False, encoding='utf-8-sig')
        print(f"成功同步数据到: {calendar_csv_path}")
        return True
        
    except Exception as e:
        print(f"同步微信公众号数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def update_wechat_data_in_calendar():
    """更新微信公众号数据在日历中的信息（如阅读量等）"""
    try:
        # 读取微信公众号数据
        wechat_csv_path = load_csv_path()
        if not os.path.exists(wechat_csv_path):
            print(f"微信公众号数据文件不存在: {wechat_csv_path}")
            return False
        
        wechat_df = pd.read_csv(wechat_csv_path, encoding='utf-8')
        if wechat_df.empty:
            print("微信公众号数据为空")
            return False
        
        # 读取日历数据文件
        calendar_csv_path = get_calendar_csv_path()
        
        if not os.path.exists(calendar_csv_path):
            print("日历数据文件不存在，请先运行sync_wechat_to_calendar()")
            return False
        
        calendar_df = pd.read_csv(calendar_csv_path, encoding='utf-8-sig')
        if calendar_df.empty:
            print("日历数据为空")
            return False
        
        # 处理时间格式
        wechat_df['发表时间'] = pd.to_datetime(wechat_df['发表时间'], errors='coerce')
        calendar_df['发布时间'] = pd.to_datetime(calendar_df['发布时间'], errors='coerce')
        
        # 更新现有文章的阅读量等信息
        updated_count = 0
        for idx, calendar_row in calendar_df.iterrows():
            # 查找匹配的微信公众号文章
            matching_wechat = wechat_df[
                (wechat_df['内容标题'] == calendar_row['标题']) & 
                (wechat_df['账号名称'] == calendar_row['账号名称'])
            ]
            
            if not matching_wechat.empty:
                wechat_row = matching_wechat.iloc[0]
                # 更新阅读量
                if pd.notna(wechat_row['总阅读人数']):
                    calendar_df.at[idx, '阅读量'] = int(wechat_row['总阅读人数'])
                    updated_count += 1
        
        if updated_count > 0:
            # 保存更新后的数据
            calendar_df.to_csv(calendar_csv_path, index=False, encoding='utf-8-sig')
            print(f"成功更新 {updated_count} 篇文章的阅读量信息")
        else:
            print("没有文章需要更新")
        
        return True
        
    except Exception as e:
        print(f"更新微信公众号数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# ==================== 主要执行函数 ====================

def update_wechat_data_from_excel(begin_date="20250609", end_date="20250818", token="254511315", cookies=None, account_name="AGI观察室"):
    """从微信公众号Excel数据更新到CSV文件"""
    # 使用自定义cookies或默认cookies
    if cookies is None:
        cookies = DEFAULT_COOKIES
    
    print(f"正在获取 {account_name} 的数据，时间范围：{begin_date} 到 {end_date}")
    result1 = get_wechat_data_cube(begin_date, end_date, token, cookies)
    
    if result1['success']:
        print("请求成功！")
        print("响应类型:", result1.get('content_type', '未知'))
        print("状态码:", result1.get('status_code', '未知'))
        print("数据类型:", type(result1['data']))
        print("数据长度:", len(result1['data']) if hasattr(result1['data'], '__len__') else 'N/A')
        print("是否标记为Excel:", result1.get('is_excel', False))
        
        # 处理响应数据
        if result1.get('is_excel') or 'excel' in result1.get('content_type', '').lower() or 'xls' in result1.get('content_type', '').lower():
            # 如果是Excel文件，保存为二进制并读取数据
            with open("result.xls", "wb") as f:
                if isinstance(result1['data'], bytes):
                    f.write(result1['data'])
                elif isinstance(result1['data'], str):
                    f.write(result1['data'].encode('latin1'))
                else:
                    f.write(str(result1['data']).encode('latin1'))
            
            print("Excel文件已保存到 result.xls")
            
            # 读取Excel数据
            try:
                df = pd.read_excel("result.xls")
                print("Excel数据预览:")
                print(df.head().to_markdown())
                print(f"\n总行数: {len(df)}")
                print(f"列名: {list(df.columns)}")
                
                # 使用原有的append_record_to_csv更新publish_history.csv
                append_record_to_csv(df)
                
                # 然后使用sync_wechat_to_calendar同步到publish_history_for_calendar.csv
                if sync_wechat_to_calendar():
                    print("数据已成功同步到日历CSV文件")
                else:
                    print("同步到日历CSV文件失败")
                
            except Exception as e:
                print(f"读取Excel文件失败: {e}")
                
        elif result1.get('is_html'):
            print("返回的是HTML内容，长度:", len(result1['data']))
            # 保存HTML内容
            with open("result.html", "w", encoding='utf-8') as f:
                f.write(result1['data'])
            print("HTML内容已保存到 result.html")
        elif 'csv' in result1.get('content_type', '').lower():
            # 如果是CSV数据，保存为CSV
            with open("result.csv", "w", encoding='utf-8') as f:
                f.write(result1['data'])
            print("CSV数据已保存到 result.csv")
        else:
            # 检查内容是否包含Excel文件特征
            if 'Root Entry' in result1['data'] or 'Workbook' in result1['data']:
                # 可能是Excel文件，尝试保存为.xls
                try:
                    with open("result.xls", "wb") as f:
                        f.write(result1['data'].encode('latin1') if isinstance(result1['data'], str) else result1['data'])
                    print("检测到Excel文件特征，已保存到 result.xls")
                except Exception as e:
                    print(f"保存Excel文件失败: {e}")
                    # 回退到文本保存
                    with open("result.txt", "w", encoding='utf-8') as f:
                        f.write(str(result1['data']))
                    print("回退保存为 result.txt")
            else:
                # 保存原始数据
                with open("result.txt", "w", encoding='utf-8') as f:
                    f.write(str(result1['data']))
                print("原始数据已保存到 result.txt")
    else:
        print("请求失败:", result1['error'])

# ==================== 主程序入口 ====================

if __name__ == '__main__':
    # 测试新的数据统计函数
    print("\n=== 测试微信公众号数据统计功能 ===")
    update_wechat_data_from_excel()
