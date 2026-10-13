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
    assert result["publishing_gate"]["reason"] == "human_approval_required", result["publishing_gate"]
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
