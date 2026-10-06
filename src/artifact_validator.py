"""Validate public production artifacts before they can leave the factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any


REQUIRED_ARTIFACT_DIRS = ("audio", "images", "designs", "video", "thumbnail")
REQUIRED_MEDIA_TYPES = ("audio", "images", "designs", "video", "thumbnail")\nALLOWED_EXTENSIONS = {\n    "audio": {".wav", ".mp3", ".m4a", ".ogg"},\n    "images": {".ppm", ".png", ".jpg", ".jpeg", ".webp"},\n    "designs": {".ppm", ".png", ".jpg", ".jpeg", ".webp"},\n    "video": {".mp4", ".webm", ".mov"},\n    "thumbnail": {".ppm", ".png", ".jpg", ".jpeg", ".webp"},\n}


class ArtifactValidator:
    def validate(self, job_root: Path, *, require_media: bool = False) -> dict[str, Any]:
        missing = [name for name in REQUIRED_ARTIFACT_DIRS if not (job_root / name).is_dir()]
        files = {
            name: sorted(str(path.relative_to(job_root)) for path in (job_root / name).glob("**/*") if path.is_file())
            for name in REQUIRED_ARTIFACT_DIRS
            if (job_root / name).is_dir()
        }
        empty_media_dirs = [name for name in REQUIRED_MEDIA_TYPES if not files.get(name)]\n        invalid_media = {}\n        for name in REQUIRED_MEDIA_TYPES:\n            invalid = []\n            for relative in files.get(name, []):\n                path = job_root / relative\n                if path.suffix.lower() not in ALLOWED_EXTENSIONS[name] or path.stat().st_size == 0:\n                    invalid.append(relative)\n            if invalid:\n                invalid_media[name] = invalid
        if require_media and (empty_media_dirs or invalid_media):
            return {
                "status": "failed",
                "reason": "invalid_or_missing_media_artifacts",
                "missing_directories": missing,
                "empty_media_directories": empty_media_dirs,
                "files": files,
            }
        return {
            "status": "valid" if not missing else "incomplete",
            "reason": None if not missing else "missing_artifact_directories",
            "missing_directories": missing,
            "empty_media_directories": empty_media_dirs,
            "files": files,
        }
