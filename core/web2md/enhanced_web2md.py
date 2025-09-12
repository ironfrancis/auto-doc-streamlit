import os
import time
import argparse
import platform
import re
import requests
import hashlib
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from core.utils.path_manager import get_ori_docs_dir

def download_image(url, save_dir, base_url=None):
    """下载网络图片到本地"""
    try:
        # 如果是相对URL，转换为绝对URL
        if not url.startswith(('http://', 'https://')) and base_url:
            url = urljoin(base_url, url)
        
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
        filename = f"web_img_{timestamp}_{url_hash}{ext}"
        
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
        
        return final_filename
        
    except Exception as e:
        print(f"下载图片失败 {url}: {str(e)}")
        return None

def process_images_in_markdown(markdown_content, base_url, images_dir):
    """处理Markdown内容中的图片，下载网络图片并更新路径"""
    # 创建图片目录
    os.makedirs(images_dir, exist_ok=True)
    
    # 匹配Markdown图片语法
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_image(match):
        alt_text = match.group(1)
        image_url = match.group(2)
        
        # 检查是否是网络图片
        if image_url.startswith(('http://', 'https://')) or (not image_url.startswith('/') and not os.path.isabs(image_url)):
            try:
                # 下载网络图片
                filename = download_image(image_url, images_dir, base_url)
                if filename:
                    # 返回绝对路径
                    new_path = os.path.abspath(os.path.join(images_dir, filename))
                    return f'![{alt_text}]({new_path})'
                else:
                    # 下载失败，保持原URL并添加警告
                    return f'![{alt_text}]({image_url}) <!-- 图片下载失败: {image_url} -->'
            except Exception as e:
                # 如果处理失败，保持原路径
                return f'![{alt_text}]({image_url}) <!-- 图片处理失败: {str(e)} -->'
        else:
            # 如果是本地路径或已经是相对路径，保持不变
            return match.group(0)
    
    # 替换所有图片路径
    processed_md = re.sub(image_pattern, replace_image, markdown_content)
    return processed_md

