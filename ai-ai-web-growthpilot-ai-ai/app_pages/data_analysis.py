import pandas as pd
import streamlit as st

from services.data_tools import (
    build_data_context,
    build_sample_operations_data,
    get_date_columns,
    get_numeric_columns,
    read_uploaded_table,
)
from services.ui import render_output, render_page_intro, run_specialist_agent
from services.workspace import make_brief, save_history


render_page_intro(
    "DATA INTELLIGENCE · 用业务数据定位增长问题",
    "数据分析<br><span>上传数据，获得可执行的运营判断</span>",
    "支持 CSV、XLSX 与 XLS 文件。系统先在本地生成字段摘要，再将必要摘要发送给当前模型进行趋势、问题和优化建议分析。",
)
st.space("medium")

sample_dataframe = build_sample_operations_data()
with st.container(horizontal=True, vertical_alignment="center"):
    if st.button("载入示例运营数据", icon=":material/dataset:", key="load_sample_dataset"):
        st.session_state.uploaded_dataframe = sample_dataframe
        st.session_state.uploaded_data_name = "北大湖民宿内容转化示例.csv"
        st.toast("示例数据已载入，可直接查看图表或运行数据分析 Agent。", icon=":material/check_circle:")
    st.download_button(
        "下载示例 CSV",
        sample_dataframe.to_csv(index=False).encode("utf-8-sig"),
        file_name="growthpilot-sample-data.csv",
        mime="text/csv",
        icon=":material/download:",
    )

uploaded_file = st.file_uploader(
    "上传销售、用户或运营数据",
    type=["csv", "xlsx", "xls"],
    max_upload_size=30,
    key="business_data_upload",
)

if uploaded_file is not None:
    try:
        dataframe = read_uploaded_table(uploaded_file.name, uploaded_file.getvalue())
    except Exception:
        st.error("数据文件读取失败，请确认文件格式、编码或工作表内容。", icon=":material/error:")
        dataframe = None
    if dataframe is not None:
        st.session_state.uploaded_dataframe = dataframe
        st.session_state.uploaded_data_name = uploaded_file.name

dataframe = st.session_state.get("uploaded_dataframe")
if dataframe is None:
    with st.container(border=True):
        st.markdown("#### :material/upload_file: 等待上传业务数据")
        st.caption("可上传销售明细、用户行为、内容发布、投放或活动数据。文件不会被模拟替换。")
else:
    numeric_columns = get_numeric_columns(dataframe)
    date_columns = get_date_columns(dataframe)
    with st.container(horizontal=True):
        st.metric("数据行数", len(dataframe), border=True)
        st.metric("字段数量", len(dataframe.columns), border=True)
        st.metric("数值指标", len(numeric_columns), border=True)
        st.metric("缺失单元格", int(dataframe.isna().sum().sum()), border=True)

    preview_col, visual_col = st.columns([1.25, 0.75], gap="large")
    with preview_col:
        with st.container(border=True):
            st.markdown("#### :material/table_chart: 数据预览")
            st.dataframe(dataframe.head(100), hide_index=True, height=300)
    with visual_col:
        with st.container(border=True):
            st.markdown("#### :material/show_chart: 指标视图")
            if numeric_columns:
                metric_column = st.selectbox("选择数值指标", numeric_columns, key="data_chart_metric")
                if date_columns:
                    date_column = st.selectbox("选择时间维度", date_columns, key="data_chart_date")
                    chart_data = dataframe[[date_column, metric_column]].copy()
                    chart_data[date_column] = pd.to_datetime(chart_data[date_column], errors="coerce")
                    chart_data = chart_data.dropna().sort_values(date_column)
                    if not chart_data.empty:
                        st.line_chart(chart_data, x=date_column, y=metric_column)
                    else:
                        st.caption("无法将所选字段识别为可用时间序列。")
                else:
                    st.bar_chart(dataframe[[metric_column]].head(30))
            else:
                st.caption("数据中没有可直接绘制的数值字段。")

    st.space("medium")
    with st.container(border=True):
        st.markdown("### :material/analytics: 数据分析 Agent")
        st.caption("点击后会向当前模型发送数据规模、字段类型、缺失情况、统计摘要和前 12 行字段样本；请勿上传不应发送给模型的敏感数据。")
        analysis_scope = st.segmented_control(
            "分析场景",
            ["销售数据", "用户数据", "运营数据"],
            default="运营数据",
            key="data_analysis_scope",
        )
        if st.button("运行数据分析 Agent", icon=":material/insights:", type="primary", width="stretch"):
            file_name = st.session_state.get("uploaded_data_name", "业务数据")
            brief = make_brief(
                file_name,
                f"已上传 {len(dataframe)} 行、{len(dataframe.columns)} 列的{analysis_scope or '运营'}数据。",
                analysis_scope or "数据分析",
                "企业运营团队",
                "识别数据趋势、问题分析与优化建议。",
            )
            context = build_data_context(dataframe)
            result = run_specialist_agent("data_analysis", brief, context)
            if result:
                st.session_state.current_output = result
                st.session_state.data_analysis_result = result
                save_history(brief, result.label, result.full_markdown, output=result, kind="analysis")

    result = st.session_state.get("data_analysis_result")
    if result:
        st.space("large")
        render_output(result, dataframe=dataframe)
