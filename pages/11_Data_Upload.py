# 使用简化路径管理
from simple_paths import *

from core.wechat.wechat_data_processor import (
    load_csv_path, 
    append_record_to_csv, 
    update_wechat_data_from_excel,
    sync_wechat_to_calendar
)
from core.crawlers.toutiao_api import fetch_article_by_site, update_toutiao_publish_history
import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
from core.wechat.cookie_manager import CookieManager
from core.utils.token_manager import TokenManager
from core.utils.theme_loader import load_anthropic_theme
from core.utils.icon_library import get_icon

# 加载主题
load_anthropic_theme()

st.title("数据上传与管理")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Excel文件上传", "微信公众号数据获取", "Cookie管理", "数据处理", "智能Cookie获取"])

with tab1:
    st.header("上传微信公众号导出的Excel文件")
    st.info("支持.xls和.xlsx格式的微信公众号数据导出文件")
    
    uploaded_file = st.file_uploader("上传Excel文件", type=['xls', 'xlsx'])
    if uploaded_file is not None:
        st.success("文件上传成功！")
        
        try:
            upload_df = pd.read_excel(uploaded_file)
            st.write(f"文件包含 {len(upload_df)} 行数据")
            st.dataframe(upload_df.head(10))
            
            if st.button("保存到CSV"):
                with st.spinner("正在保存数据..."):
                    append_record_to_csv(upload_df)
                st.success("数据保存成功！")
                
                # 自动同步到日历
                if st.button("同步到日历"):
                    with st.spinner("正在同步到日历..."):
                        if sync_wechat_to_calendar():
                            st.success("数据已成功同步到日历！")
                        else:
                            st.error("同步到日历失败")
        except Exception as e:
            st.error(f"读取文件失败: {str(e)}")

