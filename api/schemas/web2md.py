from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal


class Web2MDRequest(BaseModel):
    """网页转Markdown请求模型"""
    url: str = Field(..., description="要提取内容的网页URL")
    scope: Literal["all", "viewport"] = Field(
        default="viewport",
        description="提取范围: 'all'(所有内容) 或 'viewport'(仅视口内容)"
    )
    wait_time: int = Field(
        default=5,
        ge=3,
        le=30,
        description="等待页面加载的时间（秒）"
    )
    scroll: bool = Field(
        default=True,
        description="是否滚动页面以加载懒加载内容"
    )
    scroll_pause: float = Field(
        default=1.0,
        ge=0.5,
        le=5.0,
        description="每次滚动后的暂停时间（秒）"
    )
    viewport_height: int = Field(
        default=1080,
        ge=800,
        le=2000,
        description="浏览器视口高度（像素）"
    )
    remove_selectors: Optional[List[str]] = Field(
        default=None,
        description="要移除的元素的CSS选择器列表"
    )
    image_handling: Literal["Download to Local", "Upload to Image Bed", "Keep Original URLs"] = Field(
        default="Keep Original URLs",
        description="图片处理方式"
    )
    show_image_errors: bool = Field(
        default=False,
        description="是否在Markdown中显示图片处理错误信息"
    )
    image_bed_id: Optional[str] = Field(
        default=None,
        description="图床ID（当image_handling为'Upload to Image Bed'时使用）"
    )


class Web2MDResponse(BaseModel):
    """网页转Markdown响应模型"""
    success: bool = Field(..., description="是否成功")
    markdown: Optional[str] = Field(None, description="提取的Markdown内容")
    saved_file_path: Optional[str] = Field(None, description="保存的文件路径")
    message: Optional[str] = Field(None, description="错误或提示信息")
    stats: Optional[dict] = Field(None, description="提取统计信息")

