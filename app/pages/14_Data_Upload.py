from app.utils.wechat_data_processor import load_csv_path,append_record_to_csv
import streamlit as st
import pandas as pd



tab1, tab2 = st.tabs(["数据上传", "数据处理"])
with tab1:
    st.header("上传微信公众号导出的xls汇总数据")
    uploaded_file = st.file_uploader("上传XLS文件", type=['xls'])
    if uploaded_file is not None:
        st.write("文件上传成功！")
        upload_df = pd.read_excel(uploaded_file)
        st.dataframe(upload_df)

        if st.button("保存"):
            append_record_to_csv(upload_df)
            st.write("保存成功！")