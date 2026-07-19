import pandas as pd
import streamlit as st

from services.project_store import (
    add_task,
    create_project,
    list_activities,
    list_projects,
    list_tasks,
    update_project_status,
    update_task_status,
)
from services.ui import render_page_intro
from services.workspace import set_active_project


render_page_intro(
    "PROJECT HUB · 用项目组织策略、内容和执行任务",
    "项目管理<br><span>让 Agent 输出进入真实工作流</span>",
    "项目会持久化到本地 SQLite 数据库；在生产部署时可将同一服务层替换为企业数据库。",
)
st.space("medium")

create_tab, manage_tab = st.tabs(["创建项目", "项目任务"], on_change="rerun", key="project_management_tab")
if create_tab.open:
    with create_tab:
        with st.form("create_project_form", border=True):
            name = st.text_input("项目名称", placeholder="例如：元气盒子新品增长计划")
            industry = st.text_input("行业", placeholder="例如：健康轻食与生活方式消费")
            description = st.text_area("项目说明", placeholder="说明项目目标、业务背景和预期产出。", height=100)
            create_submitted = st.form_submit_button("创建并设为当前项目", icon=":material/create_new_folder:", type="primary", width="stretch")
        if create_submitted:
            if not all([name.strip(), industry.strip(), description.strip()]):
                st.warning("请完整填写项目名称、行业和项目说明。", icon=":material/info:")
            else:
                project = create_project(name, industry, description)
                set_active_project(project["id"], project["name"])
                st.success("项目已创建，并已设为当前项目。", icon=":material/check_circle:")

if manage_tab.open:
    with manage_tab:
        projects = list_projects()
        if not projects:
            st.info("请先创建一个项目，再添加任务和归档 Agent 输出。", icon=":material/folder:")
        else:
            project_options = {f"{project['name']} · {project['status']}": project for project in projects}
            selected_label = st.selectbox("选择项目", list(project_options), key="project_selector")
            selected_project = project_options[selected_label]
            if st.button("设为当前项目", icon=":material/check_circle:"):
                set_active_project(selected_project["id"], selected_project["name"])
                st.toast("当前项目已切换。", icon=":material/check_circle:")

            status_options = ["进行中", "已暂停", "已完成"]
            current_status = st.selectbox(
                "项目状态", status_options, index=status_options.index(selected_project["status"]) if selected_project["status"] in status_options else 0
            )
            if st.button("更新项目状态", icon=":material/update:"):
                update_project_status(selected_project["id"], current_status)
                st.rerun()

            st.space("medium")
            with st.form("create_task_form", border=True):
                task_title = st.text_input("新增任务", placeholder="例如：完成首周小红书内容排期")
                task_owner = st.text_input("负责人", placeholder="例如：内容运营")
                task_priority = st.segmented_control("优先级", ["高", "中", "低"], default="中")
                due_date = st.date_input("截止日期")
                task_submitted = st.form_submit_button("添加任务", icon=":material/add_task:", type="primary", width="stretch")
            if task_submitted:
                if not task_title.strip():
                    st.warning("请填写任务名称。", icon=":material/info:")
                else:
                    add_task(selected_project["id"], task_title, task_owner, task_priority or "中", str(due_date))
                    st.rerun()

            tasks = list_tasks(selected_project["id"])
            st.markdown("#### :material/checklist: 任务列表")
            if tasks:
                task_table = pd.DataFrame(tasks)[["title", "owner", "priority", "status", "due_date"]]
                task_table.columns = ["任务", "负责人", "优先级", "状态", "截止日期"]
                st.dataframe(task_table, hide_index=True)
                for task in tasks:
                    left, right = st.columns([4, 1])
                    with left:
                        st.caption(f"{task['title']} · {task['owner']} · {task['priority']}优先级")
                    with right:
                        status = st.selectbox("状态", ["待处理", "进行中", "已完成"], index=["待处理", "进行中", "已完成"].index(task["status"]) if task["status"] in ["待处理", "进行中", "已完成"] else 0, key=f"task_status_{task['id']}", label_visibility="collapsed")
                        if status != task["status"]:
                            update_task_status(task["id"], status)
                            st.rerun()
            else:
                st.caption("当前项目还没有任务。")

            activities = list_activities(selected_project["id"], limit=8)
            if activities:
                st.markdown("#### :material/history: 已归档 Agent 活动")
                for activity in activities:
                    st.caption(f"{activity['created_at']} · {activity['task_type']} · {activity['product_name']}")
