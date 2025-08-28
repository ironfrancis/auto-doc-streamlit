from datetime import datetime
from operator import index

import pandas as pd
import requests
import json
import os

def fetch_article_by_site():
    nums = 100
    url = f"""
    https://mp.toutiao.com/api/feed/mp_provider/v1/?provider_type=mp_provider&aid=13&app_name=news_article&category=mp_all&channel=&stream_api_version=88&genre_type_switch=%7B%22repost%22%3A1%2C%22small_video%22%3A1%2C%22toutiao_graphic%22%3A1%2C%22weitoutiao%22%3A1%2C%22xigua_video%22%3A1%7D&device_platform=pc&platform_id=0&visited_uid=531811017169131&offset=0&count={nums}&keyword=&client_extra_params=%7B%22category%22%3A%22mp_all%22%2C%22real_app_id%22%3A%221231%22%2C%22need_forward%22%3A%22true%22%2C%22offset_mode%22%3A
    """
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "cookie":"tt_webid=7539911727950546459; gfkadpd=24,6457; ttcid=2c75d73a16b0490f95aa9d685138a95073; local_city_cache=%E4%B8%9C%E8%8E%9E; x-web-secsdk-uid=86352696-4552-4a50-9883-2f4af161f4e2; csrftoken=f58f6b6b98734f668c1a64e6c931d376; _ga=GA1.1.558646257.1755522515; s_v_web_id=verify_meh4s1t8_ujv33Zcc_e7RL_4cNL_B9II_0scc19hf6OVt; passport_csrf_token=af42e25d6bbf2240969c469a365d1f2d; passport_csrf_token_default=af42e25d6bbf2240969c469a365d1f2d; n_mh=Ibfguk1p9RJdSVK2ychBzXbStl9jDnK1HF9SpJ9JK5U; passport_auth_status=99b30789ac645ca430cdeea1c7d7a654%2C; passport_auth_status_ss=99b30789ac645ca430cdeea1c7d7a654%2C; is_staff_user=false; xg_p_tos_token=1f2e3eed33a131887df8f193d1069b7b; d_ticket=1132204294795dab24f9fde4ded2a64199f61; passport_mfa_token=CjAEZN0O5f2qVySKucFYG34DMrox64MeJjradaQknzOzlHCuMGV3NxS6Qj5QTyEpC%2BMaSgo8AAAAAAAAAAAAAE9eRKpBAgNmeaJoCEADXclAEtyyrLNsJ5t0NEAKrbvD6GeqECcNkStDdF3F9fUvSAiJEMnl%2BQ0Y9rHRbCACIgEDW3g1Jg%3D%3D; sso_uid_tt=acaaebf60adf48fa5dc8edf1f27eeac5; sso_uid_tt_ss=acaaebf60adf48fa5dc8edf1f27eeac5; toutiao_sso_user=f771528a7be7911711fb05991f09e7e9; toutiao_sso_user_ss=f771528a7be7911711fb05991f09e7e9; sid_ucp_sso_v1=1.0.0-KDY0MTgyNDI5MWVjMDdiMmRlNDhmZjhhNzM3MDc5NjNlZjAwZjBjZGMKHgjrsZC23vV4EObRjMUGGM8JIAww7tn55gU4AkDvBxoCaGwiIGY3NzE1MjhhN2JlNzkxMTcxMWZiMDU5OTFmMDllN2U5; ssid_ucp_sso_v1=1.0.0-KDY0MTgyNDI5MWVjMDdiMmRlNDhmZjhhNzM3MDc5NjNlZjAwZjBjZGMKHgjrsZC23vV4EObRjMUGGM8JIAww7tn55gU4AkDvBxoCaGwiIGY3NzE1MjhhN2JlNzkxMTcxMWZiMDU5OTFmMDllN2U5; sid_guard=7ab7434ee4c8db711b164dc23be39e7f%7C1755523303%7C5184001%7CFri%2C+17-Oct-2025+13%3A21%3A44+GMT; uid_tt=dddc7778748c22e7bbc44ec6cfb772c1; uid_tt_ss=dddc7778748c22e7bbc44ec6cfb772c1; sid_tt=7ab7434ee4c8db711b164dc23be39e7f; sessionid=7ab7434ee4c8db711b164dc23be39e7f; sessionid_ss=7ab7434ee4c8db711b164dc23be39e7f; session_tlb_tag=sttt%7C12%7CerdDTuTI23EbFk3CO-Oef__________8P_FbyOb5lH8BuZwOJ1fqbnIh4KnwmjOgJatoyiTXj10%3D; sid_ucp_v1=1.0.0-KGYwYjA5MWE0NTNiZWJhY2ExNDRmMjAxNDNhMWQwN2NjYjA1MDU0YzcKGAjrsZC23vV4EOfRjMUGGM8JIAw4AkDvBxoCbGYiIDdhYjc0MzRlZTRjOGRiNzExYjE2NGRjMjNiZTM5ZTdm; ssid_ucp_v1=1.0.0-KGYwYjA5MWE0NTNiZWJhY2ExNDRmMjAxNDNhMWQwN2NjYjA1MDU0YzcKGAjrsZC23vV4EOfRjMUGGM8JIAw4AkDvBxoCbGYiIDdhYjc0MzRlZTRjOGRiNzExYjE2NGRjMjNiZTM5ZTdm; odin_tt=839c1c511c57e9e59c35daaf701b95cfe4bb8cf59f271d1df910e0202421ea5a7b11b8aafeeb89475a801fae0bb526c0; tt_scid=0C6hilFQCN9t2c6LSWadZVB5eEmoBJm3qv5o8Qm74tr2YXtFxdlw53gX-2P-FOKldcfc; _ga_QEHZPBE5HH=GS2.1.s1755528770$o2$g1$t1755528932$j39$l0$h0; ttwid=1%7CmHb6tdhvXg6C6Q-2y5QEWZh1cZpIhDCMrfF_TkpFlyk%7C1755528933%7C65cbc26f140cc4d1e72e92a37bae83c262e9ea435bfdccfb833a49531bd1f43f; tt_anti_token=JTpmC7nlph9s9t-ab5ebc864a68c2be0ef43d4e230cded694dc48117bb03ba68667c6c7e8cad05e"
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
    # 创建唯一标识符
    df['unique_key'] = df['标题'] + '|' + df['发布时间'] + '|' + df['账号名称'] + '|' + df['链接']
    
    # 移除重复记录，保留最新的数据（基于索引）
    df = df.drop_duplicates(subset=['unique_key'], keep='last')
    
    # 移除临时列
    df = df.drop('unique_key', axis=1)
    
    return df

