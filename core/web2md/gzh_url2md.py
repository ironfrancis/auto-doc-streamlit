import time
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
from bs4 import BeautifulSoup
import markdownify
import re
from urllib.parse import urljoin, urlparse, unquote

# 尝试导入path_manager，如果失败则提供默认实现
try:
    from core.utils.path_manager import get_ori_docs_dir
except ImportError:
    def get_ori_docs_dir():
        """默认的ori_docs目录获取函数"""
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'workspace', 'articles')

# from app.ai_service import ai_generate_markdown  # 已废弃，无需导入


def extract_text_content(url, include_stats=True):
    """
    专门用于提取网页文本内容的函数

    Args:
        url (str): 网页URL
        include_stats (bool): 是否包含统计信息

    Returns:
        dict: 包含文本内容和统计信息的字典，如果失败返回None
    """
    try:
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 解析HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 移除不需要的元素
        unwanted_selectors = [
            'script', 'style', 'nav', 'footer', 'aside', 'svg',
            'iframe', 'header', 'ad', 'ads', 'advertisement',
            '.ad-container', '.banner', '.popup', '.modal',
            '.cookie-consent', '.newsletter', '.social-share'
        ]
        for selector in unwanted_selectors:
            for element in soup.select(selector):
                element.decompose()

        # 提取主要文章内容（优先级顺序）
        content_selectors = [
            'article',
            'main',
            'div.content',
            'div.main',
            'div.post',
            'div.article',
            'div.entry-content',
            'div.post-content',
            '#js_content',  # 微信公众号文章专用
            '.rich_media_content',  # 微信公众号备用选择器
        ]

        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                print(f"找到内容区域: {selector}")
                break

        if not main_content:
            main_content = soup.body if soup.body else soup
            print("使用body作为内容区域")

        # 提取纯文本内容
        if main_content:
            # 获取所有文本，清理空白字符
            text_content = main_content.get_text(separator=' ')
            # 清理多余的空白字符
            text_content = ' '.join(text_content.split())
            # 移除过多的连续空格
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content.strip()
        else:
            text_content = ""

        # 计算统计信息
        if include_stats:
            char_count = len(text_content)
            word_count = len(text_content.split()) if text_content else 0

            # 估算阅读时间（假设每分钟阅读300字中文）
            reading_time = word_count // 300 + 1 if word_count > 0 else 0

            # 提取标题
            title = ""
            title_selectors = ['h1', 'title', '.title', '.post-title']
            for selector in title_selectors:
                title_element = soup.select_one(selector)
                if title_element:
                    title = title_element.get_text().strip()
                    break

            if not title and soup.title:
                title = soup.title.get_text().strip()

            return {
                'text': text_content,
                'title': title,
                'char_count': char_count,
                'word_count': word_count,
                'reading_time_minutes': reading_time,
                'url': url,
                'success': True
            }
        else:
            return {
                'text': text_content,
                'success': True
            }

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return {
            'text': '',
            'error': f'请求失败: {e}',
            'success': False
        }
    except Exception as e:
        print(f"处理过程中出错: {e}")
        return {
            'text': '',
            'error': f'处理失败: {e}',
            'success': False
        }


def fix_escaped_markdown_syntax(md_content):
    """智能修复被转义的Markdown语法，避免破坏有意转义的内容"""
    
    # 1. 修复被错误转义的标题（只在行首的情况）
    md_content = re.sub(r'^\\#', '#', md_content, flags=re.MULTILINE)
    
    # 2. 智能处理星号转义
    # 首先保护代码块中的内容
    code_blocks = []
    def preserve_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # 保护围栏代码块
    md_content = re.sub(r'```[\s\S]*?```', preserve_code_block, md_content)
    # 保护行内代码
    md_content = re.sub(r'`[^`]*`', preserve_code_block, md_content)
    
    # 现在安全地处理星号转义
    # 只有在明显不是故意转义的情况下才还原
    # 例如：在行首的列表标记，或者在明显的强调语法中
    
    # 修复行首的列表标记（被错误转义的）
    md_content = re.sub(r'^\\(\*|\+|-)\s', r'\1 ', md_content, flags=re.MULTILINE)
    
    # 修复明显的强调语法（但要小心，不要破坏有意的转义）
    # 这里我们采用保守策略，只修复最明显的错误转义
    
    # 不再无条件替换所有的 \*，而是让Markdown解析器自己处理
    
    # 恢复代码块
    for i, code_block in enumerate(code_blocks):
        md_content = md_content.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    return md_content


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
        # 3. 智能修复被转义的Markdown语法
        md_content = fix_escaped_markdown_syntax(md_content)
        # 4. 修复伪列表格式（从web转换产生的*：格式）
        from core.utils.md_utils import fix_pseudo_list_format
        md_content = fix_pseudo_list_format(md_content)
        # 5. 移除多余的markdown代码块标记
        md_content = re.sub(r'```markdown\n|\n```', '', md_content)

        # 自动生成文件名逻辑
        if not output_file:
            # 使用path_manager获取ori_docs目录
            ori_docs_dir = str(get_ori_docs_dir())

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


