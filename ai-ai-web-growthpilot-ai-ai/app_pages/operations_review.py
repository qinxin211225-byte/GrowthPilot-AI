import streamlit as st

from services.ui import render_output, render_page_intro, run_specialist_agent
from services.workspace import make_brief, save_history


render_page_intro(
    "OPERATIONS REVIEW · 将结果沉淀为下一轮增长动作",
    "运营复盘<br><span>让每一次执行都转化为可复用经验</span>",
    "输入运营结果、关键指标和观察，运营复盘 Agent 会输出复盘报告、问题总结与下一步计划。",
)
st.space("medium")

with st.form("operations_review_form", border=True):
    project_name = st.text_input("项目或产品名称", value=st.session_state.active_project_name if st.session_state.active_project_id else "")
    operation_result = st.text_area(
        "运营结果",
        placeholder="例如：活动周期、投放/内容动作、核心指标、实际结果、用户反馈和未达预期的部分。",
        height=170,
    )
    review_goal = st.text_input("本次复盘重点", placeholder="例如：找出转化下滑原因，并制定下周内容优化计划。")
    submitted = st.form_submit_button("运行运营复盘 Agent", icon=":material/fact_check:", type="primary", width="stretch")

if submitted:
    brief = make_brief(
        project_name,
        operation_result,
        "增长运营复盘",
        "运营与市场团队",
        review_goal or "形成问题总结与下一步执行计划。",
    )
    if not all([brief.product_name, brief.product_intro, brief.marketing_goal]):
        st.warning("请至少填写项目名称、运营结果和复盘重点。", icon=":material/info:")
    else:
        result = run_specialist_agent("operations_review", brief, operation_result)
        if result:
            st.session_state.current_output = result
            st.session_state.operations_review_result = result
            save_history(brief, result.label, result.full_markdown, output=result, kind="analysis")

result = st.session_state.get("operations_review_result")
if result:
    st.space("large")
    render_output(result)