def update_toutiao_publish_history():
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
    toutiao_df = fetch_article_by_site()

    # 只保留需要的字段，确保字段顺序一致
    columns = ["标题", "账号名称", "发布时间", "阅读量", "点赞量", "评论量", "链接"]
    toutiao_df = toutiao_df[columns]

    # 如果原表中没有的标题则新增，已存在的标题则更新数据
    try:
        old_df = pd.read_csv(filepath, encoding="utf-8-sig")
        if not old_df.empty:
            # 创建唯一标识符：标题+发布时间+账号名称
            old_df['unique_id'] = old_df['标题'] + '|' + old_df['发布时间'] + '|' + old_df['账号名称']
            toutiao_df['unique_id'] = toutiao_df['标题'] + '|' + toutiao_df['发布时间'] + '|' + toutiao_df['账号名称']
            
            # 找出需要新增的记录（unique_id不在旧数据中的）
            new_records = toutiao_df[~toutiao_df['unique_id'].isin(old_df['unique_id'])]
            
            # 找出需要更新的记录（unique_id在旧数据中的）
            existing_records = toutiao_df[toutiao_df['unique_id'].isin(old_df['unique_id'])]
            
            if not existing_records.empty:
                # 更新已存在的记录
                for _, new_row in existing_records.iterrows():
                    mask = old_df['unique_id'] == new_row['unique_id']
                    old_df.loc[mask, ['阅读量', '点赞量', '评论量']] = [
                        new_row['阅读量'], 
                        new_row['点赞量'], 
                        new_row['评论量']
                    ]
            
            # 合并新记录和更新后的旧记录
            if not new_records.empty:
                # 移除unique_id列，保持原有格式
                new_records = new_records.drop('unique_id', axis=1)
                old_df = old_df.drop('unique_id', axis=1)
                combined_df = pd.concat([old_df, new_records], ignore_index=True)
            else:
                combined_df = old_df.drop('unique_id', axis=1)
        else:
            combined_df = toutiao_df
    except pd.errors.EmptyDataError:
        combined_df = toutiao_df

    # 最终去重：基于标题+发布时间+账号名称
    combined_df = combined_df.drop_duplicates(subset=['标题', '发布时间', '账号名称'], keep='last')
    
    # 使用自定义去重函数进行最终清理
    combined_df = remove_duplicate_records(combined_df)
    
    # 按发布时间排序
    combined_df['发布时间'] = pd.to_datetime(combined_df['发布时间'])
    combined_df = combined_df.sort_values('发布时间', ascending=False)
    combined_df['发布时间'] = combined_df['发布时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    combined_df.to_csv(filepath, index=False, encoding="utf-8-sig")
    return True

if __name__ == "__main__":
    # print(fetch_article_by_site().to_markdown())
    # df = pd.read_csv("../../workspace/data/publish_history.csv")
    # print(df.to_markdown())
    update_toutiao_publish_history()