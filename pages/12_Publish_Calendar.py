import pandas as pd
import os
import sys
import streamlit as st
import calendar
from datetime import datetime, date, timedelta
import random

# 使用简化路径管理 - 必须在导入core模块之前
from simple_paths import *

# 导入core模块
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

# 尝试导入频道更新管理器
try:
    from core.channel.channel_update_manager import ChannelUpdateManager
except ImportError as e:
    # 如果导入失败，在页面中显示错误（而不是在这里，避免阻止页面加载）
    ChannelUpdateManager = None
    channel_update_error = str(e)


def load_csv_data():
    """从CSV文件加载数据"""
    try:
        # 优先读取 publish_history_for_calendar.csv 文件
        csv_path = "workspace/data/publish_history_for_calendar.csv"
        
        if os.path.exists(csv_path):
            st.toast(f"成功找到数据文件: {csv_path}", icon="✅")
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            
            # 检查必要的列是否存在
            if '发布时间' in df.columns:
                # 转换时间列
                df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
                # 过滤掉无效的日期数据
                df = df.dropna(subset=['发布时间'])
                
                # 清理账号名称列（如果存在）
                if '账号名称' in df.columns:
                    # 过滤掉空值和无效的账号名称
                    df = df[df['账号名称'].notna()]
                    df = df[df['账号名称'].astype(str).str.strip() != '']
                    # 确保账号名称是字符串类型
                    df['账号名称'] = df['账号名称'].astype(str)
                
                if not df.empty:
                    st.toast(f"成功加载 {len(df)} 条数据记录")
                    return df
                else:
                    st.warning("数据加载成功但所有日期数据都无效")
                    return pd.DataFrame()
            else:
                st.error(f"CSV文件缺少'发布时间'列，当前列名: {list(df.columns)}")
                return pd.DataFrame()
        
        # 备用方案：尝试从app目录的上级目录加载
        csv_path2 = "../workspace/data/publish_history_for_calendar.csv"
        if os.path.exists(csv_path2):
            st.toast(f"成功找到数据文件: {csv_path2}")
            df = pd.read_csv(csv_path2, encoding='utf-8-sig')
            
            if '发布时间' in df.columns:
                df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
                df = df.dropna(subset=['发布时间'])
                
                # 清理账号名称列（如果存在）
                if '账号名称' in df.columns:
                    df = df[df['账号名称'].notna()]
                    df = df[df['账号名称'].astype(str).str.strip() != '']
                    df['账号名称'] = df['账号名称'].astype(str)
                
                if not df.empty:
                    st.toast(f"成功加载 {len(df)} 条数据记录")
                    return df
                else:
                    st.warning("数据加载成功但所有日期数据都无效")
                    return pd.DataFrame()
            else:
                st.error(f"CSV文件缺少'发布时间'列，当前列名: {list(df.columns)}")
                return pd.DataFrame()
        
        # 备用方案：尝试从当前工作目录加载
        csv_path3 = os.path.join(os.getcwd(), "workspace", "data", "publish_history_for_calendar.csv")
        if os.path.exists(csv_path3):
            st.toast(f"成功找到数据文件: {csv_path3}")
            df = pd.read_csv(csv_path3, encoding='utf-8-sig')
            
            if '发布时间' in df.columns:
                df['发布时间'] = pd.to_datetime(df['发布时间'], errors='coerce')
                df = df.dropna(subset=['发布时间'])
                
                # 清理账号名称列（如果存在）
                if '账号名称' in df.columns:
                    df = df[df['账号名称'].notna()]
                    df = df[df['账号名称'].astype(str).str.strip() != '']
                    df['账号名称'] = df['账号名称'].astype(str)
                
                if not df.empty:
                    st.toast(f"成功加载 {len(df)} 条数据记录")
                    return df
                else:
                    st.warning("数据加载成功但所有日期数据都无效")
                    return pd.DataFrame()
            else:
                st.error(f"CSV文件缺少'发布时间'列，当前列名: {list(df.columns)}")
                return pd.DataFrame()
        
        # 如果所有方法都失败，显示错误信息
        st.error("未找到 publish_history_for_calendar.csv 数据文件，尝试了以下路径:")
        st.info(f"1. {csv_path}")
        st.info(f"2. {csv_path2}")
        st.info(f"3. {csv_path3}")
        st.info(f"当前工作目录: {os.getcwd()}")
        
        # 列出当前目录下的文件
        st.info("当前目录内容:")
        st.write(os.listdir("."))
        
        # 如果存在workspace目录，列出其内容
        if os.path.exists("workspace"):
            st.info("workspace目录内容:")
            st.write(os.listdir("workspace"))
            if os.path.exists("workspace/data"):
                st.info("workspace/data目录内容:")
                st.write(os.listdir("workspace/data"))
        
        return pd.DataFrame()

    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        st.exception(e)
        return pd.DataFrame()


