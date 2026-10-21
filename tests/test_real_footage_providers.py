from pathlib import Path
import subprocess

from src.media_providers import MediaRequest
from src.real_footage_providers import RecordedAudioProvider, RealFootageVideoProvider


def test_recorded_audio_provider_copies_only_existing_mp3(tmp_path: Path):
    source = tmp_path / "narration.mp3"
    source.write_bytes(b"ID3" + b"x" * 1500)
    result = RecordedAudioProvider().generate(
        MediaRequest("real-audio", tmp_path / "out", {"recorded_audio_path": str(source)})
    )
    assert result.status == "completed"
    assert Path(result.artifacts[0]).read_bytes() == source.read_bytes()


def test_recorded_audio_provider_rejects_non_mp3(tmp_path: Path):
    source = tmp_path / "narration.wav"
    source.write_bytes(b"x" * 2000)
    result = RecordedAudioProvider().generate(
        MediaRequest("real-audio-invalid", tmp_path / "out", {"recorded_audio_path": str(source)})
    )
    assert result.status == "failed"
    assert result.artifacts == []


def test_real_footage_provider_uses_user_clip_and_recorded_voice(tmp_path: Path, monkeypatch):
    import src.real_footage_providers as providers

    monkeypatch.setattr(
        providers.shutil, "which",
        lambda name: f"/usr/bin/{name}" if name in {"ffmpeg", "ffprobe"} else None,
    )
    clip = tmp_path / "hands.mp4"
    clip.write_bytes(b"fake clip" * 200)
    audio = tmp_path / "voice.mp3"
    audio.write_bytes(b"ID3" + b"x" * 1500)
    commands = []

    def fake_run(command, **kwargs):
        if command[0].endswith("ffprobe"):
            return subprocess.CompletedProcess(command, 0, "4.0", "")
        commands.append(command)
        Path(command[-1]).write_bytes(b"fake mp4 " + b"x" * 2048)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(providers.subprocess, "run", fake_run)
    result = RealFootageVideoProvider().generate(
        MediaRequest(
            "real-video", tmp_path / "render",
            {
                "real_footage_paths": [str(clip)],
                "audio_path": str(audio),
                "scene_plan": [
                    {"scene": 1, "duration_seconds": 2, "text": "ابدئي أول غرزة"},
                    {"scene": 2, "duration_seconds": 2, "text": "كملي بهدوء"},
                ],
            },
        )
    )
    assert result.status == "completed"
    assert Path(result.artifacts[0]).is_file()
    assert len(commands) == 3
    assert all("scale=1920:1080" in command[command.index("-vf") + 1] for command in commands[:2])
    final_command = commands[-1]
    assert str(audio) in final_command
    assert "subtitles=" in final_command[final_command.index("-vf") + 1]
    assert "zoompan" not in final_command[final_command.index("-vf") + 1]


def test_real_footage_provider_fails_closed_without_real_clip(tmp_path: Path, monkeypatch):
    import src.real_footage_providers as providers

    monkeypatch.setattr(providers.shutil, "which", lambda name: "/usr/bin/" + name)
    result = RealFootageVideoProvider().generate(
        MediaRequest("no-clip", tmp_path / "render", {"real_footage_paths": [], "audio_path": "missing.mp3"})
    )
    assert result.status == "waiting_for_inputs"
    assert result.artifacts == []
