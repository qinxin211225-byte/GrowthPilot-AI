"""视频和图片模型的可替换接口层。

本模块不会伪造媒体文件。未配置 Provider 时，只返回透明的接入状态和请求结构；
接入真实 SDK 后，只需在对应 Adapter 的 submit 方法实现调用即可。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


MediaType = Literal["video", "image"]


@dataclass(frozen=True)
class MediaProvider:
    name: str
    env_key: str
    supports: tuple[MediaType, ...]


MEDIA_PROVIDERS: dict[str, MediaProvider] = {
    "Runway": MediaProvider("Runway", "RUNWAY_API_KEY", ("video",)),
    "可灵AI": MediaProvider("可灵AI", "KLING_API_KEY", ("video", "image")),
    "即梦AI": MediaProvider("即梦AI", "JIMENG_API_KEY", ("video", "image")),
    "通义万相": MediaProvider("通义万相", "TONGYI_WANXIANG_API_KEY", ("video", "image")),
}


@dataclass(frozen=True)
class MediaGenerationRequest:
    media_type: MediaType
    provider: str
    prompt: str
    style: str
    aspect_ratio: str


@dataclass(frozen=True)
class MediaGenerationJob:
    request: MediaGenerationRequest
    status: str
    message: str

    @property
    def full_markdown(self) -> str:
        return "\n\n".join(
            [
                f"# {self.request.media_type == 'video' and '视频' or '图片'}生成接口任务",
                f"- **Provider**：{self.request.provider}",
                f"- **状态**：{self.status}",
                f"- **画幅**：{self.request.aspect_ratio}",
                f"- **风格**：{self.request.style}",
                "## 提示词\n\n" + self.request.prompt,
                "## 接入说明\n\n" + self.message,
            ]
        )


class BaseMediaAdapter:
    """Provider Adapter 的统一扩展点。"""

    def __init__(self, provider: MediaProvider) -> None:
        self.provider = provider

    def submit(self, request: MediaGenerationRequest) -> MediaGenerationJob:
        api_key = os.getenv(self.provider.env_key, "").strip()
        if not api_key:
            return MediaGenerationJob(
                request=request,
                status="等待配置",
                message=(
                    f"未检测到 {self.provider.env_key}。请在部署平台或本机环境变量中配置该密钥后，"
                    "再在对应 Adapter 中接入 Provider 的正式 SDK/API。当前没有创建或伪造媒体文件。"
                ),
            )
        return MediaGenerationJob(
            request=request,
            status="等待适配",
            message=(
                f"已检测到 {self.provider.env_key}，但当前版本尚未实现 {self.provider.name} 的专属请求适配器。"
                "请在 services/media_clients.py 的 Adapter 中按该 Provider 文档实现 submit 方法后再启用真实生成。"
            ),
        )


def supported_provider_names(media_type: MediaType) -> list[str]:
    return [provider.name for provider in MEDIA_PROVIDERS.values() if media_type in provider.supports]


def create_media_job(
    media_type: MediaType,
    provider_name: str,
    prompt: str,
    style: str,
    aspect_ratio: str,
) -> MediaGenerationJob:
    provider = MEDIA_PROVIDERS.get(provider_name)
    if provider is None or media_type not in provider.supports:
        raise ValueError("所选 Provider 不支持当前媒体类型")
    request = MediaGenerationRequest(
        media_type=media_type,
        provider=provider.name,
        prompt=prompt.strip(),
        style=style.strip(),
        aspect_ratio=aspect_ratio,
    )
    return BaseMediaAdapter(provider).submit(request)
