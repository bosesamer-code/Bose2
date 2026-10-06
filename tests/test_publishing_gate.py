from pathlib import Path
import subprocess
import wave

from src.publishing_gate import PublishingGate


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


def complete_job(root: Path) -> None:
    for name in ("audio", "images", "designs", "video", "thumbnail"):
        (root / name).mkdir()
    image = root / "images" / "scene.ppm"
    design = root / "designs" / "design.ppm"
    thumb = root / "thumbnail" / "thumb.ppm"
    audio = root / "audio" / "voice.wav"
    video = root / "video" / "video.mp4"
    for path in (image, design, thumb):
        _make_ppm(path)
    _make_wav(audio)
    _make_mp4(video, image, audio)


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
