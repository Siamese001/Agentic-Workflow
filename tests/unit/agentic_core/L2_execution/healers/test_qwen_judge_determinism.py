"""Determinism smoke test for QwenJudgeGateway (Wave 1 P1.4).

Plan: docs/archive/windsurf/legacy-tree/plans/apps-eval-qwen32b-rollout-b7c4d9.md

Scope
-----
Verifies wrapper-level determinism: given a fixed fake
QwenInferenceGateway that returns the SAME response for every call, 50
consecutive invocations of ``QwenJudgeGateway.judge`` must yield
byte-identical JudgeVerdict dicts (modulo latency, which is excluded
from the determinism contract).

What this test does NOT verify
------------------------------
Actual vLLM greedy-decoding determinism at ``temperature=0`` requires a
live Qwen server and belongs in an integration test (out of scope for
this unit smoke). This test locks the wrapper layer: rubric hashing,
prompt construction, JSON parsing, composite computation, hard-gate
handling, and marker payload.
"""

from __future__ import annotations

import asyncio
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L2_execution.healers.qwen_judge_gateway import (
    HardGateResult,
    JudgeRequest,
    JudgeVerdict,
    QwenJudgeGateway,
)

_RUBRIC_YAML = """\
rubric_id: test_judge_v1
applies_to:
  - test_hop
hard_gates:
  - gate_id: length_parity
    description: placeholder
    failure_mode: instant_reject
soft_dimensions:
  - dimension_id: groundedness
    weight: 0.50
    min_score: 0.60
  - dimension_id: clarity
    weight: 0.30
    min_score: 0.50
  - dimension_id: tone
    weight: 0.20
    min_score: 0.50
composite_threshold: 0.70
"""

# Fixed JSON response the fake gateway returns on every call.
_FAKE_JUDGE_RESPONSE = '{"groundedness": 0.82, "clarity": 0.78, "tone": 0.88}'


@dataclass(frozen=True)
class _FakeResponse:
    success: bool
    response: str | None
    confidence: float
    model_used: str
    latency_ms: float
    cached: bool = False
    tokens_used: int = 0
    error_message: str | None = None


class _FakeQwenGateway:
    """Fake QwenInferenceGateway returning a fixed JSON response."""

    model_id = "test-qwen-fake"

    def __init__(self, response_text: str) -> None:
        self._response_text = response_text
        self.call_count = 0

    async def infer(self, _request: Any) -> _FakeResponse:
        self.call_count += 1
        return _FakeResponse(
            success=True,
            response=self._response_text,
            confidence=0.9,
            model_used=self.model_id,
            latency_ms=10.0,
        )


def _strip_latency(verdict: JudgeVerdict) -> dict[str, Any]:
    """Return verdict.to_dict() minus the latency field.

    Latency is intentionally excluded from the determinism contract —
    wall-clock microsecond jitter is expected and does not indicate
    behavioral drift.
    """
    payload = verdict.to_dict()
    payload.pop("latency_ms", None)
    return payload


@pytest.fixture
def rubric_path(tmp_path: Path) -> Path:
    path = tmp_path / "test_rubric.yaml"
    path.write_text(_RUBRIC_YAML, encoding="utf-8")
    return path


