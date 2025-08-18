import pandas as pd
import os
import streamlit as st
import calendar
from datetime import datetime
import random


def load_csv_data():
    """从CSV文件加载数据"""
    try:
        # 方法1：直接从项目根目录加载
        csv_path = "workspace/data/publish_history.csv"
        
        if os.path.exists(csv_path):
            st.toast(f"成功找到数据文件: {csv_path}", icon="✅")
            df = pd.read_csv(csv_path, encoding='utf-8')
            
            # 检查必要的列是否存在
            if '发表时间' in df.columns:
                # 转换时间列
                df['发表时间'] = pd.to_datetime(df['发表时间'], errors='coerce')
                # 过滤掉无效的日期数据
                df = df.dropna(subset=['发表时间'])
                
                if not df.empty:
                    st.toast(f"成功加载 {len(df)} 条数据记录")
                    return df
                else:
                    st.warning("数据加载成功但所有日期数据都无效")
                    return pd.DataFrame()
            else:
                st.error(f"CSV文件缺少'发表时间'列，当前列名: {list(df.columns)}")
                return pd.DataFrame()
        
        # 方法2：尝试从app目录的上级目录加载
        csv_path2 = "../workspace/data/publish_history.csv"
        if os.path.exists(csv_path2):
            st.toast(f"成功找到数据文件: {csv_path2}")
            df = pd.read_csv(csv_path2, encoding='utf-8')
            
            if '发表时间' in df.columns:
                df['发表时间'] = pd.to_datetime(df['发表时间'], errors='coerce')
                df = df.dropna(subset=['发表时间'])
                
                if not df.empty:
                    st.toast(f"成功加载 {len(df)} 条数据记录")
                    return df
                else:
                    st.warning("数据加载成功但所有日期数据都无效")
                    return pd.DataFrame()
            else:
                st.error(f"CSV文件缺少'发表时间'列，当前列名: {list(df.columns)}")
                return pd.DataFrame()
        
        # 方法3：尝试从当前工作目录加载
        csv_path3 = os.path.join(os.getcwd(), "workspace", "data", "publish_history.csv")
        if os.path.exists(csv_path3):
            st.toast(f"成功找到数据文件: {csv_path3}")
            df = pd.read_csv(csv_path3, encoding='utf-8')
            
            if '发表时间' in df.columns:
                df['发表时间'] = pd.to_datetime(df['发表时间'], errors='coerce')
                df = df.dropna(subset=['发表时间'])
                
                if not df.empty:
                    st.toast(f"成功加载 {len(df)} 条数据记录")
                    return df
                else:
                    st.warning("数据加载成功但所有日期数据都无效")
                    return pd.DataFrame()
            else:
                st.error(f"CSV文件缺少'发表时间'列，当前列名: {list(df.columns)}")
                return pd.DataFrame()
        
        # 如果所有方法都失败，显示错误信息
        st.error("未找到数据文件，尝试了以下路径:")
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
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D7BDE2'
    ]
    
    account_colors = {}
    for i, account in enumerate(accounts):
        account_colors[account] = colors[i % len(colors)]
    
    return account_colors


