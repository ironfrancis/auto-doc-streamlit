import sys
import os

# 使用简化路径管理
from simple_paths import *

import streamlit as st
from language_manager import init_language, get_text
import glob
import json
from datetime import datetime
import shutil
from jinja2 import Environment, BaseLoader
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

# 初始化语言设置
init_language()

class TemplateManager:
    """HTML模板管理类"""
    
    def __init__(self):
        self.template_dir = "static/templates"
        self.template_info_file = "config/template_info.json"
        # 确保模板目录存在
        os.makedirs(self.template_dir, exist_ok=True)
        self.load_template_info()
    
    def load_template_info(self):
        """加载模板信息"""
        if os.path.exists(self.template_info_file):
            with open(self.template_info_file, 'r', encoding='utf-8') as f:
                self.template_info = json.load(f)
        else:
            self.template_info = {}
    
    def save_template_info(self):
        """保存模板信息"""
        with open(self.template_info_file, 'w', encoding='utf-8') as f:
            json.dump(self.template_info, f, ensure_ascii=False, indent=2)
    
    def get_template_files(self):
        """获取所有模板文件"""
        pattern = os.path.join(self.template_dir, "*.html")
        return sorted(glob.glob(pattern))
    
    def get_template_info(self, filepath):
        """获取模板信息"""
        filename = os.path.basename(filepath)
        
        if filename not in self.template_info:
            # 创建默认信息
            self.template_info[filename] = {
                "name": filename.replace('.html', '').replace('_', ' ').title(),
                "description": "HTML模板",
                "category": "General",
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "variables": []  # 模板变量
            }
            self.save_template_info()
        
        # 更新文件信息
        stat = os.stat(filepath)
        self.template_info[filename]["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        self.template_info[filename]["file_size"] = stat.st_size
        self.template_info[filename]["lines_count"] = self.count_lines(filepath)
        
        return self.template_info[filename]
    
    def count_lines(self, filepath):
        """统计文件行数"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
    
    def read_template(self, filepath):
        """读取模板内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading template: {str(e)}"
    
    def save_template(self, filename, content, info):
        """保存模板"""
        filepath = os.path.join(self.template_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 更新模板信息
            self.template_info[filename] = info
            self.template_info[filename]["modified"] = datetime.now().isoformat()
            self.save_template_info()
            
            return True
        except Exception as e:
            st.error(f"保存模板失败: {str(e)}")
            return False
    
    def delete_template(self, filename):
        """删除模板"""
        filepath = os.path.join(self.template_dir, filename)
        
        try:
            os.remove(filepath)
            if filename in self.template_info:
                del self.template_info[filename]
                self.save_template_info()
            return True
        except Exception as e:
            st.error(f"删除模板失败: {str(e)}")
            return False
    
    def create_template(self, filename, content, info):
        """创建新模板"""
        return self.save_template(filename, content, info)
    
    def render_template(self, filepath, variables):
        """渲染模板"""
        try:
            content = self.read_template(filepath)
            template = Environment(loader=BaseLoader()).from_string(content)
            return template.render(**variables)
        except Exception as e:
            return f"渲染模板失败: {str(e)}"
    
    def extract_variables(self, content):
        """从模板内容中提取变量"""
        import re
        # 匹配 {{ variable }} 或 {{ variable|filter }} 格式的变量
        variables = re.findall(r'\{\{\s*([^}|]+)', content)
        # 去重并去除空格
        variables = list(set([var.strip() for var in variables]))
        return variables

def main():
    st.set_page_config(page_title="HTML模板管理", layout="wide")
    
    # 加载主题
    load_anthropic_theme()
    
    st.title(get_text("page_title"))
    st.markdown("---")
    
    # 初始化模板管理器
    template_manager = TemplateManager()
    
    # 侧边栏操作
    with st.sidebar:
        st.markdown("### 🛠️ 操作面板")
        
        # 创建新模板
        if st.button(get_text("create_template"), type="primary"):
            st.session_state.show_create = True
            st.session_state.show_edit = False
            st.session_state.show_preview = False
            st.session_state.show_render = False
        
        st.markdown("---")
        
        # 模板统计
        template_files = template_manager.get_template_files()
        st.markdown(f"**📊 模板统计:**")
        st.markdown(f"- 总数量: {len(template_files)}")
        
        # 分类统计
        categories = {}
        for filepath in template_files:
            info = template_manager.get_template_info(filepath)
            category = info.get("category", "General")
            categories[category] = categories.get(category, 0) + 1
        
        # 显示分类选择
        st.markdown("**📁 分类筛选:**")
        selected_category = st.selectbox("选择分类", ["全部"] + list(categories.keys()))
        
        for category, count in categories.items():
            st.markdown(f"- {category}: {count}")
    
    # 主内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 " + get_text("template_overview"))
        
        # 根据分类筛选模板
        if selected_category != "全部":
            filtered_files = []
            for filepath in template_files:
                info = template_manager.get_template_info(filepath)
                if info.get("category") == selected_category:
                    filtered_files.append(filepath)
            template_files = filtered_files
        
        if not template_files:
            st.info(get_text("no_templates"))
        else:
            # 模板卡片网格
            cols = st.columns(3)
            
            for i, filepath in enumerate(template_files):
                filename = os.path.basename(filepath)
                info = template_manager.get_template_info(filepath)
                
                col_idx = i % 3
                
                with cols[col_idx]:
                    # 模板卡片
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 15px;
                            margin: 10px 0;
                            background: white;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        ">
                            <h4 style="margin: 0 0 10px 0; color: #333;">{info['name']}</h4>
                            <p style="margin: 0 0 10px 0; color: #666; font-size: 14px;">{info['description']}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 12px; font-size: 12px;">{info['category']}</span>
                                <span style="color: #999; font-size: 12px;">{info['lines_count']} 行</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 操作按钮
                        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                        
                        with col_btn1:
                            if st.button(f"预览", key=f"preview_{i}"):
                                st.session_state.show_preview = True
                                st.session_state.preview_file = filepath
                                st.session_state.show_edit = False
                                st.session_state.show_create = False
                                st.session_state.show_render = False
                        
                        with col_btn2:
                            if st.button(f"编辑", key=f"edit_{i}"):
                                st.session_state.show_edit = True
                                st.session_state.edit_file = filepath
                                st.session_state.show_preview = False
                                st.session_state.show_create = False
                                st.session_state.show_render = False
                        
                        with col_btn3:
                            if st.button(f"渲染", key=f"render_{i}"):
                                st.session_state.show_render = True
                                st.session_state.render_file = filepath
                                st.session_state.show_preview = False
                                st.session_state.show_edit = False
                                st.session_state.show_create = False
                        
                        with col_btn4:
                            if st.button(f"删除", key=f"delete_{i}"):
                                if st.session_state.get("confirm_delete", False):
                                    if template_manager.delete_template(filename):
                                        st.success(get_text("template_deleted"))
                                        st.rerun()
                                else:
                                    st.session_state.confirm_delete = True
                                    st.warning(get_text("confirm_delete"))
    
    with col2:
        st.markdown("### 📝 快速操作")
        
        # 创建新模板表单
        if st.session_state.get("show_create", False):
            st.markdown("#### ➕ " + get_text("create_template"))
            
            with st.form("create_template_form"):
                new_filename = st.text_input("文件名", value="new_template.html")
                new_name = st.text_input(get_text("template_name"), value="新模板")
                new_description = st.text_area(get_text("template_description"), value="这是一个新的HTML模板")
                new_category = st.selectbox(get_text("template_category"), 
                                          ["General", "News", "Blog", "Academic", "Business", "Creative"],
                                          index=0)
                
                new_content = st.text_area("模板内容", height=300, 
                                          value="""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title or '新模板' }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        .content { line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title or '新模板' }}</h1>
        <div class="content">{{ content|safe }}</div>
    </div>
</body>
</html>""")
                
                if st.form_submit_button(get_text("save_template")):
                    # 提取模板变量
                    variables = template_manager.extract_variables(new_content)
                    
                    info = {
                        "name": new_name,
                        "description": new_description,
                        "category": new_category,
                        "created": datetime.now().isoformat(),
                        "modified": datetime.now().isoformat(),
                        "variables": variables
                    }
                    
                    if template_manager.create_template(new_filename, new_content, info):
                        st.success(get_text("template_saved"))
                        st.session_state.show_create = False
                        st.rerun()
        
        # 编辑模板
        elif st.session_state.get("show_edit", False):
            filepath = st.session_state.edit_file
            filename = os.path.basename(filepath)
            info = template_manager.get_template_info(filepath)
            content = template_manager.read_template(filepath)
            
            st.markdown("#### ✏️ " + get_text("edit_template"))
            
            with st.form("edit_template_form"):
                info["name"] = st.text_input(get_text("template_name"), value=info["name"])
                info["description"] = st.text_area(get_text("template_description"), value=info["description"])
                info["category"] = st.selectbox(get_text("template_category"), 
                                               ["General", "News", "Blog", "Academic", "Business", "Creative"],
                                               index=["General", "News", "Blog", "Academic", "Business", "Creative"].index(info.get("category", "General")))
                
                edited_content = st.text_area("模板内容", value=content, height=400)
                
                # 显示模板变量
                variables = template_manager.extract_variables(edited_content)
                st.markdown("**🔍 模板变量:**")
                if variables:
                    for var in variables:
                        st.code(var, language="python")
                else:
                    st.info("未检测到模板变量")
                
                if st.form_submit_button(get_text("save_template")):
                    # 更新模板变量
                    info["variables"] = variables
                    
                    if template_manager.save_template(filename, edited_content, info):
                        st.success(get_text("template_saved"))
                        st.session_state.show_edit = False
                        st.rerun()
        
        # 预览模板
        elif st.session_state.get("show_preview", False):
            filepath = st.session_state.preview_file
            filename = os.path.basename(filepath)
            info = template_manager.get_template_info(filepath)
            content = template_manager.read_template(filepath)
            
            st.markdown("#### 👁️ " + get_text("preview_template"))
            st.markdown(f"**{info['name']}**")
            st.markdown(f"*{info['description']}*")
            st.markdown(f"分类: {info['category']}")
            
            # 显示模板信息
            st.markdown("**📊 模板信息:**")
            st.markdown(f"- 文件大小: {info.get('file_size', 0)} 字节")
            st.markdown(f"- 代码行数: {info.get('lines_count', 0)} 行")
            st.markdown(f"- 最后修改: {info.get('modified', 'Unknown')}")
            
            # 显示模板变量
            st.markdown("**🔍 模板变量:**")
            if info.get("variables"):
                for var in info["variables"]:
                    st.code(var, language="python")
            else:
                st.info("未检测到模板变量")
            
            # 显示模板内容
            with st.expander("查看模板代码", expanded=True):
                st.code(content, language="html")
        
        # 渲染模板
        elif st.session_state.get("show_render", False):
            filepath = st.session_state.render_file
            filename = os.path.basename(filepath)
            info = template_manager.get_template_info(filepath)
            content = template_manager.read_template(filepath)
            
            st.markdown("#### ▶️ " + get_text("render_template"))
            st.markdown(f"**{info['name']}**")
            
            # 模板变量输入
            st.markdown("**🔧 输入变量值:**")
            variables = {}
            
            # 为每个变量创建输入框
            if info.get("variables"):
                for var in info["variables"]:
                    # 处理带默认值的变量，如 "title or '默认标题'"
                    if 'or' in var:
                        var_name = var.split('or')[0].strip()
                        default_value = var.split('or')[1].strip().strip("'\"")
                        variables[var_name] = st.text_input(f"{var_name} (默认: {default_value})", value=default_value)
                    else:
                        variables[var] = st.text_input(var, value="")
            else:
                st.info("该模板没有定义变量")
            
            # 渲染按钮
            if st.button("渲染模板"):
                rendered_content = template_manager.render_template(filepath, variables)
                st.session_state.rendered_content = rendered_content
            
            # 显示渲染结果
            if "rendered_content" in st.session_state:
                st.markdown("**🖼️ 渲染结果:**")
                st.components.v1.html(st.session_state.rendered_content, height=400, scrolling=True)
                
                # 下载渲染结果
                st.download_button(
                    label="下载渲染结果",
                    data=st.session_state.rendered_content,
                    file_name=f"rendered_{filename}",
                    mime="text/html"
                )
    
    # 底部信息
    st.markdown("---")
    st.markdown("### 💡 使用说明")
    st.markdown("""
    - **预览**: 查看模板的HTML代码和基本信息
    - **编辑**: 修改模板内容、名称、描述和分类
    - **渲染**: 输入变量值并查看模板渲染效果
    - **删除**: 永久删除模板文件（请谨慎操作）
    - **创建**: 添加新的HTML模板
    """)

if __name__ == "__main__":
    main() 