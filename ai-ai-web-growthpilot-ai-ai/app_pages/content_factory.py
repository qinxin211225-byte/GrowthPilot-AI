import streamlit as st

from services.generator import CreativeResult, SpecialistResult
from services.media_clients import create_media_job, supported_provider_names
from services.portfolio_showcase import OPERATION_TEMPLATES, get_template
from services.ui import render_media_job, render_output, render_page_intro, run_creative_work, run_specialist_agent
from services.workspace import (
    brief_defaults,
    is_valid_brief,
    latest_matching_plan,
    make_brief,
    remember_brief,
    save_history,
)


render_page_intro(
    "CONTENT FACTORY · 从策略到可发布内容",
    "AI内容中心<br><span>一次输入，生成全渠道内容包</span>",
    "输入产品与目标用户，生成小红书内容、短视频脚本、公众号文章框架和营销推广文案。",
)
st.space("medium")
defaults = brief_defaults()

with st.container(border=True):
    st.markdown("### :material/package_2: 一键生成全渠道内容包")
    st.caption("同一份业务信息生成四类可直接进入编辑和发布流程的内容，避免不同渠道表达相互割裂。")
    with st.form("full_content_pack_form", border=False):
        pack_product = st.text_input("产品名称", value=defaults["product_name"], key="pack_product")
        pack_intro = st.text_area(
            "产品与核心卖点",
            value=defaults["product_intro"],
            placeholder="说明产品价值、差异化、价格或服务特点。",
            height=100,
            key="pack_intro",
        )
        pack_target = st.text_input("目标用户", value=defaults["target_user"], key="pack_target")
        pack_platform = st.segmented_control(
            "重点渠道",
            ["小红书", "抖音", "公众号", "多平台联动"],
            default="多平台联动",
            key="pack_platform",
        )
        pack_submitted = st.form_submit_button(
            "生成全渠道内容包",
            icon=":material/auto_awesome:",
            type="primary",
            width="stretch",
        )

if pack_submitted:
    template = get_template(st.session_state.active_template_id)
    pack_brief = make_brief(
        pack_product,
        pack_intro,
        defaults["industry"] or "品牌与内容营销",
        pack_target,
        f"使用{template.name}模板，围绕{pack_platform or '多平台'}生成可发布内容并促进咨询转化。",
    )
    if not is_valid_brief(pack_brief):
        st.warning("请完整填写产品、核心卖点和目标用户。", icon=":material/info:")
    else:
        remember_brief(pack_brief)
        pack_result = run_creative_work(pack_brief, "content_pack", latest_matching_plan(pack_brief))
        if pack_result:
            st.session_state.current_output = pack_result
            save_history(pack_brief, pack_result.label, pack_result.full_markdown, output=pack_result, kind="creative")

st.space("medium")
with st.container(border=True):
    st.markdown("### :material/auto_stories: 内容运营 Agent")
    st.caption("按所选平台生成小红书运营方案、公众号文章方案、短视频选题、爆款结构和内容日历。")
    with st.form("content_operations_form", border=False):
        content_product = st.text_input("产品名称", value=brief_defaults()["product_name"], key="content_product")
        content_intro = st.text_area("产品与核心卖点", value=brief_defaults()["product_intro"], key="content_intro", height=90)
        content_target = st.text_input("目标用户", value=brief_defaults()["target_user"], key="content_target")
        platform = st.segmented_control("核心平台", ["小红书", "公众号", "抖音", "多平台联动"], default="小红书", key="content_platform")
        content_submitted = st.form_submit_button("运行内容运营 Agent", icon=":material/auto_awesome:", type="primary", width="stretch")

if content_submitted:
    content_brief = make_brief(
        content_product,
        content_intro,
        defaults["industry"] or "内容营销",
        content_target,
        f"围绕{platform or '小红书'}建立内容资产并提升互动与转化。",
    )
    if not is_valid_brief(content_brief):
        st.warning("请完整填写产品、卖点和目标用户。", icon=":material/info:")
    else:
        remember_brief(content_brief)
        content_result = run_specialist_agent(
            "content_operations",
            content_brief,
            f"重点平台：{platform}\n运营模板：{get_template(st.session_state.active_template_id).instruction}",
        )
        if content_result:
            st.session_state.current_output = content_result
            save_history(content_brief, content_result.label, content_result.full_markdown, output=content_result, kind="creative")

