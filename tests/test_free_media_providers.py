from pathlib import Path

from src.free_media_providers import FreeLocalAudioProvider, FreeLocalImageProvider
from src.media_providers import MediaRequest


def test_free_local_audio_provider_creates_real_egyptian_speech(tmp_path: Path, monkeypatch):
    import subprocess
    import src.free_media_providers as providers

    monkeypatch.setattr(providers.shutil, "which", lambda name: "/usr/bin/edge-tts" if name == "edge-tts" else None)

    def fake_tts(command, **kwargs):
        assert "ar-EG-SalmaNeural" in command
        output = Path(command[command.index("--write-media") + 1])
        output.write_bytes(b"ID3" + b"\x00" * 1500)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(providers.subprocess, "run", fake_tts)
    result = FreeLocalAudioProvider().generate(
        MediaRequest("audio-1", tmp_path, {"script": "أهلاً بيكم في أسرار الهاند ميد"})
    )
    assert result.status == "completed"
    assert (tmp_path / "voice.mp3").is_file()
    assert not (tmp_path / "voice.wav").exists()


def test_free_local_audio_provider_never_falls_back_to_tone(tmp_path: Path, monkeypatch):
    import src.free_media_providers as providers

    monkeypatch.setattr(providers.shutil, "which", lambda _name: None)
    result = FreeLocalAudioProvider().generate(
        MediaRequest("audio-2", tmp_path, {"script": "نص عربي واضح"})
    )
    assert result.status == "not_configured"
    assert not list(tmp_path.glob("voice.*"))


def test_free_local_image_provider_creates_ppm(tmp_path: Path):
    result = FreeLocalImageProvider().generate(MediaRequest("image-1", tmp_path, {}))
    assert result.status == "completed"
    assert (tmp_path / "scene_001.ppm").is_file()


def test_free_local_image_provider_encodes_scene_purpose(tmp_path: Path):
    result = FreeLocalImageProvider().generate(
        MediaRequest(
            "lesson-1",
            tmp_path,
            {
                "scene_plan": [
                    {"scene": 1, "purpose": "hook", "text": "فكرة واحدة"},
                    {"scene": 2, "purpose": "lesson", "text": "قسمي التنفيذ إلى خطوات"},
                    {"scene": 3, "purpose": "application", "text": "راجعي النموذج وحسنيه"},
                    {"scene": 4, "purpose": "cta", "text": "تابعي الدرس القادم"},
                ],
            },
        )
    )
    assert result.status == "completed"
    assert len(result.artifacts) == 4
    assert all(Path(path).stat().st_size > 640 * 360 * 3 for path in result.artifacts)
    assert len({Path(path).read_bytes() for path in result.artifacts}) == 4


def test_free_local_image_provider_draws_host_and_handmade_props(tmp_path: Path):
    provider = FreeLocalImageProvider()
    four_steps = provider.generate(
        MediaRequest(
            "lesson-steps",
            tmp_path / "four",
            {"scene_plan": [{"scene": 1, "purpose": "lesson", "text": "قسمي التنفيذ إلى خطوات"}]},
        )
    )
    three_steps = provider.generate(
        MediaRequest(
            "lesson-generic",
            tmp_path / "three",
            {"scene_plan": [{"scene": 1, "purpose": "lesson", "text": "تعرفي على الفكرة"}]},
        )
    )
    assert four_steps.status == "completed"
    assert three_steps.status == "completed"
    for artifact in (four_steps.artifacts[0], three_steps.artifacts[0]):
        data = Path(artifact).read_bytes()
        assert data.startswith(b"P6\n640 360\n255\n")
        assert len(data) > 640 * 360 * 3


def test_arabic_subtitles_wrap_into_mobile_readable_lines():
    from src.free_media_providers import _wrap_subtitle_text

    text = "ابدئي بخطوة بسيطة وحددي الخامات والأدوات قبل التنفيذ"
    wrapped = _wrap_subtitle_text(text, width=24)

    assert "\n" in wrapped
    assert " ".join(wrapped.splitlines()) == text
    assert all(len(line) <= 24 for line in wrapped.splitlines())
