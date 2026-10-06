"""Validate public production artifacts before they can be published."""

from __future__ import annotations

from pathlib import Path
from typing import Any

REQUIRED_ARTIFACT_DIRS = ("audio", "images", "designs", "video", "thumbnail")
REQUIRED_MEDIA_TYPES = REQUIRED_ARTIFACT_DIRS
ALLOWED_EXTENSIONS = {
    "audio": {".wav", ".mp3", ".m4a", ".ogg"},
    "images": {".ppm", ".png", ".jpg", ".jpeg", ".webp"},
    "designs": {".ppm", ".png", ".jpg", ".jpeg", ".webp"},
    "video": {".mp4", ".webm", ".mov"},
    "thumbnail": {".ppm", ".png", ".jpg", ".jpeg", ".webp"},
}


class ArtifactValidator:
    def validate(self, job_root: Path, *, require_media: bool = False) -> dict[str, Any]:
        missing = [name for name in REQUIRED_ARTIFACT_DIRS if not (job_root / name).is_dir()]
        files = {
            name: sorted(
                str(path.relative_to(job_root))
                for path in (job_root / name).glob("**/*")
                if path.is_file()
            )
            for name in REQUIRED_ARTIFACT_DIRS
            if (job_root / name).is_dir()
        }
        empty_media_dirs = [name for name in REQUIRED_MEDIA_TYPES if not files.get(name)]
        invalid_media: dict[str, list[str]] = {}
        for name in REQUIRED_MEDIA_TYPES:
            invalid = []
            for relative in files.get(name, []):
                path = job_root / relative
                if path.suffix.lower() not in ALLOWED_EXTENSIONS[name] or path.stat().st_size == 0:
                    invalid.append(relative)
            if invalid:
                invalid_media[name] = invalid

        if require_media and (missing or empty_media_dirs or invalid_media):
            return {
                "status": "failed",
                "reason": "invalid_or_missing_media_artifacts",
                "missing_directories": missing,
                "empty_media_directories": empty_media_dirs,
                "invalid_media_files": invalid_media,
                "files": files,
            }
        return {
            "status": "valid" if not missing and not invalid_media else "incomplete",
            "reason": None if not missing and not invalid_media else "invalid_or_missing_artifacts",
            "missing_directories": missing,
            "empty_media_directories": empty_media_dirs,
            "invalid_media_files": invalid_media,
            "files": files,
        }
