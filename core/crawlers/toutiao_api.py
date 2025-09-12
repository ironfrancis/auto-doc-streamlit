from datetime import datetime
from operator import index

import pandas as pd
import requests
import json
import os
import re
import urllib.parse

# 账号ID到URL的映射字典
url_dict = {
    "3484813672855172": "https://mp.toutiao.com/api/feed/mp_provider/v1/?provider_type=mp_provider&aid=13&app_name=news_article&category=mp_all&channel=&stream_api_version=88&genre_type_switch=%7B%22repost%22%3A1%2C%22small_video%22%3A1%2C%22toutiao_graphic%22%3A1%2C%22weitoutiao%22%3A1%2C%22xigua_video%22%3A1%7D&device_platform=pc&platform_id=0&visited_uid=3484813672855172&offset=0&count=100&keyword=&client_extra_params=%7B%22category%22%3A%22mp_all%22%2C%22real_app_id%22%3A%221231%22%2C%22need_forward%22%3A%22true%22%2C%22offset_mode%22%3A%221%22%2C%22page_index%22%3A%221%22%2C%22status%22%3A%228%22%2C%22source%22%3A%220%22%7D&app_id=1231",
    "4223685486980743":"https://mp.toutiao.com/api/feed/mp_provider/v1/?provider_type=mp_provider&aid=13&app_name=news_article&category=mp_all&channel=&stream_api_version=88&genre_type_switch=%7B%22repost%22%3A1%2C%22small_video%22%3A1%2C%22toutiao_graphic%22%3A1%2C%22weitoutiao%22%3A1%2C%22xigua_video%22%3A1%7D&device_platform=pc&platform_id=0&visited_uid=4223685486980743&offset=0&count=10&keyword=&client_extra_params=%7B%22category%22%3A%22mp_all%22%2C%22real_app_id%22%3A%221231%22%2C%22need_forward%22%3A%22true%22%2C%22offset_mode%22%3A%221%22%2C%22page_index%22%3A%221%22%2C%22status%22%3A%228%22%2C%22source%22%3A%220%22%7D&app_id=1231"
    # 可以在这里添加更多账号的URL映射
}

def build_toutiao_mp_url(visited_uid, offset=0, count=100, keyword=""):
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

