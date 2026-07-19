"""上传业务数据的读取、脱敏摘要与可视化辅助函数。"""

from __future__ import annotations

from io import BytesIO

import pandas as pd


MAX_CONTEXT_ROWS = 12


def build_sample_operations_data() -> pd.DataFrame:
    """提供可公开演示的数据集，便于面试现场快速展示分析流程。"""
    return pd.DataFrame(
        {
            "日期": pd.date_range("2025-12-01", periods=14, freq="D"),
            "内容曝光": [3200, 3800, 4100, 3900, 5200, 6100, 6800, 7200, 7600, 8300, 8900, 9400, 10100, 10800],
            "主页访问": [210, 248, 276, 255, 342, 401, 450, 472, 488, 530, 566, 590, 625, 662],
            "咨询数": [18, 21, 25, 20, 31, 36, 43, 41, 46, 50, 49, 55, 61, 66],
            "订单数": [4, 5, 6, 4, 8, 9, 11, 10, 12, 13, 11, 14, 16, 17],
            "订单金额": [3580, 4480, 5280, 3680, 7280, 8190, 9980, 9160, 10980, 11980, 10180, 12880, 14680, 15880],
        }
    )


def read_uploaded_table(file_name: str, raw_bytes: bytes) -> pd.DataFrame:
    extension = file_name.rsplit(".", maxsplit=1)[-1].lower()
    if extension == "csv":
        return pd.read_csv(BytesIO(raw_bytes))
    if extension in {"xlsx", "xls"}:
        return pd.read_excel(BytesIO(raw_bytes))
    raise ValueError("仅支持 CSV、XLSX 或 XLS 文件。")


def build_data_context(dataframe: pd.DataFrame) -> str:
    """构造供 Agent 使用的受限摘要，避免把整份表格直接发给模型。"""
    rows, columns = dataframe.shape
    missing = dataframe.isna().sum()
    missing_summary = ", ".join(
        f"{column}: {int(count)}" for column, count in missing.items() if count > 0
    ) or "无"
    numeric_columns = dataframe.select_dtypes(include="number").columns.tolist()
    numeric_summary = "无数值列"
    if numeric_columns:
        stats = dataframe[numeric_columns].describe().round(2).transpose()
        numeric_summary = stats.to_csv()
    sample = dataframe.head(MAX_CONTEXT_ROWS).fillna("").to_csv(index=False)
    return f"""数据规模：{rows} 行 × {columns} 列
字段与类型：{', '.join(f'{column}（{dtype}）' for column, dtype in dataframe.dtypes.items())}
缺失值：{missing_summary}

数值字段摘要：
{numeric_summary}

前 {min(rows, MAX_CONTEXT_ROWS)} 行样本（仅用于理解字段含义）：
{sample}
"""


def get_numeric_columns(dataframe: pd.DataFrame) -> list[str]:
    return dataframe.select_dtypes(include="number").columns.tolist()


def get_date_columns(dataframe: pd.DataFrame) -> list[str]:
    candidates: list[str] = []
    for column in dataframe.columns:
        name = str(column).lower()
        if any(token in name for token in ("date", "time", "日期", "时间", "月", "周")):
            candidates.append(str(column))
    return candidates
