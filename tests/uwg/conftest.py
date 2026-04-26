"""UWG test fixtures."""

from __future__ import annotations

from typing import Generator, List, Tuple

import pytest

from agentic_core.L4_state.audit.audit_ledger import reset_default_ledger
from agentic_core.L4_state.contracts import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
)
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.otel.spans import reset_emitted_spans
from agentic_core.L4_state.uwg.durable_write_gateway import (
    DurableWriteGateway,
    reset_default_gateway,
)


@pytest.fixture(autouse=True)
def _reset_subsystems() -> Generator[None, None, None]:
    reset_emitted_spans()
    reset_default_ledger()
    reset_default_gateway()
    yield
    reset_emitted_spans()
    reset_default_ledger()
    reset_default_gateway()


@pytest.fixture
def gateway() -> DurableWriteGateway:
    """Return a fresh gateway per test."""
    return DurableWriteGateway()


@pytest.fixture
def well_formed_packet() -> Tuple[CommitRequest, List[StateDiff], RollbackPlan, ReadSurfaceRefreshPlan]:
    """Build a fully-valid CommitRequest + accompanying records.

    Tests that want the happy path use this. Tests that probe failure modes
    mutate fields with ``dataclasses.replace``.
    """
    rollback = stamp_digest(
        RollbackPlan(
            rollback_plan_id="rp:1",
            blast_radius="single_surface",
            target_surfaces=("memory",),
            before_snapshot_refs=("snap:before",),
            rollback_operation_types=("tombstone",),
        )
    )
    refresh = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id="rfp:1",
            source_commit_receipt_ref="<pending>",
            before_snapshot="snap:before",
            expected_after_snapshot="snap:after",
            stale_projection_policy="fail_closed",
            retry_policy="none",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            affected_surfaces=("memory",),
            required_refreshes=("memory_projection",),
            refresh_order=("memory_projection",),
        )
    )
    sd = stamp_digest(
        StateDiff(
            state_diff_id="sd:1",
            target_surface="memory",
            operation_type="memory_promotion",
            after_candidate="memrec:1",
            schema_ref="schema:memory@1",
            blast_radius="single_surface",
            rollback_plan_ref=rollback.rollback_plan_id,
            proposed_by_surface="L6",  # the proposer is L6 — but the COMMIT is from Exit
            created_at="0",
        )
    )
    cr = stamp_digest(
        CommitRequest(
            commit_request_id="cr:1",
            cleared_exit_review_packet_ref="exr:1",
            request_id="req:1",
            run_id="run:1",
            trace_root="trace:1",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            route_contract_ref="rc:1",
            replay_key="rk:1",
            rollback_plan_ref=rollback.rollback_plan_id,
            blast_radius="single_surface",
            state_diff_refs=(sd.state_diff_id,),
            gate_verdict_refs=("gv:1",),
            affected_state_surfaces=("memory",),
            expected_read_surface_refreshes=("memory_projection",),
        )
    )
    return cr, [sd], rollback, refresh
