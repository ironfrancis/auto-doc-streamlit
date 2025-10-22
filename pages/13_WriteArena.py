import sys
import os
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from datetime import datetime
import time

# 使用简化路径管理
from simple_paths import *

from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

# 初始化语言设置
from language_manager import init_language, get_text, get_language
init_language()

st.set_page_config(page_title="WriteArena - 并发写作评判", layout="wide")

# 加载主题
load_anthropic_theme()

# 自定义样式
st.markdown("""
<style>
    /* 卡片样式 */
    .result-card {
        border: 2px solid #E0E0E0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        background: linear-gradient(135deg, #FAFAF8 0%, #F5F1E8 100%);
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        border-color: #E8957B;
        box-shadow: 0 4px 12px rgba(233, 149, 123, 0.2);
    }
    
    .result-card.selected {
        border-color: #28a745;
        border-width: 3px;
        background: linear-gradient(135deg, #f0fff4 0%, #e6f9ec 100%);
    }
    
    .result-card.published {
        border-color: #007bff;
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f2ff 100%);
    }
    
    /* 端点标题 */
    .endpoint-title {
        font-size: 1.2em;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 10px;
    }
    
    /* 时间标签 */
    .elapsed-badge {
        display: inline-block;
        padding: 4px 12px;
        background: #E8957B;
        color: white;
        border-radius: 12px;
        font-size: 0.85em;
        margin-left: 10px;
    }
    
    /* 任务列表卡片 */
    .task-card {
        padding: 15px;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        margin-bottom: 10px;
        background: white;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .task-card:hover {
        border-color: #E8957B;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .task-card.judged {
        border-left: 4px solid #28a745;
    }
    
    .task-card.pending {
        border-left: 4px solid #ffc107;
    }
    
    /* 评分滑块样式优化 */
    .stSlider > div > div > div > div {
        background-color: #E8957B;
    }
    
    /* 标签样式 */
    .tag-chip {
        display: inline-block;
        padding: 4px 10px;
        margin: 4px;
        background: #E8957B;
        color: white;
        border-radius: 16px;
        font-size: 0.85em;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚔️ WriteArena - 并发写作评判平台")

# ============================================================================
# 工具函数
# ============================================================================

def get_concurrent_history_dir():
    """获取并发历史目录"""
    history_dir = os.path.join(get_workspace_dir(), "concurrent_history")
    os.makedirs(history_dir, exist_ok=True)
    return history_dir


def load_all_tasks():
    """
    加载所有并发历史任务
    
    返回:
        列表，每项包含 (file_path, metadata)
    """
    history_dir = get_concurrent_history_dir()
    if not os.path.exists(history_dir):
        return []
    
    history_files = sorted(
        [f for f in os.listdir(history_dir) if f.endswith('.json')],
        reverse=True  # 最新的在前
    )
    
    tasks = []
    for filename in history_files:
        file_path = os.path.join(history_dir, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            tasks.append((file_path, metadata))
        except Exception as e:
            st.warning(f"加载任务失败 {filename}: {e}")
            continue
    
    return tasks


def save_judgments(file_path, judgments_data):
    """
    保存评判数据到任务文件
    
    参数:
        file_path: 任务JSON文件路径
        judgments_data: 评判数据字典
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            task_data = json.load(f)
        
        task_data["judgments"] = judgments_data
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"保存评判失败: {e}")
        return False


def load_article_content(file_path):
    """
    读取文章内容
    
    参数:
        file_path: 文章文件路径
    
    返回:
        文章内容字符串，失败返回 None
    """
    if not file_path or not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return None


