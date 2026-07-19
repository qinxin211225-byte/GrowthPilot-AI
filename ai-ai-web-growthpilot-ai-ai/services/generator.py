"""GrowthPilot AI 的真实增长运营 Agent 与内容生产 Agent。"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from services.llm_client import CONNECTION_ERROR_MESSAGE, DeepSeekClient, load_deepseek_config


WORKFLOW_STEPS = [
    ("产品分析", "梳理产品价值、行业位置与目标任务"),
    ("用户画像", "识别高潜人群、使用场景与关键决策因素"),
    ("增长策略", "构建获客、转化、留存与裂变的增长路径"),
    ("内容生成", "规划小红书、抖音与内容日历的执行方向"),
    ("营销素材生成", "为视频、海报与活动准备可复用的创作简报"),
    ("执行方案整理", "汇总为可以立即推进的运营行动清单"),
]

SECTION_TITLES = {
    "product_positioning": "产品定位分析",
    "user_persona": "用户画像",
    "competitive_landscape": "竞争环境",
    "xiaohongshu_plan": "小红书运营方案",
    "douyin_topics": "抖音短视频选题",
    "content_calendar": "内容日历",
    "growth_strategy": "用户增长策略",
    "campaign_plan": "活动策划方案",
}

ANALYSIS_KEYS = ("product_positioning", "user_persona", "competitive_landscape")
OPERATION_KEYS = (
    "xiaohongshu_plan",
    "douyin_topics",
    "content_calendar",
    "growth_strategy",
    "campaign_plan",
)

CREATIVE_WORKS = {
    "content_pack": {
        "label": "全渠道内容包",
        "icon": "package_2",
        "fields": {
            "xiaohongshu_content": "小红书内容",
            "short_video_script": "短视频脚本",
            "wechat_article_outline": "公众号文章框架",
            "marketing_copy": "营销推广文案",
        },
    },
    "xiaohongshu": {
        "label": "小红书运营内容",
        "icon": "auto_stories",
        "fields": {
            "viral_titles": "爆款标题（10条）",
            "body": "正文",
            "hashtags": "标签",
            "comment_scripts": "评论区运营话术",
        },
    },
    "douyin": {
        "label": "抖音运营脚本",
        "icon": "movie",
        "fields": {
            "script_30_seconds": "30 秒短视频脚本",
            "hook_3_seconds": "黄金 3 秒开头",
            "pain_points": "用户痛点表达",
            "conversion_copy": "转化话术",
        },
    },
    "video": {
        "label": "AI 短视频创作方案",
        "icon": "videocam",
        "fields": {
            "video_theme": "视频主题",
            "storyboard": "分镜脚本",
            "shot_design": "镜头设计",
            "voiceover": "配音文案",
            "bgm_suggestion": "BGM 建议",
        },
    },
    "poster": {
        "label": "营销海报设计方案",
        "icon": "imagesmode",
        "fields": {
            "poster_theme": "海报主题与主视觉",
            "visual_style": "视觉风格",
            "layout": "版式与信息层级",
            "copy": "海报文案",
            "image_prompt": "图片生成提示词",
        },
    },
    "campaign": {
        "label": "营销活动方案",
        "icon": "campaign",
        "fields": {
            "theme": "活动主题",
            "process": "活动流程",
            "budget": "预算建议",
            "roi_prediction": "ROI 预测口径",
        },
    },
}


SPECIALIST_AGENTS = {
    "growth_strategy": {
        "label": "增长策略 Agent",
        "icon": "trending_up",
        "fields": {
            "market_analysis": "市场分析",
            "user_pain_points": "用户痛点",
            "growth_opportunities": "增长机会",
            "marketing_strategy": "营销策略",
            "execution_plan": "执行计划",
        },
    },
    "user_insight": {
        "label": "用户洞察 Agent",
        "icon": "groups",
        "fields": {
            "user_persona": "用户画像",
            "buying_motivation": "购买动机",
            "user_needs": "用户需求",
            "consumption_scenarios": "消费场景",
        },
    },
    "content_operations": {
        "label": "内容运营 Agent",
        "icon": "auto_stories",
        "fields": {
            "xiaohongshu_strategy": "小红书运营方案",
            "wechat_article": "公众号文章方案",
            "video_topics": "短视频选题",
            "viral_structure": "爆款结构",
            "content_calendar": "内容日历",
        },
    },
    "video_creation": {
        "label": "视频创作 Agent",
        "icon": "videocam",
        "fields": {
            "topic_analysis": "选题分析",
            "video_script": "视频脚本",
            "storyboard_design": "分镜设计",
            "visual_description": "画面描述",
            "ai_video_prompt": "AI 视频生成 Prompt",
            "distribution_plan": "发布方案",
        },
    },
    "data_analysis": {
        "label": "数据分析 Agent",
        "icon": "analytics",
        "fields": {
            "data_trends": "数据趋势",
            "problem_analysis": "问题分析",
            "optimization_recommendations": "优化建议",
        },
    },
    "operations_review": {
        "label": "运营复盘 Agent",
        "icon": "fact_check",
        "fields": {
            "review_report": "复盘报告",
            "problem_summary": "问题总结",
            "next_step_plan": "下一步计划",
        },
    },
}


@dataclass(frozen=True)
class GrowthBrief:
    product_name: str
    product_intro: str
    industry: str
    target_user: str
    marketing_goal: str


@dataclass(frozen=True)
class AgentResult:
    sections: dict[str, str]
    elapsed_seconds: float
    provider_label: str

    @property
    def full_markdown(self) -> str:
        return "\n\n".join(
            f"# {SECTION_TITLES[key]}\n\n{self.sections[key]}" for key in SECTION_TITLES
        )


@dataclass(frozen=True)
class CreativeResult:
    work_type: str
    sections: dict[str, str]
    elapsed_seconds: float
    provider_label: str

    @property
    def label(self) -> str:
        return CREATIVE_WORKS[self.work_type]["label"]

    @property
    def full_markdown(self) -> str:
        fields = CREATIVE_WORKS[self.work_type]["fields"]
        body = "\n\n".join(
            f"## {title}\n\n{self.sections[key]}" for key, title in fields.items()
        )
        return f"# {self.label}\n\n{body}"


@dataclass(frozen=True)
class InsightResult:
    sections: dict[str, str]
    elapsed_seconds: float
    provider_label: str

    @property
    def full_markdown(self) -> str:
        return "\n\n".join(
            f"# {SECTION_TITLES[key]}\n\n{self.sections[key]}" for key in ANALYSIS_KEYS
        )


@dataclass(frozen=True)
class SpecialistResult:
    agent_type: str
    sections: dict[str, str]
    elapsed_seconds: float
    provider_label: str

    @property
    def label(self) -> str:
        return SPECIALIST_AGENTS[self.agent_type]["label"]

    @property
    def full_markdown(self) -> str:
        fields = SPECIALIST_AGENTS[self.agent_type]["fields"]
        body = "\n\n".join(
            f"## {title}\n\n{self.sections[key]}" for key, title in fields.items()
        )
        return f"# {self.label}\n\n{body}"


ANALYSIS_SYSTEM_PROMPT = """你是 GrowthPilot AI 的增长运营 Agent，服务中国市场的运营、市场、品牌和创业团队。
现在只执行「用户需求分析」阶段。请结合用户提供的产品、行业、目标用户和营销目标，返回严格 JSON 对象，且只返回 JSON：
{
  "product_positioning": "中文 Markdown：产品定位、核心价值、差异化、增长切入点",
  "user_persona": "中文 Markdown：核心人群、细分层次、使用场景、决策驱动、信任障碍",
  "competitive_landscape": "中文 Markdown：竞争与替代方案类型、竞争环境、可抢占机会、风险提示"
}
要求：内容具体、可验证。没有实时数据时，明确以「策略假设」表述，不能把没有证据的市场数字写成事实。"""

OPERATIONS_SYSTEM_PROMPT = """你是 GrowthPilot AI 的运营方案 Agent，服务中国市场的运营、市场、品牌和创业团队。
你会收到用户简报和上一阶段真实生成的需求分析。请以此生成完整的第二阶段运营方案，返回严格 JSON 对象，且只返回 JSON：
{
  "xiaohongshu_plan": "中文 Markdown：账号定位、内容支柱、选题方向、发布节奏、转化路径",
  "douyin_topics": "中文 Markdown：至少 8 个短视频选题，含切入角度、开头钩子和互动引导",
  "content_calendar": "中文 Markdown：7 天内容日历，写清日期、主题、形式、目的、CTA",
  "growth_strategy": "中文 Markdown：获客、转化、留存、裂变四个环节的动作与指标",
  "campaign_plan": "中文 Markdown：活动主题、参与机制、传播节奏、资源投入、风险控制、复盘指标"
}
要求：所有结论围绕用户的产品和营销目标，可直接执行；不要输出 JSON 之外的解释。"""


def _brief_prompt(brief: GrowthBrief) -> str:
    return f"""产品名称：{brief.product_name}
