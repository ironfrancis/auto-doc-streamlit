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

# 动态确定模板目录路径
_current_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_current_dir)
TEMPLATE_DIR = os.path.join(_app_dir, '..', 'static', 'templates')

# 如果static/templates不存在，则使用根目录的static/templates
if not os.path.exists(TEMPLATE_DIR):
    TEMPLATE_DIR = os.path.join(_app_dir, '..', '..', 'static', 'templates')
    if not os.path.exists(TEMPLATE_DIR):
        # 如果都找不到，使用当前目录下的static/templates
        TEMPLATE_DIR = os.path.join(_current_dir, 'static', 'templates')

# 常用class到style的映射（可扩展）
CLASS_STYLE_MAP = {
    # 基础容器样式
    "magic-article-container": "max-width:700px;margin:0 auto;background-color:#fff;border-radius:12px;box-shadow:0 4px 20px rgba(0,102,255,0.1);padding:30px;",
    "magic-article-header": "text-align:center;margin-bottom:24px;",
    "magic-article-main-title": "font-size:26px;color:#0066FF;text-align:center;margin-top:30px;margin-bottom:24px;font-weight:700;letter-spacing:-0.01em;line-height:1.3;",
    "magic-article-meta": "color:#5A6B7D;font-size:14px;text-align:center;margin-bottom:30px;",
    
    # 标题样式
    "magic-article-h2-section-title": "position:relative;color:#0066FF;font-size:22px;line-height:1.4;margin-top:36px;margin-bottom:16px;padding:8px 0 8px 16px;font-weight:700;border-left:5px solid #0066FF;background-color:rgba(0,102,255,0.05);border-radius:0 6px 6px 0;padding-left:16px;display:flex;align-items:center;",
    "magic-article-h3-custom": "position:relative;color:#00A3FF;font-size:19px;font-weight:700;margin-top:22px;margin-bottom:6px;padding:4px 0;letter-spacing:0.01em;display:block;border-bottom:2px solid rgba(0,163,255,0.15);",
    
    # 列表样式
    "magic-list-item": "margin-bottom:6px;position:relative;padding-left:15px;display:block;padding-right:5px;",
    "magic-indent-level-1": "padding-left:25px;position:relative;margin-bottom:6px;padding-right:5px;",
    "magic-indent-level-2": "padding-left:40px;position:relative;margin-bottom:6px;padding-right:5px;",
    "magic-list-item-number": "margin-bottom:14px;position:relative;padding-left:25px;display:block;",
    "magic-list-item-main": "margin-bottom:14px;position:relative;padding-left:15px;list-style-type:none;",
    "magic-list-item-req": "margin-bottom:14px;position:relative;padding-left:20px;list-style-type:none;",
    "magic-list-item-guide": "margin-bottom:18px;position:relative;padding-left:20px;list-style-type:none;",
    "magic-list-item-nested": "margin-top:10px;margin-bottom:10px;",
    "magic-article-list-main": "padding-left:20px;color:#1A2332;line-height:1.8;",
    "magic-article-sublist": "padding-left:20px;margin-top:10px;",
    "magic-article-sublist-item": "margin-bottom:10px;position:relative;padding-left:20px;list-style-type:none;",
    
    # 自定义项目符号
    "magic-article-custom-bullet-square": "position:absolute;left:0;top:9px;width:8px;height:8px;background:linear-gradient(135deg,#0066FF,#00A3FF);border-radius:2px;transform:rotate(45deg);display:inline-block;margin-right:8px;",
    "magic-article-custom-bullet-circle": "position:absolute;left:0;top:9px;width:7px;height:7px;background:linear-gradient(135deg,#0066FF,#00A3FF);border-radius:50%;display:inline-block;margin-right:8px;",
    
    # 代码块样式
    "magic-code-table": "width:100%;margin:20px 0;border-collapse:collapse;border:none;background-color:#F0F6FF;border-radius:8px;overflow:hidden;box-shadow:0 3px 10px rgba(0,102,255,0.1);",
    "magic-code-header": "background:linear-gradient(135deg,#0066FF,#00A3FF);color:white;padding:8px 14px;font-size:13px;text-align:left;font-weight:normal;",
    "magic-code-header-icon": "display:inline;margin-right:0;font-weight:bold;white-space:nowrap;",
    "magic-code-copy-tip": "float:right;font-size:10px;font-weight:normal;line-height:2;color:rgba(255,255,255,0.85);",
    "magic-code-content": "font-family:SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;font-size:14px;color:#1A2332;line-height:0.2;padding:14px 18px;white-space:pre-wrap;word-break:break-word;word-wrap:break-word;background-color:#F0F6FF;overflow-x:auto;position:relative;",
    
    # 代码高亮样式
    "code-keyword": "color:#d73a49;font-weight:bold;",
    "code-comment": "color:#6a737d;font-style:italic;",
    "code-string": "color:#032f62;",
    "code-function": "color:#6f42c1;",
    "code-variable": "color:#e36209;",
    "code-number": "color:#005cc5;",
    "code-command": "color:#bc0000;font-weight:bold;",
    "code-tag": "color:#22863a;",
    "code-attribute": "color:#6f42c1;",
    "code-parameter": "color:#2d21b2;",
    "code-option": "color:#7d1f1f;",
    
    # 链接样式
    "magic-link": "color:#00A3FF;text-decoration:none;transition:all 0.2s ease;border-bottom:1px dotted #00A3FF;padding-bottom:1px;cursor:default;font-weight:500;",
    
    # 提示框样式
    "magic-article-script-tip": "color:#5A6B7D;font-size:14px;margin-top:8px;background-color:#F7FAFF;padding:8px 12px;border-radius:1px;border-left:3px solid #00A3FF;",
    
    # 分隔线样式
    "magic-article-divider-large-margin": "margin:32px 0;height:1px;background:linear-gradient(90deg,transparent,rgba(227,242,253,1) 15%,rgba(227,242,253,1) 85%,transparent);border:none;",
    
    # 其他样式
    "mac-window-buttons": "height:13px;width:43px;vertical-align:middle;margin-right:6px;margin-bottom:3px;position:relative;top:-1px;",
    "bullet-with-text": "display:inline-block;width:100%;white-space:normal;position:relative;padding-left:20px;",
    
    # 原有的列表相关样式
    "enhanced-list": "margin: 20px 0; padding: 0;",
    "unordered-list": "list-style-type: disc; margin-left: 20px;",
    "ordered-list": "list-style-type: decimal; margin-left: 20px;",
    "list-item": "margin-bottom: 6px; line-height: 1.6; padding-left: 8px;",
    
    # 表格相关样式
    "enhanced-table": "border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px;",
    "table-header": "background-color: #f6f8fa; font-weight: bold; border: 1px solid #ddd; padding: 12px 8px; text-align: left;",
    "table-cell": "border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top;",
    "table-row": "border-bottom: 1px solid #eee;",
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

def convert_class_to_inline_style_preserve_code(html):
    """转换class到inline style，但保留代码高亮相关的类"""
    soup = BeautifulSoup(html, "html.parser")
    
    # 代码高亮相关的类名（这些类需要保留）
    code_highlight_classes = {
        'highlight', 'codehilite', 'highlighttable', 'linenodiv', 'linenos',
        'hljs', 'python', 'javascript', 'html', 'css', 'bash', 'shell',
        'json', 'yaml', 'xml', 'sql', 'java', 'cpp', 'c', 'go', 'rust',
        'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'matlab',
        'code-block'  # 我们添加的自定义类
    }
    
    # 列表相关的类名（这些类需要保留）
    list_classes = {
        'enhanced-list', 'unordered-list', 'ordered-list', 'list-item'
    }
    
    # 表格相关的类名（这些类需要保留）
    table_classes = {
        'enhanced-table', 'table-header', 'table-cell', 'table-row'
    }
    
    # Pygments语法高亮类（所有单字母和双字母的类）
    pygments_classes = {
        # 基本语法元素
        'k', 'kc', 'kd', 'kn', 'kp', 'kr', 'kt',  # 关键字
        's', 's1', 's2', 'sa', 'sb', 'sc', 'sd', 'se', 'sh', 'si', 'sx', 'sr', 'ss',  # 字符串
        'c', 'c1', 'ch', 'cm', 'cp', 'cpf', 'cs',  # 注释
        'n', 'na', 'nb', 'nc', 'nd', 'ne', 'nf', 'ni', 'nl', 'nn', 'no', 'nt', 'nv', 'nx',  # 名称
        'o', 'ow',  # 操作符
        'm', 'mb', 'mf', 'mh', 'mi', 'mo',  # 数字
        'p',  # 标点
        'w',  # 空白
        'err',  # 错误
        'hll',  # 高亮行
        'g', 'gd', 'ge', 'gr', 'gh', 'gi', 'go', 'gp', 'gs', 'gu', 'gt',  # 通用
        'bp', 'fm', 'vc', 'vg', 'vi', 'vm',  # 变量
        'py', 'dl',  # Python特定
        # 更多类...
        'keyword', 'string', 'comment', 'name', 'operator', 'number', 'punctuation',
        'builtin', 'decorator', 'entity', 'exception', 'function', 'label', 
        'namespace', 'property', 'tag', 'variable'
    }
    
    # 合并所有需要保留的类
    preserved_class_names = code_highlight_classes | pygments_classes | list_classes | table_classes
    
    for tag in soup.find_all(True):
        if tag.has_attr("class"):
            styles = []
            preserved_classes = []
            
            for cls in tag["class"]:
                if cls in CLASS_STYLE_MAP:
                    # 应用我们的自定义样式
                    styles.append(CLASS_STYLE_MAP[cls])
                    # 如果是H标签相关的类，也要保留
                    if cls.startswith('magic-article-h'):
                        preserved_classes.append(cls)
                elif cls in preserved_class_names:
                    # 保留代码高亮相关的类
                    preserved_classes.append(cls)
                # 其他类会被移除
            
            # 合并原有style
            if tag.has_attr("style"):
                styles.insert(0, tag["style"])
            
            # 设置样式
            if styles:
                tag["style"] = ";".join(styles)
            
            # 更新class属性
            if preserved_classes:
                tag["class"] = preserved_classes
            else:
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

def fix_pseudo_list_format(md_text):
    """修复伪列表格式，将 '内容*：' 格式转换为正确的Markdown列表"""
    import re
    
    # 保护代码块中的内容
    code_blocks = []
    def preserve_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # 保护围栏代码块和行内代码
    md_text = re.sub(r'```[\s\S]*?```', preserve_code_block, md_text)
    md_text = re.sub(r'`[^`]*?`', preserve_code_block, md_text)
    
    # 识别和转换伪列表格式
    # 匹配模式：行开头的文字 + * + ：（可能有空格）
    # 例如：模板化内容管理*：xxx
    lines = md_text.split('\n')
    processed_lines = []
    
    for line in lines:
        # 跳过已经是正确列表格式的行
        if re.match(r'^\s*[\*\+\-]\s', line):
            processed_lines.append(line)
            continue
            
        # 跳过标题行
        if re.match(r'^\s*#{1,6}\s', line):
            processed_lines.append(line)
            continue
        
        # 跳过空行
        if not line.strip():
            processed_lines.append(line)
            continue
        
        # 检查是否是伪列表格式：文字*：内容
        pseudo_list_match = re.match(r'^([^*]+)\*：(.+)$', line.strip())
        if pseudo_list_match:
            title = pseudo_list_match.group(1).strip()
            content = pseudo_list_match.group(2).strip()
            # 转换为正确的列表格式
            new_line = f"- **{title}**：{content}"
            processed_lines.append(new_line)
            continue
        
        # 检查是否是其他伪列表格式：文字*。
        pseudo_list_end_match = re.match(r'^([^*]+)\*([。！？\.!?])?\s*$', line.strip())
        if pseudo_list_end_match:
            title = pseudo_list_end_match.group(1).strip()
            end_char = pseudo_list_end_match.group(2) or ''
            # 转换为正确的列表格式
            new_line = f"- **{title}**{end_char}"
            processed_lines.append(new_line)
            continue
        
        # 其他情况保持不变
        processed_lines.append(line)
    
    md_text = '\n'.join(processed_lines)
    
    # 恢复代码块
    for i, code_block in enumerate(code_blocks):
        md_text = md_text.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return md_text

def clean_orphaned_asterisks(md_text):
    """清理孤立和不配对的星号，避免在HTML中显示意外的*符号

    这个函数现在更加保守，只处理明显的错误情况：
    1. 行尾的孤立星号
    2. 句子中间完全孤立的单星号（前后都有空格）
    3. 不配对的双星号
    """
    import re

    # 保护代码块中的内容
    code_blocks = []
    def preserve_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"

    # 保护围栏代码块和行内代码
    md_text = re.sub(r'```[\s\S]*?```', preserve_code_block, md_text)
    md_text = re.sub(r'`[^`]*`', preserve_code_block, md_text)

    # 1. 清理行尾的孤立星号（通常是转换错误）
    md_text = re.sub(r'\s+\*\s*$', '', md_text, flags=re.MULTILINE)

    # 2. 清理句子中间的孤立单星号（前后都有空格，且不是Markdown语法的一部分）
    # 注意：这个模式不会匹配像 "word*word" 或 "*word*" 这样的有效语法
    md_text = re.sub(r'(?<=\w)\s+\*\s+(?=\w)', ' ', md_text)

    # 3. 清理句子开头的孤立星号（不是列表标记，且后面有空格）
    md_text = re.sub(r'^([^*\s].*?)\s+\*\s+', r'\1 ', md_text, flags=re.MULTILINE)

    # 4. 处理不配对的双星号和单星号（只在明显错误的情况下）
    lines = md_text.split('\n')
    cleaned_lines = []

    for line in lines:
        # 跳过列表行和标题行
        if re.match(r'^\s*[\*\+\-]\s', line) or re.match(r'^\s*#{1,6}\s', line):
            cleaned_lines.append(line)
            continue

        # 计算单星号和双星号的数量
        single_asterisks = []
        double_asterisks = []
        i = 0
        while i < len(line):
            if line[i] == '*':
                if i + 1 < len(line) and line[i + 1] == '*':
                    double_asterisks.append(i)
                    i += 2
                else:
                    single_asterisks.append(i)
                    i += 1
            else:
                i += 1

        # 处理不配对的双星号（奇数个**）
        if len(double_asterisks) % 2 == 1:
            # 移除最后一个不配对的**
            last_double_pos = double_asterisks[-1]
            line = line[:last_double_pos] + line[last_double_pos + 2:]

        # 处理不配对的单星号（奇数个*，且不是有效的Markdown语法）
        # 只有当单星号数量是奇数且没有形成有效的配对时才处理
        single_count = len(single_asterisks)
        if single_count % 2 == 1 and single_count > 0:
            # 检查是否可能是有效的Markdown语法（相邻的两个单星号之间有内容）
            valid_pairs = 0
            i = 0
            while i < single_count - 1:
                if single_asterisks[i + 1] - single_asterisks[i] > 1:
                    valid_pairs += 1
                    i += 2
                else:
                    i += 1

            # 如果没有有效的配对，移除最后一个单星号
            if valid_pairs == 0:
                last_pos = single_asterisks[-1]
                line = line[:last_pos] + line[last_pos + 1:]

        cleaned_lines.append(line)

    md_text = '\n'.join(cleaned_lines)

    # 恢复代码块
    for i, code_block in enumerate(code_blocks):
        md_text = md_text.replace(f"__CODE_BLOCK_{i}__", code_block)

    return md_text

def fix_escaped_markdown_syntax(md_text):
    """智能修复被转义的Markdown语法，避免破坏有意转义的内容"""
    import re
    
    # 1. 修复被错误转义的标题（只在行首的情况）
    md_text = re.sub(r'^\\#', '#', md_text, flags=re.MULTILINE)
    
    # 2. 智能处理星号转义
    # 首先保护代码块中的内容
    code_blocks = []
    def preserve_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # 保护围栏代码块
    md_text = re.sub(r'```[\s\S]*?```', preserve_code_block, md_text)
    # 保护行内代码
    md_text = re.sub(r'`[^`]*`', preserve_code_block, md_text)
    
    # 修复行首的列表标记（被错误转义的）
    md_text = re.sub(r'^\\(\*|\+|-)\s', r'\1 ', md_text, flags=re.MULTILINE)
    
    # 恢复代码块
    for i, code_block in enumerate(code_blocks):
        md_text = md_text.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return md_text

def preprocess_markdown_lists(md_text):
    """预处理Markdown文本，确保列表格式正确"""
    import re
    
    # 首先修复转义语法问题
    md_text = fix_escaped_markdown_syntax(md_text)
    
    # 修复伪列表格式（如：内容*：描述）
    md_text = fix_pseudo_list_format(md_text)
    
    # 清理孤立和不配对的星号
    md_text = clean_orphaned_asterisks(md_text)
    
    # 处理以 - 开头的无序列表，确保 - 后面有空格
    md_text = re.sub(r'^-([^ ])', r'- \1', md_text, flags=re.MULTILINE)
    
    # 处理以 * 开头的无序列表
    md_text = re.sub(r'^\*([^ ])', r'* \1', md_text, flags=re.MULTILINE)
    
    # 处理以 + 开头的无序列表
    md_text = re.sub(r'^\+([^ ])', r'+ \1', md_text, flags=re.MULTILINE)
    
    # 处理数字列表，确保格式正确
    md_text = re.sub(r'^(\d+)\.([^ ])', r'\1. \2', md_text, flags=re.MULTILINE)
    
    return md_text

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

def convert_absolute_paths_to_web_paths(html_content, static_dir=None):
    """将HTML中的绝对路径图片转换为Web可访问的路径"""
    import re
    
    # 如果没有指定static_dir，使用simple_paths中的配置
    if static_dir is None:
        try:
            from scripts.utils.simple_paths import get_static_dir
            static_dir = get_static_dir()
        except ImportError:
            static_dir = "static"  # fallback
    
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

def add_language_classes(html_content):
    """为代码块添加语言特定的类"""
    import re
    
    # 匹配代码块，查找语言标识
    code_block_pattern = r'```(\w+)\n(.*?)```'
    
    def replace_code_block(match):
        language = match.group(1)
        code_content = match.group(2)
        
        # 查找对应的HTML代码块
        # 这里需要更复杂的逻辑来匹配Markdown代码块和生成的HTML
        return match.group(0)
    
    # 处理HTML中的代码块，添加语言类
    # 查找 <div class="highlight"> 并添加语言类
    highlight_pattern = r'<div class="highlight">'
    
    def add_lang_to_highlight(match):
        # 这里需要从上下文推断语言
        # 暂时返回原始匹配
        return match.group(0)
    
    # 简单的语言检测和类添加
    html_content = re.sub(r'<div class="highlight">', r'<div class="highlight code-block">', html_content)
    
    return html_content

def enhance_list_styling(html_content):
    """增强列表的HTML样式，转换为AGI观察室模板格式"""
    import re
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 处理无序列表
    for ul in soup.find_all('ul'):
        # 为ul添加类
        ul['class'] = ul.get('class', []) + ['enhanced-list', 'unordered-list']
        
        # 将li转换为p标签
        for li in ul.find_all('li'):
            # 创建新的p标签
            p_tag = soup.new_tag('p', **{'class': 'magic-list-item'})
            
            # 添加自定义项目符号
            bullet_span = soup.new_tag('span', **{'class': 'magic-article-custom-bullet-square'})
            p_tag.append(bullet_span)
            p_tag.append(' ')
            
            # 移动li的内容到p标签
            for content in li.contents:
                if content.name != 'ul':  # 避免处理嵌套列表
                    p_tag.append(content)
            
            # 替换li标签
            li.replace_with(p_tag)
    
    # 处理有序列表
    for ol in soup.find_all('ol'):
        # 为ol添加类
        ol['class'] = ol.get('class', []) + ['enhanced-list', 'ordered-list']
        
        # 将li转换为p标签
        for i, li in enumerate(ol.find_all('li'), 1):
            # 创建新的p标签
            p_tag = soup.new_tag('p', **{'class': 'magic-list-item-number'})
            
            # 添加数字
            number_span = soup.new_tag('span', **{'style': 'font-weight: bold; margin-right: 8px;'})
            number_span.string = f"{i}."
            p_tag.append(number_span)
            p_tag.append(' ')
            
            # 移动li的内容到p标签
            for content in li.contents:
                if content.name != 'ol':  # 避免处理嵌套列表
                    p_tag.append(content)
            
            # 替换li标签
            li.replace_with(p_tag)
    
    return str(soup)

def enhance_table_styling(html_content):
    """增强表格的HTML样式"""
    import re
    
    # 为table标签添加类
    html_content = re.sub(r'<table([^>]*)>', r'<table\1 class="enhanced-table">', html_content)
    
    # 为thead中的th标签添加类
    html_content = re.sub(r'<th([^>]*)>', r'<th\1 class="table-header">', html_content)
    
    # 为tbody中的td标签添加类
    html_content = re.sub(r'<td([^>]*)>', r'<td\1 class="table-cell">', html_content)
    
    # 为tr标签添加类
    html_content = re.sub(r'<tr([^>]*)>', r'<tr\1 class="table-row">', html_content)
    
    return html_content

def add_header_classes(html_content):
    """为H标签添加CSS类"""
    import re
    
    # 为各级标题添加对应的CSS类
    # 使用AGI观察室模板的特殊类名
    html_content = re.sub(r'<h1([^>]*)>', r'<h1\1 class="magic-article-main-title">', html_content)
    html_content = re.sub(r'<h2([^>]*)>', r'<h2\1 class="magic-article-h2-section-title">', html_content)
    html_content = re.sub(r'<h3([^>]*)>', r'<h3\1 class="magic-article-h3-custom">', html_content)
    html_content = re.sub(r'<h4([^>]*)>', r'<h4\1 class="magic-article-h3-custom">', html_content)  # h4也使用h3样式
    html_content = re.sub(r'<h5([^>]*)>', r'<h5\1 class="magic-article-h3-custom">', html_content)  # h5也使用h3样式
    html_content = re.sub(r'<h6([^>]*)>', r'<h6\1 class="magic-article-h3-custom">', html_content)  # h6也使用h3样式
    
    return html_content

def wrap_in_section_for_rich_editor(html_content):
    """为富文本编辑器包装HTML内容，添加适合微信公众号的section标签"""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 查找body标签
    body = soup.find('body')
    if body:
        # 提取body内的所有内容
        body_content = ''.join(str(child) for child in body.children)
        
        # 创建适合富文本编辑器的section标签
        section_html = f'''<section id="nice" data-tool="mdnice编辑器" data-website="https://www.mdnice.com" style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; padding-top: 0px; padding-bottom: 0px; padding-left: 10px; padding-right: 10px; background-attachment: scroll; background-clip: border-box; background-color: rgba(0, 0, 0, 0); background-image: none; background-origin: padding-box; background-position-x: left; background-position-y: top; background-repeat: no-repeat; background-size: auto; width: auto; font-family: Optima, 'Microsoft YaHei', PingFangSC-regular, serif; font-size: 16px; color: rgb(0, 0, 0); line-height: 1.5em; word-spacing: 0em; letter-spacing: 0em; word-break: break-word; overflow-wrap: break-word; text-align: left;">
{body_content}
</section>'''
        
        return section_html
    else:
        # 如果没有body标签，直接包装整个内容
        section_html = f'''<section id="nice" data-tool="mdnice编辑器" data-website="https://www.mdnice.com" style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; padding-top: 0px; padding-bottom: 0px; padding-left: 10px; padding-right: 10px; background-attachment: scroll; background-clip: border-box; background-color: rgba(0, 0, 0, 0); background-image: none; background-origin: padding-box; background-position-x: left; background-position-y: top; background-repeat: no-repeat; background-size: auto; width: auto; font-family: Optima, 'Microsoft YaHei', PingFangSC-regular, serif; font-size: 16px; color: rgb(0, 0, 0); line-height: 1.5em; word-spacing: 0em; letter-spacing: 0em; word-break: break-word; overflow-wrap: break-word; text-align: left;">
{html_content}
</section>'''
        
        return section_html

def md_to_html(md_text: str, template_name: str = 'magic-article-template.html', static_dir: str = None, inline_css: bool = False, **kwargs) -> str:
    # 如果没有指定static_dir，使用simple_paths中的配置
    if static_dir is None:
        try:
            from scripts.utils.simple_paths import get_static_dir
            static_dir = get_static_dir()
        except ImportError:
            static_dir = "static"  # fallback
    
    # 预处理Markdown列表格式
    processed_md = preprocess_markdown_lists(md_text)
    
    # 处理图片（包括本地和网络图片）
    processed_md = process_images(processed_md, static_dir)
    
    # 配置代码高亮扩展
    codehilite_config = {
        'css_class': 'highlight',
        'use_pygments': True,
        'noclasses': False,
        'linenums': False,
        'guess_lang': True,
        'pygments_style': 'default'  # 使用默认样式，确保兼容性
    }
    
    # 转换为HTML，添加表格支持和其他常用扩展
    html_body = markdown.markdown(
        processed_md,
        extensions=[
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',  # 添加表格支持
            'markdown.extensions.fenced_code',  # 改进代码块支持
            'markdown.extensions.extra'  # 添加额外的Markdown扩展，包括列表支持
        ],
        extension_configs={'codehilite': codehilite_config}
    )
    

    
    # 手动添加语言特定的类到代码块
    html_body = add_language_classes(html_body)
    
    # 为H标签添加CSS类
    html_body = add_header_classes(html_body)
    
    # 增强列表样式
    html_body = enhance_list_styling(html_body)
    
    # 增强表格样式
    html_body = enhance_table_styling(html_body)
    
    # 使用模板渲染
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    html = template.render(content=html_body, **kwargs)
    
    # 根据inline_css参数决定是否转换class到inline style
    if inline_css:
        # 转换class到inline style（但保留代码高亮相关的类）
        html = convert_class_to_inline_style_preserve_code(html)
        
        # 处理HTML中的绝对路径图片
        html = convert_absolute_paths_to_web_paths(html, static_dir)
        
        # 将图片转换为base64编码（用于富文本编辑器）
        html = convert_images_to_base64(html, static_dir)
        
        # 为富文本编辑器优化：包装在section标签中
        html = wrap_in_section_for_rich_editor(html)
    else:
        # 处理HTML中的绝对路径图片
        html = convert_absolute_paths_to_web_paths(html, static_dir)
        
        # 将图片转换为base64编码（用于Streamlit HTML组件）
        html = convert_images_to_base64(html, static_dir)
    
    return html 