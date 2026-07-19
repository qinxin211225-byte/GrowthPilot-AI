"""GrowthPilot AI OS 的模型配置与密钥读取。"""

from __future__ import annotations

import os
from dataclasses import dataclass


DEEPSEEK_API_KEY = ""
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"


@dataclass(frozen=True)
class ModelProfile:
    model_id: str
    label: str
    provider: str
    base_url: str
    model: str
    api_key_env: str
    supports_openai_compatible: bool = True


MODEL_PROFILES: dict[str, ModelProfile] = {
    "deepseek": ModelProfile(
        model_id="deepseek",
        label="DeepSeek",
        provider="DeepSeek",
        base_url=DEEPSEEK_BASE_URL,
        model=DEEPSEEK_MODEL,
        api_key_env="DEEPSEEK_API_KEY",
    ),
    "openai": ModelProfile(
        model_id="openai",
        label="OpenAI",
        provider="OpenAI",
        base_url="https://api.openai.com/v1",
        model="gpt-4o-mini",
        api_key_env="OPENAI_API_KEY",
    ),
    "qwen": ModelProfile(
        model_id="qwen",
        label="通义千问（兼容模式）",
        provider="通义千问",
        base_url=os.getenv("QWEN_BASE_URL", ""),
        model=os.getenv("QWEN_MODEL", "qwen-plus"),
        api_key_env="QWEN_API_KEY",
    ),
    "custom": ModelProfile(
        model_id="custom",
        label="自定义兼容模型",
        provider="OpenAI Compatible",
        base_url=os.getenv("CUSTOM_LLM_BASE_URL", ""),
        model=os.getenv("CUSTOM_LLM_MODEL", ""),
        api_key_env="CUSTOM_LLM_API_KEY",
    ),
    "claude": ModelProfile(
        model_id="claude",
        label="Claude（Adapter 预留）",
        provider="Anthropic",
        base_url="",
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest"),
        api_key_env="ANTHROPIC_API_KEY",
        supports_openai_compatible=False,
    ),
}


def _get_secret(name: str, fallback: str = "") -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st

        return str(st.secrets.get(name, fallback)).strip()
    except Exception:
        return fallback.strip()


def get_deepseek_api_key() -> str:
    return _get_secret("DEEPSEEK_API_KEY", DEEPSEEK_API_KEY)


def get_model_profile(model_id: str, overrides: dict[str, str] | None = None) -> ModelProfile:
    profile = MODEL_PROFILES.get(model_id, MODEL_PROFILES["deepseek"])
    overrides = overrides or {}
    if profile.model_id != "custom":
        return profile
    return ModelProfile(
        model_id="custom",
        label="自定义兼容模型",
        provider="OpenAI Compatible",
        base_url=overrides.get("base_url", profile.base_url).strip(),
        model=overrides.get("model", profile.model).strip(),
        api_key_env="CUSTOM_LLM_API_KEY",
    )


def get_model_api_key(profile: ModelProfile) -> str:
    fallback = DEEPSEEK_API_KEY if profile.model_id == "deepseek" else ""
    return _get_secret(profile.api_key_env, fallback)


def get_model_catalog() -> list[dict[str, str | bool]]:
    return [
        {
            "model_id": profile.model_id,
            "名称": profile.label,
            "服务商": profile.provider,
            "默认模型": profile.model or "需配置",
            "调用方式": "OpenAI Compatible" if profile.supports_openai_compatible else "专属 Adapter",
            "已配置密钥": bool(get_model_api_key(profile)),
        }
        for profile in MODEL_PROFILES.values()
    ]
