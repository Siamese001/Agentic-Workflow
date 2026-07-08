"""Direct tests for IndexRefreshReceipt / GraphProjectionRefreshReceipt / AliasRefreshReceipt.

Closes the previously-implicit rows in the requirements traceability matrix
(7.3, 7.4, 7.5) by exercising each receipt type's issuance API directly.

Doctrine: ``docs/reference/00_L4_State_and_UWG/00.7_*`` PHASE 1 + PHASE 4.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.contracts import UWGCommitReceipt
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.otel.spans import get_emitted_spans
from agentic_core.L4_state.refresh.refresh_coordinator import (
    RefreshCoordinator,
    RefreshExecutionError,
)


def _commit_receipt(commit_id: str = "cr:proof") -> UWGCommitReceipt:
    return stamp_digest(
        UWGCommitReceipt(
            commit_receipt_id=commit_id,
            commit_request_ref="creq:proof",
            write_lock_receipt_ref="wlr:proof",
            uwg_validation_receipt_ref="uvr:proof",
            snapshot_before="snap:before",
            snapshot_after="snap:after",
            read_surface_refresh_plan_ref="rfp:proof",
            audit_append_receipt_ref="aar:proof",
            committed_at="0",
            l5_certification_ref="l5:proof",
        )
    )


class TestIndexRefreshReceipt:
    def test_vector_index_refresh_emits_receipt_and_span(self) -> None:
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        r = coord.issue_index_refresh(
            index_type="vector",
            commit_receipt=commit,
            source_snapshot_before="src:before",
            source_snapshot_after="src:after",
            index_manifest_before="vidx:before",
            index_manifest_after="vidx:after",
        )
        assert r.index_type == "vector"
        assert r.source_commit_receipt_ref == commit.commit_receipt_id
        assert r.deterministic_digest
        spans = [s for s in get_emitted_spans() if s.name == "l4.index.vector.refresh"]
        assert spans

    def test_sparse_and_metadata_variants_supported(self) -> None:
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        for index_type in ("sparse", "metadata"):
            r = coord.issue_index_refresh(
                index_type=index_type,
                commit_receipt=commit,
                source_snapshot_before="src:before",
                source_snapshot_after="src:after",
            )
            assert r.index_type == index_type

    def test_unknown_index_type_rejected(self) -> None:
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        with pytest.raises(RefreshExecutionError, match="unknown index_type"):
            coord.issue_index_refresh(
                index_type="quantum",  # not vector/sparse/metadata
                commit_receipt=commit,
                source_snapshot_before="src:before",
                source_snapshot_after="src:after",
            )


class TestGraphProjectionRefreshReceipt:
    def test_emits_receipt_with_source_snapshot_refs(self) -> None:
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        r = coord.issue_graph_projection_refresh(
            commit_receipt=commit,
            graph_projection_before="gp:before",
            projection_version_before="pv:1",
            relation_type_manifest_ref="rtm:1",
            source_snapshot_refs=("src:1", "src:2"),
            graph_projection_after="gp:after",
            projection_version_after="pv:2",
        )
        assert r.source_commit_receipt_ref == commit.commit_receipt_id
        assert r.source_snapshot_refs == ("src:1", "src:2")
        assert r.deterministic_digest
        spans = [s for s in get_emitted_spans() if s.name == "l4.graph_projection.refresh"]
        assert spans

    def test_empty_source_snapshot_refs_fails_closed(self) -> None:
        """00.7 PHASE 4: graph projection refresh lacking source_snapshot_refs fails closed."""
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        with pytest.raises(RefreshExecutionError, match="source_snapshot_refs"):
            coord.issue_graph_projection_refresh(
                commit_receipt=commit,
                graph_projection_before="gp:before",
                projection_version_before="pv:1",
                relation_type_manifest_ref="rtm:1",
                source_snapshot_refs=(),  # empty — fail closed
            )


class TestAliasRefreshReceipt:
    def test_policy_alias_refresh(self) -> None:
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        r = coord.issue_alias_refresh(
            alias_type="policy",
            commit_receipt=commit,
            alias_before="alias:old",
            alias_after="alias:new",
            target_record_ref="pm:1",
        )
        assert r.alias_type == "policy"
        assert r.target_record_ref == "pm:1"
        assert r.deterministic_digest
        spans = [s for s in get_emitted_spans() if s.name == "l4.alias.refresh"]
        assert spans

    def test_registry_alias_refresh(self) -> None:
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        r = coord.issue_alias_refresh(
            alias_type="registry",
            commit_receipt=commit,
            alias_before="alias:old",
            alias_after="alias:new",
            target_record_ref="rs:1",
        )
        assert r.alias_type == "registry"

    def test_route_alias_refresh(self) -> None:
        coord = RefreshCoordinator()
        commit = _commit_receipt()
        r = coord.issue_alias_refresh(
            alias_type="route",
            commit_receipt=commit,
            alias_before="alias:old",
            alias_after="alias:new",
            target_record_ref="rc:1",
        )
        assert r.alias_type == "route"


class TestRefreshExecutionGate:
    def test_execute_rejects_when_plan_does_not_match_commit(self) -> None:
        from agentic_core.L4_state.contracts import ReadSurfaceRefreshPlan

        coord = RefreshCoordinator()
        commit = _commit_receipt(commit_id="cr:abc")
        plan = stamp_digest(
            ReadSurfaceRefreshPlan(
                refresh_plan_id="rfp:1",
                source_commit_receipt_ref="cr:DIFFERENT",  # mismatch
                before_snapshot="snap:before",
                expected_after_snapshot="snap:after",
                stale_projection_policy="fail_closed",
                retry_policy="none",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                required_refreshes=("memory_projection",),
            )
        )
        with pytest.raises(RefreshExecutionError, match="does not match"):
            coord.execute(plan=plan, commit_receipt=commit)
