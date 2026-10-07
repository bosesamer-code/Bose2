from pathlib import Path

from src.content_engine import generate_queue, load_catalog


def test_generate_queue_creates_unique_lessons():
    catalog = load_catalog(Path("content/content_catalog.json"))
    queue = generate_queue(
        catalog,
        [("crochet_basics", 0), ("handmade_home", 0), ("handmade_business", 0)],
    )

    assert len(queue) == 3
    assert len({item["content_id"] for item in queue}) == 3
    assert all(item["human_approval_required"] for item in queue)
    assert all(item["publishing"]["automatic_publish"] is False for item in queue)
