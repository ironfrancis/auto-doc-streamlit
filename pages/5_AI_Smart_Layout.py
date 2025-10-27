import sys
import os
import json
import streamlit as st

# 使用简化路径管理
from simple_paths import *

# 移除未使用的导入
import requests
from core.utils.theme_loader import load_anthropic_theme

st.set_page_config(page_title="AI智能布局", layout="wide")

# 加载主题
load_anthropic_theme()

st.title("AI智能排版（实验功能）")

# 使用简化路径管理
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "html_template_with_llm_convert")
HTML_TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")

# 检查模板目录
template_dirs = []
if os.path.exists(TEMPLATE_DIR):
    template_dirs.append(("AI转换模板", TEMPLATE_DIR))
if os.path.exists(HTML_TEMPLATES_DIR):
    template_dirs.append(("标准HTML模板", HTML_TEMPLATES_DIR))

if not template_dirs:
    st.error("找不到任何模板目录！")
    st.stop()

# 收集所有模板文件
all_templates = []
for dir_name, dir_path in template_dirs:
    if os.path.exists(dir_path):
        files = [f for f in os.listdir(dir_path) if f.endswith('.html')]
        for file in files:
            all_templates.append((f"{dir_name}: {file}", os.path.join(dir_path, file)))

if not all_templates:
    st.error("没有找到任何HTML模板文件")
    st.stop()

# 显示模板选择
template_names = [name for name, path in all_templates]
template_choice = st.selectbox("选择HTML模板", template_names, key="ai_layout_template")
selected_template_path = dict(all_templates)[template_choice]

# 添加模板预览功能
if st.checkbox("预览选中的模板", key="preview_template"):
    try:
        with open(selected_template_path, 'r', encoding='utf-8') as f:
            preview_html = f.read()
        st.markdown("**模板预览：**", unsafe_allow_html=True)
        st.components.v1.html(preview_html, height=400, scrolling=True)
    except Exception as e:
        st.error(f"模板预览失败：{str(e)}")

md_input = st.text_area("输入Markdown内容", height=300, key="ai_layout_md_input")

# 读取端点
ENDPOINTS_PATH = os.path.join(CONFIG_DIR, "llm_endpoints.json")
if os.path.exists(ENDPOINTS_PATH):
    with open(ENDPOINTS_PATH, "r", encoding="utf-8") as f:
        endpoints = json.load(f)
else:
    endpoints = []
endpoint_names = [ep["name"] for ep in endpoints] if endpoints else []

if endpoints:
    selected_ep_idx = st.selectbox("选择LLM端点", range(len(endpoint_names)), format_func=lambda i: endpoint_names[i], key="ai_layout_ep_select")
    ep = endpoints[selected_ep_idx]
    llm_endpoint = st.text_input("LLM端点（如OpenAI/Magic API地址）", value=ep.get("api_url", ""), disabled=True, key="ai_layout_llm_endpoint")
    llm_api_key = st.text_input("API Key", value=ep.get("api_key", ""), type="password", disabled=True, key="ai_layout_llm_key")
    llm_model = st.text_input("模型名称", value=ep.get("model", ""), disabled=True, key="ai_layout_llm_model")
    
    # 所有端点都使用OpenAI兼容格式，无需选择API类型
else:
    llm_endpoint = st.text_input("LLM端点（如OpenAI/Magic API地址）", key="ai_layout_llm_endpoint")
    llm_api_key = st.text_input("API Key", type="password", key="ai_layout_llm_key")
    llm_model = st.text_input("模型名称", key="ai_layout_llm_model")

