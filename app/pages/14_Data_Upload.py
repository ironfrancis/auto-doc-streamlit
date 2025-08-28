from app.utils.wechat_data_processor import (
    load_csv_path, 
    append_record_to_csv, 
    update_wechat_data_from_excel,
    sync_wechat_to_calendar
)
import streamlit as st
import pandas as pd
import os
from app.cookie_manager import CookieManager
from app.token_manager import TokenManager

st.title("数据上传与管理")

tab1, tab2, tab3, tab4 = st.tabs(["Excel文件上传", "微信公众号数据获取", "Cookie管理", "数据处理"])

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
    st.info(f"🕐 当前时间：{current_time.strftime('%Y年%m月%d日 %H:%M:%S')}")
    
    # 显示默认设置信息
    st.success("📅 默认设置：开始日期为2025年6月9日，结束日期为当前日期")
    
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
                st.error("❌ 开始日期不能晚于结束日期！")
            elif days_diff > 365:
                st.warning("⚠️ 日期范围超过一年，可能需要较长时间获取")
            else:
                st.success(f"✅ 参数有效，将获取 {days_diff + 1} 天的数据")
                
        except ValueError:
            st.error("❌ 日期格式错误")
    else:
        st.warning("⚠️ 请填写完整的参数信息")
    
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
            cookie_status = f"✅ 新鲜 (更新于 {cookie_info['last_updated'].strftime('%H:%M')})"
        elif cookie_info["status"] == "warning":
            cookie_status = f"⚠️ 建议更新 (更新于 {cookie_info['last_updated'].strftime('%H:%M')})"
        elif cookie_info["status"] == "expired":
            cookie_status = f"❌ 已过期 (更新于 {cookie_info['last_updated'].strftime('%H:%M')})"
        elif cookie_info["status"] == "inactive":
            cookie_status = "🔄 未配置"
        else:
            cookie_status = "🔄 未知状态"
    
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
                    with st.expander("🔍 查看传递的参数"):
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
                    st.subheader("📊 获取到的数据预览")
                    
                    # 尝试读取生成的Excel文件
                    try:
                        if os.path.exists("result.xls"):
                            df = pd.read_excel("result.xls")
                            st.write(f"✅ 成功获取到 {len(df)} 行数据")
                            
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
                                    label="📥 下载Excel文件",
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
                st.success(f"✅ 最后更新: {status['last_updated'].strftime('%Y-%m-%d %H:%M')} (新鲜)")
            elif status["status"] == "warning":
                st.warning(f"⚠️ 最后更新: {status['last_updated'].strftime('%Y-%m-%d %H:%M')} (建议更新)")
            elif status["status"] == "expired":
                st.error(f"❌ 最后更新: {status['last_updated'].strftime('%Y-%m-%d %H:%M')} (已过期)")
            elif status["status"] == "inactive":
                st.info("🔄 未配置Cookie")
            else:
                st.info("🔄 未知状态")
        
        st.write("**Token状态：**")
        for account_name in accounts_list[:mid_point]:
            st.write(f"**{account_name}**")
            status = token_manager.get_token_status(account_name)
            
            if status["status"] == "active":
                st.success(f"✅ 已配置 (更新于 {status['last_updated']})")
            elif status["status"] == "inactive":
                st.info("🔄 未配置Token")
            else:
                st.info("🔄 未知状态")
    
    with col2:
        st.write("**Cookie状态：**")
        for account_name in accounts_list[mid_point:]:
            st.write(f"**{account_name}**")
            status = cookie_manager.get_cookie_status(account_name)
            
            if status["status"] == "fresh":
                st.success(f"✅ 最后更新: {status['last_updated'].strftime('%Y-%m-%d %H:%M')} (新鲜)")
            elif status["status"] == "warning":
                st.warning(f"⚠️ 最后更新: {status['last_updated'].strftime('%Y-%m-%d %H:%M')} (建议更新)")
            elif status["status"] == "expired":
                st.error(f"❌ 最后更新: {status['last_updated'].strftime('%Y-%m-%d %H:%M')} (已过期)")
            elif status["status"] == "inactive":
                st.info("🔄 未配置Cookie")
            else:
                st.info("🔄 未知状态")
        
        st.write("**Token状态：**")
        for account_name in accounts_list[mid_point:]:
            st.write(f"**{account_name}**")
            status = token_manager.get_token_status(account_name)
            
            if status["status"] == "active":
                st.success(f"✅ 已配置 (更新于 {status['last_updated']})")
            else:
                st.info("🔄 未配置Token")
    


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