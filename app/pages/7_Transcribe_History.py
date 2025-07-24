import streamlit as st
import json
import os

HISTORY_PATH = "app/md_transcribe_history.json"

st.title("转写历史")

with st.sidebar:
    lang = st.selectbox("语言 / Language", ["zh", "en"], index=0 if st.session_state.get("lang", "zh") == "zh" else 1, key="lang_global")
    if lang != st.session_state.get("lang", "zh"):
        st.session_state["lang"] = lang

if os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        history = json.load(f)
    if not history:
        st.info("暂无历史记录")
    else:
        for item in reversed(history):
            st.markdown(f"**频道：** {item.get('channel', '')}  ")
            st.markdown(f"**时间：** {item.get('created_at', '')}")
            st.markdown(f"**内容预览：** {item.get('md_result', '')[:100]} ...")
            with st.expander("查看完整内容"):
                st.markdown(item.get('md_result', ''), unsafe_allow_html=False)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"在Finder中打开", key=f"open_finder_{item['id']}"):
                        # 保存为临时md文件并用os.system打开Finder
                        tmp_path = f"/tmp/{item['id']}.md"
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(item.get('md_result', ''))
                        os.system(f"open -R '{tmp_path}'")
                with col2:
                    if st.button(f"跳转到Upload Markdown & Generate HTML", key=f"goto_upload_{item['id']}"):
                        st.session_state['upload_md_content'] = item.get('md_result', '')
                        st.switch_page('pages/3_Upload_MD_to_HTML.py')
            st.markdown("---")
else:
    st.info("暂无历史记录") 