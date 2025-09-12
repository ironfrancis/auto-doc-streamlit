import requests
import pandas as pd

def fetch_baijiahao_article_list_statistic(cookie: str, start_day: str, end_day: str, type_: str = "news"):
    """
    获取百家号文章统计数据

    参数:
        cookie (str): 登录百家号后台的Cookie字符串
        start_day (str): 开始日期，格式如 '20250828'
        end_day (str): 结束日期，格式如 '20250903'
        type_ (str): 类型，默认为 'news'

    返回:
        pd.DataFrame: 文章统计数据表
    """
    url = (
        "https://baijiahao.baidu.com/author/eco/statistics/articleListStatistic"
        f"?is_export=1&type={type_}&start_day={start_day}&end_day={end_day}"
    )
    headers = {
        "cookie": cookie.strip(),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://baijiahao.baidu.com/",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 401 or resp.status_code == 403:
            raise Exception("Cookie已失效或无权限，请重新登录百家号后台获取Cookie。")
        if resp.status_code != 200:
            raise Exception(f"请求失败，状态码: {resp.status_code}")

        # 百家号返回的是csv格式
        if resp.text.strip().startswith("{"):
            # 可能是错误信息
            try:
                err = resp.json()
                raise Exception(f"百家号API返回错误: {err.get('msg', err)}")
            except Exception:
                raise Exception("百家号API返回未知错误，且不是csv格式。")
        # 解析csv
        from io import StringIO
        df = pd.read_csv(StringIO(resp.text))
        return df
    except Exception as e:
        print(f"❌ 获取百家号文章统计数据失败: {e}")
        return pd.DataFrame()


