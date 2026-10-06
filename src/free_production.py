"""Free local production entry point with no external credentials."""

from __future__ import annotations

from pathlib import Path
from typing import Any\nimport json\n\nfrom src.job_state import ProductionJob

from src.artifact_validator import ArtifactValidator
from src.free_media_providers import free_local_registry
from src.media_pipeline import MediaPipeline


def run_free_production(task_id: str, job_root: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    state_path = job_root / "job_state.json"\n    job = ProductionJob.from_dict(json.loads(state_path.read_text(encoding="utf-8")))\n    job.transition("producing")\n    state_path.write_text(json.dumps(job.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")\n\n    pipeline = MediaPipeline(free_local_registry())
    result = pipeline.run(task_id, job_root, inputs)
    validation = ArtifactValidator().validate(job_root, require_media=True)
    result["validation"] = validation
    result["publish_ready"] = result["status"] == "completed" and validation["status"] == "valid"
    return result
