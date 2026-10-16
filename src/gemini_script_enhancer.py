"""Optional Gemini-based Egyptian Arabic lesson refinement.

The production pipeline remains fully usable without a Gemini API key. When
GEMINI_API_KEY is configured as a GitHub Actions secret, Gemini may improve
spoken phrasing while preserving the lesson's four-scene structure and safety
rules. Network/API failures always fall back to the reviewed local script.
"""

from __future__ import annotations

import copy
import json
import os
import urllib.error
import urllib.request
from typing import Any

from src.content_engine import validate_lesson


def enhance_lesson_with_gemini(
    lesson: dict[str, Any], api_key: str | None = None
) -> dict[str, Any]:
    """Refine Arabic scene wording using Gemini, or return the local lesson."""
    key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
    if not key:
        return lesson

    model = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()
    original = copy.deepcopy(lesson)
    scene_spec = [
        {"purpose": s["purpose"], "text": s["text"]}
        for s in original["scenes"]
    ]
    prompt = (
        "Rewrite this beginner handmade/crochet lesson in clear, natural Egyptian "
        "Arabic suitable for a female narrator. Keep every instruction practical, "
        "accurate, and beginner-safe. Do not invent facts, materials, prices, or "
        "results. Preserve exactly the four scene purposes and order: hook, lesson, "
        "application, cta. Return ONLY JSON with a 'scenes' array, each item having "
        "'purpose' and 'text'. Keep text concise for spoken narration. Input: "
        + json.dumps(scene_spec, ensure_ascii=False)
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.35,
            "maxOutputTokens": 1200,
        },
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        refined = json.loads(text)
        scenes = refined.get("scenes")
        if not isinstance(scenes, list) or len(scenes) != 4:
            return lesson
        expected = [scene["purpose"] for scene in original["scenes"]]
        if [scene.get("purpose") for scene in scenes] != expected:
            return lesson
        updated = copy.deepcopy(original)
        for current, candidate in zip(updated["scenes"], scenes):
            wording = candidate.get("text")
            if not isinstance(wording, str) or not wording.strip() or len(wording) > 1200:
                return lesson
            current["text"] = wording.strip()
        updated["script"] = " ".join(scene["text"] for scene in updated["scenes"])
        validate_lesson(updated)
        return updated
    except (KeyError, IndexError, TypeError, ValueError, OSError, TimeoutError, urllib.error.URLError):
        # Optional AI must never stop the free deterministic production path.
        return lesson
