import streamlit as st

from services.ui import render_output, render_page_intro, run_creative_work
from services.workspace import is_valid_brief, latest_matching_plan, make_brief, remember_brief, save_history


render_page_intro(
    "XIAOHONGSHU ASSISTANT · 面向种草与转化的内容引擎",
    "小红书助手<br><span>把卖点写成用户想收藏的内容</span>",
    "输入产品、目标用户和核心卖点，生成 10 条标题、正文、标签与评论区运营话术。",
)
st.space("medium")

with st.form("xiaohongshu_form", border=True):
    product_name = st.text_input("产品", placeholder="例如：元气盒子")
    target_user = st.text_input("目标用户", placeholder="例如：想控制饮食但没有时间做饭的城市白领")
    selling_point = st.text_area("核心卖点", placeholder="例如：每周配送、营养师搭配、低负担又省时间。", height=110)
    submitted = st.form_submit_button(
        "生成小红书运营内容",
        icon=":material/auto_stories:",
        type="primary",
        width="stretch",
    )

if submitted:
    brief = make_brief(
        product_name,
        selling_point,
        "小红书内容营销",
        target_user,
        "在小红书建立可信种草内容，并推动用户评论、收藏和私信咨询。",
    )
    if not is_valid_brief(brief):
        st.warning("请填写产品、目标用户和核心卖点。", icon=":material/info:")
    else:
        remember_brief(brief)
        result = run_creative_work(brief, "xiaohongshu", latest_matching_plan(brief))
        if result:
            st.session_state.current_output = result
            save_history(brief, result.label, result.full_markdown, output=result, kind="creative")

if st.session_state.current_output:
    st.space("large")
    render_output(st.session_state.current_output)
