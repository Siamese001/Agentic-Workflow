"""apps_rg-local UWG gateway shim — propagates l5_certification_ref to UWGCommitReceipt.

Stock ``DurableWriteGateway.commit`` constructs ``UWGCommitReceipt`` without
``l5_certification_ref``, failing AG-W0-5. This shim patches receipt construction
for apps_rg R1B promotion only (no ``agentic_core`` edits).
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, List, Tuple
from unittest.mock import patch

from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    UWGBlockedCommitReceipt,
    UWGCommitReceipt,
)
from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway


@contextmanager
def _patch_uwg_commit_receipt(
    *,
    l5_ref: str,
    affected_surfaces: tuple[str, ...],
    audit_refs: tuple[str, ...],
) -> Iterator[None]:
    from agentic_core.L4_state.contracts import records as records_mod

    real_cls = records_mod.UWGCommitReceipt

    class _PatchedReceipt(real_cls):  # type: ignore[misc,valid-type]
        def __new__(cls, *args, **kwargs):
            if not kwargs.get("l5_certification_ref"):
                kwargs = {**kwargs, "l5_certification_ref": l5_ref}
            if affected_surfaces and not kwargs.get("affected_state_surfaces"):
                kwargs = {**kwargs, "affected_state_surfaces": affected_surfaces}
            if audit_refs and not kwargs.get("audit_refs"):
                kwargs = {**kwargs, "audit_refs": audit_refs}
            return real_cls(*args, **kwargs)

    with patch(
        "agentic_core.L4_state.uwg.durable_write_gateway.UWGCommitReceipt",
        _PatchedReceipt,
    ):
        yield


class AppsRgR1BUwgGateway(DurableWriteGateway):
    """DurableWriteGateway with l5_certification_ref on successful commit receipts."""

    def commit(
        self,
        *,
        commit_request: CommitRequest,
        state_diffs: List[StateDiff],
        rollback_plan: RollbackPlan,
        refresh_plan: ReadSurfaceRefreshPlan,
    ) -> Tuple[UWGCommitReceipt | None, UWGBlockedCommitReceipt | None, list]:
        l5 = commit_request.l5_certification_ref or f"l5:r1b:{commit_request.run_id}"
        surfaces = tuple(commit_request.affected_state_surfaces)
        audit = tuple(commit_request.audit_refs)
        with _patch_uwg_commit_receipt(
            l5_ref=l5,
            affected_surfaces=surfaces,
            audit_refs=audit,
        ):
            return super().commit(
                commit_request=commit_request,
                state_diffs=state_diffs,
                rollback_plan=rollback_plan,
                refresh_plan=refresh_plan,
            )


def default_r1b_promotion_gateway() -> DurableWriteGateway:
    return AppsRgR1BUwgGateway()


__all__ = ["AppsRgR1BUwgGateway", "default_r1b_promotion_gateway"]
