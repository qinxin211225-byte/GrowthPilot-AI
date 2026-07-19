"""GrowthPilot 工作台的共享 Streamlit 视图与交互封装。"""

from __future__ import annotations

from html import escape
from typing import Callable

import streamlit as st

from services.generator import (
    CREATIVE_WORKS,
    SPECIALIST_AGENTS,
    SECTION_TITLES,
    WORKFLOW_STEPS,
    AgentResult,
    CreativeResult,
    GrowthBrief,
    InsightResult,
    SpecialistResult,
    generate_creative_work,
    generate_growth_plan,
    generate_specialist_agent,
    generate_user_insights,
)
from services.exporters import (
    build_excel_report,
    build_pdf_report,
    build_ppt_report,
    build_word_report,
    export_formats_available,
)
from services.llm_client import CONNECTION_ERROR_MESSAGE
from services.media_clients import MediaGenerationJob


OutputResult = AgentResult | CreativeResult | InsightResult | SpecialistResult


def apply_workspace_styles() -> None:
    """仅因产品明确要求而注入的 SaaS 级视觉细节。"""
    st.markdown(
        """
        <style>
        .stApp {
          background:
            radial-gradient(circle at 94% 2%, rgba(142, 104, 255, .18), transparent 25rem),
            radial-gradient(circle at 0% 20%, rgba(64, 180, 255, .15), transparent 26rem),
            linear-gradient(180deg, #fbfcff 0%, #f7f9ff 52%, #f9fbff 100%);
        }
        [data-testid="stHeader"] { background: rgba(251,252,255,.82); backdrop-filter: blur(14px); }
        [data-testid="stToolbar"] { display: none; }
        [data-testid="stSidebar"] { background: rgba(255,255,255,.88); border-right: 1px solid #e5e9fa; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] { padding-top: 1rem; }
        [data-testid="stSidebar"] a { border-radius: 12px; transition: background .18s ease, transform .18s ease; }
        [data-testid="stSidebar"] a:hover { background: #f1efff; transform: translateX(2px); }
        .block-container { max-width: 1380px; padding-top: 2.25rem; padding-bottom: 4.5rem; animation: page-enter .42s ease both; }
        @keyframes page-enter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes soft-float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
        @keyframes glow-pulse { 0%,100% { box-shadow: 0 0 0 rgba(98,87,216,0); } 50% { box-shadow: 0 0 0 8px rgba(98,87,216,.06); } }
        .gp-hero {
          position: relative; overflow: hidden; padding: clamp(2rem, 4.5vw, 4.35rem);
          border: 1px solid rgba(114,99,235,.18); border-radius: 30px;
          background: linear-gradient(118deg, rgba(255,255,255,.98), rgba(245,243,255,.96));
          box-shadow: 0 24px 70px rgba(68,68,144,.12);
        }
        .gp-hero:after { content:""; position:absolute; width:360px; height:360px; right:-120px; top:-150px; border-radius:50%; background:radial-gradient(circle, rgba(116,91,255,.26), rgba(91,180,255,.04) 64%, transparent 66%); animation: soft-float 6s ease-in-out infinite; }
        .gp-kicker { color:#6659d9; letter-spacing:.14em; font-size:.74rem; font-weight:800; }
        .gp-title { max-width:800px; margin:.55rem 0 .8rem; color:#18203c; font-weight:800; letter-spacing:-.065em; line-height:1.03; font-size:clamp(2.45rem,5vw,5rem); }
        .gp-title span { background:linear-gradient(105deg,#2e4aaf,#7657dc 55%,#2f9be1); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
        .gp-copy { max-width:650px; color:#5a6682; font-size:1.07rem; line-height:1.8; }
        .gp-section-kicker { color:#7668dc; font-weight:800; letter-spacing:.12em; font-size:.73rem; margin-bottom:.35rem; }
        .gp-flow { display:flex; flex-wrap:wrap; align-items:center; gap:.5rem; margin-top:.9rem; }
        .gp-flow-step { padding:.48rem .72rem; border-radius:999px; border:1px solid #e3e7f7; background:rgba(255,255,255,.78); color:#4d5b7d; font-size:.79rem; animation: glow-pulse 2.8s ease-in-out infinite; }
        .gp-flow-arrow { color:#8a82d8; font-size:.9rem; }
        .gp-module-icon { color:#6756e7; font-size:1.6rem; line-height:1; }
        .gp-module-title { color:#202943; font-weight:800; margin-top:.7rem; font-size:1.02rem; }
        .gp-module-copy { color:#68748f; font-size:.88rem; line-height:1.65; margin-top:.35rem; }
        .gp-muted { color:#75819a; font-size:.8rem; }
        .gp-surface { background:rgba(255,255,255,.72); border:1px solid rgba(229,233,247,.92); border-radius:18px; padding:1rem 1.1rem; backdrop-filter:blur(16px); }
        .gp-status-dot { width:8px; height:8px; display:inline-block; margin-right:6px; border-radius:99px; background:#22c55e; box-shadow:0 0 0 5px rgba(34,197,94,.10); animation:glow-pulse 2.1s ease-in-out infinite; }
        .gp-reveal { animation:page-enter .45s ease both; }
        .gp-agent-pipeline { display:grid; gap:.45rem; margin-top:.9rem; }
        .gp-agent-step { display:grid; grid-template-columns:2.15rem 1fr auto; align-items:center; gap:.8rem; padding:.72rem .85rem; border:1px solid #e4e8f5; border-radius:15px; background:rgba(255,255,255,.78); transition:transform .18s ease,border-color .18s ease; }
        .gp-agent-step:hover { transform:translateX(3px); border-color:rgba(98,87,216,.34); }
        .gp-agent-step.is-active { border-color:#7668dc; background:linear-gradient(105deg,#f7f5ff,#eff7ff); animation:glow-pulse 2s ease-in-out infinite; }
        .gp-agent-index { display:grid; place-items:center; width:2.05rem; height:2.05rem; border-radius:11px; color:#5d58d6; background:#f0efff; font-size:.78rem; font-weight:800; }
        .gp-agent-name { color:#202943; font-size:.92rem; font-weight:800; }
        .gp-agent-description { margin-top:.14rem; color:#73809b; font-size:.78rem; }
        .gp-agent-state { color:#16845b; background:#e9f8f1; border-radius:999px; padding:.24rem .55rem; font-size:.7rem; font-weight:800; white-space:nowrap; }
        .gp-agent-arrow { color:#9a91dd; padding-left:.72rem; height:.36rem; line-height:.36rem; }
        .gp-demo-tag { display:inline-flex; align-items:center; gap:.35rem; padding:.3rem .65rem; border-radius:999px; background:#eef0ff; color:#5d58d6; font-size:.72rem; font-weight:800; }
        .gp-case-title { color:#202943; font-size:1.2rem; font-weight:800; margin:.6rem 0 .35rem; }
        .gp-case-copy { color:#68748f; line-height:1.7; font-size:.9rem; }
        div[data-testid="stVerticalBlockBorderWrapper"] { background:rgba(255,255,255,.84); border:1px solid #e4e8f5; border-radius:20px; box-shadow:0 12px 34px rgba(52,65,125,.055); transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease; }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover { transform:translateY(-2px); border-color:rgba(106,87,226,.31); box-shadow:0 18px 42px rgba(66,61,145,.10); }
        [data-testid="stMetric"] { background:rgba(255,255,255,.68); border-radius:16px; }
        div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button { border-radius:13px; font-weight:700; transition:transform .18s ease, box-shadow .18s ease; }
        div.stButton > button:hover, div.stDownloadButton > button:hover, div.stFormSubmitButton > button:hover { transform:translateY(-1px); }
        div.stButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"] { border:0; color:white; background:linear-gradient(105deg,#5d58e9,#7b56dc 52%,#3d91e8); box-shadow:0 9px 22px rgba(98,82,223,.25); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_intro(kicker: str, title: str, copy: str, *, accent: str | None = None) -> None:
    # 页面既可由 app.py 的导航加载，也可在开发/测试环境单独打开。
    # 在这里兜底初始化，避免任一业务页直接读取会话状态时出现红色报错。
    from services.workspace import initialise_workspace_state

    initialise_workspace_state()
    title_html = title if not accent else title.replace(accent, f"<span>{accent}</span>")
    st.markdown(
        f"""
        <section class="gp-hero">
          <div class="gp-kicker">{kicker}</div>
          <div class="gp-title">{title_html}</div>
          <div class="gp-copy">{copy}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_workflow(active_step: int | None = None) -> None:
    parts: list[str] = []
    for index, (name, _description) in enumerate(WORKFLOW_STEPS):
        active_class = " style='border-color:#7b6ce1;color:#5e52ce;background:#f2efff'" if active_step == index else ""
        parts.append(f"<span class='gp-flow-step'{active_class}>{index + 1}. {name}</span>")
        if index < len(WORKFLOW_STEPS) - 1:
            parts.append("<span class='gp-flow-arrow'>→</span>")
    st.markdown("<div class='gp-flow'>" + "".join(parts) + "</div>", unsafe_allow_html=True)


def render_agent_pipeline(
    steps: list[tuple[str, str, str]],
    *,
    active_step: int | None = None,
    completed: bool = False,
    start_index: int = 0,
) -> None:
    """展示可理解的多 Agent 协作链路，不触发额外模型调用。"""
    parts = ["<div class='gp-agent-pipeline'>"]
    for index, (name, description, _icon) in enumerate(steps):
        state_class = " is-active" if active_step == index else ""
        if completed or (active_step is not None and index < active_step):
            state_label = "已完成"
        elif active_step == index:
            state_label = "执行中"
        else:
            state_label = "待执行"
        parts.append(
            f"<div class='gp-agent-step{state_class}'>"
            f"<div class='gp-agent-index'>{start_index + index + 1:02d}</div>"
            "<div>"
            f"<div class='gp-agent-name'>{escape(name)}</div>"
            f"<div class='gp-agent-description'>{escape(description)}</div>"
            "</div>"
            f"<div class='gp-agent-state'>{state_label}</div>"
            "</div>"
        )
        if index < len(steps) - 1:
            parts.append("<div class='gp-agent-arrow'>↓</div>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_module_card(icon: str, title: str, copy: str) -> None:
    with st.container(border=True):
        st.markdown(f":material/{icon}:")
        st.markdown(f"<div class='gp-module-title'>{title}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='gp-module-copy'>{copy}</div>", unsafe_allow_html=True)


def render_section(title: str, icon: str, content: str) -> None:
    with st.container(border=True):
        st.markdown(f"#### :material/{icon}: {title}")
        st.markdown(content)


def render_output(output: OutputResult, dataframe=None) -> None:
    st.success(
        f"已生成 · 耗时 {output.elapsed_seconds:.1f} 秒 · {output.provider_label}",
        icon=":material/check_circle:",
    )
    if isinstance(output, AgentResult):
        cards = [
            (SECTION_TITLES[key], icon, key)
            for key, icon in [
                ("product_positioning", "target"), ("user_persona", "groups"),
                ("competitive_landscape", "travel_explore"), ("xiaohongshu_plan", "auto_stories"),
                ("douyin_topics", "movie"), ("content_calendar", "calendar_month"),
                ("growth_strategy", "trending_up"), ("campaign_plan", "campaign"),
            ]
        ]
    elif isinstance(output, InsightResult):
        cards = [(SECTION_TITLES[key], icon, key) for key, icon in [
            ("product_positioning", "target"), ("user_persona", "groups"),
            ("competitive_landscape", "travel_explore"),
        ]]
    elif isinstance(output, SpecialistResult):
        agent = SPECIALIST_AGENTS[output.agent_type]
        cards = [(title, agent["icon"], key) for key, title in agent["fields"].items()]
    else:
        work = CREATIVE_WORKS[output.work_type]
        cards = [(title, work["icon"], key) for key, title in work["fields"].items()]

    for start in range(0, len(cards), 2):
        left, right = st.columns(2, gap="medium")
        for column, (title, icon, key) in zip((left, right), cards[start : start + 2]):
            with column:
                render_section(title, icon, output.sections[key])

    with st.expander("复制或导出生成结果", icon=":material/content_copy:"):
        st.caption("可使用代码块右上角的复制图标，或下载 Markdown 文件。")
        st.code(output.full_markdown, language="markdown")
        st.download_button(
            "下载 Markdown 文件",
            output.full_markdown,
            file_name="growthpilot-result.md",
            mime="text/markdown",
            icon=":material/download:",
            width="stretch",
        )
    render_export_actions(
        output.full_markdown,
        dataframe=dataframe,
        report_title=getattr(output, "label", "GrowthPilot AI OS 报告"),
    )


def render_export_actions(
    markdown: str,
    dataframe=None,
    report_title: str = "GrowthPilot AI OS 报告",
) -> None:
    """将当前真实生成内容转换为可交付的办公文件。"""
    st.space("small")
    with st.expander("导出企业工作文件", icon=":material/file_export:"):
        st.caption("报告可导出为 PDF、Word、PPT 和 Excel；文件由当前结果即时生成。")
        available = export_formats_available()
        missing = [label for key, label in {"word": "Word", "pdf": "PDF", "ppt": "PPT", "excel": "Excel"}.items() if not available[key]]
        if missing:
            st.warning(
                "当前环境缺少导出依赖：" + "、".join(missing) + "。请按 requirements.txt 安装后重启应用。",
                icon=":material/download:",
            )
            return
        word_bytes = build_word_report(markdown, report_title)
        pdf_bytes = build_pdf_report(markdown, report_title)
        ppt_bytes = build_ppt_report(markdown, report_title)
        excel_bytes = build_excel_report(markdown, dataframe, report_title)
        with st.container(horizontal=True):
            st.download_button("导出 Word", word_bytes, "growthpilot-report.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", icon=":material/description:")
            st.download_button("导出 PDF", pdf_bytes, "growthpilot-report.pdf", "application/pdf", icon=":material/picture_as_pdf:")
            st.download_button("导出 PPT", ppt_bytes, "growthpilot-plan.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", icon=":material/slideshow:")
            st.download_button("导出 Excel", excel_bytes, "growthpilot-analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", icon=":material/table_chart:")


def render_media_job(job: MediaGenerationJob) -> None:
    message = job.message
    if job.status == "等待配置":
        st.warning(message, icon=":material/key_off:")
    else:
        st.info(message, icon=":material/construction:")
    with st.expander("查看媒体生成请求结构", icon=":material/api:"):
        st.code(job.full_markdown, language="markdown")


def _handle_generation(action: Callable[[], OutputResult], label: str) -> OutputResult | None:
    st.session_state.task_status = "执行中"
    with st.status(f"{label}正在执行", expanded=True) as status:
        status.write(":material/psychology: AI 正在读取业务简报与目标。")
        try:
            output = action()
        except Exception:
            status.update(label="生成失败", state="error", expanded=True)
            st.session_state.task_status = "连接失败"
            st.error(CONNECTION_ERROR_MESSAGE, icon=":material/error:")
            return None
        status.write(":material/auto_awesome: DeepSeek 已完成内容与策略生成。")
        status.update(label=f"{label}已完成", state="complete", expanded=False)
        return output


def run_growth_plan(brief: GrowthBrief) -> AgentResult | None:
    st.session_state.task_status = "执行中"
    with st.status("增长运营 Agent 正在执行", expanded=True) as status:
        def show_step(index: int) -> None:
            name, description = WORKFLOW_STEPS[index]
            status.write(f":material/check_circle: **第 {index + 1} 步：{name}** · {description}")

        try:
            result = generate_growth_plan(brief, on_step=show_step)
        except Exception:
            status.update(label="生成失败", state="error", expanded=True)
            st.session_state.task_status = "连接失败"
            st.error(CONNECTION_ERROR_MESSAGE, icon=":material/error:")
            return None
        status.update(label="完整增长运营方案已完成", state="complete", expanded=False)
        return result


def run_creative_work(
    brief: GrowthBrief,
    work_type: str,
    strategy_context: AgentResult | None = None,
) -> CreativeResult | None:
    return _handle_generation(
        lambda: generate_creative_work(brief, work_type, strategy_context),
        CREATIVE_WORKS[work_type]["label"],
    )


def run_user_insights(brief: GrowthBrief) -> InsightResult | None:
    return _handle_generation(lambda: generate_user_insights(brief), "用户洞察")


def run_specialist_agent(
    agent_type: str,
    brief: GrowthBrief,
    additional_context: str = "",
) -> SpecialistResult | None:
    label = SPECIALIST_AGENTS[agent_type]["label"]
    return _handle_generation(
        lambda: generate_specialist_agent(agent_type, brief, additional_context),
        label,
    )
