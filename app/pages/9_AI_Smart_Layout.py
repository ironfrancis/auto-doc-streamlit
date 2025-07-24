import sys
import os
import json
import streamlit as st
import requests

st.set_page_config(page_title="AI智能排版", layout="wide")
st.title("AI智能排版（实验功能）")

with st.sidebar:
    lang = st.selectbox("语言 / Language", ["zh", "en"], index=0 if st.session_state.get("lang", "zh") == "zh" else 1, key="lang_global")
    if lang != st.session_state.get("lang", "zh"):
        st.session_state["lang"] = lang

# 读取模板
TEMPLATE_DIR = "app/html_templates"
template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
template_choice = st.selectbox("选择HTML模板", template_files, key="ai_layout_template")

md_input = st.text_area("输入Markdown内容", height=300, key="ai_layout_md_input")

# 读取端点
ENDPOINTS_PATH = "app/llm_endpoints.json"
if os.path.exists(ENDPOINTS_PATH):
    with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
        endpoints = json.load(f)
else:
    endpoints = []
endpoint_names = [ep["name"] for ep in endpoints] if endpoints else []

if endpoints:
    selected_ep_idx = st.selectbox("选择LLM端点", range(len(endpoint_names)), format_func=lambda i: endpoint_names[i], key="ai_layout_ep_select")
    ep = endpoints[selected_ep_idx]
    llm_endpoint = st.text_input("LLM端点（如OpenAI/Magic API地址）", value=ep.get("api_url", ""), key="ai_layout_llm_endpoint")
    llm_api_key = st.text_input("API Key", value=ep.get("api_key", ""), type="password", key="ai_layout_llm_key")
    llm_model = st.text_input("模型名称", value=ep.get("model", ""), key="ai_layout_llm_model")
else:
    llm_endpoint = st.text_input("LLM端点（如OpenAI/Magic API地址）", key="ai_layout_llm_endpoint")
    llm_api_key = st.text_input("API Key", type="password", key="ai_layout_llm_key")
    llm_model = st.text_input("模型名称", key="ai_layout_llm_model")

if st.button("AI智能排版并生成HTML", key="ai_layout_btn"):
    if not md_input.strip():
        st.warning("请输入Markdown内容！")
    else:
        # 读取模板内容
        with open(os.path.join(TEMPLATE_DIR, template_choice), 'r', encoding='utf-8') as f:
            template_html = f.read()
        # 构造LLM提示词
        prompt = f"""
你是一个专业的内容排版助手。请根据以下要求，将用户提供的Markdown内容，结合给定的HTML模板，智能排版为一篇适合公众号/网页发布的完整HTML文章：
- 保持模板的样式和结构，内容插入到模板的主内容区（如<!--CONTENT-->或<div class='magic-article-container'>）
- 每一行都用<p>标签包裹，代码块、列表、引用等用模板推荐的结构
- 保证排版美观、结构清晰、适合阅读
- 只输出最终完整HTML代码，不要输出解释说明

【HTML模板】
{template_html}

【Markdown内容】
{md_input}
"""
        # 调用LLM
        headers = {"Authorization": f"Bearer {llm_api_key}", "Content-Type": "application/json"}
        data = {
            "model": llm_model,
            "messages": [
                {"role": "system", "content": "你是一个专业的内容排版助手。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4096
        }
        try:
            resp = requests.post(llm_endpoint, headers=headers, json=data, timeout=120)
            if resp.status_code == 200:
                result = resp.json()
                html_result = result["choices"][0]["message"]["content"]
                st.success("AI排版成功！")
                st.markdown("**HTML预览：**", unsafe_allow_html=True)
                st.components.v1.html(html_result, height=800, scrolling=True)
                st.markdown("**完整HTML代码：**")
                st.code(html_result, language="html")
            else:
                st.error(f"AI排版失败：{resp.text}")
        except Exception as e:
            st.error(f"请求异常：{e}")

st.info("本页面为实验功能，直接调用大模型进行内容+模板智能排版，适合复杂结构或AI美化场景。建议内容不宜过长，避免API超时。") 