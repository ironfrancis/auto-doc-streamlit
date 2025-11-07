import sys
import os
import json
import streamlit as st
import requests
import tempfile
from datetime import datetime

from core.utils.language_manager import init_language, get_text, get_language
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon
from core.utils.api_client import APIClient, APIError, APIConnectionError

# 多语言文本定义
T = {
    "zh": {
        "page_title": "图床配置管理",
        "name": "图床名称",
        "type": "图床类型",
        "api_url": "API地址",
        "token": "认证Token",
        "description": "描述",
        "default": "默认图床",
        "enabled": "启用状态",
        "new_bed": "新图床",
        "submit": "提交",
        "edit": "编辑",
        "delete": "删除",
        "test": "测试",
        "save": "保存",
        "cancel": "取消",
        "show": "显示",
        "hide": "隐藏",
        "success": "操作成功",
        "error": "操作失败",
        "test_success": "测试成功",
        "test_failed": "测试失败"
    },
    "en": {
        "page_title": "Image Bed Manager",
        "name": "Bed Name",
        "type": "Bed Type",
        "api_url": "API URL",
        "token": "Auth Token",
        "description": "Description",
        "default": "Default Bed",
        "enabled": "Enabled",
        "new_bed": "New Bed",
        "submit": "Submit",
        "edit": "Edit",
        "delete": "Delete",
        "test": "Test",
        "save": "Save",
        "cancel": "Cancel",
        "show": "Show",
        "hide": "Hide",
        "success": "Success",
        "error": "Failed",
        "test_success": "Test Success",
        "test_failed": "Test Failed"
    }
}

st.set_page_config(page_title="图床配置管理", layout="wide")

# 加载主题
load_anthropic_theme()

# 标题
st.title("图床配置管理")
st.caption("管理多个图床服务配置，支持 SCDN 和 Lsky Pro")

# 图床类型配置
BED_TYPES = ["scdn", "lsky"]

# 使用API读取已配置的图床
def load_image_beds():
    """从API获取图床配置"""
    try:
        client = APIClient()
        image_beds = client.get_image_beds()
        # 转换API响应格式为页面需要的格式
        converted_beds = []
        for bed in image_beds:
            converted_bed = client.convert_image_bed_to_legacy_format(bed)
            converted_beds.append(converted_bed)
        return converted_beds
    except (APIError, APIConnectionError) as e:
        st.error(f"连接API失败: {str(e)}")
        return []
    except Exception as e:
        st.error(f"加载图床配置失败: {str(e)}")
        return []

def create_image_bed(bed_data):
    """通过API创建新图床"""
    try:
        client = APIClient()
        # 转换页面数据为API格式
        api_bed_data = client.convert_image_bed_to_api_format(bed_data)
        client.create_image_bed(api_bed_data)
        return True, "图床配置创建成功"
    except (APIError, APIConnectionError) as e:
        return False, f"连接API失败: {str(e)}"
    except Exception as e:
        return False, f"创建图床配置失败: {str(e)}"

def update_image_bed(bed_id, bed_data):
    """通过API更新图床"""
    try:
        client = APIClient()
        # 转换页面数据为API格式
        api_bed_data = client.convert_image_bed_to_api_format(bed_data)
        client.update_image_bed(bed_id, api_bed_data)
        return True, "图床配置更新成功"
    except (APIError, APIConnectionError) as e:
        return False, f"连接API失败: {str(e)}"
    except Exception as e:
        return False, f"更新图床配置失败: {str(e)}"

def delete_image_bed(bed_id):
    """通过API删除图床"""
    try:
        client = APIClient()
        client.delete_image_bed(bed_id)
        return True, "图床配置删除成功"
    except (APIError, APIConnectionError) as e:
        return False, f"连接API失败: {str(e)}"
    except Exception as e:
        return False, f"删除图床配置失败: {str(e)}"

def set_default_image_bed(bed_id):
    """通过API设置默认图床"""
    try:
        client = APIClient()
        # 设置指定图床为默认（API会自动处理取消其他默认图床）
        payload = {"is_default": "true"}
        client.update_image_bed(bed_id, payload)
        return True, "默认图床设置成功"
    except (APIError, APIConnectionError) as e:
        return False, f"连接API失败: {str(e)}"
    except Exception as e:
        return False, f"设置默认图床失败: {str(e)}"