def test_extract_text_content():
    """测试文本内容提取功能"""
    test_urls = [
        "https://mp.weixin.qq.com/s/BMIQe8HkEDmwXZGD12SgoA",
        "https://example.com",  # 这是一个不存在的URL，用于测试错误处理
    ]

    print("=" * 60)
    print("测试文本内容提取功能")
    print("=" * 60)

    for i, url in enumerate(test_urls, 1):
        print(f"\n测试 {i}: {url}")
        print("-" * 40)

        try:
            result = extract_text_content(url, include_stats=True)

            if result['success']:
                print(f"✓ 成功提取内容")
                print(f"标题: {result.get('title', '未找到标题')[:50]}...")
                print(f"字符数: {result['char_count']}")
                print(f"字数: {result['word_count']}")
                print(f"预估阅读时间: {result['reading_time_minutes']} 分钟")

                # 显示前200个字符的内容预览
                preview = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                print(f"内容预览: {preview}")
            else:
                print(f"✗ 提取失败: {result.get('error', '未知错误')}")

        except Exception as e:
            print(f"✗ 测试过程中出错: {e}")

        print()


def get_text_length_from_csv(csv_path, url_column='内容url', batch_size=5):
    """
    从CSV文件中批量提取文章文本长度

    Args:
        csv_path (str): CSV文件路径
        url_column (str): URL列的列名
        batch_size (int): 每批处理的数量，避免请求过于频繁

    Returns:
        pandas.DataFrame: 包含新列的DataFrame
    """
    try:
        import pandas as pd
        import time

        # 读取CSV文件
        df = pd.read_csv(csv_path)
        print(f"读取到 {len(df)} 条记录")

        # 初始化新列
        df['正文字数'] = 0
        df['标题'] = ''
        df['阅读时间'] = 0
        df['提取状态'] = '待处理'

        # 批量处理
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]

            for idx, row in batch.iterrows():
                url = row[url_column]
                print(f"正在处理第 {idx+1} 条: {url[:50]}...")

                try:
                    result = extract_text_content(url, include_stats=True)

                    if result['success']:
                        df.at[idx, '正文字数'] = result['word_count']
                        df.at[idx, '标题'] = result['title']
                        df.at[idx, '阅读时间'] = result['reading_time_minutes']
                        df.at[idx, '提取状态'] = '成功'
                        print(f"  ✓ 成功 - 字数:{result['word_count']}, 标题:{result['title'][:30]}...")
                    else:
                        df.at[idx, '提取状态'] = f"失败:{result.get('error', '未知错误')}"
                        print(f"  ✗ 失败 - {result.get('error', '未知错误')}")

                except Exception as e:
                    df.at[idx, '提取状态'] = f"异常:{str(e)}"
                    print(f"  ✗ 异常 - {e}")

                # 添加短暂延迟，避免请求过于频繁
                time.sleep(1)

            print(f"已处理 {min(i+batch_size, len(df))}/{len(df)} 条记录")
            # 批次间稍长延迟
            if i + batch_size < len(df):
                time.sleep(2)

        # 保存结果
        output_path = csv_path.replace('.csv', '_with_text_analysis.csv')
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n结果已保存到: {output_path}")

        # 输出统计信息
        success_count = len(df[df['提取状态'] == '成功'])
        print("\n统计信息:")
        print(f"总记录数: {len(df)}")
        print(f"成功提取: {success_count}")
        print(f"成功率: {success_count/len(df)*100:.1f}%")

        # 计算平均字数（避免空序列错误）
        valid_word_counts = df[df['正文字数'] > 0]['正文字数']
        if len(valid_word_counts) > 0:
            print(f"平均字数: {valid_word_counts.mean():.0f}")
        else:
            print("平均字数: 暂无有效数据")

        return df

    except Exception as e:
        print(f"批量处理过程中出错: {e}")
        return None


if __name__ == "__main__":
    # 测试新的文本提取功能
    test_extract_text_content()

    # 测试批量处理CSV文件的功能（如果有publish_history.csv文件）
    print("\n" + "=" * 60)
    print("测试批量处理CSV文件功能")
    print("=" * 60)

    csv_path = "./workspace/data/publish_history.csv"
    if os.path.exists(csv_path):
        print(f"找到CSV文件: {csv_path}")
        print("开始批量处理（仅处理前3条记录作为测试）...")

        # 读取并处理前3条记录
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            test_df = df.head(3).copy()

            # 保存临时测试文件
            test_csv_path = csv_path.replace('.csv', '_test_sample.csv')
            test_df.to_csv(test_csv_path, index=False, encoding='utf-8-sig')

            # 处理测试文件
            result_df = get_text_length_from_csv(test_csv_path, batch_size=2)

            if result_df is not None:
                print("✓ 批量处理测试成功")
                print(f"处理了 {len(result_df)} 条记录")
            else:
                print("✗ 批量处理测试失败")

            # 清理临时文件
            if os.path.exists(test_csv_path):
                os.remove(test_csv_path)
                print("临时测试文件已清理")

        except Exception as e:
            print(f"批量处理测试出错: {e}")
    else:
        print(f"未找到CSV文件: {csv_path}")
        print("跳过批量处理测试")

    # 也可以测试原有的Markdown转换功能
    print("\n" + "=" * 60)
    print("测试Markdown转换功能")
    print("=" * 60)

    url = "https://mp.weixin.qq.com/s/BMIQe8HkEDmwXZGD12SgoA"
    result = fetch_and_convert_to_md(url)
    if result:
        print("✓ Markdown转换成功")
        print(f"内容长度: {len(result)} 字符")
    else:
        print("✗ Markdown转换失败")