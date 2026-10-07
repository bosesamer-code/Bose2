"""Destination-neutral publishing adapters with safe dry-run behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class PublishResult:
    destination: str
    status: str
    reason: str | None = None


class Publisher(Protocol):
    destination: str

    def publish(self, contract: dict[str, Any]) -> PublishResult: ...


class DryRunPublisher:
    def __init__(self, destination: str) -> None:
        self.destination = destination

    def publish(self, contract: dict[str, Any]) -> PublishResult:
        if contract["approval"]["approved"] is not True:
            return PublishResult(
                self.destination, "blocked", "human_approval_required"
            )
        return PublishResult(self.destination, "dry_run_ready")


class PublishingRouter:
    def __init__(self, publishers: dict[str, Publisher] | None = None) -> None:
        self.publishers = publishers or {
            "facebook": DryRunPublisher("facebook"),
            "youtube": DryRunPublisher("youtube"),
        }

    def publish(self, contract: dict[str, Any]) -> dict[str, Any]:
        results = []
        for destination in contract["destinations"]:
            publisher = self.publishers.get(destination)
            if publisher is None:
                results.append(
                    PublishResult(destination, "blocked", "publisher_not_configured")
                )
                continue
            results.append(publisher.publish(contract))
        return {
            "status": "ready" if all(r.status == "dry_run_ready" for r in results) else "blocked",
            "results": [r.__dict__ for r in results],
        }
