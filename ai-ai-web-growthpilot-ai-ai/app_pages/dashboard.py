import streamlit as st

from services.llm_client import load_active_model_config
from services.portfolio_showcase import AGENT_PIPELINE, BEIDAHU_SHOWCASE, OPERATION_TEMPLATES
from services.project_store import list_projects, list_tasks
from services.ui import (
    render_agent_pipeline,
    render_export_actions,
    render_module_card,
    render_page_intro,
)
from services.workspace import get_workspace_metrics, load_showcase_brief


def open_showcase() -> None:
    load_showcase_brief(BEIDAHU_SHOWCASE.case_id, BEIDAHU_SHOWCASE.brief)
    st.toast("完整案例已展开，业务简报也已载入工作台。", icon=":material/check_circle:")


def close_showcase() -> None:
    st.session_state.showcase_open = False


def open_template(template_name: str) -> None:
    st.session_state.active_template_id = template_name


render_page_intro(
    "GROWTHPILOT AI · AI 增长运营助手",
    "GrowthPilot AI<br><span>让AI成为你的增长运营团队</span>",
    "从需求分析、增长策略到内容生产与报告交付，一份业务输入完成完整运营工作流。",
)

st.space("medium")
st.markdown("<div class='gp-section-kicker'>快速开始</div>", unsafe_allow_html=True)
quick_actions = [
    ("市场分析", "query_stats", "app_pages/growth_analysis.py"),
    ("内容生成", "auto_stories", "app_pages/content_factory.py"),
    ("数据分析", "analytics", "app_pages/data_analysis.py"),
    ("营销方案", "campaign", "app_pages/growth_analysis.py"),
]
for column, (label, icon, page_path) in zip(st.columns(4, gap="medium"), quick_actions):
    with column:
        if st.button(label, icon=f":material/{icon}:", key=f"quick_{label}", width="stretch"):
            if label == "营销方案":
                st.session_state.active_template_id = "活动策划"
            st.switch_page(page_path)

st.space("medium")
with st.container(border=True):
    case_left, case_right = st.columns([1.55, 0.45], vertical_alignment="center", gap="large")
    with case_left:
        st.markdown("<span class='gp-demo-tag'>求职展示案例 · 30 秒看懂产品</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='gp-case-title'>{BEIDAHU_SHOWCASE.name}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='gp-case-copy'>{BEIDAHU_SHOWCASE.summary}</div>", unsafe_allow_html=True)
        st.caption("内置案例用于稳定展示产品价值；点击真实生成入口时仍调用当前配置的 DeepSeek 模型。")
    with case_right:
        st.button(
            "查看完整案例",
            icon=":material/play_circle:",
            type="primary",
            width="stretch",
            on_click=open_showcase,
        )

if st.session_state.showcase_open:
    st.space("medium")
    with st.container(border=True):
        title_left, title_right = st.columns([4, 1], vertical_alignment="center")
        with title_left:
            st.markdown(f"### :material/ac_unit: {BEIDAHU_SHOWCASE.name}")
            st.caption("已载入案例业务简报，可直接进入增长分析让 DeepSeek 重新生成。")
        with title_right:
            st.button("收起案例", icon=":material/expand_less:", on_click=close_showcase, width="stretch")

        flow_col, result_col = st.columns([0.78, 1.22], gap="large")
        with flow_col:
            st.markdown("#### :material/account_tree: Agent 执行流程")
            render_agent_pipeline(AGENT_PIPELINE, completed=True)
        with result_col:
            demo_tabs = st.tabs(["用户分析", "市场分析", "内容运营", "营销报告"])
            with demo_tabs[0]:
                st.markdown(BEIDAHU_SHOWCASE.user_analysis)
            with demo_tabs[1]:
                st.markdown(BEIDAHU_SHOWCASE.market_analysis)
            with demo_tabs[2]:
                st.markdown(BEIDAHU_SHOWCASE.content_operations)
            with demo_tabs[3]:
                st.markdown(BEIDAHU_SHOWCASE.marketing_report)

        with st.container(horizontal=True):
            if st.button("使用 DeepSeek 重新生成", icon=":material/auto_awesome:", type="primary"):
                st.switch_page("app_pages/growth_analysis.py")
            st.download_button(
                "下载 Markdown 报告",
                BEIDAHU_SHOWCASE.full_markdown,
                file_name="北大湖滑雪民宿增长营销方案.md",
                mime="text/markdown",
                icon=":material/download:",
            )
        render_export_actions(
            BEIDAHU_SHOWCASE.full_markdown,
            report_title=BEIDAHU_SHOWCASE.name,
        )

