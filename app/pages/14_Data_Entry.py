import sys
import os
import json
import streamlit as st

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from language_manager import init_language, get_text
from datetime import datetime, date
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from utils.data_collector import ChannelDataCollector

T = {
    "en": {
        "page_title": "Data Entry",
        "add_channel": "Add Channel",
        "add_record": "Add Publish Record",
        "update_metrics": "Update Metrics",
        "channel_name": "Channel Name",
        "channel_description": "Channel Description",
        "article_title": "Article Title",
        "publish_date": "Publish Date",
        "publish_time": "Publish Time",
        "status": "Status",
        "views": "Views",
        "likes": "Likes",
        "comments": "Comments",
        "shares": "Shares",
        "url": "URL",
        "tags": "Tags",
        "add": "Add",
        "update": "Update",
        "save": "Save",
        "cancel": "Cancel",
        "success": "Operation Successful",
        "error": "Operation Failed",
        "select_channel": "Select Channel",
        "select_record": "Select Record",
        "new_views": "New Views",
        "new_likes": "New Likes",
        "new_comments": "New Comments",
        "new_shares": "New Shares",
        "export_data": "Export Data",
        "import_data": "Import Data",
        "upload_file": "Upload CSV File",
        "download_data": "Download Data"
    }
}

# 初始化语言设置
init_language()

st.set_page_config(page_title=get_text("page_title"), layout="wide")
st.title(get_text("page_title"))

# 初始化数据采集器
collector = ChannelDataCollector()

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📺 " + get_text("add_channel"),
    "📝 " + get_text("add_record"), 
    "📊 " + get_text("update_metrics"),
    "🗑️ " + "删除管理",
    "📁 " + get_text("import_data")
])

with tab1:
    st.subheader(get_text("add_channel"))
    
    with st.form("add_channel_form"):
        channel_name = st.text_input(get_text("channel_name"), key="new_channel_name")
        channel_description = st.text_area(get_text("channel_description"), key="new_channel_desc")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button(get_text("add")):
                if channel_name.strip():
                    collector.add_channel(channel_name.strip(), channel_description.strip())
                    st.success(f"✅ 频道 '{channel_name}' 添加成功")
                    st.rerun()
                else:
                    st.error("❌ 频道名称不能为空")
        
        with col2:
            if st.form_submit_button(get_text("cancel")):
                st.rerun()
    
    # 显示现有频道
    st.subheader("现有频道")
    if collector.channels_data:
        for channel in collector.channels_data:
            with st.expander(f"📺 {channel['channel_name']}"):
                st.write(f"**描述:** {channel.get('description', '无描述')}")
                st.write(f"**记录数:** {len(channel['publish_records'])}")
    else:
        st.info("暂无频道，请先添加频道")

with tab2:
    st.subheader(get_text("add_record"))
    
    # 检查是否有频道
    if not collector.channels_data:
        st.warning("请先添加频道")
    else:
        with st.form("add_record_form"):
            # 选择频道
            channel_names = [ch['channel_name'] for ch in collector.channels_data]
            selected_channel = st.selectbox(get_text("select_channel"), channel_names)
            
            # 基本信息
            title = st.text_input(get_text("article_title"))
            col1, col2 = st.columns(2)
            with col1:
                publish_date = st.date_input(get_text("publish_date"), value=date.today())
                publish_time = st.time_input(get_text("publish_time"), value=datetime.now().time())
                status = st.selectbox(get_text("status"), ["published", "draft", "scheduled"])
            
            with col2:
                views = st.number_input(get_text("views"), min_value=0, value=0)
                likes = st.number_input(get_text("likes"), min_value=0, value=0)
                comments = st.number_input(get_text("comments"), min_value=0, value=0)
                shares = st.number_input(get_text("shares"), min_value=0, value=0)
            
            url = st.text_input(get_text("url"))
            tags_input = st.text_input(get_text("tags"), placeholder="用逗号分隔，如: AI,技术,新闻")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button(get_text("add")):
                    if title.strip():
                        # 处理标签
                        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                        
                        record = {
                            'title': title.strip(),
                            'publish_date': publish_date.strftime('%Y-%m-%d'),
                            'publish_time': publish_time.strftime('%H:%M'),
                            'status': status,
                            'views': views,
                            'likes': likes,
                            'comments': comments,
                            'shares': shares,
                            'url': url.strip(),
                            'tags': tags
                        }
                        
                        collector.add_publish_record(selected_channel, record)
                        st.success(f"✅ 发布记录添加成功: {title}")
                        st.rerun()
                    else:
                        st.error("❌ 文章标题不能为空")
            
            with col2:
                if st.form_submit_button(get_text("cancel")):
                    st.rerun()

