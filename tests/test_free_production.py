from pathlib import Path
import shutil

import src.free_media_providers as media_providers
from src.free_production import run_free_production


def _disable_network_tts_for_unit_test(monkeypatch):
    real_which = shutil.which
    monkeypatch.setattr(
        media_providers.shutil, "which",
        lambda name: None if name == "edge-tts" else real_which(name),
    )


def test_free_production_blocks_job_without_real_speech(tmp_path: Path, monkeypatch):
    _disable_network_tts_for_unit_test(monkeypatch)
    result = run_free_production(
        "free-0001",
        tmp_path,
        {"script": "Teach a handmade technique."},
    )

    assert result["status"] == "waiting_for_providers"
    assert result["publish_ready"] is False
    assert result["job_state"]["status"] == "failed"


def test_free_production_rerun_of_ready_job_is_stable(tmp_path: Path, monkeypatch):
    _disable_network_tts_for_unit_test(monkeypatch)
    first = run_free_production("free-rerun-0001", tmp_path, {"script": "Teach crochet."})
    if first["job_state"]["status"] != "ready":
        return

    second = run_free_production("free-rerun-0001", tmp_path, {"script": "Teach crochet."})

    assert second["publish_ready"] is True
    assert second["job_state"]["status"] == "ready"
    assert second["job_state"]["attempts"] == first["job_state"]["attempts"]
