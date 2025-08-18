import sys
import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
from datetime import datetime, timedelta
import calendar

# 添加正确的路径
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # 如果__file__不可用，使用当前工作目录
    current_dir = os.getcwd()
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入依赖模块
try:
    from language_manager import init_language, get_text
except ImportError:
    # 如果模块不存在，创建简单的替代函数
    def init_language():
        return "zh"
    
    def get_text(key, lang="zh"):
        return key

try:
    from path_manager import get_json_data_dir
except ImportError:
    # 如果模块不存在，创建简单的替代函数
    def get_json_data_dir():
        return os.path.join(os.getcwd(), "workspace", "data")

try:
    from utils.calendar_visualizer import CalendarVisualizer
except ImportError:
    # 如果模块不存在，创建一个简单的替代类
    class CalendarVisualizer:
        def __init__(self, records, selected_channels, start_date, end_date):
            self.records = records
            self.selected_channels = selected_channels
            self.start_date = start_date
            self.end_date = end_date
        
        def create_heatmap_calendar(self):
            return None
        
        def create_monthly_calendar(self, year, month):
            return None
        
        def create_channel_timeline(self):
            return None
        
        def create_publish_pattern_analysis(self):
            return None

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

# CSV数据文件路径
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 
                        "workspace", "data", "publish_history.csv")

def load_csv_data():
    """从CSV文件加载数据"""
    try:
        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH, encoding='utf-8')
            
            # 数据预处理
            if '发表时间' in df.columns:
                try:
                    df['发表时间'] = pd.to_datetime(df['发表时间'], errors='coerce')
                    df['publish_date'] = df['发表时间'].dt.strftime('%Y-%m-%d')
                    df['publish_date'] = df['publish_date'].fillna('')
                except Exception as e:
                    st.warning(f"日期转换警告: {e}")
                    # 修复：确保publish_date列存在且为Series类型
                    if 'publish_date' in df.columns:
                        df['publish_date'] = df['publish_date'].fillna('')
                    else:
                        df['publish_date'] = ''
            else:
                if 'publish_date' in df.columns:
                    df['publish_date'] = df['publish_date'].fillna('').astype(str)
                else:
                    df['publish_date'] = ''
            
            # 过滤掉没有有效日期的记录
            df = df[df['publish_date'] != '']
            df = df[df['publish_date'] != 'nan']
            
            if 'publish_time' not in df.columns:
                df['publish_time'] = '12:00'
            
            # 重命名列以匹配原有结构
            df = df.rename(columns={
                '内容标题': 'title',
                '总阅读人数': 'views',
                '总阅读次数': 'total_views',
                '总分享人数': 'shares',
                '总分享次数': 'total_shares',
                '阅读后关注人数': 'followers_after_read',
                '送达人数': 'delivered_count',
                '公众号消息阅读次数': 'official_account_reads',
                '送达阅读率': 'delivery_read_rate',
                '首次分享次数': 'first_share_count',
                '分享产生阅读次数': 'share_generated_reads',
                '首次分享率': 'first_share_rate',
                '每次分享带来阅读次数': 'reads_per_share',
                '阅读完成率': 'read_completion_rate',
                '内容url': 'url',
                '账号名称': 'channel_name'
            })
            
            # 确保数值类型正确
            numeric_columns = [
                'views', 'total_views', 'shares', 'total_shares', 'followers_after_read',
                'delivered_count', 'official_account_reads', 'delivery_read_rate',
                'first_share_count', 'share_generated_reads', 'first_share_rate',
                'reads_per_share', 'read_completion_rate'
            ]
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # 添加缺失的列
            if 'likes' not in df.columns:
                df['likes'] = 0
            if 'comments' not in df.columns:
                df['comments'] = 0
            if 'status' not in df.columns:
                df['status'] = 'published'
            else:
                df['status'] = df['status'].fillna('published')
            
            if 'title' not in df.columns:
                df['title'] = '无标题'
            else:
                df['title'] = df['title'].fillna('无标题')
            
            if 'url' not in df.columns:
                df['url'] = ''
            else:
                df['url'] = df['url'].fillna('')
            
            # 生成ID
            if 'id' not in df.columns:
                df['id'] = range(1, len(df) + 1)
            else:
                df['id'] = pd.to_numeric(df['id'], errors='coerce').fillna(0).astype(int)
                if (df['id'] == 0).any():
                    df['id'] = range(1, len(df) + 1)
            
            # 确保channel_name字段存在
            if 'channel_name' not in df.columns:
                df['channel_name'] = 'AGI观察室'
            else:
                df['channel_name'] = df['channel_name'].fillna('AGI观察室')
            
            return df.to_dict('records')
        else:
            st.warning(f"CSV文件不存在: {CSV_PATH}")
            return []
    except Exception as e:
        st.error(f"读取CSV文件时出错: {str(e)}")
        return []

