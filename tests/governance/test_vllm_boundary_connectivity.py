"""vLLM Boundary Connectivity Governance Tests.

Validates that governance test paths never touch the network,
and that _call_vllm request/response parsing and error semantics
are deterministic and correctly mapped.

Compliance: REV 5 - routing_invariants_version = 1
"""

from __future__ import annotations

import io
import json
import urllib.error
import urllib.request

import pytest

pytestmark = pytest.mark.governance


# ---------------------------------------------------------------------------
# Test 1 — Governance functions never trigger urlopen
# ---------------------------------------------------------------------------


def test_generate_proposal_does_not_touch_network_when_not_called(
    monkeypatch,
) -> None:
    """normalize_payload, canonical_hash, and evaluate must not call urlopen."""

    def _urlopen_trap(*args, **kwargs):
        raise AssertionError("urlopen was called during governance path")

    monkeypatch.setattr(urllib.request, "urlopen", _urlopen_trap)

    from agentic_core.L4_state.config.vllm_routing_predicates import evaluate
    from tools.vllm_boundary_client import canonical_hash, normalize_payload

    # Exercise every governance-path function
    normalize_payload({"a": 1})
    canonical_hash({"a": 1})
    evaluate({"routing_version": "1"})
    evaluate({"routing_version": "1", "requires_policy_read": True})

    # If we reach here, urlopen was never called


# ---------------------------------------------------------------------------
# Test 2 — _call_vllm uses urlopen once and parses chat/completions
# ---------------------------------------------------------------------------


def test_call_vllm_uses_urlopen_once_and_parses_chat_completions(
    monkeypatch,
) -> None:
    """_call_vllm must call urlopen exactly once and parse the response."""
    call_log = []

    fake_body = json.dumps({"choices": [{"message": {"content": "OK"}}]}).encode("utf-8")

    class FakeResponse:
        def read(self):
            return fake_body

        def decode(self, _enc="utf-8"):
            return fake_body.decode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def _fake_urlopen(req, *, timeout=None):
        call_log.append({"url": req.full_url, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)
    monkeypatch.setenv("VLLM_BASE_URL", "http://test-host:9999/v1")
    monkeypatch.setenv("VLLM_MODEL_NAME", "test-model")

    # Reload module-level constants after env change
    import tools.vllm_boundary_client as bc

    monkeypatch.setattr(bc, "VLLM_BASE_URL", "http://test-host:9999/v1")
    monkeypatch.setattr(bc, "VLLM_MODEL_NAME", "test-model")

    result = bc._call_vllm("hi", {"temperature": 0, "top_p": 1})

    assert len(call_log) == 1, f"urlopen called {len(call_log)} times"
    assert call_log[0]["url"].endswith("/chat/completions")
    assert result == "OK"


# ---------------------------------------------------------------------------
# Test 3 — HTTPError maps to RuntimeError
# ---------------------------------------------------------------------------


def test_call_vllm_http_error_maps_to_runtimeerror(monkeypatch) -> None:
    """Non-2xx HTTP response must raise RuntimeError with status code."""

    def _fake_urlopen(req, *, timeout=None):
        raise urllib.error.HTTPError(
            url=req.full_url,
            code=400,
            msg="Bad Request",
            hdrs={},
            fp=io.BytesIO(b"invalid payload"),
        )

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    import tools.vllm_boundary_client as bc

    with pytest.raises(RuntimeError, match="400"):
        bc._call_vllm("hi", {})


# ---------------------------------------------------------------------------
# Test 4 — Timeout maps to TimeoutError
# ---------------------------------------------------------------------------


def test_call_vllm_timeout_maps_to_timeouterror(monkeypatch) -> None:
    """Socket timeout must raise TimeoutError."""

    def _fake_urlopen(req, *, timeout=None):
        raise urllib.error.URLError(reason=TimeoutError("timed out"))

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    import tools.vllm_boundary_client as bc

    with pytest.raises(TimeoutError, match="timed out"):
        bc._call_vllm("hi", {})


# ---------------------------------------------------------------------------
# Test 5 — Connection refused maps to ConnectionError
# ---------------------------------------------------------------------------


def test_call_vllm_connection_refused_maps_to_connectionerror(
    monkeypatch,
) -> None:
    """DNS/connection refused must raise ConnectionError."""

    def _fake_urlopen(req, *, timeout=None):
        raise urllib.error.URLError(reason=ConnectionRefusedError("Connection refused"))

    monkeypatch.setattr(urllib.request, "urlopen", _fake_urlopen)

    import tools.vllm_boundary_client as bc

    with pytest.raises(ConnectionError, match="connection failed"):
        bc._call_vllm("hi", {})
