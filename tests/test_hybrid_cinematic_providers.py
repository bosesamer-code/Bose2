from pathlib import Path

from src.hybrid_cinematic_providers import HybridNarrationProvider, hybrid_cinematic_registry
from src.media_providers import MediaRequest


def test_hybrid_narration_uses_edge_tts_when_script_is_provided(tmp_path: Path, monkeypatch):
    import src.hybrid_cinematic_providers as providers

    expected = tmp_path / "voice.mp3"

    def fake_generate(self, request):
        expected.parent.mkdir(parents=True, exist_ok=True)
        expected.write_bytes(b"fake audio")
        return providers.MediaResult(self.name, self.media_type, "completed", [str(expected)])

    monkeypatch.setattr(providers.FreeLocalAudioProvider, "generate", fake_generate)
    result = HybridNarrationProvider().generate(
        MediaRequest("tts", tmp_path / "audio", {"script": "أهلًا بيكم في درس الكروشيه"})
    )
    assert result.status == "completed"
    assert result.artifacts == [str(expected)]


def test_hybrid_narration_prefers_supplied_recording(tmp_path: Path, monkeypatch):
    import src.hybrid_cinematic_providers as providers

    source = tmp_path / "narration.mp3"
    source.write_bytes(b"ID3" + b"x" * 1500)
    result = HybridNarrationProvider().generate(
        MediaRequest("recorded", tmp_path / "audio", {"recorded_audio_path": str(source), "script": "ignored"})
    )
    assert result.status == "completed"
    assert Path(result.artifacts[0]).read_bytes() == source.read_bytes()


def test_hybrid_registry_keeps_expected_media_types():
    registry = hybrid_cinematic_registry()
    assert registry.media_types() == ["audio", "design", "image", "thumbnail", "video"]
    assert registry.get("video").name == "real-crochet-footage"
