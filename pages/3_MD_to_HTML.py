import sys
import os

# 使用简化路径管理
from simple_paths import *

import streamlit as st
from language_manager import init_language, get_text, get_language
from md_utils import md_to_html, TEMPLATE_DIR
# Using simple_paths for path management - functions already imported
import glob

# 多语言文本定义
T = {
    "zh": {
        "page_title": "MD转HTML",
        "or": "或者",
        "html_newtab": "在新标签页中打开",
        "html_preview": "HTML预览",
        "inline_css_option": "生成内联CSS的HTML（适合粘贴到富文本编辑器）",
        "copy_inline_css": "📋 复制内联CSS HTML",
        "copy_inline_css_help": "复制带有内联样式的HTML代码，可直接粘贴到公众号后台等富文本编辑器"
    },
    "en": {
        "page_title": "MD to HTML Converter",
        "or": "or",
        "html_newtab": "Open in new tab",
        "html_preview": "HTML Preview",
        "inline_css_option": "Generate HTML with inline CSS (suitable for rich text editors)",
        "copy_inline_css": "📋 Copy Inline CSS HTML",
        "copy_inline_css_help": "Copy HTML with inline styles for direct pasting into rich text editors"
    }
}


st.set_page_config(page_title="MD转HTML", layout="wide")
st.title("MD转HTML")

STATIC_DIR = get_static_dir()
os.makedirs(STATIC_DIR, exist_ok=True)

# 最近md文件选择
md_review_dir = get_md_review_dir()
recent_md_files = sorted(glob.glob(f"{md_review_dir}/*.md"), key=os.path.getmtime, reverse=True)[:10]
recent_md_names = [os.path.basename(f) for f in recent_md_files]
selected_md = st.selectbox("选择最近的Markdown文件（可选）", ["-"] + recent_md_names, key="md2html_recent_md")

# 粘贴/上传/选择md内容
md_text = ""
if selected_md != "-":
    with open(os.path.join(md_review_dir, selected_md), "r", encoding="utf-8") as f:
        md_text = f.read()
else:
    uploaded_md = st.file_uploader(get_text("upload"), type=["md"], key="upload_md_file")
    st.markdown(f"**{T['zh']['or']}**")
    pasted_md = st.text_area(get_text("paste"), height=200, key="paste_md_content")
    if uploaded_md:
        md_text = uploaded_md.read().decode("utf-8")
    elif pasted_md.strip():
        md_text = pasted_md

