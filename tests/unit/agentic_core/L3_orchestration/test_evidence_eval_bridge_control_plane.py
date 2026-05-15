"""Control-plane proof: EvidenceBundle → ExitControlGate.evaluate → L6 packets."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
    build_exit_artifact,
    emit_bundle_telemetry,
    evaluate_and_emit,
)
from agentic_core.L5_safety.enforcement.exit_control_gate import ExitControlGate
from agentic_core.L5_safety.types.exit_disposition_types import ExitGateResult
from agentic_core.L6_observability.utils.evaluation.async_eval_packet import (
    get_async_eval_ingester,
    get_shadow_eval_ingester,
    reset_async_eval_ingester,
    reset_shadow_eval_ingester,
)


def _bundle(*, contra: bool = False) -> MagicMock:
    chunk = MagicMock()
    chunk.chunk_id = "c1"
    chunk.combined_score = 0.82
    anchor = MagicMock()
    anchor.provenance_confidence = 0.88
    b = MagicMock()
    b.ranked_chunks = [chunk]
    b.citation_anchors = {"c1": anchor}
    b.contradiction_flags = [object()] if contra else []
    b.collection = "code_chunks"
    b.query = "control-plane-proof"
    b.exact_match_winners = ["c1"]
    b.shaping_stats = {"input_count": 2, "after_dedup": 1}
    b.retrieval_id = "rid-proof-1"
    return b


def _ctx() -> MagicMock:
    c = MagicMock()
    c.run_id = "run-cp-1"
    c.trace_id = "trace-cp-1"
    c.policy_hash = "sha256:test-policy"
    return c


@pytest.fixture(autouse=True)
def _reset_queues() -> None:
    reset_async_eval_ingester()
    reset_shadow_eval_ingester()
    yield
    reset_async_eval_ingester()
    reset_shadow_eval_ingester()


def test_emit_bundle_telemetry_returns_metrics_and_matches_exit_artifact() -> None:
    bundle = _bundle()
    metrics = emit_bundle_telemetry(bundle, request_id="req-x", trace_id="tr-x")
    art = build_exit_artifact(bundle)
    assert art["_evidence_metrics"]["citation_completeness"] == pytest.approx(metrics.citation_completeness)
    assert art["_evidence_metrics"]["support_coverage"] == pytest.approx(metrics.support_coverage)


def test_evaluate_and_emit_uses_exit_control_gate_and_enriches_shadow_telemetry() -> None:
    bundle = _bundle()
    gate_result, wsd = evaluate_and_emit(bundle, _ctx(), tool_name="test.lane")

    assert isinstance(gate_result, ExitGateResult)
    assert gate_result.disposition.value in {
        "ALLOW_RESPONSE",
        "DENY_RETURN",
        "ESCALATE_TO_HITL",
        "COMMIT_TO_UWG",
    }
    assert wsd.value in {"ABSTAIN", "ESCALATE", "REFINE", "PROCEED"}

    assert get_async_eval_ingester().qsize() >= 1
    assert get_shadow_eval_ingester().qsize() >= 1
    shadow = get_shadow_eval_ingester().drain(max_packets=10)[0]
    assert shadow.telemetry.get("evidence_metrics_sealed"), "shadow must carry sealed evidence_metrics"
    assert "citation_completeness" in shadow.telemetry["evidence_metrics_sealed"]


def test_sealed_artifact_evidence_bundle_populated_for_evaluate_sealed() -> None:
    from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
        _build_sealed_l2_artifact,
    )

    bundle = _bundle()
    ctx = _ctx()
    exit_dict = build_exit_artifact(bundle)
    gate = ExitControlGate(policy_hash=ctx.policy_hash)
    exit_result = gate.evaluate(exit_dict)
    from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
        _compute_metrics,
    )

    metrics = _compute_metrics(bundle)
    sealed = _build_sealed_l2_artifact(
        bundle,
        ctx,
        exit_result=exit_result,
        metrics=metrics,
        exit_dict=exit_dict,
    )
    assert sealed.evidence_bundle.get("_evidence_metrics") is not None
    cr = gate.evaluate_sealed(sealed)
    assert cr.disposition == exit_result.disposition
