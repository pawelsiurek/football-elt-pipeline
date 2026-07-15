"""Tests for elt/extract.py — the API layer, with requests fully mocked.

No network and no API key required: we replace requests.get with a fake that
returns canned responses, so these run anywhere (including CI with zero secrets).
"""

import extract
import pytest


class FakeResponse:
    """Minimal stand-in for requests.Response covering what extract.py touches."""

    def __init__(self, status_code: int, json_data: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self) -> dict:
        return self._json


def test_extract_matches_hits_right_url_and_returns_json(monkeypatch, matches_payload):
    captured = {}

    def fake_get(url, headers):
        captured["url"] = url
        captured["headers"] = headers
        return FakeResponse(200, matches_payload)

    monkeypatch.setattr(extract.requests, "get", fake_get)

    result = extract.extract_matches("PL")

    assert result == matches_payload
    assert captured["url"] == "https://api.football-data.org/v4/competitions/PL/matches"
    assert "X-Auth-Token" in captured["headers"]


def test_extract_standings_hits_right_url(monkeypatch, standings_payload):
    def fake_get(url, headers):
        assert url.endswith("/competitions/PL/standings")
        return FakeResponse(200, standings_payload)

    monkeypatch.setattr(extract.requests, "get", fake_get)
    assert extract.extract_standings("PL") == standings_payload


def test_extract_scorers_hits_right_url(monkeypatch, scorers_payload):
    def fake_get(url, headers):
        assert url.endswith("/competitions/PL/scorers")
        return FakeResponse(200, scorers_payload)

    monkeypatch.setattr(extract.requests, "get", fake_get)
    assert extract.extract_scorers("PL") == scorers_payload


@pytest.mark.parametrize(
    "func_name",
    ["extract_matches", "extract_standings", "extract_scorers"],
)
def test_extract_raises_on_non_200(monkeypatch, func_name):
    """A non-200 (e.g. 429 rate-limit) must surface as an exception, not be swallowed."""

    def fake_get(url, headers):
        return FakeResponse(429, text="You reached your request limit.")

    monkeypatch.setattr(extract.requests, "get", fake_get)

    func = getattr(extract, func_name)
    with pytest.raises(Exception, match="429"):
        func("PL")
