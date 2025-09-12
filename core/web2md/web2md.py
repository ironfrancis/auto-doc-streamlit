import os
import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from core.utils.path_manager import get_ori_docs_dir

def extract_markdown_from_url(url, output_file=None, scope="viewport", wait_time=5):
    """
    使用MagicLens从网页提取Markdown内容

    参数:
        url (str): 要提取内容的网页URL
        output_file (str, optional): 输出文件路径。如果为None，则自动生成
        scope (str, optional): 提取范围，可以是'all'或'viewport'
        wait_time (int, optional): 等待页面加载的时间（秒）

    返回:
        str: 提取的Markdown内容
    """
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小

    # 初始化WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 访问URL
        driver.get(url)
        print(f"正在加载页面: {url}")

        # 等待页面加载
        time.sleep(wait_time)

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
        
        # # 后处理：修复可能的伪列表格式问题
        # if markdown_content:
        #     try:
        #         from core.utils.md_utils import fix_pseudo_list_format
        #         markdown_content = fix_pseudo_list_format(markdown_content)
        #         print("已应用伪列表格式修复")
        #     except ImportError:
        #         print("警告：无法导入伪列表修复函数")
        #     except Exception as e:
        #         print(f"警告：伪列表修复失败: {e}")

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
    parser = argparse.ArgumentParser(description="从网页提取Markdown内容")
    parser.add_argument("url", help="要提取内容的网页URL")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-s", "--scope", choices=["all", "viewport"], default="viewport",
                        help="提取范围: 'all'(所有内容) 或 'viewport'(仅视口内容)")
    parser.add_argument("-w", "--wait", type=int, default=5,
                        help="等待页面加载的时间（秒）")

    args = parser.parse_args()

    # 提取Markdown
    extract_markdown_from_url(args.url, args.output, args.scope, args.wait)

if __name__ == "__main__":
    # main()
    extract_markdown_from_url("https://mp.weixin.qq.com/s/BMIQe8HkEDmwXZGD12SgoA", scope="viewport", wait_time=5)
