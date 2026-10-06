"""Free local production entry point with no external credentials."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.artifact_validator import ArtifactValidator
from src.free_media_providers import free_local_registry
from src.job_state import ProductionJob
from src.media_pipeline import MediaPipeline


def _persist(job: ProductionJob, state_path: Path) -> None:
    state_path.write_text(
        json.dumps(job.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_free_production(task_id: str, job_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    job_root.mkdir(parents=True, exist_ok=True)
    state_path = job_root / "job_state.json"
    if state_path.exists():
        job = ProductionJob.from_dict(json.loads(state_path.read_text(encoding="utf-8")))
    else:
        job = ProductionJob(task_id)
    job.transition("producing")
    _persist(job, state_path)

    pipeline = MediaPipeline(free_local_registry())
    result = pipeline.run(task_id, job_root, inputs)
    validation = ArtifactValidator().validate(job_root, require_media=True)
    result["validation"] = validation
    result["publish_ready"] = (
        result["status"] == "completed" and validation["status"] == "valid"
    )

    job.transition("validating")
    if result["publish_ready"]:
        job.transition("ready")
    else:
        job.transition("failed", validation.get("reason") or "media_production_incomplete")
    _persist(job, state_path)
    result["job_state"] = job.to_dict()
    return result