def create_engagement_analysis(records):
    """创建用户参与度分析图表"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    
    # 计算参与度指标
    df['engagement_rate'] = (df['shares'] + df['followers_after_read']) / df['views'].replace(0, 1) * 100
    df['share_efficiency'] = df['share_generated_reads'] / df['total_shares'].replace(0, 1)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("阅读完成率分布", "送达阅读率分布", "分享效率", "参与度分析"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 阅读完成率分布
    fig.add_trace(
        go.Histogram(x=df['read_completion_rate'], name="阅读完成率", nbinsx=20),
        row=1, col=1
    )
    
    # 送达阅读率分布
    fig.add_trace(
        go.Histogram(x=df['delivery_read_rate'], name="送达阅读率", nbinsx=20),
        row=1, col=2
    )
    
    # 分享效率散点图
    fig.add_trace(
        go.Scatter(x=df['total_shares'], y=df['share_efficiency'], 
                   mode='markers', name="分享效率"),
        row=2, col=1
    )
    
    # 参与度分析
    fig.add_trace(
        go.Scatter(x=df['views'], y=df['engagement_rate'], 
                   mode='markers', name="参与度"),
        row=2, col=2
    )
    
    fig.update_layout(height=600, title_text="用户参与度分析")
    return fig

def create_channel_performance_dashboard(records):
    """创建频道表现仪表板"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    
    # 按频道聚合数据
    channel_stats = df.groupby('channel_name').agg({
        'views': ['mean', 'sum', 'count'],
        'shares': ['mean', 'sum'],
        'read_completion_rate': 'mean',
        'delivery_read_rate': 'mean',
        'share_generated_reads': 'sum',
        'followers_after_read': 'sum'
    }).round(2)
    
    # 重命名列
    channel_stats.columns = [
        '平均阅读人数', '总阅读人数', '文章数量',
        '平均分享人数', '总分享人数',
        '平均阅读完成率', '平均送达阅读率',
        '分享产生阅读总数', '阅读后关注总数'
    ]
    
    # 创建仪表板图表
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("各频道文章数量", "各频道平均阅读人数", "各频道平均阅读完成率", "各频道分享产生阅读数"),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # 文章数量
    fig.add_trace(
        go.Bar(x=channel_stats.index, y=channel_stats['文章数量'], name="文章数量"),
        row=1, col=1
    )
    
    # 平均阅读人数
    fig.add_trace(
        go.Bar(x=channel_stats.index, y=channel_stats['平均阅读人数'], name="平均阅读人数"),
        row=1, col=2
    )
    
    # 平均阅读完成率
    fig.add_trace(
        go.Bar(x=channel_stats.index, y=channel_stats['平均阅读完成率'], name="平均阅读完成率"),
        row=2, col=1
    )
    
    # 分享产生阅读数
    fig.add_trace(
        go.Bar(x=channel_stats.index, y=channel_stats['分享产生阅读总数'], name="分享产生阅读数"),
        row=2, col=2
    )
    
    fig.update_layout(height=600, title_text="频道表现仪表板")
    return fig, channel_stats

