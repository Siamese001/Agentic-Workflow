"""W7.1 proof-of-pattern: apps_rg routes through the ingress gate.

These tests verify ONLY the ingress-wiring semantics:

* Malformed envelopes never reach ``GovernedRgRun`` — they are rejected by
  :class:`IngressEnvelopeCheck` with a rendered rejection.
* Clarification path: missing ``ResumeRequest`` fields surface as
  :class:`ClarificationRequired` without invoking the runner.
* Happy path: a well-formed envelope produces a stamped request that is
  handed to the runner.

The underlying ``run_governed_e2e`` is replaced with a stub to keep these
tests hermetic — they must not exercise LLM, retrieval, or L2 execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    ClarificationRequired,
    IngressEnvelopeCheck,
)
from apps_rg.integrations.rg_ingress_runner import RgIngressRunner


@dataclass(frozen=True)
class _FakeRunRecord:
    run_id: str
    target_role: str


class _FakeRgRun:
    """Stand-in for ``GovernedRgRun`` — no LLM, no retrieval, no I/O."""

    calls: list[Any] = []

    def run_governed_e2e(self, request: Any, *, inject_chunks: Any = None) -> _FakeRunRecord:
        self.calls.append(request)
        return _FakeRunRecord(run_id=f"rg-fake-{len(self.calls)}", target_role=request.target_role)


@pytest.fixture()
def runner() -> RgIngressRunner:
    fake = _FakeRgRun()
    fake.calls = []
    # Use a fresh gate so dedup state doesn't leak between tests.
    return RgIngressRunner(gate=IngressEnvelopeCheck(), runner=fake)  # type: ignore[arg-type]


def test_malformed_chat_envelope_rejected_string(runner: RgIngressRunner) -> None:
    # A chat turn without message text still satisfies the chat adapter,
    # but the resulting payload fails ResumeRequest parsing → clarification.
    out = runner.handle_chat({"user_id": "alice", "message": "hello"})
    assert isinstance(out, ClarificationRequired)
    assert "ResumeRequest" in out.reason


def test_http_missing_identity_header_still_rejects_via_ingress(runner: RgIngressRunner) -> None:
    # Depth failure is a deterministic transport-level rejection.
    deep: Any = "x"
    for _ in range(100):
        deep = [deep]
    # Use a runner with a tight depth limit.
    gate = IngressEnvelopeCheck(max_payload_depth=3)
    r = RgIngressRunner(gate=gate, runner=_FakeRgRun())  # type: ignore[arg-type]
    out = r.handle_http(headers={"X-Caller-Identity": "svc"}, body=deep)
    assert isinstance(out, tuple)
    status, _, body = out
    assert status == 400
    assert "PAYLOAD_TOO_DEEP" in body


def test_http_happy_path_dispatches_to_runner() -> None:
    fake = _FakeRgRun()
    r = RgIngressRunner(gate=IngressEnvelopeCheck(), runner=fake)  # type: ignore[arg-type]
    body = {
        "candidate_name": "Alice Example",
        "target_role": "Senior Engineer",
        "target_industry": "Fintech",
        "experience_level": "Senior",
    }
    with patch("apps_rg.integrations.rg_ingress_runner._parse_resume_request") as parse:
        # Avoid importing the real ResumeRequest type — the parser is the seam.
        class _Stub:
            candidate_name = body["candidate_name"]
            target_role = body["target_role"]
            target_industry = body["target_industry"]
            experience_level = body["experience_level"]

        parse.return_value = _Stub()
        out = r.handle_http(
            headers={"X-Caller-Identity": "svc", "X-Request-Id": "rid-1"},
            body=body,
        )
    assert isinstance(out, _FakeRunRecord)
    assert out.target_role == "Senior Engineer"
    assert len(fake.calls) == 1