def get_account_colors(accounts):
    """为每个账号分配固定的颜色"""
    # 预定义的颜色列表，确保颜色区分度
    colors = [
        '#FF6B6B',  # 红色 - AGI启示录
        '#4ECDC4',  # 青色 - AGI观察室  
        '#45B7D1',  # 蓝色 - AI万象志
        '#96CEB4',  # 绿色 - 人工智能漫游指南
        '#FFEAA7',  # 黄色
        '#DDA0DD',  # 紫色
        '#98D8C8',  # 薄荷绿
        '#F7DC6F',  # 金黄色
        '#BB8FCE',  # 淡紫色
        '#85C1E9',  # 天蓝色
        '#F8C471',  # 橙色
        '#82E0AA',  # 浅绿色
        '#F1948A',  # 粉红色
        '#D7BDE2',  # 淡紫色
        '#AED6F1',  # 浅蓝色
    ]
    
    # 过滤掉无效的账号名称（NaN、None、空字符串等）
    valid_accounts = []
    for account in accounts:
        if pd.notna(account) and account and str(account).strip():
            valid_accounts.append(str(account))
    
    # 为了确保颜色一致性，我们对账号名称进行排序
    sorted_accounts = sorted(valid_accounts)
    account_colors = {}
    for i, account in enumerate(sorted_accounts):
        account_colors[account] = colors[i % len(colors)]
    
    return account_colors


def calculate_update_reminders(df):
    """计算每个账号的更新提醒（考虑工作日因素）"""
    if df.empty:
        return {}
    
    # 获取当前日期（昨天，因为统计接口只能更新到昨日）
    yesterday = date.today() - timedelta(days=1)
    
    reminders = {}
    
    # 按账号分组分析
    for account in df['账号名称'].unique():
        account_data = df[df['账号名称'] == account].copy()
        
        if len(account_data) < 2:  # 至少需要2篇文章才能计算频率
            continue
            
        # 确保时间列是datetime类型
        account_data['发布时间'] = pd.to_datetime(account_data['发布时间'], errors='coerce')
        account_data = account_data.dropna(subset=['发布时间'])
        
        if len(account_data) < 2:
            continue
            
        # 按时间排序
        account_data = account_data.sort_values('发布时间')
        
        # 计算历史发布频率（考虑工作日）
        first_date = account_data['发布时间'].min().date()
        last_date = account_data['发布时间'].max().date()
        
        # 计算总工作日数量（排除周末）
        total_workdays = 0
        current_date = first_date
        while current_date <= last_date:
            # 0=周一, 1=周二, ..., 4=周五, 5=周六, 6=周日
            if current_date.weekday() < 5:  # 周一到周五
                total_workdays += 1
            current_date += timedelta(days=1)
        
        total_posts = len(account_data)
        
        if total_workdays > 0:
            # 使用工作日计算平均频率
            avg_frequency_workdays = total_workdays / total_posts  # 工作日/篇
            
            # 计算当前更新间隔（从最后更新到昨天，只计算工作日）
            current_workday_interval = 0
            current_date = last_date + timedelta(days=1)
            while current_date <= yesterday:
                if current_date.weekday() < 5:  # 周一到周五
                    current_workday_interval += 1
                current_date += timedelta(days=1)
            
            # 计算比值（基于工作日）
            ratio = current_workday_interval / avg_frequency_workdays if avg_frequency_workdays > 0 else float('inf')
            
            # 同时保留传统日历日计算（用于对比）
            total_calendar_days = (last_date - first_date).days + 1
            avg_frequency_calendar = total_calendar_days / total_posts if total_posts > 0 else 0
            current_calendar_interval = (yesterday - last_date).days
            ratio_calendar = current_calendar_interval / avg_frequency_calendar if avg_frequency_calendar > 0 else float('inf')
            
            reminders[account] = {
                'avg_frequency_workdays': avg_frequency_workdays,  # 工作日/篇
                'avg_frequency_calendar': avg_frequency_calendar,  # 日历日/篇
                'current_workday_interval': current_workday_interval,  # 当前工作日间隔
                'current_calendar_interval': current_calendar_interval,  # 当前日历日间隔
                'ratio': ratio,  # 基于工作日的比值
                'ratio_calendar': ratio_calendar,  # 基于日历日的比值
                'total_posts': total_posts,
                'total_workdays': total_workdays,
                'total_calendar_days': total_calendar_days,
                'last_update': last_date,
                'first_update': first_date
            }
    
    return reminders


