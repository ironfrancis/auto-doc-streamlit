import requests

def fetch_toutiao_feed(offset=0, count=10, keyword=None,cookies=None):
    """
    封装今日头条 API 请求
    
    Args:
        offset (int): 分页偏移量，默认为 0
        count (int): 每页数量，默认为 10
        keyword (str, optional): 搜索关键词，默认为 None
    
    Returns:
        dict: API 返回的 JSON 数据
    """
    url = "https://mp.toutiao.com/api/feed/mp_provider/v1/"
    
    params = {
        "provider_type": "mp_provider",
        "aid": "13",
        "app_name": "news_article",
        "category": "mp_all",
        "channel": "",
        "stream_api_version": "88",
        "genre_type_switch": "{\"repost\":1,\"small_video\":1,\"toutiao_graphic\":1,\"weitoutiao\":1,\"xigua_video\":1}",
        "device_platform": "pc",
        "platform_id": "0",
        "visited_uid": "3484813672855172",
        "offset": offset,
        "count": count,
        "keyword": keyword if keyword else "",
        "client_extra_params": "{\"category\":\"mp_all\",\"real_app_id\":\"1231\",\"need_forward\":\"true\",\"offset_mode\":\"1\",\"page_index\":\"1\",\"status\":\"8\",\"source\":\"0\"}",
        "app_id": "1231"
    }
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9",
        "priority": "u=1, i",
        "referer": "https://mp.toutiao.com/profile_v4/manage/content/all",
        "rpc-persist-bytetim_business_stream_caller": "mp",
        "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    cookies = {
        "tt_webid": "7521987389596075570",
        "_ga": "GA1.1.1598848217.1753344798",
        "is_staff_user": "false",
        "gfkadpd": "1231,25897",
        "ttcid": "328c07b7ca7c49bf8dc07f5eddc200b125",
        "csrf_session_id": "df0622c6faddc708a0ebc87ea42d1342",
        "s_v_web_id": "verify_mf3qbrr8_8Yy5ahpv_PmU7_4Bo5_8ebj_o7U4OodlpWeY",
        "d_ticket": "94414382501e4c026c6758829d774a322680a",
        "n_mh": "Rygl16cNr_J8qqFyeuQoyKIg7Z71pn7aUjAgp-7wmj8",
        "tt_scid": "N8ppakwP24pl6tyEd5cvtYFf-hPiZ1m4s6l-0.1Pnxo134zkg9ZHJ-HOGbdHI6mcfd80",
        "passport_csrf_token": "20061e7643ebbeca095c098f9276f406",
        "passport_csrf_token_default": "20061e7643ebbeca095c098f9276f406",
        "passport_mfa_token": "CjFgD6%2BCBJbrDL0e3jeVSIoIuLTd8bMKaC0Oki25T5X%2FLYRNY86OJ9YAS3dDEOWm0%2FDyGkoKPAAAAAAAAAAAAABPbhTB55CgGBiPI0Y3HIDpK6OgeVTkn1mL94ZuLAUBNpK0kTy%2FEVoTAw%2BdS3NRRNFSZhCgmPsNGPax0WwgAiIBA5p4Cc0%3D",
        "sso_uid_tt": "15f7c996b4b5bcbe99dfe37a96c1821f",
        "sso_uid_tt_ss": "15f7c996b4b5bcbe99dfe37a96c1821f",
        "toutiao_sso_user": "1c20664a6f80e13408d925e019565306",
        "toutiao_sso_user_ss": "1c20664a6f80e13408d925e019565306",
        "sid_ucp_sso_v1": "1.0.0-KGUzZjUzYWFjMmUxZTU1YjBmYWI3NzQ2Y2RiMDY3MjA0YjA4ZDE5NGYKHgiE7dDItq2YBhD8ieDFBhgYIAww6qLaxQY4AkDvBxoCaGwiIDFjMjA2NjRhNmY4MGUxMzQwOGQ5MjVlMDE5NTY1MzA2",
        "ssid_ucp_sso_v1": "1.0.0-KGUzZjUzYWFjMmUxZTU1YjBmYWI3NzQ2Y2RiMDY3MjA0YjA4ZDE5NGYKHgiE7dDItq2YBhD8ieDFBhgYIAww6qLaxQY4AkDvBxoCaGwiIDFjMjA2NjRhNmY4MGUxMzQwOGQ5MjVlMDE5NTY1MzA2",
        "sid_guard": "3715359669da7168d8ee78474b3c8904%7C1756890364%7C5184001%7CSun%2C+02-Nov-2025+09%3A06%3A05+GMT",
        "uid_tt": "4faa4429c863a339e64659ea7f5a82a3",
        "uid_tt_ss": "4faa4429c863a339e64659ea7f5a82a3",
        "sid_tt": "3715359669da7168d8ee78474b3c8904",
        "sessionid": "3715359669da7168d8ee78474b3c8904",
        "sessionid_ss": "3715359669da7168d8ee78474b3c8904",
        "session_tlb_tag": "sttt%7C3%7CNxU1lmnacWjY7nhHSzyJBP_________gi2texHgGEs2lqYvv0FCvz7dqz1ykpHD34G7HXI1dGMY%3D",
        "sid_ucp_v1": "1.0.0-KDU5ZGVhM2MyOTk3ZGJlYWI5OThkNjE0NWQ2YjJhNGRlYWViZDU4Y2IKGAiE7dDItq2YBhD8ieDFBhgYIAw4AkDvBxoCbHEiIDM3MTUzNTk2NjlkYTcxNjhkOGVlNzg0NzRiM2M4OTA0",
        "ssid_ucp_v1": "1.0.0-KDU5ZGVhM2MyOTk3ZGJlYWI5OThkNjE0NWQ2YjJhNGRlYWViZDU4Y2IKGAiE7dDItq2YBhD8ieDFBhgYIAw4AkDvBxoCbHEiIDM3MTUzNTk2NjlkYTcxNjhkOGVlNzg0NzRiM2M4OTA0",
        "odin_tt": "a55418e1749d8e47e964cd5fee14a54a628b9f85f254d90306d146b8f3dbcc5e69860cc81e9a2759c9f7c19227809c7b",
        "_ga_QEHZPBE5HH": "GS2.1.s1756912767$o11$g0$t1756912767$j60$l0$h0",
        "ttwid": "1%7CFIb8XOAcosIceiGnsMHDreVkYcf6QSlkstXTMLOl7ZQ%7C1756967087%7C6a725c10652f5cac64e1a3cb6310f211232d564181f7b3c0719addd4d1ebe0a5"
    }
    
    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    response.raise_for_status()
    return response.json()

# 示例用法
if __name__ == "__main__":
    result = fetch_toutiao_feed(offset=0, count=10)
    print(result)