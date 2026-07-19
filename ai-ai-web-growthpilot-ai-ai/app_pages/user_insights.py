import streamlit as st

from services.ui import render_output, render_page_intro, run_specialist_agent, run_user_insights
from services.workspace import brief_defaults, is_valid_brief, make_brief, remember_brief, save_history


render_page_intro(
    "USER INSIGHTS · 用真实业务语境理解用户",
    "用户洞察<br><span>找到增长的关键人群</span>",
    "通过产品定位、用户画像与竞争环境分析，为内容和增长策略建立可靠的输入。",
)
st.space("medium")

defaults = brief_defaults()
with st.form("user_insights_form", border=True):
    product_name = st.text_input("产品名称", value=defaults["product_name"])
    product_intro = st.text_area("产品信息", value=defaults["product_intro"], height=100)
    left, right = st.columns(2)
    with left:
        industry = st.text_input("所在行业", value=defaults["industry"])
    with right:
        target_user = st.text_input("目标用户", value=defaults["target_user"])
    marketing_goal = st.text_input("营销目标", value=defaults["marketing_goal"], placeholder="本次希望验证的用户与增长问题")
    insight_submitted = st.form_submit_button("运行用户洞察 Agent", icon=":material/groups:", type="primary", width="stretch")
    legacy_submitted = st.form_submit_button("生成基础用户洞察", icon=":material/search:", width="stretch")

if insight_submitted or legacy_submitted:
    brief = make_brief(product_name, product_intro, industry, target_user, marketing_goal)
    if not is_valid_brief(brief):
        st.warning("请完整填写业务信息后再开始分析。", icon=":material/info:")
    else:
        remember_brief(brief)
        result = run_specialist_agent("user_insight", brief) if insight_submitted else run_user_insights(brief)
        if result:
            st.session_state.current_output = result
            save_history(brief, result.label if insight_submitted else "基础用户洞察", result.full_markdown, output=result, kind="analysis")

if st.session_state.current_output:
    st.space("large")
    render_output(st.session_state.current_output)
