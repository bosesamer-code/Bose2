from pathlib import Path

from src.free_media_providers import FreeLocalAudioProvider, FreeLocalImageProvider
from src.media_providers import MediaRequest


def test_free_local_audio_provider_creates_wav(tmp_path: Path):
    result = FreeLocalAudioProvider().generate(MediaRequest("audio-1", tmp_path, {}))
    assert result.status == "completed"
    assert (tmp_path / "voice.wav").is_file()


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
                    {"scene": 1, "purpose": "hook", "text": "ابدئي بفكرة واحدة"},
                    {"scene": 2, "purpose": "lesson", "text": "قسمي التنفيذ إلى خطوات"},
                    {"scene": 3, "purpose": "application", "text": "راجعي النموذج وحسنيه"},
                    {"scene": 4, "purpose": "cta", "text": "تابعي الدرس القادم"},
                ]
            },
        )
    )
    assert result.status == "completed"
    assert len(result.artifacts) == 4
    assert all(Path(path).stat().st_size > 640 * 360 * 3 for path in result.artifacts)
    assert len({Path(path).read_bytes() for path in result.artifacts}) == 4
