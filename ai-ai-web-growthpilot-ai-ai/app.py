"""GrowthPilot AI 的多页面增长运营工作台入口。"""

import streamlit as st

from services.llm_client import load_active_model_config
from services.ui import apply_workspace_styles
from services.workspace import initialise_workspace_state


st.set_page_config(
    page_title="GrowthPilot AI · AI增长运营智能体",
    page_icon=":material/rocket_launch:",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialise_workspace_state()
apply_workspace_styles()

pages = {
    "GrowthPilot AI": [
        st.Page(
            "app_pages/dashboard.py",
            title="工作台",
            icon=":material/dashboard:",
            default=True,
        ),
    ],
    "专业 Agent": [
        st.Page("app_pages/growth_analysis.py", title="增长分析", icon=":material/query_stats:"),
        st.Page("app_pages/user_insights.py", title="用户洞察", icon=":material/groups:"),
        st.Page("app_pages/content_factory.py", title="内容中心", icon=":material/auto_awesome:"),
        st.Page("app_pages/video_center.py", title="视频创作", icon=":material/videocam:"),
        st.Page("app_pages/xiaohongshu_assistant.py", title="小红书助手", icon=":material/auto_stories:"),
        st.Page("app_pages/data_analysis.py", title="数据分析", icon=":material/analytics:"),
        st.Page("app_pages/operations_review.py", title="运营复盘", icon=":material/fact_check:"),
    ],
    "项目与系统": [
        st.Page("app_pages/project_management.py", title="项目管理", icon=":material/folder_managed:"),
        st.Page("app_pages/history_projects.py", title="历史记录", icon=":material/history:"),
        st.Page("app_pages/model_management.py", title="模型管理", icon=":material/tune:"),
    ],
}

page = st.navigation(pages, position="sidebar", expanded=True)

config = load_active_model_config()
with st.sidebar:
    st.markdown("### :material/rocket_launch: GrowthPilot AI")
    st.caption("AI 增长运营助手 · 求职展示版 V1.0")
    if config.is_configured:
        st.success(f"{config.label} 已连接 · {config.model}", icon=":material/cloud_done:")
    else:
        st.warning("当前模型尚未完成可用配置", icon=":material/key_off:")
    st.caption(f"当前项目：{st.session_state.active_project_name}")

page.run()
