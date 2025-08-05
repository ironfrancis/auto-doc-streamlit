import markdown
from jinja2 import Environment, FileSystemLoader
import os
import re
import shutil
import requests
import base64
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import hashlib
import time

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'html_templates')

# 常用class到style的映射（可扩展）
CLASS_STYLE_MAP = {
    "magic-list-item": "margin-bottom:6px;position:relative;padding-left:15px;display:block;padding-right:5px;",
    "magic-article-container": "max-width:700px;margin:0 auto;background-color:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,102,255,0.1);padding:30px;",
    "magic-indent-level-1": "padding-left:25px;position:relative;margin-bottom:6px;padding-right:5px;",
    "magic-indent-level-2": "padding-left:40px;position:relative;margin-bottom:6px;padding-right:5px;",
    "magic-article-h2-section-title": "position:relative;color:#0066FF;font-size:22px;line-height:1.4;margin-top:36px;margin-bottom:16px;padding:8px 0 8px 16px;font-weight:700;border-left:5px solid #0066FF;background-color:rgba(0,102,255,0.05);border-radius:0 6px 6px 0;padding-left:16px;display:flex;align-items:center;",
    "magic-article-h3-custom": "position:relative;color:#00A3FF;font-size:19px;font-weight:700;margin-top:22px;margin-bottom:6px;padding:4px 0;letter-spacing:0.01em;display:block;border-bottom:2px solid rgba(0,163,255,0.15);",
    # ...可继续补充...
}

