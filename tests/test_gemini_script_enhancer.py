from pathlib import Path

from src.content_engine import generate_lesson, load_catalog
from src.gemini_script_enhancer import enhance_lesson_with_gemini


def test_gemini_refinement_is_optional_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    catalog = load_catalog(Path("content/content_catalog.json"))
    lesson = generate_lesson(catalog, "crochet_basics", 0)
    before = lesson["script"]

    result = enhance_lesson_with_gemini(lesson)

    assert result["script"] == before
    assert len(result["scenes"]) == 4
    assert [scene["purpose"] for scene in result["scenes"]] == ["hook", "lesson", "application", "cta"]



class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        import json
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")


def _fake_response(scenes):
    import json
    text = json.dumps({"scenes": scenes}, ensure_ascii=False)
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


def test_gemini_enhancer_rejects_short_response_for_long_video_target(monkeypatch):
    import json
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    catalog = load_catalog(Path("content/content_catalog.json"))
    lesson = generate_lesson(catalog, "crochet_basics", 0)
    short_scenes = [
        {"purpose": scene["purpose"], "text": "شرح بسيط ومفيد للمبتدئين."}
        for scene in lesson["scenes"]
    ]
    monkeypatch.setattr(
        "src.gemini_script_enhancer.urllib.request.urlopen",
        lambda *args, **kwargs: FakeResponse(_fake_response(short_scenes)),
    )

    result = enhance_lesson_with_gemini(lesson)

    assert result is lesson


def test_gemini_enhancer_accepts_script_in_target_word_range(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    catalog = load_catalog(Path("content/content_catalog.json"))
    lesson = generate_lesson(catalog, "crochet_basics", 0)
    purposes = [scene["purpose"] for scene in lesson["scenes"]]
    long_scenes = [
        {
            "purpose": purpose,
            "text": " ".join(
                ["ابدئي", "بهدوء", "راجعي", "الغرز", "وثبتي", "شد", "الخيط", "وقارني",
                 "العينة", "بعد", "كل", "سطر", "وسجلي", "النتيجة", "قبل", "الاستمرار"] * 3
            ),
        }
        for purpose in purposes
    ]
    monkeypatch.setattr(
        "src.gemini_script_enhancer.urllib.request.urlopen",
        lambda *args, **kwargs: FakeResponse(_fake_response(long_scenes)),
    )

    result = enhance_lesson_with_gemini(lesson)

    assert result is not lesson
    assert 160 <= len(result["script"].split()) <= 330
    assert [scene["purpose"] for scene in result["scenes"]] == purposes