def test_image_bed(bed_config):
    """测试图床连接"""
    try:
        if bed_config["type"] == "scdn":
            # 测试 SCDN 图床
            test_file_path = os.path.join(os.path.dirname(__file__), "..", "core", "utils", "test.png")
            if not os.path.exists(test_file_path):
                return False, "测试图片不存在"
            
            with open(test_file_path, 'rb') as f:
                files = {'image': f}
                response = requests.post(bed_config["api_url"], files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'url' in result:
                    return True, f"测试成功，返回URL: {result['url']}"
                else:
                    return False, f"上传失败: {result}"
            else:
                return False, f"HTTP错误 {response.status_code}: {response.text}"
                
        elif bed_config["type"] == "lsky":
            # 测试 Lsky Pro 图床
            test_file_path = os.path.join(os.path.dirname(__file__), "..", "core", "utils", "test.png")
            if not os.path.exists(test_file_path):
                return False, "测试图片不存在"
            
            headers = {
                'Authorization': f'Bearer {bed_config["token"]}',
                'Accept': 'application/json'
            }
            # 规范化 API 地址：若未以 /upload 结尾，自动补全
            api_url = bed_config["api_url"].rstrip('/')
            if not api_url.endswith('upload'):
                api_url = f"{api_url}/upload"
            with open(test_file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(api_url, files=files, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') and 'data' in result:
                    return True, f"测试成功，返回URL: {result['data'].get('links', {}).get('url', 'N/A')}"
                else:
                    return False, f"上传失败: {result.get('message', 'Unknown error')}"
            else:
                return False, f"HTTP错误 {response.status_code}: {response.text}"
        else:
            return False, "不支持的图床类型"
            
    except Exception as e:
        return False, f"测试异常: {str(e)}"

# 创建标签页
tab1, tab2 = st.tabs(["图床管理", "图床测试"])

# 第一个标签页：图床管理
with tab1:
    image_beds = load_image_beds()
    
    st.subheader("已配置的图床")
    
    cols_per_row = 2
    num_cards = len(image_beds) + 1
    rows = (num_cards + cols_per_row - 1) // cols_per_row
    
    # 初始化session state
    if "edit_idx_bed" not in st.session_state:
        st.session_state["edit_idx_bed"] = None
    if "show_token" not in st.session_state:
        st.session_state["show_token"] = {}
    if "default_idx" not in st.session_state:
        st.session_state["default_idx"] = next((i for i, bed in enumerate(image_beds) if bed.get("default")), None)
    if "test_result" not in st.session_state:
        st.session_state["test_result"] = {}
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            card_idx = row * cols_per_row + col_idx
            if card_idx < len(image_beds):
                bed = image_beds[card_idx]
                with cols[col_idx]:
                    with st.expander(bed['name'], expanded=False):
                        # 显示图床信息
                        st.markdown(f"**{T['zh']['name']}:** {bed['name']}")
                        st.markdown(f"**{T['zh']['type']}:** {bed['type']}")
                        st.markdown(f"**{T['zh']['api_url']}:** {bed['api_url']}")
                        
                        # Token 显示/隐藏
                        token_shown = st.session_state["show_token"].get(card_idx, False)
                        token_val = bed['token'] if token_shown else ("*" * 8 if bed['token'] else "")
                        st.text_input(T['zh']['token'], value=token_val, type="default", disabled=True, key=f"showtoken_{card_idx}")
                        if st.button(T['zh']['show'] if not token_shown else T['zh']['hide'], key=f"showbtn_{card_idx}"):
                            st.session_state["show_token"][card_idx] = not token_shown
                            st.rerun()
                        
                        st.markdown(f"**{T['zh']['description']}:** {bed.get('description', '')}")
                        st.markdown(f"**{T['zh']['enabled']}:** {'✅' if bed.get('enabled', True) else '❌'}")
                        
                        if st.session_state["default_idx"] == card_idx:
                            st.markdown(f"<span style='color:green;font-weight:bold'>{T['zh']['default']}</span>", unsafe_allow_html=True)
                        
                        # 操作按钮
                        btn_cols = st.columns(4)
                        with btn_cols[0]:
                            if st.button(T['zh']['edit'], key=f"edit_bed_{card_idx}"):
                                st.session_state["edit_idx_bed"] = card_idx
                                st.rerun()
                        with btn_cols[1]:
                            if st.button(T['zh']['delete'], key=f"del_bed_{card_idx}"):
                                success, message = delete_image_bed(bed["id"])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        with btn_cols[2]:
                            if st.button(T['zh']['default'], key=f"setdef_bed_{card_idx}"):
                                success, message = set_default_image_bed(bed["id"])
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        with btn_cols[3]:
                            if st.button(T['zh']['test'], key=f"test_bed_{card_idx}"):
                                success, message = test_image_bed(bed)
                                st.session_state["test_result"] = {"idx": card_idx, "success": success, "message": message}
                        
                        # 显示测试结果
                        if st.session_state.get("test_result", {}).get("idx") == card_idx:
                            with st.expander("测试结果", expanded=True):
                                result = st.session_state["test_result"]
                                if result["success"]:
                                    st.success(f"{T['zh']['test_success']}: {result['message']}")
                                else:
                                    st.error(f"{T['zh']['test_failed']}: {result['message']}")
                        
                        # 编辑模式
                        if st.session_state["edit_idx_bed"] == card_idx:
                            new_name = st.text_input(T['zh']['name'], value=bed["name"], key=f"edit_bed_name_{card_idx}")
                            new_type = st.selectbox(T['zh']['type'], BED_TYPES, index=BED_TYPES.index(bed["type"]) if bed["type"] in BED_TYPES else 0, key=f"edit_bed_type_{card_idx}")
                            new_api_url = st.text_input(T['zh']['api_url'], value=bed["api_url"], key=f"edit_bed_url_{card_idx}")
                            new_token = st.text_input(T['zh']['token'], value=bed["token"], type="password", key=f"edit_bed_token_{card_idx}")
                            new_description = st.text_area(T['zh']['description'], value=bed.get("description", ""), key=f"edit_bed_desc_{card_idx}")
                            new_enabled = st.checkbox(T['zh']['enabled'], value=bed.get("enabled", True), key=f"edit_bed_enabled_{card_idx}")

                            save_col, cancel_col = st.columns(2)
                            with save_col:
                                if st.button(T['zh']['save'], key=f"save_bed_{card_idx}"):
                                    updated_bed = {
                                        "id": bed["id"],
                                        "name": new_name,
                                        "type": new_type,
                                        "api_url": new_api_url,
                                        "token": new_token,
                                        "description": new_description,
                                        "enabled": new_enabled,
                                        "default": (st.session_state["default_idx"] == card_idx)
                                    }
                                    success, message = update_image_bed(bed["id"], updated_bed)
                                    if success:
                                        st.session_state["edit_idx_bed"] = None
                                        st.success(message)
                                        st.rerun()
                                    else:
                                        st.error(message)
                            with cancel_col:
                                if st.button(T['zh']['cancel'], key=f"cancel_bed_{card_idx}"):
                                    st.session_state["edit_idx_bed"] = None
                                    st.rerun()
                                    
            elif card_idx == len(image_beds):
                # 新建图床卡片
                with cols[col_idx]:
                    with st.expander(T['zh']['new_bed'], expanded=False):
                        st.markdown(f"**{T['zh']['new_bed']}**")
                        name = st.text_input(T['zh']['name'], key=f"new_bed_name_{card_idx}")
                        bed_type = st.selectbox(T['zh']['type'], BED_TYPES, key=f"new_bed_type_{card_idx}")
                        api_url = st.text_input(T['zh']['api_url'], key=f"new_bed_url_{card_idx}")
                        token = st.text_input(T['zh']['token'], type="password", key=f"new_bed_token_{card_idx}")
                        description = st.text_area(T['zh']['description'], key=f"new_bed_desc_{card_idx}")
                        enabled = st.checkbox(T['zh']['enabled'], value=True, key=f"new_bed_enabled_{card_idx}")
                        set_default = st.checkbox(T['zh']['default'], key=f"new_bed_default_{card_idx}")
                        
                        if st.button(T['zh']['submit'], key=f"new_bed_submit_{card_idx}"):
                            if not name.strip():
                                st.warning("请输入图床名称！")
                            elif not api_url.strip():
                                st.warning("请输入API地址！")
                            else:
                                new_bed = {
                                    "name": name,
                                    "type": bed_type,
                                    "api_url": api_url,
                                    "token": token,
                                    "description": description,
                                    "enabled": enabled,
                                    "default": set_default
                                }
                                success, message = create_image_bed(new_bed)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)

# 第二个标签页：图床测试
with tab2:
    st.title("图床连接测试")
    
    # 读取图床配置
    test_beds = load_image_beds()
    if test_beds:
        bed_names = [bed["name"] for bed in test_beds]
        selected_bed_name = st.selectbox("选择要测试的图床", bed_names)
        
        if selected_bed_name:
            selected_bed = next((bed for bed in test_beds if bed["name"] == selected_bed_name), None)
            if selected_bed:
                st.subheader(f"测试图床: {selected_bed['name']}")
                st.info(f"**类型:** {selected_bed['type']}  |  **API地址:** {selected_bed['api_url']}")
                
                if st.button("开始测试"):
                    with st.spinner("正在测试图床连接..."):
                        success, message = test_image_bed(selected_bed)
                        
                        if success:
                            st.success(f"✅ {T['zh']['test_success']}")
                            st.info(f"**测试结果:** {message}")
                        else:
                            st.error(f"❌ {T['zh']['test_failed']}")
                            st.error(f"**错误信息:** {message}")
    else:
        st.warning("没有配置任何图床，请先在\"图床管理\"标签页中添加图床配置。")

# 添加使用说明
with st.expander("使用说明"):
    st.markdown("""
    ### 图床配置说明
    
    **支持的图床类型:**
    
    1. **SCDN 图床**
       - API地址: `https://img.scdn.io/api/v1.php`
       - 无需认证Token
       - 免费图床服务
    
    2. **Lsky Pro 图床**
       - API地址: `https://your-domain.com/api/v1/upload`
       - 需要Bearer Token认证
       - 私有图床服务
    
    **配置步骤:**
    
    1. 点击"新图床"卡片
    2. 填写图床名称、类型、API地址等信息
    3. 对于Lsky Pro，需要提供Bearer Token
    4. 点击"提交"保存配置
    5. 使用"测试"功能验证配置是否正确
    
    **注意事项:**
    
    - 每个图床都需要唯一的名称
    - 只能设置一个默认图床
    - 建议先测试图床连接再使用
    - Token信息会加密存储，请妥善保管
    """)