产品介绍：{brief.product_intro}
所在行业：{brief.industry}
目标用户：{brief.target_user}
营销目标：{brief.marketing_goal}"""


def _require_sections(payload: dict, expected_keys: tuple[str, ...] | dict[str, str]) -> dict[str, str]:
    keys = expected_keys.keys() if isinstance(expected_keys, dict) else expected_keys
    missing = [key for key in keys if not isinstance(payload.get(key), str) or not payload[key].strip()]
    if missing:
        raise RuntimeError(CONNECTION_ERROR_MESSAGE)
    return {key: payload[key].strip() for key in keys}


def _sections_to_markdown(sections: dict[str, str], titles: dict[str, str]) -> str:
    return "\n\n".join(f"## {titles[key]}\n{content}" for key, content in sections.items())


class GrowthAgent:
    """两阶段工作流：先做需求洞察，再根据洞察生成运营方案。"""

    def run(self, brief: GrowthBrief, on_step: Callable[[int], None] | None = None) -> AgentResult:
        config = load_deepseek_config()
        client = DeepSeekClient(config)
        started = perf_counter()

        if on_step:
            on_step(0)
        analysis = _require_sections(
            client.generate_json(ANALYSIS_SYSTEM_PROMPT, _brief_prompt(brief)), ANALYSIS_KEYS
        )

        for index in (1, 2, 3, 4):
            if on_step:
                on_step(index)
        operation_prompt = f"""{_brief_prompt(brief)}

