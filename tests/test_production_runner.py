from pathlib import Path

from src.production_runner import ProductionRunner


def manifest():
    return {
        "contract_version": 1,
        "task_id": "video-0005",
        "production_status": "ready_for_public_factory",
        "permissions": {
            "produce_media": True,
            "publish": False,
            "access_private_core": False,
        },
        "inputs": {
            "script": "Teach the first crochet step.",
            "production_goal": "grow_followers",
        },
        "scene_plan": [{"scene": 1, "role": "hook"}],
        "validation_requirements": ["required_artifact_directories", "media_presence"],
    }


def test_runner_prepares_public_job(tmp_path: Path):
    result = ProductionRunner(tmp_path).run(manifest())

    assert result["production_status"] == "prepared"
    assert result["job_state"]["status"] == "queued"
    job = tmp_path / "video-0005"
    assert (job / "manifest.json").exists()
    assert (job / "scene_manifest.json").exists()
    assert (job / "script.json").exists()


def test_runner_rejects_publish_permission(tmp_path: Path):
    data = manifest()
    data["permissions"]["publish"] = True

    try:
        ProductionRunner(tmp_path).run(data)
    except ValueError as exc:
        assert "publish_must_be_false" in str(exc)
    else:
        raise AssertionError("publish permission must be rejected")