@pytest.fixture
def qwen_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force is_qwen_available to True so the wrapper takes the LLM path."""
    import agentic_core.L2_execution.healers.qwen_judge_gateway as module

    monkeypatch.setattr(module, "is_qwen_available", lambda: True)


def test_judge_verdict_is_byte_identical_across_50_runs(
    rubric_path: Path, qwen_available: None
) -> None:
    """50 consecutive judges on the same input yield identical verdicts."""
    fake = _FakeQwenGateway(_FAKE_JUDGE_RESPONSE)
    gateway = QwenJudgeGateway(inference_gateway=fake)

    request = JudgeRequest(
        app_name="test_app",
        rubric_path=rubric_path,
        candidate_text="The deterministic system shipped in 6 weeks.",
        pre_computed_hard_gates=(
            HardGateResult(gate_id="length_parity", passed=True, detail="ok"),
        ),
        context_metadata={"jd_facets": ["platform", "shipping"]},
        emit_marker=False,  # don't spam the capture queue from the test
    )

    baseline: dict[str, Any] | None = None
    for iteration in range(50):
        verdict = asyncio.run(gateway.judge(request))
        payload = _strip_latency(verdict)
        if baseline is None:
            baseline = payload
            continue
        assert payload == baseline, (
            f"verdict drift detected at iteration {iteration}: "
            f"{payload!r} != {baseline!r}"
        )

    assert baseline is not None
    assert baseline["accepted"] is True
    # Composite = 0.50*0.82 + 0.30*0.78 + 0.20*0.88 = 0.820 (weights sum to 1.0)
    assert baseline["composite"] == pytest.approx(0.820, abs=1e-3)
    assert baseline["rubric_id"] == "test_judge_v1"
    assert baseline["fallback_reason"] == ""
    assert baseline["first_failed_gate"] is None
    assert fake.call_count == 50


def test_hard_gate_veto_is_deterministic(rubric_path: Path) -> None:
    """Hard-gate veto path returns without calling the LLM, same every time."""
    fake = _FakeQwenGateway("should not be called")
    gateway = QwenJudgeGateway(inference_gateway=fake)

    request = JudgeRequest(
        app_name="test_app",
        rubric_path=rubric_path,
        candidate_text="placeholder",
        pre_computed_hard_gates=(
            HardGateResult(
                gate_id="length_parity", passed=False, detail="too short"
            ),
        ),
        emit_marker=False,
    )

    baseline: dict[str, Any] | None = None
    for _ in range(10):
        verdict = asyncio.run(gateway.judge(request))
        payload = _strip_latency(verdict)
        if baseline is None:
            baseline = payload
        else:
            assert payload == baseline

    assert baseline is not None
    assert baseline["accepted"] is False
    assert baseline["fallback_reason"] == "hard_gate_veto"
    assert baseline["first_failed_gate"] == "length_parity"
    assert baseline["model_used"] == "deterministic_fallback"
    assert fake.call_count == 0


def test_preflight_failure_is_deterministic(
    rubric_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Preflight-failed path returns a deterministic fallback verdict."""
    import agentic_core.L2_execution.healers.qwen_judge_gateway as module

    monkeypatch.setattr(module, "is_qwen_available", lambda: False)

    fake = _FakeQwenGateway("should not be called")
    gateway = QwenJudgeGateway(inference_gateway=fake)

    request = JudgeRequest(
        app_name="test_app",
        rubric_path=rubric_path,
        candidate_text="candidate",
        pre_computed_hard_gates=(),
        emit_marker=False,
    )

    baseline: dict[str, Any] | None = None
    for _ in range(10):
        verdict = asyncio.run(gateway.judge(request))
        payload = _strip_latency(verdict)
        if baseline is None:
            baseline = payload
        else:
            assert payload == baseline

    assert baseline is not None
    assert baseline["accepted"] is False
    assert baseline["fallback_reason"] == "preflight_failed"
    assert baseline["first_failed_gate"] == "qwen_preflight_failed"
    assert fake.call_count == 0


def test_parse_failure_is_deterministic(
    rubric_path: Path, qwen_available: None
) -> None:
    """Non-JSON model response collapses to a deterministic parse_failure verdict."""
    fake = _FakeQwenGateway("definitely not json")
    gateway = QwenJudgeGateway(inference_gateway=fake)

    request = JudgeRequest(
        app_name="test_app",
        rubric_path=rubric_path,
        candidate_text="candidate",
        pre_computed_hard_gates=(),
        emit_marker=False,
    )

    baseline: dict[str, Any] | None = None
    for _ in range(10):
        verdict = asyncio.run(gateway.judge(request))
        payload = _strip_latency(verdict)
        if baseline is None:
            baseline = payload
        else:
            assert payload == baseline

    assert baseline is not None
    assert baseline["accepted"] is False
    assert baseline["fallback_reason"] == "parse_failure"
    assert baseline["first_failed_gate"] == "parse_failure"
    assert baseline["composite"] == 0.0


def test_rubric_hash_is_stable_across_calls(
    rubric_path: Path, qwen_available: None
) -> None:
    """The rubric hash is a content-derived SHA-256 prefix; must be stable."""
    fake = _FakeQwenGateway(_FAKE_JUDGE_RESPONSE)
    gateway = QwenJudgeGateway(inference_gateway=fake)

    request = JudgeRequest(
        app_name="test_app",
        rubric_path=rubric_path,
        candidate_text="candidate",
        pre_computed_hard_gates=(),
        emit_marker=False,
    )

    hashes: set[str] = set()
    for _ in range(5):
        verdict = asyncio.run(gateway.judge(request))
        hashes.add(verdict.rubric_hash)

    assert len(hashes) == 1, f"rubric hash drift: {hashes!r}"
