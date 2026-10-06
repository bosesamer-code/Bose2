from pathlib import Path

from src.artifact_validator import ArtifactValidator


def test_empty_prepared_job_is_valid_without_media_requirement(tmp_path: Path):
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        (tmp_path / name).mkdir()

    result = ArtifactValidator().validate(tmp_path)
    assert result["status"] == "valid"


def test_media_required_fails_without_media(tmp_path: Path):
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        (tmp_path / name).mkdir()

    result = ArtifactValidator().validate(tmp_path, require_media=True)
    assert result["status"] == "failed"
    assert result["reason"] == "invalid_or_missing_media_artifacts"
    assert len(result["empty_media_directories"]) == 5


def test_media_required_accepts_complete_artifact_set(tmp_path: Path):
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        directory = tmp_path / name
        directory.mkdir()
        (directory / {"audio": "voice.wav", "images": "scene.ppm", "designs": "design.ppm", "video": "video.mp4", "thumbnail": "thumb.ppm"}[name]).write_bytes(b"ok")

    result = ArtifactValidator().validate(tmp_path, require_media=True)
    assert result["status"] == "valid"
    assert result["empty_media_directories"] == []