metrics = get_workspace_metrics()
projects = list_projects()
active_project_id = st.session_state.active_project_id
active_tasks = list_tasks(active_project_id) if active_project_id else []
completed_tasks = sum(task["status"] == "已完成" for task in active_tasks)
model = load_active_model_config()
st.space("medium")
with st.container(horizontal=True):
    st.metric("今日任务", metrics["today_generation_count"], border=True, chart_data=[0, metrics["today_generation_count"]])
    st.metric("内容生成数量", metrics["content_count"], border=True, chart_data=[0, metrics["content_count"]])
    st.metric("增长机会", metrics["growth_suggestion_count"], border=True, chart_data=[0, metrics["growth_suggestion_count"]])
    st.metric("项目任务", f"{completed_tasks}/{len(active_tasks)}", border=True)

st.space("medium")
state_col, project_col, history_col = st.columns([1.12, 1, 1], gap="medium")
with state_col:
    with st.container(border=True):
        st.markdown("#### :material/neurology: AI 工作状态")
        st.markdown(f"<span class='gp-status-dot'></span> **{metrics['task_status']}**", unsafe_allow_html=True)
        st.caption(f"最近活动：{st.session_state.last_activity}")
        st.caption(f"当前模型：{model.label} · {model.model or '待配置'}")
with project_col:
    with st.container(border=True):
        st.markdown("#### :material/folder_managed: 项目数据")
        st.metric("已保存项目", len(projects), border=False)
        st.caption(f"当前项目：{metrics['active_project_name']}")
        st.caption("在项目管理中创建项目、分配任务并归档 Agent 输出。")
with history_col:
    with st.container(border=True):
        st.markdown("#### :material/history: 历史任务")
        st.metric("本次会话记录", len(st.session_state.history), border=False)
        st.caption("任务结果可导出 PDF、Word、PPT 和 Excel。")

st.space("large")
st.markdown("<div class='gp-section-kicker'>AGENT 执行流程</div>", unsafe_allow_html=True)
st.subheader("一份需求，由多个专业 Agent 协同完成", anchor=False)
st.caption("从用户需求到可下载报告，每一步都有明确职责和业务产出。")
pipeline_left, pipeline_right = st.columns([1, 1], gap="large")
with pipeline_left:
    render_agent_pipeline(AGENT_PIPELINE[:3])
with pipeline_right:
    render_agent_pipeline(AGENT_PIPELINE[3:], start_index=3)

st.space("large")
st.markdown("<div class='gp-section-kicker'>核心能力</div>", unsafe_allow_html=True)
module_cards = [
    ("query_stats", "AI 市场分析", "从产品定位、竞争环境到增长切口，建立可验证的策略假设。"),
    ("auto_stories", "AI 内容生成", "用渠道化工作流生产小红书、抖音和营销活动内容。"),
    ("trending_up", "AI 用户增长", "把获客、转化、留存和裂变拆解成可执行动作。"),
    ("fact_check", "AI 运营复盘", "用实际生成记录沉淀项目过程与下一轮优化线索。"),
]
for column, (icon, title, copy) in zip(st.columns(4, gap="medium"), module_cards):
    with column:
        render_module_card(icon, title, copy)

st.space("large")
st.markdown("<div class='gp-section-kicker'>模板中心</div>", unsafe_allow_html=True)
st.subheader("从成熟运营框架开始，而不是从空白输入开始", anchor=False)
for column, template in zip(st.columns(4, gap="medium"), OPERATION_TEMPLATES.values()):
    with column:
        with st.container(border=True, height="stretch"):
            st.markdown(f"#### :material/{template.icon}: {template.name}")
            st.caption(template.description)
            if st.button("使用模板", key=f"dashboard_template_{template.name}", width="stretch"):
                open_template(template.name)
                st.switch_page("app_pages/content_factory.py")

st.space("large")
with st.container(border=True):
    st.markdown("#### :material/history: 最近项目")
    history = st.session_state.history[:4]
    if history:
        for record in history:
            st.markdown(f"**{record['task_type']}** · {record['product_name']}")
            st.caption(f"{record['created_at']} · {record['preview']}")
    else:
        st.caption("还没有项目记录。完成一次增长分析或内容生成后，会在这里展示真实任务结果。")
