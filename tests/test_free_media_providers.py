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
