import sys
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from language_manager import init_language, get_text
from path_manager import get_json_data_dir
from datetime import datetime, timedelta
import calendar

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.calendar_visualizer import CalendarVisualizer

T = {
    "en": {
        "page_title": "Channel Publish History",
        "overview": "Publish Overview",
        "calendar_view": "Calendar View",
        "statistics": "Statistics",
        "detailed_records": "Detailed Records",
        "channel_filter": "Select Channel",
        "date_range": "Date Range",
        "all_channels": "All Channels",
        "total_published": "Total Published",
        "total_views": "Total Views",
        "total_likes": "Total Likes",
        "total_comments": "Total Comments",
        "total_shares": "Total Shares",
        "publish_frequency": "Publish Frequency",
        "performance_trend": "Performance Trend",
        "top_articles": "Top Articles",
        "article_id": "Article ID",
        "title": "Title",
        "publish_date": "Publish Date",
        "publish_time": "Publish Time",
        "status": "Status",
        "views": "Views",
        "likes": "Likes",
        "comments": "Comments",
        "shares": "Shares",
        "url": "URL",
        "tags": "Tags",
        "published": "Published",
        "draft": "Draft",
        "scheduled": "Scheduled",
        "no_data": "No Data",
        "export_data": "Export Data",
        "import_data": "Import Data",
        "add_record": "Add Record",
        "edit_record": "Edit Record",
        "delete_record": "Delete Record",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "confirm_delete": "Confirm Delete",
        "success": "Operation Successful",
        "error": "Operation Failed"
    }
}



st.set_page_config(page_title=get_text("page_title"), layout="wide")
st.title(get_text("page_title"))

# 数据文件路径
HISTORY_PATH = get_json_data_dir() / "channel_publish_history.json"

def load_publish_history():
    """加载发布历史数据"""
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_publish_history(data):
    """保存发布历史数据"""
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_records(history_data):
    """获取所有发布记录"""
    all_records = []
    for channel in history_data:
        for record in channel["publish_records"]:
            record["channel_name"] = channel["channel_name"]
            all_records.append(record)
    return all_records

def create_calendar_data(records, selected_channels, start_date, end_date):
    """创建日历数据"""
    calendar_data = []
    for record in records:
        if record["channel_name"] in selected_channels:
            publish_date = datetime.strptime(record["publish_date"], "%Y-%m-%d")
            if start_date <= publish_date <= end_date:
                calendar_data.append({
                    "date": record["publish_date"],
                    "channel": record["channel_name"],
                    "title": record["title"],
                    "status": record["status"],
                    "views": record["views"],
                    "likes": record["likes"]
                })
    return calendar_data

def create_performance_chart(records, selected_channels):
    """创建表现趋势图表"""
    if not records:
        return None
    
    # 按日期分组统计
    df = pd.DataFrame(records)
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    df = df[df['channel_name'].isin(selected_channels)]
    
    if df.empty:
        return None
    
    daily_stats = df.groupby('publish_date').agg({
        'views': 'sum',
        'likes': 'sum',
        'comments': 'sum',
        'shares': 'sum'
    }).reset_index()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(get_text("views"), get_text("likes"), get_text("comments"), get_text("shares")),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['views'], 
                   mode='lines+markers', name=get_text("views")),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['likes'], 
                   mode='lines+markers', name=get_text("likes")),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['comments'], 
                   mode='lines+markers', name=get_text("comments")),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['shares'], 
                   mode='lines+markers', name=get_text("shares")),
        row=2, col=2
    )
    
    fig.update_layout(height=600, title_text=get_text("performance_trend"))
    return fig

