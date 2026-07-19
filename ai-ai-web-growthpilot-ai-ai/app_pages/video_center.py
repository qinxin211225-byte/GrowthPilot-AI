import streamlit as st

from services.generator import CreativeResult, SpecialistResult
from services.media_clients import create_media_job, supported_provider_names
from services.ui import render_media_job, render_output, render_page_intro, run_creative_work, run_specialist_agent
from services.workspace import is_valid_brief, latest_matching_plan, make_brief, remember_brief, save_history


render_page_intro(
    "VIDEO STUDIO · 从选题到分镜的短视频工作流",
    "短视频中心<br><span>先写好，才能拍好</span>",
    "用 DeepSeek 生成视频主题、分镜、镜头、配音和 BGM 建议，并预留多视频模型的真实生成接口。",
)
st.space("medium")

with st.container(border=True):
    st.markdown("### :material/movie_filter: 视频创作 Agent")
    st.caption("从需求输入、选题分析到 AI 视频 Prompt 和发布方案，形成完整的视频生产链路。")
    with st.form("video_agent_form", border=False):
        agent_product = st.text_input("产品名称", key="video_agent_product")
        agent_intro = st.text_area("产品信息", key="video_agent_intro", height=90)
        agent_user = st.text_input("目标用户", key="video_agent_user")
        agent_platform = st.segmented_control("发布平台", ["抖音", "小红书", "视频号", "多平台"], default="抖音", key="video_agent_platform")
        agent_submitted = st.form_submit_button("运行视频创作 Agent", icon=":material/auto_awesome:", type="primary", width="stretch")

if agent_submitted:
    agent_brief = make_brief(
        agent_product,
        agent_intro,
        "视频内容营销",
        agent_user,
        f"为{agent_platform or '抖音'}建立可执行的视频生产与发布方案。",
    )
    if not is_valid_brief(agent_brief):
        st.warning("请完整填写产品信息与目标用户。", icon=":material/info:")
    else:
        remember_brief(agent_brief)
        agent_result = run_specialist_agent("video_creation", agent_brief, f"发布平台：{agent_platform}")
        if agent_result:
            st.session_state.current_output = agent_result
            save_history(agent_brief, agent_result.label, agent_result.full_markdown, output=agent_result, kind="creative")

if isinstance(st.session_state.get("current_output"), SpecialistResult) and st.session_state.current_output.agent_type == "video_creation":
    st.space("large")
    render_output(st.session_state.current_output)

with st.container(border=True):
    st.markdown("### :material/videocam: AI 短视频生成")
    with st.form("video_factory_form", border=False):
        product_name = st.text_input("产品名称", placeholder="例如：元气盒子")
        product_intro = st.text_area("产品信息", placeholder="产品卖点、使用场景、价格或优势。", height=100)
        target_user = st.text_input("目标用户", placeholder="例如：加班频繁、关注健康的城市职场人")
        video_style = st.segmented_control(
            "视频风格",
            ["真实口播", "剧情反转", "质感种草", "知识科普"],
            default="真实口播",
        )
        submitted = st.form_submit_button(
            "生成短视频方案",
            icon=":material/auto_awesome:",
            type="primary",
            width="stretch",
        )

if submitted:
    brief = make_brief(
        product_name,
        product_intro,
        "短视频内容营销",
        target_user,
        f"在抖音通过{video_style or '真实口播'}风格完成内容种草与转化。",
    )
    if not is_valid_brief(brief):
        st.warning("请完整填写产品信息和目标用户。", icon=":material/info:")
    else:
        remember_brief(brief)
        result = run_creative_work(brief, "video", latest_matching_plan(brief))
        if result:
            st.session_state.current_output = result
            st.session_state.video_brief = brief
            save_history(brief, result.label, result.full_markdown, output=result, kind="creative")

video_output = st.session_state.get("current_output")
if isinstance(video_output, CreativeResult) and video_output.work_type == "video":
    st.space("large")
    render_output(video_output)

st.space("large")
with st.container(border=True):
    st.markdown("### :material/phone_iphone: AI 抖音运营模块")
    st.caption("针对抖音的内容效率与转化场景，单独生成 30 秒脚本、黄金 3 秒、用户痛点和转化话术。")
    with st.form("douyin_operations_form", border=False):
        douyin_product = st.text_input("产品", key="douyin_product", placeholder="例如：元气盒子")
        douyin_target = st.text_input("目标用户", key="douyin_target", placeholder="例如：关注健康但经常加班的城市白领")
        douyin_point = st.text_area(
            "转化卖点",
            key="douyin_point",
            placeholder="例如：按周配送、营养搭配、首单低门槛体验。",
            height=85,
        )
        douyin_submitted = st.form_submit_button(
            "生成抖音运营脚本",
            icon=":material/auto_awesome:",
            type="primary",
            width="stretch",
        )

if douyin_submitted:
    douyin_brief = make_brief(
        douyin_product,
        douyin_point,
        "抖音短视频运营",
        douyin_target,
        "通过短视频建立认知、激发兴趣并引导用户完成咨询或下单。",
    )
    if not is_valid_brief(douyin_brief):
        st.warning("请填写产品、目标用户和转化卖点。", icon=":material/info:")
    else:
        remember_brief(douyin_brief)
        douyin_result = run_creative_work(
            douyin_brief, "douyin", latest_matching_plan(douyin_brief)
        )
        if douyin_result:
            st.session_state.current_output = douyin_result
            save_history(
                douyin_brief,
                douyin_result.label,
                douyin_result.full_markdown,
                output=douyin_result,
                kind="creative",
            )

if isinstance(st.session_state.get("current_output"), CreativeResult) and st.session_state.current_output.work_type == "douyin":
    st.space("large")
    render_output(st.session_state.current_output)

st.space("large")
with st.container(border=True):
    st.markdown("### :material/play_circle: 生成视频")
    st.caption("这里是视频模型接口入口。未接入 Runway、可灵AI、即梦AI、通义万相的真实凭证前，不会生成或伪造视频文件。")
    provider = st.selectbox("视频 Provider", supported_provider_names("video"), key="video_provider")
    controls_left, controls_right = st.columns(2)
    with controls_left:
        style = st.selectbox("生成风格", ["电影感", "真实感", "品牌广告", "社媒原生"], key="video_media_style")
    with controls_right:
        ratio = st.segmented_control("视频比例", ["9:16", "16:9", "1:1"], default="9:16", key="video_ratio")
    if st.button("生成视频", icon=":material/movie:", type="primary", width="stretch"):
        if not (isinstance(video_output, CreativeResult) and video_output.work_type == "video"):
            st.warning("请先生成短视频方案，再提交视频生成任务。", icon=":material/info:")
        else:
            prompt = "\n\n".join(
                [
                    video_output.sections["video_theme"],
                    video_output.sections["storyboard"],
                    video_output.sections["shot_design"],
                ]
            )
            job = create_media_job("video", provider, prompt, style, ratio or "9:16")
            st.session_state.video_media_job = job
            brief = st.session_state.get("video_brief")
            if brief:
                save_history(brief, "视频生成接口任务", job.full_markdown, output=job, kind="media")

if st.session_state.get("video_media_job"):
    render_media_job(st.session_state.video_media_job)
