"""End-to-end free factory orchestration up to the human publishing gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.free_production import run_free_production
from src.production_runner import ProductionRunner
from src.publishing_gate import PublishingGate


def _factory_contract(manifest: dict[str, Any]) -> dict[str, Any]:\n    """Build the public production contract for the free-factory entry point."""\n    return {\n        "contract_version": 1,\n        "task_id": str(contract["task_id"]),\n        "production_status": "ready_for_public_factory",\n        "permissions": {\n            "produce_media": True,\n            "publish": False,\n            "access_private_core": False,\n        },\n        "inputs": dict(manifest.get("inputs", {})),\n        "scene_plan": list(manifest.get("scene_plan", [])),\n        "validation_requirements": ["required_artifact_directories", "media_presence"],\n    }\n\ndef run_free_factory(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    contract = _factory_contract(manifest)\n    prepared = ProductionRunner(root).run(contract)
    job_root = root / str(manifest["task_id"])
    production = run_free_production(
        str(manifest["task_id"]),
        job_root,
        contract["inputs"],
    )
    gate = PublishingGate().evaluate(job_root, human_approved=False)
    return {
        "task_id": manifest["task_id"],
        "prepared": prepared,
        "production": production,
        "publishing_gate": gate,
    }
