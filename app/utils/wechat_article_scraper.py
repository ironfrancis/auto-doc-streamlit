#!/usr/bin/env python3
"""
微信公众号文章信息自动采集工具
支持从微信公众号文章链接中提取发布信息
"""

import requests
import re
import json
from datetime import datetime
from typing import Dict, Optional, List
import time
from urllib.parse import urlparse, parse_qs
import streamlit as st

class WeChatArticleScraper:
    """微信公众号文章信息采集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_article_id(self, url: str) -> Optional[str]:
        """从URL中提取文章ID"""
        try:
            # 微信公众号文章URL格式：https://mp.weixin.qq.com/s/文章ID
            match = re.search(r'/s/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            print(f"提取文章ID失败: {e}")
            return None
    
    def get_article_info(self, url: str) -> Optional[Dict]:
        """获取文章基本信息"""
        try:
            article_id = self.extract_article_id(url)
            if not article_id:
                return None
            
            # 构建API请求URL
            api_url = f"https://mp.weixin.qq.com/mp/getappmsgext"
            
            params = {
                '__biz': '',  # 需要从页面中提取
                'mid': article_id,
                'sn': '',     # 需要从页面中提取
                'idx': '1',
                'appmsg_type': '9',
                'f': 'json'
            }
            
            response = self.session.get(url)
            if response.status_code == 200:
                # 从页面中提取必要参数
                html_content = response.text
                
                # 提取__biz参数
                biz_match = re.search(r'__biz=([^&]+)', html_content)
                if biz_match:
                    params['__biz'] = biz_match.group(1)
                
                # 提取sn参数
                sn_match = re.search(r'sn=([^&]+)', html_content)
                if sn_match:
                    params['sn'] = sn_match.group(1)
                
                # 尝试获取文章数据
                return self._parse_article_data(html_content, article_id)
            
            return None
            
        except Exception as e:
            print(f"获取文章信息失败: {e}")
            return None
    
    def _parse_article_data(self, html_content: str, article_id: str) -> Dict:
        """解析文章数据"""
        article_info = {
            'id': article_id,
            'url': '',
            'title': '',
            'publish_date': '',
            'publish_time': '',
            'status': 'published',
            'views': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'channel_name': '',
            'tags': []
        }
        
        try:
            # 提取标题
            title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html_content)
            if title_match:
                article_info['title'] = title_match.group(1).strip()
            
            # 提取发布时间
            time_match = re.search(r'var publish_time = "([^"]+)"', html_content)
            if time_match:
                publish_time_str = time_match.group(1)
                try:
                    publish_time = datetime.fromtimestamp(int(publish_time_str))
                    article_info['publish_date'] = publish_time.strftime('%Y-%m-%d')
                    article_info['publish_time'] = publish_time.strftime('%H:%M')
                except:
                    pass
            
            # 提取公众号名称
            account_match = re.search(r'var nickname = "([^"]+)"', html_content)
            if account_match:
                article_info['channel_name'] = account_match.group(1)
            
            # 提取阅读量等信息（需要特殊处理）
            # 注意：微信公众号的阅读量等数据需要特殊权限才能获取
            
        except Exception as e:
            print(f"解析文章数据失败: {e}")
        
        return article_info
    
    def scrape_from_url(self, url: str) -> Optional[Dict]:
        """从URL直接采集文章信息"""
        try:
            # 验证URL格式
            if not url.startswith('https://mp.weixin.qq.com/s/'):
                return None
            
            article_info = self.get_article_info(url)
            if article_info:
                article_info['url'] = url
                return article_info
            
            return None
            
        except Exception as e:
            print(f"URL采集失败: {e}")
            return None

class WeChatDataCollector:
    """微信公众号数据采集器"""
    
    def __init__(self, data_collector):
        self.scraper = WeChatArticleScraper()
        self.data_collector = data_collector
    
    def add_article_from_url(self, url: str, channel_name: str = None) -> bool:
        """从URL添加文章"""
        try:
            article_info = self.scraper.scrape_from_url(url)
            if not article_info:
                return False
            
            # 如果提供了频道名称，使用提供的名称
            if channel_name:
                article_info['channel_name'] = channel_name
            
            # 如果没有频道名称，使用默认名称
            if not article_info['channel_name']:
                article_info['channel_name'] = '未知公众号'
            
            # 添加到数据采集器
            self.data_collector.add_publish_record(
                article_info['channel_name'], 
                article_info
            )
            
            return True
            
        except Exception as e:
            print(f"添加文章失败: {e}")
            return False
    
    def batch_add_articles(self, urls: List[str], channel_name: str = None) -> Dict:
        """批量添加文章"""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for url in urls:
            try:
                if self.add_article_from_url(url, channel_name):
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"失败: {url}")
                
                # 添加延迟避免请求过快
                time.sleep(1)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"错误: {url} - {str(e)}")
        
        return results

def create_manual_entry_form():
    """创建手动录入表单"""
    st.subheader("📝 手动录入文章信息")
    
    with st.form("manual_article_form"):
        url = st.text_input("文章链接", placeholder="https://mp.weixin.qq.com/s/...")
        channel_name = st.text_input("公众号名称", placeholder="请输入公众号名称")
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("文章标题")
            publish_date = st.date_input("发布日期", value=datetime.now().date())
        with col2:
            publish_time = st.time_input("发布时间", value=datetime.now().time())
            status = st.selectbox("状态", ["published", "draft", "scheduled"])
        
        col1, col2 = st.columns(2)
        with col1:
            views = st.number_input("阅读量", min_value=0, value=0)
            likes = st.number_input("点赞数", min_value=0, value=0)
        with col2:
            comments = st.number_input("评论数", min_value=0, value=0)
            shares = st.number_input("分享数", min_value=0, value=0)
        
        tags_input = st.text_input("标签", placeholder="用逗号分隔，如: AI,技术,新闻")
        
        if st.form_submit_button("添加文章"):
            if title.strip() and channel_name.strip():
                tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                
                article_info = {
                    'title': title.strip(),
                    'publish_date': publish_date.strftime('%Y-%m-%d'),
                    'publish_time': publish_time.strftime('%H:%M'),
                    'status': status,
                    'views': views,
                    'likes': likes,
                    'comments': comments,
                    'shares': shares,
                    'url': url.strip(),
                    'tags': tags
                }
                
                return channel_name.strip(), article_info
            
            else:
                st.error("请填写文章标题和公众号名称")
                return None, None
    
    return None, None

def main():
    """主函数 - 测试采集功能"""
    from app.utils.data_collector import ChannelDataCollector
    
    collector = ChannelDataCollector()
    wechat_collector = WeChatDataCollector(collector)
    
    # 测试URL
    test_url = "https://mp.weixin.qq.com/s/YEEgiKCu2YMUls7QFJ24EQ"
    
    print("🧪 测试微信公众号文章采集")
    print("=" * 50)
    
    # 尝试采集文章信息
    article_info = wechat_collector.scraper.scrape_from_url(test_url)
    
    if article_info:
        print("✅ 文章信息采集成功:")
        for key, value in article_info.items():
            print(f"  {key}: {value}")
    else:
        print("❌ 文章信息采集失败")
        print("💡 可能的原因:")
        print("  1. 文章需要验证才能访问")
        print("  2. 网络连接问题")
        print("  3. 微信公众号反爬虫机制")
        print("  4. 需要登录或特殊权限")

if __name__ == "__main__":
    main() 