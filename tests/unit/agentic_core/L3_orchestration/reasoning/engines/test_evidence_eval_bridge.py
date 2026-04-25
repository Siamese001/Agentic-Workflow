"""Unit tests for agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge.

Targets Wave-3 / Phase P7. Source: 266 lines, fan_in=50 (L3, impact 87.5).
Covers the pure scoring/classification paths plus the top-level evaluate_and_emit
with telemetry + async-eval mocked out.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest import mock

import pytest

from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
    EvidenceMetrics,
    WeakSupportDisposition,
    _anchor_confidence,
    _bundle_query_hash,
    _bundle_retrieval_id,
    _chunk_score,
    _compute_metrics,
    _safe_float,
    _safe_len,
    build_exit_artifact,
    classify_evidence_support,
)


def _bundle(
    *,
    query: str = "q",
    collection: str = "c",
    anchors=None,
    ranked=None,
    contradictions=None,
    exact_winners=None,
    shaping=None,
    retrieval_id=None,
) -> SimpleNamespace:
    return SimpleNamespace(
        query=query,
        collection=collection,
        citation_anchors=anchors or {},
        ranked_chunks=ranked or [],
        contradiction_flags=contradictions or [],
        exact_match_winners=exact_winners or [],
        shaping_stats=shaping or {},
        retrieval_id=retrieval_id,
    )


class TestSafeHelpers:
    def test_safe_float_valid(self) -> None:
        assert _safe_float(1.5) == 1.5
        assert _safe_float("2.0") == 2.0
        assert _safe_float(3) == 3.0

    def test_safe_float_invalid_returns_default(self) -> None:
        assert _safe_float(None) == 0.0
        assert _safe_float("not-a-number") == 0.0
        assert _safe_float(object(), default=-1.0) == -1.0

    def test_safe_len_happy(self) -> None:
        assert _safe_len([1, 2, 3]) == 3
        assert _safe_len("abc") == 3

    def test_safe_len_non_sized(self) -> None:
        assert _safe_len(None) == 0
        assert _safe_len(42) == 0


class TestBundleHashers:
    def test_query_hash_deterministic(self) -> None:
        b1 = _bundle(query="same", collection="col")
        b2 = _bundle(query="same", collection="col")
        assert _bundle_query_hash(b1) == _bundle_query_hash(b2)

    def test_query_hash_differs_by_query(self) -> None:
        assert _bundle_query_hash(_bundle(query="a")) != _bundle_query_hash(_bundle(query="b"))

    def test_query_hash_truncated_to_16_chars(self) -> None:
        assert len(_bundle_query_hash(_bundle())) == 16

    def test_retrieval_id_uses_explicit(self) -> None:
        b = _bundle(retrieval_id="explicit-123")
        assert _bundle_retrieval_id(b) == "explicit-123"

    def test_retrieval_id_fallback_prefix(self) -> None:
        b = _bundle()
        # retrieval_id=None -> falls back
        assert _bundle_retrieval_id(b).startswith("ret-")


class TestAnchorAndChunkScoring:
    def test_anchor_confidence_from_dict(self) -> None:
        assert _anchor_confidence({"provenance_confidence": 0.8}) == 0.8

    def test_anchor_confidence_from_object(self) -> None:
        a = SimpleNamespace(provenance_confidence=0.5)
        assert _anchor_confidence(a) == 0.5

    def test_anchor_confidence_missing_returns_zero(self) -> None:
        assert _anchor_confidence({}) == 0.0

    def test_chunk_score_from_dict_combined_first(self) -> None:
        chunk = {"combined_score": 0.9, "score": 0.1, "vector_score": 0.2}
        assert _chunk_score(chunk) == 0.9

    def test_chunk_score_from_dict_falls_back(self) -> None:
        assert _chunk_score({"vector_score": 0.3}) == 0.3
        assert _chunk_score({}) == 0.0

    def test_chunk_score_from_object(self) -> None:
        c = SimpleNamespace(combined_score=0.7)
        assert _chunk_score(c) == 0.7

    def test_chunk_score_empty_object(self) -> None:
        assert _chunk_score(SimpleNamespace()) == 0.0


class TestComputeMetrics:
    def test_empty_bundle_produces_zeros(self) -> None:
        m = _compute_metrics(_bundle())
        assert m.citation_completeness == 0.0
        assert m.support_coverage == 0.0
        assert m.contradiction_present is False
        assert m.grounded_replayable is False

    def test_high_quality_bundle_grounded(self) -> None:
        m = _compute_metrics(
            _bundle(
                anchors={"a1": {"provenance_confidence": 0.9}, "a2": {"provenance_confidence": 0.85}},
                ranked=[{"combined_score": 0.9}],
            )
        )
        assert m.citation_completeness > 0.75
        assert m.support_coverage == 0.9
        assert m.grounded_replayable is True

    def test_contradiction_flags_block_grounded(self) -> None:
        m = _compute_metrics(
            _bundle(
                anchors={"a": {"provenance_confidence": 0.95}},
                ranked=[{"combined_score": 0.9}],
                contradictions=["conflict-1"],
            )
        )
        assert m.contradiction_present is True
        assert m.grounded_replayable is False

    def test_dedup_savings_computation(self) -> None:
        m = _compute_metrics(
            _bundle(
                ranked=[{}, {}],  # 2 after dedup
                shaping={"input_count": 10, "after_dedup": 2},
            )
        )
        # 1 - 2/10 = 0.8
        assert m.dedup_savings == pytest.approx(0.8)


class TestClassifyEvidenceSupport:
    def _metrics(self, **kwargs) -> EvidenceMetrics:
        defaults = {
            "citation_completeness": 0.8,
            "support_coverage": 0.7,
            "contradiction_present": False,
            "provenance_completeness": 0.8,
            "exact_match_ratio": 0.5,
            "dedup_savings": 0.0,
            "grounded_replayable": True,
            "retrieval_id": "r-1",
            "collection": "c",
            "query_hash": "h" * 16,
        }
        defaults.update(kwargs)
        return EvidenceMetrics(**defaults)  # type: ignore[arg-type]

    def test_contradiction_forces_escalate(self) -> None:
        m = self._metrics(contradiction_present=True)
        assert classify_evidence_support(m) == WeakSupportDisposition.ESCALATE

    def test_low_coverage_ungrounded_abstain(self) -> None:
        m = self._metrics(support_coverage=0.15, grounded_replayable=False)
        assert classify_evidence_support(m) == WeakSupportDisposition.ABSTAIN

    def test_mid_coverage_refine(self) -> None:
        m = self._metrics(support_coverage=0.3)
        assert classify_evidence_support(m) == WeakSupportDisposition.REFINE

    def test_low_citation_refine(self) -> None:
        m = self._metrics(support_coverage=0.9, citation_completeness=0.5)
        assert classify_evidence_support(m) == WeakSupportDisposition.REFINE

    def test_high_quality_proceed(self) -> None:
        m = self._metrics(support_coverage=0.9, citation_completeness=0.9)
        assert classify_evidence_support(m) == WeakSupportDisposition.PROCEED


class TestBuildExitArtifact:
    def test_contradiction_disables_rules_compliant(self) -> None:
        b = _bundle(contradictions=["x"])
        a = build_exit_artifact(b)
        assert a["rules_compliant"] is False
        assert a["safety_clear"] is False
        assert a["escalation_reason"] == "evidence_contradiction_detected"

    def test_clean_bundle_no_escalation_reason(self) -> None:
        b = _bundle(anchors={"a": {"provenance_confidence": 0.9}}, ranked=[{"combined_score": 0.9}])
        a = build_exit_artifact(b)
        assert a["rules_compliant"] is True
        assert a["escalation_reason"] is None

    def test_artifact_has_all_keys(self) -> None:
        a = build_exit_artifact(_bundle())
        assert {
            "rules_compliant",
            "answer_fit",
            "safety_clear",
            "grounded_replayable",
            "confidence_score",
            "escalation_reason",
            "_evidence_metrics",
        } <= set(a.keys())

    def test_confidence_score_bounded(self) -> None:
        a = build_exit_artifact(_bundle())
        assert 0.0 <= a["confidence_score"] <= 1.0


class TestEvaluateAndEmit:
    """Happy-path integration tests for the public pipeline.

    Source bugs fixed 2026-04-24:
    - ``_publish_metrics`` now calls ``TelemetryBus.publish(...)`` with
      per-field kwargs instead of a malformed ``BusMessage(...)``.
    - ``_build_sealed_l2_artifact`` now passes ``artifact_id=...`` (required)
      and omits ``run_scope`` (ClassVar sentinel).
    """

    def test_end_to_end_with_empty_bundle_returns_abstain(self) -> None:
        from agentic_core.L3_orchestration.reasoning.engines import evidence_eval_bridge as mod

        with (
            mock.patch.object(mod, "get_telemetry_bus") as gb,
            mock.patch.object(mod, "get_async_eval_ingester") as gi,
            mock.patch.object(mod, "enqueue_shadow_eval_packet"),
        ):
            bus = mock.Mock()
            bus.publish.return_value = True
            gb.return_value = bus
            gi.return_value = mock.Mock()
            ctx = SimpleNamespace(run_id="r-1", trace_id="t-1", policy_hash="ph-1")
            gate_result, disposition = mod.evaluate_and_emit(_bundle(), ctx)
            assert disposition == WeakSupportDisposition.ABSTAIN
            assert gate_result.disposition.value == "DENY_RETURN"
            # publish was called with proper kwargs (no BusMessage TypeError)
            bus.publish.assert_called_once()
            call_kwargs = bus.publish.call_args.kwargs
            assert call_kwargs["signal_type"] == "evidence_quality_metrics"
            assert call_kwargs["trace_id"] == "t-1"

    def test_end_to_end_proceed_path(self) -> None:
        from agentic_core.L3_orchestration.reasoning.engines import evidence_eval_bridge as mod

        with (
            mock.patch.object(mod, "get_telemetry_bus") as gb,
            mock.patch.object(mod, "get_async_eval_ingester") as gi,
            mock.patch.object(mod, "enqueue_shadow_eval_packet"),
        ):
            bus = mock.Mock()
            bus.publish.return_value = True
            gb.return_value = bus
            gi.return_value = mock.Mock()
            good_bundle = _bundle(
                anchors={"a": {"provenance_confidence": 0.95}},
                ranked=[{"combined_score": 0.9}],
            )
            ctx = SimpleNamespace(run_id="r-2", trace_id="t-2", policy_hash="ph")
            _, disposition = mod.evaluate_and_emit(good_bundle, ctx)
            assert disposition == WeakSupportDisposition.PROCEED

    def test_sealed_artifact_construction_does_not_crash(self) -> None:
        # Direct call to _build_sealed_l2_artifact — verifies the ClassVar fix.
        from agentic_core.L3_orchestration.reasoning.engines import evidence_eval_bridge as mod

        ctx = SimpleNamespace(run_id="r", trace_id="t", policy_hash="ph")
        gate_result = SimpleNamespace(disposition=SimpleNamespace(value="PROCEED"))
        artifact = mod._build_sealed_l2_artifact(_bundle(), ctx, gate_result=gate_result)
        assert artifact.trace_id == "t"
        assert artifact.artifact_id.startswith("seal-")
        # run_scope remains the ClassVar sentinel — not an instance attribute override
        assert artifact.run_scope == "CURRENT_RUN"
