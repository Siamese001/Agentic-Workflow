"""Unit tests for agentic_core.L4_state.refresh.refresh_coordinator.

W6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — P2 L4 read-surface refresh.
``RefreshCoordinator`` (00.7 §PHASE 3/4) issues post-commit read-surface
refreshes ONLY after a UWGCommitReceipt; refresh without a matching commit
receipt fails closed. Covers REFRESH_ORDER, plan/commit binding guards,
the deterministic _infer_state_surface mapping, per-refresh receipt
issuance + caching, and the index/graph/alias issuance error paths.

All dependencies (AuditLedger, OTel spans) are in-memory/degraded — no IO.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.audit.audit_ledger import AuditLedger
from agentic_core.L4_state.contracts.records import (
    ReadSurfaceRefreshPlan,
    UWGCommitReceipt,
)
from agentic_core.L4_state.refresh.refresh_coordinator import (
    REFRESH_ORDER,
    RefreshCoordinator,
    RefreshExecutionError,
)


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _commit_receipt(*, commit_id: str = "commit-1") -> UWGCommitReceipt:
    return UWGCommitReceipt(
        commit_receipt_id=commit_id,
        commit_request_ref="req-1",
        write_lock_receipt_ref="lock-1",
        uwg_validation_receipt_ref="val-1",
        snapshot_before="snap-before",
        snapshot_after="snap-after",
        read_surface_refresh_plan_ref="plan-1",
        audit_append_receipt_ref="audit-1",
        committed_at="2026-06-14T00:00:00Z",
        l5_certification_ref="cert-1",  # non-empty -> structurally valid
    )


def _plan(
    *,
    commit_id: str = "commit-1",
    required: tuple[str, ...] = ("policy_alias", "vector_index"),
    plan_id: str = "plan-1",
) -> ReadSurfaceRefreshPlan:
    return ReadSurfaceRefreshPlan(
        refresh_plan_id=plan_id,
        source_commit_receipt_ref=commit_id,
        before_snapshot="snap-before",
        expected_after_snapshot="snap-after",
        stale_projection_policy="strict",
        retry_policy="none",
        policy_hash="ph",
        blueprint_hash="bh",
        required_refreshes=required,
    )


@pytest.fixture()
def coordinator() -> RefreshCoordinator:
    # Fresh in-memory ledger per test so audit appends are isolated.
    return RefreshCoordinator(audit_ledger=AuditLedger())


# ---------------------------------------------------------------------------
class TestRefreshOrder:
    def test_refresh_order_is_canonical_tuple(self) -> None:
        assert isinstance(REFRESH_ORDER, tuple)
        assert REFRESH_ORDER[0] == "policy_alias"
        assert REFRESH_ORDER[-1] == "route_baseline"

    def test_refresh_order_has_no_duplicates(self) -> None:
        assert len(REFRESH_ORDER) == len(set(REFRESH_ORDER))


# ---------------------------------------------------------------------------
class TestInferStateSurface:
    @pytest.mark.parametrize(
        "refresh_type,expected",
        [
            ("policy_alias", "policy"),
            ("schema_alias", "schema"),
            ("registry_alias", "registry"),
            ("cache_invalidation", "cache"),
            ("source_chunk_projection", "source_chunk"),
            ("metadata_index", "metadata_index"),
            ("sparse_index", "sparse_index"),
            ("vector_index", "vector_index"),
            ("graph_projection", "graph_projection"),
            ("memory_projection", "memory"),
            ("prompt_bom_cache", "prompt_bom"),
            ("route_baseline", "route_baseline"),
        ],
    )
    def test_known_mappings(self, refresh_type: str, expected: str) -> None:
        assert RefreshCoordinator._infer_state_surface(refresh_type) == expected

    def test_unknown_type_passes_through(self) -> None:
        assert RefreshCoordinator._infer_state_surface("novel_surface") == "novel_surface"


# ---------------------------------------------------------------------------
class TestExecute:
    def test_execute_issues_one_receipt_per_required_refresh(
        self, coordinator: RefreshCoordinator
    ) -> None:
        commit = _commit_receipt()
        plan = _plan(required=("policy_alias", "vector_index", "graph_projection"))
        receipts = coordinator.execute(plan=plan, commit_receipt=commit)
        assert len(receipts) == 3
        assert [r.refresh_type for r in receipts] == [
            "policy_alias",
            "vector_index",
            "graph_projection",
        ]

    def test_execute_receipt_fields_bound_to_plan_and_commit(
        self, coordinator: RefreshCoordinator
    ) -> None:
        commit = _commit_receipt()
        plan = _plan(required=("policy_alias",))
        (receipt,) = coordinator.execute(plan=plan, commit_receipt=commit)
        assert receipt.source_commit_receipt_ref == "commit-1"
        assert receipt.refresh_plan_ref == "plan-1"
        assert receipt.state_surface == "policy"
        assert receipt.status == "SUCCESS"
        assert receipt.after_snapshot == "snap-after"
        assert receipt.deterministic_digest  # stamped

    def test_execute_caches_receipts_for_lookup(
        self, coordinator: RefreshCoordinator
    ) -> None:
        commit = _commit_receipt()
        plan = _plan(required=("policy_alias", "vector_index"))
        receipts = coordinator.execute(plan=plan, commit_receipt=commit)
        for r in receipts:
            assert coordinator.get_receipt(r.refresh_receipt_id) is r
        assert len(coordinator.all_receipts()) == 2

    def test_execute_empty_required_yields_no_receipts(
        self, coordinator: RefreshCoordinator
    ) -> None:
        commit = _commit_receipt()
        plan = _plan(required=())
        assert coordinator.execute(plan=plan, commit_receipt=commit) == []

    def test_execute_missing_commit_id_fails_closed(
        self, coordinator: RefreshCoordinator
    ) -> None:
        commit = _commit_receipt(commit_id="")
        plan = _plan(commit_id="")
        with pytest.raises(RefreshExecutionError, match="missing source_commit_receipt"):
            coordinator.execute(plan=plan, commit_receipt=commit)

    def test_execute_plan_commit_mismatch_fails_closed(
        self, coordinator: RefreshCoordinator
    ) -> None:
        commit = _commit_receipt(commit_id="commit-A")
        plan = _plan(commit_id="commit-B")  # ref does not match the receipt
        with pytest.raises(RefreshExecutionError, match="does not match"):
            coordinator.execute(plan=plan, commit_receipt=commit)

    def test_get_receipt_unknown_returns_none(
        self, coordinator: RefreshCoordinator
    ) -> None:
        assert coordinator.get_receipt("nope") is None


# ---------------------------------------------------------------------------
class TestIssueIndexRefresh:
    @pytest.mark.parametrize("index_type", ["vector", "sparse", "metadata"])
    def test_valid_index_types(self, coordinator: RefreshCoordinator, index_type: str) -> None:
        receipt = coordinator.issue_index_refresh(
            index_type=index_type,
            commit_receipt=_commit_receipt(),
            source_snapshot_before="b",
            source_snapshot_after="a",
        )
        assert receipt.index_type == index_type
        assert receipt.source_commit_receipt_ref == "commit-1"
        assert receipt.deterministic_digest

    def test_unknown_index_type_raises(self, coordinator: RefreshCoordinator) -> None:
        with pytest.raises(RefreshExecutionError, match="unknown index_type"):
            coordinator.issue_index_refresh(
                index_type="bogus",
                commit_receipt=_commit_receipt(),
                source_snapshot_before="b",
                source_snapshot_after="a",
            )


# ---------------------------------------------------------------------------
class TestIssueGraphProjectionRefresh:
    def test_requires_non_empty_source_snapshot_refs(
        self, coordinator: RefreshCoordinator
    ) -> None:
        with pytest.raises(RefreshExecutionError, match="source_snapshot_refs"):
            coordinator.issue_graph_projection_refresh(
                commit_receipt=_commit_receipt(),
                graph_projection_before="gp-b",
                projection_version_before="v1",
                relation_type_manifest_ref="rtm",
                source_snapshot_refs=(),
            )

    def test_valid_graph_refresh(self, coordinator: RefreshCoordinator) -> None:
        receipt = coordinator.issue_graph_projection_refresh(
            commit_receipt=_commit_receipt(),
            graph_projection_before="gp-b",
            projection_version_before="v1",
            relation_type_manifest_ref="rtm",
            source_snapshot_refs=("s1",),
        )
        assert receipt.source_snapshot_refs == ("s1",)
        assert receipt.deterministic_digest


# ---------------------------------------------------------------------------
class TestIssueAliasRefresh:
    def test_alias_refresh_roundtrip(self, coordinator: RefreshCoordinator) -> None:
        receipt = coordinator.issue_alias_refresh(
            alias_type="policy",
            commit_receipt=_commit_receipt(),
            alias_before="a0",
            alias_after="a1",
            target_record_ref="rec-1",
        )
        assert receipt.alias_type == "policy"
        assert receipt.alias_before == "a0"
        assert receipt.alias_after == "a1"
        assert receipt.deterministic_digest