with tab2:
    st.header("自动获取微信公众号数据")
    st.info("直接从微信公众平台获取最新数据，无需手动导出Excel文件")
    
    # 动态设置默认日期
    from datetime import datetime, timedelta
    
    # 显示当前时间信息
    current_time = datetime.now()
    st.info(f"当前时间：{current_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
    
    # 显示默认设置信息
    st.success(f"默认设置：开始日期为2025年6月9日，结束日期为当前日期")
    
    # 开始日期：设置为2025年6月9日
    default_begin_date = "20250609"
    
    # 结束日期：设置为当前日期
    current_date = datetime.now()
    default_end_date = current_date.strftime("%Y%m%d")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 初始化session_state中的日期
        if 'begin_date' not in st.session_state:
            st.session_state.begin_date = datetime.strptime(default_begin_date, "%Y%m%d").date()
        if 'end_date' not in st.session_state:
            st.session_state.end_date = current_date.date()
        
        # 使用日期选择器，然后转换为YYYYMMDD格式
        begin_date_picker = st.date_input(
            "开始日期",
            value=st.session_state.begin_date,
            help="选择开始日期",
            key="begin_date_picker"
        )
        begin_date = begin_date_picker.strftime("%Y%m%d")
        
        end_date_picker = st.date_input(
            "结束日期",
            value=st.session_state.end_date,
            help="选择结束日期",
            key="end_date_picker"
        )
        end_date = end_date_picker.strftime("%Y%m%d")
        
        # 显示转换后的日期格式
        st.caption(f"开始日期: {begin_date} | 结束日期: {end_date}")
        
        # 快速设置按钮
        st.write("**快速设置日期范围：**")
        col_quick1, col_quick2, col_quick3 = st.columns(3)
        
        with col_quick1:
            if st.button("最近7天", key="last_7_days"):
                st.session_state.begin_date = (current_date - timedelta(days=6)).date()
                st.session_state.end_date = current_date.date()
                st.rerun()
        
        with col_quick2:
            if st.button("最近30天", key="last_30_days"):
                st.session_state.begin_date = (current_date - timedelta(days=29)).date()
                st.session_state.end_date = current_date.date()
                st.rerun()
        
        with col_quick3:
            if st.button("本月", key="this_month"):
                st.session_state.begin_date = current_date.replace(day=1).date()
                st.session_state.end_date = current_date.date()
                st.rerun()
    
    with col2:
        account_name = st.selectbox(
            "公众号名称",
            ["AGI观察室", "AGI启示录", "AI 万象志", "人工智能漫游指南", "自定义"],
            help="选择要获取数据的公众号"
        )
        
        if account_name == "自定义":
            custom_account = st.text_input("请输入公众号名称")
            if custom_account:
                account_name = custom_account
    
    # 初始化Token管理器
    if 'token_manager' not in st.session_state:
        st.session_state.token_manager = TokenManager()
    
    token_manager = st.session_state.token_manager
    
    # 根据选择的公众号自动获取对应的Token
    default_token = token_manager.get_token(account_name) or "254511315"
    
    token = st.text_input(
        "Token", 
        value=default_token, 
        help="微信公众平台的token"
    )
    
    # 添加更新Token按钮
    if st.button("更新Token", key="update_token_btn"):
        if token.strip():
            if token_manager.set_token(account_name, token.strip()):
                st.success(f"{account_name} 的Token已更新！")
                st.rerun()
            else:
                st.error("Token更新失败！")
        else:
            st.warning("请输入Token字符串")
    
    # 参数验证和显示
    st.write("**参数验证：**")
    if begin_date and end_date and token:
        try:
            begin_dt = datetime.strptime(begin_date, "%Y%m%d")
            end_dt = datetime.strptime(end_date, "%Y%m%d")
            days_diff = (end_dt - begin_dt).days
            
            if begin_dt > end_dt:
                st.error(f"开始日期不能晚于结束日期！")
            elif days_diff > 365:
                st.warning(f"日期范围超过一年，可能需要较长时间获取")
            else:
                st.success(f"参数有效，将获取 {days_diff + 1} 天的数据")
                
        except ValueError:
            st.error(f"日期格式错误")
    else:
        st.warning(f"请填写完整的参数信息")
    
    # 动态获取Cookie配置
    st.subheader("Cookie配置")
    
    # 初始化Cookie管理器
    if 'cookie_manager' not in st.session_state:
        st.session_state.cookie_manager = CookieManager()
    
    cookie_manager = st.session_state.cookie_manager
    
    # 根据选择的公众号自动选择对应的Cookie
    selected_cookies = ""
    cookie_status = "未配置"
    
    # 获取当前账号的Cookie状态
    if account_name != "自定义":
        cookie_info = cookie_manager.get_cookie_status(account_name)
        selected_cookies = cookie_manager.get_cookie(account_name) or ""
        
        # 显示Cookie状态
        if cookie_info["status"] == "fresh":
            cookie_status = f"{""} 新鲜 (更新于 {cookie_info["last_updated'].strftime('%H:%M')})"
        elif cookie_info["status"] == "warning":
            cookie_status = f"{""} 建议更新 (更新于 {cookie_info["last_updated'].strftime('%H:%M')})"
        elif cookie_info["status"] == "expired":
            cookie_status = f"{""} 已过期 (更新于 {cookie_info["last_updated'].strftime('%H:%M')})"
        elif cookie_info["status"] == "inactive":
            cookie_status = f"{""} 未配置"
        else:
            cookie_status = f"{""} 未知状态"
    
    # 显示Cookie输入框
    selected_cookies = st.text_area(
        f"{account_name} Cookie",
        value=selected_cookies,
        height=80,
        help="从Cookie管理标签页复制对应的Cookie，或直接输入新的Cookie"
    )
    
    # 显示Cookie状态
    st.info(f"Cookie状态: {cookie_status}")
    
    # 添加更新Cookie按钮
    if st.button("更新Cookie", key="update_cookie_btn"):
        if selected_cookies.strip():
            if cookie_manager.set_cookie(account_name, selected_cookies.strip()):
                st.success(f"{account_name} 的Cookie已更新！")
                st.rerun()
            else:
                st.error("Cookie更新失败！")
        else:
            st.warning("请输入Cookie字符串")
    
    if st.button("获取数据", type="primary"):
        if not begin_date or not end_date or not token:
            st.error("请填写完整的参数信息")
        elif not selected_cookies.strip():
            st.error("请配置Cookie信息")
        else:
            with st.spinner(f"正在获取 {account_name} 的数据..."):
                try:
                    # 验证日期格式
                    try:
                        # 验证日期格式是否正确
                        datetime.strptime(begin_date, "%Y%m%d")
                        datetime.strptime(end_date, "%Y%m%d")
                    except ValueError:
                        st.error("日期格式错误！请使用YYYYMMDD格式，如：20250609")
                        st.stop()
                    
                    # 验证日期范围
                    begin_dt = datetime.strptime(begin_date, "%Y%m%d")
                    end_dt = datetime.strptime(end_date, "%Y%m%d")
                    
                    if begin_dt > end_dt:
                        st.error("开始日期不能晚于结束日期！")
                        st.stop()
                    
                    # 显示即将获取的参数信息
                    st.info(f"准备获取数据：{account_name}，时间范围：{begin_date} 到 {end_date}")
                    
                    # 显示详细参数信息（调试用）
                    with st.expander(f"查看传递的参数"):
                        st.write(f"**账号名称:** {account_name}")
                        st.write(f"**开始日期:** {begin_date}")
                        st.write(f"**结束日期:** {end_date}")
                        st.write(f"**Token:** {token}")
                        st.write(f"**Cookie长度:** {len(selected_cookies)} 字符")
                        st.write(f"**Cookie状态:** {cookie_status}")
                    
                    # 获取数据
                    st.info("正在调用数据获取函数...")
                    result = update_wechat_data_from_excel(
                        begin_date=begin_date,
                        end_date=end_date,
                        token=token,
                        cookies=selected_cookies,
                        account_name=account_name
                    )
                    
                    if result:
                        st.success(f"{account_name} 数据获取成功！")
                    else:
                        st.warning(f"{account_name} 数据获取完成，但可能没有新数据")
                    
                    # 自动更新Cookie和Token时间
                    if cookie_manager.refresh_cookie(account_name):
                        st.success("Cookie时间已自动更新！")
                    if token_manager.refresh_token(account_name):
                        st.success("Token时间已自动更新！")
                    
                    # 显示获取到的数据
                    st.subheader(f"获取到的数据预览")
                    
                    # 尝试读取生成的Excel文件
                    try:
                        if os.path.exists("result.xls"):
                            df = pd.read_excel("result.xls")
                            st.write(f"{""} 成功获取到 {len(df)} 行数据")
                            
                            # 显示数据统计
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("总行数", len(df))
                            with col2:
                                st.metric("总列数", len(df.columns))
                            with col3:
                                if '总阅读人数' in df.columns:
                                    total_reads = df['总阅读人数'].sum() if df['总阅读人数'].dtype in ['int64', 'float64'] else 0
                                    st.metric("总阅读量", f"{total_reads:,}")
                            
                            # 显示列名
                            st.write("**列名信息：**")
                            st.code(", ".join(df.columns.tolist()))
                            
                            # 显示数据预览
                            st.write("**数据预览：**")
                            st.dataframe(df.head(10), use_container_width=True)
                            
                            # 显示数据统计信息
                            if '发表时间' in df.columns:
                                st.write("**时间范围：**")
                                try:
                                    df['发表时间'] = pd.to_datetime(df['发表时间'], format='%Y%m%d', errors='coerce')
                                    min_date = df['发表时间'].min()
                                    max_date = df['发表时间'].max()
                                    if pd.notna(min_date) and pd.notna(max_date):
                                        st.info(f"从 {min_date.strftime('%Y-%m-%d')} 到 {max_date.strftime('%Y-%m-%d')}")
                                except:
                                    st.info("时间格式解析失败")
                            
                            # 提供下载链接
                            with open("result.xls", "rb") as file:
                                st.download_button(
                                    label=f"下载Excel文件",
                                    data=file.read(),
                                    file_name=f"{account_name}_{begin_date}_{end_date}.xls",
                                    mime="application/vnd.ms-excel"
                                )
                                
                        else:
                            st.warning("未找到生成的Excel文件，可能数据获取失败")
                            
                    except Exception as e:
                        st.error(f"读取Excel文件失败: {str(e)}")
                        st.info("请检查数据是否成功获取")
                        
                except Exception as e:
                    st.error(f"获取数据失败: {str(e)}")

with tab3:
    st.header("Cookie和Token管理")
    st.info("管理不同公众号的登录Cookie和Token，用于自动获取数据")
    
    # 确保Cookie管理器和Token管理器已初始化
    if 'cookie_manager' not in st.session_state:
        st.session_state.cookie_manager = CookieManager()
    if 'token_manager' not in st.session_state:
        st.session_state.token_manager = TokenManager()
    
    cookie_manager = st.session_state.cookie_manager
    token_manager = st.session_state.token_manager
    
    # Cookie和Token配置管理
    st.subheader("Cookie和Token配置管理")
    
    # 添加新账号
    with st.expander("添加新账号"):
        new_account = st.text_input("新账号名称")
        new_description = st.text_input("账号描述")
        new_token = st.text_input("Token")
        if st.button("添加账号"):
            if new_account:
                # 同时添加到Cookie和Token管理器
                cookie_success = cookie_manager.add_custom_account(new_account, new_description)
                token_success = token_manager.add_custom_account(new_account, new_description)
                
                if new_token:
                    token_manager.set_token(new_account, new_token, new_description)
                
                if cookie_success and token_success:
                    st.success(f"账号 {new_account} 添加成功！")
                    st.rerun()
                else:
                    st.error("账号添加失败！")
    
    # Cookie获取说明
    st.subheader("如何获取Cookie")
    with st.expander("Cookie获取步骤"):
        st.markdown("""
        1. **登录微信公众平台**：https://mp.weixin.qq.com/
        2. **打开浏览器开发者工具**：
           - Chrome/Edge: 按F12或右键"检查"
           - Firefox: 按F12或右键"检查元素"
        3. **切换到Network标签页**
        4. **刷新页面或进行任何操作**
        5. **找到任意请求**，右键选择"Copy > Copy as cURL (bash)"
        6. **从cURL命令中提取Cookie部分**：
           ```bash
           curl 'https://mp.weixin.qq.com/...' \\
             -H 'Cookie: 这里就是你要的Cookie字符串'
           ```
        7. **复制Cookie字符串**到对应的输入框
        """)
    
    # 配置文件信息
    st.subheader("配置文件信息")
    cookie_config_info = cookie_manager.get_config_info()
    token_config_info = token_manager.get_config_info()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总账号数", cookie_config_info["total_accounts"])
    with col2:
        st.metric("活跃Cookie", cookie_config_info["active_accounts"])
    with col3:
        st.metric("过期Cookie", cookie_config_info["expired_accounts"])
    with col4:
        st.metric("活跃Token", token_config_info["active_accounts"])
    
    # 备份和恢复
    st.subheader("备份和恢复")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("备份Cookie配置"):
            backup_path = cookie_manager.backup_config()
            if backup_path:
                st.success(f"Cookie配置已备份到: {backup_path}")
            else:
                st.error("Cookie配置备份失败")
    
    with col2:
        if st.button("备份Token配置"):
            backup_path = token_manager.backup_config()
            if backup_path:
                st.success(f"Token配置已备份到: {backup_path}")
            else:
                st.error("Token配置备份失败")
    
    with col3:
        st.info("Cookie配置文件: " + cookie_config_info["config_file"])
        st.info("Token配置文件: " + token_config_info["config_file"])
    
    # 显示所有账号的Cookie和Token状态
    st.subheader("Cookie和Token状态监控")
    
    all_cookies = cookie_manager.get_all_cookies()
    all_tokens = token_manager.get_all_tokens()
    
    # 按列显示Cookie和Token状态
    col1, col2 = st.columns(2)
    
    accounts_list = list(all_cookies.keys())
    mid_point = len(accounts_list) // 2
    
    with col1:
        st.write("**Cookie状态：**")
        for account_name in accounts_list[:mid_point]:
            st.write(f"**{account_name}**")
            status = cookie_manager.get_cookie_status(account_name)
            
            if status["status"] == "fresh":
                st.success(f"{""} 最后更新: {status["last_updated'].strftime('%Y-%m-%d %H:%M')} (新鲜)")
            elif status["status"] == "warning":
                st.warning(f"{""} 最后更新: {status["last_updated'].strftime('%Y-%m-%d %H:%M')} (建议更新)")
            elif status["status"] == "expired":
                st.error(f"{""} 最后更新: {status["last_updated'].strftime('%Y-%m-%d %H:%M')} (已过期)")
            elif status["status"] == "inactive":
                st.info(f"{""} 未配置Cookie")
            else:
                st.info(f"{""} 未知状态")
        
        st.write("**Token状态：**")
        for account_name in accounts_list[:mid_point]:
            st.write(f"**{account_name}**")
            status = token_manager.get_token_status(account_name)
            
            if status["status"] == "active":
                st.success(f"{""} 已配置 (更新于 {status["last_updated']})")
            elif status["status"] == "inactive":
                st.info(f"{""} 未配置Token")
            else:
                st.info(f"{""} 未知状态")
    
    with col2:
        st.write("**Cookie状态：**")
        for account_name in accounts_list[mid_point:]:
            st.write(f"**{account_name}**")
            status = cookie_manager.get_cookie_status(account_name)
            
            if status["status"] == "fresh":
                st.success(f"{""} 最后更新: {status["last_updated'].strftime('%Y-%m-%d %H:%M')} (新鲜)")
            elif status["status"] == "warning":
                st.warning(f"{""} 最后更新: {status["last_updated'].strftime('%Y-%m-%d %H:%M')} (建议更新)")
            elif status["status"] == "expired":
                st.error(f"{""} 最后更新: {status["last_updated'].strftime('%Y-%m-%d %H:%M')} (已过期)")
            elif status["status"] == "inactive":
                st.info(f"{""} 未配置Cookie")
            else:
                st.info(f"{""} 未知状态")
        
        st.write("**Token状态：**")
        for account_name in accounts_list[mid_point:]:
            st.write(f"**{account_name}**")
            status = token_manager.get_token_status(account_name)
            
            if status["status"] == "active":
                st.success(f"{""} 已配置 (更新于 {status["last_updated']})")
            else:
                st.info(f"{""} 未配置Token")
    


with tab4:
    st.header("数据处理与同步")
    st.info("管理已上传的数据，同步到日历等")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("同步数据到日历"):
            with st.spinner("正在同步数据到日历..."):
                if sync_wechat_to_calendar():
                    st.success("数据同步成功！")
                else:
                    st.error("数据同步失败")
    
    with col2:
        if st.button("查看数据统计"):
            try:
                # 读取CSV文件显示统计信息
                csv_path = load_csv_path()
                df = pd.read_csv(csv_path)
                st.write(f"当前CSV文件包含 {len(df)} 行数据")
                st.write(f"列名: {list(df.columns)}")
                st.dataframe(df.head(5))
            except Exception as e:
                st.error(f"读取数据失败: {str(e)}")

with tab5:
    st.header("智能Cookie获取")
    st.info("使用用户自己获取的Cookie，智能识别账号名称并获取数据")
    
    # 添加Cookie输入区域
    st.subheader("Cookie输入")
    user_cookie = st.text_area(
        "粘贴你的Cookie",
        height=100,
        help="从浏览器开发者工具中复制完整的Cookie字符串",
        placeholder="appmsglist_action_3932945554=card; yyb_muid=09829BC94D52631210D48DDE4C5A62BB; ..."
    )
    
    # 智能识别账号名称的函数
    def extract_account_from_cookie(cookie_string):
        """从Cookie中提取账号信息"""
        try:
            # 微信公众号字段识别
            slave_user_match = re.search(r'slave_user=([^;]+)', cookie_string)
            if slave_user_match:
                slave_user = slave_user_match.group(1)
                if slave_user.startswith('gh_'):
                    return f"公众号-{slave_user}"
            
            bizuin_match = re.search(r'bizuin=(\d+)', cookie_string)
            if bizuin_match:
                bizuin = bizuin_match.group(1)
                return f"公众号-{bizuin}"
            
            wxuin_match = re.search(r'wxuin=(\d+)', cookie_string)
            if wxuin_match:
                wxuin = wxuin_match.group(1)
                return f"公众号-{wxuin}"
            
            # 今日头条字段识别
            tt_webid_match = re.search(r'tt_webid=(\d+)', cookie_string)
            if tt_webid_match:
                tt_webid = tt_webid_match.group(1)
                return f"头条号-{tt_webid}"
            
            toutiao_sso_match = re.search(r'toutiao_sso_user=([^;]+)', cookie_string)
            if toutiao_sso_match:
                toutiao_sso = toutiao_sso_match.group(1)
                return f"头条号-{toutiao_sso}"
            
            uid_tt_match = re.search(r'uid_tt=([^;]+)', cookie_string)
            if uid_tt_match:
                uid_tt = uid_tt_match.group(1)
                return f"头条号-{uid_tt}"
            
            # 其他平台识别
            if 'toutiao' in cookie_string.lower() or 'tt_' in cookie_string:
                return "头条号-未知用户"
            
            if 'weixin' in cookie_string.lower() or 'wx_' in cookie_string:
                return "公众号-未知用户"
            
            return "未知平台"
        except Exception as e:
            st.error(f"解析Cookie失败: {e}")
            return "解析失败"
    
    # 显示识别结果
    if user_cookie.strip():
        detected_account = extract_account_from_cookie(user_cookie)
        st.success(f"识别到的账号: {detected_account}")
        
        # 显示Cookie解析信息
        with st.expander(f"Cookie解析详情"):
            try:
                # 提取微信公众号关键字段
                slave_user_match = re.search(r'slave_user=([^;]+)', user_cookie)
                bizuin_match = re.search(r'bizuin=(\d+)', user_cookie)
                wxuin_match = re.search(r'wxuin=(\d+)', user_cookie)
                
                # 提取今日头条关键字段
                tt_webid_match = re.search(r'tt_webid=(\d+)', user_cookie)
                toutiao_sso_match = re.search(r'toutiao_sso_user=([^;]+)', user_cookie)
                uid_tt_match = re.search(r'uid_tt=([^;]+)', user_cookie)
                
                st.write("**微信公众号字段:**")
                if slave_user_match:
                    st.write(f"- slave_user: {slave_user_match.group(1)}")
                if bizuin_match:
                    st.write(f"- bizuin: {bizuin_match.group(1)}")
                if wxuin_match:
                    st.write(f"- wxuin: {wxuin_match.group(1)}")
                
                st.write("**今日头条字段:**")
                if tt_webid_match:
                    st.write(f"- tt_webid: {tt_webid_match.group(1)}")
                if toutiao_sso_match:
                    st.write(f"- toutiao_sso_user: {toutiao_sso_match.group(1)}")
                if uid_tt_match:
                    st.write(f"- uid_tt: {uid_tt_match.group(1)}")
                
                # 显示Cookie长度和格式
                st.write(f"**Cookie信息:**")
                st.write(f"- 长度: {len(user_cookie)} 字符")
                st.write(f"- 包含分号数量: {user_cookie.count(';')} 个")
                
                # 平台识别
                platform = "未知"
                if 'toutiao' in user_cookie.lower() or 'tt_' in user_cookie:
                    platform = "今日头条"
                elif 'weixin' in user_cookie.lower() or 'wx_' in user_cookie:
                    platform = "微信公众号"
                st.write(f"- 识别平台: {platform}")
                
            except Exception as e:
                st.error(f"解析Cookie详情失败: {e}")
    
    # 日期选择
    st.subheader("日期范围选择")
    st.info(f"开始日期默认为2025年6月9日（项目运营开始时间），结束日期为当前日期")
    col1, col2 = st.columns(2)
    
    with col1:
        begin_date = st.date_input(
            "开始日期",
            value=datetime(2025, 6, 9),
            help="选择开始日期"
        )
        begin_date_str = begin_date.strftime("%Y%m%d")
    
    with col2:
        end_date = st.date_input(
            "结束日期",
            value=datetime.now(),
            help="选择结束日期"
        )
        end_date_str = end_date.strftime("%Y%m%d")
    
    # 显示日期范围
    days_diff = (end_date - begin_date).days
    if days_diff >= 0:
        st.info(f"将获取 {days_diff + 1} 天的数据")
    else:
        st.error(f"{""} 开始日期不能晚于结束日期！")
    
    # 获取数据按钮
    if st.button(f"开始获取数据", type="primary"):
        if not user_cookie.strip():
            st.error("请先输入Cookie")
        elif days_diff < 0:
            st.error("请选择正确的日期范围")
        else:
            with st.spinner("正在获取数据..."):
                try:
                    # 根据平台类型调用不同的数据获取函数
                    if detected_account.startswith("头条号"):
                        st.info(f"检测到今日头条Cookie，正在获取头条号数据...")
                        
                        # 获取今日头条数据
                        df = fetch_article_by_site(user_cookie)
                        if df is not None and not df.empty:
                            # 保存到CSV
                            update_toutiao_publish_history(user_cookie)
                            st.success(f"{""} {detected_account} 数据获取成功！")
                            
                            # 显示获取到的数据
                            st.subheader(f"获取到的数据预览")
                            st.write(f"{""} 成功获取到 {len(df)} 行数据")
                            
                            # 显示数据统计
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("总行数", len(df))
                            with col2:
                                st.metric("总列数", len(df.columns))
                            with col3:
                                if '阅读量' in df.columns:
                                    total_reads = df['阅读量'].sum() if df['阅读量'].dtype in ['int64', 'float64'] else 0
                                    st.metric("总阅读量", f"{total_reads:,}")
                            
                            # 显示数据预览
                            st.write("**数据预览：**")
                            st.dataframe(df.head(10), use_container_width=True)
                            
                            # 显示保存位置
                            st.info("📁 数据已保存到: workspace/data/publish_history_for_calendar.csv")
                            
                        else:
                            st.warning(f"{""} {detected_account} 数据获取完成，但没有获取到新数据")
                    
                    elif detected_account.startswith("公众号"):
                        st.info(f"检测到微信公众号Cookie，正在获取公众号数据...")
                        
                        # 调用微信公众号数据获取函数
                        result = update_wechat_data_from_excel(
                            begin_date=begin_date_str,
                            end_date=end_date_str,
                            token="",  # 不需要token
                            cookies=user_cookie,
                            account_name=detected_account
                        )
                        
                        if result:
                            st.success(f"{""} {detected_account} 数据获取成功！")
                            
                            # 显示获取到的数据
                            st.subheader(f"获取到的数据预览")
                            
                            # 尝试读取生成的Excel文件
                            if os.path.exists("result.xls"):
                                df = pd.read_excel("result.xls")
                                st.write(f"{""} 成功获取到 {len(df)} 行数据")
                                
                                # 显示数据统计
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("总行数", len(df))
                                with col2:
                                    st.metric("总列数", len(df.columns))
                                with col3:
                                    if '总阅读人数' in df.columns:
                                        total_reads = df['总阅读人数'].sum() if df['总阅读人数'].dtype in ['int64', 'float64'] else 0
                                        st.metric("总阅读量", f"{total_reads:,}")
                                
                                # 显示数据预览
                                st.write("**数据预览：**")
                                st.dataframe(df.head(10), use_container_width=True)
                                
                                # 提供下载链接
                                with open("result.xls", "rb") as file:
                                    st.download_button(
                                        label=f"下载Excel文件",
                                        data=file.read(),
                                        file_name=f"{detected_account}_{begin_date_str}_{end_date_str}.xls",
                                        mime="application/vnd.ms-excel"
                                    )
                            else:
                                st.warning("未找到生成的Excel文件，可能数据获取失败")
                                
                        else:
                            st.warning(f"{""} {detected_account} 数据获取完成，但可能没有新数据")
                    
                    else:
                        st.error(f"{""} 不支持的平台类型: {detected_account}")
                        st.info("目前支持：微信公众号、今日头条")
                        
                except Exception as e:
                    st.error(f"获取数据失败: {str(e)}")
                    st.info("请检查Cookie是否有效或网络连接是否正常")
    
    # 使用说明
    st.subheader("📖 使用说明")
    with st.expander("如何获取Cookie"):
        st.markdown("""
        ### 步骤1: 登录微信公众平台
        1. 打开浏览器，访问 https://mp.weixin.qq.com/
        2. 使用你的微信账号登录
        
        ### 步骤2: 获取Cookie
        1. **打开开发者工具**：
           - Chrome/Edge: 按 `F12` 或右键选择"检查"
           - Firefox: 按 `F12` 或右键选择"检查元素"
        
        2. **切换到Network标签页**
        
        3. **刷新页面**或进行任何操作
        
        4. **找到任意请求**，右键选择"Copy > Copy as cURL (bash)"
        
        5. **从cURL命令中提取Cookie**：
           ```bash
           curl 'https://mp.weixin.qq.com/...' \\
             -H 'Cookie: 这里就是你要的Cookie字符串'
           ```
        
        6. **复制Cookie字符串**到上面的输入框
        
        ### 步骤3: 智能识别
        - 系统会自动从Cookie中提取账号信息
        - **微信公众号**: 识别 `slave_user`、`bizuin`、`wxuin` 等字段
        - **今日头条**: 识别 `tt_webid`、`toutiao_sso_user`、`uid_tt` 等字段
        - 自动生成账号名称格式：`公众号-{ID}` 或 `头条号-{ID}`
        
        ### 步骤4: 获取数据
        - 选择日期范围（开始日期默认为2025年6月9日，即项目运营开始时间）
        - 点击"开始获取数据"按钮
        - 系统会根据平台类型自动调用相应的数据获取函数
        - **微信公众号**: 获取文章数据并生成Excel文件
        - **今日头条**: 获取文章数据并保存到CSV文件
        """)
    
    # 注意事项
    st.subheader(f"{""} 注意事项")
    st.info("""
    - **多平台支持**: 目前支持微信公众号和今日头条两个平台
    - **Cookie有效期**: Cookie通常有24-48小时的有效期，过期后需要重新获取
    - **账号权限**: 确保Cookie对应的账号有权限访问文章数据
    - **网络环境**: 建议在稳定的网络环境下使用
    - **数据安全**: 请勿在公共网络环境下使用，保护你的账号安全
    - **数据保存**: 今日头条数据保存到CSV，微信公众号数据生成Excel文件
    """)