"""End-to-end free factory orchestration up to the human publishing gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.free_production import run_free_production
from src.production_runner import ProductionRunner
from src.publishing_gate import PublishingGate


def _factory_contract(manifest: dict[str, Any]) -> dict[str, Any]:
    """Build the public production contract for the free-factory entry point."""
    scene_plan = list(manifest.get("scene_plan", []))
    duration_seconds = sum(int(scene.get("duration_seconds", 0)) for scene in scene_plan)
    return {
        "contract_version": 1,
        "task_id": str(manifest["task_id"]),
        "production_status": "ready_for_public_factory",
        "permissions": {
            "produce_media": True,
            "publish": False,
            "access_private_core": False,
        },
        "inputs": {
            **dict(manifest.get("inputs", {})),
            "duration_seconds": duration_seconds,
            "scene_plan": scene_plan,
        },
        "scene_plan": scene_plan,
        "validation_requirements": [
            "required_artifact_directories",
            "media_presence",
        ],
    }


def run_free_factory(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    contract = _factory_contract(manifest)
    prepared = ProductionRunner(root).run(contract)
    job_root = root / str(contract["task_id"])
    production = run_free_production(
        str(contract["task_id"]),
        job_root,
        contract["inputs"],
    )
    gate = PublishingGate().evaluate(job_root, human_approved=False)
    return {
        "task_id": contract["task_id"],
        "prepared": prepared,
        "production": production,
        "publishing_gate": gate,
    }
