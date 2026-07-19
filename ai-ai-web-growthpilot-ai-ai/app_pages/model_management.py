import pandas as pd
import streamlit as st

from config import MODEL_PROFILES, get_model_catalog
from services.llm_client import load_active_model_config
from services.ui import render_page_intro


render_page_intro(
    "MODEL CONTROL · 将模型连接与业务 Agent 解耦",
    "模型管理<br><span>选择适合当前任务的 AI 引擎</span>",
    "DeepSeek 是默认生产模型。OpenAI、通义千问和其他 OpenAI Compatible 服务可通过环境变量或 Secrets 配置后接入。",
)
st.space("medium")

current = load_active_model_config()
with st.container(horizontal=True):
    st.metric("当前模型", current.label, border=True)
    st.metric("当前版本", current.model or "待配置", border=True)
    st.metric("连接状态", "已就绪" if current.is_configured else "待配置", border=True)

with st.container(border=True):
    st.markdown("### :material/tune: 选择工作模型")
    model_ids = list(MODEL_PROFILES)
    selected_id = st.selectbox(
        "模型",
        model_ids,
        index=model_ids.index(st.session_state.active_model_id) if st.session_state.active_model_id in model_ids else 0,
        format_func=lambda model_id: MODEL_PROFILES[model_id].label,
    )
    if selected_id == "custom":
        custom_base_url = st.text_input("自定义 Base URL", value=st.session_state.model_overrides.get("base_url", ""), placeholder="例如：https://api.example.com/v1")
        custom_model = st.text_input("自定义模型名称", value=st.session_state.model_overrides.get("model", ""), placeholder="例如：your-chat-model")
    else:
        custom_base_url = ""
        custom_model = ""
    if st.button("应用当前模型", icon=":material/check_circle:", type="primary"):
        st.session_state.active_model_id = selected_id
        if selected_id == "custom":
            st.session_state.model_overrides = {"base_url": custom_base_url, "model": custom_model}
        st.rerun()
    st.caption("API Key 不在页面输入。请使用部署平台环境变量或 `.streamlit/secrets.toml` 配置，避免将密钥暴露在浏览器中。")

with st.container(border=True):
    st.markdown("### :material/dns: 模型目录")
    catalog = pd.DataFrame(get_model_catalog())
    st.dataframe(catalog, hide_index=True)
    st.caption("Claude 已注册为专属 Adapter 预留；在接入 Anthropic SDK 前，请使用 DeepSeek、OpenAI、通义千问兼容模式或自定义兼容模型执行 Agent。")