def create_trend_analysis(records):
    """创建趋势分析图表"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    
    # 按日期聚合
    daily_stats = df.groupby('publish_date').agg({
        'views': 'sum',
        'shares': 'sum',
        'read_completion_rate': 'mean',
        'delivery_read_rate': 'mean',
        'share_generated_reads': 'sum',
        'followers_after_read': 'sum'
    }).reset_index()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("阅读人数趋势", "分享人数趋势", "阅读完成率趋势", "送达阅读率趋势"),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # 阅读人数趋势
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['views'], 
                   mode='lines+markers', name="阅读人数"),
        row=1, col=1
    )
    
    # 分享人数趋势
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['shares'], 
                   mode='lines+markers', name="分享人数"),
        row=1, col=2
    )
    
    # 阅读完成率趋势
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['read_completion_rate'], 
                   mode='lines+markers', name="阅读完成率"),
        row=2, col=1
    )
    
    # 送达阅读率趋势
    fig.add_trace(
        go.Scatter(x=daily_stats['publish_date'], y=daily_stats['delivery_read_rate'], 
                   mode='lines+markers', name="送达阅读率"),
        row=2, col=2
    )
    
    fig.update_layout(height=600, title_text="趋势分析")
    return fig

def create_heatmap_analysis(records):
    """创建热力图分析"""
    if not records:
        return None
    
    df = pd.DataFrame(records)
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    df['weekday'] = df['publish_date'].dt.day_name()
    df['hour'] = df['publish_date'].dt.hour
    
    # 按星期和小时创建热力图数据
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_cn = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    # 发布频率热力图
    publish_heatmap = df.groupby(['weekday', 'hour']).size().unstack(fill_value=0)
    publish_heatmap = publish_heatmap.reindex(weekday_order)
    publish_heatmap.index = weekday_cn
    
    fig = go.Figure(data=go.Heatmap(
        z=publish_heatmap.values,
        x=publish_heatmap.columns,
        y=publish_heatmap.index,
        colorscale='Viridis',
        text=publish_heatmap.values,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="发布时间热力图",
        xaxis_title="小时",
        yaxis_title="星期",
        height=400
    )
    
    return fig



def create_monthly_calendar(records, year, month, selected_channels):
    """创建月度日历视图"""
    if not records:
        return None
    
    # 过滤指定年月的数据
    filtered_data = []
    for record in records:
        if record.get("channel_name") in selected_channels:
            try:
                publish_date = datetime.strptime(record["publish_date"], "%Y-%m-%d")
                if publish_date.year == year and publish_date.month == month:
                    filtered_data.append(record)
            except (ValueError, TypeError):
                continue
    
    if not filtered_data:
        return None
    
    # 创建日历数据
    df = pd.DataFrame(filtered_data)
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    
    # 按日期分组统计
    daily_stats = df.groupby('publish_date').agg({
        'views': 'sum',
        'shares': 'sum',
        'title': lambda x: list(x)
    }).reset_index()
    
    # 创建日历HTML
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # 使用Streamlit的HTML组件
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto;">
        <h2 style="text-align: center; color: #333;">{year}年{month}月发布日历</h2>
        <table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
            <thead>
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f5f5f5;">周一</th>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f5f5f5;">周二</th>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f5f5f5;">周三</th>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f5f5f5;">周四</th>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f5f5f5;">周五</th>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f5f5f5;">周六</th>
                    <th style="border: 1px solid #ddd; padding: 8px; background-color: #f5f5f5;">周日</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for week in cal:
        html_content += "<tr>"
        for day in week:
            if day == 0:
                html_content += '<td style="border: 1px solid #ddd; padding: 8px; background-color: #f9f9f9;">&nbsp;</td>'
            else:
                # 查找当天的发布记录
                day_date = datetime(year, month, day)
                day_records = daily_stats[daily_stats['publish_date'].dt.date == day_date.date()]
                
                if not day_records.empty:
                    # 有发布记录
                    total_views = day_records['views'].sum()
                    total_shares = day_records['shares'].sum()
                    article_count = len(day_records)
                    
                    html_content += f"""
                    <td style="border: 1px solid #ddd; padding: 8px; background-color: #e8f5e8; position: relative;">
                        <div style="font-weight: bold; color: #2d5a2d;">{day}</div>
                        <div style="font-size: 12px; color: #666;">
                            📝 {article_count}篇<br>
                            👀 {total_views:,}<br>
                            📤 {total_shares:,}
                        </div>
                    </td>
                    """
                else:
                    # 无发布记录
                    html_content += f'<td style="border: 1px solid #ddd; padding: 8px;">{day}</td>'
        html_content += "</tr>"
    
    html_content += """
            </tbody>
        </table>
    </div>
    """
    
    return html_content

def create_timeline_view(records, selected_channels):
    """创建时间线视图"""
    if not records:
        return None
    
    # 过滤数据
    filtered_data = []
    for record in records:
        if record.get("channel_name") in selected_channels:
            filtered_data.append(record)
    
    if not filtered_data:
        return None
    
    df = pd.DataFrame(filtered_data)
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    df = df.sort_values('publish_date')
    
    # 创建时间线图表
    fig = go.Figure()
    
    # 为每个频道创建不同的颜色
    channels = df['channel_name'].unique()
    colors = px.colors.qualitative.Set3[:len(channels)]
    
    for i, channel in enumerate(channels):
        channel_data = df[df['channel_name'] == channel]
        
        fig.add_trace(go.Scatter(
            x=channel_data['publish_date'],
            y=channel_data['views'],
            mode='markers+lines',
            name=channel,
            marker=dict(size=8, color=colors[i]),
            hovertemplate='<b>%{text}</b><br>' +
                         '日期: %{x}<br>' +
                         '阅读人数: %{y:,}<br>' +
                         '分享人数: %{customdata}<br>' +
                         '<extra></extra>',
            text=channel_data['title'],
            customdata=channel_data['shares']
        ))
    
    fig.update_layout(
        title="发布时间线",
        xaxis_title="日期",
        yaxis_title="阅读人数",
        height=500,
        hovermode='closest'
    )
    
    return fig

st.set_page_config(page_title="频道发布历史", layout="wide")
st.title("📊 频道发布历史 - 数据可视化分析")

# 添加刷新按钮
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🔄 刷新数据", help="从CSV文件重新加载最新数据"):
        st.rerun()
with col2:
    # 显示数据文件信息
    if os.path.exists(CSV_PATH):
        file_size = os.path.getsize(CSV_PATH)
        file_time = datetime.fromtimestamp(os.path.getmtime(CSV_PATH))
        st.info(f"📁 数据文件: {file_size:,} 字节 | 更新时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.warning("⚠️ 数据文件不存在")
with col3:
    # 显示数据统计
    all_records_temp = load_csv_data()
    st.metric("📊 总记录数", len(all_records_temp))

def get_all_records():
    """获取所有发布记录"""
    return load_csv_data()

# 加载数据
all_records = get_all_records()

# 获取所有频道名称
all_channels = []
if all_records:
    for record in all_records:
        if "channel_name" in record and record["channel_name"]:
            all_channels.append(record["channel_name"])
    all_channels = list(set(all_channels))

# 侧边栏过滤器
with st.sidebar:
    st.subheader("🔍 频道筛选")
    selected_channels = st.multiselect(
        "选择频道",
        all_channels,
        default=all_channels
    )
    
    st.subheader("📅 日期范围")
    # 获取数据中的日期范围
    if all_records:
        dates = []
        for record in all_records:
            if "publish_date" in record and record["publish_date"]:
                try:
                    if isinstance(record["publish_date"], str) and record["publish_date"].strip():
                        date_obj = datetime.strptime(record["publish_date"], "%Y-%m-%d")
                        dates.append(date_obj)
                except (ValueError, TypeError):
                    continue
        
        if dates:
            min_date = min(dates).date()
            max_date = max(dates).date()
        else:
            min_date = datetime.now().date() - timedelta(days=30)
            max_date = datetime.now().date()
    else:
        min_date = datetime.now().date() - timedelta(days=30)
        max_date = datetime.now().date()
    
    start_date = st.date_input("开始日期", min_date)
    end_date = st.date_input("结束日期", max_date)

# 过滤数据
filtered_records = []
for record in all_records:
    if ("channel_name" in record and record["channel_name"] in selected_channels and
        "publish_date" in record and record["publish_date"]):
        try:
            publish_date = datetime.strptime(record["publish_date"], "%Y-%m-%d").date()
            if start_date <= publish_date <= end_date:
                filtered_records.append(record)
        except (ValueError, TypeError):
            continue

# 创建标签页
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 概览仪表板", 
    "📈 趋势分析", 
    "🎯 参与度分析",
    "📅 时间分析",
    "📅 发布日历",
    "📋 详细记录",
    "🔍 高级分析"
])

with tab1:
    st.subheader("📊 概览仪表板")
    
    if filtered_records:
        # 计算总体统计
        total_published = len([r for r in filtered_records if r["status"] == "published"])
        total_views = sum(r.get("views", 0) for r in filtered_records)
        total_shares = sum(r.get("shares", 0) for r in filtered_records)
        avg_read_completion = np.mean([r.get("read_completion_rate", 0) for r in filtered_records])
        avg_delivery_read_rate = np.mean([r.get("delivery_read_rate", 0) for r in filtered_records])
        
        # 显示统计卡片
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 总发布数", total_published)
        with col2:
            st.metric("👀 总阅读人数", f"{total_views:,}")
        with col3:
            st.metric("📤 总分享人数", f"{total_shares:,}")
        with col4:
            st.metric("📊 平均阅读完成率", f"{avg_read_completion:.1f}%")
        
        # 频道表现仪表板
        dashboard_fig, channel_stats = create_channel_performance_dashboard(filtered_records)
        if dashboard_fig:
            st.plotly_chart(dashboard_fig, use_container_width=True)
        
        # 显示频道统计表格
        if channel_stats is not None:
            st.subheader("📊 频道详细统计")
            st.dataframe(channel_stats, use_container_width=True)
        
        # 热门文章
        st.subheader("🔥 热门文章 TOP 10")
        top_articles = sorted(filtered_records, key=lambda x: x.get("views", 0), reverse=True)[:10]
        
        for i, article in enumerate(top_articles, 1):
            with st.expander(f"#{i} {article.get('title', '无标题')} ({article.get('channel_name', '未知频道')})"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"**阅读人数:** {article.get('views', 0):,}")
                with col2:
                    st.write(f"**分享人数:** {article.get('shares', 0):,}")
                with col3:
                    st.write(f"**阅读完成率:** {article.get('read_completion_rate', 0):.1f}%")
                with col4:
                    st.write(f"**发布日期:** {article.get('publish_date', '')}")
                
                if article.get('url'):
                    st.write(f"**链接:** {article['url']}")
    else:
        st.info("暂无数据")

with tab2:
    st.subheader("📈 趋势分析")
    
    if filtered_records:
        # 趋势分析图表
        trend_fig = create_trend_analysis(filtered_records)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
        
        # 月度统计
        st.subheader("📅 月度统计")
        df_monthly = pd.DataFrame(filtered_records)
        df_monthly['publish_date'] = pd.to_datetime(df_monthly['publish_date'])
        df_monthly['month'] = df_monthly['publish_date'].dt.to_period('M')
        
        monthly_stats = df_monthly.groupby('month').agg({
            'views': 'sum',
            'shares': 'sum',
            'read_completion_rate': 'mean',
            'delivery_read_rate': 'mean'
        }).reset_index()
        
        monthly_stats['month'] = monthly_stats['month'].astype(str)
        
        fig_monthly = make_subplots(
            rows=1, cols=2,
            subplot_titles=("月度阅读人数", "月度分享人数"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig_monthly.add_trace(
            go.Bar(x=monthly_stats['month'], y=monthly_stats['views'], name="阅读人数"),
            row=1, col=1
        )
        
        fig_monthly.add_trace(
            go.Bar(x=monthly_stats['month'], y=monthly_stats['shares'], name="分享人数"),
            row=1, col=2
        )
        
        fig_monthly.update_layout(height=400, title_text="月度趋势")
        st.plotly_chart(fig_monthly, use_container_width=True)
        
    else:
        st.info("暂无数据")

with tab3:
    st.subheader("🎯 用户参与度分析")
    
    if filtered_records:
        # 参与度分析图表
        engagement_fig = create_engagement_analysis(filtered_records)
        if engagement_fig:
            st.plotly_chart(engagement_fig, use_container_width=True)
        
        # 分享效率分析
        st.subheader("📤 分享效率分析")
        df_share = pd.DataFrame(filtered_records)
        
        # 计算分享相关指标
        df_share['share_efficiency'] = df_share['share_generated_reads'] / df_share['total_shares'].replace(0, 1)
        df_share['share_engagement'] = df_share['shares'] / df_share['views'].replace(0, 1) * 100
        
        fig_share = make_subplots(
            rows=1, cols=2,
            subplot_titles=("分享效率分布", "分享参与度分布"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig_share.add_trace(
            go.Histogram(x=df_share['share_efficiency'], name="分享效率", nbinsx=20),
            row=1, col=1
        )
        
        fig_share.add_trace(
            go.Histogram(x=df_share['share_engagement'], name="分享参与度", nbinsx=20),
            row=1, col=2
        )
        
        fig_share.update_layout(height=400, title_text="分享效率分析")
        st.plotly_chart(fig_share, use_container_width=True)
        
    else:
        st.info("暂无数据")

with tab4:
    st.subheader("📅 时间分析")
    
    if filtered_records:
        # 发布时间热力图
        heatmap_fig = create_heatmap_analysis(filtered_records)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        
        # 星期发布频率
        st.subheader("📊 星期发布频率")
        df_weekday = pd.DataFrame(filtered_records)
        df_weekday['publish_date'] = pd.to_datetime(df_weekday['publish_date'])
        df_weekday['weekday'] = df_weekday['publish_date'].dt.day_name()
        
        weekday_counts = df_weekday['weekday'].value_counts()
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_cn = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        weekday_counts = weekday_counts.reindex(weekday_order)
        weekday_counts.index = weekday_cn
        
        fig_weekday = px.bar(
            x=weekday_counts.index, 
            y=weekday_counts.values,
            title="各星期发布文章数量",
            labels={'x': '星期', 'y': '文章数量'}
        )
        st.plotly_chart(fig_weekday, use_container_width=True)
        
    else:
        st.info("暂无数据")

with tab5:
    st.subheader("📅 发布日历")
    
    if filtered_records:
        # 选择日历视图类型
        calendar_type = st.selectbox(
            "选择日历视图类型",
            ["月度日历", "时间线视图"],
            index=0
        )
        
        if calendar_type == "月度日历":
            st.subheader("📅 月度发布日历")
            
            # 获取数据中的年份范围
            if filtered_records:
                dates = []
                for record in filtered_records:
                    if "publish_date" in record and record["publish_date"]:
                        try:
                            if isinstance(record["publish_date"], str) and record["publish_date"].strip():
                                date_obj = datetime.strptime(record["publish_date"], "%Y-%m-%d")
                                dates.append(date_obj)
                        except (ValueError, TypeError):
                            continue
                
                if dates:
                    years = sorted(list(set(date.year for date in dates)))
                else:
                    years = [datetime.now().year]
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
                
                calendar_html = create_monthly_calendar(filtered_records, year, month, selected_channels)
                if calendar_html:
                    # 使用Streamlit的HTML组件显示日历
                    st.components.v1.html(calendar_html, height=600)
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
            st.subheader("📈 发布时间线")
            timeline_fig = create_timeline_view(filtered_records, selected_channels)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)
            else:
                st.info("暂无数据生成时间线")
    else:
        st.info("暂无数据")

with tab6:
    st.subheader("📋 详细记录")
    
    if filtered_records:
        # 创建数据表格
        df_records = pd.DataFrame(filtered_records)
        
        # 选择显示的列
        display_columns = [
            "id", "channel_name", "title", "publish_date", 
            "views", "shares", "read_completion_rate", "delivery_read_rate",
            "share_generated_reads", "followers_after_read"
        ]
        
        # 确保所有列都存在
        available_columns = [col for col in display_columns if col in df_records.columns]
        
        # 显示数据表格
        st.dataframe(
            df_records[available_columns],
            use_container_width=True
        )
        
        # 导出功能
        if st.button("📥 导出数据"):
            csv = df_records.to_csv(index=False)
            st.download_button(
                label="下载CSV文件",
                data=csv,
                file_name=f"channel_publish_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("暂无数据")

with tab7:
    st.subheader("🔍 高级分析")
    
    if filtered_records:
        # 相关性分析
        st.subheader("📊 指标相关性分析")
        df_corr = pd.DataFrame(filtered_records)
        
        # 选择数值列进行相关性分析
        numeric_columns = [
            'views', 'shares', 'read_completion_rate', 'delivery_read_rate',
            'share_generated_reads', 'followers_after_read', 'total_views', 'total_shares'
        ]
        
        available_numeric = [col for col in numeric_columns if col in df_corr.columns]
        
        if len(available_numeric) > 1:
            correlation_matrix = df_corr[available_numeric].corr()
            
            fig_corr = px.imshow(
                correlation_matrix,
                title="指标相关性热力图",
                color_continuous_scale='RdBu',
                aspect="auto"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        
        # 分布分析
        st.subheader("📈 指标分布分析")
        if filtered_records:
            df_dist = pd.DataFrame(filtered_records)
            
            # 选择要分析的指标
            metrics_to_analyze = ['views', 'shares', 'read_completion_rate', 'delivery_read_rate']
            available_metrics = [m for m in metrics_to_analyze if m in df_dist.columns]
            
            if available_metrics:
                fig_dist = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=available_metrics,
                    specs=[[{"secondary_y": False}, {"secondary_y": False}],
                           [{"secondary_y": False}, {"secondary_y": False}]]
                )
                
                for i, metric in enumerate(available_metrics):
                    row = (i // 2) + 1
                    col = (i % 2) + 1
                    
                    fig_dist.add_trace(
                        go.Histogram(x=df_dist[metric], name=metric, nbinsx=20),
                        row=row, col=col
                    )
                
                fig_dist.update_layout(height=500, title_text="指标分布分析")
                st.plotly_chart(fig_dist, use_container_width=True)
        
        # 异常值检测
        st.subheader("🔍 异常值检测")
        if filtered_records:
            df_outlier = pd.DataFrame(filtered_records)
            
            # 检测阅读人数的异常值
            if 'views' in df_outlier.columns:
                Q1 = df_outlier['views'].quantile(0.25)
                Q3 = df_outlier['views'].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df_outlier[(df_outlier['views'] < lower_bound) | (df_outlier['views'] > upper_bound)]
                
                if not outliers.empty:
                    st.warning(f"发现 {len(outliers)} 个阅读人数异常值")
                    st.dataframe(outliers[['title', 'channel_name', 'views', 'publish_date']], use_container_width=True)
                else:
                    st.success("未发现阅读人数异常值")
        
    else:
        st.info("暂无数据") 