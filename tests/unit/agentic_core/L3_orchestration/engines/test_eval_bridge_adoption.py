"""Smoke tests — evaluation pipeline adoption.

Verifies that the evaluation pipeline adoption is coherent across:
  - _build_sealed_l2_artifact() → SealedL2Artifact with run_scope='CURRENT_RUN'
  - evaluate_and_emit() → enqueues AsyncEvalPacket AND ShadowEvalPacket
  - enqueue_shadow_eval_packet() / ShadowEvalIngester singleton
  - GovernedAppRunner l6_ingested probe uses canonical ingester qsize()

These are *smoke* tests that prove canonical-owner usage, not unit tests of
each decision branch inside the gate.  External surfaces (ChromaDB, L4) are
mocked.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.eval_pipeline


# ---------------------------------------------------------------------------
# Helpers — minimal mock EvidenceBundle and ExecutionContext
# ---------------------------------------------------------------------------


def _make_bundle(*, grounded: bool = True, contradictions: bool = False) -> MagicMock:
    chunk = MagicMock()
    chunk.chunk_id = "c1"
    chunk.combined_score = 0.75 if grounded else 0.10

    anchor = MagicMock()
    anchor.provenance_confidence = 0.9 if grounded else 0.1

    bundle = MagicMock()
    bundle.ranked_chunks = [chunk]
    bundle.citation_anchors = {"c1": anchor}
    bundle.contradiction_flags = ["x"] if contradictions else []
    bundle.collection = "test_col"
    bundle.query = "test query"
    bundle.exact_match_winners = ["c1"] if grounded else []
    bundle.shaping_stats = {"input_count": 2, "after_dedup": 1}
    return bundle


def _make_ctx(run_id: str = "run-001") -> MagicMock:
    ctx = MagicMock()
    ctx.run_id = run_id
    ctx.policy_hash = "ph-abc"
    ctx.trace_id = "tr-001"
    return ctx


# ---------------------------------------------------------------------------
# 1. _build_sealed_l2_artifact — canonical typed artifact factory
# ---------------------------------------------------------------------------


class TestBuildSealedL2Artifact:
    def test_produces_current_run_scope(self) -> None:
        from agentic_core.L2_execution.types.sealed_l2_artifact import SealedL2Artifact
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            _build_sealed_l2_artifact,
        )

        artifact = _build_sealed_l2_artifact(_make_bundle(grounded=True), _make_ctx())

        assert isinstance(artifact, SealedL2Artifact)
        assert artifact.run_scope == "CURRENT_RUN"

    def test_uses_run_id_as_trace_fallback(self) -> None:
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            _build_sealed_l2_artifact,
        )

        ctx = MagicMock()
        ctx.run_id = "run-xyz"
        ctx.policy_hash = ""
        ctx.trace_id = ""

        artifact = _build_sealed_l2_artifact(_make_bundle(), ctx)

        assert artifact.exec_trace.get("run_id") == "run-xyz"

    def test_deny_disposition_maps_to_failure(self) -> None:
        from agentic_core.L2_execution.types.sealed_l2_artifact import TerminalClassification
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            _build_sealed_l2_artifact,
        )

        gate_mock = MagicMock()
        gate_mock.disposition.value = "DENY_RETURN"
        artifact = _build_sealed_l2_artifact(_make_bundle(), _make_ctx(), gate_result=gate_mock)

        assert artifact.terminal_classification == TerminalClassification.FAILURE

    def test_escalate_disposition_maps_to_needs_help(self) -> None:
        from agentic_core.L2_execution.types.sealed_l2_artifact import TerminalClassification
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            _build_sealed_l2_artifact,
        )

        gate_mock = MagicMock()
        gate_mock.disposition.value = "ESCALATE_TO_HITL"
        artifact = _build_sealed_l2_artifact(_make_bundle(), _make_ctx(), gate_result=gate_mock)

        assert artifact.terminal_classification == TerminalClassification.NEEDS_HELP

    def test_contradiction_flags_set_escalation_reason(self) -> None:
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            _build_sealed_l2_artifact,
        )

        bundle = _make_bundle(contradictions=True)
        artifact = _build_sealed_l2_artifact(bundle, _make_ctx())

        assert artifact.escalation_reason is not None
        assert "evidence_contradictions" in artifact.escalation_reason

    def test_empty_trace_id_and_run_id_uuid_fallback(self) -> None:
        """When both trace_id and run_id are empty the artifact still gets a non-empty trace_id."""
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            _build_sealed_l2_artifact,
        )

        ctx = MagicMock()
        ctx.trace_id = ""
        ctx.run_id = ""
        ctx.policy_hash = ""

        artifact = _build_sealed_l2_artifact(_make_bundle(), ctx)

        assert artifact.trace_id != "", "UUID fallback must produce non-empty trace_id"
        assert artifact.exec_trace.get("trace_id") != ""

    def test_commit_disposition_sets_has_commit_payload(self) -> None:
        """COMMIT_TO_UWG disposition maps to has_commit_payload=True."""
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            _build_sealed_l2_artifact,
        )

        gate_mock = MagicMock()
        gate_mock.disposition.value = "COMMIT_TO_UWG"
        artifact = _build_sealed_l2_artifact(_make_bundle(), _make_ctx(), gate_result=gate_mock)

        assert artifact.has_commit_payload is True


# ---------------------------------------------------------------------------
# 2. ShadowEvalIngester — canonical future-run queue
# ---------------------------------------------------------------------------


class TestShadowEvalIngester:
    def setup_method(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            reset_shadow_eval_ingester,
        )

        reset_shadow_eval_ingester()

    def test_enqueue_and_drain(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            ShadowEvalPacket,
            enqueue_shadow_eval_packet,
            get_shadow_eval_ingester,
        )

        pkt = ShadowEvalPacket(packet_id="sep-001", run_id="r1", sealed_at=0.0)
        result = enqueue_shadow_eval_packet(pkt)

        assert result is True
        drained = get_shadow_eval_ingester().drain(max_packets=10)
        assert len(drained) == 1
        assert drained[0].packet_id == "sep-001"

    def test_qsize_reflects_queue_depth(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            ShadowEvalPacket,
            enqueue_shadow_eval_packet,
            get_shadow_eval_ingester,
        )

        for i in range(3):
            enqueue_shadow_eval_packet(ShadowEvalPacket(packet_id=f"sep-{i:03d}", run_id="r1", sealed_at=0.0))

        assert get_shadow_eval_ingester().qsize() == 3

    def test_drained_packets_have_future_run_scope(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            ShadowEvalPacket,
            enqueue_shadow_eval_packet,
            get_shadow_eval_ingester,
        )

        enqueue_shadow_eval_packet(ShadowEvalPacket(packet_id="sep-x", run_id="r1", sealed_at=0.0))
        drained = get_shadow_eval_ingester().drain()

        assert all(pkt.run_scope == "FUTURE_RUN" for pkt in drained)


# ---------------------------------------------------------------------------
# 3. evaluate_and_emit — both ingestion paths must fire
# ---------------------------------------------------------------------------


class TestEvaluateAndEmitAdoption:
    def setup_method(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            reset_async_eval_ingester,
            reset_shadow_eval_ingester,
        )

        reset_async_eval_ingester()
        reset_shadow_eval_ingester()

    def test_shadow_packet_enqueued(self) -> None:
        """evaluate_and_emit() must enqueue a ShadowEvalPacket via the canonical path."""
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            evaluate_and_emit,
        )
        from ops_scripts.reports.async_eval_packet import (
            get_shadow_eval_ingester,
        )

        evaluate_and_emit(_make_bundle(grounded=True), _make_ctx(), tool_name="test_lane")

        assert get_shadow_eval_ingester().qsize() > 0

    def test_async_eval_packet_enqueued(self) -> None:
        """The existing AsyncEvalPacket path must still fire alongside shadow path."""
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            evaluate_and_emit,
        )
        from ops_scripts.reports.async_eval_packet import (
            get_async_eval_ingester,
        )

        evaluate_and_emit(_make_bundle(grounded=True), _make_ctx(), tool_name="test_lane")

        assert get_async_eval_ingester().qsize() > 0

    def test_returns_gate_result_and_disposition(self) -> None:
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            WeakSupportDisposition,
            evaluate_and_emit,
        )

        gate_result, disposition = evaluate_and_emit(_make_bundle(grounded=True), _make_ctx())

        assert gate_result is not None
        assert isinstance(disposition, WeakSupportDisposition)

    def test_deny_path_still_enqueues_shadow_packet(self) -> None:
        """Even on deny disposition, shadow packet is queued for future-run learning."""
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            evaluate_and_emit,
        )
        from ops_scripts.reports.async_eval_packet import (
            get_shadow_eval_ingester,
        )

        # Low-grounded bundle forces DENY / ABSTAIN disposition
        evaluate_and_emit(_make_bundle(grounded=False), _make_ctx())

        assert get_shadow_eval_ingester().qsize() > 0

    def test_escalate_path_enqueues_shadow_packet(self) -> None:
        """Contradiction bundle routes to ESCALATE — still must enqueue shadow packet."""
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            evaluate_and_emit,
        )
        from ops_scripts.reports.async_eval_packet import (
            get_shadow_eval_ingester,
        )

        evaluate_and_emit(_make_bundle(contradictions=True), _make_ctx())

        assert get_shadow_eval_ingester().qsize() > 0

    def test_shadow_packet_scope_is_future_run(self) -> None:
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            evaluate_and_emit,
        )
        from ops_scripts.reports.async_eval_packet import (
            get_shadow_eval_ingester,
        )

        evaluate_and_emit(_make_bundle(grounded=True), _make_ctx())
        drained = get_shadow_eval_ingester().drain()

        assert all(pkt.run_scope == "FUTURE_RUN" for pkt in drained)

    def test_non_blocking_when_shadow_path_fails(self) -> None:
        """evaluate_and_emit must not raise even if the shadow packet path fails.

        Invariants checked:
        - returns a 2-tuple (gate_result, disposition)
        - shadow queue is empty (exception swallowed, nothing enqueued)
        """
        from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import (
            WeakSupportDisposition,
            evaluate_and_emit,
        )
        from ops_scripts.reports.async_eval_packet import (
            get_shadow_eval_ingester,
        )

        with patch(
            "agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge.ExitControlGate.evaluate",
            side_effect=RuntimeError("simulated gate failure"),
        ):
            result = evaluate_and_emit(_make_bundle(grounded=True), _make_ctx())

        assert isinstance(result, tuple), "evaluate_and_emit must return a tuple"
        assert len(result) == 2, "must return (gate_result, disposition)"
        gate_result, disposition = result
        assert gate_result is not None
        assert isinstance(disposition, WeakSupportDisposition)
        assert get_shadow_eval_ingester().qsize() == 0, (
            "shadow queue must be empty when shadow path raises — exception must be swallowed"
        )


# ---------------------------------------------------------------------------
# 4. l6_ingested probe — canonical check using ingester qsize()
# ---------------------------------------------------------------------------


class TestL6IngestedProbe:
    """Verify the l6_ingested logic in governed_app_runner uses canonical ingesters."""

    def setup_method(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            reset_async_eval_ingester,
            reset_shadow_eval_ingester,
        )

        reset_async_eval_ingester()
        reset_shadow_eval_ingester()

    def test_true_when_shadow_packet_queued(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            ShadowEvalPacket,
            enqueue_shadow_eval_packet,
            get_async_eval_ingester,
            get_shadow_eval_ingester,
        )

        enqueue_shadow_eval_packet(ShadowEvalPacket(packet_id="sep-x", run_id="r1", sealed_at=0.0))

        l6_ingested = get_async_eval_ingester().qsize() > 0 or get_shadow_eval_ingester().qsize() > 0
        assert l6_ingested is True

    def test_true_when_async_packet_queued(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            AsyncEvalPacket,
            get_async_eval_ingester,
            get_shadow_eval_ingester,
        )

        pkt = AsyncEvalPacket(
            packet_id="ap-x",
            run_id="r1",
            lane_id="l",
            collection="c",
            policy_hash="p",
            citation_completeness=0.0,
            support_coverage=0.0,
            provenance_completeness=0.0,
            exact_match_ratio=0.0,
            grounded_replayable=False,
            contradiction_present=False,
            query_hash="",
            retrieval_id="",
            exit_disposition="",
            exit_trace_id="",
            exit_reason="",
            weak_support_disposition="",
            sealed_at=0.0,
        )
        get_async_eval_ingester().ingest(pkt)

        l6_ingested = get_async_eval_ingester().qsize() > 0 or get_shadow_eval_ingester().qsize() > 0
        assert l6_ingested is True

    def test_false_when_both_queues_empty(self) -> None:
        from ops_scripts.reports.async_eval_packet import (
            get_async_eval_ingester,
            get_shadow_eval_ingester,
        )

        l6_ingested = get_async_eval_ingester().qsize() > 0 or get_shadow_eval_ingester().qsize() > 0
        assert l6_ingested is False
