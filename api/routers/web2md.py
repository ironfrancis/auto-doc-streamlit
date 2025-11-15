"""
网页转Markdown API路由
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException
from typing import Optional
from api.schemas.web2md import Web2MDRequest, Web2MDResponse
from core.web2md.enhanced_web2md import extract_markdown_from_url

router = APIRouter(prefix="/api/web2md", tags=["web2md"])


@router.post("/fetch", response_model=Web2MDResponse)
async def fetch_web_to_markdown(request: Web2MDRequest):
    """
    从网页提取Markdown内容
    
    参数说明：
    - url: 要提取内容的网页URL
    - scope: 提取范围（'all' 或 'viewport'）
    - wait_time: 等待页面加载的时间（秒）
    - scroll: 是否滚动页面
    - scroll_pause: 每次滚动后的暂停时间（秒）
    - viewport_height: 浏览器视口高度（像素）
    - remove_selectors: 要移除的元素的CSS选择器列表
    - image_handling: 图片处理方式
    - show_image_errors: 是否显示图片处理错误
    - image_bed_id: 图床ID（可选）
    """
    try:
        # 处理URL格式
        url = request.url
        if not url.startswith(("http://", "https://")):
            if not url.startswith("file:/"):
                url = f"https://{url}"
        
        # 获取图床配置（如果需要）
        image_bed_config = None
        if request.image_handling == "Upload to Image Bed":
            if request.image_bed_id:
                try:
                    from core.utils.img_bed import get_image_bed_by_id
                    image_bed_config = get_image_bed_by_id(request.image_bed_id)
                    if not image_bed_config:
                        return Web2MDResponse(
                            success=False,
                            message=f"未找到ID为 '{request.image_bed_id}' 的图床配置"
                        )
                except ImportError:
                    return Web2MDResponse(
                        success=False,
                        message="图床模块未找到，无法使用图床上传功能"
                    )
            else:
                # 使用默认图床
                try:
                    from core.utils.img_bed import get_default_image_bed
                    image_bed_config = get_default_image_bed()
                    if not image_bed_config:
                        return Web2MDResponse(
                            success=False,
                            message="未找到默认图床配置，请设置默认图床或提供图床ID"
                        )
                except ImportError:
                    return Web2MDResponse(
                        success=False,
                        message="图床模块未找到，无法使用图床上传功能"
                    )
        
        # 调用提取函数
        result = extract_markdown_from_url(
            url=url,
            scope=request.scope,
            wait_time=request.wait_time,
            scroll=request.scroll,
            scroll_pause=request.scroll_pause,
            viewport_height=request.viewport_height,
            remove_selectors=request.remove_selectors,
            image_handling=request.image_handling,
            show_image_errors=request.show_image_errors,
            image_bed_config=image_bed_config
        )
        
        # 解析返回结果
        if result and len(result) == 2:
            markdown, saved_file_path = result
        else:
            markdown, saved_file_path = None, None
        
        if markdown:
            # 计算统计信息
            stats = {
                "characters": len(markdown),
                "words": len(markdown.split()),
                "lines": markdown.count('\n') + 1
            }
            
            return Web2MDResponse(
                success=True,
                markdown=markdown,
                saved_file_path=saved_file_path,
                stats=stats
            )
        else:
            return Web2MDResponse(
                success=False,
                message="提取失败，请检查URL和网络连接"
            )
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return Web2MDResponse(
            success=False,
            message=f"提取过程中发生错误: {str(e)}",
        )


