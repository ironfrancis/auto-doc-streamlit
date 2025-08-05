import streamlit as st
from app.language_manager import get_text

def handle_navigation():
    """处理页面导航"""
    # 检查URL参数
    query_params = st.experimental_get_query_params()
    target_page = query_params.get("page", [None])[0]
    
    if target_page:
        # 清除URL参数
        st.experimental_set_query_params()
        return target_page
    
    return None

def get_page_mapping():
    """获取页面映射"""
    return {
        "1_Creation_and_AI_Transcription": "AI内容创作与转写",
        "2_Local_MD_Review": "本地MD审核", 
        "3_Web_to_MD": "网页转MD",
        "4_Channel_Registration": "频道注册",
        "5_LLM_Endpoint_Registration": "LLM端点管理",
        "6_MD_to_HTML_Converter": "MD转HTML",
        "7_Transcribe_History": "转写历史",
        "8_LLM_Testing": "LLM测试",
        "9_AI_Smart_Layout": "AI智能布局",
        "10_InfoSource_Registration": "信息源注册",
        "11_HTML_Template_Manager": "HTML模板管理",
        "12_Image_Search_Test": "图片搜索测试",
        "13_Channel_Publish_History": "频道发布历史",
        "14_Data_Entry": "数据录入"
    }

def create_navigation_card(title, description, icon, page_key, tags=None):
    """创建导航卡片"""
    if tags is None:
        tags = []
    
    # 构建导航URL
    nav_url = f"/?page={page_key}"
    
    # 创建卡片HTML
    card_html = f"""
    <div class="feature-card" onclick="window.location.href='{nav_url}'">
        <span class="feature-icon">{icon}</span>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
        <div class="feature-tags">
    """
    
    for tag in tags:
        card_html += f'<span class="feature-tag">{tag}</span>'
    
    card_html += """
        </div>
    </div>
    """
    
    return card_html

