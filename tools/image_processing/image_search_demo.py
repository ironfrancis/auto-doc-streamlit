import requests
import json
import os
from typing import List, Dict

class ImageSearchAPI:
    """图片搜索API集成类"""
    
    def __init__(self):
        # API密钥配置（实际使用时需要申请）
        self.unsplash_access_key = "YOUR_UNSPLASH_ACCESS_KEY"
        self.pexels_api_key = "YOUR_PEXELS_API_KEY"
        self.bing_subscription_key = "YOUR_BING_SUBSCRIPTION_KEY"
    
    def search_unsplash(self, query: str, count: int = 10) -> List[Dict]:
        """使用Unsplash API搜索图片"""
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": count,
                "client_id": self.unsplash_access_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for photo in data.get("results", []):
                results.append({
                    "id": photo["id"],
                    "url": photo["urls"]["regular"],
                    "thumb": photo["urls"]["thumb"],
                    "alt": photo.get("alt_description", ""),
                    "author": photo["user"]["name"],
                    "source": "unsplash"
                })
            
            return results
            
        except Exception as e:
            print(f"Unsplash API错误: {e}")
            return []
    
    def search_pexels(self, query: str, count: int = 10) -> List[Dict]:
        """使用Pexels API搜索图片"""
        try:
            url = "https://api.pexels.com/v1/search"
            headers = {
                "Authorization": self.pexels_api_key
            }
            params = {
                "query": query,
                "per_page": count
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for photo in data.get("photos", []):
                results.append({
                    "id": photo["id"],
                    "url": photo["src"]["large"],
                    "thumb": photo["src"]["medium"],
                    "alt": photo.get("alt", ""),
                    "author": photo["photographer"],
                    "source": "pexels"
                })
            
            return results
            
        except Exception as e:
            print(f"Pexels API错误: {e}")
            return []
    
    def search_bing(self, query: str, count: int = 10) -> List[Dict]:
        """使用Bing Image Search API搜索图片"""
        try:
            url = "https://api.bing.microsoft.com/v7.0/images/search"
            headers = {
                "Ocp-Apim-Subscription-Key": self.bing_subscription_key
            }
            params = {
                "q": query,
                "count": count,
                "mkt": "zh-CN"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for image in data.get("value", []):
                results.append({
                    "id": image.get("imageId", ""),
                    "url": image["contentUrl"],
                    "thumb": image.get("thumbnailUrl", image["contentUrl"]),
                    "alt": image.get("name", ""),
                    "author": "Bing",
                    "source": "bing"
                })
            
            return results
            
        except Exception as e:
            print(f"Bing API错误: {e}")
            return []
    
    def search_all_sources(self, query: str, count: int = 10) -> List[Dict]:
        """从所有来源搜索图片"""
        all_results = []
        
        # 并行搜索多个API
        unsplash_results = self.search_unsplash(query, count)
        pexels_results = self.search_pexels(query, count)
        bing_results = self.search_bing(query, count)
        
        all_results.extend(unsplash_results)
        all_results.extend(pexels_results)
        all_results.extend(bing_results)
        
        # 去重和排序
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        
        return unique_results[:count * 3]  # 返回最多3倍数量的结果
    
    def download_image(self, url: str, filename: str) -> bool:
        """下载图片到本地"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 确保目录存在
            os.makedirs("downloaded_images", exist_ok=True)
            
            filepath = os.path.join("downloaded_images", filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"图片已下载: {filepath}")
            return True
            
        except Exception as e:
            print(f"下载图片失败: {e}")
            return False

def demo_image_search():
    """演示图片搜索功能"""
    searcher = ImageSearchAPI()
    
    # 示例搜索
    query = "artificial intelligence technology"
    print(f"搜索关键词: {query}")
    
    results = searcher.search_all_sources(query, count=5)
    
    print(f"\n找到 {len(results)} 张图片:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['alt']} (来源: {result['source']})")
        print(f"   链接: {result['url']}")
        print(f"   作者: {result['author']}")
        print()

if __name__ == "__main__":
    demo_image_search() 