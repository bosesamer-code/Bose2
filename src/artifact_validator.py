"""Validate public production artifacts before they can be published."""

from __future__ import annotations

import shutil
import subprocess
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


def _valid_image(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            header = handle.read(2)
        if path.suffix.lower() == ".ppm":
            return header in {b"P3", b"P6"}
        return header == b"\\x89P" or header == b"\\xff\\xd8" or header == b"RI"
    except OSError:
        return False


def _probe_media(path: Path) -> bool:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return False
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0 and bool(result.stdout.strip())


class ArtifactValidator:
    def validate(self, job_root: Path, *, require_media: bool = False) -> dict[str, Any]:
        missing = [name for name in REQUIRED_ARTIFACT_DIRS if not (job_root / name).is_dir()]
        files = {
            name: sorted(str(path.relative_to(job_root)) for path in (job_root / name).glob("**/*") if path.is_file())
            for name in REQUIRED_ARTIFACT_DIRS
            if (job_root / name).is_dir()
        }
        empty_media_dirs = [name for name in REQUIRED_MEDIA_TYPES if not files.get(name)]
        invalid_media: dict[str, list[str]] = {}
        for name in REQUIRED_MEDIA_TYPES:
            for relative in files.get(name, []):
                path = job_root / relative
                valid_extension = path.suffix.lower() in ALLOWED_EXTENSIONS[name]
                if path.stat().st_size == 0 or not valid_extension:
                    invalid_media.setdefault(name, []).append(relative)
                    continue
                valid = _valid_image(path) if name in {"images", "designs", "thumbnail"} else _probe_media(path)
                if not valid:
                    invalid_media.setdefault(name, []).append(relative)

        failed = bool(missing or empty_media_dirs or invalid_media)
        if require_media and failed:
            status, reason = "failed", "invalid_or_missing_media_artifacts"
        else:
            status = "incomplete" if missing or invalid_media else "valid"
            reason = None if status == "valid" else "invalid_or_missing_artifacts"
        return {
            "status": status,
            "reason": reason,
            "missing_directories": missing,
            "empty_media_directories": empty_media_dirs,
            "invalid_media_files": invalid_media,
            "files": files,
        }
"