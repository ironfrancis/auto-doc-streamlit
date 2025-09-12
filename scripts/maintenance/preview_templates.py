#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML模板预览器
自动读取@app/html_templates下的所有模板，并提供预览功能
"""

import os
import glob
import json
import re
from jinja2 import Environment, BaseLoader
import streamlit as st

# 设置页面配置
st.set_page_config(
    page_title="HTML模板预览器",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("🎨 HTML模板预览器")
st.markdown("---")

# 模板管理类
class TemplatePreviewer:
    def __init__(self):
        self.template_dir = "app/html_templates"
        self.template_info_file = "app/template_info.json"
        self.load_template_info()
    
    def load_template_info(self):
        """加载模板信息"""
        if os.path.exists(self.template_info_file):
            with open(self.template_info_file, 'r', encoding='utf-8') as f:
                self.template_info = json.load(f)
        else:
            self.template_info = {}
    
    def get_template_files(self):
        """获取所有模板文件"""
        pattern = os.path.join(self.template_dir, "*.html")
        return sorted(glob.glob(pattern))
    
    def get_template_info(self, filepath):
        """获取模板信息"""
        filename = os.path.basename(filepath)
        return self.template_info.get(filename, {})
    
    def read_template(self, filepath):
        """读取模板内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading template: {str(e)}"
    
    def extract_variables(self, content):
        """从模板内容中提取变量"""
        # 匹配 {{ variable }} 或 {{ variable|filter }} 格式的变量
        variables = re.findall(r'\{\{\s*([^}|]+)', content)
        # 去重并去除空格
        variables = list(set([var.strip() for var in variables]))
        return variables
    
    def render_template(self, filepath, variables):
        """渲染模板"""
        try:
            content = self.read_template(filepath)
            template = Environment(loader=BaseLoader()).from_string(content)
            return template.render(**variables)
        except Exception as e:
            return f"渲染模板失败: {str(e)}"

# 初始化预览器
previewer = TemplatePreviewer()

# 获取所有模板文件
template_files = previewer.get_template_files()

# 侧边栏
with st.sidebar:
    st.markdown("### 📋 模板列表")
    
    # 模板统计
    st.markdown(f"**总计:** {len(template_files)} 个模板")
    
    # 分类统计
    categories = {}
    for filepath in template_files:
        info = previewer.get_template_info(filepath)
        category = info.get("category", "未分类")
        categories[category] = categories.get(category, 0) + 1
    
    st.markdown("**📁 分类统计:**")
    for category, count in categories.items():
        st.markdown(f"- {category}: {count}")
    
    st.markdown("---")
    
    # 模板选择
    template_names = [os.path.basename(f) for f in template_files]
    selected_template = st.selectbox("选择模板", template_names)

# 主内容区域
if not template_files:
    st.info("未找到任何HTML模板文件")
else:
    # 找到选中的模板路径
    selected_filepath = None
    for filepath in template_files:
        if os.path.basename(filepath) == selected_template:
            selected_filepath = filepath
            break
    
    if selected_filepath:
        # 获取模板信息
        template_info = previewer.get_template_info(selected_filepath)
        template_content = previewer.read_template(selected_filepath)
        template_variables = previewer.extract_variables(template_content)
        
        # 显示模板信息
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📄 模板详情")
            
            # 模板基本信息
            st.markdown(f"**名称:** {template_info.get('name', '未命名')}")
            st.markdown(f"**描述:** {template_info.get('description', '无描述')}")
            st.markdown(f"**分类:** {template_info.get('category', '未分类')}")
            
            # 模板变量
            st.markdown("**🔍 模板变量:**")
            if template_variables:
                for var in template_variables:
                    st.code(var, language="python")
            else:
                st.info("该模板没有定义变量")
            
            # 模板代码
            with st.expander("查看模板代码", expanded=False):
                st.code(template_content, language="html")
        
        with col2:
            st.markdown("### ▶️ 模板预览")
            
            # 变量输入
            st.markdown("**🔧 输入变量值:**")
            variables = {}
            
            # 为每个变量创建输入框
            if template_variables:
                for var in template_variables:
                    # 处理带默认值的变量，如 "title or '默认标题'"
                    if 'or' in var:
                        var_name = var.split('or')[0].strip()
                        default_value = var.split('or')[1].strip().strip("'\"")
                        variables[var_name] = st.text_input(f"{var_name}", value=default_value, key=f"var_{var_name}")
                    else:
                        variables[var] = st.text_input(var, value="", key=f"var_{var}")
                
                # 渲染按钮
                if st.button("渲染模板", type="primary"):
                    rendered_content = previewer.render_template(selected_filepath, variables)
                    st.session_state[f"rendered_{selected_template}"] = rendered_content
            else:
                st.info("该模板没有变量需要输入")
                # 如果没有变量，直接渲染
                if st.button("渲染模板", type="primary"):
                    rendered_content = previewer.render_template(selected_filepath, {})
                    st.session_state[f"rendered_{selected_template}"] = rendered_content
            
            # 显示渲染结果
            if f"rendered_{selected_template}" in st.session_state:
                st.markdown("**🖼️ 预览效果:**")
                st.components.v1.html(st.session_state[f"rendered_{selected_template}"], height=500, scrolling=True)
                
                # 下载渲染结果
                st.download_button(
                    label="📥 下载渲染结果",
                    data=st.session_state[f"rendered_{selected_template}"],
                    file_name=f"rendered_{selected_template}",
                    mime="text/html"
                )

# 底部信息
st.markdown("---")
st.markdown("### 💡 使用说明")
st.markdown("""
1. 在左侧选择要预览的HTML模板
2. 查看模板的详细信息和变量
3. 在右侧输入变量值（如果有的话）
4. 点击"渲染模板"按钮查看预览效果
5. 可以下载渲染后的HTML文件
""")

if __name__ == "__main__":
    pass