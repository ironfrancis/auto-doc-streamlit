#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Typora 自定义命令：图片上传到图床
用于在 Typora 中通过自定义命令自动上传图片到配置的图床

使用方法：
1. 在 Typora 中设置：偏好设置 -> 图像 -> 上传服务 -> 自定义命令
2. 命令填写：python /path/to/typora_upload_image.py
3. 确保配置文件 config/image_beds.json 已正确配置
"""

import sys
import os
import json

# 添加项目根目录到 Python 路径，以便导入项目模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from core.utils.img_bed import upload_image_to_bed, get_default_image_bed
except ImportError:
    # 如果导入失败，尝试直接在当前目录查找
    import requests
    import tempfile
    from urllib.parse import urljoin
    from typing import Optional, Dict, List

    def load_image_beds_config() -> List[Dict]:
        """加载图床配置文件"""
        config_paths = [
            os.path.join(current_dir, "config", "image_beds.json"),
            os.path.join(current_dir, "workspace", "data", "json", "image_beds.json"),
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    return config.get("image_beds", [])
                except Exception as e:
                    print(f"读取图床配置失败 {path}: {e}", file=sys.stderr)
                    continue
        
        return []

    def get_default_image_bed() -> Optional[Dict]:
        """获取默认图床配置"""
        image_beds = load_image_beds_config()
        for bed in image_beds:
            if bed.get("default") and bed.get("enabled", True):
                return bed
        for bed in image_beds:
            if bed.get("enabled", True):
                return bed
        return None

    def upload_to_lsky(image_path: str, api_url: str, token: str) -> Optional[str]:
        """上传图片到 Lsky Pro"""
        try:
            normalized_url = api_url.rstrip('/')
            if not normalized_url.endswith('upload'):
                normalized_url = f"{normalized_url}/upload"
            
            if not os.path.exists(image_path):
                return None
            
            headers = {
                'Authorization': f'Bearer 1|Wx59l8hVR5Xxcb7XyzJP7uCUgEqLNal1RMUbEahR',
                'Accept': 'application/json'
            }
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(normalized_url, files=files, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') and 'data' in result:
                    image_url = result['data'].get('links', {}).get('url')
                    if image_url:
                        return image_url
            return None
        except Exception:
            return None

    def upload_to_scdn(image_path: str, api_url: str) -> Optional[str]:
        """上传图片到 SCDN 图床"""
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(api_url, files=files, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'url' in result:
                    return result['url']
            return None
        except Exception:
            return None

    def upload_image_to_bed(image_path: str, bed_config: Optional[Dict] = None) -> Optional[str]:
        """将本地图片上传到图床"""
        try:
            if bed_config is None:
                bed_config = get_default_image_bed()
                if bed_config is None:
                    return None
            
            bed_type = bed_config.get("type", "scdn")
            api_url = bed_config.get("api_url", "")
            token = bed_config.get("token", "")
            
            if not api_url:
                return None
            
            if bed_type == "lsky":
                if not token:
                    return None
                return upload_to_lsky(image_path, api_url, token)
            elif bed_type == "scdn":
                return upload_to_scdn(image_path, api_url)
            else:
                return None
        except Exception:
            return None


def main():
    """
    主函数：处理 Typora 传递的图片路径并上传到图床
    """
    # Typora 会将图片路径作为第一个参数传递
    if len(sys.argv) < 2:
        print("错误：未提供图片路径", file=sys.stderr)
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"错误：图片文件不存在: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    # 检查是否为有效的图片文件
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in valid_extensions:
        print(f"错误：不支持的图片格式: {file_ext}", file=sys.stderr)
        sys.exit(1)
    
    # 获取默认图床配置
    bed_config = get_default_image_bed()
    if bed_config is None:
        print("错误：未找到可用的图床配置，请检查 config/image_beds.json", file=sys.stderr)
        sys.exit(1)
    
    # 上传图片
    try:
        image_url = upload_image_to_bed(image_path, bed_config)
        
        if image_url:
            # 输出 Markdown 格式的图片链接（Typora 会接收这个输出）
            print(image_url)
            sys.exit(0)
        else:
            print(f"错误：图片上传失败", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"错误：上传过程中发生异常: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