def render_feature_cards():
    """渲染功能卡片"""
    lang = st.session_state.get("lang", "zh")
    
    if lang == "zh":
        # 中文版功能卡片
        features = {
            "content_creation": {
                "title": "📝 内容创作",
                "cards": [
                    {
                        "title": "AI内容创作与转写",
                        "description": "多频道风格写作，自动联动LLM端点，高效内容生产",
                        "icon": "🤖",
                        "page": "1_Creation_and_AI_Transcription",
                        "tags": ["AI写作", "多频道", "LLM集成"]
                    },
                    {
                        "title": "网页转Markdown",
                        "description": "一键提取网页内容并转为Markdown格式",
                        "icon": "🌐",
                        "page": "3_Web_to_MD",
                        "tags": ["网页抓取", "格式转换", "内容提取"]
                    },
                    {
                        "title": "本地MD审核",
                        "description": "本地Markdown文件审核和编辑功能",
                        "icon": "📄",
                        "page": "2_Local_MD_Review",
                        "tags": ["本地文件", "MD编辑", "内容审核"]
                    },
                    {
                        "title": "MD转HTML",
                        "description": "Markdown转HTML，支持多种模板和样式",
                        "icon": "🔄",
                        "page": "6_MD_to_HTML_Converter",
                        "tags": ["格式转换", "HTML模板", "样式定制"]
                    },
                    {
                        "title": "AI智能布局",
                        "description": "AI辅助的内容布局和排版优化",
                        "icon": "🎨",
                        "page": "9_AI_Smart_Layout",
                        "tags": ["AI布局", "排版优化", "智能设计"]
                    },
                    {
                        "title": "转写历史",
                        "description": "查看和管理所有AI转写的历史记录",
                        "icon": "📚",
                        "page": "7_Transcribe_History",
                        "tags": ["历史记录", "内容管理", "数据追踪"]
                    }
                ]
            },
            "data_management": {
                "title": "📊 数据管理",
                "cards": [
                    {
                        "title": "频道注册",
                        "description": "注册和管理内容发布频道",
                        "icon": "📋",
                        "page": "4_Channel_Registration",
                        "tags": ["频道管理", "配置设置", "风格定制"]
                    },
                    {
                        "title": "频道发布历史",
                        "description": "查看频道发布历史和数据分析",
                        "icon": "📈",
                        "page": "13_Channel_Publish_History",
                        "tags": ["数据分析", "发布记录", "可视化"]
                    },
                    {
                        "title": "数据录入",
                        "description": "手动录入和管理频道发布数据",
                        "icon": "📝",
                        "page": "14_Data_Entry",
                        "tags": ["数据录入", "手动管理", "批量操作"]
                    },
                    {
                        "title": "信息源注册",
                        "description": "注册和管理内容信息源",
                        "icon": "📰",
                        "page": "10_InfoSource_Registration",
                        "tags": ["信息源", "内容来源", "源管理"]
                    }
                ]
            },
            "system_management": {
                "title": "🔧 系统管理",
                "cards": [
                    {
                        "title": "LLM端点管理",
                        "description": "注册、测试和管理LLM API端点",
                        "icon": "🔌",
                        "page": "5_LLM_Endpoint_Registration",
                        "tags": ["API管理", "LLM配置", "端点测试"]
                    },
                    {
                        "title": "LLM测试",
                        "description": "测试LLM端点和提示词效果",
                        "icon": "🧪",
                        "page": "8_LLM_Testing",
                        "tags": ["功能测试", "提示词", "效果对比"]
                    },
                    {
                        "title": "HTML模板管理",
                        "description": "管理和自定义HTML输出模板",
                        "icon": "🎨",
                        "page": "11_HTML_Template_Manager",
                        "tags": ["模板管理", "HTML定制", "样式设计"]
                    },
                    {
                        "title": "图片搜索测试",
                        "description": "测试和验证图片搜索功能",
                        "icon": "🔍",
                        "page": "12_Image_Search_Test",
                        "tags": ["图片搜索", "功能测试", "图片管理"]
                    }
                ]
            }
        }
    else:
        # 英文版功能卡片
        features = {
            "content_creation": {
                "title": "📝 Content Creation",
                "cards": [
                    {
                        "title": "AI Content Creation & Transcription",
                        "description": "Multi-channel style writing with auto-linked LLM endpoints",
                        "icon": "🤖",
                        "page": "1_Creation_and_AI_Transcription",
                        "tags": ["AI Writing", "Multi-channel", "LLM Integration"]
                    },
                    {
                        "title": "Web to Markdown",
                        "description": "Extract web content and convert to Markdown format",
                        "icon": "🌐",
                        "page": "3_Web_to_MD",
                        "tags": ["Web Scraping", "Format Conversion", "Content Extraction"]
                    },
                    {
                        "title": "MD to HTML",
                        "description": "Convert Markdown to HTML with multiple templates",
                        "icon": "🔄",
                        "page": "6_MD_to_HTML_Converter",
                        "tags": ["Format Conversion", "HTML Templates", "Style Customization"]
                    },
                    {
                        "title": "AI Smart Layout",
                        "description": "AI-assisted content layout and typography optimization",
                        "icon": "🎨",
                        "page": "9_AI_Smart_Layout",
                        "tags": ["AI Layout", "Typography", "Smart Design"]
                    }
                ]
            },
            "data_management": {
                "title": "📊 Data Management",
                "cards": [
                    {
                        "title": "Channel Registration",
                        "description": "Register and manage content publishing channels",
                        "icon": "📋",
                        "page": "4_Channel_Registration",
                        "tags": ["Channel Management", "Configuration", "Style Customization"]
                    },
                    {
                        "title": "Channel Publish History",
                        "description": "View channel publish history and data analysis",
                        "icon": "📈",
                        "page": "13_Channel_Publish_History",
                        "tags": ["Data Analysis", "Publish Records", "Visualization"]
                    },
                    {
                        "title": "LLM Endpoint Management",
                        "description": "Register, test and manage LLM API endpoints",
                        "icon": "🔌",
                        "page": "5_LLM_Endpoint_Registration",
                        "tags": ["API Management", "LLM Configuration", "Endpoint Testing"]
                    },
                    {
                        "title": "LLM Testing",
                        "description": "Test LLM endpoints and prompt effectiveness",
                        "icon": "🧪",
                        "page": "8_LLM_Testing",
                        "tags": ["Function Testing", "Prompts", "Effect Comparison"]
                    }
                ]
            }
        }
    
    return features 