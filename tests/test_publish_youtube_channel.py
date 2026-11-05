from scripts.publish_youtube import verify_target_channel


class _Request:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class _Channels:
    def list(self, **kwargs):
        if kwargs.get("forHandle"):
            return _Request({"items": [{"id": "target-channel", "snippet": {"title": "Handmade Secrets"}}]})
        if kwargs.get("mine"):
            return _Request({"items": [
                {"id": "other-channel", "snippet": {"title": "Other"}},
                {"id": "target-channel", "snippet": {"title": "Handmade Secrets"}},
            ]})
        raise AssertionError(f"Unexpected channels.list arguments: {kwargs}")


class _YouTube:
    def channels(self):
        return _Channels()


def test_target_channel_can_be_one_of_multiple_authorized_channels(monkeypatch):
    monkeypatch.setenv("YOUTUBE_EXPECTED_CHANNEL_HANDLE", "handmade.secrets")

    assert verify_target_channel(_YouTube()) == "target-channel"


def test_target_channel_not_authorized_fails_closed(monkeypatch):
    monkeypatch.setenv("YOUTUBE_EXPECTED_CHANNEL_HANDLE", "handmade.secrets")

    class WrongChannelYouTube:
        def channels(self):
            class Channels:
                def list(self, **kwargs):
                    if kwargs.get("forHandle"):
                        return _Request({"items": [{"id": "target-channel"}]})
                    return _Request({"items": [{"id": "different-channel"}]})
            return Channels()

    try:
        verify_target_channel(WrongChannelYouTube())
    except SystemExit as exc:
        assert "not among" in str(exc)
    else:
        raise AssertionError("Expected a fail-closed channel mismatch")
