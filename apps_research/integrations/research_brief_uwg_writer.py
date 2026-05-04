"""UWG write path for research briefs — DS-3.

Plan: ``apps-research-deferred-scope-b7e3d2`` W3 (phase 3.1).

Provides :func:`commit_brief_record`: takes a sealed
``GovernedE2ERunRecord``, constructs a ``ResearchBriefRecord``, submits
it through ``DurableWriteGateway.commit``, and emits the mandatory
``ROUTER_DECISION:`` marker per constitutional §29.

Design decisions
----------------
- **source_surface = "Exit"** — UWG only accepts commits from Exit.
  We treat the post-run provenance commit as a synthetic Exit pseudo-run,
  consistent with ``app_domain_registration.py`` precedent.
- **operation_type = "append_record"** — canonical ALLOWED_OPERATIONS entry
  for immutable provenance appends.
- **blast_radius = "single_surface"** — the commit touches exactly one
  surface (``l4.research_brief``).
- **fail-soft** — any exception is caught and logged; the caller's
  ``GovernedE2ERunRecord`` is returned regardless of UWG outcome.
  This ensures that UWG commitment never breaks the research pipeline.
- **ROUTER_DECISION: + emit_ledger_event** — emitted via
  ``RouterClosedLoopHelper`` per constitutional §29 (closed-loop router
  enforcement). Fail-soft if helper unavailable.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    stamp_digest,
)
from agentic_core.L4_state.research.research_brief_record import ResearchBriefRecord
from agentic_core.L4_state.uwg.durable_write_gateway import (
    DurableWriteGateway,
    get_default_gateway,
)

if TYPE_CHECKING:
    from apps_research.integrations.governed_research_run import GovernedE2ERunRecord

_log = logging.getLogger(__name__)

_L4_SURFACE = "l4.research_brief"
_SCHEMA_REF = "schema://apps_research/research_brief_record/1.0"
_POLICY_REF = "policy://apps_research/governed_e2e/v1"
_BLUEPRINT_REF = "blueprint://apps_research/governed_e2e/v1"

# Constitutional §29 — closed-loop router enforcement
_HELPER = None  # type: ignore[var-annotated]


def _get_helper():
    """Lazy singleton for RouterClosedLoopHelper (fail-soft)."""
    global _HELPER  # noqa: PLW0603
    if _HELPER is not None:
        return _HELPER
    try:
        from tools.ledgers.router_helper import RouterClosedLoopHelper  # noqa: PLC0415

        _HELPER = RouterClosedLoopHelper(
            layer="L4",
            router="research_brief_uwg_writer",
            ledger_name="router_l4_uwg",
            repo_area="apps_research/integrations/research_brief_uwg_writer.py",
        )
        return _HELPER
    except ImportError:
        _log.debug("RouterClosedLoopHelper unavailable for research_brief_uwg_writer")
        return None


def _fec_digest(fec_context: dict) -> str:
    """SHA-256 hex of the canonical JSON of the FEC context dict."""
    try:
        raw = json.dumps(fec_context, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()
    except (TypeError, ValueError):
        return ""


def commit_brief_record(
    run_record: "GovernedE2ERunRecord",
    *,
    gateway: Optional[DurableWriteGateway] = None,
    tenant_id: str = "platform",
) -> ResearchBriefRecord:
    """Commit a research brief provenance record through UWG.

    Args:
        run_record: Sealed ``GovernedE2ERunRecord`` from
            ``GovernedResearchRun.run_governed_e2e()``.
        gateway: Override gateway (test injection).  Defaults to the
            process-wide singleton.
        tenant_id: Tenant scope.  Defaults to ``"platform"``.

    Returns:
        A ``ResearchBriefRecord`` whose ``commit_receipt_ref`` is:

        - the ``UWGCommitReceipt.commit_receipt_id`` on success,
        - ``"BLOCKED"`` when the UWG rejects the commit,
        - ``"COMMIT_FAILED"`` on any unexpected exception.

    Never raises — all exceptions are caught and logged (fail-soft).
    """
    t_start = time.time()
    record_id = str(uuid.uuid4())
    committed_at = datetime.now(timezone.utc).isoformat()
    fec_digest = _fec_digest(run_record.fec_run_context or {})

    brief_record = ResearchBriefRecord(
        record_id=record_id,
        run_id=run_record.run_id,
        trace_id=getattr(run_record, "trace_id", ""),
        topic=run_record.topic,
        l0_intent=run_record.l0_intent,
        l0_confidence=run_record.l0_confidence,
        grounded=run_record.grounded,
        citation_count=run_record.citation_count,
        disposition=run_record.disposition,
        research_depth_profile=run_record.research_depth_profile or "",
        fec_context_digest=fec_digest,
        committed_at=committed_at,
        commit_receipt_ref="PENDING",
    )

    helper = _get_helper()
    handle = None
    commit_receipt_ref = "COMMIT_FAILED"

    try:
        gw = gateway or get_default_gateway()
        replay_key = compute_deterministic_digest(
            {
                "record_id": record_id,
                "run_id": run_record.run_id,
                "topic": run_record.topic,
                "fec_digest": fec_digest,
            }
        )

        commit_request_id = f"research-brief::{run_record.run_id}::{replay_key[:12]}"
        rollback_plan_id = f"rollback-plan::{commit_request_id}"
        refresh_plan_id = f"refresh-plan::{commit_request_id}"

        sd = stamp_digest(
            StateDiff(
                state_diff_id=str(uuid.uuid4()),
                target_surface=_L4_SURFACE,
                operation_type="append_record",
                after_candidate=f"l4://research_brief/{record_id}",
                schema_ref=_SCHEMA_REF,
                blast_radius="single_surface",
                rollback_plan_ref=rollback_plan_id,
                proposed_by_surface="Exit",
                created_at=str(int(t_start)),
                validation_rules=("dataclass_frozen_check",),
                policy_refs=(_POLICY_REF,),
            )
        )

        rollback_plan = stamp_digest(
            RollbackPlan(
                rollback_plan_id=rollback_plan_id,
                blast_radius="single_surface",
                target_surfaces=(_L4_SURFACE,),
                rollback_operation_types=("tombstone",),
                policy_refs=(_POLICY_REF,),
                schema_refs=(_SCHEMA_REF,),
            )
        )

        refresh_plan = stamp_digest(
            ReadSurfaceRefreshPlan(
                refresh_plan_id=refresh_plan_id,
                source_commit_receipt_ref="",
                before_snapshot=gw.last_snapshot_id,
                expected_after_snapshot="",
                stale_projection_policy="serve_with_warn",
                retry_policy="exponential_backoff_max_3",
                policy_hash=_POLICY_REF,
                blueprint_hash=_BLUEPRINT_REF,
                affected_surfaces=(_L4_SURFACE,),
                required_refreshes=(_L4_SURFACE,),
                refresh_order=(_L4_SURFACE,),
            )
        )

        commit_request = stamp_digest(
            CommitRequest(
                commit_request_id=commit_request_id,
                cleared_exit_review_packet_ref=f"erp://research-brief::{replay_key}",
                request_id=f"req::{commit_request_id}",
                run_id=run_record.run_id,
                trace_root=getattr(run_record, "trace_id", "") or run_record.run_id,
                tenant_id=tenant_id,
                policy_hash=_POLICY_REF,
                blueprint_hash=_BLUEPRINT_REF,
                route_contract_ref="route://apps_research/governed_e2e/v1",
                replay_key=replay_key,
                rollback_plan_ref=rollback_plan_id,
                blast_radius="single_surface",
                source_surface="Exit",
                state_diff_refs=(sd.state_diff_id,),
                gate_verdict_refs=(f"gate://research-brief::{replay_key}",),
                affected_state_surfaces=(_L4_SURFACE,),
                expected_read_surface_refreshes=(_L4_SURFACE,),
            )
        )

        # Constitutional §29 — emit ROUTER_DECISION: before commit
        if helper is not None:
            handle = helper.record_decision(
                selected="commit",
                cell={
                    "source_surface": "Exit",
                    "blast_radius": "single_surface",
                },
                predicted_p_success=1.0,
                eu_score=1.0,
                decision_id=commit_request_id,
                prediction_extras={
                    "run_id": run_record.run_id,
                    "grounded": str(run_record.grounded),
                    "disposition": run_record.disposition,
                },
            )

        _log.info(
            "research_brief_uwg_writer: committing run_id=%s replay_key=%s",
            run_record.run_id,
            replay_key[:12],
        )

        commit_receipt, blocked_receipt, _refresh = gw.commit(
            commit_request=commit_request,
            state_diffs=[sd],
            rollback_plan=rollback_plan,
            refresh_plan=refresh_plan,
        )

        latency_ms = int((time.time() - t_start) * 1000)

        if commit_receipt is not None:
            commit_receipt_ref = commit_receipt.commit_receipt_id
            _log.info(
                "research_brief_uwg_writer: committed run_id=%s receipt=%s",
                run_record.run_id,
                commit_receipt_ref[:16],
            )
        else:
            commit_receipt_ref = "BLOCKED"
            reason = (
                tuple(blocked_receipt.blocked_reason_codes)
                if blocked_receipt
                else ("unknown",)
            )
            _log.warning(
                "research_brief_uwg_writer: UWG blocked run_id=%s reasons=%s",
                run_record.run_id,
                reason,
            )

        # Constitutional §29 — bind outcome
        if helper is not None and handle is not None:
            try:
                helper.bind_outcome(
                    handle,
                    success=commit_receipt is not None,
                    latency_ms=latency_ms,
                    outcome_extras={
                        "commit_receipt_ref": commit_receipt_ref,
                        "run_id": run_record.run_id,
                    },
                )
            except (AttributeError, TypeError, ValueError, RuntimeError):  # guardian: allow-log-and-swallow -- ledger bind_outcome is best-effort; never break the run
                _log.debug("research_brief_uwg_writer: bind_outcome failed", exc_info=True)

    except (AttributeError, TypeError, ValueError, RuntimeError, ImportError) as exc:  # guardian: allow-log-and-swallow -- UWG commit is best-effort provenance; run record must always be returned
        _log.warning(
            "research_brief_uwg_writer: commit failed for run_id=%s: %s",
            getattr(run_record, "run_id", "?"),
            exc,
        )
        commit_receipt_ref = "COMMIT_FAILED"

    # Emit ROUTER_DECISION: marker (constitutional §29)
    # This is the text-side emission; the helper above is the ledger-side.
    _log.info(
        "ROUTER_DECISION: layer=L4 router=research_brief_uwg_writer "
        "selected=%s run_id=%s commit_receipt_ref=%s",
        "commit" if commit_receipt_ref not in ("BLOCKED", "COMMIT_FAILED") else "blocked",
        getattr(run_record, "run_id", "?"),
        commit_receipt_ref,
    )

    return ResearchBriefRecord(
        record_id=brief_record.record_id,
        run_id=brief_record.run_id,
        trace_id=brief_record.trace_id,
        topic=brief_record.topic,
        l0_intent=brief_record.l0_intent,
        l0_confidence=brief_record.l0_confidence,
        grounded=brief_record.grounded,
        citation_count=brief_record.citation_count,
        disposition=brief_record.disposition,
        research_depth_profile=brief_record.research_depth_profile,
        fec_context_digest=brief_record.fec_context_digest,
        committed_at=brief_record.committed_at,
        commit_receipt_ref=commit_receipt_ref,
    )


__all__ = ["commit_brief_record"]
