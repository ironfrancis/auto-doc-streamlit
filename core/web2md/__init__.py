"""
Web2MD包 - 网页转Markdown功能
"""

from .enhanced_web2md import extract_markdown_from_url
from .web2md import extract_markdown_from_url as extract_markdown_from_url_basic
from .gzh_url2md import fetch_and_convert_to_md

__all__ = [
    'extract_markdown_from_url',
    'extract_markdown_from_url_basic', 
    'fetch_and_convert_to_md'
]
