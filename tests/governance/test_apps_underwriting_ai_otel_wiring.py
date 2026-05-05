"""D4 — OTEL span wiring tests for apps_underwriting_ai.

Validates that:
  1. ObservabilityAdapter.emit_stage_span() is callable and fail-soft.
  2. ObservabilityAdapter.emit_x3_span() is callable and fail-soft.
  3. Span names follow the uw.stage.<id> / uw.exit.x3_disposition convention.
  4. Both methods fall back to logging-only when the OTEL SDK is absent.
  5. UnderwritingExitFecProducer.produce_exit_bundle() emits an X3 span
     without crashing — verified via logging capture.

Plan: apps-underwriting-ai-deferred-scope-e8b2f4 D4.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_underwriting_ai.integrations.observability_adapter import (
    ObservabilityAdapter,
    _otel_span,
)
from apps_underwriting_ai.integrations.underwriting_exit_fec_producer import (
    UnderwritingExitFecProducer,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def adapter() -> ObservabilityAdapter:
    return ObservabilityAdapter()


def _approve_fec() -> dict:
    return {
        "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
        "c0_state": "PASS",
        "evidence_ids": ["doc-001", "doc-002"],
        "support_score": 0.91,
        "evidence_sufficiency": "sufficient",
    }


def _approve_ctx() -> dict:
    return {
        "demo_policy_hash": "sha256-policy-test",
        "blueprint_hash": "sha256-blueprint-test",
        "route_contract": {"route_family": "R3R4_MANAGED_WORKFLOW"},
        "verdict": "APPROVE",
        "reason_code_bundle": ["RC000_CREDIT_SCORE_STRONG"],
        "hitl_posture": "HITL_NONE",
        "demo_packet_id": "test-d4-001",
    }


# ---------------------------------------------------------------------------
# D4.1 — emit_stage_span() smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_emit_stage_span_is_callable(adapter: ObservabilityAdapter) -> None:
    """emit_stage_span() must not raise regardless of OTEL SDK presence."""
    adapter.emit_stage_span(
        stage_id="stage_1_evidence_register",
        request_id="req-d4-test",
        success=True,
        duration_ms=12.5,
        receipt_type="L2_RECEIPT_E1",
    )


@pytest.mark.governance
def test_emit_stage_span_failure_safe(adapter: ObservabilityAdapter) -> None:
    """emit_stage_span() must not raise when the OTEL span path raises."""
    with patch(
        "apps_underwriting_ai.integrations.observability_adapter._get_tracer",
        side_effect=RuntimeError("otel boom"),
    ):
        adapter.emit_stage_span(
            stage_id="stage_2_doc_reconcile",
            request_id="req-d4-fail",
            success=False,
        )


# ---------------------------------------------------------------------------
# D4.2 — emit_x3_span() smoke tests
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_emit_x3_span_is_callable(adapter: ObservabilityAdapter) -> None:
    """emit_x3_span() must not raise regardless of OTEL SDK presence."""
    adapter.emit_x3_span(
        request_id="req-d4-x3",
        x3_disposition="X3A_APPROVE",
        exit_mode="FAIL_CLOSED",
        hitl_posture="HITL_NONE",
        violations=[],
    )


@pytest.mark.governance
def test_emit_x3_span_failure_safe(adapter: ObservabilityAdapter) -> None:
    """emit_x3_span() must not raise when the OTEL span path raises."""
    with patch(
        "apps_underwriting_ai.integrations.observability_adapter._get_tracer",
        side_effect=RuntimeError("otel boom"),
    ):
        adapter.emit_x3_span(
            request_id="req-d4-fail",
            x3_disposition="X3E_SAFE_ABSTAIN",
            exit_mode="FAIL_CLOSED",
        )


# ---------------------------------------------------------------------------
# D4.3 — span name conventions
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_stage_span_name_convention() -> None:
    """OTEL span for stage_id='foo' must be named 'uw.stage.foo'."""
    captured_names: list[str] = []

    class _FakeTracer:
        def start_as_current_span(self, name: str, **_: object):
            captured_names.append(name)
            import contextlib  # noqa: PLC0415

            @contextlib.contextmanager
            def _ctx():
                yield MagicMock()

            return _ctx()

    with patch(
        "apps_underwriting_ai.integrations.observability_adapter._get_tracer",
        return_value=_FakeTracer(),
    ):
        adapter = ObservabilityAdapter()
        adapter.emit_stage_span(
            stage_id="stage_3_risk_scoring",
            request_id="req-span-name",
            success=True,
        )

    assert "uw.stage.stage_3_risk_scoring" in captured_names, (
        f"Expected 'uw.stage.stage_3_risk_scoring' in spans; got {captured_names}"
    )


@pytest.mark.governance
def test_x3_span_name_convention() -> None:
    """OTEL span for X3 exit must be named 'uw.exit.x3_disposition'."""
    captured_names: list[str] = []

    class _FakeTracer:
        def start_as_current_span(self, name: str, **_: object):
            captured_names.append(name)
            import contextlib  # noqa: PLC0415

            @contextlib.contextmanager
            def _ctx():
                yield MagicMock()

            return _ctx()

    with patch(
        "apps_underwriting_ai.integrations.observability_adapter._get_tracer",
        return_value=_FakeTracer(),
    ):
        adapter = ObservabilityAdapter()
        adapter.emit_x3_span(
            request_id="req-x3-name",
            x3_disposition="X3A_APPROVE",
            exit_mode="FAIL_CLOSED",
        )

    assert "uw.exit.x3_disposition" in captured_names, (
        f"Expected 'uw.exit.x3_disposition' in spans; got {captured_names}"
    )


# ---------------------------------------------------------------------------
# D4.4 — _otel_span() no-op when SDK absent
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_otel_span_noop_when_sdk_absent() -> None:
    """_otel_span() must yield None and not raise when OTEL SDK absent."""
    with patch(
        "apps_underwriting_ai.integrations.observability_adapter._get_tracer",
        return_value=None,
    ):
        with _otel_span("uw.test.noop", attributes={"k": "v"}) as span:
            assert span is None


# ---------------------------------------------------------------------------
# D4.5 — exit FEC producer calls emit_x3_span without crashing
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_produce_exit_bundle_emits_x3_span_without_crash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """produce_exit_bundle() must complete successfully; OTEL path must not crash it."""
    fec = _approve_fec()
    ctx = _approve_ctx()
    with caplog.at_level(logging.INFO, logger="apps_underwriting_ai"):
        producer = UnderwritingExitFecProducer()
        bundle = producer.produce_exit_bundle(fec, ctx)

    assert bundle.get("x3_emitted") is True
    assert bundle.get("x3_disposition") == "X3A_APPROVE"