def extract_account_id_from_cookie(cookie_str):
    """
    从Cookie字符串中提取账号ID
    
    Args:
        cookie_str: Cookie字符串
        
    Returns:
        str: 账号ID，如果未找到则返回None
    """
    # 清理Cookie字符串
    cleaned_cookie = cookie_str.strip().replace('\n', '').replace('\r', '').replace('\t', '')
    
    # 尝试多种模式提取账号ID
    patterns = [
        r'uid_tt=([^;]+)',           # uid_tt=账号ID
        r'toutiao_sso_user=([^;]+)', # toutiao_sso_user=账号ID
        r'tt_webid=(\d+)',           # tt_webid=数字ID
        r'sessionid=([^;]+)',        # sessionid=账号ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, cleaned_cookie)
        if match:
            account_id = match.group(1)
            print(f"🔍 从Cookie中提取到账号ID: {account_id}")
            return account_id
    
    print("⚠️ 未能从Cookie中提取到账号ID")
    return None

def add_account_url(account_id, custom_url=None):
    """
    为账号添加专用URL
    
    Args:
        account_id: 账号ID
        custom_url: 自定义URL，如果为None则使用默认模板
    """
    if custom_url:
        url_dict[account_id] = custom_url
        print(f"✅ 为账号 {account_id} 添加了自定义URL")
    else:
        # 使用默认URL模板
        default_url = "https://mp.toutiao.com/api/feed/mp_provider/v1/?provider_type=mp_provider&aid=13&app_name=news_article&category=mp_all&channel=&stream_api_version=88&genre_type_switch=%7B%22repost%22%3A1%2C%22small_video%22%3A1%2C%22toutiao_graphic%22%3A1%2C%22weitoutiao%22%3A1%7D&device_platform=pc&platform_id=0&visited_uid={}&offset=0&count=100&keyword=&client_extra_params=%7B%22category%22%3A%22mp_all%22%2C%22real_app_id%22%3A%221231%22%2C%22need_forward%22%3A%22true%22%2C%22offset_mode%22%3A%221%22%2C%22page_index%22%3A%221%22%2C%22status%22%3A%228%22%2C%22source%22%3A%220%22%7D&app_id=1231"
        url_dict[account_id] = default_url.format(account_id)
        print(f"✅ 为账号 {account_id} 添加了默认URL模板")

def get_url_for_account(account_id):
    """
    根据账号ID获取对应的请求URL
    
    Args:
        account_id: 账号ID
        
    Returns:
        str: 对应的URL，如果未找到则返回默认URL
    """
    if account_id in url_dict:
        print(f"✅ 找到账号 {account_id} 的专用URL")
        return url_dict[account_id]
    else:
        print(f"⚠️ 未找到账号 {account_id} 的专用URL，使用动态构建的URL")
        # 使用新的URL构建函数
        return build_toutiao_mp_url(account_id)

def list_account_urls():
    """
    列出所有已配置的账号URL
    
    Returns:
        dict: 账号ID到URL的映射
    """
    print("📋 已配置的账号URL:")
    for account_id, url in url_dict.items():
        print(f"  {account_id}: {url[:100]}...")
    return url_dict


def fetch_article_by_site(cookie_str,url=None):
    # 清理Cookie字符串，移除换行符和多余空格
    cleaned_cookie = cookie_str.strip().replace('\n', '').replace('\r', '').replace('\t', '')
    
    # 提取账号ID
    account_id = extract_account_id_from_cookie(cleaned_cookie)
    
    # 获取对应的URL
    if not url:
        url = get_url_for_account(account_id)
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "priority": "u=1, i",
        "referer": "https://mp.toutiao.com/profile_v4/manage/content/all",
        "rpc-persist-bytetim_business_stream_caller": "mp",
        "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "cookie": cleaned_cookie
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        
        # 检查HTTP状态码
        if resp.status_code == 401:
            raise Exception("Cookie已失效，需要重新登录 (401 Unauthorized)")
        elif resp.status_code == 403:
            raise Exception("Cookie已失效，权限不足 (403 Forbidden)")
        elif resp.status_code == 429:
            raise Exception("请求频率过高，请稍后再试 (429 Too Many Requests)")
        elif resp.status_code != 200:
            raise Exception(f"HTTP请求失败，状态码: {resp.status_code}")
        
        # 检查响应内容
        try:
            resp_json = resp.json()
        except Exception as e:
            raise Exception(f"响应不是有效的JSON格式: {str(e)}")
        
        # 检查API返回的错误信息
        if 'error' in resp_json:
            error_msg = resp_json.get('error', '')
            if 'unauthorized' in error_msg.lower() or 'forbidden' in error_msg.lower():
                raise Exception("Cookie已失效，需要重新登录")
            elif 'rate limit' in error_msg.lower() or 'too many requests' in error_msg.lower():
                raise Exception("请求频率过高，请稍后再试")
            else:
                raise Exception(f"API返回错误: {error_msg}")
        
        # 检查是否有数据返回
        if 'data' not in resp_json:
            raise Exception("API响应中没有数据字段")
        
        articles = resp_json.get("data", {})
        if not articles:
            raise Exception("API返回的文章数据为空")
            
    except requests.exceptions.Timeout:
        raise Exception("请求超时，网络连接缓慢")
    except requests.exceptions.ConnectionError:
        raise Exception("网络连接失败，请检查网络")
    except Exception as e:
        # 重新抛出异常，保持原有的错误信息
        raise e
    df = pd.DataFrame(columns='标题 发布时间 展现量 阅读量 点赞量 评论量 账号名称 链接'.split(" "))
    articles = resp_json.get("data", {})
    processed_titles = set()  # 用于跟踪已处理的标题
    
    for article in articles:
        article = article.get("assembleCell", {})
        title = article['itemCell']['articleBase']['title']
        if len(title) > 64:
            title = title[:64] + "..."
        title = title.replace("\n", "").strip()
        
        publishTime = article['itemCell']['articleBase']['publishTime']
        publishTime = datetime.fromtimestamp(publishTime)
        if publishTime.year < 2025:
            continue
            
        article_url = article['itemCell']['articleBase']['articleURL']
        
        # 文章数据
        article_status = json.loads(article['itemCell']['extra']['origin_content'])['ArticleStat']
        comment_count = article_status['CommentCount']
        like_count = article_status['DiggCount']
        impression_count = article_status['ImpressionCount']
        read_count = article_status['GoDetailCount']

        article_type = json.loads(article['itemCell']['extra']['origin_content'])['ArticleAttr']['ArticleType']
        article_type_suffix = {
            "article": "",
            "weitoutiao": "微头条",
            "video": "视频",
            "short_video": "视频",
        }.get(article_type, "未知类型")

        # 创建带后缀的完整标题
        full_title = title + article_type_suffix if article_type_suffix else title
        
        # 检查是否已经处理过相同的标题+URL组合
        title_url_key = f"{full_title}|{article_url}"
        if title_url_key in processed_titles:
            continue
        processed_titles.add(title_url_key)
        
        author = "头条号-"+json.loads(article['itemCell']['extra']['origin_content'])['ArticleAttr']['Extra']['user_name']
        publishTime_str = publishTime.strftime('%Y-%m-%d %H:%M:%S')

        df = df._append({
            "标题": full_title,
            "发布时间": publishTime_str,
            "展现量": impression_count,
            "阅读量": read_count,
            "点赞量": like_count,
            "评论量": comment_count,
            "账号名称": author,
            "链接": article_url,
        }, ignore_index=True)

    return df

def remove_duplicate_records(df):
    """移除重复记录，基于标题+发布时间+账号名称+链接的组合"""
    if df.empty:
        return df
        
    # 创建唯一标识符
    df['unique_key'] = df['标题'] + '|' + df['发布时间'] + '|' + df['账号名称'] + '|' + df['链接']
    
    # 移除重复记录，保留最新的数据（基于索引）
    df = df.drop_duplicates(subset=['unique_key'], keep='last')
    
    # 移除临时列
    df = df.drop('unique_key', axis=1)
    
    return df

def create_unique_id(df):
    """创建统一的唯一标识符"""
    if df.empty:
        return df
    df['unique_id'] = df['标题'] + '|' + df['发布时间'] + '|' + df['账号名称']
    return df

def update_toutiao_publish_history(cookie_str=None,url=None):
    """更新今日头条发布历史数据"""
    import os
    filepath = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "workspace",
        "data",
        "publish_history_for_calendar.csv"
    )
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # 如果文件不存在或为空，则初始化
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        columns = ["标题", "账号名称", "发布时间", "阅读量", "点赞量", "评论量", "链接"]
        empty_df = pd.DataFrame(columns=columns)
        empty_df.to_csv(filepath, index=False, encoding="utf-8-sig")

    # 获取今日头条文章数据
    toutiao_df = fetch_article_by_site(cookie_str,url)
    
    if toutiao_df.empty:
        print("⚠️ 未获取到新数据")
        return True

    # 只保留需要的字段，确保字段顺序一致
    columns = ["标题", "账号名称", "发布时间", "阅读量", "点赞量", "评论量", "链接"]
    toutiao_df = toutiao_df[columns]
    
    # 1. 先对新数据进行内部去重
    print(f"📊 获取到 {len(toutiao_df)} 条新数据")
    toutiao_df = remove_duplicate_records(toutiao_df)
    print(f"🔍 内部去重后剩余 {len(toutiao_df)} 条数据")

    # 读取现有数据
    try:
        old_df = pd.read_csv(filepath, encoding="utf-8-sig")
        if old_df.empty:
            print("📝 现有数据为空，直接保存新数据")
            combined_df = toutiao_df
        else:
            print(f"📚 现有数据 {len(old_df)} 条")
            
            # 2. 为两个数据集创建统一的唯一标识符
            old_df = create_unique_id(old_df)
            toutiao_df = create_unique_id(toutiao_df)
            
            # 3. 找出需要新增的记录（unique_id不在旧数据中的）
            new_records = toutiao_df[~toutiao_df['unique_id'].isin(old_df['unique_id'])]
            print(f"➕ 发现 {len(new_records)} 条新记录")
            
            # 4. 找出需要更新的记录（unique_id在旧数据中的）
            existing_records = toutiao_df[toutiao_df['unique_id'].isin(old_df['unique_id'])]
            print(f"🔄 发现 {len(existing_records)} 条需要更新的记录")
            
            if not existing_records.empty:
                # 更新已存在的记录
                for _, new_row in existing_records.iterrows():
                    mask = old_df['unique_id'] == new_row['unique_id']
                    old_df.loc[mask, ['阅读量', '点赞量', '评论量']] = [
                        new_row['阅读量'], 
                        new_row['点赞量'], 
                        new_row['评论量']
                    ]
                print("✅ 已更新现有记录的数据")
            
            # 5. 合并新记录和更新后的旧记录
            if not new_records.empty:
                # 移除unique_id列，保持原有格式
                new_records = new_records.drop('unique_id', axis=1)
                old_df = old_df.drop('unique_id', axis=1)
                combined_df = pd.concat([old_df, new_records], ignore_index=True)
                print(f"🔗 合并后共 {len(combined_df)} 条记录")
            else:
                combined_df = old_df.drop('unique_id', axis=1)
                print("ℹ️ 没有新记录需要添加")
                
    except pd.errors.EmptyDataError:
        print("📝 现有数据为空，直接保存新数据")
        combined_df = toutiao_df

    # 6. 最终去重：基于标题+发布时间+账号名称
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['标题', '发布时间', '账号名称'], keep='last')
    after_dedup = len(combined_df)
    
    if before_dedup != after_dedup:
        print(f"🧹 最终去重：移除 {before_dedup - after_dedup} 条重复记录")
    
    # 7. 使用自定义去重函数进行最终清理
    before_final_dedup = len(combined_df)
    combined_df = remove_duplicate_records(combined_df)
    after_final_dedup = len(combined_df)
    
    if before_final_dedup != after_final_dedup:
        print(f"🧽 最终清理：移除 {before_final_dedup - after_final_dedup} 条重复记录")
    
    # 8. 按发布时间排序
    combined_df['发布时间'] = pd.to_datetime(combined_df['发布时间'])
    combined_df = combined_df.sort_values('发布时间', ascending=False)
    combined_df['发布时间'] = combined_df['发布时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # 9. 保存数据
    combined_df.to_csv(filepath, index=False, encoding="utf-8-sig")
    print(f"💾 数据已保存到 {filepath}，共 {len(combined_df)} 条记录")
    return True

if __name__ == "__main__":
    update_toutiao_publish_history(
        cookie_str="""
tt_webid=7521987389596075570; _ga=GA1.1.1598848217.1753344798; is_staff_user=false; gfkadpd=1231,25897; ttcid=328c07b7ca7c49bf8dc07f5eddc200b125; csrf_session_id=df0622c6faddc708a0ebc87ea42d1342; s_v_web_id=verify_mf3qbrr8_8Yy5ahpv_PmU7_4Bo5_8ebj_o7U4OodlpWeY; tt_scid=N8ppakwP24pl6tyEd5cvtYFf-hPiZ1m4s6l-0.1Pnxo134zkg9ZHJ-HOGbdHI6mcfd80; passport_csrf_token=20061e7643ebbeca095c098f9276f406; passport_csrf_token_default=20061e7643ebbeca095c098f9276f406; _ga_QEHZPBE5HH=GS2.1.s1756970354$o12$g1$t1756971985$j60$l0$h0; passport_mfa_token=CjAJWSMZ8Odp3cOdicWpD%2BcuYeo7adS3e5g3WkGj3fAI2UvJ9bX0QqxFFHb9UYuahocaSgo8AAAAAAAAAAAAAE9v4oxaVwcYyP3PQpB7RnmsK46mtIqPYs0H90frrI1JwMEf2XvAni6MDPkuYwXpOMAJEJyk%2Bw0Y9rHRbCACIgEDutBNXA%3D%3D; d_ticket=7f084b5eaef84e7998eec8c9bf5f9bb52680a; n_mh=Ibfguk1p9RJdSVK2ychBzXbStl9jDnK1HF9SpJ9JK5U; sso_uid_tt=4f4b5c304b60b8a772139d25e83c2a10; sso_uid_tt_ss=4f4b5c304b60b8a772139d25e83c2a10; toutiao_sso_user=631365540fee7f96a161c0905d74f3d9; toutiao_sso_user_ss=631365540fee7f96a161c0905d74f3d9; sid_ucp_sso_v1=1.0.0-KDM4ZDY0YmEyYjZjNTVhNWUzYmMyMTdiNGJmNTIzOGFjMzM5Mjk1NjAKHgjrsZC23vV4EO2H5cUGGM8JIAww7tn55gU4AkDvBxoCaGwiIDYzMTM2NTU0MGZlZTdmOTZhMTYxYzA5MDVkNzRmM2Q5; ssid_ucp_sso_v1=1.0.0-KDM4ZDY0YmEyYjZjNTVhNWUzYmMyMTdiNGJmNTIzOGFjMzM5Mjk1NjAKHgjrsZC23vV4EO2H5cUGGM8JIAww7tn55gU4AkDvBxoCaGwiIDYzMTM2NTU0MGZlZTdmOTZhMTYxYzA5MDVkNzRmM2Q5; odin_tt=e52e06d6f667fba5b9c9195e41472a4d37e2d7d6e875a7d70f97b6e99973d8f4d15ee773c5f3360c007ffdd4d469d0b267481c7ecf8a2e797e91624a847ab4af; sid_guard=2cd96b914ad93c4827a5957a99d0362a%7C1756972014%7C5184001%7CMon%2C+03-Nov-2025+07%3A46%3A55+GMT; uid_tt=4b5d9d0a61563c9ce3c1f741a22d9c85; uid_tt_ss=4b5d9d0a61563c9ce3c1f741a22d9c85; sid_tt=2cd96b914ad93c4827a5957a99d0362a; sessionid=2cd96b914ad93c4827a5957a99d0362a; sessionid_ss=2cd96b914ad93c4827a5957a99d0362a; session_tlb_tag=sttt%7C7%7CLNlrkUrZPEgnpZV6mdA2Kv________-tuaz-kb3hRMQNVsbHi0jcZlEMHv9oq6P-IdBOv0ClK-U%3D; sid_ucp_v1=1.0.0-KDczNDcxN2NjZGM2YjcyYjc1OWQxYzZiMDJlMzM4NmVlNDIxMTVhOGIKGAjrsZC23vV4EO6H5cUGGM8JIAw4AkDvBxoCbHEiIDJjZDk2YjkxNGFkOTNjNDgyN2E1OTU3YTk5ZDAzNjJh; ssid_ucp_v1=1.0.0-KDczNDcxN2NjZGM2YjcyYjc1OWQxYzZiMDJlMzM4NmVlNDIxMTVhOGIKGAjrsZC23vV4EO6H5cUGGM8JIAw4AkDvBxoCbHEiIDJjZDk2YjkxNGFkOTNjNDgyN2E1OTU3YTk5ZDAzNjJh; ttwid=1%7CFIb8XOAcosIceiGnsMHDreVkYcf6QSlkstXTMLOl7ZQ%7C1756972015%7C39e6ead5243e77421496530538191109848029ea7045a1eabd293a816eb7b121
        """
        ,url="""
https://mp.toutiao.com/api/feed/mp_provider/v1/?provider_type=mp_provider&aid=13&app_name=news_article&category=mp_all&channel=&stream_api_version=88&genre_type_switch=%7B%22repost%22%3A1%2C%22small_video%22%3A1%2C%22toutiao_graphic%22%3A1%2C%22weitoutiao%22%3A1%2C%22xigua_video%22%3A1%7D&device_platform=pc&platform_id=0&visited_uid=531811017169131&offset=0&count=10&keyword=&client_extra_params=%7B%22category%22%3A%22mp_all%22%2C%22real_app_id%22%3A%221231%22%2C%22need_forward%22%3A%22true%22%2C%22offset_mode%22%3A%221%22%2C%22page_index%22%3A%221%22%2C%22status%22%3A%228%22%2C%22source%22%3A%220%22%7D&app_id=1231
        """
        )