with tab3:
    st.subheader(get_text("update_metrics"))
    
    all_records = collector.get_all_records()
    if not all_records:
        st.info("暂无记录可更新")
    else:
        # 选择记录
        record_options = [f"[{r['channel_name']}] {r['title']}" for r in all_records]
        selected_record_idx = st.selectbox(get_text("select_record"), range(len(record_options)), 
                                         format_func=lambda x: record_options[x])
        
        if selected_record_idx is not None:
            selected_record = all_records[selected_record_idx]
            
            st.write(f"**当前记录:** {selected_record['title']}")
            st.write(f"**频道:** {selected_record['channel_name']}")
            
            with st.form("update_metrics_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_views = st.number_input(get_text("new_views"), min_value=0, 
                                              value=selected_record['views'])
                    new_likes = st.number_input(get_text("new_likes"), min_value=0, 
                                              value=selected_record['likes'])
                
                with col2:
                    new_comments = st.number_input(get_text("new_comments"), min_value=0, 
                                                 value=selected_record['comments'])
                    new_shares = st.number_input(get_text("new_shares"), min_value=0, 
                                               value=selected_record['shares'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button(get_text("update")):
                        metrics = {
                            'views': new_views,
                            'likes': new_likes,
                            'comments': new_comments,
                            'shares': new_shares
                        }
                        
                        collector.update_record_metrics(selected_record['channel_name'], 
                                                     selected_record['id'], metrics)
                        st.success("✅ 数据指标更新成功")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button(get_text("cancel")):
                        st.rerun()

with tab4:
    st.subheader("🗑️ 删除管理")
    
    # 删除频道
    st.subheader("删除频道")
    if collector.channels_data:
        channel_names = [ch['channel_name'] for ch in collector.channels_data]
        channel_to_delete = st.selectbox("选择要删除的频道", channel_names)
        
        if st.button("🗑️ 删除频道", type="secondary"):
            if collector.delete_channel(channel_to_delete):
                st.success(f"✅ 频道 '{channel_to_delete}' 删除成功")
                st.rerun()
            else:
                st.error(f"❌ 删除频道失败")
    else:
        st.info("暂无频道可删除")
    
    # 删除记录
    st.subheader("删除发布记录")
    all_records = collector.get_all_records()
    if all_records:
        record_options = [f"[{r['channel_name']}] {r['title']}" for r in all_records]
        record_to_delete_idx = st.selectbox("选择要删除的记录", range(len(record_options)), 
                                          format_func=lambda x: record_options[x])
        
        if st.button("🗑️ 删除记录", type="secondary"):
            selected_record = all_records[record_to_delete_idx]
            if collector.delete_record(selected_record['channel_name'], selected_record['id']):
                st.success(f"✅ 记录删除成功")
                st.rerun()
            else:
                st.error(f"❌ 删除记录失败")
    else:
        st.info("暂无记录可删除")

with tab5:
    st.subheader(get_text("import_data"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(get_text("export_data"))
        if st.button(get_text("download_data")):
            all_records = collector.get_all_records()
            if all_records:
                df = pd.DataFrame(all_records)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载CSV文件",
                    data=csv,
                    file_name=f"channel_publish_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("暂无数据可导出")
    
    with col2:
        st.subheader(get_text("import_data"))
        uploaded_file = st.file_uploader(get_text("upload_file"), type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                st.write("**预览数据:**")
                st.dataframe(df.head())
                
                if st.button("导入数据"):
                    imported_count = 0
                    for _, row in df.iterrows():
                        channel_name = row.get('channel_name', '未知频道')
                        record = {
                            'id': str(row.get('id', '')),
                            'title': row.get('title', ''),
                            'publish_date': row.get('publish_date', ''),
                            'publish_time': row.get('publish_time', ''),
                            'status': row.get('status', 'published'),
                            'views': int(row.get('views', 0)),
                            'likes': int(row.get('likes', 0)),
                            'comments': int(row.get('comments', 0)),
                            'shares': int(row.get('shares', 0)),
                            'url': row.get('url', ''),
                            'tags': row.get('tags', '').split(',') if row.get('tags') else []
                        }
                        
                        collector.add_publish_record(channel_name, record)
                        imported_count += 1
                    
                    st.success(f"✅ 成功导入 {imported_count} 条记录")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ 文件读取失败: {e}")

# 显示当前数据统计
st.sidebar.subheader("📊 数据统计")
all_records = collector.get_all_records()
if all_records:
    st.sidebar.write(f"**总频道数:** {len(collector.channels_data)}")
    st.sidebar.write(f"**总记录数:** {len(all_records)}")
    
    # 计算总指标
    total_views = sum(r['views'] for r in all_records)
    total_likes = sum(r['likes'] for r in all_records)
    st.sidebar.write(f"**总浏览量:** {total_views:,}")
    st.sidebar.write(f"**总点赞数:** {total_likes:,}")
else:
    st.sidebar.write("暂无数据") 