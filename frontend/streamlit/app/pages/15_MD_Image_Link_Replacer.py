import sys
import os
import re
import json
import streamlit as st

# 使用简化路径管理
from scripts.utils.simple_paths import *

from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

# 直接复用增强版处理逻辑
from core.web2md.enhanced_web2md import process_images_in_markdown
from core.utils.img_bed import get_default_image_bed, list_available_image_beds


st.set_page_config(page_title="Markdown 图片链接替换", layout="wide")

# 加载主题
load_anthropic_theme()

st.title("Markdown 图片链接替换")
st.caption("左侧粘贴原始 Markdown，右侧生成替换为图床后的 Markdown")

with st.expander("选项", expanded=False):
    colopt1, colopt2, colopt3 = st.columns([1, 1, 2])
    with colopt1:
        show_image_errors = st.checkbox("在Markdown中显示错误提示", value=False)
    with colopt2:
        auto_use_default_bed = st.checkbox("自动使用默认图床", value=True)
    with colopt3:
        base_url = st.text_input("基准URL（可选，用于相对路径解析）", value="")

    selected_image_bed = None
    if not auto_use_default_bed:
        try:
            beds = list_available_image_beds()
            if beds:
                bed_options = {f"{bed['name']} ({bed['type']})": bed for bed in beds}
                chosen = st.selectbox("选择图床（未勾选自动时生效）", list(bed_options.keys()))
                selected_image_bed = bed_options[chosen]
            else:
                st.warning("未发现可用图床，请在图床配置页面添加并启用图床")
        except Exception as e:
            st.warning(f"读取图床配置失败：{e}")

st.markdown("---")

left, right = st.columns([1, 1])

with left:
    st.subheader("原始 Markdown")
    src_md = st.text_area("在此粘贴Markdown内容", height=420, placeholder="在此粘贴含有图片链接的Markdown，例如：\n\n![示例](https://example.com/image.png)")
    run = st.button("开始替换图片链接")

with right:
    st.subheader("替换后的 Markdown")
    if run:
        try:
            # 选取图床配置
            bed_cfg = selected_image_bed
            if bed_cfg is None:
                bed_cfg = get_default_image_bed()
            if bed_cfg is None:
                st.error("未找到默认图床且无可用图床，请前往图床配置页面设置")
            else:
                # 统计图片数量以便进度与日志（控制台）
                image_pattern = r'!\[[^\]]*\]\(([^)]+)\)'
                image_count = len(re.findall(image_pattern, src_md or ""))

                processed = process_images_in_markdown(
                    markdown_content=src_md or "",
                    base_url=(base_url or None),
                    images_dir=None,
                    mode="upload",
                    show_errors=show_image_errors,
                    image_bed_config=bed_cfg,
                    total_count=image_count,
                )

                st.code(processed, language="markdown")

                file_name = "md_image_replaced.md"
                st.download_button(
                    label="下载替换后的Markdown",
                    data=processed,
                    file_name=file_name,
                    mime="text/markdown",
                )

                st.info(f"已使用图床：{bed_cfg.get('name', 'Unknown')} ({bed_cfg.get('type', 'Unknown')})")
        except Exception as e:
            st.error(f"处理失败：{e}")
    else:
        st.code("", language="markdown")

with st.expander("使用说明"):
    st.markdown(
        """
        - 将含有图片语法的 Markdown 粘贴在左侧，点击“开始替换”。\n
        - 系统会尝试将所有 `![alt](url)` 链接中的图片上传到当前图床，并替换为新URL。\n
        - 若存在相对路径图片，可填写“基准URL”用于解析。\n
        - 默认自动使用“默认图床”；如需指定，请取消勾选并在下拉框选择。\n
        - 替换过程的详细日志会输出到控制台（用于排查问题）。
        """
    )