def save_annotations_to_task(task_path, endpoint_name, annotations):
    """
    保存批注到任务文件
    
    参数:
        task_path: 任务JSON文件路径
        endpoint_name: 端点名称
        annotations: 批注数组
    """
    try:
        with open(task_path, "r", encoding="utf-8") as f:
            task_data = json.load(f)
        
        # 添加批注数据
        if 'annotations' not in task_data:
            task_data['annotations'] = {}
        
        task_data['annotations'][endpoint_name] = annotations
        
        # 保存
        with open(task_path, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        st.error(f"保存批注失败: {e}")
        return False


def load_annotations_from_task(task_data, endpoint_name):
    """
    从任务数据加载批注
    
    参数:
        task_data: 任务数据字典
        endpoint_name: 端点名称
    
    返回:
        批注数组
    """
    annotations = task_data.get('annotations', {}).get(endpoint_name, [])
    return annotations

def render_article_with_annotations(article_content, endpoint_name, task_path, key):
    """渲染带批注功能的文章"""
    # 加载已有批注
    if task_path:
        try:
            with open(task_path, "r", encoding="utf-8") as f:
                task_data = json.load(f)
            existing_annotations = load_annotations_from_task(task_data, endpoint_name)
        except:
            existing_annotations = []
    else:
        existing_annotations = []
    
    existing_annotations_json = json.dumps(existing_annotations)
    
    # 简单的 Markdown 转 HTML
    import html
    import re
    
    html_content = html.escape(article_content)
    # 处理标题
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    # 处理粗体
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    # 处理斜体
    html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)
    # 处理换行
    html_content = html_content.replace('\n', '<br>')
    html_content = f"<div>{html_content}</div>"
    
    # 构建简化的批注 HTML
    annotation_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                margin: 20px;
                padding: 20px;
                background: #f8f9fa;
            }}
            .article-content {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                max-width: 800px;
                margin: 0 auto;
                user-select: text;
            }}
            .annotation-toolbar {{
                position: fixed;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                z-index: 10000;
                display: none;
                border: 2px solid #007bff;
                min-width: 250px;
            }}
            .annotation-form {{
                display: flex;
                flex-direction: column;
                gap: 8px;
            }}
            .annotation-form input, .annotation-form select, .annotation-form textarea {{
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }}
            .annotation-form button {{
                padding: 8px 16px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            .annotation-form button:hover {{
                background: #0056b3;
            }}
            .highlight {{
                background-color: #ffeb3b;
                cursor: pointer;
                position: relative;
            }}
            .highlight:hover {{
                background-color: #ffc107;
            }}
            .annotation-list {{
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            .annotation-item {{
                background: white;
                padding: 10px;
                margin: 8px 0;
                border-radius: 4px;
                border-left: 4px solid #007bff;
            }}
            .annotation-item .quote {{
                font-style: italic;
                color: #666;
                margin-bottom: 5px;
            }}
            .annotation-item .type {{
                font-weight: bold;
                color: #007bff;
            }}
            .annotation-item .severity {{
                font-size: 12px;
                color: #666;
            }}
            .status {{
                position: fixed;
                top: 10px;
                right: 10px;
                background: #28a745;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 9999;
            }}
        </style>
    </head>
    <body>
        <div class="status" id="status">批注模式已开启 - 选择文本进行批注</div>
        
        <div class="annotation-toolbar" id="toolbar">
            <div class="annotation-form">
                <h4>添加批注</h4>
                <input type="text" id="annotation-type" placeholder="批注类型" list="type-list">
                <datalist id="type-list">
                    <option value="📝 语言问题">
                    <option value="📊 事实错误">
                    <option value="💡 内容建议">
                    <option value="⚠️ 风格问题">
                    <option value="🔧 格式问题">
                </datalist>
                <select id="annotation-severity">
                    <option value="low">低</option>
                    <option value="medium">中</option>
                    <option value="high">高</option>
                </select>
                <textarea id="annotation-content" placeholder="批注内容" rows="3"></textarea>
                <button onclick="saveAnnotation()">保存批注</button>
                <button onclick="cancelAnnotation()" style="background: #6c757d;">取消</button>
            </div>
        </div>
        
        <div class="article-content" id="article-content">
            {html_content}
        </div>
        
        <div class="annotation-list" id="annotation-list">
            <h3>📋 批注列表</h3>
            <div id="annotations-container">
                <p style="color: #666;">暂无批注</p>
            </div>
        </div>
        
        <script>
            let currentSelection = null;
            let annotations = {existing_annotations_json};
            let toolbarVisible = false;
            
            // 初始化
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('批注页面加载完成');
                renderAnnotations();
                setupTextSelection();
            }});
            
            function setupTextSelection() {{
                const content = document.getElementById('article-content');
                console.log('设置文本选择功能，目标元素:', content);
                
                if (!content) {{
                    console.error('找不到文章内容元素！');
                    return;
                }}
                
                // 添加文本选择事件
                content.addEventListener('mouseup', function(e) {{
                    console.log('鼠标释放事件触发');
                    
                    // 延迟检查选择，确保选择完成
                    setTimeout(function() {{
                        const selection = window.getSelection();
                        const text = selection.toString().trim();
                        console.log('选中的文本:', text);
                        
                        if (text.length > 0) {{
                            currentSelection = {{
                                text: text,
                                range: selection.getRangeAt(0)
                            }};
                            
                            // 显示工具栏
                            showToolbar(e.pageX, e.pageY);
                        }}
                    }}, 50);
                }});
                
                // 添加双击事件作为备选方案
                content.addEventListener('dblclick', function(e) {{
                    console.log('双击事件触发');
                    setTimeout(function() {{
                        const selection = window.getSelection();
                        const text = selection.toString().trim();
                        console.log('双击选中的文本:', text);
                        
                        if (text.length > 0) {{
                            currentSelection = {{
                                text: text,
                                range: selection.getRangeAt(0)
                            }};
                            
                            // 显示工具栏
                            showToolbar(e.pageX, e.pageY);
                        }}
                    }}, 10);
                }});
                
                // 只在工具栏外部点击时隐藏
                document.addEventListener('click', function(e) {{
                    // 如果点击的是工具栏内部，不隐藏
                    if (e.target.closest('.annotation-toolbar')) {{
                        console.log('点击工具栏内部，保持显示');
                        return;
                    }}
                    
                    // 如果工具栏可见且点击的是外部区域，隐藏工具栏
                    if (toolbarVisible) {{
                        console.log('点击外部区域，隐藏工具栏');
                        hideToolbar();
                    }}
                }});
                
                // 添加键盘事件处理
                document.addEventListener('keydown', function(e) {{
                    if (e.key === 'Escape') {{
                        hideToolbar();
                    }}
                }});
                
                console.log('文本选择功能设置完成');
            }}
            
            function showToolbar(x, y) {{
                const toolbar = document.getElementById('toolbar');
                if (toolbar) {{
                    toolbar.style.display = 'block';
                    toolbar.style.left = x + 'px';
                    toolbar.style.top = y + 'px';
                    toolbarVisible = true;
                    console.log('工具栏显示在位置:', x, y);
                }} else {{
                    console.error('找不到工具栏元素！');
                }}
            }}
            
            function hideToolbar() {{
                const toolbar = document.getElementById('toolbar');
                if (toolbar) {{
                    toolbar.style.display = 'none';
                    toolbarVisible = false;
                    currentSelection = null;
                    console.log('工具栏已隐藏');
                }}
            }}
            
            function saveAnnotation() {{
                if (!currentSelection) {{
                    alert('请先选择文本');
                    return;
                }}
                
                const type = document.getElementById('annotation-type').value;
                const severity = document.getElementById('annotation-severity').value;
                const content = document.getElementById('annotation-content').value;
                
                if (!type || !content) {{
                    alert('请填写批注类型和内容');
                    return;
                }}
                
                // 创建批注
                const annotation = {{
                    id: Date.now(),
                    quote: currentSelection.text,
                    type: type,
                    severity: severity,
                    content: content,
                    created_at: new Date().toLocaleString()
                }};
                
                annotations.push(annotation);
                
                // 高亮文本
                highlightText(currentSelection.range, annotation.id);
                
                // 清空表单
                document.getElementById('annotation-type').value = '';
                document.getElementById('annotation-content').value = '';
                document.getElementById('annotation-severity').value = 'medium';
                
                // 隐藏工具栏
                hideToolbar();
                
                // 重新渲染批注列表
                renderAnnotations();
                
                // 通知父窗口
                window.parent.postMessage({{
                    type: 'annotations_updated',
                    annotations: annotations,
                    endpoint: '{endpoint_name}'
                }}, '*');
                
                console.log('批注已保存:', annotation);
            }}
            
            function cancelAnnotation() {{
                hideToolbar();
            }}
            
            function highlightText(range, annotationId) {{
                const span = document.createElement('span');
                span.className = 'highlight';
                span.setAttribute('data-annotation-id', annotationId);
                span.onclick = function() {{ 
                    const annotation = annotations.find(a => a.id === annotationId);
                    if (annotation) {{
                        alert('批注详情:\\n\\n类型: ' + annotation.type + '\\n严重程度: ' + annotation.severity + '\\n内容: ' + annotation.content);
                    }}
                }};
                
                try {{
                    range.surroundContents(span);
                }} catch(e) {{
                    // 如果无法包围，则替换内容
                    range.deleteContents();
                    range.insertNode(span);
                    span.appendChild(document.createTextNode(range.toString()));
                }}
            }}
            
            function renderAnnotations() {{
                const container = document.getElementById('annotations-container');
                container.innerHTML = '';
                
                if (annotations.length === 0) {{
                    container.innerHTML = '<p style="color: #666;">暂无批注</p>';
                    return;
                }}
                
                annotations.forEach(annotation => {{
                    const item = document.createElement('div');
                    item.className = 'annotation-item';
                    item.innerHTML = `
                        <div class="quote">"${{annotation.quote}}"</div>
                        <div class="type">${{annotation.type}}</div>
                        <div class="severity">严重程度: ${{annotation.severity}}</div>
                        <div>${{annotation.content}}</div>
                    `;
                    container.appendChild(item);
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    # 渲染批注 HTML
    component_value = components.html(annotation_html, height=800, scrolling=True)
    
    # 处理来自 JavaScript 的消息
    if component_value is not None and isinstance(component_value, dict):
        if component_value.get('type') == 'annotations_updated':
            annotations = component_value.get('annotations', [])
            endpoint = component_value.get('endpoint')
            
            # 保存批注
            if save_annotations_to_task(task_path, endpoint, annotations):
                st.success(f"✅ 批注已自动保存（共 {len(annotations)} 条）")
                st.rerun()


# ============================================================================
# 预设标签和评分维度
# ============================================================================

PRESET_TAGS = [
    "准确", "详细", "流畅", "简洁", "创新", "实用", 
    "专业", "通俗", "深度", "全面", "逻辑清晰", "案例丰富"
]

SCORE_DIMENSIONS = {
    "accuracy": {"name": "准确性", "help": "内容是否准确、无误"},
    "creativity": {"name": "创意性", "help": "角度是否新颖、有创意"},
    "readability": {"name": "可读性", "help": "语言流畅、结构清晰"},
    "professionalism": {"name": "专业性", "help": "专业术语、深度"},
    "practicality": {"name": "实用性", "help": "对读者的实用价值"},
}

# ============================================================================
# 会话状态初始化
# ============================================================================

if "selected_task_path" not in st.session_state:
    st.session_state.selected_task_path = None

if "judgment_data" not in st.session_state:
    st.session_state.judgment_data = {}

if "show_annotation_modal" not in st.session_state:
    st.session_state.show_annotation_modal = False

if "annotation_endpoint" not in st.session_state:
    st.session_state.annotation_endpoint = None

# ============================================================================
# 任务选择区
# ============================================================================

st.markdown("## 📋 选择并发任务")

tasks = load_all_tasks()

if not tasks:
    st.info("暂无并发历史任务，请先在 **Creation and Transcription** 页面执行并发转写")
else:
    # 构建任务选项
    task_options = []
    task_map = {}
    
    for file_path, metadata in tasks:
        task_id = metadata.get("id", "未知")
        channel = metadata.get("channel", "未知")
        timestamp = metadata.get("timestamp", "未知")
        stats = metadata.get("statistics", {})
        success_endpoints = stats.get("success", 0)
        total_endpoints = stats.get("total", 0)
        is_judged = metadata.get("judgments", {}).get("judged", False)
        
        # 构建显示名称
        status_icon = "✅" if is_judged else "⏳"
        display_name = f"{status_icon} {timestamp} | {channel} | {success_endpoints}/{total_endpoints} 端点"
        
        task_options.append(display_name)
        task_map[display_name] = file_path
    
    # 下拉框选择任务
    selected_task_display = st.selectbox(
        "选择要评判的任务",
        ["--- 请选择任务 ---"] + task_options,
        key="task_selector"
    )
    
    # 更新选中的任务
    if selected_task_display != "--- 请选择任务 ---":
        new_selected_path = task_map[selected_task_display]
        if st.session_state.selected_task_path != new_selected_path:
            st.session_state.selected_task_path = new_selected_path
            st.session_state.judgment_data = {}
            st.rerun()
    else:
        # 清空选择
        if st.session_state.selected_task_path is not None:
            st.session_state.selected_task_path = None
            st.rerun()

# ============================================================================
# 结果对比与评判区
# ============================================================================

if st.session_state.selected_task_path:
    selected_path = st.session_state.selected_task_path
    
    # 加载任务数据
    with open(selected_path, "r", encoding="utf-8") as f:
        task_data = json.load(f)
    
    # 显示任务信息（与标题合并，极简风格）
    channel = task_data.get('channel', '未知')
    timestamp = task_data.get('timestamp', '未知')
    stats = task_data.get('statistics', {})
    success_count = stats.get('success', 0)
    total_count = stats.get('total', 0)
    is_judged = task_data.get("judgments", {}).get("judged", False)
    status = "已评判" if is_judged else "待评判"
    
    st.markdown(f"**{channel}** | {timestamp} | {success_count}/{total_count} 成功 | {status}")
    
    st.markdown("---")
    
    # 加载现有评判（如果有）
    existing_judgments = task_data.get("judgments", {})
    
    # 初始化评判数据
    if "current_judgments" not in st.session_state:
        st.session_state.current_judgments = existing_judgments
    
    results = task_data.get("results", [])
    
    if not results:
        st.warning("该任务没有结果数据")
    else:
        # 计算列数（最多4列）
        num_results = len(results)
        num_columns = min(num_results, 4)
        
        # 创建并排列
        result_columns = st.columns(num_columns)
        
        # 存储本次评判数据
        current_ratings = {}
        best_choice = None
        
        # 遍历每个结果
        for idx, result_info in enumerate(results):
            col_idx = idx % num_columns
            
            endpoint_name = result_info.get("endpoint", "未知")
            success = result_info.get("success", False)
            elapsed = result_info.get("elapsed", 0)
            file_path = result_info.get("file_path", "")
            
            if not success:
                continue
            
            with result_columns[col_idx]:
                # 读取文章内容
                article_content = load_article_content(file_path)
                
                # 显示端点标题和耗时
                st.markdown(f"""
                <div class="endpoint-title">
                    {endpoint_name}
                    <span class="elapsed-badge">⏱ {elapsed:.1f}s</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 文章预览（带批注按钮和格式切换）
                with st.expander("📄 查看文章内容", expanded=False):
                    if article_content:
                        # 批注模式切换
                        annotation_mode = st.toggle(
                            "✍️ 批注模式",
                            value=False,
                            key=f"annotation_mode_{idx}_{endpoint_name}",
                            help="开启后可直接在文章上批注"
                        )
                        
                        # 手动批注按钮（仅在批注模式下显示）
                        if annotation_mode:
                            if st.button("✍️ 手动批注", key=f"manual_annotation_{idx}_{endpoint_name}", help="如果选择文本不工作，点击此按钮手动输入批注"):
                                st.session_state[f"show_manual_annotation_{idx}_{endpoint_name}"] = True
                        
                        st.markdown("---")
                        
                        # 手动批注表单（仅在批注模式下显示）
                        if annotation_mode and st.session_state.get(f"show_manual_annotation_{idx}_{endpoint_name}", False):
                            st.markdown("### ✍️ 手动批注")
                            with st.form(key=f"manual_annotation_form_{idx}_{endpoint_name}"):
                                col_manual1, col_manual2 = st.columns(2)
                                with col_manual1:
                                    manual_type = st.selectbox(
                                        "批注类型",
                                        ["📝 语言问题", "📊 事实错误", "💡 内容建议", "⚠️ 风格问题", "🔧 格式问题"],
                                        key=f"manual_type_{idx}_{endpoint_name}"
                                    )
                                with col_manual2:
                                    manual_severity = st.selectbox(
                                        "严重程度",
                                        ["low", "medium", "high"],
                                        index=1,
                                        key=f"manual_severity_{idx}_{endpoint_name}"
                                    )
                                
                                manual_quote = st.text_area(
                                    "引用文本",
                                    placeholder="输入要批注的文本片段",
                                    key=f"manual_quote_{idx}_{endpoint_name}"
                                )
                                
                                manual_content = st.text_area(
                                    "批注内容",
                                    placeholder="输入批注内容",
                                    key=f"manual_content_{idx}_{endpoint_name}"
                                )
                                
                                col_submit1, col_submit2 = st.columns(2)
                                with col_submit1:
                                    if st.form_submit_button("保存批注", use_container_width=True):
                                        if manual_quote and manual_content:
                                            # 保存手动批注
                                            annotation = {
                                                "id": int(time.time() * 1000),
                                                "quote": manual_quote,
                                                "type": manual_type,
                                                "severity": manual_severity,
                                                "content": manual_content,
                                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            }
                                            
                                            if save_annotations_to_task(st.session_state.selected_task_path, endpoint_name, [annotation]):
                                                st.success("✅ 批注已保存")
                                                st.session_state[f"show_manual_annotation_{idx}_{endpoint_name}"] = False
                                                st.rerun()
                                        else:
                                            st.error("请填写引用文本和批注内容")
                                
                                with col_submit2:
                                    if st.form_submit_button("取消", use_container_width=True):
                                        st.session_state[f"show_manual_annotation_{idx}_{endpoint_name}"] = False
                                        st.rerun()
                            
                            st.markdown("---")
                        
                        # 根据批注模式渲染内容
                        if annotation_mode:
                            # 批注模式 - 使用内联批注器
                            render_article_with_annotations(
                                article_content, 
                                endpoint_name, 
                                st.session_state.selected_task_path,
                                key=f"annotator_{idx}_{endpoint_name}"
                            )
                        else:
                            # 普通预览模式 - 只显示 Markdown
                            st.markdown(article_content)
                    else:
                        st.warning("无法加载文章内容")
                
                st.markdown("---")
                
                # 评判区域
                st.markdown("### 📊 评判")
                
                # 加载现有评分（如果有）
                existing_rating = existing_judgments.get("ratings", {}).get(endpoint_name, {})
                existing_scores = existing_rating.get("scores", {})
                
                # 总体评分（必填）
                overall_score = st.slider(
                    "⭐ 总体评分",
                    min_value=1,
                    max_value=10,
                    value=existing_scores.get("overall", 5),
                    key=f"overall_{idx}_{endpoint_name}",
                    help="必填项：总体评价"
                )
                
                # 细分维度评分（可选，默认5分）
                with st.expander("📈 细分维度评分（可选）", expanded=False):
                    dimension_scores = {}
                    for dim_key, dim_info in SCORE_DIMENSIONS.items():
                        dim_score = st.slider(
                            dim_info["name"],
                            min_value=1,
                            max_value=10,
                            value=existing_scores.get(dim_key, 5),
                            key=f"{dim_key}_{idx}_{endpoint_name}",
                            help=dim_info["help"]
                        )
                        dimension_scores[dim_key] = dim_score
                
                # 标签选择
                st.markdown("**🏷️ 标签**")
                existing_tags = existing_rating.get("tags", [])
                selected_tags = st.multiselect(
                    "选择标签",
                    PRESET_TAGS,
                    default=existing_tags,
                    key=f"tags_{idx}_{endpoint_name}",
                    label_visibility="collapsed"
                )
                
                # 评语
                notes = st.text_area(
                    "💬 评语",
                    value=existing_rating.get("notes", ""),
                    height=100,
                    key=f"notes_{idx}_{endpoint_name}",
                    placeholder="添加详细评价..."
                )
                
                # 🎯 核心功能：采用并计划发布
                existing_published = existing_rating.get("published", False)
                is_published = st.checkbox(
                    "✅ 采用，计划发布",
                    value=existing_published,
                    key=f"publish_{idx}_{endpoint_name}",
                    help="勾选此项标记该结果将被发布"
                )
                
                # 如果标记为发布，显示发布信息输入
                publish_info = None
                if is_published:
                    with st.expander("📝 发布信息（可选）", expanded=existing_published):
                        existing_publish_info = existing_rating.get("publish_info", {}) or {}
                        
                        publish_platforms = st.multiselect(
                            "发布平台",
                            ["微信公众号", "知乎", "掘金", "CSDN", "个人博客", "其他"],
                            default=existing_publish_info.get("platforms", []),
                            key=f"platforms_{idx}_{endpoint_name}"
                        )
                        
                        publish_urls = st.text_area(
                            "发布链接（每行一个）",
                            value="\n".join(existing_publish_info.get("urls", [])),
                            key=f"urls_{idx}_{endpoint_name}",
                            height=60
                        )
                        
                        publish_info = {
                            "published_at": existing_publish_info.get("published_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "platforms": publish_platforms,
                            "urls": [url.strip() for url in publish_urls.split("\n") if url.strip()],
                            "performance": existing_publish_info.get("performance", {})
                        }
                
                # 选为最佳
                is_best = st.checkbox(
                    "🏆 选为最佳",
                    value=(existing_judgments.get("best_choice") == endpoint_name),
                    key=f"best_{idx}_{endpoint_name}"
                )
                
                if is_best:
                    best_choice = endpoint_name
                
                # 收集当前评判数据
                current_ratings[endpoint_name] = {
                    "scores": {
                        "overall": overall_score,
                        **dimension_scores
                    },
                    "tags": selected_tags,
                    "notes": notes,
                    "published": is_published,
                    "publish_info": publish_info
                }
        
        # 整体评价
        st.markdown("---")
        st.markdown("### 📝 整体评价")
        
        overall_notes = st.text_area(
            "对本次对比的总结",
            value=existing_judgments.get("overall_notes", ""),
            height=100,
            key="overall_notes",
            placeholder="例如：本次对比中哪个端点表现最好，各有什么特点..."
        )
        
        # 保存按钮
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn2:
            if st.button("💾 保存评判", type="primary", use_container_width=True):
                # 构建完整的评判数据
                judgments_data = {
                    "judged": True,
                    "judged_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "best_choice": best_choice,
                    "ratings": current_ratings,
                    "overall_notes": overall_notes
                }
                
                # 保存到文件
                if save_judgments(selected_path, judgments_data):
                    st.success("✅ 评判保存成功！")
                    st.balloons()
                    
                    # 更新session state
                    st.session_state.current_judgments = judgments_data
                    
                    # 延迟刷新
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ 保存失败，请重试")

# ============================================================================
# 侧边栏：统计信息
# ============================================================================

with st.sidebar:
    st.markdown("## 📊 统计信息")
    
    if tasks:
        # 加载所有评判数据进行统计
        all_judgments = []
        for file_path, metadata in tasks:
            judgments = metadata.get("judgments", {})
            if judgments.get("judged", False):
                all_judgments.append(judgments)
        
        if all_judgments:
            st.metric("已评判任务", len(all_judgments))
            
            # 统计被选为最佳的端点
            best_choices = [j.get("best_choice") for j in all_judgments if j.get("best_choice")]
            if best_choices:
                from collections import Counter
                best_counter = Counter(best_choices)
                
                st.markdown("### 🏆 最佳选择统计")
                for endpoint, count in best_counter.most_common(5):
                    percentage = (count / len(best_choices)) * 100
                    st.markdown(f"**{endpoint}**: {count}次 ({percentage:.1f}%)")
            
            # 统计发布情况
            published_count = 0
            published_by_endpoint = {}
            
            for judgment in all_judgments:
                ratings = judgment.get("ratings", {})
                for endpoint, rating in ratings.items():
                    if rating.get("published", False):
                        published_count += 1
                        published_by_endpoint[endpoint] = published_by_endpoint.get(endpoint, 0) + 1
            
            if published_count > 0:
                st.markdown("### 📢 发布统计")
                st.metric("已发布文章", published_count)
                
                st.markdown("**按端点统计：**")
                for endpoint, count in sorted(published_by_endpoint.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.markdown(f"- {endpoint}: {count}篇")
            
            # 统计批注情况
            total_annotations = 0
            annotations_by_type = {}
            
            for file_path, metadata in tasks:
                annotations_data = metadata.get("annotations", {})
                for endpoint, annos in annotations_data.items():
                    total_annotations += len(annos)
                    for anno in annos:
                        anno_type = anno.get("type", "unknown")
                        annotations_by_type[anno_type] = annotations_by_type.get(anno_type, 0) + 1
            
            if total_annotations > 0:
                st.markdown("### ✍️ 批注统计")
                st.metric("总批注数", total_annotations)
                
                st.markdown("**按类型统计：**")
                type_names = {
                    "language": "📝 语言问题",
                    "fact": "📊 事实错误",
                    "content": "💡 内容建议",
                    "style": "⚠️ 风格问题",
                    "format": "🔧 格式问题"
                }
                for anno_type, count in sorted(annotations_by_type.items(), key=lambda x: x[1], reverse=True):
                    type_label = type_names.get(anno_type, anno_type)
                    st.markdown(f"- {type_label}: {count}条")
        else:
            st.info("暂无评判数据")
    else:
        st.info("暂无任务数据")
    
    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.markdown("""
    1. 从下拉框选择要评判的并发任务
    2. 展开文章内容，切换 Markdown/HTML 格式查看
    3. 开启"✍️ 批注模式"可直接在文章上批注
    4. 为每个端点打分、添加标签和评语
    5. 勾选"采用，计划发布"标记发布
    6. 选择最佳结果
    7. 保存评判
    
    **💡 提示**: 
    - 批注模式：开启开关→选择文本→填写批注→保存，文本会高亮显示
    - 如果拖拽选择不工作，可以尝试双击文本选择
    - 如果选择文本不工作，点击"✍️ 手动批注"按钮
    - 按 ESC 键可以关闭批注工具栏
    """)

# ============================================================================
# 批注模态窗口（已废弃，改为内联批注）
# ============================================================================

# 注释：批注功能已改为内联模式，不再需要模态窗口
if False and st.session_state.show_annotation_modal and st.session_state.annotation_endpoint:
    endpoint_info = st.session_state.annotation_endpoint
    endpoint_name = endpoint_info['name']
    article_content = endpoint_info['content']
    
    # 重新加载任务数据（确保在作用域内）
    if st.session_state.selected_task_path:
        with open(st.session_state.selected_task_path, "r", encoding="utf-8") as f:
            task_data = json.load(f)
    else:
        task_data = {}
    
    # 加载已有批注
    existing_annotations = load_annotations_from_task(task_data, endpoint_name)
    existing_annotations_json = json.dumps(existing_annotations)
    
    # 转换 Markdown 为 HTML（简单处理）
    import html
    import re
    
    # 简单的 Markdown 转 HTML
    html_content = html.escape(article_content)
    # 处理标题
    html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
    # 处理段落
    html_content = re.sub(r'\n\n', '</p><p>', html_content)
    html_content = f'<p>{html_content}</p>'
    # 处理粗体
    html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
    
    # 创建批注 HTML
    annotation_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
                line-height: 1.8;
                padding: 20px;
                color: #2B2B2B;
                background-color: #F5F1E8;
                margin: 0;
            }}
            
            #article-content {{
                max-width: 900px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            
            h1, h2, h3 {{
                color: #2B2B2B;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }}
            
            p {{
                margin-bottom: 1em;
            }}
            
            .close-button {{
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                background: #E8957B;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                z-index: 10001;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }}
            
            .close-button:hover {{
                background: #D97A5E;
            }}
            
            .annotation-stats {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 15px 20px;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                z-index: 10001;
                font-size: 13px;
            }}
            
            .annotation-stats h4 {{
                margin: 0 0 10px 0;
                font-size: 14px;
                color: #2B2B2B;
            }}
            
            .stat-item {{
                margin: 5px 0;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <button class="close-button" onclick="closeAnnotation()">✖ 关闭批注</button>
        
        <div id="article-content">
            <h1 style="text-align: center; color: #E8957B;">📝 {endpoint_name}</h1>
            <hr style="border: none; border-top: 2px solid #E8957B; margin: 20px 0;">
            {html_content}
        </div>
        
        <div class="annotation-stats" id="annotation-stats">
            <h4>📊 批注统计</h4>
            <div class="stat-item">总批注数: <strong id="total-count">0</strong></div>
            <div class="stat-item">高优先级: <strong id="high-count">0</strong></div>
            <div class="stat-item">中优先级: <strong id="medium-count">0</strong></div>
            <div class="stat-item">低优先级: <strong id="low-count">0</strong></div>
        </div>
        
        <script>
            // 加载批注 JS
            (function() {{
                const script = document.createElement('script');
                script.src = window.location.origin + '/static/js/article_annotator.js';
                script.onload = function() {{
                    // 初始化批注工具
                    window.annotator = new ArticleAnnotator('article-content', {{
                        highlightColor: '#fff59d',
                        selectedColor: '#ffeb3b',
                        readOnly: false
                    }});
                    
                    // 加载已有批注
                    const existingAnnotations = {existing_annotations_json};
                    if (existingAnnotations && existingAnnotations.length > 0) {{
                        window.annotator.loadAnnotations(existingAnnotations);
                        updateStats();
                    }}
                    
                    // 监听批注变化，更新统计
                    const originalSave = window.annotator.saveAnnotation;
                    window.annotator.saveAnnotation = function() {{
                        originalSave.call(window.annotator);
                        updateStats();
                        notifyStreamlit();
                    }};
                    
                    const originalDelete = window.annotator.deleteAnnotation;
                    window.annotator.deleteAnnotation = function(id) {{
                        originalDelete.call(window.annotator, id);
                        updateStats();
                        notifyStreamlit();
                    }};
                }};
                document.head.appendChild(script);
            }})();
            
            // 更新统计信息
            function updateStats() {{
                if (!window.annotator) return;
                
                const annotations = window.annotator.getAnnotations();
                document.getElementById('total-count').textContent = annotations.length;
                
                const high = annotations.filter(a => a.severity === 'high').length;
                const medium = annotations.filter(a => a.severity === 'medium').length;
                const low = annotations.filter(a => a.severity === 'low').length;
                
                document.getElementById('high-count').textContent = high;
                document.getElementById('medium-count').textContent = medium;
                document.getElementById('low-count').textContent = low;
            }}
            
            // 通知 Streamlit
            function notifyStreamlit() {{
                if (!window.annotator) return;
                
                const annotations = window.annotator.getAnnotations();
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{
                        type: 'annotations_updated',
                        endpoint: '{endpoint_name}',
                        annotations: annotations
                    }}
                }}, '*');
            }}
            
            // 关闭批注窗口
            function closeAnnotation() {{
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{
                        type: 'close_annotation'
                    }}
                }}, '*');
            }}
        </script>
    </body>
    </html>
    """
    
    # 显示批注界面
    st.markdown("---")
    st.markdown(f"## ✍️ 批注模式 - {endpoint_name}")
    
    col_close1, col_close2 = st.columns([3, 1])
    with col_close2:
        if st.button("关闭批注", key="close_annotation", use_container_width=True):
            st.session_state.show_annotation_modal = False
            st.session_state.annotation_endpoint = None
            st.rerun()
    
    # 渲染批注 HTML
    component_value = components.html(annotation_html, height=800, scrolling=True)
    
    # 处理来自 JavaScript 的消息
    if component_value is not None and isinstance(component_value, dict):
        if component_value.get('type') == 'annotations_updated':
            annotations = component_value.get('annotations', [])
            endpoint = component_value.get('endpoint')
            
            # 保存批注
            if save_annotations_to_task(st.session_state.selected_task_path, endpoint, annotations):
                st.success(f"✅ 批注已自动保存（共 {len(annotations)} 条）")
        
        elif component_value.get('type') == 'close_annotation':
            st.session_state.show_annotation_modal = False
            st.session_state.annotation_endpoint = None
            st.rerun()
    
    # 显示批注列表
    st.markdown("---")
    st.markdown("### 📋 批注列表")
    
    current_annotations = load_annotations_from_task(task_data, endpoint_name)
    
    if current_annotations:
        for anno in current_annotations:
            with st.expander(f"{anno.get('type', 'unknown')} - {anno.get('quote', '')[:50]}..."):
                st.markdown(f"**引用片段:** {anno.get('quote', '')}")
                st.markdown(f"**类型:** {anno.get('type', 'unknown')}")
                st.markdown(f"**严重程度:** {anno.get('severity', 'medium')}")
                st.markdown(f"**批注内容:** {anno.get('content', '')}")
                st.markdown(f"**创建时间:** {anno.get('created_at', '')}")
    else:
        st.info("暂无批注，请在文章中选择文本并添加批注")

