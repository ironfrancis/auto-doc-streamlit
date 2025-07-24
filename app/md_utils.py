import markdown
from jinja2 import Environment, FileSystemLoader
import os
from bs4 import BeautifulSoup

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

def md_to_html(md_text: str, template_name: str = 'wepub.html', **kwargs) -> str:
    html_body = markdown.markdown(md_text, extensions=['extra', 'codehilite'])
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(template_name)
    html = template.render(content=html_body, **kwargs)
    html = convert_class_to_inline_style(html)
    return html 