if st.button("AI智能排版并生成HTML", key="ai_layout_btn"):
    if not md_input.strip():
        st.warning("请输入Markdown内容！")
    elif not llm_endpoint.strip() or not llm_api_key.strip() or not llm_model.strip():
        st.warning("请填写完整的LLM配置信息！")
    else:
        try:
            # 读取模板内容
            with open(selected_template_path, 'r', encoding='utf-8') as f:
                template_html = f.read()
            
            # 构造LLM提示词
            prompt = f"""你是一个专业的内容排版助手。请根据以下要求，将用户提供的Markdown内容，结合给定的HTML模板，智能排版为一篇适合公众号/网页发布的完整HTML文章：
- 保持模板的样式和结构，内容插入到模板的主内容区（如<!--CONTENT-->或<div class='magic-article-container'>）
- 每一行都用<p>标签包裹，代码块、列表、引用等用模板推荐的结构
- 保证排版美观、结构清晰、适合阅读
- 只输出最终完整HTML代码，不要输出解释说明

【HTML模板】
{template_html}

**用户Markdown内容：**
{md_input}"""
            
            # 所有端点都使用OpenAI兼容格式
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
            
            # 调用LLM
            with st.spinner("AI正在处理中..."):
                resp = requests.post(llm_endpoint, headers=headers, json=data, timeout=120)
                
            if resp.status_code == 200:
                result = resp.json()
                try:
                    # 根据API响应格式解析结果
                    # 尝试多种可能的响应格式
                    if "choices" in result and len(result["choices"]) > 0:
                        if "message" in result["choices"][0]:
                            html_result = result["choices"][0]["message"]["content"]
                        else:
                            html_result = result["choices"][0].get("text", str(result["choices"][0]))
                    elif "content" in result:
                        if isinstance(result["content"], list) and len(result["content"]) > 0:
                            html_result = result["content"][0].get("text", str(result["content"][0]))
                        else:
                            html_result = result["content"]
                    elif "data" in result and "messages" in result["data"]:
                        # Magic API格式
                        if len(result["data"]["messages"]) > 0:
                            html_result = result["data"]["messages"][0]["message"]["content"]
                        else:
                            html_result = "API返回的消息列表为空"
                    elif "text" in result:
                        html_result = result["text"]
                    elif "response" in result:
                        html_result = result["response"]
                        # 如果都不匹配，显示整个响应用于调试
                        st.warning("无法识别API响应格式，显示原始响应：")
                        st.json(result)
                        html_result = str(result)
                    
                    # 验证HTML格式
                    if not html_result.strip().startswith('<!DOCTYPE html') and not html_result.strip().startswith('<html'):
                        st.warning("AI返回的内容可能不是完整HTML，尝试修复...")
                        # 尝试包装为完整HTML
                        if '<body' in html_result and '</body>' in html_result:
                            html_result = f"<!DOCTYPE html>\n<html lang='zh-CN'>\n<head>\n<meta charset='UTF-8'>\n<title>AI生成的文章</title>\n</head>\n{html_result}"
                        else:
                            html_result = f"<!DOCTYPE html>\n<html lang='zh-CN'>\n<head>\n<meta charset='UTF-8'>\n<title>AI生成的文章</title>\n<style>\nbody {{ font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif; line-height: 1.6; margin: 20px; }}\n</style>\n</head>\n<body>\n{html_result}\n</body>\n</html>"
                    
                    st.success("AI排版成功！")
                    
                    # 添加HTML预览选项
                    preview_option = st.radio("选择预览方式", ["Streamlit预览", "新窗口打开", "仅显示代码"], key="preview_option")
                    
                    if preview_option == "Streamlit预览":
                        st.markdown("**HTML预览：**", unsafe_allow_html=True)
                        # 使用iframe包装，提高安全性
                        safe_html = f"""
                        <iframe srcdoc="{html_result.replace('"', '&quot;')}" 
                                width="100%" height="800" 
                                frameborder="0" 
                                style="border: 1px solid #ddd; border-radius: 5px;">
                        </iframe>
                        """
                        st.components.v1.html(safe_html, height=800, scrolling=False)
                    elif preview_option == "新窗口打开":
                        # 生成临时HTML文件供下载
                        import tempfile
                        import base64
                        
                        # 创建临时文件
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                            f.write(html_result)
                            temp_file_path = f.name
                        
                        # 读取文件并编码为base64
                        with open(temp_file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # 创建下载链接
                        b64 = base64.b64encode(file_content).decode()
                        href = f'<a href="data:text/html;base64,{b64}" download="ai_generated_article.html" target="_blank">点击下载HTML文件</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        st.info("下载后双击文件即可在浏览器中预览")
                        
                        # 清理临时文件
                        os.unlink(temp_file_path)
                    
                    st.markdown("**完整HTML代码：**")
                    st.code(html_result, language="html")
                    
                except (KeyError, IndexError, TypeError) as e:
                    st.error(f"解析API响应失败：{str(e)}")
                    st.info("原始响应内容：")
                    st.json(result)
            else:
                st.error(f"AI排版失败：{resp.status_code} - {resp.text}")
        except FileNotFoundError:
            st.error(f"找不到模板文件：{template_choice}")
        except Exception as e:
            st.error(f"处理异常：{str(e)}")

st.info("本页面为实验功能，直接调用大模型进行内容+模板智能排版，适合复杂结构或AI美化场景。建议内容不宜过长，避免API超时。") 