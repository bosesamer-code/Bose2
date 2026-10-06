from pathlib import Path

from src.publishing_gate import PublishingGate


def complete_job(root: Path) -> None:
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        directory = root / name
        directory.mkdir()
        (directory / {"audio": "voice.wav", "images": "scene.ppm", "designs": "design.ppm", "video": "video.mp4", "thumbnail": "thumb.ppm"}[name]).write_bytes(b"ok")


def test_publishing_is_blocked_without_human_approval(tmp_path: Path):
    complete_job(tmp_path)
    result = PublishingGate().evaluate(tmp_path)
    assert result["publish_allowed"] is False
    assert result["reason"] == "human_approval_required"


def test_publishing_is_allowed_only_after_validation_and_approval(tmp_path: Path):
    complete_job(tmp_path)
    result = PublishingGate().evaluate(tmp_path, human_approved=True)
    assert result["status"] == "approved"
    assert result["publish_allowed"] is True
