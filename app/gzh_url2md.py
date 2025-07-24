import time

import requests
from bs4 import BeautifulSoup
import markdownify
import re
from urllib.parse import urljoin, urlparse, unquote
from app.ai_service import ai_generate_markdown


def fetch_and_convert_to_md(url, output_file=None):
    try:
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析HTML内容并提取核心内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除不需要的元素（增加广告相关class）
        unwanted_selectors = [
            'script', 'style', 'nav', 'footer', 'aside', 'svg',
            'iframe', 'header', 'ad', 'ads', 'advertisement',
            '.ad-container', '.banner', '.popup', '.modal',
            '.cookie-consent', '.newsletter', '.social-share'
        ]
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

        # 提取主要文章内容（增加更多内容区域class）
        content_selectors = [
            'article',
            'main',
            'div.content',
            'div.main',
            'div.post',
            'div.article',
            'div.entry-content',
            'div.post-content'
        ]

        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.body if soup.body else soup

        # 处理图片链接（修复URL编码问题并确保100%可用）
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        for img in main_content.find_all('img', src=True):
            src = img.get('src', '').strip()
            if not src:
                continue

            try:
                # 解码URL编码的特殊字符
                decoded_src = unquote(src)

                # 处理相对路径
                if not decoded_src.startswith(('http://', 'https://', 'data:')):
                    decoded_src = urljoin(base_url, decoded_src)

                # 确保URL是有效的
                parsed_url = urlparse(decoded_src)
                if not (parsed_url.scheme and parsed_url.netloc) and not decoded_src.startswith('data:'):
                    continue

                # 创建Markdown图片语法，确保特殊字符被转义
                alt_text = img.get('alt', '').replace('[', '\\[').replace(']', '\\]')
                md_image = f"![{alt_text}]({decoded_src})"

                # 替换原img标签
                img.replace_with(md_image)

            except Exception as e:
                print(f"处理图片链接出错: {e}")
                continue

        # 转换为Markdown格式
        md_content = markdownify.markdownify(
            str(main_content),
            heading_style="ATX",
            escape_underscores=False,
            keep_inline_images_in=['img']
        )

        # 后处理：修复Markdown中的常见问题
        # 1. 修复错误的图片标签
        md_content = re.sub(r'\[/link\?target=[^\]]+\]\(([^)]+)\)', r'![](\1)', md_content)
        # 2. 移除多余的空白行
        md_content = re.sub(r'\n{3,}', '\n\n', md_content)
        # 3. 修复被转义的Markdown语法
        md_content = md_content.replace('\\#', '#').replace('\\*', '*')
        # 4. 移除多余的markdown代码块标记
        md_content = re.sub(r'```markdown\n|\n```', '', md_content)

        # 自动生成文件名逻辑
        if not output_file:
            import os
            # 获取项目根目录的绝对路径
            current_dir = os.path.dirname(os.path.abspath(__file__))  # app目录
            project_root = os.path.dirname(current_dir)  # 项目根目录
            ori_docs_dir = os.path.join(project_root, 'ori_docs')
            
            # 确保ori_docs目录存在
            os.makedirs(ori_docs_dir, exist_ok=True)
            
            # 查找最大编号
            max_num = 0
            for filename in os.listdir(ori_docs_dir):
                if filename.endswith('.md'):
                    try:
                        num = int(filename.split('.')[0])
                        if num > max_num:
                            max_num = num
                    except ValueError:
                        continue
            
            # 使用绝对路径生成输出文件名
            output_file = os.path.join(ori_docs_dir, f"{max_num + 1:03d}.md")

        # 使用AI优化Markdown内容
        try:
            prompt = f"""
            请优化以下从网页转换而来的Markdown内容，使其更加清晰、结构化，并修复任何格式问题：
            剔除内容中的广告、导航栏、页脚、弹窗、cookie提示、评论、相关推荐等无关内容。
            不要删减文章原本的内容和配图，只清理与文章主题完全无关的元素。

            {md_content}

            请返回优化后的完整Markdown内容，不要添加任何额外的解释。
            """


            # optimized_md = ai_generate_markdown(prompt)
            optimized_md = requests.post(
                url="http://localhost:1234/v1/chat/completions",
                json={
                    "model": "google/gemma-3-12b",
                    "messages": [
                        {"role": "system", "content": "优化Markdown内容，保持专业格式"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": -1,
                    "stream": False
                }
            ).json()["choices"][0]["message"]["content"]
            # 在$PLACEHOLDER$位置插入以下代码
            if optimized_md:
                # 清理多余的markdown标记
                optimized_md = optimized_md.replace('```markdown', '').replace('```', '')
                # 修复可能存在的图片链接格式
                optimized_md = re.sub(r'!\[([^\]]*)\]\(([^)]*)\)', r'![\1](\2)', optimized_md)
                # 确保标题格式统一
                optimized_md = re.sub(r'^#+\s*(.*)', lambda m: f"# {m.group(1)}", optimized_md, flags=re.MULTILINE)

            # 如果AI生成成功，使用优化后的内容
            if optimized_md:
                md_content = optimized_md
                print("已使用AI优化Markdown内容")
        except Exception as e:
            print(f"AI优化Markdown内容失败: {e}")
            # 如果AI优化失败，继续使用原始内容

        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"成功转换并保存到 {output_file}")
        return md_content

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"处理过程中出错: {e}")


if __name__ == "__main__":
    url = "https://mp.weixin.qq.com/s/PyOk4fKebF00ZC-CPsD-3Q"
    print(fetch_and_convert_to_md(url))