def visualize_publish_calendar():
    # 加载主题
    load_anthropic_theme()
    
    df = load_csv_data()
    
    if df.empty:
        st.error("无法加载数据，请检查数据文件")
        return

    st.title("自媒体矩阵发布日历")
    
    # 添加一键更新按钮区域
    st.write("---")
    st.write("### 🔄 一键更新所有频道")
    
    # 创建两列布局：左侧更新按钮，右侧状态显示
    col_update1, col_update2 = st.columns([2, 3])
    
    with col_update1:
        # 一键更新按钮
        if st.button(f"一键更新所有频道", type="primary", use_container_width=True):
            # 检查ChannelUpdateManager是否可用
            if ChannelUpdateManager is None:
                st.error(f"频道更新管理器加载失败")
                if 'channel_update_error' in globals():
                    st.error(f"错误详情: {channel_update_error}")
                st.info("请检查 core/channel/channel_update_manager.py 文件是否存在")
            else:
                try:
                    # 初始化频道更新管理器
                    update_manager = ChannelUpdateManager()
                    
                    # 执行更新
                    with st.spinner("正在更新所有频道，请稍候..."):
                        update_results = update_manager.update_all_channels()
                    
                    # 将更新结果存储到session state
                    st.session_state.update_results = update_results
                    st.session_state.last_update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 显示更新完成提示
                    st.success(f"频道更新完成！")
                    
                    # 自动刷新页面数据
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"更新过程中发生错误: {str(e)}")
                    st.exception(e)
    
    with col_update2:
        # 显示更新状态和结果
        if 'update_results' in st.session_state and st.session_state.update_results:
            st.write("**📊 最近更新结果:**")
            
            # 统计成功和失败数量
            success_count = len([r for r in st.session_state.update_results.values() if r['status'] == 'success'])
            error_count = len([r for r in st.session_state.update_results.values() if r['status'] == 'error'])
            
            # 显示统计信息
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("总频道数", len(st.session_state.update_results))
            with col_stat2:
                st.metric("成功", success_count, delta=f"+{success_count}")
            with col_stat3:
                st.metric("失败", error_count, delta=f"-{error_count}" if error_count > 0 else None)
            
            # 显示最后更新时间
            if 'last_update_time' in st.session_state:
                st.caption(f"最后更新: {st.session_state.last_update_time}")
            
            # 展开显示详细结果
            with st.expander(f"查看详细更新结果"):
                for channel_name, result in st.session_state.update_results.items():
                    status_icon = "✅" if result['status'] == 'success' else "❌"
                    st.write(f"{status_icon} **{channel_name}**: {result['message']}")
                    st.caption(f"更新时间: {result['timestamp']}")
                    st.write("---")
        else:
            st.info(f"点击左侧按钮开始更新所有频道")
    
    st.write("---")

    # 检查数据是否为空
    if df.empty:
        st.warning("没有可用的数据")
        return

    # 获取数据的年份和月份范围
    df['年份'] = df['发布时间'].dt.year
    df['月份'] = df['发布时间'].dt.month
    
    min_year = int(df['年份'].min())
    max_year = int(df['年份'].max())
    
    # 获取所有可用的年月组合
    available_months = df[['年份', '月份']].drop_duplicates().sort_values(['年份', '月份'])
    
    # 创建月份选择器
    st.write("### 选择月份")
    
    # 方法1：使用selectbox选择年月
    if not available_months.empty:
        # 创建年月选项
        month_options = []
        for _, row in available_months.iterrows():
            month_options.append(f"{int(row['年份'])}年{int(row['月份'])}月")
        
        selected_month_str = st.selectbox(
            "选择要查看的月份",
            options=month_options,
            index=len(month_options) - 1  # 默认选择最新的月份
        )
        
        # 解析选择的年月
        selected_year = int(selected_month_str.split('年')[0])
        selected_month = int(selected_month_str.split('年')[1].split('月')[0])
        

    else:
        st.error("没有可用的月份数据")
        return

    # 过滤数据
    filtered_df = df[(df['发布时间'].dt.year == selected_year) & (df['发布时间'].dt.month == selected_month)]
    

    # 使用CSS样式优化日历布局 - 苹果风格
    st.markdown("""
    <style>
    /* 移除Streamlit所有可能的宽度限制 */
    .main .block-container,
    .main .block-container > div,
    .stMainBlockContainer,
    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: none !important;
        width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* 日历表格样式 - 苹果风格 */
    .apple-calendar {
        width: 100%;
        border-collapse: collapse;
        background: var(--calendar-bg, #ffffff);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        table-layout: fixed; /* 确保表格列等宽 */
    }
    
    /* 表头样式 */
    .apple-calendar thead {
        background: var(--header-bg, #f5f5f7);
        border-bottom: 1px solid var(--border-color, #d2d2d7);
    }
    
    .apple-calendar th {
        width: 14.28571429%; /* 100% / 7 = 14.28571429% 确保7列等宽 */
        padding: 12px 8px;
        text-align: center;
        font-size: 13px;
        font-weight: 600;
        color: var(--header-text, #8e8e93);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 日期单元格样式 */
    .apple-calendar td {
        width: 14.28571429%; /* 100% / 7 = 14.28571429% 确保7列等宽 */
        border: 1px solid var(--border-color, #d2d2d7);
        padding: 8px;
        height: 100px;
        vertical-align: top;
        background: var(--cell-bg, #ffffff);
        position: relative;
        transition: background-color 0.2s ease;
    }
    
    .apple-calendar td:hover {
        background: var(--cell-hover, #f5f5f7);
    }
    
    /* 周末列样式 - 稍微灰一点 */
    .apple-calendar td:first-child,
    .apple-calendar td:last-child {
        background: var(--weekend-bg, #f8f8f8);
    }
    
    .apple-calendar td:first-child:hover,
    .apple-calendar td:last-child:hover {
        background: var(--weekend-hover, #f0f0f0);
    }
    
    /* 日期数字样式 */
    .cal-day-number {
        font-size: 15px;
        font-weight: 500;
        color: var(--day-text, #1d1d1f);
        margin-bottom: 4px;
    }
    
    .cal-day-number.today {
        background: #007aff;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
    }
    
    /* 空日期样式 */
    .cal-empty {
        background: var(--empty-bg, #fafafa);
    }
    
    /* 文章标签样式 */
    .cal-event {
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 4px;
        margin: 2px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-weight: 500;
    }
    
    /* 账号小圆点 */
    .cal-dots {
        display: flex;
        gap: 4px;
        margin-top: 4px;
        flex-wrap: wrap;
    }
    
    .cal-dot {
        border-radius: 50%;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    
    .cal-dot:hover {
        transform: scale(1.2);
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    
    .cal-dot.clickable {
        cursor: pointer;
    }
    
    .cal-dot.non-clickable {
        cursor: default;
    }
    
    /* 链接样式 */
    .cal-dots a {
        text-decoration: none;
        display: inline-block;
    }
    
    .cal-dots a:hover .cal-dot {
        transform: scale(1.2);
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    
    /* 自定义tooltip样式 - 使用JavaScript动态创建 */
    .custom-tooltip {
        position: fixed !important;
        z-index: 2147483647 !important;
        background: rgba(0, 0, 0, 0.95) !important;
        color: white !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        white-space: pre-line !important;
        text-align: left !important;
        min-width: 250px !important;
        max-width: 400px !important;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
        pointer-events: none !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif !important;
        line-height: 1.4 !important;
        backdrop-filter: blur(10px) !important;
        border: none !important;
        margin: 0 !important;
        overflow: visible !important;
        clip: auto !important;
        clip-path: none !important;
    }
    
    /* 确保tooltip不被任何元素覆盖 */
    .custom-tooltip * {
        z-index: inherit !important;
        position: relative !important;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .apple-calendar td {
            height: 80px;
            padding: 6px;
        }
        .cal-day-number {
            font-size: 14px;
        }
        .cal-event {
            font-size: 10px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 追加更兼容的暗黑主题柔和配色（兼容多种选择器 + 系统深色偏好）
    st.markdown("""
    <style>
    /* 兼容 Streamlit 各版本暗色选择器 */
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar {
      background: #14161b !important;
      box-shadow: 0 2px 8px rgba(0,0,0,0.35) !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar thead {
      background: #1b1e24 !important;
      border-bottom: 1px solid #2a2d36 !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar th {
      color: #9aa3ad !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar td {
      background: #14161b !important;
      border-color: #252932 !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar td:hover {
      background: #1b1f26 !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .cal-day-number {
      color: #e0e3e7 !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .cal-day-number.today {
      background: #2d6cdf !important;
      color: #ffffff !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .cal-empty {
      background: #101218 !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar td:first-child,
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar td:last-child {
      background: #171a21 !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar td:first-child:hover,
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar td:last-child:hover {
      background: #1e222b !important;
    }
    :is(html[data-theme="dark"], body[data-theme="dark"], .stApp[data-theme="dark"], [data-testid="stAppViewContainer"][data-theme="dark"], :root[data-theme="dark"]) .apple-calendar .cal-event {
      background: rgba(0,122,255,0.18) !important;
      color: #9ecaff !important;
      border: 1px solid rgba(0,122,255,0.22) !important;
    }

    /* 系统深色偏好作为兜底 */
    @media (prefers-color-scheme: dark) {
      .apple-calendar { background: #14161b !important; box-shadow: 0 2px 8px rgba(0,0,0,0.35) !important; }
      .apple-calendar thead { background: #1b1e24 !important; border-bottom: 1px solid #2a2d36 !important; }
      .apple-calendar th { color: #9aa3ad !important; }
      .apple-calendar td { background: #14161b !important; border-color: #252932 !important; }
      .apple-calendar td:hover { background: #1b1f26 !important; }
      .cal-day-number { color: #e0e3e7 !important; }
      .cal-day-number.today { background: #2d6cdf !important; color: #ffffff !important; }
      .cal-empty { background: #101218 !important; }
      .apple-calendar td:first-child, .apple-calendar td:last-child { background: #171a21 !important; }
      .apple-calendar td:first-child:hover, .apple-calendar td:last-child:hover { background: #1e222b !important; }
      .apple-calendar .cal-event { background: rgba(0,122,255,0.18) !important; color: #9ecaff !important; border: 1px solid rgba(0,122,255,0.22) !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 创建苹果风格的日历
    st.write(f"### {selected_year}年{selected_month}月")
    
    # 获取当前日期
    today = date.today()
    
    # 构建HTML表格 - 周日在左侧，周六在右侧
    calendar_html = """
    <table class="apple-calendar">
        <thead>
            <tr>
                <th>周日</th>
                <th>周一</th>
                <th>周二</th>
                <th>周三</th>
                <th>周四</th>
                <th>周五</th>
                <th>周六</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # 使用calendar模块生成以周日为起始的日历
    import calendar as cal_module
    
    # 设置一周的第一天为周日 (6表示周日)
    cal_module.setfirstweekday(6)  # 6 = 周日
    cal_sunday_first = cal_module.monthcalendar(selected_year, selected_month)
    
    # 生成日历行
    for week in cal_sunday_first:
        calendar_html += "<tr>"
        
        for day in week:
            if day == 0:
                calendar_html += '<td class="cal-empty"></td>'
            else:
                daily_posts = filtered_df[filtered_df['发布时间'].dt.day == day]
                
                # 检查是否是今天
                is_today = (today.year == selected_year and 
                           today.month == selected_month and 
                           today.day == day)
                
                calendar_html += '<td>'
                
                # 日期数字
                if is_today:
                    calendar_html += f'<div class="cal-day-number today">{day}</div>'
                else:
                    calendar_html += f'<div class="cal-day-number">{day}</div>'
                
                if not daily_posts.empty:
                    # 文章数量标签
                    calendar_html += f'<div class="cal-event" style="background: #007aff20; color: #007aff;">{daily_posts.shape[0]}篇</div>'
                    
                    # 账号小圆点
                    account_counts = daily_posts['账号名称'].value_counts()
                    # 获取所有账号的颜色（保持一致性）
                    all_accounts = filtered_df['账号名称'].unique()
                    account_colors = get_account_colors(all_accounts)
                    
                    calendar_html += '<div class="cal-dots">'
                    # 按账号名称排序，确保显示顺序一致
                    for account in sorted(account_counts.index):
                        account_posts = daily_posts[daily_posts['账号名称'] == account]
                        # 为每篇文章显示一个小圆点
                        for _, post in account_posts.iterrows():
                            # 计算小圆点大小（基于阅读量，整体放大，更敏感的变化）
                            read_count = post.get('阅读量', 0)
                            if pd.isna(read_count) or read_count == 0:
                                dot_size = 8  # 最小尺寸
                            elif read_count < 100:
                                dot_size = 10
                            elif read_count < 300:
                                dot_size = 12
                            elif read_count < 600:
                                dot_size = 14
                            elif read_count < 1000:
                                dot_size = 16
                            elif read_count < 2000:
                                dot_size = 18
                            elif read_count < 5000:
                                dot_size = 20
                            elif read_count < 10000:
                                dot_size = 22
                            else:
                                dot_size = 26  # 最大尺寸
                            
                            # 获取文章链接
                            article_link = post.get('链接', '')
                            
                            # 构建详细的提示信息
                            title = post.get('标题', '')
                            like_count = post.get('点赞量', 0)
                            if pd.isna(like_count):
                                like_count = 0
                            
                            # 使用HTML实体编码处理特殊字符，避免HTML解析问题
                            import html
                            safe_title = html.escape(str(title))
                            safe_account = html.escape(str(account))
                            safe_read_count = html.escape(str(read_count))
                            safe_like_count = html.escape(str(like_count))
                            
                            # 格式化提示信息（使用HTML换行标签）
                            tooltip_text = f"{safe_title}<br>账号: {safe_account}<br>阅读量: {safe_read_count}<br>点赞量: {safe_like_count}"
                            
                            if article_link and pd.notna(article_link):
                                # 可点击的小圆点 - 使用a标签包装
                                calendar_html += f'<a href="{article_link}" target="_blank" style="text-decoration: none;"><div class="cal-dot" style="background: {account_colors[account]}; width: {dot_size}px; height: {dot_size}px;" data-tooltip="{tooltip_text}"></div></a>'
                            else:
                                # 不可点击的小圆点
                                calendar_html += f'<div class="cal-dot" style="background: {account_colors[account]}; width: {dot_size}px; height: {dot_size}px;" data-tooltip="{tooltip_text}"></div>'
                    calendar_html += '</div>'
                
                calendar_html += '</td>'
        calendar_html += "</tr>"
    
    calendar_html += """
        </tbody>
    </table>
    """
    
    # 创建两列布局：左侧日历，右侧图例和统计
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # 左侧显示日历
        st.markdown(calendar_html, unsafe_allow_html=True)
        
        # 添加纯CSS tooltip样式
        st.markdown("""
        <style>
        .cal-dot {
          position: relative;
          cursor: pointer;
          transition: transform 0.15s ease;
        }
        
        .cal-dot:hover {
          transform: scale(1.1);
        }
        
        .cal-dot::after {
          content: attr(data-tooltip);
          position: absolute;
          bottom: 100%;
          left: 50%;
          transform: translateX(-50%);
          background: rgba(0, 0, 0, 0.95);
          color: white;
          padding: 10px 14px;
          border-radius: 8px;
          font-size: 12px;
          white-space: pre-line;
          text-align: left;
          min-width: 220px;
          max-width: 320px;
          z-index: 999999;
          opacity: 0;
          visibility: hidden;
          transition: all 0.2s ease;
          pointer-events: none;
          box-shadow: 0 6px 20px rgba(0,0,0,0.4);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
          line-height: 1.4;
        }
        
        .cal-dot:hover::after {
          opacity: 1;
          visibility: visible;
        }
        
        /* 确保tooltip不被裁剪 */
        .apple-calendar {
          overflow: visible !important;
        }
        
        /* 点击动画 */
        .cal-dot:active {
          transform: scale(0.9);
        }
        
        /* 确保链接内的tooltip也能显示 */
        a:hover .cal-dot::after {
          opacity: 1;
          visibility: visible;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 简单的点击动画
        st.markdown("""
        <script>
        (function(){
          // 为所有小圆点添加点击动画
          document.addEventListener('click', function(e) {
            const dot = e.target.closest('.cal-dot');
            if (dot) {
              dot.style.transform = 'scale(0.85)';
              setTimeout(function() {
                dot.style.transform = 'scale(1)';
              }, 150);
            }
          });
          
          console.log('Click animation ready!');
        })();
        </script>
        """, unsafe_allow_html=True)

        # 重置calendar模块设置，避免影响其他代码
        cal_module.setfirstweekday(0)  # 恢复默认设置（周一为第一天）

    with col2:
        # 右侧显示图例和统计（图例在上，统计在下）
        total_articles = len(filtered_df)
        total_accounts = len(filtered_df['账号名称'].unique()) if not filtered_df.empty else 0
        
        # 图例说明（放在上面）
        st.write(f"### 图例说明")
        st.caption(f"{total_articles}篇 · {total_accounts}个账号")
        
        if not filtered_df.empty:
            # 获取所有账号并排序
            accounts = sorted(filtered_df['账号名称'].unique())
            account_colors = get_account_colors(accounts)
            
            # 显示每个账号的颜色、文章数量和占比（紧凑显示）
            for account in accounts:
                account_posts = filtered_df[filtered_df['账号名称'] == account]
                count = len(account_posts)
                percentage = round((count / total_articles) * 100, 1)
                
                # 创建紧凑的图例项
                st.markdown(
                    f'<div style="display: flex; align-items: center; margin: 4px 0; font-size: 12px;">'
                    f'<div style="width: 12px; height: 12px; border-radius: 50%; '
                    f'background-color: {account_colors[account]}; margin-right: 6px; '
                    f'box-shadow: 0 1px 2px rgba(0,0,0,0.1);"></div>'
                    f'<div style="flex: 1; line-height: 1.2;">'
                    f'<span style="font-weight: 500;">{account}</span><br>'
                    f'<span style="color: #666; font-size: 11px;">{count}篇 ({percentage}%)</span>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("无数据")
        
        st.write("---")
        
        # 本月统计（放在下面，紧凑显示）
        st.write("### 本月统计")
        
        if not filtered_df.empty:
            # 使用紧凑的metric显示
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("文章数", total_articles, delta=None)
                st.metric("账号数", total_accounts, delta=None)
            
            with col_stat2:
                # 计算平均每个工作日发布数量
                if '发布时间' in filtered_df.columns:
                    filtered_df['发布时间'] = pd.to_datetime(filtered_df['发布时间'], errors='coerce')
                    filtered_df = filtered_df.dropna(subset=['发布时间'])
                    if not filtered_df.empty:
                        # 计算工作日数量（排除周末）
                        
                        # 获取该月的所有日期
                        month_start = datetime(selected_year, selected_month, 1)
                        if selected_month == 12:
                            next_month = datetime(selected_year + 1, 1, 1)
                        else:
                            next_month = datetime(selected_year, selected_month + 1, 1)
                        
                        # 计算该月的总天数
                        month_end = next_month - pd.Timedelta(days=1)
                        total_days = month_end.day
                        
                        # 计算工作日数量（周一到周五）
                        workdays = 0
                        for day in range(1, total_days + 1):
                            current_date = datetime(selected_year, selected_month, day)
                            # 0=周一, 1=周二, ..., 4=周五, 5=周六, 6=周日
                            if current_date.weekday() < 5:  # 周一到周五
                                workdays += 1
                        
                        # 计算平均每个工作日的发布数量
                        avg_workday_posts = round(total_articles / workdays, 1) if workdays > 0 else 0
                        
                        # 显示日均发布数量（基于工作日）
                        st.metric("日均", f"{avg_workday_posts}篇", delta=f"共{workdays}个工作日")
                        
        else:
            st.info("暂无数据")

    # 添加账号更新提醒区域（在日历下方）
    st.write("---")
    st.write("### 📊 账号更新提醒")
    
    
    # 计算账号更新提醒
    update_reminders = calculate_update_reminders(df)
    
    if update_reminders:
        # 找出需要更新的账号（基于工作日的比值 < 1）
        need_update = [acc for acc, data in update_reminders.items() if data['ratio'] < 1]
        
        if need_update:
            for account in need_update:
                data = update_reminders[account]
                st.write(f"• **{account}**：历史平均{data['avg_frequency_workdays']:.1f}个工作日/篇，"
                       f"当前工作日间隔{data['current_workday_interval']}天，比值{data['ratio']:.2f}")
            
            # 找出最需要更新的账号（基于工作日的比值最小）
            most_urgent = min(update_reminders.items(), key=lambda x: x[1]['ratio'])
            st.error(f"🚨 最需要更新：**{most_urgent[0]}**")
        else:
            st.success(f"所有账号更新频率正常（基于工作日计算）")
            
    else:
        st.info("暂无足够的历史数据进行分析")
    
    # 添加Cookie状态检查区域
    st.write("---")
    st.write("### 🔐 Cookie状态检查")
    
    if st.button(f"检查所有频道Cookie状态", use_container_width=True):
        # 检查ChannelUpdateManager是否可用
        if ChannelUpdateManager is None:
            st.error(f"频道更新管理器加载失败")
            if 'channel_update_error' in globals():
                st.error(f"错误详情: {channel_update_error}")
            st.info("请检查 core/channel/channel_update_manager.py 文件是否存在")
        else:
            try:
                # 初始化频道更新管理器
                update_manager = ChannelUpdateManager()
                
                # 检查Cookie状态
                with st.spinner("正在检查Cookie状态..."):
                    cookie_status = update_manager.check_cookie_status()
                
                # 显示Cookie状态
                if cookie_status:
                    st.write("**📊 Cookie状态概览:**")
                    
                    # 统计有效和失效的Cookie
                    valid_count = len([s for s in cookie_status.values() if s == 'valid'])
                    expired_count = len([s for s in cookie_status.values() if s == 'expired'])
                    
                    # 显示统计信息
                    col_cookie1, col_cookie2, col_cookie3 = st.columns(3)
                    with col_cookie1:
                        st.metric("总频道数", len(cookie_status))
                    with col_cookie2:
                        st.metric("Cookie有效", valid_count, delta=f"+{valid_count}")
                    with col_cookie3:
                        st.metric("Cookie失效", expired_count, delta=f"-{expired_count}" if expired_count > 0 else None)
                    
                    # 显示详细状态
                    with st.expander(f"查看详细Cookie状态"):
                        for channel_name, status in cookie_status.items():
                            status_icon = "✅" if status == 'valid' else "❌"
                            status_text = "有效" if status == 'valid' else "失效"
                            status_color = "green" if status == 'valid' else "red"
                            
                            st.markdown(f"{status_icon} **{channel_name}**: <span style='color: {status_color};'>{status_text}</span>", unsafe_allow_html=True)
                            
                            if status == 'expired':
                                st.warning(f"{channel_name} 的Cookie已失效，需要重新登录")
                            
                            st.write("---")
                    
                    # 如果有失效的Cookie，显示提醒
                    if expired_count > 0:
                        st.error(f"🚨 发现 {expired_count} 个频道的Cookie已失效！")
                        st.info("**建议操作:**")
                        st.write("1. 重新登录相关平台账号")
                        st.write("2. 更新Cookie配置")
                        st.write("3. 检查账号权限是否正常")
                else:
                    st.warning("无法获取Cookie状态信息")
                    
            except Exception as e:
                st.error(f"Cookie状态检查失败: {str(e)}")
                st.exception(e)


visualize_publish_calendar()