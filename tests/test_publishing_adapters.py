from src.publishing_contract import build_publishing_contract
from src.publishers import PublishingRouter


def test_publishing_contract_requires_human_approval():
    content = {
        "content_id": "handmade-001",
        "title": "درس هاند ميد",
        "publishing": {"facebook": True, "youtube": True, "automatic_publish": False},
        "human_approval_required": True,
    }
    contract = build_publishing_contract(content, artifact_path="video/final.mp4")
    result = PublishingRouter().publish(contract)
    assert result["status"] == "blocked"
    assert all(item["reason"] == "human_approval_required" for item in result["results"])


def test_approved_contract_reaches_both_dry_run_destinations():
    content = {
        "content_id": "handmade-002",
        "title": "درس هاند ميد 2",
        "publishing": {"facebook": True, "youtube": True, "automatic_publish": False},
        "human_approval_required": True,
    }
    contract = build_publishing_contract(
        content, artifact_path="video/final.mp4", approved=True
    )
    result = PublishingRouter().publish(contract)
    assert result["status"] == "ready"
    assert {item["destination"] for item in result["results"]} == {"facebook", "youtube"}
