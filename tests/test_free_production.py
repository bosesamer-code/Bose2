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
