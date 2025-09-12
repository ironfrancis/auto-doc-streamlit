import sys
import os
import subprocess

# 使用简化路径管理
from simple_paths import *

from language_manager import init_language, get_text
import streamlit as st
import requests
from core.web2md import extract_markdown_from_url
# get_project_root is already imported from simple_paths
import json
from datetime import datetime
import time
import re
from pathlib import Path
import urllib.parse
from urllib.parse import urlparse
import hashlib
import base64
# Using simple_paths for path management - get_ori_docs_dir is already imported

# 页面设置
st.set_page_config(page_title="网页转MD", layout="wide")

# 标题
st.title("Web to Markdown")
st.caption("Extract content from web pages and convert to Markdown format")

# 获取项目根目录
project_root = get_project_root()
ori_docs_dir = get_ori_docs_dir()

# 创建表单
with st.form("web2md_form"):
    # URL输入
    url = st.text_input(
        "Web URL",
        placeholder="https://example.com",
        help="Enter the URL of the web page you want to extract"
    )

    # 创建两列布局用于基本选项
    col1, col2 = st.columns(2)

    with col1:
        # 提取范围选择
        scope = st.radio(
            "Extraction Scope",
            ["all", "viewport"],
            index=0,
            help="'all': Extract all content | 'viewport': Only extract visible content"
        )

        # 等待时间设置
        wait_time = st.slider(
            "Page Load Wait Time (seconds)",
            min_value=3,
            max_value=30,
            value=5,
            help="Increase this for pages with dynamic content"
        )

    with col2:
        # 滚动选项
        enable_scroll = st.checkbox(
            "Enable Page Scrolling",
            value=True,
            help="Scroll through the page to load lazy content before extraction"
        )

        # 滚动暂停时间
        scroll_pause = st.slider(
            "Scroll Pause Time (seconds)",
            min_value=0.5,
            max_value=5.0,
            value=1.0,
            step=0.5,
            help="Time to wait after each scroll action"
        )

        # 图片下载选项
        download_images = st.checkbox(
            "Download Images to Local",
            value=True,
            help="Automatically download images from the webpage to local directory"
        )

        # 自动打开文件选项
        auto_open = st.checkbox(
            "Auto-open file after extraction",
            value=True,
            help="Automatically open the extracted Markdown file with default application"
        )

    # 高级选项折叠区域
    with st.expander("Advanced Options"):
        # 视口高度
        viewport_height = st.slider(
            "Browser Viewport Height (pixels)",
            min_value=800,
            max_value=2000,
            value=1080,
            step=100,
            help="Height of the browser viewport in pixels"
        )

        # 要移除的选择器
        remove_selectors = st.text_area(
            "Remove Elements (CSS Selectors)",
            placeholder="nav, .ads, #sidebar, .footer",
            help="CSS selectors of elements to remove before extraction (comma separated)"
        )

    # 提交按钮
    submitted = st.form_submit_button("Extract Content")

# 处理表单提交
if submitted and url:
    if not url.startswith(("http://", "https://")):
        if not url.startswith("file:/"):
            url = f"https://{url}"

    with st.spinner(f"Extracting content from {url}..."):
        try:
            # 处理要移除的选择器
            selectors_to_remove = None
            if 'remove_selectors' in locals() and remove_selectors:
                selectors_to_remove = [s.strip() for s in remove_selectors.split(',') if s.strip()]
            
            # 提取Markdown内容
            result = extract_markdown_from_url(
                url=url,
                scope=scope,
                wait_time=wait_time,
                scroll=enable_scroll if 'enable_scroll' in locals() else True,
                scroll_pause=scroll_pause if 'scroll_pause' in locals() else 1.0,
                viewport_height=viewport_height if 'viewport_height' in locals() else 1080,
                remove_selectors=selectors_to_remove,
                download_images=download_images if 'download_images' in locals() else True
            )

            # 解析返回结果
            if result and len(result) == 2:
                markdown, saved_file_path = result
            else:
                markdown, saved_file_path = None, None

            if markdown:
                # 显示成功消息
                st.success("Content extracted successfully!")

                # 显示图片下载信息
                if 'download_images' in locals() and download_images:
                    static_dir = project_root / "app" / "static"
                    images_dir = static_dir / "images"
                    if images_dir.exists():
                        image_files = [f for f in images_dir.iterdir() if f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp')]
                        if image_files:
                            st.info(f"✅ Downloaded {len(image_files)} images to local directory")
                            with st.expander("View downloaded images", expanded=False):
                                for img_file in sorted(image_files):
                                    file_size = img_file.stat().st_size
                                    st.markdown(f"- {img_file.name} ({file_size} bytes)")

                # 创建两列布局
                col1, col2 = st.columns([3, 1])

                with col1:
                    # 显示提取的内容
                    st.subheader("Extracted Markdown")
                    st.code(markdown, language="markdown")

                with col2:
                    # 下载按钮
                    st.subheader("Download")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"web_extract_{timestamp}.md"

                    st.download_button(
                        label="Download Markdown",
                        data=markdown,
                        file_name=filename,
                        mime="text/markdown"
                    )

                    # 显示保存路径
                    if saved_file_path:
                        st.info(f"Automatically saved to: `{saved_file_path}`")

                        # 如果用户选择了自动打开文件
                        if 'auto_open' in locals() and auto_open:
                            try:
                                # 跨平台文件打开
                                if sys.platform == "darwin":  # macOS
                                    subprocess.run(['open', str(saved_file_path)], check=True)
                                elif sys.platform == "win32":  # Windows
                                    subprocess.run(['start', str(saved_file_path)], shell=True, check=True)
                                else:  # Linux
                                    subprocess.run(['xdg-open', str(saved_file_path)], check=True)
                                
                                st.success(f"✅ 文件已使用默认应用打开：{os.path.basename(saved_file_path)}")
                            except subprocess.CalledProcessError as e:
                                st.warning(f"⚠️ 无法自动打开文件：{str(e)}")
                            except Exception as e:
                                st.warning(f"⚠️ 打开文件时发生错误：{str(e)}")
                    else:
                        st.warning("文件保存路径未知，无法自动打开文件")

                # 提取统计信息
                st.subheader("Extraction Statistics")
                stats_col1, stats_col2, stats_col3 = st.columns(3)

                with stats_col1:
                    st.metric("Characters", len(markdown))

                with stats_col2:
                    st.metric("Words", len(markdown.split()))

                with stats_col3:
                    st.metric("Lines", markdown.count('\n') + 1)
            else:
                st.error("Failed to extract content. Please check the URL and try again.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)
elif submitted:
    st.warning("Please enter a valid URL")

# 添加使用说明
with st.expander("Usage Tips"):
    st.markdown("""
    ### Tips for Better Extraction
    
    1. **Use 'all' scope** for most websites to extract complete content.
    
    2. **Enable page scrolling** to load lazy-loaded content before extraction.
    
    3. **Increase wait time** for complex pages with many dynamic elements.
    
    4. **Remove interfering elements** using CSS selectors to clean up the extraction:
       - Navigation menus: `nav, .navigation, .navbar`
       - Advertisements: `.ads, .ad-container, [class*="ad-"]`
       - Sidebars: `#sidebar, .sidebar, aside`
       - Footers: `footer, .footer`
       - Popups: `.modal, .popup, .overlay`
       
    5. **Adjust viewport height** if the page has unusual layout requirements.
    
    6. **Image Download**: Enable "Download Images to Local" to automatically download images from the webpage. Images will be saved to `static/images/` directory and paths will be updated in the Markdown content.
    
    7. If extraction fails, try opening the page in a regular browser first to ensure it loads properly.
    """)


