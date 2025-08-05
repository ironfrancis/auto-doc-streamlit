import sys
import os

# 添加正确的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import streamlit as st
from language_manager import init_language, get_text
import glob
import json
from datetime import datetime
import shutil

# 初始化语言设置
init_language()

class TemplateManager:
    """HTML模板管理类"""
    
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
                "modified": datetime.now().isoformat()
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

def main():
    st.set_page_config(page_title=get_text("page_title"), layout="wide")
    st.title("🎨 " + get_text("page_title"))
    st.markdown("---")
    
    # 初始化模板管理器
    template_manager = TemplateManager()
    
    # 侧边栏操作
    with st.sidebar:
        st.markdown("### 🛠️ 操作面板")
        
        # 创建新模板
        if st.button("➕ " + get_text("create_template"), type="primary"):
            st.session_state.show_create = True
            st.session_state.show_edit = False
            st.session_state.show_preview = False
        
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
        
        for category, count in categories.items():
            st.markdown(f"- {category}: {count}")
    
    # 主内容区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 " + get_text("template_overview"))
        
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
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        
                        with col_btn1:
                            if st.button("👁️ 预览", key=f"preview_{i}"):
                                st.session_state.show_preview = True
                                st.session_state.preview_file = filepath
                                st.session_state.show_edit = False
                                st.session_state.show_create = False
                        
                        with col_btn2:
                            if st.button("✏️ 编辑", key=f"edit_{i}"):
                                st.session_state.show_edit = True
                                st.session_state.edit_file = filepath
                                st.session_state.show_preview = False
                                st.session_state.show_create = False
                        
                        with col_btn3:
                            if st.button("🗑️ 删除", key=f"delete_{i}"):
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
                new_name = st.text_input(get_text("template_name"))
                new_description = st.text_area(get_text("template_description"))
                new_category = st.selectbox(get_text("template_category"), 
                                          ["General", "News", "Blog", "Academic", "Business", "Creative"])
                
                new_content = st.text_area("模板内容", height=300, 
                                          value="""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title or 'New Template' }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        .content { line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title or 'New Template' }}</h1>
        <div class="content">{{ content|safe }}</div>
    </div>
</body>
</html>""")
                
                if st.form_submit_button(get_text("save_template")):
                    info = {
                        "name": new_name,
                        "description": new_description,
                        "category": new_category,
                        "created": datetime.now().isoformat(),
                        "modified": datetime.now().isoformat()
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
                
                if st.form_submit_button(get_text("save_template")):
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
            st.markdown("**模板信息:**")
            st.markdown(f"- 文件大小: {info.get('file_size', 0)} 字节")
            st.markdown(f"- 代码行数: {info.get('lines_count', 0)} 行")
            st.markdown(f"- 最后修改: {info.get('modified', 'Unknown')}")
            
            # 显示模板内容
            with st.expander("查看模板代码", expanded=False):
                st.code(content, language="html")
    
    # 底部信息
    st.markdown("---")
    st.markdown("### 💡 使用说明")
    st.markdown("""
    - **预览**: 查看模板的HTML代码和基本信息
    - **编辑**: 修改模板内容、名称、描述和分类
    - **删除**: 永久删除模板文件（请谨慎操作）
    - **创建**: 添加新的HTML模板
    """)

if __name__ == "__main__":
    main() 