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


def test_free_local_image_provider_uses_scene_text_for_lesson_structure(tmp_path: Path):
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
    assert Path(four_steps.artifacts[0]).read_bytes() != Path(three_steps.artifacts[0]).read_bytes()
