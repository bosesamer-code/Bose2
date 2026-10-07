"""Automatic publishing plan with explicit owner-controlled enablement."""

from __future__ import annotations

from typing import Any


def build_automatic_publish_plan(content: dict[str, Any], artifact_path: str) -> dict[str, Any]:
    publishing = dict(content.get("publishing", {}))
    destinations = [name for name in ("facebook", "youtube") if publishing.get(name) is True]
    if not destinations:
        raise ValueError("no_publish_destinations")
    if publishing.get("automatic_publish") is not True:
        raise ValueError("automatic_publish_not_enabled")
    if content.get("owner_controlled") is not True:
        raise ValueError("owner_control_required")
    return {
        "contract_version": 1,
        "content_id": str(content["content_id"]),
        "title": str(content["title"]),
        "description": str(content.get("description", content["title"])),
        "artifact_path": artifact_path,
        "destinations": destinations,
        "automatic_publish": True,
        "owner_controlled": True,
    }
