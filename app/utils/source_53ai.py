#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
53AI网站文章爬虫
获取53AI网站的所有文章信息
"""

import requests
import pandas as pd
from datetime import datetime
import re
import time
from urllib.parse import urljoin

class Source53AI:
    def __init__(self):
        self.base_url = "https://www.53ai.com"
        self.news_url = "https://www.53ai.com/news.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_news_page(self, page=1):
        """获取新闻页面"""
        try:
            if page == 1:
                url = self.news_url
            else:
                url = f"{self.base_url}/news_{page}.html"
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None
    
    def parse_articles(self, html_content):
        """解析文章列表"""
        articles = []
        
        try:
            # 查找所有文章链接
            link_pattern = r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
            links = re.findall(link_pattern, html_content)
            
            for link_url, link_text in links:
                # 过滤可能的文章链接
                if any(keyword in link_text.lower() for keyword in ['ai', '人工智能', '机器学习', '深度学习', '算法', '技术', '新闻', '资讯']):
                    if not link_url.startswith('http'):
                        link_url = urljoin(self.base_url, link_url)
                    
                    # 检查是否是文章页面
                    if any(keyword in link_url for keyword in ['/news/', '/article/', '/post/', '/content/', '.html']):
                        article_info = {
                            'title': link_text.strip(),
                            'url': link_url,
                            'publish_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': '53AI',
                            'platform': 'website'
                        }
                        articles.append(article_info)
            
        except Exception as e:
            print(f"解析文章失败: {e}")
        
        return articles
    
    def get_article_content(self, article_url):
        """获取文章内容"""
        try:
            response = self.session.get(article_url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            html_content = response.text
            
            # 提取文章内容 - 使用多种模式
            content_patterns = [
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*article-content[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*post-content[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*text[^"]*"[^>]*>(.*?)</div>',
                r'<article[^>]*>(.*?)</article>',
                r'<div[^>]*class="[^"]*main[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*id="[^"]*content[^"]*"[^>]*>(.*?)</div>'
            ]
            
            for pattern in content_patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    content = match.group(1)
                    # 清理HTML标签
                    content = re.sub(r'<[^>]+>', '', content)
                    content = re.sub(r'\s+', ' ', content).strip()
                    if len(content) > 50:
                        return content
            
            # 如果正则表达式失败，尝试提取所有文本内容
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 移除script和style标签
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # 获取文本内容
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                if len(text) > 100:  # 确保内容足够长
                    return text[:1000]  # 限制长度
                    
            except ImportError:
                print("BeautifulSoup未安装，使用备用方法")
            
            return ""
            
        except Exception as e:
            print(f"获取文章内容失败: {e}")
            return ""
    
    def crawl_articles(self, max_pages=5):
        """爬取文章"""
        all_articles = []
        
        print(f"开始爬取53AI网站文章，最多爬取 {max_pages} 页...")
        
        for page in range(1, max_pages + 1):
            print(f"正在爬取第 {page} 页...")
            
            html_content = self.get_news_page(page)
            if not html_content:
                print(f"第 {page} 页获取失败")
                break
            
            articles = self.parse_articles(html_content)
            if not articles:
                print(f"第 {page} 页没有找到文章")
                break
            
            print(f"第 {page} 页找到 {len(articles)} 篇文章")
            
            # 获取文章详情
            for article in articles:
                print(f"  获取文章: {article['title'][:50]}...")
                content = self.get_article_content(article['url'])
                article['content'] = content
                time.sleep(0.5)  # 延迟避免请求过快
            
            all_articles.extend(articles)
            
            if len(articles) < 5:  # 如果文章数量少，可能到最后一页
                break
        
        if all_articles:
            df = pd.DataFrame(all_articles)
            print(f"爬取完成！共获取 {len(df)} 篇文章")
            return df
        else:
            print("没有找到任何文章")
            return pd.DataFrame()
    
    def save_to_csv(self, df, filename=None):
        """保存到CSV"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"53ai_articles_{timestamp}.csv"
        
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"数据已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"保存失败: {e}")
            return ""

def test_single_article():
    """测试单个文章内容提取"""
    print("测试单个文章内容提取...")
    
    crawler = Source53AI()
    
    # 测试一个具体的文章URL
    test_url = "https://www.53ai.com/news/qianyanjishu"
    print(f"测试URL: {test_url}")
    
    content = crawler.get_article_content(test_url)
    if content:
        print(f"内容长度: {len(content)}")
        print(f"内容预览: {content[:200]}...")
    else:
        print("未获取到内容")

def main():
    """主函数"""
    print("53AI网站文章爬虫")
    
    # 先测试单个文章
    test_single_article()
    
    print("\n" + "="*50)
    
    # 然后爬取所有文章
    crawler = Source53AI()
    df = crawler.crawl_articles(5)  # 爬取5页
    
    if not df.empty:
        print("\n爬取结果:")
        print(df.head())
        
        filename = crawler.save_to_csv(df)
        if filename:
            print(f"\n数据已保存到: {filename}")

if __name__ == "__main__":
    main()