def visualize_publish_calendar():
    df = load_csv_data()
    
    if df.empty:
        st.error("无法加载数据，请检查数据文件")
        return

    st.title("微信公众号文章发布日历")

    # 检查数据是否为空
    if df.empty:
        st.warning("没有可用的数据")
        return

    # 获取数据的年份和月份范围
    df['年份'] = df['发表时间'].dt.year
    df['月份'] = df['发表时间'].dt.month
    
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
    filtered_df = df[(df['发表时间'].dt.year == selected_year) & (df['发表时间'].dt.month == selected_month)]

    # 创建两列布局：左侧日历，右侧图例
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # 生成日历
        cal = calendar.monthcalendar(selected_year, selected_month)
        
        # 使用CSS样式优化日历布局
        st.markdown("""
        <style>
        /* 移除Streamlit所有可能的宽度限制 */
        .main .block-container,
        .main .block-container > div,
        .stMainBlockContainer,
        .block-container,
        .st-emotion-cache-1w723zb,
        .e4man114,
        [data-testid="stMainBlockContainer"] {
            max-width: none !important;
            width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
        
        /* 覆盖Streamlit的默认样式 */
        .stApp > div:first-child {
            max-width: none !important;
            width: 100% !important;
        }
        
        /* 确保主容器占满宽度 */
        .main {
            max-width: none !important;
            width: 100% !important;
        }
        
        /* 日历容器样式 */
        .calendar-container {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px 0;
            width: 100%;
            max-width: none !important;
        }
        
        /* 日历网格容器 */
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 1px;
            background-color: #e0e0e0;
            padding: 1px;
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* 日历单元格 */
        .calendar-cell {
            background-color: var(--background-color, #ffffff);
            padding: 12px 8px;
            min-height: 100px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            border: none;
            position: relative;
        }
        
        /* 暗黑主题适配 */
        @media (prefers-color-scheme: dark) {
            .calendar-cell {
                --background-color: #1e1e1e;
                --text-color: #ffffff;
                --border-color: #404040;
                --header-bg: #2d2d2d;
                --post-count-bg: #404040;
                --post-count-color: #e0e0e0;
            }
        }
        
        /* 亮色主题 */
        @media (prefers-color-scheme: light) {
            .calendar-cell {
                --background-color: #ffffff;
                --text-color: #2c3e50;
                --border-color: #e0e0e0;
                --header-bg: #f8f9fa;
                --post-count-bg: #ecf0f1;
                --post-count-color: #7f8c8d;
            }
        }
        
        /* 强制亮色主题样式（覆盖Streamlit主题） */
        .calendar-cell {
            background-color: #ffffff !important;
            color: #2c3e50 !important;
        }
        
        /* 自定义日历样式 */
        .calendar-date {
            font-size: 24px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 8px;
            font-family: 'Georgia', serif;
        }
        
        .calendar-post-count {
            font-size: 14px;
            font-weight: 600;
            color: #7f8c8d;
            margin-bottom: 10px;
            font-family: 'Segoe UI', sans-serif;
            background-color: #ecf0f1;
            padding: 4px 8px;
            border-radius: 12px;
            display: inline-block;
            border: 1px solid #d0d0d0;
        }
        
        .calendar-dots-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 4px;
            margin-top: 8px;
        }
        
        .calendar-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            border: 2px solid #ffffff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .calendar-header {
            font-size: 16px;
            font-weight: 600;
            color: #34495e;
            background-color: #f8f9fa;
            padding: 12px 8px;
            border-radius: 8px;
            margin-bottom: 8px;
            text-align: center;
            font-family: 'Segoe UI', sans-serif;
            border: 1px solid #e0e0e0;
        }
        
        .calendar-empty {
            color: #bdc3c7;
            font-style: italic;
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
        }
        
        /* 响应式设计 */
        @media (max-width: 1200px) {
            .calendar-cell {
                min-height: 90px;
                padding: 10px 6px;
            }
            .calendar-date {
                font-size: 22px;
            }
            .calendar-post-count {
                font-size: 13px;
                padding: 3px 6px;
            }
            .calendar-dot {
                width: 11px;
                height: 11px;
            }
        }
        
        @media (max-width: 768px) {
            .calendar-cell {
                min-height: 80px;
                padding: 8px 4px;
            }
            .calendar-date {
                font-size: 20px;
            }
            .calendar-post-count {
                font-size: 12px;
                padding: 2px 5px;
            }
            .calendar-dot {
                width: 10px;
                height: 10px;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 使用Streamlit原生组件创建日历
        st.write(f"### {selected_year}年{selected_month}月发布日历")
        
        # 创建表头
        header_cols = st.columns(7)
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i, day in enumerate(weekdays):
            with header_cols[i]:
                st.markdown(f'<div class="calendar-header">{day}</div>', unsafe_allow_html=True)
        
        # 使用CSS Grid创建日历
        calendar_html = '<div class="calendar-grid">'
        
        # 生成日历内容
        for week in cal:
            for day in week:
                if day == 0:
                    calendar_html += '<div class="calendar-cell calendar-empty"></div>'
                else:
                    daily_posts = filtered_df[filtered_df['发表时间'].dt.day == day]
                    if not daily_posts.empty:
                        # 获取账号统计
                        account_counts = daily_posts['账号名称'].value_counts()
                        account_colors = get_account_colors(account_counts.index.tolist())
                        
                        # 生成小圆点HTML
                        dots_html = '<div class="calendar-dots-container">'
                        for account in account_counts.index:
                            dots_html += f'<div class="calendar-dot" style="background-color: {account_colors[account]};" title="{account}"></div>'
                        dots_html += '</div>'
                        
                        # 创建日历日期单元格
                        calendar_html += f"""
                        <div class="calendar-cell">
                            <div class="calendar-date">{day}</div>
                            <div class="calendar-post-count">{daily_posts.shape[0]}篇</div>
                            {dots_html}
                        </div>
                        """
                    else:
                        calendar_html += f"""
                        <div class="calendar-cell">
                            <div class="calendar-date">{day}</div>
                        </div>
                        """
        
        calendar_html += '</div>'
        
        # 显示日历
        st.markdown(calendar_html, unsafe_allow_html=True)

    with col2:
        # 右侧图例
        st.write("### 图例说明")
        
        if not filtered_df.empty:
            # 获取所有账号
            accounts = filtered_df['账号名称'].unique()
            account_colors = get_account_colors(accounts)
            
            # 显示每个账号的颜色和文章数量
            for account in accounts:
                account_posts = filtered_df[filtered_df['账号名称'] == account]
                count = len(account_posts)
                
                # 创建图例项
                st.markdown(
                    f'<div style="display: flex; align-items: center; margin: 8px 0;">'
                    f'<div style="width: 16px; height: 16px; border-radius: 50%; '
                    f'background-color: {account_colors[account]}; margin-right: 8px;"></div>'
                    f'<span>{account} ({count}篇)</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # 显示统计信息
            st.write("---")
            st.write(f"**总计: {len(filtered_df)} 篇**")
            
            # 按账号统计
            account_stats = filtered_df['账号名称'].value_counts()
            st.write("**按账号统计:**")
            for account, count in account_stats.items():
                st.write(f"• {account}: {count}篇")
        else:
            st.info(f"{selected_year}年{selected_month}月没有发布记录")

    # 显示当月发布详情
    st.write("---")
    st.write("### 当月发布详情")
    if not filtered_df.empty:
        st.dataframe(filtered_df[['内容标题', '发表时间', '账号名称']])
    else:
        st.info(f"{selected_year}年{selected_month}月没有发布记录")

visualize_publish_calendar()