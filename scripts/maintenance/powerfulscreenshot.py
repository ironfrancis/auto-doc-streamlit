import requests
from urllib.parse import urlencode

def search_unsplash(api_key, query, per_page=5):
    base_url = "https://api.unsplash.com/search/photos"
    headers = {
        "Authorization": f"Client-ID {api_key}"
    }
    params = {
        "query": query,
        "per_page": per_page
    }

    response = requests.get(f"{base_url}?{urlencode(params)}", headers=headers)
    response.raise_for_status()

    results = response.json()["results"]
    return [result["urls"]["regular"] for result in results]

# 使用示例
api_key = "K15fQ88g2F5n-OAIZ0ZxInaqCZsMsXLm8H0mUftKVbw"  # 替换为你的Unsplash API密钥
images = search_unsplash(api_key, """

""")
for img_url in images:
    print(img_url)