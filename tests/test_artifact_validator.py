from pathlib import Path

from src.artifact_validator import ArtifactValidator


def test_empty_prepared_job_is_incomplete(tmp_path: Path):
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        (tmp_path / name).mkdir()

    result = ArtifactValidator().validate(tmp_path)
    assert result["status"] == "valid"


def test_media_required_fails_without_media(tmp_path: Path):
    (tmp_path / "video").mkdir()

    result = ArtifactValidator().validate(tmp_path, require_media=True)
    assert result["status"] == "failed"
    assert result["reason"] == "no_media_artifacts"
