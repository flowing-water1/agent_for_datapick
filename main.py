import json

import pandas as pd
import streamlit as st
import os
from utils import dataframe_agent

import hmac

import hmac
import streamlit as st


def check_password():
    def login_form():
        with st.form("Credentials"):
            col0, col1, col2 = st.columns([0.2, 0.4, 2], vertical_alignment="top")
            with col0:
                st.write(" ")
            with col1:
                st.markdown(" ")
            with col2:
                st.markdown("## 📈Agent_For_DataPick")
            st.text_input("账号名称", key="username")
            st.text_input("账号密码", type="password", key="password")
            # 将按钮靠右放置
            cols = st.columns([4, 1])
            cols[1].form_submit_button("登录", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 账号不存在或者密码不正确")
    return False


if check_password():
    st.title("💡 泛用表格提取工具")

    with st.sidebar:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        openai_api_base = st.secrets["OPENAI_API_BASE"]

        st.markdown("## OPENAI_API_KEY 和 OPENAI_API_BASE已经在后端配置好了，直接用即可")

        if st.button("登出"):
            # 清除会话状态
            del st.session_state["password_correct"]
            st.rerun()  # 重新运行应用，回到登录页面

    data = st.file_uploader("上传你的数据文件（xlsx或csv格式）：", type=['xlsx', 'csv'])
    if data:
        # 获取文件扩展名
        file_extension = data.name.split('.')[-1]

        # 根据扩展名选择读取方式
        if file_extension == 'xlsx':
            st.session_state["df"] = pd.read_excel(data)
        elif file_extension == 'csv':
            st.session_state["df"] = pd.read_csv(data)
        else:
            st.error("不支持的文件格式，请上传xlsx或csv文件。")

        with st.expander("原始数据"):
            st.dataframe(st.session_state["df"])


    model_name = st.selectbox(
            "请选择模型：(优先前面两个应该就能解决问题了)",
            ("gpt-3.5-turbo", "gpt-4-1106-preview","gpt-4","gpt-4o","gpt-4o-2024-05-13"), key="2"
        )
    query = st.text_area("请输入你关于以上表格想要提取的内容：")
    button = st.button("提取数据", key="1")

    st.divider()

    if button and not openai_api_key:
        st.toast("请先输入OpenAI API密钥", icon="🚨")

    if button and "df" not in st.session_state:

        st.toast("请先上传excel数据文件",icon="🚨")


    if button and openai_api_key and "df" in st.session_state:
        with st.spinner("AI正在思考中，请稍等..."):
            response, read = dataframe_agent(openai_api_key, openai_api_base,model_name, st.session_state["df"], query)
            st.write(response)
            st.divider()
            st.write("思考过程：")
            st.json(read, expanded=False)
            st.divider()

            # 检查 read 中的每个元素
            if isinstance(read, list):
                for i, element in enumerate(read):

                    if isinstance(element, tuple) and len(element) > 0:
                        log_content = element[0].log if hasattr(element[0], 'log') else None
                        remaining_content = element[1] if len(element) > 1 else None

                        if log_content:
                            st.write(f"思考过程{i + 1}：")
                            st.write(log_content)

                        # 确保 remaining_content 是有效的类型
                        if remaining_content is not None:
                            # 检查是否为 Pandas Index 类型
                            if isinstance(remaining_content, pd.Index):
                                st.write(remaining_content.tolist())  # 转换为列表形式展示
                                st.divider()
                            else:
                                st.write(remaining_content)
                                st.divider()
                        else:
                            st.write(f"元素 {i} 中没有后续内容。")
            else:
                st.write("read 不是有效的列表格式。")

            response_dict = json.loads(response)
            if "answer" in response_dict:
                st.write(response_dict["answer"])
            if "table" in response_dict:
                st.table(pd.DataFrame(response_dict["table"]["data"],
                                      columns=response_dict["table"]["columns"]))
else:
    st.stop()