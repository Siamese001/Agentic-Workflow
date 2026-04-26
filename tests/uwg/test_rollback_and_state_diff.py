"""UWG rollback and StateDiff tests.

Doctrine: ``docs/reference/00_L4_State_and_UWG/00.6_*`` §PHASE 3 + §PHASE 6.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from agentic_core.L4_state.contracts import RollbackPlan
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.otel.spans import get_emitted_spans
from agentic_core.L4_state.uwg.durable_write_gateway import ALLOWED_OPERATIONS


class TestStateDiffValidation:
    def test_unknown_operation_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(diffs[0], operation_type="i_made_this_up", deterministic_digest="")
        bad = stamp_digest(bad)
        commit, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=[bad],
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert any("unknown_operation::" in code for code in blocked.blocked_reason_codes)

    def test_missing_schema_ref_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(diffs[0], schema_ref="", deterministic_digest="")
        bad = stamp_digest(bad)
        commit, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=[bad],
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert any("missing_schema_ref::" in code for code in blocked.blocked_reason_codes)

    def test_allowed_operations_match_doctrine(self) -> None:
        # Per 00.6 §PHASE 3
        expected = {
            "append_record",
            "version_insert",
            "alias_swap",
            "cache_invalidate",
            "index_refresh",
            "graph_projection_refresh",
            "registry_update",
            "policy_version_publish",
            "memory_promotion",
            "rollback",
            "tombstone",
        }
        assert expected == set(ALLOWED_OPERATIONS)


class TestRollback:
    def test_rollback_after_commit(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is not None
        assert blocked is None

        rollback_receipt = gateway.rollback(
            rollback_plan=rollback,
            source_commit_receipt=commit,
            reason_codes=("test_rollback",),
        )
        assert rollback_receipt.snapshot_before_rollback == commit.snapshot_after
        assert rollback_receipt.snapshot_after_rollback != commit.snapshot_after
        assert rollback_receipt.audit_append_receipt_ref
        assert "test_rollback" in rollback_receipt.reason_codes

    def test_rollback_appends_audit_ledger(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit, _, _ = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is not None
        gateway.rollback(
            rollback_plan=rollback,
            source_commit_receipt=commit,
            reason_codes=("user_requested",),
        )
        events = {r.event_type for r in gateway.audit_ledger.read()}
        assert "rollback_applied" in events

    def test_rollback_emits_span(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit, _, _ = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is not None
        gateway.rollback(
            rollback_plan=rollback,
            source_commit_receipt=commit,
        )
        names = {s.name for s in get_emitted_spans()}
        assert "uwg.rollback.apply" in names

    def test_rollback_requires_before_snapshot(self, gateway) -> None:
        """A rollback against a commit with no snapshot_before must error."""
        from agentic_core.L4_state.contracts import UWGCommitReceipt

        empty_rollback = stamp_digest(
            RollbackPlan(rollback_plan_id="rp:empty", blast_radius="single_surface")
        )
        # Construct a fake commit receipt with empty snapshot_before to trigger the check
        bad_commit = UWGCommitReceipt(
            commit_receipt_id="cr:fake",
            commit_request_ref="r:1",
            write_lock_receipt_ref="wlr:1",
            uwg_validation_receipt_ref="uvr:1",
            snapshot_before="",  # <- the violation
            snapshot_after="snap:after",
            read_surface_refresh_plan_ref="rfp:1",
            audit_append_receipt_ref="aar:1",
            committed_at="0",
        )
        with pytest.raises(ValueError, match="snapshot_before"):
            gateway.rollback(
                rollback_plan=empty_rollback,
                source_commit_receipt=bad_commit,
            )
