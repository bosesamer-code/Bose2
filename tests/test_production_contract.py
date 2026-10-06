from src.production_contract import validate_contract


def valid_contract():
    return {
        "contract_version": 1,
        "task_id": "video-0006",
        "production_status": "ready_for_public_factory",
        "permissions": {
            "produce_media": True,
            "publish": False,
            "access_private_core": False,
        },
        "inputs": {"script": "Teach a crochet technique."},
        "scene_plan": [],
        "validation_requirements": ["required_artifact_directories", "media_presence"],
    }


def test_valid_contract():
    ok, errors = validate_contract(valid_contract())
    assert ok
    assert errors == []


def test_contract_rejects_publish_permission():
    contract = valid_contract()
    contract["permissions"]["publish"] = True

    ok, errors = validate_contract(contract)

    assert not ok
    assert "publish_must_be_false" in errors


def test_contract_rejects_secret():
    contract = valid_contract()
    contract["inputs"]["api_key"] = "must never be here"

    ok, errors = validate_contract(contract)

    assert not ok
    assert "forbidden_secret_or_private_data" in errors
