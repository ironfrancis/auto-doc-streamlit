import requests
import tempfile
import os
import json
from urllib.parse import urljoin
from typing import Optional, Tuple, Dict, List

def load_image_beds_config() -> List[Dict]:
    """
    加载图床配置文件
    
    Returns:
        图床配置列表
    """
    try:
        # 优先使用 simple_paths 提供的 CONFIG_DIR（workspace/data/json）
        config_paths: List[str] = []
        try:
            from simple_paths import get_config_dir
            config_dir = get_config_dir()
            config_paths.append(os.path.join(config_dir, "image_beds.json"))
        except Exception:
            pass

        # 其次回退到仓库 config 目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        config_paths.append(os.path.join(project_root, "config", "image_beds.json"))

        # 依次尝试读取
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    print(f"读取图床配置: {path}")
                    return config.get("image_beds", [])
                except Exception as e:
                    print(f"读取图床配置失败 {path}: {e}")
                    continue

        print(f"未找到图床配置文件，已尝试: {config_paths}")
        return []
    except Exception as e:
        print(f"加载图床配置失败: {str(e)}")
        return []

def get_default_image_bed() -> Optional[Dict]:
    """
    获取默认图床配置
    
    Returns:
        默认图床配置或None
    """
    image_beds = load_image_beds_config()
    # 1) 优先返回“默认且启用”的图床
    for bed in image_beds:
        if bed.get("default") and bed.get("enabled", True):
            return bed
    # 2) 若没有默认项，则返回第一个启用的图床，作为兜底
    for bed in image_beds:
        if bed.get("enabled", True):
            return bed
    # 3) 均不可用则返回 None
    return None