template_files = [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.html')]
template_choice = st.selectbox(get_text("select_template"), template_files, key="select_template_choice")

# 添加内联CSS选项
inline_css_option = st.checkbox(T['zh']['inline_css_option'], value=True, key="inline_css_checkbox")

if st.button(get_text("convert"), key="convert_button"):
    if not md_text.strip():
        st.warning("请上传、粘贴或选择Markdown内容！")
    else:
        # 显示处理进度
        with st.spinner("正在处理Markdown内容和图片..."):
        # 根据用户选择决定是否生成内联CSS
            if inline_css_option:
                # 生成带有内联CSS的HTML（适合富文本编辑器）
                html_result = md_to_html(md_text, template_name=template_choice, static_dir=STATIC_DIR, inline_css=True)
            else:
                # 生成普通HTML（保留CSS类，适合网页显示）
                html_result = md_to_html(md_text, template_name=template_choice, static_dir=STATIC_DIR, inline_css=False)
            
        html_path = os.path.join(STATIC_DIR, "md2html_preview.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_result)
        
        st.success(get_text("success"))
        
        # 显示图片处理信息
        images_dir = get_images_dir()
        if os.path.exists(images_dir):
            image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            if image_files:
                st.info(f"✅ 已处理 {len(image_files)} 张图片（包括本地复制和网络下载）")
                st.info("💡 图片已自动转换为base64编码，HTML组件中可以正确显示")
                with st.expander("查看处理的图片", expanded=False):
                    for img_file in sorted(image_files):
                        file_path = os.path.join(images_dir, img_file)
                        file_size = os.path.getsize(file_path)
                        st.markdown(f"- {img_file} ({file_size} bytes)")
                
                # 显示图片预览
                with st.expander("图片预览", expanded=False):
                    cols = st.columns(3)
                    for i, img_file in enumerate(image_files[:9]):  # 最多显示9张图片
                        col_idx = i % 3
                        with cols[col_idx]:
                            try:
                                st.image(os.path.join(images_dir, img_file), caption=img_file, use_container_width=True)
                            except Exception as e:
                                st.error(f"无法预览 {img_file}: {str(e)}")
        
        html_url = "/static/md2html_preview.html"
        st.markdown(f"[{T['zh']['html_newtab']}](http://localhost:8501{html_url})", unsafe_allow_html=True)
        st.markdown(f"**{T['zh']['html_preview']}**", unsafe_allow_html=True)
        col1, col2 = st.columns([8, 1])
        with col1:
            st.components.v1.html(html_result, height=600, scrolling=True)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 获取当前语言
            current_lang = get_language()
            
            # 根据内联CSS选项显示不同的复制按钮
            if inline_css_option:
                copy_button_text = T['zh']['copy_inline_css'] if current_lang == "zh" else T['en']['copy_inline_css']
                copy_help_text = T['zh']['copy_inline_css_help'] if current_lang == "zh" else T['en']['copy_inline_css_help']
            else:
                copy_button_text = "📋 复制HTML" if current_lang == "zh" else "📋 Copy HTML"
                copy_help_text = "点击复制生成的HTML代码到剪贴板" if current_lang == "zh" else "Copy generated HTML to clipboard"
            
            if st.button(copy_button_text, key="copy_html_btn", help=copy_help_text):
                # 使用Streamlit的会话状态来处理复制
                st.session_state['html_to_copy'] = html_result
                if inline_css_option:
                    copy_success_msg = "✅ 内联CSS HTML代码已准备复制！可直接粘贴到公众号后台等富文本编辑器。" if current_lang == "zh" else "✅ Inline CSS HTML code ready! Can be pasted directly into rich text editors."
                else:
                    copy_success_msg = "✅ HTML代码已准备复制！请使用下方的文本框手动复制。" if current_lang == "zh" else "✅ HTML code ready! Please copy from the text box below."
                st.success(copy_success_msg)
            
            # 如果用户点击了复制按钮，显示可复制的文本框
            if 'html_to_copy' in st.session_state and st.session_state.get('html_to_copy'):
                if inline_css_option:
                    st.markdown("**内联CSS HTML代码（适合粘贴到富文本编辑器）:**" if current_lang == "zh" else "**Inline CSS HTML Code (suitable for rich text editors):**")
                else:
                    st.markdown("**HTML代码:**" if current_lang == "zh" else "**HTML Code:**")
                
                # 创建一个带有自动选择功能的文本框
                html_content = st.session_state['html_to_copy']
                
                # 使用expander来节省空间
                expander_title = "点击展开HTML代码" if current_lang == "zh" else "Click to expand HTML code"
                if inline_css_option:
                    expander_title = "点击展开内联CSS HTML代码" if current_lang == "zh" else "Click to expand inline CSS HTML code"
                
                with st.expander(expander_title, expanded=True):
                    st.code(html_content, language='html')
                    
                    # 提供下载功能作为备选
                    download_label = "💾 下载内联CSS HTML文件" if inline_css_option else "💾 下载HTML文件"
                    if current_lang != "zh":
                        download_label = "💾 Download Inline CSS HTML file" if inline_css_option else "💾 Download HTML file"
                    
                    st.download_button(
                        label=download_label,
                        data=html_content,
                        file_name="converted_inline_css.html" if inline_css_option else "converted.html",
                        mime="text/html",
                        key="download_html_btn"
                    )
                
                # 添加一个JavaScript方案来尝试复制到剪贴板
                import json
                escaped_html = json.dumps(html_content)
                
                if inline_css_option:
                    copy_success_msg = "内联CSS HTML已复制到剪贴板！可直接粘贴到富文本编辑器" if current_lang == "zh" else "Inline CSS HTML copied to clipboard! Can be pasted directly into rich text editors"
                    copy_fail_msg = "自动复制失败，请手动复制上方代码" if current_lang == "zh" else "Auto-copy failed, please copy the code above manually"
                    button_text = "🚀 一键复制内联CSS HTML到剪贴板" if current_lang == "zh" else "🚀 Copy Inline CSS HTML to Clipboard"
                else:
                    copy_success_msg = "HTML已复制到剪贴板!" if current_lang == "zh" else "HTML copied to clipboard!"
                    copy_fail_msg = "自动复制失败，请手动复制上方代码" if current_lang == "zh" else "Auto-copy failed, please copy the code above manually"
                    button_text = "🚀 一键复制到剪贴板" if current_lang == "zh" else "🚀 Copy to Clipboard"
                
                st.markdown(f"""
                <div>
                    <button onclick="copyHtmlToClipboard()" style="
                        background-color: #ff4b4b;
                        color: white;
                        border: none;
                        padding: 0.5rem 1rem;
                        border-radius: 0.25rem;
                        cursor: pointer;
                        font-size: 0.875rem;
                        margin-top: 0.5rem;
                        transition: background-color 0.3s ease;
                    " onmouseover="this.style.backgroundColor='#e63939'" onmouseout="this.style.backgroundColor='#ff4b4b'">
                        {button_text}
                    </button>
                </div>
                <script>
                function copyHtmlToClipboard() {{
                    const htmlContent = {escaped_html};
                    
                    // 尝试使用现代Clipboard API
                    if (navigator.clipboard && window.isSecureContext) {{
                        navigator.clipboard.writeText(htmlContent).then(function() {{
                            showCopySuccess('{copy_success_msg}');
                        }}).catch(function(err) {{
                            console.error('复制失败:', err);
                            fallbackCopyTextToClipboard(htmlContent);
                        }});
                    }} else {{
                        fallbackCopyTextToClipboard(htmlContent);
                    }}
                }}

                function fallbackCopyTextToClipboard(text) {{
                    const textArea = document.createElement("textarea");
                    textArea.value = text;
                    textArea.style.position = "fixed";
                    textArea.style.left = "-999999px";
                    textArea.style.top = "-999999px";
                    textArea.style.opacity = "0";
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    
                    try {{
                        const successful = document.execCommand('copy');
                        if (successful) {{
                            showCopySuccess('{copy_success_msg}');
                        }} else {{
                            showCopyError('{copy_fail_msg}');
                        }}
                    }} catch (err) {{
                        console.error('Fallback: 复制失败', err);
                        showCopyError('{copy_fail_msg}');
                    }}
                    
                    document.body.removeChild(textArea);
                }}

                function showCopySuccess(message) {{
                    // 创建成功提示
                    const successDiv = document.createElement('div');
                    successDiv.innerHTML = '✅ ' + message;
                    successDiv.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background-color: #4CAF50;
                        color: white;
                        padding: 12px 20px;
                        border-radius: 4px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                        z-index: 10000;
                        font-size: 14px;
                        max-width: 300px;
                        word-wrap: break-word;
                    `;
                    document.body.appendChild(successDiv);
                    
                    // 3秒后自动移除
                    setTimeout(() => {{
                        if (successDiv.parentNode) {{
                            successDiv.parentNode.removeChild(successDiv);
                        }}
                    }}, 3000);
                }}

                function showCopyError(message) {{
                    // 创建错误提示
                    const errorDiv = document.createElement('div');
                    errorDiv.innerHTML = '❌ ' + message;
                    errorDiv.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background-color: #f44336;
                        color: white;
                        padding: 12px 20px;
                        border-radius: 4px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                        z-index: 10000;
                        font-size: 14px;
                        max-width: 300px;
                        word-wrap: break-word;
                    `;
                    document.body.appendChild(errorDiv);
                    
                    // 5秒后自动移除
                    setTimeout(() => {{
                        if (errorDiv.parentNode) {{
                            errorDiv.parentNode.removeChild(errorDiv);
                        }}
                    }}, 5000);
                }}
                </script>
                """, unsafe_allow_html=True) 