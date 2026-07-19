"""OpenAI Compatible 的通用模型调用层，默认使用 DeepSeek。"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from openai import APIConnectionError, APIError, AuthenticationError, OpenAI, RateLimitError

from config import ModelProfile, get_model_api_key, get_model_profile


CONNECTION_ERROR_MESSAGE = "AI连接失败，请检查API Key、Base URL 或网络连接。"
MODEL_ADAPTER_MESSAGE = "当前模型需要专属 Adapter，请在模型管理中心选择已配置的兼容模型。"
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMConfig:
    model_id: str
    label: str
    provider: str
    api_key: str
    base_url: str
    model: str
    supports_openai_compatible: bool

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.base_url and self.model and self.supports_openai_compatible)


DeepSeekConfig = LLMConfig


def _read_active_selection() -> tuple[str, dict[str, str]]:
    try:
        import streamlit as st

        return (
            str(st.session_state.get("active_model_id", "deepseek")),
            dict(st.session_state.get("model_overrides", {})),
        )
    except Exception:
        return "deepseek", {}


def _to_config(profile: ModelProfile) -> LLMConfig:
    return LLMConfig(
        model_id=profile.model_id,
        label=profile.label,
        provider=profile.provider,
        api_key=get_model_api_key(profile),
        base_url=profile.base_url.rstrip("/"),
        model=profile.model,
        supports_openai_compatible=profile.supports_openai_compatible,
    )


def load_active_model_config() -> LLMConfig:
    model_id, overrides = _read_active_selection()
    return _to_config(get_model_profile(model_id, overrides))


def load_deepseek_config() -> LLMConfig:
    """兼容旧调用名；实际返回当前模型中心选择的配置。"""
    return load_active_model_config()


class OpenAICompatibleClient:
    """统一调用 DeepSeek、OpenAI 与其他兼容 Chat Completions 的服务。"""

    def __init__(self, config: LLMConfig) -> None:
        if not config.supports_openai_compatible:
            raise RuntimeError(MODEL_ADAPTER_MESSAGE)
        if not config.is_configured:
            raise RuntimeError(CONNECTION_ERROR_MESSAGE)
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url, timeout=90.0)

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                temperature=0.7,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except (AuthenticationError, RateLimitError, APIConnectionError, APIError) as exc:
            logger.warning("LLM request failed: provider=%s error=%s", self.config.provider, type(exc).__name__)
            raise RuntimeError(CONNECTION_ERROR_MESSAGE) from exc

        content = response.choices[0].message.content or "{}"
        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.warning("LLM returned invalid JSON: provider=%s", self.config.provider)
            raise RuntimeError(CONNECTION_ERROR_MESSAGE) from exc
        logger.info("LLM request succeeded: provider=%s model=%s", self.config.provider, self.config.model)
        return result


DeepSeekClient = OpenAICompatibleClient
