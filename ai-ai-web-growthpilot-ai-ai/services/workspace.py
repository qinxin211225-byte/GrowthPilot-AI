"""GrowthPilot 工作台的会话状态、历史任务与统计数据。"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from services.generator import AgentResult, GrowthBrief
from services.project_store import initialise_store, record_activity


WORKSPACE_DEFAULTS: dict[str, Any] = {
    "workspace_brief": {
        "product_name": "",
        "product_intro": "",
        "industry": "",
        "target_user": "",
        "marketing_goal": "",
    },
    "history": [],
    "current_output": None,
    "current_plan": None,
    "current_plan_signature": "",
    "task_status": "待命",
    "last_activity": "尚未生成任务",
    "active_project_id": "",
    "active_project_name": "未归档项目",
    "active_model_id": "deepseek",
    "model_overrides": {},
    "active_template_id": "新媒体运营",
    "showcase_open": False,
    "showcase_case_id": "",
}


def initialise_workspace_state() -> None:
    """仅由入口文件调用，保证所有页面共享同一组会话状态。"""
    for key, value in WORKSPACE_DEFAULTS.items():
        st.session_state.setdefault(key, value.copy() if isinstance(value, dict) else value.copy() if isinstance(value, list) else value)
    initialise_store()


def set_active_project(project_id: str, project_name: str) -> None:
    st.session_state.active_project_id = project_id
    st.session_state.active_project_name = project_name


def load_showcase_brief(case_id: str, brief: dict[str, str]) -> None:
    """将展示案例载入工作台，供后续真实 Agent 页面继续使用。"""
    st.session_state.workspace_brief = dict(brief)
    st.session_state.showcase_open = True
    st.session_state.showcase_case_id = case_id
    st.session_state.last_activity = "已打开完整演示案例"


def make_brief(
    product_name: str,
    product_intro: str,
    industry: str,
    target_user: str,
    marketing_goal: str,
) -> GrowthBrief:
    return GrowthBrief(
        product_name=product_name.strip(),
        product_intro=product_intro.strip(),
        industry=industry.strip(),
        target_user=target_user.strip(),
        marketing_goal=marketing_goal.strip(),
    )


def is_valid_brief(brief: GrowthBrief) -> bool:
    return all(
        [brief.product_name, brief.product_intro, brief.industry, brief.target_user, brief.marketing_goal]
    )


def remember_brief(brief: GrowthBrief) -> None:
    st.session_state.workspace_brief = {
        "product_name": brief.product_name,
        "product_intro": brief.product_intro,
        "industry": brief.industry,
        "target_user": brief.target_user,
        "marketing_goal": brief.marketing_goal,
    }


def brief_defaults() -> dict[str, str]:
    return dict(st.session_state.workspace_brief)


def brief_signature(brief: GrowthBrief) -> str:
    return "\n".join(
        [
            brief.product_name,
            brief.product_intro,
            brief.industry,
            brief.target_user,
            brief.marketing_goal,
        ]
    )


def latest_matching_plan(brief: GrowthBrief) -> AgentResult | None:
    plan = st.session_state.current_plan
    if isinstance(plan, AgentResult) and st.session_state.current_plan_signature == brief_signature(brief):
        return plan
    return None


def save_history(
    brief: GrowthBrief,
    task_type: str,
    content: str,
    *,
    output: Any = None,
    kind: str = "analysis",
) -> None:
    created_at = datetime.now()
    record = {
        "id": created_at.isoformat(timespec="microseconds"),
        "created_at": created_at.strftime("%m-%d %H:%M"),
        "task_type": task_type,
        "product_name": brief.product_name,
        "preview": " ".join(content.split())[:96],
        "brief_signature": brief_signature(brief),
        "content": content,
        "output": output,
        "kind": kind,
    }
    st.session_state.history.insert(0, record)
    st.session_state.history = st.session_state.history[:30]
    st.session_state.task_status = "已完成"
    st.session_state.last_activity = f"{task_type} · {created_at.strftime('%H:%M')}"
    if st.session_state.active_project_id:
        record_activity(
            st.session_state.active_project_id,
            task_type,
            brief.product_name,
            content,
        )


def restore_history(record_id: str) -> dict[str, Any] | None:
    for record in st.session_state.history:
        if record["id"] == record_id:
            st.session_state.current_output = record.get("output")
            if isinstance(record.get("output"), AgentResult):
                st.session_state.current_plan = record["output"]
                st.session_state.current_plan_signature = record["brief_signature"]
            return record
    return None


def clear_history() -> None:
    st.session_state.history = []
    st.session_state.current_output = None
    st.session_state.current_plan = None
    st.session_state.current_plan_signature = ""
    st.session_state.task_status = "待命"
    st.session_state.last_activity = "历史项目已清空"


def get_workspace_metrics() -> dict[str, int | str]:
    today_prefix = datetime.now().strftime("%m-%d")
    history = st.session_state.history
    today = [record for record in history if record["created_at"].startswith(today_prefix)]
    content_tasks = [record for record in history if record.get("kind") in {"creative", "media"}]
    latest_plan = next(
        (record.get("output") for record in history if isinstance(record.get("output"), AgentResult)),
        None,
    )
    return {
        "today_generation_count": len(today),
        "content_count": len(content_tasks),
        "growth_suggestion_count": len(latest_plan.sections) if latest_plan else 0,
        "task_status": st.session_state.task_status,
        "active_project_name": st.session_state.active_project_name,
    }
