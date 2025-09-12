import streamlit as st
import os
from PIL import Image
import glob

def main():
    st.set_page_config(page_title="PDF图片查看器", layout="wide")
    st.title("📄 PDF预览图片查看器")
    st.markdown("---")
    
    # 图片目录
    image_dir = "downloaded_pdf_images"
    
    if not os.path.exists(image_dir):
        st.error(f"图片目录 {image_dir} 不存在！")
        return
    
    # 获取所有PNG文件
    image_files = sorted(glob.glob(os.path.join(image_dir, "*.png")))
    
    if not image_files:
        st.warning("没有找到PNG图片文件！")
        return
    
    st.success(f"找到 {len(image_files)} 张图片")
    
    # 侧边栏控制
    with st.sidebar:
        st.header("📋 控制面板")
        
        # 显示模式选择
        display_mode = st.selectbox(
            "显示模式",
            ["单页查看", "网格浏览", "幻灯片模式"],
            index=0
        )
        
        if display_mode == "单页查看":
            page_num = st.slider("选择页码", 1, len(image_files), 1)
            selected_file = image_files[page_num - 1]
        elif display_mode == "网格浏览":
            cols = st.slider("每行显示列数", 2, 6, 3)
        else:  # 幻灯片模式
            auto_play = st.checkbox("自动播放", value=False)
            if auto_play:
                play_speed = st.slider("播放速度(秒)", 1.0, 10.0, 3.0)
    
    # 主内容区域
    if display_mode == "单页查看":
        st.subheader(f"第 {page_num} 页")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            try:
                image = Image.open(selected_file)
                st.image(image, caption=f"第 {page_num} 页", use_container_width=True)
            except Exception as e:
                st.error(f"无法加载图片: {str(e)}")
        
        with col2:
            st.info(f"**文件信息:**\n- 文件名: {os.path.basename(selected_file)}\n- 文件大小: {os.path.getsize(selected_file) / 1024:.1f} KB")
            
            # 导航按钮
            col_prev, col_next = st.columns(2)
            with col_prev:
                if page_num > 1:
                    if st.button("⬅️ 上一页"):
                        st.session_state.page_num = page_num - 1
                        st.rerun()
            
            with col_next:
                if page_num < len(image_files):
                    if st.button("下一页 ➡️"):
                        st.session_state.page_num = page_num + 1
                        st.rerun()
    
    elif display_mode == "网格浏览":
        st.subheader("网格浏览模式")
        
        # 计算行数
        rows = (len(image_files) + cols - 1) // cols
        
        for row in range(rows):
            cols_list = st.columns(cols)
            for col_idx in range(cols):
                file_idx = row * cols + col_idx
                if file_idx < len(image_files):
                    with cols_list[col_idx]:
                        try:
                            image = Image.open(image_files[file_idx])
                            st.image(image, caption=f"第 {file_idx + 1} 页", use_container_width=True)
                        except Exception as e:
                            st.error(f"无法加载图片: {str(e)}")
    
    else:  # 幻灯片模式
        st.subheader("幻灯片模式")
        
        if 'current_slide' not in st.session_state:
            st.session_state.current_slide = 0
        
        # 显示当前幻灯片
        if st.session_state.current_slide < len(image_files):
            try:
                image = Image.open(image_files[st.session_state.current_slide])
                st.image(image, caption=f"第 {st.session_state.current_slide + 1} 页", use_container_width=True)
            except Exception as e:
                st.error(f"无法加载图片: {str(e)}")
        
        # 控制按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⏮️ 第一页"):
                st.session_state.current_slide = 0
                st.rerun()
        
        with col2:
            if st.button("⏯️ 播放/暂停"):
                st.session_state.auto_play = not st.session_state.get('auto_play', False)
                st.rerun()
        
        with col3:
            if st.button("⏭️ 最后一页"):
                st.session_state.current_slide = len(image_files) - 1
                st.rerun()
        
        # 进度条
        progress = (st.session_state.current_slide + 1) / len(image_files)
        st.progress(progress)
        st.caption(f"进度: {st.session_state.current_slide + 1} / {len(image_files)}")
        
        # 自动播放逻辑
        if st.session_state.get('auto_play', False):
            import time
            time.sleep(play_speed)
            if st.session_state.current_slide < len(image_files) - 1:
                st.session_state.current_slide += 1
                st.rerun()
            else:
                st.session_state.auto_play = False
                st.rerun()

if __name__ == "__main__":
    main() 