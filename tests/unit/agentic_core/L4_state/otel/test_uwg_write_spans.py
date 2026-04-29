"""Unit tests for `agentic_core.L4_state.otel.uwg_write_spans`.

Maps to: docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md
Phase 5 OTEL CONTRACT.
And: docs/reference/00B_L4_State_Archive_and_UWG/00B.8a_L4_UWG_State_Audit_Replay_Consistency_Tests.md
Phase 8 OTEL ASSERTION SHAPE.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.otel.uwg_write_spans import (
    clear_recorded_spans,
    emit_blocked_span,
    emit_committed_span,
    emit_compare_span,
    emit_context_frozen_span,
    emit_stage_emit_span,
    recorded_spans,
)


@pytest.fixture(autouse=True)
def _reset_recorder() -> None:
    clear_recorded_spans()


def _filler(seed: str) -> str:
    return (seed * 16)[:64]


class TestRecorderLifecycle:
    def test_clear_resets(self) -> None:
        emit_blocked_span(
            decisive_rule_id="UWG_COMMIT_BLOCKED",
            first_mismatched_stage="x",
            trace_id="t",
            sealed_receipt_id="s",
            terminal_class="T",
            rollback_required=False,
        )
        assert len(recorded_spans()) == 1
        clear_recorded_spans()
        assert recorded_spans() == ()


class TestSpanShapes:
    def test_context_frozen_span_carries_all_required_attrs(self) -> None:
        emit_context_frozen_span(
            durable_write_digest=_filler("a"),
            request_id="req-1",
            run_id="run-1",
            trace_id="trace-1",
            tenant_id="tenant-1",
            principal_id="prin-1",
            exit_disposition_id="x3-1",
            commit_request_id="cr-1",
            target_store_id="store-1",
            target_object_ref="obj-1",
            mutation_intent_class="UPDATE",
            state_diff_candidate_hash=_filler("d"),
            before_snapshot_hash=_filler("b"),
            after_candidate_hash=_filler("c"),
            schema_hash=_filler("s"),
            policy_hash=_filler("p"),
            blueprint_hash=_filler("u"),
            capability_scope_hash=_filler("e"),
            sandbox_envelope_hash=_filler("f"),
            l5_certification_packet_hash=_filler("L"),
            replay_key="replay-1",
            idempotency_key="idem-1",
            write_lock_id="lock-1",
            transaction_id="tx-1",
        )
        spans = recorded_spans()
        assert len(spans) == 1
        span = spans[0]
        assert span.name == "uwg.write.context.frozen"
        assert span.attributes["durable_write_digest"] == _filler("a")
        assert span.attributes["mutation_intent_class"] == "UPDATE"
        assert span.attributes["idempotency_key"] == "idem-1"

    def test_stage_emit_span(self) -> None:
        emit_stage_emit_span(
            stage_name="UWG_VALIDATION",
            stage_digest_alias="uwg_validation_digest",
            durable_write_digest=_filler("a"),
            stage_emitted_digest=_filler("a"),
            trace_id="trace-1",
        )
        span = recorded_spans()[0]
        assert span.name == "uwg.write.stage.emit"
        assert span.attributes["stage_name"] == "UWG_VALIDATION"
        assert span.attributes["stage_digest_alias"] == "uwg_validation_digest"

    def test_compare_span_match(self) -> None:
        emit_compare_span(
            chain_complete=True,
            all_match=True,
            first_mismatched_stage="",
            trace_id="trace-1",
        )
        span = recorded_spans()[0]
        assert span.name == "uwg.write.compare"
        assert span.attributes["all_match"] is True

    def test_compare_span_mismatch(self) -> None:
        emit_compare_span(
            chain_complete=True,
            all_match=False,
            first_mismatched_stage="audit_ledger_digest",
            trace_id="trace-1",
        )
        span = recorded_spans()[0]
        assert span.attributes["all_match"] is False
        assert span.attributes["first_mismatched_stage"] == "audit_ledger_digest"

    def test_committed_span(self) -> None:
        emit_committed_span(
            l4_state_receipt_digest=_filler("a"),
            audit_ledger_digest=_filler("a"),
            replay_snapshot_digest=_filler("a"),
            retrieval_cache_invalidation_digest=_filler("a"),
            trace_id="trace-1",
            transaction_id="tx-1",
            idempotency_key="idem-1",
            terminal_class="L4_DURABLE_COMMITTED",
        )
        span = recorded_spans()[0]
        assert span.name == "uwg.write.committed"
        assert span.attributes["idempotency_replay"] is False
        assert span.attributes["terminal_class"] == "L4_DURABLE_COMMITTED"

    def test_committed_span_idempotency_replay(self) -> None:
        emit_committed_span(
            l4_state_receipt_digest=_filler("a"),
            audit_ledger_digest=_filler("a"),
            replay_snapshot_digest=_filler("a"),
            retrieval_cache_invalidation_digest=_filler("a"),
            trace_id="trace-1",
            transaction_id="tx-1",
            idempotency_key="idem-1",
            terminal_class="L4_DURABLE_COMMITTED",
            idempotency_replay=True,
        )
        span = recorded_spans()[0]
        assert span.attributes["idempotency_replay"] is True

    def test_blocked_span_carries_decisive_rule_id_and_rollback(self) -> None:
        emit_blocked_span(
            decisive_rule_id="UWG_COMMIT_BLOCKED",
            first_mismatched_stage="audit_ledger_digest",
            trace_id="trace-1",
            sealed_receipt_id="uwg-receipt-abc",
            terminal_class="DURABLE_WRITE_CONTEXT_MISMATCH",
            rollback_required=True,
        )
        span = recorded_spans()[0]
        assert span.name == "uwg.write.blocked"
        assert span.attributes["decisive_rule_id"] == "UWG_COMMIT_BLOCKED"
        assert span.attributes["rollback_required"] is True


class TestSpanCardinality:
    """Mirrors 00B.8a Phase 8 cardinality assertions."""

    def test_match_path_no_blocked_span(self) -> None:
        emit_compare_span(
            chain_complete=True,
            all_match=True,
            first_mismatched_stage="",
            trace_id="t",
        )
        emit_committed_span(
            l4_state_receipt_digest=_filler("a"),
            audit_ledger_digest=_filler("a"),
            replay_snapshot_digest=_filler("a"),
            retrieval_cache_invalidation_digest=_filler("a"),
            trace_id="t",
            transaction_id="tx-1",
            idempotency_key="idem-1",
            terminal_class="L4_DURABLE_COMMITTED",
        )
        names = [s.name for s in recorded_spans()]
        assert "uwg.write.committed" in names
        assert "uwg.write.blocked" not in names

    def test_mismatch_path_no_committed_pre_commit(self) -> None:
        emit_compare_span(
            chain_complete=True,
            all_match=False,
            first_mismatched_stage="uwg_validation_digest",
            trace_id="t",
        )
        emit_blocked_span(
            decisive_rule_id="UWG_COMMIT_BLOCKED",
            first_mismatched_stage="uwg_validation_digest",
            trace_id="t",
            sealed_receipt_id="uwg-receipt-abc",
            terminal_class="DURABLE_WRITE_CONTEXT_MISMATCH",
            rollback_required=False,
        )
        names = [s.name for s in recorded_spans()]
        assert "uwg.write.blocked" in names
        assert "uwg.write.committed" not in names