第一阶段需求分析（必须作为本阶段方案依据）：
{_sections_to_markdown(analysis, SECTION_TITLES)}"""
        operations = _require_sections(
            client.generate_json(OPERATIONS_SYSTEM_PROMPT, operation_prompt), OPERATION_KEYS
        )

        if on_step:
            on_step(5)
        return AgentResult(
            sections={**analysis, **operations},
            elapsed_seconds=perf_counter() - started,
            provider_label=f"{config.label} · {config.model}",
        )


class InsightAgent:
    """只执行分析阶段，供用户洞察页使用。"""

    def run(self, brief: GrowthBrief) -> InsightResult:
        config = load_deepseek_config()
        started = perf_counter()
        payload = DeepSeekClient(config).generate_json(ANALYSIS_SYSTEM_PROMPT, _brief_prompt(brief))
        return InsightResult(
            sections=_require_sections(payload, ANALYSIS_KEYS),
            elapsed_seconds=perf_counter() - started,
            provider_label=f"{config.label} · {config.model}",
        )


class CreativeAgent:
    """基于业务简报和可选增长策略，直接生产渠道作品。"""

    def run(
        self,
        brief: GrowthBrief,
        work_type: str,
        strategy_context: AgentResult | None = None,
    ) -> CreativeResult:
        if work_type not in CREATIVE_WORKS:
            raise ValueError("不支持的作品类型")

        config = load_deepseek_config()
        started = perf_counter()
        work = CREATIVE_WORKS[work_type]
        fields: dict[str, str] = work["fields"]
        schema = ",\n  ".join(f'"{key}": "中文 Markdown：{title}"' for key, title in fields.items())
        context = ""
        if strategy_context:
            context = "\n\n可复用的增长策略上下文：\n" + strategy_context.full_markdown[:12000]

        system_prompt = f"""你是 GrowthPilot AI 的内容与活动生产 Agent。请为中国市场直接生成「{work['label']}」。