def convert_class_to_inline_style(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        if tag.has_attr("class"):
            styles = []
            for cls in tag["class"]:
                if cls in CLASS_STYLE_MAP:
                    styles.append(CLASS_STYLE_MAP[cls])
            # 合并原有style
            if tag.has_attr("style"):
                styles.insert(0, tag["style"])
            if styles:
                tag["style"] = ";".join(styles)
            del tag["class"]
    return str(soup)

def image_to_base64(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        # 获取文件扩展名来确定MIME类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"转换图片为base64失败 {image_path}: {str(e)}")
        return None

def convert_images_to_base64(html_content, static_dir="app/static"):
    """将HTML中的图片路径转换为base64编码"""
    import re
    
    # 获取静态目录的绝对路径
    static_abs_path = os.path.abspath(static_dir)
    images_dir = os.path.join(static_abs_path, "images")
    
    # 匹配HTML中的img标签
    img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
    
    def replace_img_src(match):
        img_tag = match.group(0)
        src_path = match.group(1)
        
        # 检查是否是Web路径（/static/images/...）
        if src_path.startswith('/static/images/'):
            # 构建完整的文件路径
            relative_path = src_path.replace('/static/', '')
            full_path = os.path.join(static_abs_path, relative_path)
            
            if os.path.exists(full_path):
                # 转换为base64
                base64_data = image_to_base64(full_path)
                if base64_data:
                    # 替换src属性
                    new_img_tag = re.sub(r'src=["\'][^"\']+["\']', f'src="{base64_data}"', img_tag)
                    return new_img_tag
        
        # 如果不是我们的路径或转换失败，保持不变
        return img_tag
    
    # 替换所有图片路径
    processed_html = re.sub(img_pattern, replace_img_src, html_content)
    return processed_html

def download_image(url, save_dir):
    """下载网络图片到本地"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # 从URL或响应头获取文件扩展名
        content_type = response.headers.get('content-type', '')
        if 'image/' in content_type:
            ext = content_type.split('/')[-1].split(';')[0]
            if ext == 'jpeg':
                ext = 'jpg'
        else:
            # 从URL获取扩展名
            parsed_url = urlparse(url)
            ext = os.path.splitext(parsed_url.path)[1]
            if not ext:
                ext = '.jpg'  # 默认扩展名
        
        # 生成唯一文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        timestamp = int(time.time())
        filename = f"img_{timestamp}_{url_hash}{ext}"
        
        # 确保文件名唯一
        base_name, ext_name = os.path.splitext(filename)
        counter = 1
        final_filename = filename
        while os.path.exists(os.path.join(save_dir, final_filename)):
            final_filename = f"{base_name}_{counter}{ext_name}"
            counter += 1
        
        # 保存图片
        file_path = os.path.join(save_dir, final_filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return final_filename, file_path
        
    except Exception as e:
        print(f"下载图片失败 {url}: {str(e)}")
        return None, None

def process_images(md_text, static_dir="app/static"):
    """处理图片路径，包括本地图片复制和网络图片下载"""
    # 创建静态图片目录
    images_dir = os.path.join(static_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # 匹配Markdown图片语法
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # 检查是否是网络图片
        if image_path.startswith(('http://', 'https://')):
            try:
                # 下载网络图片
                filename, file_path = download_image(image_path, images_dir)
                if filename:
                    # 返回绝对路径
                    new_path = os.path.abspath(os.path.join(images_dir, filename))
                    return f'![{alt_text}]({new_path})'
                else:
                    # 下载失败，保持原URL并添加警告
                    return f'![{alt_text}]({image_path}) <!-- 图片下载失败: {image_path} -->'
            except Exception as e:
                # 如果处理失败，保持原路径
                return f'![{alt_text}]({image_path}) <!-- 图片处理失败: {str(e)} -->'
        
        # 检查是否是本地路径
        elif os.path.isabs(image_path) or (not image_path.startswith('http') and not image_path.startswith('/')):
            try:
                # 如果是绝对路径，直接使用
                if os.path.isabs(image_path):
                    source_path = image_path
                else:
                    # 如果是相对路径，尝试在当前目录查找
                    source_path = os.path.abspath(image_path)
                
                if os.path.exists(source_path):
                    # 生成新的文件名
                    filename = os.path.basename(source_path)
                    # 确保文件名唯一
                    base_name, ext = os.path.splitext(filename)
                    counter = 1
                    new_filename = filename
                    while os.path.exists(os.path.join(images_dir, new_filename)):
                        new_filename = f"{base_name}_{counter}{ext}"
                        counter += 1
                    
                    # 复制图片到静态目录
                    dest_path = os.path.join(images_dir, new_filename)
                    shutil.copy2(source_path, dest_path)
                    
                    # 返回绝对路径
                    new_path = os.path.abspath(dest_path)
                    return f'![{alt_text}]({new_path})'
                else:
                    # 如果文件不存在，保持原路径并添加警告
                    return f'![{alt_text}]({image_path}) <!-- 图片文件不存在: {image_path} -->'
            except Exception as e:
                # 如果处理失败，保持原路径
                return f'![{alt_text}]({image_path}) <!-- 图片处理失败: {str(e)} -->'
        else:
            # 如果是已经是静态路径，保持不变
            return match.group(0)
    
    # 替换所有图片路径
    processed_md = re.sub(image_pattern, replace_image, md_text)
    return processed_md

def convert_absolute_paths_to_web_paths(html_content, static_dir="app/static"):
    """将HTML中的绝对路径图片转换为Web可访问的路径"""
    import re
    
    # 获取静态目录的绝对路径
    static_abs_path = os.path.abspath(static_dir)
    images_dir = os.path.join(static_abs_path, "images")
    
    # 匹配HTML中的img标签（更宽松的匹配）
    img_pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
    
    def replace_img_src(match):
        img_tag = match.group(0)
        src_path = match.group(1)
        
        # 检查是否是绝对路径且指向我们的静态目录
        if os.path.isabs(src_path) and src_path.startswith(static_abs_path):
            # 计算相对于静态目录的路径
            relative_path = os.path.relpath(src_path, static_abs_path)
            # 转换为Web路径
            web_path = f"/static/{relative_path}"
            # 替换src属性
            new_img_tag = re.sub(r'src=["\'][^"\']+["\']', f'src="{web_path}"', img_tag)
            return new_img_tag
        else:
            # 如果不是我们的绝对路径，保持不变
            return img_tag
    
    # 替换所有图片路径
    processed_html = re.sub(img_pattern, replace_img_src, html_content)
    
    # 也处理Markdown转换后的其他可能的图片引用格式
    # 处理可能的注释中的绝对路径
    comment_pattern = r'<!--\s*图片文件不存在:\s*([^>]+)\s*-->'
    
    def replace_comment_path(match):
        comment = match.group(0)
        path = match.group(1)
        
        # 检查是否是绝对路径且指向我们的静态目录
        if os.path.isabs(path) and path.startswith(static_abs_path):
            # 计算相对于静态目录的路径
            relative_path = os.path.relpath(path, static_abs_path)
            # 转换为Web路径
            web_path = f"/static/{relative_path}"
            # 替换注释中的路径
            new_comment = comment.replace(path, web_path)
            return new_comment
        else:
            return comment
    
    # 替换注释中的路径
    processed_html = re.sub(comment_pattern, replace_comment_path, processed_html)
    
    return processed_html

def md_to_html(md_text: str, template_name: str = 'wepub.html', static_dir: str = "app/static", **kwargs) -> str:
    # 处理图片（包括本地和网络图片）
    processed_md = process_images(md_text, static_dir)
    
    # 转换为HTML
    html_body = markdown.markdown(processed_md, extensions=['extra', 'codehilite'])
    
    # 使用模板渲染
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    html = template.render(content=html_body, **kwargs)
    
    # 转换class到inline style
    html = convert_class_to_inline_style(html)
    
    # 处理HTML中的绝对路径图片
    html = convert_absolute_paths_to_web_paths(html, static_dir)
    
    # 将图片转换为base64编码（用于Streamlit HTML组件）
    html = convert_images_to_base64(html, static_dir)
    
    return html 