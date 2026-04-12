"""Evidence-governance regression tests — deterministic, no ChromaDB required.

Covers the full evidence-governed execution path:
  - WeakSupportDisposition enum + classify_evidence_support() correctness
  - evaluate_and_emit() adapter: returns (ExitGateResult, WeakSupportDisposition)
  - build_exit_artifact() exit artifact field completeness (X1A–X1D)
  - BUS T emission contract: evidence calls emit, legacy calls do not
  - ActionNode + ToolIntentExecutor sidecar wiring (presence only, no live calls)
  - Baseline threshold integrity: sealed constants match stored JSON

All tests are @pytest.mark.regression and @pytest.mark.retrieval_guard.
None require a live ChromaDB connection.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
    EvidenceMetrics,
    WeakSupportDisposition,
    build_exit_artifact,
    classify_evidence_support,
    evaluate_and_emit,
    _ABSTAIN_COVERAGE_THRESHOLD,
    _REFINE_COVERAGE_THRESHOLD,
    _GROUNDED_CITATION_THRESHOLD,
)
from agentic_core.L3_orchestration.reasoning.engines.evidence_shaper import (
    CitationAnchor,
    ContradictionFlag,
    EvidenceBundle,
)
from agentic_core.L2_execution.audit.telemetry_bus import BusType, get_telemetry_bus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASELINE_PATH = Path(__file__).parents[6] / "ops_scripts" / "ci" / "evidence_governance_baseline.json"


def _metrics(
    *,
    coverage: float = 0.80,
    citation: float = 0.90,
    contradiction: bool = False,
    grounded: bool = True,
) -> EvidenceMetrics:
    """Minimal EvidenceMetrics factory for parametric tests."""
    return EvidenceMetrics(
        citation_completeness=citation,
        support_coverage=coverage,
        contradiction_present=contradiction,
        provenance_completeness=0.90,
        exact_match_ratio=0.50,
        dedup_savings=0.10,
        grounded_replayable=grounded,
        retrieval_id="ret-test",
        collection="code_chunks",
        query_hash="abc123",
    )


def _minimal_bundle(
    *,
    coverage: float = 0.80,
    citation_confidence: float = 0.90,
    contradiction: bool = False,
) -> EvidenceBundle:
    """Minimal EvidenceBundle with one high-quality chunk — no ChromaDB call."""

    class _FakeChunk:
        chunk_id = "chunk-001"
        combined_score = coverage
        metadata: dict[str, Any] = {
            "canonical_digest": "d001",
            "file_path": "agentic_core/L3_orchestration/reasoning/engines/evidence_eval_bridge.py",
            "layer": "L3",
        }

    anchor = CitationAnchor(
        chunk_id="chunk-001",
        collection="code_chunks",
        canonical_digest="d001",
        file_path="agentic_core/L3_orchestration/reasoning/engines/evidence_eval_bridge.py",
        layer="L3",
        provenance_confidence=citation_confidence,
    )
    contradiction_flags = (
        [ContradictionFlag(id_a="c1", id_b="c2", reason="contradicts", score_a=0.9, score_b=0.85)]
        if contradiction
        else []
    )
    return EvidenceBundle(
        query="EvidenceBundle regression test query",
        collection="code_chunks",
        ranked_chunks=[_FakeChunk()],
        citation_anchors={"chunk-001": anchor},
        contradiction_flags=contradiction_flags,
        exact_match_winners=["chunk-001"],
        expanded_chunk_ids=[],
        shaping_stats={"input_count": 1, "after_dedup": 1},
    )


def _drain_bus_t_evidence() -> list[Any]:
    """Drain evidence_quality_metrics messages from BUS T."""
    bus = get_telemetry_bus()
    msgs = bus.drain(BusType.TELEMETRY, max_messages=200)
    return [m for m in msgs if getattr(m, "signal_type", "") == "evidence_quality_metrics"]


def _load_baseline() -> dict[str, Any]:
    with _BASELINE_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# TestWeakSupportDispositionContract
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.retrieval_guard
class TestWeakSupportDispositionContract:
    """classify_evidence_support() must produce the correct disposition for each case."""

    def test_low_coverage_produces_abstain(self):
        m = _metrics(coverage=0.10, contradiction=False, grounded=False)
        assert classify_evidence_support(m) == WeakSupportDisposition.ABSTAIN

    def test_contradiction_produces_escalate(self):
        m = _metrics(coverage=0.80, contradiction=True, grounded=True)
        assert classify_evidence_support(m) == WeakSupportDisposition.ESCALATE

    def test_marginal_coverage_produces_refine(self):
        m = _metrics(coverage=0.45, contradiction=False, grounded=True)
        assert classify_evidence_support(m) == WeakSupportDisposition.REFINE

    def test_high_quality_produces_proceed(self):
        m = _metrics(coverage=0.75, citation=0.80, contradiction=False, grounded=True)
        assert classify_evidence_support(m) == WeakSupportDisposition.PROCEED

    def test_escalate_takes_priority_over_low_coverage(self):
        m = _metrics(coverage=0.05, contradiction=True, grounded=False)
        assert classify_evidence_support(m) == WeakSupportDisposition.ESCALATE

    def test_boundary_at_abstain_threshold_grounded_false_is_abstain(self):
        m = _metrics(coverage=_ABSTAIN_COVERAGE_THRESHOLD, contradiction=False, grounded=False)
        assert classify_evidence_support(m) == WeakSupportDisposition.ABSTAIN

    def test_boundary_just_above_refine_with_good_citation_is_proceed(self):
        m = _metrics(
            coverage=_REFINE_COVERAGE_THRESHOLD + 0.01,
            citation=_GROUNDED_CITATION_THRESHOLD + 0.01,
            contradiction=False,
            grounded=True,
        )
        assert classify_evidence_support(m) == WeakSupportDisposition.PROCEED

    def test_low_citation_with_adequate_coverage_is_refine(self):
        m = _metrics(
            coverage=_REFINE_COVERAGE_THRESHOLD + 0.05,
            citation=_GROUNDED_CITATION_THRESHOLD - 0.05,
            contradiction=False,
            grounded=True,
        )
        assert classify_evidence_support(m) == WeakSupportDisposition.REFINE

    def test_disposition_is_deterministic_for_same_inputs(self):
        m = _metrics(coverage=0.50, contradiction=False, grounded=True)
        d1 = classify_evidence_support(m)
        d2 = classify_evidence_support(m)
        assert d1 == d2

    def test_all_four_disposition_values_reachable(self):
        dispositions = {
            classify_evidence_support(_metrics(coverage=0.10, grounded=False)),
            classify_evidence_support(_metrics(coverage=0.80, contradiction=True, grounded=True)),
            classify_evidence_support(_metrics(coverage=0.45, grounded=True)),
            classify_evidence_support(_metrics(coverage=0.75, citation=0.80, grounded=True)),
        }
        assert dispositions == {
            WeakSupportDisposition.ABSTAIN,
            WeakSupportDisposition.ESCALATE,
            WeakSupportDisposition.REFINE,
            WeakSupportDisposition.PROCEED,
        }

    def test_disposition_never_none(self):
        for m in [
            _metrics(coverage=0.0, grounded=False),
            _metrics(coverage=1.0, citation=1.0, grounded=True),
            _metrics(coverage=0.50, grounded=True),
            _metrics(coverage=0.80, contradiction=True),
        ]:
            assert classify_evidence_support(m) is not None


# ---------------------------------------------------------------------------
# TestExitArtifactFields
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.retrieval_guard
class TestExitArtifactFields:
    """build_exit_artifact() must produce all required X1A–X1D keys."""

    _REQUIRED_KEYS = {
        "rules_compliant",
        "answer_fit",
        "safety_clear",
        "grounded_replayable",
        "confidence_score",
    }

    def test_all_required_keys_present(self):
        bundle = _minimal_bundle()
        artifact = build_exit_artifact(bundle)
        assert self._REQUIRED_KEYS.issubset(artifact.keys()), (
            f"Missing keys: {self._REQUIRED_KEYS - artifact.keys()}"
        )

    def test_evidence_metrics_pass_through_present(self):
        bundle = _minimal_bundle()
        artifact = build_exit_artifact(bundle)
        assert "_evidence_metrics" in artifact

    def test_confidence_score_is_float_in_range(self):
        bundle = _minimal_bundle(coverage=0.70)
        artifact = build_exit_artifact(bundle)
        assert isinstance(artifact["confidence_score"], float)
        assert 0.0 <= artifact["confidence_score"] <= 1.0

    def test_grounded_replayable_is_bool(self):
        bundle = _minimal_bundle()
        artifact = build_exit_artifact(bundle)
        assert isinstance(artifact["grounded_replayable"], bool)

    def test_contradiction_sets_escalation_reason(self):
        bundle = _minimal_bundle(contradiction=True)
        artifact = build_exit_artifact(bundle)
        assert artifact.get("escalation_reason") is not None
        assert "contradiction" in str(artifact["escalation_reason"]).lower()

    def test_no_contradiction_has_no_escalation_reason(self):
        bundle = _minimal_bundle(contradiction=False)
        artifact = build_exit_artifact(bundle)
        assert artifact.get("escalation_reason") is None

    def test_evidence_metrics_has_citation_completeness(self):
        bundle = _minimal_bundle()
        artifact = build_exit_artifact(bundle)
        metrics_dict = artifact["_evidence_metrics"]
        assert "citation_completeness" in metrics_dict
        assert isinstance(metrics_dict["citation_completeness"], float)

    def test_minimum_field_count_matches_baseline(self):
        baseline = _load_baseline()
        min_count = baseline["thresholds"]["exit_artifact_minimum_field_count"]
        bundle = _minimal_bundle()
        artifact = build_exit_artifact(bundle)
        required_keys = set(baseline["thresholds"]["exit_artifact_required_keys"])
        present = required_keys.intersection(artifact.keys())
        assert len(present) >= min_count, (
            f"Only {len(present)}/{min_count} required exit artifact fields present"
        )


# ---------------------------------------------------------------------------
# TestEvaluateAndEmitAdapter
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.retrieval_guard
class TestEvaluateAndEmitAdapter:
    """evaluate_and_emit() must return (ExitGateResult, WeakSupportDisposition)."""

    def _fake_ctx(self, run_id: str = "run-test-001") -> SimpleNamespace:
        return SimpleNamespace(policy_hash=None, run_id=run_id)

    def test_returns_2_tuple(self):
        bundle = _minimal_bundle(coverage=0.80)
        result = evaluate_and_emit(bundle, self._fake_ctx())
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_second_element_is_weak_support_disposition(self):
        bundle = _minimal_bundle(coverage=0.80)
        _, disposition = evaluate_and_emit(bundle, self._fake_ctx())
        assert isinstance(disposition, WeakSupportDisposition)

    def test_weak_bundle_produces_abstain_or_refine(self):
        bundle = _minimal_bundle(coverage=0.10, citation_confidence=0.20)
        _, disposition = evaluate_and_emit(bundle, self._fake_ctx())
        assert disposition in (WeakSupportDisposition.ABSTAIN, WeakSupportDisposition.REFINE)

    def test_contradiction_bundle_produces_escalate(self):
        bundle = _minimal_bundle(contradiction=True)
        _, disposition = evaluate_and_emit(bundle, self._fake_ctx())
        assert disposition == WeakSupportDisposition.ESCALATE

    def test_high_quality_bundle_does_not_produce_abstain(self):
        bundle = _minimal_bundle(coverage=0.80, citation_confidence=0.95)
        _, disposition = evaluate_and_emit(bundle, self._fake_ctx())
        assert disposition != WeakSupportDisposition.ABSTAIN

    def test_gate_result_has_disposition_attribute(self):
        bundle = _minimal_bundle()
        gate_result, _ = evaluate_and_emit(bundle, self._fake_ctx())
        assert hasattr(gate_result, "disposition")

    def test_disposition_never_none(self):
        bundle = _minimal_bundle()
        _, disposition = evaluate_and_emit(bundle, self._fake_ctx())
        assert disposition is not None


# ---------------------------------------------------------------------------
# TestBusTEmissionContract
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.retrieval_guard
class TestBusTEmissionContract:
    """BUS T must receive evidence_quality_metrics on every evaluate_and_emit() call."""

    def test_evaluate_and_emit_emits_to_bus_t(self):
        _drain_bus_t_evidence()  # clear prior state
        bundle = _minimal_bundle(coverage=0.70)
        ctx = SimpleNamespace(policy_hash=None, run_id="bus-test-001")
        evaluate_and_emit(bundle, ctx)
        msgs = _drain_bus_t_evidence()
        assert len(msgs) >= 1, "evaluate_and_emit must publish to BUS T"

    def test_bus_t_payload_has_citation_completeness(self):
        _drain_bus_t_evidence()
        bundle = _minimal_bundle()
        ctx = SimpleNamespace(policy_hash=None, run_id="bus-test-002")
        evaluate_and_emit(bundle, ctx)
        msgs = _drain_bus_t_evidence()
        assert len(msgs) >= 1
        payload = msgs[0].payload
        assert "citation_completeness" in payload
        assert isinstance(payload["citation_completeness"], float)

    def test_bus_t_payload_has_no_durable_write_keys(self):
        _drain_bus_t_evidence()
        bundle = _minimal_bundle()
        ctx = SimpleNamespace(policy_hash=None, run_id="bus-test-003")
        evaluate_and_emit(bundle, ctx)
        msgs = _drain_bus_t_evidence()
        assert len(msgs) >= 1
        forbidden = {"write", "commit", "mutate", "store", "persist"}
        for key in msgs[0].payload:
            assert key.lower() not in forbidden, (
                f"BUS T payload key '{key}' suggests durable write — forbidden"
            )

    def test_bus_t_payload_has_support_coverage(self):
        _drain_bus_t_evidence()
        bundle = _minimal_bundle(coverage=0.72)
        ctx = SimpleNamespace(policy_hash=None, run_id="bus-test-004")
        evaluate_and_emit(bundle, ctx)
        msgs = _drain_bus_t_evidence()
        assert msgs[0].payload["support_coverage"] == pytest.approx(0.72, abs=0.02)

    def test_bus_t_message_is_telemetry_type(self):
        _drain_bus_t_evidence()
        bundle = _minimal_bundle()
        ctx = SimpleNamespace(policy_hash=None, run_id="bus-test-005")
        evaluate_and_emit(bundle, ctx)
        msgs = _drain_bus_t_evidence()
        assert msgs[0].bus_type == BusType.TELEMETRY


# ---------------------------------------------------------------------------
# TestLegacyCallerIsolation
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.retrieval_guard
class TestLegacyCallerIsolation:
    """Legacy callers (no evidence_bundle) must not emit evidence metrics to BUS T."""

    def test_action_node_without_bundle_emits_no_evidence_messages(self):
        from agentic_core.L2_execution.reasoning.action_node import ActionNode

        _drain_bus_t_evidence()
        node = ActionNode()
        try:
            node.act(reasoning={})
        except Exception:  # guardian: allow-broad-exception -- legacy path may raise (no real executor)
            pass
        msgs = _drain_bus_t_evidence()
        assert len(msgs) == 0, (
            f"Legacy ActionNode.act() with no evidence_bundle emitted {len(msgs)} evidence msg(s); expected 0"
        )

    def test_action_node_with_bundle_emits_evidence_messages(self):
        import agentic_core.L2_execution.reasoning.action_node as _an_mod
        from types import SimpleNamespace

        _drain_bus_t_evidence()
        bundle = _minimal_bundle(coverage=0.70)
        ctx = SimpleNamespace(policy_hash=None, run_id="an-sidecar-test")
        sidecar_fn = getattr(_an_mod, "_invoke_evidence_sidecar", None)
        assert sidecar_fn is not None, "_invoke_evidence_sidecar must exist at module level"
        sidecar_fn(bundle, ctx, "action_node.act")
        msgs = _drain_bus_t_evidence()
        assert len(msgs) >= 1, "_invoke_evidence_sidecar (action_node) must emit evidence metrics to BUS T"

    def test_evidence_sidecar_is_callable_on_action_node(self):
        import agentic_core.L2_execution.reasoning.action_node as _an_mod

        fn = getattr(_an_mod, "_invoke_evidence_sidecar", None)
        assert callable(fn), "action_node module must export _invoke_evidence_sidecar callable"

    def test_evidence_sidecar_is_callable_on_tool_intent_executor(self):
        import agentic_core.L2_execution.reasoning.tool_intent_executor as _tie_mod

        fn = getattr(_tie_mod, "_invoke_evidence_sidecar", None)
        assert callable(fn), "tool_intent_executor module must export _invoke_evidence_sidecar callable"


# ---------------------------------------------------------------------------
# TestBaselineIntegrity
# ---------------------------------------------------------------------------


@pytest.mark.regression
@pytest.mark.retrieval_guard
class TestBaselineIntegrity:
    """The stored baseline JSON must remain consistent with live code constants."""

    def test_baseline_file_exists(self):
        assert _BASELINE_PATH.exists(), f"Baseline file not found: {_BASELINE_PATH}"

    def test_baseline_is_valid_json(self):
        data = _load_baseline()
        assert isinstance(data, dict)

    def test_baseline_has_required_top_level_keys(self):
        data = _load_baseline()
        for key in ("thresholds", "gate_mode", "_version", "regression_commands"):
            assert key in data, f"Baseline missing top-level key: {key}"

    def test_baseline_abstain_threshold_matches_code(self):
        data = _load_baseline()
        baseline_val = data["thresholds"]["abstain_coverage_threshold"]
        assert baseline_val == pytest.approx(_ABSTAIN_COVERAGE_THRESHOLD), (
            f"Baseline abstain threshold {baseline_val} != code constant {_ABSTAIN_COVERAGE_THRESHOLD}"
        )

    def test_baseline_refine_threshold_matches_code(self):
        data = _load_baseline()
        baseline_val = data["thresholds"]["refine_coverage_threshold"]
        assert baseline_val == pytest.approx(_REFINE_COVERAGE_THRESHOLD), (
            f"Baseline refine threshold {baseline_val} != code constant {_REFINE_COVERAGE_THRESHOLD}"
        )

    def test_baseline_citation_threshold_matches_code(self):
        data = _load_baseline()
        baseline_val = data["thresholds"]["grounded_citation_threshold"]
        assert baseline_val == pytest.approx(_GROUNDED_CITATION_THRESHOLD), (
            f"Baseline citation threshold {baseline_val} != code constant {_GROUNDED_CITATION_THRESHOLD}"
        )

    def test_baseline_gate_mode_is_enforce(self):
        data = _load_baseline()
        assert data["gate_mode"] == "enforce", "Evidence governance baseline must be in 'enforce' mode"

    def test_baseline_exit_artifact_required_keys_match_build_exit_artifact(self):
        data = _load_baseline()
        baseline_keys = set(data["thresholds"]["exit_artifact_required_keys"])
        bundle = _minimal_bundle()
        artifact = build_exit_artifact(bundle)
        for key in baseline_keys:
            assert key in artifact, f"Baseline required key '{key}' absent from build_exit_artifact() output"

    def test_regression_command_keys_present(self):
        data = _load_baseline()
        cmds = data["regression_commands"]
        assert "unit_tests" in cmds
        assert "benchmark_check" in cmds
