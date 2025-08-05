import sys
import os

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import streamlit as st
from language_manager import init_language, get_text
from md_utils import md_to_html
from path_manager import get_static_dir, get_md_review_dir, get_images_dir
import glob

# 多语言文本定义
T = {
    "zh": {
        "page_title": "MD转HTML",
        "or": "或者",
        "html_newtab": "在新标签页中打开",
        "html_preview": "HTML预览"
    },
    "en": {
        "page_title": "MD to HTML Converter",
        "or": "or",
        "html_newtab": "Open in new tab",
        "html_preview": "HTML Preview"
    }
}

st.markdown("### 📋 功能说明")
st.markdown("""
    **支持的图片格式:**
    - 本地图片路径 (绝对路径或相对路径)
    - 网络图片URL (自动下载到本地)
    - 静态资源路径
    
    **图片处理:**
    - 自动复制本地图片到静态目录
    - 自动下载网络图片到本地
    - Markdown中使用绝对路径
    - HTML中自动转换为base64编码
    - 支持PNG、JPG、JPEG、GIF、WebP格式
    """)
    
st.markdown("### 💡 使用提示")
st.markdown("""
    **本地图片示例:**
    ```
    ![图片描述](/Users/username/Desktop/image.png)
    ![图片描述](./images/photo.jpg)
    ```
    
    **网络图片示例:**
    ```
    ![图片描述](https://example.com/image.jpg)
    ![图片描述](https://cdn.example.com/photo.png)
    ```
    
    **注意:** 网络图片会自动下载到本地，图片路径会更新为绝对路径，确保图片在离线环境下也能正常显示。
    """)

st.set_page_config(page_title=get_text("page_title"), layout="wide")
st.title(get_text("page_title"))

STATIC_DIR = get_static_dir()
TEMPLATE_DIR = "app/html_templates"
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

if st.button(get_text("convert"), key="convert_button"):
    if not md_text.strip():
        st.warning("请上传、粘贴或选择Markdown内容！")
    else:
        # 显示处理进度
        with st.spinner("正在处理Markdown内容和图片..."):
            html_result = md_to_html(md_text, template_name=template_choice, static_dir=STATIC_DIR)
        
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
            st.button(
                "📋 复制HTML" if get_text("get_language()") == "zh" else "📋 Copy HTML",
                key="copy_html_btn",
                help="点击复制生成的HTML代码到剪贴板" if get_text("get_language()") == "zh" else "Copy generated HTML to clipboard"
            )
            import json
            repr_html = json.dumps(html_result)
            st.markdown(f"""
            <script>
            function copyToClipboard(text) {{
                navigator.clipboard.writeText(text);
            }}
            const btn = window.parent.document.querySelector('button[data-testid="baseButton-copy_html_btn"]');
            if (btn) {{
                btn.onclick = function() {{
                    copyToClipboard({repr_html});
                    alert('{('已复制到剪贴板' if lang == 'zh' else 'Copied to clipboard!')}');
                }}
            }}
            </script>
            """, unsafe_allow_html=True) 