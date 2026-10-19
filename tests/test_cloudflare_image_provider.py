from pathlib import Path
from types import SimpleNamespace

from src.cloudflare_image_provider import CloudflareWorkersAIImageProvider
from src.media_providers import MediaRequest


def test_cloudflare_image_provider_writes_png_without_logging_secrets(tmp_path, monkeypatch):
    import src.cloudflare_image_provider as provider_module

    token = "do-not-log-this-token"
    account_id = "account-id"
    image_bytes = b"\x89PNG\r\n\x1a\n" + b"x" * 100
    captured = {}

    class FakeResponse:
        headers = {"Content-Type": "image/png"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return image_bytes

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["authorization"] = req.get_header("Authorization")
        captured["body"] = req.data
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(provider_module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setenv("CLOUDFLARE_MAX_IMAGES_PER_JOB", "4")

    result = CloudflareWorkersAIImageProvider(token, account_id).generate(
        MediaRequest("test", tmp_path, {"scene_plan": [{"purpose": "lesson", "text": "basic crochet stitch"}]})
    )

    assert result.status == "completed"
    assert len(result.artifacts) == 1
    assert Path(result.artifacts[0]).read_bytes() == image_bytes
    assert captured["authorization"] == "Bearer " + token
    assert account_id in captured["url"]
    assert token not in str(result)
    assert captured["timeout"] == 90


def test_cloudflare_provider_refuses_missing_credentials(tmp_path):
    result = CloudflareWorkersAIImageProvider("", "").generate(
        MediaRequest("test", tmp_path, {"scene_plan": [{"text": "crochet"}]})
    )
    assert result.status == "not_configured"
    assert result.artifacts == []


def test_cloudflare_provider_scene_cap_sends_no_requests(tmp_path, monkeypatch):
    import src.cloudflare_image_provider as provider_module

    def forbidden_urlopen(*_args, **_kwargs):
        raise AssertionError("No request should be sent above the safety cap.")

    monkeypatch.setattr(provider_module.urllib.request, "urlopen", forbidden_urlopen)
    monkeypatch.setenv("CLOUDFLARE_MAX_IMAGES_PER_JOB", "1")
    provider = CloudflareWorkersAIImageProvider("token", "account")
    result = provider.generate(
        MediaRequest("test", tmp_path, {"scene_plan": [{"text": "one"}, {"text": "two"}]})
    )
    assert result.status == "not_configured"
    assert result.artifacts == []