def extract_markdown_from_url(url, output_file=None, scope="viewport", wait_time=5,
                             scroll=True, scroll_pause=1.0, viewport_height=1080,
                             remove_selectors=None, download_images=True):
    """
    使用MagicLens从网页提取Markdown内容（增强版）

    参数:
        url (str): 要提取内容的网页URL
        output_file (str, optional): 输出文件路径。如果为None，则自动生成
        scope (str, optional): 提取范围，可以是'all'或'viewport'
        wait_time (int, optional): 等待页面加载的时间（秒）
        scroll (bool, optional): 是否滚动页面以加载懒加载内容
        scroll_pause (float, optional): 每次滚动后的暂停时间（秒）
        viewport_height (int, optional): 浏览器视口高度（像素）
        remove_selectors (list, optional): 要移除的元素的CSS选择器列表
        download_images (bool, optional): 是否下载图片到本地

    返回:
        str: 提取的Markdown内容
    """
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size=1920,{viewport_height}")  # 设置窗口大小
    chrome_options.add_argument("--no-sandbox")  # 添加安全参数
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决内存不足问题

    # 初始化WebDriver（使用webdriver_manager自动管理ChromeDriver）
    try:
        # 使用webdriver-manager自动下载和管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"使用webdriver-manager初始化Chrome失败: {e}")
        try:
            # 备用方案：尝试使用系统安装的ChromeDriver
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e2:
            print(f"备用方案也失败: {e2}")
            # 提供更详细的错误信息和解决方案
            error_msg = """
Chrome初始化失败，可能是以下原因之一：

1. 网络连接问题：webdriver-manager无法下载匹配的ChromeDriver
2. 版本不兼容：系统中的ChromeDriver版本与Chrome浏览器版本不匹配
3. 权限问题：无法访问ChromeDriver或Chrome浏览器

解决方案：
1. 检查网络连接
2. 删除旧版本ChromeDriver：sudo rm -f /usr/local/bin/chromedriver
3. 手动下载匹配版本的ChromeDriver：https://googlechromelabs.github.io/chromedriver/
4. 或者使用代理设置环境变量：export HTTPS_PROXY=http://your-proxy:port

请检查Chrome版本并下载对应的ChromeDriver。
"""
            raise Exception(error_msg)

    try:
        # 访问URL
        driver.get(url)
        print(f"正在加载页面: {url}")

        # 等待页面加载
        time.sleep(wait_time)

        # 滚动页面以加载懒加载内容
        if scroll:
            print("滚动页面以加载懒加载内容...")
            # 获取页面高度
            last_height = driver.execute_script("return document.body.scrollHeight")

            while True:
                # 滚动到页面底部
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # 等待内容加载
                time.sleep(scroll_pause)

                # 计算新的滚动高度并与上一个滚动高度进行比较
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # 如果页面高度没有变化，说明已经滚动到底部
                    break
                last_height = new_height

            # 滚动回顶部
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(scroll_pause)

        # 移除干扰元素
        if remove_selectors:
            print(f"移除干扰元素: {remove_selectors}")
            for selector in remove_selectors:
                try:
                    # 尝试移除匹配的元素
                    driver.execute_script(f"""
                        var elements = document.querySelectorAll('{selector}');
                        for(var i=0; i<elements.length; i++){{
                            elements[i].parentNode.removeChild(elements[i]);
                        }}
                    """)
                except Exception as e:
                    print(f"移除元素 '{selector}' 时出错: {e}")

        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 读取MagicLens脚本（在static/js目录下）
        lens_js_path = os.path.join(current_dir, "..", "..", "static", "js", "lens.js")
        with open(lens_js_path, "r", encoding="utf-8") as f:
            lens_js = f.read()

        # 注入MagicLens脚本
        driver.execute_script(lens_js)

        # 调用MagicLens提取Markdown
        print(f"使用MagicLens提取内容 (scope={scope})...")
        markdown_content = driver.execute_script(f"return window.MagicLens.readAsMarkdown('{scope}');")
        
        # 后处理：修复可能的伪列表格式问题
        if markdown_content:
            try:
                from core.utils.md_utils import fix_pseudo_list_format
                markdown_content = fix_pseudo_list_format(markdown_content)
                print("已应用伪列表格式修复")
            except ImportError:
                print("警告：无法导入伪列表修复函数")
            except Exception as e:
                print(f"警告：伪列表修复失败: {e}")

            # 后处理：将超过2个连续星号替换为2个星号，避免转换错误
            try:
                # 使用正则表达式匹配3个或更多连续的星号，替换为2个星号
                import re
                # 先统计有多少个需要替换的地方
                matches = re.findall(r'\*{3,}', markdown_content)
                if matches:
                    markdown_content = re.sub(r'\*{3,}', '**', markdown_content)
                    print(f"已将 {len(matches)} 处多余星号替换为2个星号")
            except Exception as e:
                print(f"警告：星号处理失败: {e}")

        # 如果启用图片下载，处理图片
        if download_images and markdown_content:
            print("正在处理图片...")
            # 获取项目根目录
            project_root = os.path.dirname(current_dir)
            static_dir = os.path.join(project_root, 'app', 'static')
            images_dir = os.path.join(static_dir, 'images')
            
            # 处理图片
            markdown_content = process_images_in_markdown(markdown_content, url, images_dir)
            print(f"图片处理完成，保存到: {images_dir}")

        # 自动生成输出文件名
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

        # 保存Markdown内容到文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"成功提取并保存到: {output_file}")
        return markdown_content, output_file

    except Exception as e:
        print(f"提取过程中出错: {e}")
        return None, None

    finally:
        # 关闭WebDriver
        driver.quit()

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="从网页提取Markdown内容（增强版）")
    parser.add_argument("url", help="要提取内容的网页URL")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-s", "--scope", choices=["all", "viewport"], default="viewport",
                        help="提取范围: 'all'(所有内容) 或 'viewport'(仅视口内容)")
    parser.add_argument("-w", "--wait", type=int, default=5,
                        help="等待页面加载的时间（秒）")
    parser.add_argument("--no-scroll", action="store_false", dest="scroll",
                        help="禁用页面滚动")
    parser.add_argument("--scroll-pause", type=float, default=1.0,
                        help="每次滚动后的暂停时间（秒）")
    parser.add_argument("--viewport-height", type=int, default=1080,
                        help="浏览器视口高度（像素）")
    parser.add_argument("--remove", nargs="+", dest="remove_selectors",
                        help="要移除的元素的CSS选择器（空格分隔）")
    parser.add_argument("--no-images", action="store_false", dest="download_images",
                        help="禁用图片下载")

    args = parser.parse_args()

    # 提取Markdown
    extract_markdown_from_url(
        args.url,
        args.output,
        args.scope,
        args.wait,
        args.scroll,
        args.scroll_pause,
        args.viewport_height,
        args.remove_selectors,
        args.download_images
    )

# if __name__ == "__main__":
#     main()
if __name__ == "__main__":
    test_url = "https://mp.weixin.qq.com/s/R0ninv_5YTlLeNnw0zk4Ew"
    extract_markdown_from_url(
        url=test_url,
    )

