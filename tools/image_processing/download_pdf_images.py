import requests
import os
from urllib.parse import urlparse
import time

def download_pdf_images():
    """下载PDF预览图片到本地"""
    
    # 创建保存目录
    save_dir = "downloaded_pdf_images"
    os.makedirs(save_dir, exist_ok=True)
    
    # 基础URL
    base_url = "https://pubres.wshoto.com/base-material-server/wx28adff7eb4c338ad/17539294198722025世界人工智能大会综合专业报告.pdf"
    
    # 下载参数
    params = {
        "ci-process": "doc-preview",
        "imageDpi": "600DPI",
        "scale": "200",
        "dstType": "png"
    }
    
    # 下载所有页面（1-44页）
    total_pages = 44
    downloaded_count = 0
    
    print(f"开始下载 {total_pages} 页PDF预览图片...")
    
    for page in range(1, total_pages + 1):
        try:
            # 构建完整URL
            params["page"] = page
            url = f"{base_url}?ci-process={params['ci-process']}&page={page}&imageDpi={params['imageDpi']}&scale={params['scale']}&dstType={params['dstType']}"
            
            # 文件名
            filename = f"page_{page:02d}.png"
            filepath = os.path.join(save_dir, filename)
            
            print(f"正在下载第 {page} 页: {filename}")
            
            # 发送请求
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            downloaded_count += 1
            print(f"✅ 第 {page} 页下载完成")
            
            # 添加延迟避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ 第 {page} 页下载失败: {str(e)}")
            continue
    
    print(f"\n下载完成！成功下载 {downloaded_count}/{total_pages} 页")
    print(f"文件保存在: {os.path.abspath(save_dir)}")
    
    return save_dir

if __name__ == "__main__":
    download_pdf_images() 