def create_channel_comparison(records, selected_channels):
    """创建频道对比图表"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    df = df[df['channel_name'].isin(selected_channels)]
    
    if df.empty:
        return None
    
    channel_stats = df.groupby('channel_name').agg({
        'views': 'sum',
        'likes': 'sum',
        'comments': 'sum',
        'shares': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=channel_stats['channel_name'],
        y=channel_stats['views'],
        name=get_text("views"),
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        x=channel_stats['channel_name'],
        y=channel_stats['likes'],
        name=get_text("likes"),
        marker_color='lightgreen'
    ))
    
    fig.update_layout(
        title=get_text("channel_filter") + " - " + get_text("statistics"),
        barmode='group',
        height=400
    )
    
    return fig

# 加载数据
history_data = load_publish_history()
all_records = get_all_records(history_data)

# 获取所有频道名称
all_channels = [channel["channel_name"] for channel in history_data]

# 侧边栏过滤器
with st.sidebar:
    st.subheader("🔍 " + get_text("channel_filter"))
    selected_channels = st.multiselect(
        get_text("channel_filter"),
        all_channels,
        default=all_channels
    )
    
    st.subheader("📅 " + get_text("date_range"))
    # 获取数据中的日期范围
    if all_records:
        dates = [datetime.strptime(record["publish_date"], "%Y-%m-%d") for record in all_records]
        min_date = min(dates).date()
        max_date = max(dates).date()
    else:
        min_date = datetime.now().date() - timedelta(days=30)
        max_date = datetime.now().date()
    
    start_date = st.date_input("开始日期", min_date)
    end_date = st.date_input("结束日期", max_date)

# 过滤数据
filtered_records = [record for record in all_records 
                   if record["channel_name"] in selected_channels and
                   start_date <= datetime.strptime(record["publish_date"], "%Y-%m-%d").date() <= end_date]

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 " + get_text("overview"), 
    "📅 " + get_text("calendar_view"), 
    "📈 " + get_text("statistics"), 
    "📋 " + get_text("detailed_records"),
    "🎯 " + "高级分析"
])

with tab1:
    st.subheader(get_text("overview"))
    
    if filtered_records:
        # 计算总体统计
        total_published = len([r for r in filtered_records if r["status"] == "published"])
        total_views = sum(r["views"] for r in filtered_records)
        total_likes = sum(r["likes"] for r in filtered_records)
        total_comments = sum(r["comments"] for r in filtered_records)
        total_shares = sum(r["shares"] for r in filtered_records)
        
        # 显示统计卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(get_text("total_published"), total_published)
        with col2:
            st.metric(get_text("total_views"), f"{total_views:,}")
        with col3:
            st.metric(get_text("total_likes"), f"{total_likes:,}")
        with col4:
            st.metric(get_text("total_shares"), f"{total_shares:,}")
        
        # 热门文章
        st.subheader(get_text("top_articles"))
        top_articles = sorted(filtered_records, key=lambda x: x["views"], reverse=True)[:5]
        
        for i, article in enumerate(top_articles, 1):
            with st.expander(f"#{i} {article['title']} ({article['channel_name']})"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**{T['en']['views']}:** {article['views']:,}")
                with col2:
                    st.write(f"**{T['en']['likes']}:** {article['likes']:,}")
                with col3:
                    st.write(f"**{T['en']['comments']}:** {article['comments']:,}")
                with col4:
                    st.write(f"**{T['en']['shares']}:** {article['shares']:,}")
                st.write(f"**{T['en']['publish_date']}:** {article['publish_date']}")
                if article['url']:
                    st.write(f"**{T['en']['url']}:** {article['url']}")
    else:
        st.info(get_text("no_data"))

with tab2:
    st.subheader(get_text("calendar_view"))
    
    if filtered_records:
        # 创建日历可视化器
        calendar_viz = CalendarVisualizer(filtered_records, selected_channels, start_date, end_date)
        
        # 选择日历视图类型
        calendar_type = st.selectbox(
            "选择日历视图类型",
            ["热力图日历", "月度日历", "时间线视图"],
            index=0
        )
        
        if calendar_type == "热力图日历":
            heatmap_fig = calendar_viz.create_heatmap_calendar()
            if heatmap_fig:
                st.plotly_chart(heatmap_fig, use_container_width=True)
            else:
                st.info("暂无数据生成热力图")
        
        elif calendar_type == "月度日历":
            # 获取数据中的年份范围
            if filtered_records:
                dates = [datetime.strptime(record["publish_date"], "%Y-%m-%d") for record in filtered_records]
                years = sorted(list(set(date.year for date in dates)))
                current_year = datetime.now().year
                
                # 如果数据中没有当前年份，添加当前年份
                if current_year not in years:
                    years.append(current_year)
                    years.sort()
                
                # 默认选择当前年份
                default_year_index = years.index(current_year) if current_year in years else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    year = st.selectbox("选择年份", years, index=default_year_index)
                with col2:
                    month = st.selectbox("选择月份", range(1, 13), index=datetime.now().month-1)
                
                calendar_html = calendar_viz.create_monthly_calendar(year, month)
                if calendar_html:
                    st.markdown(calendar_html, unsafe_allow_html=True)
                else:
                    st.info("该月份暂无发布记录")
            else:
                # 没有数据时，显示当前年月
                col1, col2 = st.columns(2)
                with col1:
                    year = st.selectbox("选择年份", [datetime.now().year], index=0)
                with col2:
                    month = st.selectbox("选择月份", range(1, 13), index=datetime.now().month-1)
                
                st.info("暂无数据，请先添加发布记录")
        
        elif calendar_type == "时间线视图":
            timeline_fig = calendar_viz.create_channel_timeline()
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)
            else:
                st.info("暂无数据生成时间线")
    else:
        st.info(get_text("no_data"))

with tab3:
    st.subheader(get_text("statistics"))
    
    if filtered_records:
        # 表现趋势图表
        performance_fig = create_performance_chart(filtered_records, selected_channels)
        if performance_fig:
            st.plotly_chart(performance_fig, use_container_width=True)
        
        # 频道对比图表
        comparison_fig = create_channel_comparison(filtered_records, selected_channels)
        if comparison_fig:
            st.plotly_chart(comparison_fig, use_container_width=True)
        
        # 发布频率分析
        st.subheader(get_text("publish_frequency"))
        df_freq = pd.DataFrame(filtered_records)
        df_freq['publish_date'] = pd.to_datetime(df_freq['publish_date'])
        
        # 按频道统计发布频率
        freq_stats = df_freq.groupby('channel_name').size().reset_index(name='count')
        freq_fig = px.bar(freq_stats, x='channel_name', y='count', 
                         title="各频道发布文章数量")
        st.plotly_chart(freq_fig, use_container_width=True)
        
    else:
        st.info(get_text("no_data"))

with tab4:
    st.subheader(get_text("detailed_records"))
    
    if filtered_records:
        # 创建数据表格
        df_records = pd.DataFrame(filtered_records)
        
        # 添加操作按钮
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("➕ " + get_text("add_record")):
                st.session_state["show_add_form"] = True
        
        # 显示数据表格
        st.dataframe(
            df_records[[
                "id", "channel_name", "title", "publish_date", 
                "publish_time", "status", "views", "likes", 
                "comments", "shares"
            ]],
            use_container_width=True
        )
        
        # 导出功能
        if st.button("📥 " + get_text("export_data")):
            csv = df_records.to_csv(index=False)
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name=f"channel_publish_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info(get_text("no_data"))

with tab5:
    st.subheader("🎯 高级分析")
    
    if filtered_records:
        calendar_viz = CalendarVisualizer(filtered_records, selected_channels, start_date, end_date)
        
        # 发布模式分析
        st.subheader("📊 发布模式分析")
        pattern_fig = calendar_viz.create_publish_pattern_analysis()
        if pattern_fig:
            st.plotly_chart(pattern_fig, use_container_width=True)
        
        # 频道表现对比
        st.subheader("📈 频道表现对比")
        if filtered_records:
            df_analysis = pd.DataFrame(filtered_records)
            
            # 计算每个频道的平均表现指标
            channel_performance = df_analysis.groupby('channel_name').agg({
                'views': ['mean', 'sum'],
                'likes': ['mean', 'sum'],
                'comments': ['mean', 'sum'],
                'shares': ['mean', 'sum']
            }).round(2)
            
            # 重命名列
            channel_performance.columns = [
                '平均浏览量', '总浏览量', '平均点赞', '总点赞',
                '平均评论', '总评论', '平均分享', '总分享'
            ]
            
            st.dataframe(channel_performance, use_container_width=True)
            
            # 创建雷达图
            fig_radar = go.Figure()
            
            for channel in df_analysis['channel_name'].unique():
                channel_data = df_analysis[df_analysis['channel_name'] == channel]
                avg_views = channel_data['views'].mean()
                avg_likes = channel_data['likes'].mean()
                avg_comments = channel_data['comments'].mean()
                avg_shares = channel_data['shares'].mean()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=[avg_views, avg_likes, avg_comments, avg_shares],
                    theta=['平均浏览量', '平均点赞', '平均评论', '平均分享'],
                    fill='toself',
                    name=channel
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(channel_performance['平均浏览量'].max(), 
                                     channel_performance['平均点赞'].max(),
                                     channel_performance['平均评论'].max(),
                                     channel_performance['平均分享'].max())]
                    )),
                showlegend=True,
                title="频道表现雷达图"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info(get_text("no_data"))

# 添加记录的表单
if st.session_state.get("show_add_form", False):
    with st.form("add_record_form"):
        st.subheader("➕ " + get_text("add_record"))
        
        col1, col2 = st.columns(2)
        with col1:
            channel_name = st.selectbox("频道名称", all_channels)
            article_id = st.text_input("文章ID")
            title = st.text_input("标题")
            publish_date = st.date_input("发布日期")
            publish_time = st.time_input("发布时间")
        
        with col2:
            status = st.selectbox("状态", ["published", "draft", "scheduled"])
            views = st.number_input("浏览量", min_value=0, value=0)
            likes = st.number_input("点赞数", min_value=0, value=0)
            comments = st.number_input("评论数", min_value=0, value=0)
            shares = st.number_input("分享数", min_value=0, value=0)
        
        url = st.text_input("链接")
        tags = st.text_input("标签（用逗号分隔）")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button(get_text("save")):
                # 添加新记录的逻辑
                new_record = {
                    "id": article_id,
                    "title": title,
                    "publish_date": publish_date.strftime("%Y-%m-%d"),
                    "publish_time": publish_time.strftime("%H:%M"),
                    "status": status,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "url": url,
                    "tags": [tag.strip() for tag in tags.split(",") if tag.strip()]
                }
                
                # 找到对应的频道并添加记录
                for channel in history_data:
                    if channel["channel_name"] == channel_name:
                        channel["publish_records"].append(new_record)
                        break
                
                save_publish_history(history_data)
                st.success(get_text("success"))
                st.session_state["show_add_form"] = False
                st.rerun()
        
        with col2:
            if st.form_submit_button(get_text("cancel")):
                st.session_state["show_add_form"] = False
                st.rerun() 