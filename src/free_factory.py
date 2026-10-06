"""End-to-end free factory orchestration up to the human publishing gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from free_production import run_free_production
from production_runner import ProductionRunner
from publishing_gate import PublishingGate


def run_free_factory(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    prepared = ProductionRunner(root).run(manifest)
    job_root = root / str(manifest["task_id"])
    production = run_free_production(
        str(manifest["task_id"]),
        job_root,
        manifest["inputs"],
    )
    gate = PublishingGate().evaluate(job_root, human_approved=False)
    return {
        "task_id": manifest["task_id"],
        "prepared": prepared,
        "production": production,
        "publishing_gate": gate,
    }
