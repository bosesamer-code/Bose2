"""Deterministic content engine for the handmade production factory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_SCENES = ("hook", "lesson", "application", "cta")

REQUIRED_RULES = (
    "one_clear_learning_goal",
    "include_hook",
    "include_practical_steps",
    "include_cta",
    "avoid_unverified_claims",
    "keep_content_beginner_friendly",
)


def load_catalog(path: Path) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("human_approval_required") is not True:
        raise ValueError("human_approval_required must be true")
    if catalog.get("automatic_publish") is not False:
        raise ValueError("automatic_publish must be false")
    rules = catalog.get("generation_rules", {})
    missing = [rule for rule in REQUIRED_RULES if rules.get(rule) is not True]
    if missing:
        raise ValueError(f"missing_generation_rules:{','.join(missing)}")
    return catalog


def validate_lesson(lesson: dict[str, Any]) -> dict[str, Any]:
    scenes = lesson.get("scenes", [])
    if [scene.get("purpose") for scene in scenes] != list(REQUIRED_SCENES):
        raise ValueError("invalid_scene_sequence")
    if any(not str(scene.get("text", "")).strip() for scene in scenes):
        raise ValueError("scene_text_required")
    if any(int(scene.get("duration_seconds", 0)) <= 0 for scene in scenes):
        raise ValueError("scene_duration_required")
    if sum(int(scene["duration_seconds"]) for scene in scenes) < 20:
        raise ValueError("lesson_too_short")
    if lesson.get("human_approval_required") is not True:
        raise ValueError("human_approval_required")
    if lesson.get("publishing", {}).get("automatic_publish") is not False:
        raise ValueError("automatic_publish_must_be_false")
    return lesson


def generate_lesson(catalog: dict[str, Any], topic_id: str, idea_index: int = 0) -> dict[str, Any]:
    topics = {item["topic_id"]: item for item in catalog.get("topics", [])}
    if topic_id not in topics:
        raise ValueError(f"unknown_topic:{topic_id}")

    topic = topics[topic_id]
    ideas = topic.get("ideas", [])
    if not ideas:
        raise ValueError(f"topic_has_no_ideas:{topic_id}")
    if idea_index < 0 or idea_index >= len(ideas):
        raise ValueError(f"invalid_idea_index:{idea_index}")

    idea = ideas[idea_index]
    content_id = f"{topic_id}-{idea_index + 1:03d}"
    scenes = [
        {"scene": 1, "duration_seconds": 4, "purpose": "hook", "text": idea},
        {
            "scene": 2,
            "duration_seconds": 8,
            "purpose": "lesson",
            "text": f"ابدئي بخطوة بسيطة في موضوع {idea}، وحددي الخامات والأدوات قبل التنفيذ.",
        },
        {
            "scene": 3,
            "duration_seconds": 8,
            "purpose": "application",
            "text": "نفذي نموذجًا صغيرًا، سجلي ما نجح، ثم عدلي النتيجة في المحاولة التالية.",
        },
        {
            "scene": 4,
            "duration_seconds": 4,
            "purpose": "cta",
            "text": "تابعي الدروس القادمة لأفكار هاند ميد عملية وبسيطة.",
        },
    ]

    return validate_lesson({
        "content_id": content_id,
        "language": catalog["language"],
        "title": idea,
        "topic": topic["category"],
        "audience": "beginners",
        "format": catalog["default_format"],
        "script": " ".join(scene["text"] for scene in scenes),
        "scenes": scenes,
        "visual_style": "clean_handmade_tutorial",
        "video_format": "mp4_16_9",
        "publishing": {
            "facebook": True,
            "youtube": True,
            "automatic_publish": False,
        },
        "human_approval_required": True,
    })


def generate_queue(
    catalog: dict[str, Any],
    selections: list[tuple[str, int]],
) -> list[dict[str, Any]]:
    queue = [generate_lesson(catalog, topic_id, index) for topic_id, index in selections]
    ids = [item["content_id"] for item in queue]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_content_id")
    return queue
