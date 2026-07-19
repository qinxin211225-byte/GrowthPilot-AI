import streamlit as st

from services.generator import AgentResult
from services.portfolio_showcase import AGENT_PIPELINE
from services.ui import render_agent_pipeline, render_output, render_page_intro, run_growth_plan, run_specialist_agent
from services.workspace import (
    brief_defaults,
    is_valid_brief,
    make_brief,
    remember_brief,
    save_history,
)


render_page_intro(
    "GROWTH ANALYSIS · 真实 DeepSeek 工作流",
    "AI增长分析<br><span>把业务问题转化为增长动作</span>",
    "输入产品信息、行业、目标用户与营销目标，输出市场分析、用户画像、增长建议和完整执行方案。",
)
st.space("medium")
st.markdown("<div class='gp-section-kicker'>当前 Agent 工作流</div>", unsafe_allow_html=True)
workflow_col, outcome_col = st.columns([1.05, 0.95], gap="large")
with workflow_col:
    render_agent_pipeline(AGENT_PIPELINE)
with outcome_col:
    with st.container(border=True):
        st.markdown("#### :material/inventory_2: 本页核心产出")
        st.markdown("**市场分析** · 判断竞争环境和增长机会")
        st.markdown("**用户画像** · 明确人群、场景和决策因素")
        st.markdown("**增长建议** · 形成获客、转化、留存和执行动作")
        st.caption("完整方案还会补充内容规划、活动策略与可下载报告。")
st.space("medium")

defaults = brief_defaults()
with st.container(border=True):
    st.markdown("### :material/edit_note: 创建增长简报")
    st.caption("所有字段会被发送给 DeepSeek，用于生成与当前业务匹配的真实策略结果。")
    with st.form("growth_analysis_form"):
        product_name = st.text_input("产品名称", value=defaults["product_name"], placeholder="例如：元气盒子")
        product_intro = st.text_area(
            "产品信息",
            value=defaults["product_intro"],
            placeholder="说明产品价值、核心服务、价格或差异化。",
            height=110,
        )
        industry = st.text_input("所在行业", value=defaults["industry"], placeholder="例如：健康轻食与生活方式消费")
        target_user = st.text_input("目标用户", value=defaults["target_user"], placeholder="例如：一线城市 25-35 岁职场人群")
        marketing_goal = st.text_area(
            "营销目标",
            value=defaults["marketing_goal"],
            placeholder="例如：30 天内获得 500 名试用用户并建立品牌种草心智。",
            height=90,
        )
        full_plan_submitted = st.form_submit_button(
            "生成完整增长方案",
            type="primary",
            icon=":material/bolt:",
            width="stretch",
        )
        strategy_agent_submitted = st.form_submit_button(
            "运行增长策略 Agent",
            icon=":material/psychology:",
            width="stretch",
        )

if full_plan_submitted or strategy_agent_submitted:
    brief = make_brief(product_name, product_intro, industry, target_user, marketing_goal)
    if not is_valid_brief(brief):
        st.warning("请完整填写产品信息、行业、目标用户和营销目标。", icon=":material/info:")
    else:
        remember_brief(brief)
        result = (
            run_growth_plan(brief)
            if full_plan_submitted
            else run_specialist_agent("growth_strategy", brief)
        )
        if result:
            st.session_state.current_output = result
            if isinstance(result, AgentResult):
                st.session_state.current_plan = result
                from services.workspace import brief_signature

                st.session_state.current_plan_signature = brief_signature(brief)
            save_history(
                brief,
                "完整增长运营方案" if full_plan_submitted else result.label,
                result.full_markdown,
                output=result,
                kind="analysis",
            )

current_output = st.session_state.current_output
if current_output:
    st.space("large")
    st.markdown("<div class='gp-section-kicker'>生成结果</div>", unsafe_allow_html=True)
    render_output(current_output)
