"""Validated publishing handoff contract for external destinations."""

from __future__ import annotations

from typing import Any

DESTINATIONS = ("facebook", "youtube")


def build_publishing_contract(
    content: dict[str, Any],
    *,
    artifact_path: str,
    approved: bool = False,
) -> dict[str, Any]:
    publishing = dict(content.get("publishing", {}))
    destinations = [name for name in DESTINATIONS if publishing.get(name) is True]
    if not destinations:
        raise ValueError("no_publish_destinations")
    if publishing.get("automatic_publish") is not False:
        raise ValueError("automatic_publish_must_be_false")
    if content.get("human_approval_required") is not True:
        raise ValueError("human_approval_required")
    if not artifact_path:
        raise ValueError("artifact_path_required")
    return {
        "contract_version": 1,
        "content_id": str(content["content_id"]),
        "title": str(content["title"]),
        "description": str(content.get("description", content["title"])),
        "language": str(content.get("language", "ar")),
        "artifact_path": artifact_path,
        "destinations": destinations,
        "approval": {
            "required": True,
            "approved": bool(approved),
        },
        "automatic_publish": False,
    }
