

import requests

def get_juejin_article():
    url = "https://aicoding.juejin.cn/post/7535487304314568738"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.text

def extract_article_info(html_content):
    """
    从掘金文章HTML中提取关键信息
    返回包含标题、作者、发布时间、阅读量等信息的字典
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取文章标题
    title = soup.find('h1', class_='article-title').get_text(strip=True)

    # 提取作者信息
    author = soup.find('span', class_='name').get_text(strip=True)

    # 提取发布时间
    publish_time = soup.find('time', class_='time').get_text(strip=True)

    # 提取阅读量
    read_count = soup.find('span', class_='views-count').get_text(strip=True)

    # 提取阅读时长
    read_time = soup.find('span', class_='read-time').get_text(strip=True)

    # 提取文章内容摘要（添加None检查）
    meta_description = soup.find('meta', itemprop='description')
    abstract = meta_description['content'] if meta_description else None

    # 提取文章标签
    tags = [tag.get_text(strip=True) for tag in soup.select('.tag-list-box .tag')]

    return {
        'title': title,
        'author': author,
        'publish_time': publish_time,
        'read_count': read_count,
        'read_time': read_time,
        'abstract': abstract,
        'tags': tags
    }

from playwright.sync_api import sync_playwright

def get_juejin_article_with_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://aicoding.juejin.cn/post/7535487304314568738")

        # 等待阅读量元素加载
        page.wait_for_selector('.view-count')

        # 获取实际阅读量
        view_count = page.inner_text('.view-count')

        browser.close()
        return view_count

if __name__ == "__main__":
    # result = get_juejin_article()
    # print(result)
    # print(extract_article_info(result))
    print(get_juejin_article_with_playwright())
