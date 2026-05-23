"""UWG commit pipeline — l5_certification_ref fail-closed and receipt threading."""

from __future__ import annotations

from dataclasses import replace

import pytest

from agentic_core.L4_state.contracts import CommitRequest
from agentic_core.L4_state.contracts.records import stamp_digest


class TestCommitRequestL5CertRefFailClosed:
    def test_empty_l5_cert_ref_rejected_at_construction(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            stamp_digest(
                CommitRequest(
                    commit_request_id="cr:bad-l5",
                    cleared_exit_review_packet_ref="exr:1",
                    request_id="req:1",
                    run_id="run:1",
                    trace_root="trace:1",
                    tenant_id="t:1",
                    policy_hash="ph:1",
                    blueprint_hash="bh:1",
                    route_contract_ref="rc:1",
                    replay_key="rk:1",
                    rollback_plan_ref="rp:1",
                    blast_radius="single_surface",
                    state_diff_refs=("sd:1",),
                    gate_verdict_refs=("gv:1",),
                    affected_state_surfaces=("memory",),
                    expected_read_surface_refreshes=("memory_projection",),
                    l5_certification_ref="",
                )
            )

    def test_whitespace_l5_cert_ref_rejected(self) -> None:
        with pytest.raises(ValueError, match="l5_certification_ref"):
            stamp_digest(
                CommitRequest(
                    commit_request_id="cr:ws-l5",
                    cleared_exit_review_packet_ref="exr:1",
                    request_id="req:1",
                    run_id="run:1",
                    trace_root="trace:1",
                    tenant_id="t:1",
                    policy_hash="ph:1",
                    blueprint_hash="bh:1",
                    route_contract_ref="rc:1",
                    replay_key="rk:1",
                    rollback_plan_ref="rp:1",
                    blast_radius="single_surface",
                    state_diff_refs=("sd:1",),
                    gate_verdict_refs=("gv:1",),
                    affected_state_surfaces=("memory",),
                    expected_read_surface_refreshes=("memory_projection",),
                    l5_certification_ref="   ",
                )
            )


class TestCommitReceiptThreadsL5Ref:
    def test_happy_path_receipt_matches_request_ref(
        self, gateway, well_formed_packet
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit_receipt, blocked, _ = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert blocked is None
        assert commit_receipt is not None
        assert commit_receipt.l5_certification_ref == cr.l5_certification_ref

    def test_blocked_commit_does_not_emit_commit_receipt_with_empty_l5(
        self, gateway, well_formed_packet
    ) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, source_surface="L2")
        commit_receipt, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit_receipt is None
        assert blocked is not None
