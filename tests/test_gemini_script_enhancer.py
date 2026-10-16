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

