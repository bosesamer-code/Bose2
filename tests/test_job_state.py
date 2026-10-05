import pytest

from src.job_state import ProductionJob


def test_happy_path():
    job = ProductionJob("video-1")
    job.transition("producing")
    job.transition("validating")
    job.transition("ready")
    assert job.status == "ready"


def test_invalid_transition():
    job = ProductionJob("video-1")
    with pytest.raises(ValueError):
        job.transition("ready")


def test_retry_limit():
    job = ProductionJob("video-1", max_attempts=1)
    job.transition("producing")
    job.transition("failed", "provider error")
    job.transition("queued")
    with pytest.raises(ValueError, match="retry_limit_reached"):
        job.transition("queued")
