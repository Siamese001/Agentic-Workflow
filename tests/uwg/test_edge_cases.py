"""Exhaustive UWG edge-case sweep.

Covers every validation failure code in `_validate`, every value in each
enumerated field, and every boundary condition that the doctrinal pack
requires to be fail-closed. Adds 30+ tests that go beyond the 38 hardening
tests added in commit 878cc2a913.

Failure-mode coverage matrix (13 reason codes from `_validate`):

| Reason code                                      | Where tested                                      |
|--------------------------------------------------|---------------------------------------------------|
| `non_exit_source`                                | commit_pipeline (existing)                        |
| `non_authorized:<surface>` (15 surfaces)         | test_no_direct_l4_write (existing)                |
| `missing::policy_hash`                           | commit_pipeline (existing)                        |
| `missing::blueprint_hash`                        | hardening (existing)                              |
| `missing::replay_key`                            | commit_pipeline (existing)                        |
| `missing::tenant_id`                             | THIS FILE                                         |
| `missing::request_id`                            | THIS FILE                                         |
| `missing::run_id`                                | THIS FILE                                         |
| `missing::trace_root`                            | THIS FILE                                         |
| `missing::gate_verdict_refs`                     | commit_pipeline (existing)                        |
| `unknown_operation::*`                           | commit_pipeline (existing)                        |
| `missing_target_surface::*`                      | THIS FILE                                         |
| `missing_rollback_plan_ref::*`                   | THIS FILE                                         |
| `missing_schema_ref::*`                          | commit_pipeline (existing)                        |
| `audit_ledger_unavailable`                       | THIS FILE                                         |
| `rollback_plan_id_mismatch`                      | THIS FILE                                         |
| `missing::refresh_plan_id`                       | THIS FILE                                         |
| `blast_radius_unbounded::*`                      | THIS FILE                                         |
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from agentic_core.L4_state.audit.audit_ledger import AuditLedger
from agentic_core.L4_state.contracts import StateDiff
from agentic_core.L4_state.uwg.durable_write_gateway import (
    ALLOWED_OPERATIONS,
    NON_AUTHORIZED_SOURCES,
    DurableWriteGateway,
)


# =====================================================================
# Validation failure-mode exhaustive coverage
# =====================================================================


class TestRequiredFieldsExhaustive:
    """Each of the 7 required CommitRequest fields blocks when empty."""

    @pytest.mark.parametrize(
        "field,reason_code",
        [
            ("tenant_id", "missing::tenant_id"),
            ("request_id", "missing::request_id"),
            ("run_id", "missing::run_id"),
            ("trace_root", "missing::trace_root"),
        ],
    )
    def test_each_required_field_blocks_when_empty(
        self, gateway, well_formed_packet, field, reason_code
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, **{field: ""})
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert reason_code in blocked.blocked_reason_codes


class TestStateDiffValidation:
    """State diff per-field validation: target_surface and rollback_plan_ref."""

    def test_state_diff_missing_target_surface_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad_diff = replace(diffs[0], target_surface="")
        commit, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=[bad_diff],
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert any(
            rc.startswith("missing_target_surface::") for rc in blocked.blocked_reason_codes
        )

    def test_state_diff_missing_rollback_plan_ref_blocks(
        self, gateway, well_formed_packet
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad_diff = replace(diffs[0], rollback_plan_ref="")
        commit, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=[bad_diff],
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert any(
            rc.startswith("missing_rollback_plan_ref::") for rc in blocked.blocked_reason_codes
        )

    def test_all_eleven_allowed_operations_accepted(self, gateway, well_formed_packet) -> None:
        """Every operation in the canonical 11-operation tuple commits successfully."""
        cr, diffs, rollback, refresh = well_formed_packet
        # Sanity: ALLOWED_OPERATIONS is the doctrinal 11
        assert len(ALLOWED_OPERATIONS) == 11
        for op in ALLOWED_OPERATIONS:
            diff = replace(diffs[0], operation_type=op, state_diff_id=f"sd:{op}")
            commit, blocked, _ = gateway.commit(
                commit_request=replace(cr, commit_request_id=f"cr:{op}"),
                state_diffs=[diff],
                rollback_plan=rollback,
                refresh_plan=refresh,
            )
            assert commit is not None, f"operation_type={op} should be accepted"
            assert blocked is None


class TestRollbackPlanLink:
    def test_rollback_plan_id_mismatch_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad_rollback = replace(rollback, rollback_plan_id="rp:DIFFERENT")
        commit, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=bad_rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "rollback_plan_id_mismatch" in blocked.blocked_reason_codes


class TestRefreshPlanLink:
    def test_missing_refresh_plan_id_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad_refresh = replace(refresh, refresh_plan_id="")
        commit, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=bad_refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "missing::refresh_plan_id" in blocked.blocked_reason_codes


class TestBlastRadiusBounded:
    """Every value in the canonical 5-value blast_radius enum is accepted; everything else blocks."""

    @pytest.mark.parametrize(
        "value",
        ["single_surface", "tenant_scoped", "route_scoped", "policy_scoped", "registry_scoped"],
    )
    def test_each_allowed_blast_radius_value_accepted(
        self, gateway, well_formed_packet, value
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit, blocked, _ = gateway.commit(
            commit_request=replace(cr, blast_radius=value),
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is not None
        assert blocked is None

    @pytest.mark.parametrize("value", ["unbounded", "global", "", "all", "WORLD"])
    def test_unknown_blast_radius_blocks(self, gateway, well_formed_packet, value) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit, blocked, _ = gateway.commit(
            commit_request=replace(cr, blast_radius=value),
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert any(
            rc.startswith("blast_radius_unbounded::") for rc in blocked.blocked_reason_codes
        )


class TestAuditLedgerUnavailable:
    def test_unavailable_audit_ledger_blocks_commit(self, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        ledger = AuditLedger()
        ledger.set_available(False)
        gw = DurableWriteGateway(audit_ledger=ledger)
        commit, blocked, _ = gw.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "audit_ledger_unavailable" in blocked.blocked_reason_codes


# =====================================================================
# Anti-bypass exhaustive coverage
# =====================================================================


class TestAntiBypassSurfacesExhaustive:
    """All 15 NON_AUTHORIZED_SOURCES surfaces are blocked individually."""

    def test_non_authorized_sources_set_size(self) -> None:
        """SSOT check: doctrine 00.6 §PHASE 1 lists exactly 15 non-authorized surfaces."""
        assert len(NON_AUTHORIZED_SOURCES) == 15

    @pytest.mark.parametrize("surface", sorted(NON_AUTHORIZED_SOURCES))
    def test_each_non_authorized_surface_blocks_with_specific_reason_code(
        self, gateway, well_formed_packet, surface
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, source_surface=surface)
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        # The non_authorized_source reason carries the surface name
        assert f"non_authorized:{surface}" in blocked.blocked_reason_codes


class TestEmptyAndWhitespaceSourceSurface:
    """Boundary: empty or whitespace source_surface should fail closed (not Exit)."""

    @pytest.mark.parametrize("value", ["", "  ", "\t", "exit", "EXIT"])
    def test_non_canonical_source_surface_blocks(
        self, gateway, well_formed_packet, value
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, source_surface=value)
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "non_exit_source" in blocked.blocked_reason_codes


# =====================================================================
# 00.6 — Sequential commit isolation
# =====================================================================


class TestSequentialCommitIsolation:
    def test_two_sequential_commits_produce_distinct_audit_records(
        self, gateway, well_formed_packet
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit1, _, _ = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        cr2 = replace(cr, commit_request_id="cr:2", request_id="req:2", run_id="run:2")
        commit2, _, _ = gateway.commit(
            commit_request=cr2,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit1 is not None and commit2 is not None
        assert commit1.commit_receipt_id != commit2.commit_receipt_id
        events = [r.event_type for r in gateway.audit_ledger.read()]
        assert events.count("commit_request_received") == 2
        assert events.count("atomic_commit_applied") == 2

    def test_blocked_commit_does_not_advance_snapshot(
        self, gateway, well_formed_packet
    ) -> None:
        """A FAIL-validation commit must NOT change the gateway's last snapshot."""
        cr, diffs, rollback, refresh = well_formed_packet
        snapshot_before = gateway._last_snapshot_id  # noqa: SLF001 — invariant probe
        bad = replace(cr, source_surface="L2")  # non-Exit
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        # Snapshot pointer unchanged
        assert gateway._last_snapshot_id == snapshot_before  # noqa: SLF001
