"""Safety tests for publishing scripts: explicit consent is mandatory."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run_script(script: str, confirmation_name: str, confirmation_value: str | None):
    env = os.environ.copy()
    env.pop(confirmation_name, None)
    if confirmation_value is not None:
        env[confirmation_name] = confirmation_value
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), "missing.mp4", "missing-package.json"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_youtube_upload_refuses_without_explicit_confirmation():
    result = _run_script("publish_youtube.py", "YOUTUBE_UPLOAD_CONFIRMATION", None)
    assert result.returncode != 0
    assert "explicit one-video private-upload confirmation" in result.stderr


def test_youtube_confirmation_still_checks_local_video_before_network():
    result = _run_script(
        "publish_youtube.py",
        "YOUTUBE_UPLOAD_CONFIRMATION",
        "UPLOAD_ONE_PRIVATE_TEST_VIDEO",
    )
    assert result.returncode != 0
    assert "Video file is missing or empty" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr


def test_facebook_upload_refuses_without_explicit_confirmation():
    result = _run_script("publish_facebook.py", "FACEBOOK_PUBLISH_CONFIRMATION", None)
    assert result.returncode != 0
    assert "explicit Facebook Page publication confirmation" in result.stderr


def test_facebook_confirmation_still_checks_local_video_before_network():
    result = _run_script(
        "publish_facebook.py",
        "FACEBOOK_PUBLISH_CONFIRMATION",
        "I_APPROVE_FACEBOOK_PAGE_PUBLICATION",
    )
    assert result.returncode != 0
    assert "Video is missing, empty, or not an MP4" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr
