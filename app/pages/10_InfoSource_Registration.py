import sys
import os
import json
import streamlit as st

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from language_manager import init_language, get_text
import requests

st.set_page_config(page_title="信息源注册", layout="wide")
st.title("信息源注册与管理")

INFO_PATH = "app/info_sources.json"

# 读取信息源
if os.path.exists(INFO_PATH):
    with open(INFO_PATH, "r", encoding="utf-8") as f:
        info_sources = json.load(f)
else:
    info_sources = []

# 顶端注册表单
st.subheader("注册新信息源")
new_title = st.text_input("信息源名称", key="info_title")
new_url = st.text_input("信息源URL", key="info_url")
preview_content = ""
if new_url.strip():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(new_url.strip(), headers=headers, timeout=8)
        if resp.status_code == 200:
            preview_content = resp.text[:500]  # 只预览前500字符
        else:
            preview_content = f"请求失败，状态码：{resp.status_code}"
    except Exception as e:
        preview_content = f"请求异常：{e}"
if preview_content:
    st.markdown(f"**预览：**\n{preview_content}")
if st.button("注册信息源", key="reg_info_btn"):
    if not new_title.strip() or not new_url.strip():
        st.warning("请输入信息源名称和URL！")
    else:
        info_sources.append({"title": new_title.strip(), "url": new_url.strip()})
        with open(INFO_PATH, "w", encoding="utf-8") as f:
            json.dump(info_sources, f, ensure_ascii=False, indent=2)
        st.success("信息源注册成功！")
        st.rerun()

st.markdown("---")
st.subheader("已注册信息源")

if "edit_info_idx" not in st.session_state:
    st.session_state["edit_info_idx"] = None
# 不再需要preview_info_idx

# 展示所有信息源
if not info_sources:
    st.info("暂无信息源，请先注册。")
else:
    for idx, info in enumerate(reversed(info_sources)):
        real_idx = len(info_sources) - 1 - idx  # 反向索引，便于编辑/删除
        with st.expander(f"{info['title']}", expanded=False):
            if st.session_state["edit_info_idx"] == real_idx:
                # 编辑模式
                edit_title = st.text_input("信息源名称", value=info['title'], key=f"edit_title_{real_idx}")
                edit_url = st.text_input("信息源URL", value=info['url'], key=f"edit_url_{real_idx}")
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("保存", key=f"save_info_{real_idx}"):
                        info_sources[real_idx]["title"] = edit_title.strip()
                        info_sources[real_idx]["url"] = edit_url.strip()
                        with open(INFO_PATH, "w", encoding="utf-8") as f:
                            json.dump(info_sources, f, ensure_ascii=False, indent=2)
                        st.session_state["edit_info_idx"] = None
                        st.success("保存成功！")
                        st.rerun()
                with btn_col2:
                    if st.button("取消", key=f"cancel_info_{real_idx}"):
                        st.session_state["edit_info_idx"] = None
                        st.rerun()
            else:
                st.markdown(f"**URL：** {info['url']}")
                # 自动请求并预览内容
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    resp = requests.get(info['url'], headers=headers, timeout=8)
                    if resp.status_code == 200:
                        content = resp.text[:500]
                    else:
                        content = f"请求失败，状态码：{resp.status_code}"
                except Exception as e:
                    content = f"请求异常：{e}"
                st.markdown(f"**预览：**\n{content}")
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("编辑", key=f"edit_info_{real_idx}"):
                        st.session_state["edit_info_idx"] = real_idx
                        st.rerun()
                with btn_col2:
                    if st.button("删除", key=f"del_info_{real_idx}"):
                        info_sources.pop(real_idx)
                        with open(INFO_PATH, "w", encoding="utf-8") as f:
                            json.dump(info_sources, f, ensure_ascii=False, indent=2)
                        st.success("已删除！")
                        st.rerun()
                # 自动网页预览
                st.info(f"网页预览: {info['url']} (如页面空白，说明目标网站禁止了嵌入)")
                st.components.v1.iframe(info['url'], height=400, scrolling=True) 