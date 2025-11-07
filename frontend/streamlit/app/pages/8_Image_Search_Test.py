import sys
import os

# 使用简化路径管理
from scripts.utils.simple_paths import *

import streamlit as st
from core.utils.language_manager import init_language, get_text
import requests
import json
import time
from typing import List, Dict
import pandas as pd
from PIL import Image
import io
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

T = {
    "zh": {
        "page_title": "图片搜索API测试",
        "search_placeholder": "输入搜索关键词...",
        "search_button": "搜索图片",
        "api_comparison": "API对比",
        "results_count": "结果数量",
        "download_image": "下载",
        "preview_image": "预览",
        "no_results": "未找到结果",
        "search_error": "搜索错误",
        "loading": "搜索中...",
        "api_status": "API状态",
        "response_time": "响应时间",
        "image_quality": "图片质量",
        "copyright_info": "版权信息",
    }
}

class ImageSearchTester:
    """图片搜索API测试类（仅支持Unsplash）"""
    
    def __init__(self):
        # 使用真实的Unsplash API密钥
        self.unsplash_access_key = "K15fQ88g2F5n-OAIZ0ZxInaqCZsMsXLm8H0mUftKVbw"
    
    def search_unsplash(self, query: str, count: int = 10) -> Dict:
        """使用Unsplash API搜索图片"""
        try:
            start_time = time.time()
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": count,
                "client_id": self.unsplash_access_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for photo in data.get("results", []):
                    results.append({
                        "id": photo["id"],
                        "url": photo["urls"]["regular"],
                        "thumb": photo["urls"]["thumb"],
                        "alt": photo.get("alt_description", ""),
                        "author": photo["user"]["name"],
                        "source": "unsplash",
                        "width": photo["width"],
                        "height": photo["height"],
                        "likes": photo.get("likes", 0)
                    })
                
                return {
                    "success": True,
                    "results": results,
                    "response_time": response_time,
                    "total_results": len(results),
                    "mock": False
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "response_time": response_time,
                    "results": []
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response_time": 0,
                "results": []
            }
    
    def search(self, query: str, count: int = 10) -> Dict:
        """搜索Unsplash API"""
        st.write(f"正在搜索 Unsplash...")
        result = self.search_unsplash(query, count)
        
        # 显示结果
        if result["success"]:
            st.success(f"Unsplash: 找到 {len(result['results'])} 张图片")
        else:
            st.error(f"Unsplash: {result['error']}")
        
        return result

def main():
    # 语言设置
        
    # 初始化搜索结果状态
    if "search_results" not in st.session_state:
        st.session_state["search_results"] = None
    if "last_search_query" not in st.session_state:
        st.session_state["last_search_query"] = ""
    
        
        
    st.set_page_config(page_title="图片搜索测试", layout="wide")
    
    # 加载主题
    load_anthropic_theme()
    
    st.title(get_text("page_title"))
    st.markdown("---")
    
    # 初始化搜索器
    searcher = ImageSearchTester()
    
    # 搜索界面
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input(
            get_text("search_placeholder"),
            value="artificial intelligence",
            key="search_query"
        )
    
    with col2:
        result_count = st.number_input(
            "每API结果数",
            min_value=1,
            max_value=20,
            value=5,
            key="result_count"
        )
    
    with col3:
        search_button = st.button(get_text("search_button"), type="primary")
    
    # 添加清除结果按钮
    if st.session_state["search_results"] is not None:
        if st.button(f"清除结果", key="clear_results"):
            st.session_state["search_results"] = None
            st.session_state["last_search_query"] = ""
            st.rerun()
    
    # 执行搜索
    if search_button and search_query:
        # 搜索所有API
        with st.spinner(get_text("loading")):
            all_results = searcher.search(search_query, result_count)
        
        # 保存搜索结果到session_state
        st.session_state["search_results"] = all_results
        st.session_state["last_search_query"] = search_query
    
    # 显示搜索结果（从session_state中获取）
    if st.session_state["search_results"] is not None:
        all_results = st.session_state["search_results"]
        
        st.markdown("### 📊 " + get_text("api_comparison"))
        
        # 显示API对比表格
        comparison_data = []
        if all_results["success"]:
            comparison_data.append({
                "API": "Unsplash",
                get_text("results_count"): all_results["total_results"],
                get_text("response_time"): f"{all_results['response_time']:.2f}s",
                get_text("api_status"): f"成功"
            })
        else:
            comparison_data.append({
                "API": "Unsplash",
                get_text("results_count"): 0,
                get_text("response_time"): f"{all_results['response_time']:.2f}s",
                get_text("api_status"): f"{all_results['error']}"
            })
        
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
        
        # 显示搜索结果
        st.markdown("### 🖼️ 搜索结果")
        
        if all_results["success"] and all_results["results"]:
            with st.expander(f"Unsplash ({len(all_results['results'])} 张图片)", expanded=True):
                # 创建网格布局
                cols = st.columns(3)
                
                for i, image_data in enumerate(all_results["results"]):
                    col_idx = i % 3
                    
                    with cols[col_idx]:
                        st.markdown(f"**{image_data['alt'][:30]}...**")
                        
                        # 显示缩略图
                        try:
                            response = requests.get(image_data["thumb"], timeout=30)
                            if response.status_code == 200:
                                image = Image.open(io.BytesIO(response.content))
                                st.image(image, caption=f"作者: {image_data['author']}", use_container_width=True)
                            else:
                                st.error("无法加载图片")
                        except Exception as e:
                            st.error(f"图片加载失败: {str(e)}")
                        
                        # 图片信息
                        st.caption(f"尺寸: {image_data['width']}x{image_data['height']}")
                        if image_data.get('likes'):
                            st.caption(f"点赞: {image_data['likes']}")
                        
                        # 操作按钮
                        col_prev, col_next = st.columns(2)
                        with col_prev:
                            # 使用链接而不是按钮来避免状态问题
                            st.markdown(f"[👁️ 预览]({image_data['url']})")
                        
                        with col_next:
                            download_key = f"download_unsplash_{i}"
                            if st.button(f"下载", key=download_key):
                                # 下载图片
                                try:
                                    with st.spinner("正在下载图片..."):
                                        response = requests.get(image_data["url"], timeout=30)
                                        if response.status_code == 200:
                                            # 保存到本地
                                            os.makedirs("downloaded_images", exist_ok=True)
                                            filename = f"unsplash_{image_data['id']}.jpg"
                                            filepath = os.path.join("downloaded_images", filename)
                                            
                                            with open(filepath, 'wb') as f:
                                                f.write(response.content)
                                            
                                            st.success(f"已下载: {filename}")
                                        else:
                                            st.error("下载失败")
                                except Exception as e:
                                    st.error(f"下载错误: {str(e)}")
                        
                        st.markdown("---")
        

    
    # 侧边栏信息
    with st.sidebar:
        st.markdown("### 📋 API信息")
        st.markdown("""
        **当前仅支持Unsplash API**
        - **Unsplash**: 高质量免费图片
        
        **当前状态:** 使用真实API
        """)
        
        st.markdown("### 🔑 API密钥")
        st.markdown("""
        **已配置Unsplash API密钥**
        - 密钥状态: ✅ 已配置
        """)
        
        st.markdown("### 💡 使用建议")
        st.markdown("""
        1. 输入英文关键词效果更好
        2. 可以尝试不同的关键词组合
        3. 点击图片链接可查看原图
        4. 下载前检查图片版权信息
        """)

if __name__ == "__main__":
    main() 