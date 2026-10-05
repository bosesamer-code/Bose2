from pathlib import Path

from src.media_pipeline import MediaPipeline


def test_default_pipeline_is_safe_without_external_providers(tmp_path: Path):
    result = MediaPipeline().run(
        "video-0006",
        tmp_path,
        {"script": "Teach a handmade technique."},
    )

    assert result["status"] == "waiting_for_providers"
    assert len(result["providers"]) == 5
    assert all(item["status"] == "not_configured" for item in result["providers"])
