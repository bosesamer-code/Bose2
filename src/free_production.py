"""Free local production entry point with no external credentials."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.artifact_validator import ArtifactValidator
from src.free_media_providers import free_local_registry
from src.media_pipeline import MediaPipeline


def run_free_production(task_id: str, job_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    pipeline = MediaPipeline(free_local_registry())
    result = pipeline.run(task_id, job_root, inputs)
    validation = ArtifactValidator().validate(job_root, require_media=True)
    result["validation"] = validation
    result["publish_ready"] = result["status"] == "completed" and validation["status"] == "valid"
    return result