st.space("medium")
with st.container(border=True):
    st.markdown("### :material/dashboard_customize: 运营模板中心")
    template_names = list(OPERATION_TEMPLATES)
    active_template = st.session_state.active_template_id
    selected_template = st.selectbox(
        "选择模板",
        template_names,
        index=template_names.index(active_template) if active_template in template_names else 0,
        key="portfolio_content_template",
    )
    st.session_state.active_template_id = selected_template
    selected_spec = get_template(selected_template)
    st.caption(selected_spec.description)
    st.markdown(f"**生成侧重点：** {selected_spec.instruction}")

with st.container(border=True):
    st.markdown("### :material/imagesmode: 营销海报生成")
    st.caption("第一步由 DeepSeek 输出真实的海报策略与图片提示词；第二步预留图片模型 API 接口。")
    with st.form("poster_factory_form", border=False):
        brand = st.text_input("品牌", value=defaults["product_name"], placeholder="例如：元气盒子")
        product = st.text_area(
            "产品",
            value=defaults["product_intro"],
            placeholder="产品核心价值、卖点、产品形态。",
            height=100,
        )
        campaign = st.text_input("活动", value=defaults["marketing_goal"], placeholder="例如：新品订阅首周尝鲜计划")
        target_user = st.text_input("活动目标人群", value=defaults["target_user"], placeholder="例如：城市白领与轻食爱好者")
        submitted = st.form_submit_button(
            "生成海报设计方案",
            icon=":material/auto_awesome:",
            type="primary",
            width="stretch",
        )

if submitted:
    brief = make_brief(
        brand,
        product,
        defaults["industry"] or "品牌营销",
        target_user,
        campaign,
    )
    if not is_valid_brief(brief):
        st.warning("请填写品牌、产品、活动和目标人群。", icon=":material/info:")
    else:
        remember_brief(brief)
        result = run_creative_work(brief, "poster", latest_matching_plan(brief))
        if result:
            st.session_state.current_output = result
            st.session_state.poster_brief = brief
            save_history(brief, result.label, result.full_markdown, output=result, kind="creative")

poster_output = st.session_state.get("current_output")
if isinstance(poster_output, SpecialistResult) and poster_output.agent_type == "content_operations":
    st.space("large")
    render_output(poster_output)
elif isinstance(poster_output, CreativeResult) and poster_output.work_type in {"poster", "content_pack"}:
    st.space("large")
    render_output(poster_output)

st.space("large")
with st.container(border=True):
    st.markdown("### :material/api: 图片生成 API 接口")
    st.caption("选择 Provider 后会创建透明的接口任务。未配置 Provider 密钥时，不会伪造海报文件。")
    provider = st.selectbox("图片 Provider", supported_provider_names("image"), key="poster_provider")
    media_left, media_right = st.columns(2)
    with media_left:
        style = st.selectbox("视觉风格", ["品牌质感", "极简科技", "节日营销", "生活方式"], key="poster_style")
    with media_right:
        ratio = st.segmented_control("海报比例", ["1:1", "3:4", "9:16"], default="3:4", key="poster_ratio")
    if st.button("提交图片生成任务", icon=":material/image:", width="stretch"):
        if not (isinstance(poster_output, CreativeResult) and poster_output.work_type == "poster"):
            st.warning("请先生成海报设计方案，再提交图片生成任务。", icon=":material/info:")
        else:
            prompt = poster_output.sections["image_prompt"]
            job = create_media_job("image", provider, prompt, style, ratio or "3:4")
            st.session_state.poster_media_job = job
            brief = st.session_state.get("poster_brief")
            if brief:
                save_history(brief, "图片生成接口任务", job.full_markdown, output=job, kind="media")

if st.session_state.get("poster_media_job"):
    render_media_job(st.session_state.poster_media_job)
