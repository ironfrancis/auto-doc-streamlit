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

# 初始化语言设置
init_language()

st.set_page_config(page_title="LLM Testing", layout="wide")
st.title("LLM Endpoint & Prompt 测试工具")

# 读取端点
ENDPOINTS_PATH = "app/llm_endpoints.json"
if os.path.exists(ENDPOINTS_PATH):
    with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
        endpoints = json.load(f)
else:
    endpoints = []
endpoint_names = [ep["name"] for ep in endpoints] if endpoints else []

col1, col2 = st.columns(2)
with col1:
    selected_endpoint = st.selectbox("选择LLM端点", endpoint_names) if endpoint_names else ""
    prompt = st.text_area("提示词 (Prompt)", height=120)
    if st.button("测试LLM回复"):
        if not selected_endpoint or not prompt.strip():
            st.warning("请选择端点并输入提示词！")
        else:
            ep = next((e for e in endpoints if e["name"] == selected_endpoint), None)
            if not ep:
                st.error("端点未找到！")
            else:
                # 构造请求
                api_type = ep.get("api_type", "")
                api_url = ep.get("api_url", "")
                api_key = ep.get("api_key", "")
                model = ep.get("model", "")
                is_openai = ep.get("is_openai_compatible", False)
                try:
                    if is_openai:
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
                        resp = requests.post(api_url, headers=headers, json=data, timeout=30)
                    elif api_type == "Magic":
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        data = {
                            "model": model,
                            "messages": [
                                {"role": "system", "content": "你是一个有帮助的助手。"},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7,
                            "stream": False
                        }
                        resp = requests.post(api_url, headers=headers, json=data, timeout=30)
                    else:
                        st.error("暂不支持该API类型")
                        resp = None
                    if resp is not None:
                        meta = {"status_code": resp.status_code, "headers": dict(resp.headers)}
                        if resp.status_code == 200:
                            try:
                                result = resp.json()
                                if "data" in result and "messages" in result["data"] and result["data"]["messages"]:
                                    reply = result["data"]["messages"][0]["message"]["content"]
                                else:
                                    reply = result["choices"][0]["message"]["content"]
                            except Exception:
                                reply = resp.text
                            st.success("测试成功！")
                            st.code(f"元数据：\n{meta}", language="json")
                            st.code(f"模型回复：\n{reply or '无回复'}", language="markdown")
                        else:
                            st.error(f"测试失败，状态码：{resp.status_code}")
                            st.code(f"响应内容：\n{resp.text}")
                except Exception as e:
                    st.error(f"请求异常：{e}")

with col2:
    st.info("本页面用于快速测试不同端点和提示词组合，适合调试和对比LLM效果。\n\n左侧选择端点并输入提示词，点击测试即可实时查看回复。")

# 移除原有的语言选择器，使用统一的语言管理 