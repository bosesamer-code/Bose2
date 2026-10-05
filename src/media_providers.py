"""Provider-neutral interfaces for audio, image/design, and video production."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass
class MediaRequest:
    task_id: str
    output_dir: Path
    payload: dict[str, Any]


@dataclass
class MediaResult:
    provider: str
    media_type: str
    status: str
    artifacts: list[str]
    error: str | None = None


class MediaProvider(Protocol):
    name: str
    media_type: str

    def generate(self, request: MediaRequest) -> MediaResult:
        ...


class StubMediaProvider:
    """Safe local placeholder used until a real provider is configured."""

    def __init__(self, name: str, media_type: str) -> None:
        self.name = name
        self.media_type = media_type

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        return MediaResult(
            provider=self.name,
            media_type=self.media_type,
            status="not_configured",
            artifacts=[],
            error="No external media provider is configured.",
        )


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, MediaProvider] = {}

    def register(self, provider: MediaProvider) -> None:
        self._providers[provider.media_type] = provider

    def get(self, media_type: str) -> MediaProvider:
        try:
            return self._providers[media_type]
        except KeyError as exc:
            raise KeyError(f"No provider registered for media type: {media_type}") from exc

    def media_types(self) -> list[str]:
        return sorted(self._providers)


def default_registry() -> ProviderRegistry:
    registry = ProviderRegistry()
    registry.register(StubMediaProvider("local-placeholder", "audio"))
    registry.register(StubMediaProvider("local-placeholder", "image"))
    registry.register(StubMediaProvider("local-placeholder", "design"))
    registry.register(StubMediaProvider("local-placeholder", "video"))
    registry.register(StubMediaProvider("local-placeholder", "thumbnail"))
    return registry
