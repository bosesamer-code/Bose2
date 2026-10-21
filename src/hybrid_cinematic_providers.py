"""Optional no-GPU cinematic montage: local footage + Egyptian Arabic TTS + FFmpeg.

This provider path never downloads footage or publishes content. Operators supply
clips they own or have permission to use; the default factory stays unchanged.
"""
from __future__ import annotations

from src.free_media_providers import (
    FreeLocalAudioProvider,
    FreeLocalDesignProvider,
    FreeLocalImageProvider,
    FreeLocalThumbnailProvider,
)
from src.media_providers import MediaRequest, MediaResult, ProviderRegistry
from src.real_footage_providers import RecordedAudioProvider, RealFootageVideoProvider


class HybridNarrationProvider:
    """Prefer supplied MP3 narration; otherwise synthesize Egyptian Arabic from script."""

    name = "hybrid-free-narration"
    media_type = "audio"

    def __init__(self) -> None:
        self.recorded = RecordedAudioProvider()
        self.tts = FreeLocalAudioProvider()

    def generate(self, request: MediaRequest) -> MediaResult:
        if str(request.payload.get("recorded_audio_path", "")).strip():
            return self.recorded.generate(request)
        return self.tts.generate(request)


def hybrid_cinematic_registry() -> ProviderRegistry:
    """Build an opt-in no-GPU montage registry without changing default providers."""
    registry = ProviderRegistry()
    registry.register(HybridNarrationProvider())
    registry.register(FreeLocalImageProvider())
    registry.register(FreeLocalDesignProvider())
    registry.register(RealFootageVideoProvider())
    registry.register(FreeLocalThumbnailProvider())
    return registry
