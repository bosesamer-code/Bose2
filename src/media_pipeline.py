"""Run provider-neutral media generation for a production job."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from media_providers import MediaRequest, ProviderRegistry, default_registry


class MediaPipeline:
    MEDIA_TYPES = ("audio", "image", "design", "video", "thumbnail")

    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self.registry = registry or default_registry()

    def run(self, task_id: str, job_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        payload = dict(inputs)

        for media_type in self.MEDIA_TYPES:
            provider = self.registry.get(media_type)
            result = provider.generate(
                MediaRequest(
                    task_id=task_id,
                    output_dir=job_root / self._directory(media_type),
                    payload=payload,
                )
            )
            results.append(
                {
                    "provider": result.provider,
                    "media_type": result.media_type,
                    "status": result.status,
                    "artifacts": result.artifacts,
                    "error": result.error,
                }
            )
            if result.artifacts:
                payload[f"{media_type}_path"] = result.artifacts[0]

        ready = all(item["status"] == "completed" for item in results)
        return {
            "task_id": task_id,
            "status": "completed" if ready else "waiting_for_providers",
            "providers": results,
        }

    @staticmethod
    def _directory(media_type: str) -> str:
        return {
            "audio": "audio",
            "image": "images",
            "design": "designs",
            "video": "video",
            "thumbnail": "thumbnail",
        }[media_type]
