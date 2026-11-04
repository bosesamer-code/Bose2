"""Unit tests for Facebook Page identity preflight."""

from __future__ import annotations

import pytest

from scripts.publish_facebook import verify_page_identity


class FakeResponse:
    def __init__(self, payload, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise RuntimeError(self.error)

    def json(self):
        return self.payload


class FakeHTTP:
    def __init__(self, payload=None, error=None):
        self.payload = payload if payload is not None else {"id": "123", "name": "Test Page"}
        self.error = error
        self.calls = []

    def get(self, url, *, params, timeout):
        self.calls.append((url, params, timeout))
        return FakeResponse(self.payload, self.error)


def test_page_identity_accepts_exact_configured_page_id():
    http = FakeHTTP({"id": "123", "name": "Bose Test Page"})
    name = verify_page_identity(http, "v26.0", "123", "do-not-log-this-token")
    assert name == "Bose Test Page"
    assert http.calls[0][0] == "https://graph.facebook.com/v26.0/123"
    assert http.calls[0][1]["fields"] == "id,name"
    assert http.calls[0][1]["access_token"] == "do-not-log-this-token"
    assert http.calls[0][2] == 30


def test_page_identity_rejects_a_different_page_id():
    http = FakeHTTP({"id": "999", "name": "Wrong Page"})
    with pytest.raises(SystemExit, match="does not resolve to the configured Page ID"):
        verify_page_identity(http, "v26.0", "123", "token")


def test_page_identity_fails_closed_without_exposing_api_error_or_token():
    secret = "sensitive-token-value"
    http = FakeHTTP(error=f"request failed with {secret}")
    with pytest.raises(SystemExit) as error:
        verify_page_identity(http, "v26.0", "123", secret)
    assert secret not in str(error.value)
    assert "refusing upload" in str(error.value)
