import os
import time
import argparse
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def extract_markdown_from_url(url, output_file=None, scope="viewport", wait_time=5,
                             scroll=True, scroll_pause=1.0, viewport_height=1080,
                             remove_selectors=None):
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

    # 初始化WebDriver（不使用webdriver_manager）
    try:
        # 直接使用Chrome浏览器，不需要指定驱动路径
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"使用默认方式初始化Chrome失败: {e}")
        try:
            # 尝试使用系统默认的ChromeDriver位置
            system = platform.system()
            if system == "Darwin":  # macOS
                driver_path = "/usr/local/bin/chromedriver"
            elif system == "Linux":
                driver_path = "/usr/bin/chromedriver"
            elif system == "Windows":
                driver_path = "C:\\Program Files\\chromedriver.exe"
            else:
                raise Exception(f"不支持的操作系统: {system}")
            
            service = Service(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e2:
            print(f"使用系统默认路径初始化Chrome失败: {e2}")
            raise Exception("无法初始化Chrome浏览器。请确保已安装Chrome和ChromeDriver，并且它们的版本兼容。")

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

        # 读取MagicLens脚本
        lens_js_path = os.path.join(current_dir, "lens.js")
        with open(lens_js_path, "r", encoding="utf-8") as f:
            lens_js = f.read()

        # 注入MagicLens脚本
        driver.execute_script(lens_js)

        # 调用MagicLens提取Markdown
        print(f"使用MagicLens提取内容 (scope={scope})...")
        markdown_content = driver.execute_script(f"return window.MagicLens.readAsMarkdown('{scope}');")

        # 自动生成输出文件名
        if not output_file:
            # 获取项目根目录
            project_root = os.path.dirname(current_dir)
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

        # 保存Markdown内容到文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"成功提取并保存到: {output_file}")
        return markdown_content

    except Exception as e:
        print(f"提取过程中出错: {e}")
        return None

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
        args.remove_selectors
    )

if __name__ == "__main__":
    main()
