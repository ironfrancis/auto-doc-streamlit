import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CalendarVisualizer:
    """日历可视化工具类"""
    
    def __init__(self, records, selected_channels, start_date, end_date):
        self.records = records
        self.selected_channels = selected_channels
        self.start_date = start_date
        self.end_date = end_date
        
    def create_heatmap_calendar(self):
        """创建热力图日历"""
        if not self.records:
            return None
            
        # 创建日期范围
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        
        # 按日期统计发布数量
        df = pd.DataFrame(self.records)
        df['publish_date'] = pd.to_datetime(df['publish_date'])
        
        # 过滤选中的频道
        df = df[df['channel_name'].isin(self.selected_channels)]
        
        # 按日期分组统计
        daily_counts = df.groupby('publish_date').size().reset_index(name='count')
        daily_counts['publish_date'] = pd.to_datetime(daily_counts['publish_date'])
        
        # 创建完整的日期数据
        calendar_data = []
        for date in date_range:
            count = daily_counts[daily_counts['publish_date'] == date]['count'].iloc[0] if date in daily_counts['publish_date'].values else 0
            calendar_data.append({
                'date': date,
                'count': count,
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'weekday': date.weekday()
            })
        
        df_calendar = pd.DataFrame(calendar_data)
        
        # 计算周数
        total_weeks = (len(df_calendar) + 6) // 7
        
        # 创建热力图数据
        heatmap_data = []
        for week in range(total_weeks):
            week_data = []
            for day in range(7):
                idx = week * 7 + day
                if idx < len(df_calendar):
                    week_data.append(df_calendar.iloc[idx]['count'])
                else:
                    week_data.append(0)
            heatmap_data.append(week_data)
        
        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
            y=[f"第{i}周" for i in range(1, total_weeks + 1)],
            colorscale='Blues',
            showscale=True,
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="发布日历热力图",
            xaxis_title="星期",
            yaxis_title="周次",
            height=400
        )
        
        return fig
    
    def create_monthly_calendar(self, year, month):
        """创建月度日历视图"""
        # 获取该月的所有日期
        cal = calendar.monthcalendar(year, month)
        
        # 获取该月的发布记录
        month_records = [r for r in self.records 
                        if datetime.strptime(r['publish_date'], '%Y-%m-%d').year == year and
                        datetime.strptime(r['publish_date'], '%Y-%m-%d').month == month and
                        r['channel_name'] in self.selected_channels]
        
        # 按日期分组
        records_by_date = {}
        for record in month_records:
            date = record['publish_date']
            if date not in records_by_date:
                records_by_date[date] = []
            records_by_date[date].append(record)
        
        # 创建日历HTML
        month_name = calendar.month_name[month]
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 800px;">
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
            html += "<tr>"
            for day in week:
                if day == 0:
                    html += '<td style="border: 1px solid #ddd; padding: 8px; background-color: #f9f9f9;"></td>'
                else:
                    date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    if date_str in records_by_date:
                        records = records_by_date[date_str]
                        bg_color = "#e8f5e8" if any(r['status'] == 'published' for r in records) else "#fff3cd"
                        html += f'<td style="border: 1px solid #ddd; padding: 8px; background-color: {bg_color};">'
                        html += f'<div style="font-weight: bold; color: #333;">{day}</div>'
                        for record in records:
                            status_icon = "🟢" if record['status'] == 'published' else "🟡" if record['status'] == 'draft' else "🔵"
                            html += f'<div style="font-size: 12px; margin: 2px 0;">{status_icon} {record["channel_name"]}</div>'
                        html += '</td>'
                    else:
                        html += f'<td style="border: 1px solid #ddd; padding: 8px;"><div style="font-weight: bold; color: #333;">{day}</div></td>'
            html += "</tr>"
        
        html += """
                </tbody>
            </table>
            <div style="margin-top: 10px; font-size: 12px; color: #666;">
                <span>🟢 已发布</span> | <span>🟡 草稿</span> | <span>🔵 已排期</span>
            </div>
        </div>
        """
        
        return html
    
    def create_channel_timeline(self):
        """创建频道时间线"""
        if not self.records:
            return None
            
        df = pd.DataFrame(self.records)
        df['publish_date'] = pd.to_datetime(df['publish_date'])
        df = df[df['channel_name'].isin(self.selected_channels)]
        
        if df.empty:
            return None
        
        # 按频道和日期排序
        df = df.sort_values(['channel_name', 'publish_date'])
        
        # 创建时间线图表
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
        
        for i, channel in enumerate(df['channel_name'].unique()):
            channel_data = df[df['channel_name'] == channel]
            
            fig.add_trace(go.Scatter(
                x=channel_data['publish_date'],
                y=[channel] * len(channel_data),
                mode='markers',
                name=channel,
                marker=dict(
                    size=10,
                    color=colors[i % len(colors)],
                    symbol='circle'
                ),
                text=channel_data['title'],
                hovertemplate='<b>%{text}</b><br>日期: %{x}<br>频道: %{y}<extra></extra>'
            ))
        
        fig.update_layout(
            title="频道发布时间线",
            xaxis_title="日期",
            yaxis_title="频道",
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_publish_pattern_analysis(self):
        """创建发布模式分析"""
        if not self.records:
            return None
            
        df = pd.DataFrame(self.records)
        df['publish_date'] = pd.to_datetime(df['publish_date'])
        df = df[df['channel_name'].isin(self.selected_channels)]
        
        if df.empty:
            return None
        
        # 分析发布模式
        df['weekday'] = df['publish_date'].dt.day_name()
        df['hour'] = pd.to_datetime(df['publish_time'], format='%H:%M').dt.hour
        
        # 按星期几统计
        weekday_stats = df.groupby('weekday').size().reset_index(name='count')
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_stats['weekday'] = pd.Categorical(weekday_stats['weekday'], categories=weekday_order, ordered=True)
        weekday_stats = weekday_stats.sort_values('weekday')
        
        # 按小时统计
        hour_stats = df.groupby('hour').size().reset_index(name='count')
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("按星期发布分布", "按小时发布分布"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 星期分布
        fig.add_trace(
            go.Bar(
                x=weekday_stats['weekday'],
                y=weekday_stats['count'],
                name="星期分布",
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # 小时分布
        fig.add_trace(
            go.Bar(
                x=hour_stats['hour'],
                y=hour_stats['count'],
                name="小时分布",
                marker_color='lightgreen'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="发布模式分析",
            height=400,
            showlegend=False
        )
        
        return fig 