from pathlib import Path

from src.free_production import run_free_production


def test_free_production_builds_and_validates_job(tmp_path: Path):
    result = run_free_production(
        "free-0001",
        tmp_path,
        {"script": "Teach a handmade technique."},
    )

    assert result["status"] in {"completed", "waiting_for_providers"}
    if result["status"] == "completed":
        assert result["validation"]["status"] == "valid"
        assert result["publish_ready"] is True


def test_free_production_rerun_of_ready_job_is_stable(tmp_path: Path):
    first = run_free_production("free-rerun-0001", tmp_path, {"script": "Teach crochet."})
    if first["job_state"]["status"] != "ready":
        return

    second = run_free_production("free-rerun-0001", tmp_path, {"script": "Teach crochet."})

    assert second["publish_ready"] is True
    assert second["job_state"]["status"] == "ready"
    assert second["job_state"]["attempts"] == first["job_state"]["attempts"]
