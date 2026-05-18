"""Regression: X1D provider_request artifacts must not persist credentials."""

from __future__ import annotations

import io
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from apps_rg.runtime.judges import executive_summary_x1d as x1d


_FAKE_GOOGLE_STYLE_KEY = "AIzaSyFakeSecret01234567890123456789012"
_FAKE_OPENAI_KEY = "sk-FAKE_openai_key_do_not_use"


def test_sanitize_request_url_strips_sensitive_query_keys() -> None:
    raw = (
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        f"?key={_FAKE_GOOGLE_STYLE_KEY}&foo=bar"
    )
    safe, omitted = x1d._sanitize_request_url_for_x1d_artifact(raw)
    assert _FAKE_GOOGLE_STYLE_KEY not in safe
    assert "key=" not in safe.lower()
    assert "foo=bar" in safe
    assert "key" in omitted


@pytest.mark.parametrize(
    ("param", "value"),
    [
        ("api_key", "secret_api"),
        ("access_token", "tok_secret"),
        ("token", "bare_token"),
        ("authorization", "Bearer_xx"),
        ("auth", "basic_xx"),
        ("client_secret", "sec_val"),
    ],
)
def test_sanitize_request_url_strips_named_sensitive_params(param: str, value: str) -> None:
    url = f"https://example.com/path?{param}={value}&keep=1"
    safe, omitted = x1d._sanitize_request_url_for_x1d_artifact(url)
    assert value not in safe
    assert f"{param.lower()}=" not in safe.lower()
    assert "keep=1" in safe
    assert param in omitted


def test_openai_provider_request_payload_has_no_bearer_or_raw_api_key() -> None:
    """OpenAI request artifact records payload only (never Authorization header)."""
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "x"}],
    }
    artifact_preview = {
        "payload": payload,
        "input_hash": "abcd",
        "timestamp": "t",
    }
    dumped = json.dumps(artifact_preview)
    assert "Bearer " not in dumped
    assert _FAKE_OPENAI_KEY not in dumped


def test_gemini_provider_request_artifact_redacts_url_under_429(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Integration-style check: first provider_request write omits API key material."""

    monkeypatch.setenv("APPS_RG_GOOGLE_JUDGE_MAX_RETRIES", "0")

    captured: list[tuple[Path, dict]] = []

    def spy_write(path: Path, data: object) -> str:
        assert isinstance(data, dict)
        captured.append((path, dict(data)))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return str(path)

    def boom_urlopen(*_a: object, **_k: object) -> object:
        body = b'{"error":{"code":429,"message":"quota"}}'
        raise urllib.error.HTTPError(
            "https://generativelanguage.googleapis.com/",
            429,
            "RESOURCE_EXHAUSTED",
            {},
            io.BytesIO(body),
        )

    monkeypatch.setattr(x1d, "_write_artifact", spy_write)
    monkeypatch.setattr(x1d.urllib.request, "urlopen", boom_urlopen)
    monkeypatch.setattr(x1d.time, "sleep", lambda _s: None)

    out = x1d._call_gemini(
        _FAKE_GOOGLE_STYLE_KEY,
        '{"score_scale":"0_to_5","score":4,"threshold":4,"pass":true}',
        "gemini-2.5-flash",
        "deadbeef",
        "gemini_pro",
        model_source="TEST_MODEL_SOURCE",
        artifact_base=tmp_path,
    )
    assert out.provider_blocked is True

    req_writes = [d for p, d in captured if "provider_request" in p.name]
    assert len(req_writes) >= 1
    body = req_writes[0]
    dumped = json.dumps(body)

    assert _FAKE_GOOGLE_STYLE_KEY not in dumped
    assert "key=" not in dumped.lower()
    assert "Bearer " not in dumped
    assert body.get("resolved_model") == "gemini-2.5-flash"
    assert body.get("resolved_model_source") == "TEST_MODEL_SOURCE"
    assert body.get("request_timeout_seconds") == 60
    assert body.get("gemini_max_retries_configured") == 0
    assert body.get("provider_key") == "gemini_pro"
    url = str(body.get("url") or "")
    assert url.startswith("https://generativelanguage.googleapis.com/")
    assert ":generateContent" in url
    assert "?" not in url or _FAKE_GOOGLE_STYLE_KEY not in url
