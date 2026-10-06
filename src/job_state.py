"""Durable, deterministic production job state machine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


STATUSES = {
    "queued",
    "producing",
    "validating",
    "ready",
    "failed",
    "blocked",
    "rolled_back",
}

TRANSITIONS = {
    "queued": {"producing", "blocked", "queued"},
    "producing": {"validating", "failed", "blocked"},
    "validating": {"ready", "failed", "blocked"},
    "ready": set(),
    "failed": {"queued", "rolled_back", "blocked"},
    "blocked": set(),
    "rolled_back": set(),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProductionJob:
    task_id: str
    status: str = "queued"
    attempts: int = 0
    max_attempts: int = 2
    created_at: str = ""
    updated_at: str = ""
    error: str | None = None

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = utc_now()
        if not self.updated_at:
            self.updated_at = self.created_at
        if self.status not in STATUSES:
            raise ValueError(f"invalid status: {self.status}")

    def transition(self, new_status: str, error: str | None = None) -> None:
        if new_status not in STATUSES:
            raise ValueError(f"invalid status: {new_status}")
        if new_status not in TRANSITIONS[self.status]:
            raise ValueError(f"invalid transition: {self.status} -> {new_status}")
        if new_status == "queued":
            if self.attempts >= self.max_attempts:
                raise ValueError("retry_limit_reached")
            self.attempts += 1
        self.status = new_status
        self.error = error
        self.updated_at = utc_now()

    @classmethod\n    def from_dict(cls, data: dict[str, Any]) -> "ProductionJob":\n        return cls(\n            task_id=str(data["task_id"]),\n            status=str(data.get("status", "queued")),\n            attempts=int(data.get("attempts", 0)),\n            max_attempts=int(data.get("max_attempts", 2)),\n            created_at=str(data.get("created_at", "")),\n            updated_at=str(data.get("updated_at", "")),\n            error=data.get("error"),\n        )\n\n    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "status": self.status,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error,
        }
