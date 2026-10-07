from pathlib import Path
import subprocess
import wave

from src.artifact_validator import ArtifactValidator


def _make_ppm(path: Path) -> None:
    path.write_bytes(b"P6\n2 2\n255\n" + b"\x00\x00\x00" * 4)


def _make_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(8000)
        handle.writeframes(b"\x00\x00" * 800)


def _make_mp4(path: Path, image: Path, audio: Path) -> None:
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-i", str(image), "-i", str(audio),
            "-t", "0.1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


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
    assert len(result["empty_media_dirs"]) == 5


def test_fake_media_is_rejected(tmp_path: Path):
    for name, filename in {
        "audio": "voice.wav", "images": "scene.ppm", "designs": "design.ppm",
        "video": "video.mp4", "thumbnail": "thumb.ppm",
    }.items():
        directory = tmp_path / name
        directory.mkdir()
        (directory / filename).write_bytes(b"not real media")
    result = ArtifactValidator().validate(tmp_path, require_media=True)
    assert result["status"] == "failed"
    assert set(result["invalid_media_files"]) == {"audio", "images", "designs", "video", "thumbnail"}


def test_media_required_accepts_real_artifact_set(tmp_path: Path):
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        (tmp_path / name).mkdir()
    image = tmp_path / "images" / "scene.ppm"
    design = tmp_path / "designs" / "design.ppm"
    thumb = tmp_path / "thumbnail" / "thumb.ppm"
    audio = tmp_path / "audio" / "voice.wav"
    video = tmp_path / "video" / "video.mp4"
    for path in (image, design, thumb):
        _make_ppm(path)
    _make_wav(audio)
    _make_mp4(video, image, audio)

    result = ArtifactValidator().validate(tmp_path, require_media=True)
    assert result["status"] == "valid"
    assert result["invalid_media_files"] == {}
    assert result["empty_media_dirs"] == []


def test_validator_ignores_video_helper_files(tmp_path: Path):
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        (tmp_path / name).mkdir(parents=True)
    (tmp_path / "audio" / "voice.wav").write_bytes(b"RIFF" + b"0" * 100)
    (tmp_path / "images" / "scene.ppm").write_bytes(b"P6\n1 1\n255\n\x00\x00\x00")
    (tmp_path / "designs" / "design.ppm").write_bytes(b"P6\n1 1\n255\n\x00\x00\x00")
    (tmp_path / "thumbnail" / "thumb.ppm").write_bytes(b"P6\n1 1\n255\n\x00\x00\x00")
    (tmp_path / "video" / "scenes.txt").write_text("ffmpeg helper", encoding="utf-8")
    result = ArtifactValidator().validate(tmp_path, require_media=True)
    assert "video/scenes.txt" not in result["invalid_media_files"].get("video", [])
