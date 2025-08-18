import pandas as pd
import os
import sys
import streamlit as st


def load_csv_data():
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

    df = pd.read_csv(CSV_PATH, encoding='utf-8')

    return df


def visualize_data():
    df = load_csv_data()

    st.title("微信公众号文章数据分析")

    # 按账号名称分组统计
    st.header("各账号文章数量统计")
    account_counts = df['账号名称'].value_counts()
    st.bar_chart(account_counts)

    # 阅读量Top10文章
    st.header("阅读量Top10文章")
    top_reads = df.nlargest(10, '总阅读人数')[['内容标题', '总阅读人数', '账号名称']]
    st.dataframe(top_reads)

    # 分享量Top10文章
    st.header("分享量Top10文章")
    top_shares = df.nlargest(10, '总分享次数')[['内容标题', '总分享次数', '账号名称']]
    st.dataframe(top_shares)

    # 按日期统计发布量
    st.header("每日文章发布数量")
    df['发表时间'] = pd.to_datetime(df['发表时间'])
    daily_counts = df.resample('D', on='发表时间').size()
    st.line_chart(daily_counts)

    # 送达阅读率分布
    st.header("送达阅读率分布")
    st.bar_chart(df['送达阅读率'].value_counts(bins=10))

    # 阅读完成率分布
    st.header("阅读完成率分布")
    st.bar_chart(df['阅读完成率'].value_counts(bins=10))

visualize_data()