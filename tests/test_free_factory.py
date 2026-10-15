from pathlib import Path
import shutil

import src.free_media_providers as media_providers
from src.free_factory import run_free_factory


def _disable_network_tts_for_unit_test(monkeypatch):
    real_which = shutil.which
    monkeypatch.setattr(
        media_providers.shutil, "which",
        lambda name: None if name == "edge-tts" else real_which(name),
    )


def test_free_factory_fails_closed_without_real_speech(tmp_path: Path, monkeypatch):
    _disable_network_tts_for_unit_test(monkeypatch)
    manifest = {
        "task_id": "factory-0001",
        "scene_plan": [
            {"scene": 1, "duration_seconds": 2, "purpose": "hook", "text": "Handmade lesson"},
            {"scene": 2, "duration_seconds": 2, "purpose": "lesson", "text": "First step"},
        ],
        "inputs": {"script": "Teach a handmade technique."},
    }

    result = run_free_factory(manifest, tmp_path)

    assert result["prepared"]["production_status"] == "prepared"
    assert result["publishing_gate"]["publish_allowed"] is False
    assert result["publishing_gate"]["reason"] == "artifact_validation_failed", result["publishing_gate"]
    assert result["production"]["publish_ready"] is False
    assert result["production"]["job_state"]["status"] == "failed"


def test_factory_creates_one_visual_per_scene_and_blocks_missing_speech(tmp_path: Path, monkeypatch):
    _disable_network_tts_for_unit_test(monkeypatch)
    manifest = {
        "task_id": "factory-scene-001",
        "scene_plan": [
            {"scene": 1, "duration_seconds": 2, "purpose": "hook", "text": "Hook"},
            {"scene": 2, "duration_seconds": 3, "purpose": "lesson", "text": "Lesson"},
            {"scene": 3, "duration_seconds": 2, "purpose": "cta", "text": "CTA"},
        ],
        "inputs": {"script": "A short handmade lesson."},
    }

    result = run_free_factory(manifest, tmp_path)
    assert result["production"]["publish_ready"] is False

    images = sorted((tmp_path / "factory-scene-001" / "images").glob("scene_*.ppm"))
    assert len(images) == 3


def test_egyptian_tts_retries_transient_failure_and_succeeds(tmp_path: Path, monkeypatch):
    import subprocess
    import src.free_media_providers as providers
    from src.media_providers import MediaRequest

    monkeypatch.setattr(providers.shutil, "which", lambda name: "/usr/bin/edge-tts")
    monkeypatch.setattr(providers.time, "sleep", lambda seconds: None)
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if len(calls) == 1:
            raise subprocess.CalledProcessError(
                1, command, stderr="temporary service connection failure"
            )
        output = Path(command[command.index("--write-media") + 1])
        output.write_bytes(b"x" * 2048)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(providers.subprocess, "run", fake_run)
    result = providers.FreeLocalAudioProvider().generate(
        MediaRequest("tts-retry", tmp_path, {"script": "تجربة صوت عربي"})
    )

    assert result.status == "completed"
    assert len(calls) == 2
    assert Path(result.artifacts[0]).name == "voice.mp3"
    assert Path(result.artifacts[0]).stat().st_size >= 1024


def test_egyptian_tts_reports_last_error_and_never_fakes_speech(tmp_path: Path, monkeypatch):
    import subprocess
    import src.free_media_providers as providers
    from src.media_providers import MediaRequest

    monkeypatch.setattr(providers.shutil, "which", lambda name: "/usr/bin/edge-tts")
    monkeypatch.setattr(providers.time, "sleep", lambda seconds: None)

    def fake_run(command, **kwargs):
        raise subprocess.CalledProcessError(
            1, command, stderr="service unavailable: temporary upstream error"
        )

    monkeypatch.setattr(providers.subprocess, "run", fake_run)
    result = providers.FreeLocalAudioProvider().generate(
        MediaRequest("tts-fail", tmp_path, {"script": "تجربة صوت عربي"})
    )

    assert result.status == "failed"
    assert "after 3 attempts" in result.error
    assert "service unavailable" in result.error
    assert result.artifacts == []
    assert not (tmp_path / "voice.mp3").exists()
