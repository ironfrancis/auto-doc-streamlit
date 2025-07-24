import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os

def get_project_root() -> Path:
    """获取项目根目录的路径"""
    # 当前文件的目录
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    # 项目根目录（当前文件的父目录）
    project_root = current_dir.parent
    return project_root

def fetch_wechat_article(url: str) -> str:
    # 占位：实际需处理反爬、登录等
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    # 公众号正文一般在id="js_content"
    content = soup.find(id="js_content")
    return content.get_text() if content else "" 