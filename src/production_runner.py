"""Public media production runner.

Consumes a safe production manifest and prepares deterministic media artifacts.
External AI/media providers are intentionally not embedded here; provider adapters
can be added later without exposing private-core secrets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProductionRunner:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("production")

    def run(self, manifest: dict[str, Any]) -> dict[str, Any]:
        self._validate_manifest(manifest)

        task_id = manifest["task_id"]
        job_root = self.root / task_id

        directories = [
            "audio",
            "images",
            "designs",
            "video",
            "thumbnail",
        ]
        for directory in directories:
            (job_root / directory).mkdir(parents=True, exist_ok=True)

        self._write_json(job_root / "manifest.json", manifest)
        self._write_json(
            job_root / "scene_manifest.json",
            {
                "task_id": task_id,
                "scenes": manifest["scene_plan"],
            },
        )
        self._write_json(
            job_root / "script.json",
            {
                "task_id": task_id,
                "script": manifest["inputs"]["script"],
            },
        )

        return {
            "task_id": task_id,
            "production_status": "prepared",
            "job_path": str(job_root),
            "artifact_directories": directories,
            "next_step": "run_media_providers",
        }

    def _validate_manifest(self, manifest: dict[str, Any]) -> None:
        if manifest.get("contract_version") != 1:
            raise ValueError("Unsupported production contract version.")

        if manifest.get("production_status") != "ready_for_public_factory":
            raise ValueError("Manifest is not ready for public production.")

        permissions = manifest.get("permissions", {})
        if permissions.get("publish") is not False:
            raise ValueError("Public production cannot receive publishing permission.")
        if permissions.get("access_private_core") is not False:
            raise ValueError("Public production cannot receive private-core access.")

        if not manifest.get("task_id"):
            raise ValueError("task_id is required.")

        inputs = manifest.get("inputs", {})
        if not inputs.get("script"):
            raise ValueError("A script is required.")

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
