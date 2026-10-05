"""Prepare a production job from a validated private-core manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.job_state import ProductionJob
from src.production_contract import validate_contract


class ProductionRunner:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("production")

    def run(self, manifest: dict[str, Any]) -> dict[str, Any]:
        ok, errors = validate_contract(manifest)
        if not ok:
            raise ValueError(";".join(errors))

        task_id = str(manifest["task_id"])
        job = ProductionJob(task_id)
        job.transition("producing")
        job_root = self.root / task_id

        for name in ("audio", "images", "designs", "video", "thumbnail"):
            (job_root / name).mkdir(parents=True, exist_ok=True)

        self._write_json(job_root / "manifest.json", manifest)
        self._write_json(job_root / "scene_manifest.json", {
            "task_id": task_id,
            "scenes": manifest["scene_plan"],
        })
        self._write_json(job_root / "script.json", {
            "task_id": task_id,
            "script": manifest["inputs"]["script"],
        })
        self._write_json(job_root / "job_state.json", job.to_dict())

        return {
            "task_id": task_id,
            "production_status": "producing",
            "job_path": str(job_root),
            "job_state": job.to_dict(),
            "artifact_directories": [str(job_root / name) for name in (
                "audio", "images", "designs", "video", "thumbnail"
            )],
            "next_step": "run_media_providers",
        }

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
