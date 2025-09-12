import urllib.parse
import json


def build_toutiao_mp_url(visited_uid, offset=0, count=10, keyword=""):
    """
    构建今日头条媒体平台API URL

    Args:
        visited_uid (str): 要访问的自媒体账号UID
        offset (int): 分页偏移量
        count (int): 每页数量
        keyword (str): 搜索关键词

    Returns:
        str: 构建完成的URL
    """
    # 基础URL
    base_url = "https://mp.toutiao.com/api/feed/mp_provider/v1/"

    # 固定参数
    params = {
        "provider_type": "mp_provider",
        "aid": "13",
        "app_name": "news_article",
        "category": "mp_all",
        "channel": "",
        "stream_api_version": "88",
        "device_platform": "pc",
        "platform_id": "0",
        "visited_uid": visited_uid,
        "offset": str(offset),
        "count": str(count),
        "keyword": keyword,
        "app_id": "1231"
    }

    # JSON参数 - genre_type_switch
    genre_switch = {
        "repost": 1,
        "small_video": 1,
        "toutiao_graphic": 1,
        "weitoutiao": 1,
        "xigua_video": 1
    }
    params["genre_type_switch"] = json.dumps(genre_switch, ensure_ascii=False)

    # JSON参数 - client_extra_params
    client_params = {
        "category": "mp_all",
        "real_app_id": "1231",
        "need_forward": "true",
        "offset_mode": "1",
        "page_index": "1",
        "status": "8",
        "source": "0"
    }
    params["client_extra_params"] = json.dumps(client_params, ensure_ascii=False)

    # 构建查询字符串
    query_string = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

    # 组合完整URL
    full_url = f"{base_url}?{query_string}"

    return full_url


# 使用示例
if __name__ == "__main__":
    # 示例1：构建原始URL
    visited_uid = "3484813672855172"
    url = build_toutiao_mp_url(visited_uid)
    print("生成的URL:")
    print(url)
    print("\n" + "=" * 50 + "\n")

