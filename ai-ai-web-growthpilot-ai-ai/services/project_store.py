"""轻量级 SQLite 项目、任务与活动记录存储。

本地开发可直接持久化到 data/growthpilot.db；公网部署时应将该层替换为
托管数据库，不影响上层页面和 Agent 服务调用。
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator
from uuid import uuid4


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "growthpilot.db"


@contextmanager
def _connection() -> Iterator[sqlite3.Connection]:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialise_store() -> None:
    with _connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                title TEXT NOT NULL,
                owner TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                due_date TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            );
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                product_name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            );
            """
        )


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def create_project(name: str, industry: str, description: str) -> dict[str, str]:
    initialise_store()
    project = {
        "id": uuid4().hex,
        "name": name.strip(),
        "industry": industry.strip(),
        "description": description.strip(),
        "status": "进行中",
        "created_at": _now(),
        "updated_at": _now(),
    }
    with _connection() as connection:
        connection.execute(
            """INSERT INTO projects (id, name, industry, description, status, created_at, updated_at)
            VALUES (:id, :name, :industry, :description, :status, :created_at, :updated_at)""",
            project,
        )
    return project


def list_projects() -> list[dict[str, str]]:
    initialise_store()
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def update_project_status(project_id: str, status: str) -> None:
    with _connection() as connection:
        connection.execute(
            "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
            (status, _now(), project_id),
        )


def add_task(
    project_id: str,
    title: str,
    owner: str,
    priority: str,
    due_date: str | None = None,
) -> dict[str, str]:
    task = {
        "id": uuid4().hex,
        "project_id": project_id,
        "title": title.strip(),
        "owner": owner.strip() or "未分配",
        "status": "待处理",
        "priority": priority,
        "due_date": due_date or "",
        "created_at": _now(),
    }
    with _connection() as connection:
        connection.execute(
            """INSERT INTO tasks (id, project_id, title, owner, status, priority, due_date, created_at)
            VALUES (:id, :project_id, :title, :owner, :status, :priority, :due_date, :created_at)""",
            task,
        )
    return task


def list_tasks(project_id: str) -> list[dict[str, str]]:
    with _connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at DESC", (project_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def update_task_status(task_id: str, status: str) -> None:
    with _connection() as connection:
        connection.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))


def record_activity(
    project_id: str,
    task_type: str,
    product_name: str,
    content: str,
) -> None:
    with _connection() as connection:
        connection.execute(
            """INSERT INTO activities (id, project_id, task_type, product_name, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (uuid4().hex, project_id, task_type, product_name, content, _now()),
        )
        connection.execute("UPDATE projects SET updated_at = ? WHERE id = ?", (_now(), project_id))


def list_activities(project_id: str | None = None, limit: int = 50) -> list[dict[str, str]]:
    with _connection() as connection:
        if project_id:
            rows = connection.execute(
                "SELECT * FROM activities WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
                (project_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM activities ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [dict(row) for row in rows]
