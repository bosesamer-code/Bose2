from pathlib import Path

from src.free_factory import run_free_factory


def test_free_factory_stops_at_human_gate(tmp_path: Path):
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
    assert result["production"]["publish_ready"] is True
    assert result["production"]["job_state"]["status"] == "ready"


def test_factory_creates_one_visual_per_scene(tmp_path: Path):
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
    assert result["production"]["validation"]["status"] == "valid", result["production"]["validation"]

    images = sorted((tmp_path / "factory-scene-001" / "images").glob("scene_*.ppm"))
    assert len(images) == 3
