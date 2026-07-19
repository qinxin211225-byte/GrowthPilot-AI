import streamlit as st

from services.generator import AgentResult, CreativeResult, InsightResult, SpecialistResult
from services.media_clients import MediaGenerationJob
from services.project_store import list_activities
from services.ui import render_media_job, render_output, render_page_intro
from services.workspace import clear_history, restore_history


render_page_intro(
    "PROJECT HISTORY · 保留真实生成过程与可复用成果",
    "历史项目<br><span>每一次生成，都是下一次增长的资产</span>",
    "生成结果会进入当前会话记录；归档到项目后的活动还会保存在本地项目数据库中。",
)
st.space("medium")

history = st.session_state.history
persisted_activities = list_activities(st.session_state.active_project_id or None, limit=30)
if not history and not persisted_activities:
    with st.container(border=True):
        st.markdown("#### :material/history: 暂无历史项目")
        st.caption("在增长分析、内容工厂、短视频中心或小红书助手完成任务后，结果会自动进入这里。")
else:
    top_left, top_right = st.columns([5, 1], vertical_alignment="center")
    with top_left:
        st.caption(f"当前会话已保存 {len(history)} 条真实任务记录。")
    with top_right:
        st.button("清空记录", icon=":material/delete_sweep:", on_click=clear_history, width="stretch")

    for record in history:
        with st.expander(
            f"{record['task_type']} · {record['product_name']} · {record['created_at']}",
            icon=":material/history:",
        ):
            st.caption(record["preview"])
            if st.button("打开完整结果", key=f"open_history_{record['id']}", icon=":material/open_in_new:"):
                restore_history(record["id"])
                st.session_state.history_selected_id = record["id"]

selected_id = st.session_state.get("history_selected_id")
selected = next((record for record in st.session_state.history if record["id"] == selected_id), None)
if selected:
    st.space("large")
    st.markdown("<div class='gp-section-kicker'>项目结果</div>", unsafe_allow_html=True)
    output = selected.get("output")
    if isinstance(output, (AgentResult, CreativeResult, InsightResult, SpecialistResult)):
        render_output(output)
    elif isinstance(output, MediaGenerationJob):
        render_media_job(output)
    else:
        st.markdown(selected["content"])

if persisted_activities:
    st.space("large")
    st.markdown("<div class='gp-section-kicker'>当前项目已归档活动</div>", unsafe_allow_html=True)
    scope_label = st.session_state.active_project_name if st.session_state.active_project_id else "全部项目"
    st.caption(f"当前范围：{scope_label}。这些记录保存在项目数据库中，刷新浏览器后仍可查看。")
    for activity in persisted_activities:
        with st.expander(f"{activity['task_type']} · {activity['created_at']}", icon=":material/database:"):
            st.markdown(activity["content"])
