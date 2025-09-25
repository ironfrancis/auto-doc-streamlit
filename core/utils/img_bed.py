import requests
import tempfile
import os
from urllib.parse import urljoin
from typing import Optional, Tuple

def upload_image_to_bed(image_path: str) -> Optional[str]:
    """
    将本地图片上传到图床

    Args:
        image_path: 本地图片文件路径

    Returns:
        图床链接，如果上传失败则返回None
    """
    try:
        url = 'https://img.scdn.io/api/v1.php'

        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(url, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if result.get('success') and 'url' in result:
                return result['url']
            else:
                print(f"上传失败: {result}")
                return None
        else:
            print(f"HTTP错误 {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print(f"上传图片到图床失败: {str(e)}")
        return None

def upload_image_from_url(image_url: str, base_url: Optional[str] = None) -> Optional[str]:
    """
    从URL下载图片并上传到图床

    Args:
        image_url: 图片URL
        base_url: 基础URL，用于处理相对路径

    Returns:
        图床链接，如果处理失败则返回None
    """
    try:
        # 处理相对URL
        if not image_url.startswith(('http://', 'https://')) and base_url:
            image_url = urljoin(base_url, image_url)

        # 下载图片
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(image_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            # 上传到图床
            bed_url = upload_image_to_bed(tmp_file_path)
            return bed_url
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_file_path)
            except:
                pass

    except Exception as e:
        print(f"处理图片URL失败 {image_url}: {str(e)}")
        return None

def scdn_bed(img_url: str) -> Optional[str]:
    """
    兼容性函数：上传图片URL到图床

    Args:
        img_url: 图片URL

    Returns:
        图床链接
    """
    return upload_image_from_url(img_url)

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

if __name__ == "__main__":
    test_upload()