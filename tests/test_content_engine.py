from pathlib import Path

from src.content_engine import generate_lesson, load_catalog


def test_content_catalog_generates_beginner_lesson():
    catalog = load_catalog(Path("content/content_catalog.json"))
    lesson = generate_lesson(catalog, "crochet_basics", 0)

    assert lesson["content_id"] == "crochet_basics-001"
    assert lesson["human_approval_required"] is True
    assert lesson["publishing"]["automatic_publish"] is False
    assert len(lesson["scenes"]) == 4
    assert lesson["scenes"][0]["purpose"] == "hook"
    assert lesson["scenes"][-1]["purpose"] == "cta"


def test_content_engine_rejects_unknown_topic():
    catalog = load_catalog(Path("content/content_catalog.json"))

    try:
        generate_lesson(catalog, "does_not_exist", 0)
    except ValueError as exc:
        assert str(exc) == "unknown_topic:does_not_exist"
    else:
        raise AssertionError("unknown topic must fail")