def upload_to_lsky(image_path: str, api_url: str, token: str) -> Optional[str]:
    """
    上传图片到 Lsky Pro
    
    Args:
        image_path: 本地图片文件路径
        api_url: Lsky API 地址（如 https://example.com/api/v1/upload）
        token: Bearer Token
    
    Returns:
        图片URL或None
    """
    try:
        # 规范化 Lsky API 地址：若未以 /upload 结尾，自动补全
        normalized_url = api_url.rstrip('/')
        if not normalized_url.endswith('upload'):
            normalized_url = f"{normalized_url}/upload"
            print(f"  API地址已规范化: {api_url} -> {normalized_url}")
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"  文件不存在: {image_path}")
            return None
        
        file_size = os.path.getsize(image_path)
        print(f"  准备上传文件: {image_path} ({file_size} bytes)")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        }
        print(f"  发送请求到: {normalized_url}")
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(normalized_url, files=files, headers=headers, timeout=30)
        
        print(f"  响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  响应内容: {result}")
            
            if result.get('status') and 'data' in result:
                image_url = result['data'].get('links', {}).get('url')
                if image_url:
                    print(f"  上传成功，图片URL: {image_url}")
                    return image_url
                else:
                    print(f"  响应中没有图片URL，完整响应: {result}")
                    return None
            else:
                error_msg = result.get('message', 'Unknown error')
                print(f"  Lsky上传失败: {error_msg}")
                print(f"  完整响应: {result}")
                return None
        else:
            print(f"  Lsky HTTP错误 {response.status_code}")
            print(f"  响应内容: {response.text[:500]}")  # 只打印前500字符
            return None
            
    except requests.exceptions.Timeout:
        print(f"  上传到Lsky超时: {api_url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  上传到Lsky请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"  上传图片到Lsky异常: {str(e)}")
        import traceback
        print(f"  异常详情: {traceback.format_exc()}")
        return None

def upload_to_scdn(image_path: str, api_url: str) -> Optional[str]:
    """
    上传图片到 SCDN 图床
    
    Args:
        image_path: 本地图片文件路径
        api_url: SCDN API 地址
    
    Returns:
        图片URL或None
    """
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(api_url, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result.get('success') and 'url' in result:
                return result['url']
            else:
                print(f"SCDN上传失败: {result}")
                return None
        else:
            print(f"SCDN HTTP错误 {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"上传图片到SCDN失败: {str(e)}")
        return None

def upload_image_to_bed(image_path: str, bed_config: Optional[Dict] = None) -> Optional[str]:
    """
    将本地图片上传到图床

    Args:
        image_path: 本地图片文件路径
        bed_config: 图床配置，如果为None则使用默认图床

    Returns:
        图床链接，如果上传失败则返回None
    """
    try:
        # 如果没有提供图床配置，使用默认图床
        if bed_config is None:
            print("  未提供图床配置，尝试获取默认图床...")
            bed_config = get_default_image_bed()
            if bed_config is None:
                print("  ✗ 没有找到默认图床配置")
                return None
            print(f"  使用默认图床: {bed_config.get('name', 'Unknown')}")
        
        bed_type = bed_config.get("type", "scdn")
        api_url = bed_config.get("api_url", "")
        token = bed_config.get("token", "")
        
        print(f"  图床类型: {bed_type}")
        print(f"  API地址: {api_url}")
        
        if not api_url:
            print("  ✗ 图床API地址为空")
            return None
        
        # 根据图床类型调用对应的上传函数
        if bed_type == "lsky":
            if not token:
                print("  ✗ Lsky图床需要认证Token")
                return None
            print(f"  使用Lsky图床上传...")
            return upload_to_lsky(image_path, api_url, token)
        elif bed_type == "scdn":
            print(f"  使用SCDN图床上传...")
            return upload_to_scdn(image_path, api_url)
        else:
            print(f"  ✗ 不支持的图床类型: {bed_type}")
            return None
            
    except Exception as e:
        print(f"  ✗ 上传图片到图床异常: {str(e)}")
        import traceback
        print(f"  异常详情: {traceback.format_exc()}")
        return None

def upload_image_from_url(image_url: str, base_url: Optional[str] = None, bed_config: Optional[Dict] = None) -> Optional[str]:
    """
    从URL下载图片并上传到图床

    Args:
        image_url: 图片URL
        base_url: 基础URL，用于处理相对路径
        bed_config: 图床配置，如果为None则使用默认图床

    Returns:
        图床链接，如果处理失败则返回None
    """
    tmp_file_path = None
    try:
        # 处理相对URL
        original_url = image_url
        if not image_url.startswith(('http://', 'https://')) and base_url:
            image_url = urljoin(base_url, image_url)
            print(f"  相对URL已转换: {original_url} -> {image_url}")

        # 下载图片
        print(f"  开始下载图片: {image_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(image_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        file_size = int(response.headers.get('content-length', 0))
        if file_size > 0:
            print(f"  图片下载成功，大小: {file_size} bytes")
        else:
            print(f"  图片下载成功，大小: 未知")

        # 根据Content-Type确定文件扩展名
        content_type = response.headers.get('content-type', '').lower()
        print(f"  Content-Type: {content_type}")
        if 'jpeg' in content_type or 'jpg' in content_type:
            suffix = '.jpg'
        elif 'png' in content_type:
            suffix = '.png'
        elif 'webp' in content_type:
            suffix = '.webp'
        elif 'gif' in content_type:
            suffix = '.gif'
        else:
            # 默认使用.jpg，大多数图床都支持
            suffix = '.jpg'
        print(f"  使用文件扩展名: {suffix}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        print(f"  临时文件已创建: {tmp_file_path}")

        # 上传到图床
        print(f"  开始上传到图床...")
        if bed_config:
            print(f"  图床配置: {bed_config.get('name', 'Unknown')} ({bed_config.get('type', 'Unknown')})")
        bed_url = upload_image_to_bed(tmp_file_path, bed_config)
        
        if bed_url:
            print(f"  图床上传成功: {bed_url}")
        else:
            print(f"  图床上传失败: 返回值为None")
        
        return bed_url

    except requests.exceptions.Timeout:
        print(f"  下载图片超时: {image_url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  下载图片请求失败: {image_url} - {str(e)}")
        return None
    except Exception as e:
        print(f"  处理图片URL失败 {image_url}: {str(e)}")
        import traceback
        print(f"  异常详情: {traceback.format_exc()}")
        return None
    finally:
        # 清理临时文件
        if tmp_file_path:
            try:
                os.unlink(tmp_file_path)
                print(f"  临时文件已删除: {tmp_file_path}")
            except Exception as e:
                print(f"  删除临时文件失败: {tmp_file_path} - {str(e)}")

def scdn_bed(img_url: str) -> Optional[str]:
    """
    兼容性函数：上传图片URL到图床

    Args:
        img_url: 图片URL

    Returns:
        图床链接
    """
    return upload_image_from_url(img_url)

def get_image_bed_by_id(bed_id: str) -> Optional[Dict]:
    """
    根据ID获取图床配置
    
    Args:
        bed_id: 图床ID
    
    Returns:
        图床配置或None
    """
    image_beds = load_image_beds_config()
    for bed in image_beds:
        if bed.get("id") == bed_id and bed.get("enabled", True):
            return bed
    return None

def list_available_image_beds() -> List[Dict]:
    """
    获取所有可用的图床列表
    
    Returns:
        可用图床配置列表
    """
    image_beds = load_image_beds_config()
    return [bed for bed in image_beds if bed.get("enabled", True)]

# 测试函数
def test_upload():
    """测试上传功能"""
    # 使用测试图片
    file_path = '/Users/xuchao/Projects/Auto-doc-streamlit/core/utils/test.png'
    if os.path.exists(file_path):
        result = upload_image_to_bed(file_path)
        print(f"测试上传结果: {result}")
        return result
    else:
        print("测试图片不存在")
        return None

def test_lsky_upload():
    """测试Lsky上传功能"""
    file_path = '/Users/xuchao/Projects/Auto-doc-streamlit/core/utils/test.png'
    if os.path.exists(file_path):
        # 这里需要替换为实际的Lsky配置
        api_url = "https://your-lsky-domain.com/api/v1/upload"
        token = "your-bearer-token"
        result = upload_to_lsky(file_path, api_url, token)
        print(f"Lsky测试上传结果: {result}")
        return result
    else:
        print("测试图片不存在")
        return None

if __name__ == "__main__":
    test_upload()