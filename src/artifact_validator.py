"""Validate public production artifacts before they can leave the factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any


REQUIRED_ARTIFACT_DIRS = ("audio", "images", "designs", "video", "thumbnail")


class ArtifactValidator:
    def validate(self, job_root: Path, *, require_media: bool = False) -> dict[str, Any]:
        missing = [
            name for name in REQUIRED_ARTIFACT_DIRS
            if not (job_root / name).is_dir()
        ]

        files = {
            name: sorted(str(path.relative_to(job_root)) for path in (job_root / name).glob("**/*") if path.is_file())
            for name in REQUIRED_ARTIFACT_DIRS
            if (job_root / name).is_dir()
        }

        media_present = any(files.get(name) for name in REQUIRED_ARTIFACT_DIRS)
        if require_media and not media_present:
            return {
                "status": "failed",
                "reason": "no_media_artifacts",
                "missing_directories": missing,
                "files": files,
            }

        return {
            "status": "valid" if not missing else "incomplete",
            "reason": None if not missing else "missing_artifact_directories",
            "missing_directories": missing,
            "files": files,
        }
