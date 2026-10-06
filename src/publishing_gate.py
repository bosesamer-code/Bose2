"""Human-controlled gate between production and external publishing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from artifact_validator import ArtifactValidator


class PublishingGate:
    def evaluate(self, job_root: Path, *, human_approved: bool = False) -> dict[str, Any]:
        validation = ArtifactValidator().validate(job_root, require_media=True)
        ready = validation["status"] == "valid"
        return {
            "validation": validation,
            "human_approved": human_approved,
            "status": "approved" if ready and human_approved else "blocked",
            "publish_allowed": ready and human_approved,
            "reason": None if ready and human_approved else (
                "human_approval_required" if ready else "artifact_validation_failed"
            ),
        }