请只返回严格 JSON，不要输出任何 JSON 之外的说明：
{{
  {schema}
}}
要求：所有字段完整、可直接使用，符合中文互联网平台表达；内容必须与产品、行业、用户和营销目标一致。
若涉及预算、ROI 或预测，请写明测算前提，不能伪造已发生的数据。
特别要求：若输出「爆款标题（10条）」，必须提供恰好 10 条不同标题。"""
        if work_type == "content_pack":
            system_prompt += """
全渠道内容包额外要求：
1. 小红书内容必须包含 5 个标题、完整正文、标签和评论区互动引导。
2. 短视频脚本必须包含黄金 3 秒、30 秒脚本、镜头提示和转化话术。
3. 公众号文章框架必须包含标题、开场、三级结构、核心论点和结尾 CTA。
4. 营销推广文案必须同时提供朋友圈短文案、社群文案和一句话广告语。"""
        payload = DeepSeekClient(config).generate_json(system_prompt, _brief_prompt(brief) + context)
        return CreativeResult(
            work_type=work_type,
            sections=_require_sections(payload, fields),
            elapsed_seconds=perf_counter() - started,
            provider_label=f"{config.label} · {config.model}",
        )


class SpecialistAgent:
    """企业场景下的专业 Agent，统一复用当前模型中心的真实模型连接。"""

    def run(
        self,
        agent_type: str,
        brief: GrowthBrief,
        additional_context: str = "",
    ) -> SpecialistResult:
        if agent_type not in SPECIALIST_AGENTS:
            raise ValueError("不支持的专业 Agent 类型")

        config = load_deepseek_config()
        started = perf_counter()
        agent = SPECIALIST_AGENTS[agent_type]
        fields: dict[str, str] = agent["fields"]
        schema = ",\n  ".join(f'"{key}": "中文 Markdown：{title}"' for key, title in fields.items())
        system_prompt = f"""你是 GrowthPilot AI OS 中的「{agent['label']}」，服务企业运营、市场与品牌团队。
请根据业务简报和补充上下文产出专业、可执行、面向中国市场的方案。
只返回严格 JSON，不要包含 JSON 之外的解释：
{{
  {schema}
}}
要求：
1. 避免编造已发生的市场数据、销售数据或 ROI；需要估算时明确标记为策略假设。
2. 方案必须具有优先级、可执行动作和适合当前产品的表达。
3. 所有字段均需完整输出。"""
        prompt = _brief_prompt(brief)
        if additional_context.strip():
            prompt += "\n\n补充上下文：\n" + additional_context.strip()[:14000]
        payload = DeepSeekClient(config).generate_json(system_prompt, prompt)
        return SpecialistResult(
            agent_type=agent_type,
            sections=_require_sections(payload, fields),
            elapsed_seconds=perf_counter() - started,
            provider_label=f"{config.label} · {config.model}",
        )


def generate_growth_plan(brief: GrowthBrief, on_step: Callable[[int], None] | None = None) -> AgentResult:
    return GrowthAgent().run(brief, on_step)


def generate_user_insights(brief: GrowthBrief) -> InsightResult:
    return InsightAgent().run(brief)


def generate_creative_work(
    brief: GrowthBrief,
    work_type: str,
    strategy_context: AgentResult | None = None,
) -> CreativeResult:
    return CreativeAgent().run(brief, work_type, strategy_context)


def generate_specialist_agent(
    agent_type: str,
    brief: GrowthBrief,
    additional_context: str = "",
) -> SpecialistResult:
    return SpecialistAgent().run(agent_type, brief, additional_context)
