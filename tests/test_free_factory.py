from pathlib import Path

from src.free_factory import run_free_factory


def test_free_factory_stops_at_human_gate(tmp_path: Path):
    manifest = {
        "task_id": "factory-0001",
        "scene_plan": [{"scene": 1, "text": "Handmade lesson"}],
        "inputs": {"script": "Teach a handmade technique."},
    }

    result = run_free_factory(manifest, tmp_path)

    assert result["prepared"]["production_status"] == "prepared"
    assert result["publishing_gate"]["publish_allowed"] is False
    assert result["publishing_gate"]["reason"] == "human_approval_required"
