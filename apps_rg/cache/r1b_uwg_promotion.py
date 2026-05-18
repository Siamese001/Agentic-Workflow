"""W10 — UWG-gated durable admission for R1B semantic cache (apps_rg only)."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_constants import (
    CACHE_GRAIN_ROLE_TARGET_RUN,
    R1B_SCHEMA_REF,
    R1B_STORAGE_SUBSYSTEM,
    R1B_UWG_TARGET_SURFACE,
)
from apps_rg.cache.r1b_durable_write_guard import assert_r1b_durable_write_authority
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uwg_promotion_enabled() -> bool:
    if os.environ.get("APPS_RG_R1B_SKIP_UWG", "").strip().lower() in ("1", "true", "yes"):
        return False
    return True


@dataclass
class R1BCachePromotionCandidate:
    """Post-Exit cache promotion proposal — inert until UWG admits."""

    record: HistoricalIntentRecord
    chunks: list[HistoricalOutputChunk]
    post_exit_eligibility: dict[str, Any]
    source_run_id: str
    request_id: str
    trace_root: str
    tenant_id: str
    policy_hash: str
    blueprint_hash: str
    cleared_exit_review_packet_ref: str
    x3_disposition_ref: str
    proof_eligibility_ref: str
    replay_refs: tuple[str, ...] = field(default_factory=tuple)
    audit_refs: tuple[str, ...] = field(default_factory=tuple)

    @property
    def cache_admissible(self) -> bool:
        return bool(self.record.cache_admissible)


@dataclass
class R1BPromotionOutcome:
    status: str  # ADMITTED | BLOCKED | SKIPPED
    record_id: str
    durable_write_path: str
    commit_request_id: str = ""
    uwg_commit_receipt_id: str = ""
    blocked_commit_receipt_id: str = ""
    blocked_reason_codes: tuple[str, ...] = field(default_factory=tuple)
    missing_contract_fields: tuple[str, ...] = field(default_factory=tuple)
    fixture_mirror_written: bool = False
    c0_fact_vectors_consulted: bool = False
    governance_receipt: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "record_id": self.record_id,
            "durable_write_path": self.durable_write_path,
            "commit_request_id": self.commit_request_id,
            "uwg_commit_receipt_id": self.uwg_commit_receipt_id,
            "blocked_commit_receipt_id": self.blocked_commit_receipt_id,
            "blocked_reason_codes": list(self.blocked_reason_codes),
            "missing_contract_fields": list(self.missing_contract_fields),
            "fixture_mirror_written": self.fixture_mirror_written,
            "c0_fact_vectors_consulted": self.c0_fact_vectors_consulted,
            "governance_receipt": self.governance_receipt,
            "cache_grain": CACHE_GRAIN_ROLE_TARGET_RUN,
            "target_surface": R1B_UWG_TARGET_SURFACE,
        }


def build_r1b_promotion_candidate(
    *,
    record: HistoricalIntentRecord,
    chunks: list[HistoricalOutputChunk],
    post_exit_eligibility: dict[str, Any],
    run_dir: Path | str | None = None,
    tenant_id: str = "apps_rg",
) -> R1BCachePromotionCandidate:
    exit_meta = post_exit_eligibility.get("exit_metadata") or {}
    source_run_id = str(
        exit_meta.get("source_run_id")
        or record.source_run_id
        or record.record_id
    )
    run_path = Path(run_dir) if run_dir else None
    x3_ref = str((run_path / "x3_disposition.json") if run_path else "x3_disposition.json")
    proof_ref = str((run_path / "run_manifest.json") if run_path else "run_manifest.json")
    cleared_exit = f"exit_packet:{source_run_id}"
    if run_path and (run_path / "x3_disposition.json").is_file():
        cleared_exit = f"exit_packet_digest:{_digest_file(run_path / 'x3_disposition.json')}"
    return R1BCachePromotionCandidate(
        record=record,
        chunks=chunks,
        post_exit_eligibility=post_exit_eligibility,
        source_run_id=source_run_id,
        request_id=str(record.record_id),
        trace_root=f"trace:{source_run_id}",
        tenant_id=tenant_id,
        policy_hash=str(record.prompt_profile_hash or "unknown"),
        blueprint_hash=str(record.gate_profile_hash or "unknown"),
        cleared_exit_review_packet_ref=cleared_exit,
        x3_disposition_ref=x3_ref,
        proof_eligibility_ref=proof_ref,
        replay_refs=(str(record.record_id), source_run_id),
        audit_refs=(x3_ref, proof_ref),
    )


def _digest_file(path: Path) -> str:
    from agentic_core.L4_state.contracts.digests import compute_deterministic_digest

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        payload = {"path": str(path)}
    return compute_deterministic_digest(payload)


def build_r1b_commit_bundle(
    candidate: R1BCachePromotionCandidate,
) -> tuple[Any, list[Any], Any, Any]:
    """Build CommitRequest + StateDiffs for UWG admission."""
    from agentic_core.L4_state.contracts.records import (
        CommitRequest,
        ReadSurfaceRefreshPlan,
        RollbackPlan,
        StateDiff,
        stamp_digest,
    )

    assert_r1b_durable_write_authority(attempting_surface="Exit")

    rollback = stamp_digest(
        RollbackPlan(
            rollback_plan_id=f"r1b_rp:{candidate.record.record_id}",
            blast_radius="single_surface",
            target_surfaces=(R1B_UWG_TARGET_SURFACE,),
            before_snapshot_refs=("snap:r1b:before",),
            rollback_operation_types=("tombstone",),
        )
    )
    refresh = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id=f"r1b_rfp:{candidate.record.record_id}",
            source_commit_receipt_ref="<pending>",
            before_snapshot="snap:r1b:before",
            expected_after_snapshot="snap:r1b:after",
            stale_projection_policy="fail_closed",
            retry_policy="none",
            policy_hash=candidate.policy_hash,
            blueprint_hash=candidate.blueprint_hash,
            affected_surfaces=(R1B_UWG_TARGET_SURFACE,),
            required_refreshes=("r1b_semantic_cache_projection",),
            refresh_order=("r1b_semantic_cache_projection",),
        )
    )
    payload_ref = f"r1b:intent:{candidate.record.record_id}"
    sd = stamp_digest(
        StateDiff(
            state_diff_id=f"r1b_sd:{candidate.record.record_id}",
            target_surface=R1B_UWG_TARGET_SURFACE,
            operation_type="memory_promotion",
            after_candidate=payload_ref,
            schema_ref=R1B_SCHEMA_REF,
            blast_radius="single_surface",
            rollback_plan_ref=rollback.rollback_plan_id,
            proposed_by_surface="Exit",
            created_at=_utc_now(),
            replay_refs=candidate.replay_refs,
            audit_refs=candidate.audit_refs,
        )
    )
    cr = stamp_digest(
        CommitRequest(
            commit_request_id=f"r1b_cr:{candidate.record.record_id}",
            cleared_exit_review_packet_ref=candidate.cleared_exit_review_packet_ref,
            request_id=candidate.request_id,
            run_id=candidate.source_run_id,
            trace_root=candidate.trace_root,
            tenant_id=candidate.tenant_id,
            policy_hash=candidate.policy_hash,
            blueprint_hash=candidate.blueprint_hash,
            route_contract_ref=f"route:apps_rg:r1b:{CACHE_GRAIN_ROLE_TARGET_RUN}",
            replay_key=f"r1b:{candidate.record.normalized_intent_digest}",
            rollback_plan_ref=rollback.rollback_plan_id,
            blast_radius="single_surface",
            state_diff_refs=(sd.state_diff_id,),
            gate_verdict_refs=(f"gv:r1b:post_exit:{candidate.source_run_id}",),
            l5_certification_ref=f"l5:r1b:post_exit:{candidate.source_run_id}",
            affected_state_surfaces=(R1B_UWG_TARGET_SURFACE,),
            expected_read_surface_refreshes=("r1b_semantic_cache_projection",),
            audit_refs=candidate.audit_refs,
        )
    )
    return cr, [sd], rollback, refresh


def promote_r1b_cache_via_uwg(
    candidate: R1BCachePromotionCandidate,
    *,
    gateway: Any | None = None,
) -> R1BPromotionOutcome:
    """Submit R1B promotion through DurableWriteGateway (Exit-sourced CommitRequest)."""
    if not candidate.cache_admissible:
        return R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            blocked_reason_codes=("cache_not_admissible",),
        )

    if not _uwg_promotion_enabled():
        return R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            blocked_reason_codes=("APPS_RG_R1B_SKIP_UWG",),
            missing_contract_fields=("uwg_promotion_disabled_by_env",),
        )

    from apps_rg.cache.r1b_uwg_gateway_shim import default_r1b_promotion_gateway

    from apps_rg.cache.r1b_uwg_receipt_contract import (
        build_governance_receipt_bundle,
        validate_commit_request_governance,
    )

    gw = gateway or default_r1b_promotion_gateway()
    cr, state_diffs, rollback, refresh = build_r1b_commit_bundle(candidate)
    gov_check = validate_commit_request_governance(cr)
    if not gov_check.valid:
        bundle = build_governance_receipt_bundle(
            commit_request=cr,
            state_diffs=state_diffs,
        )
        return R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            commit_request_id=cr.commit_request_id,
            blocked_reason_codes=gov_check.reason_codes,
            missing_contract_fields=gov_check.missing_fields,
            governance_receipt=bundle.to_dict(),
        )
    try:
        commit_receipt, blocked_receipt, _refresh = gw.commit(
            commit_request=cr,
            state_diffs=state_diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
    except ValueError as exc:
        msg = str(exc)
        missing = ("UWGCommitReceipt.l5_certification_ref",) if "l5_certification_ref" in msg else (msg,)
        return R1BPromotionOutcome(
            status="BLOCKED",
            record_id=candidate.record.record_id,
            durable_write_path="none",
            commit_request_id=cr.commit_request_id,
            blocked_reason_codes=(msg,),
            missing_contract_fields=missing,
        )
    if commit_receipt is not None:
        gov_bundle = build_governance_receipt_bundle(
            commit_request=cr,
            state_diffs=state_diffs,
            commit_receipt=commit_receipt,
        )
        return R1BPromotionOutcome(
            status="ADMITTED",
            record_id=candidate.record.record_id,
            durable_write_path="UWG→L4",
            commit_request_id=cr.commit_request_id,
            uwg_commit_receipt_id=commit_receipt.commit_receipt_id,
            governance_receipt=gov_bundle.to_dict(),
        )
    blocked_codes: tuple[str, ...] = ()
    blocked_id = ""
    missing: list[str] = []
    if blocked_receipt is not None:
        blocked_codes = tuple(blocked_receipt.blocked_reason_codes)
        blocked_id = blocked_receipt.blocked_commit_receipt_id
        if "missing::gate_verdict_refs" in blocked_codes:
            missing.append("gate_verdict_refs")
        if any("missing::" in c for c in blocked_codes):
            missing.extend(c for c in blocked_codes if c.startswith("missing::"))
    gov_bundle = build_governance_receipt_bundle(
        commit_request=cr,
        state_diffs=state_diffs,
        blocked_receipt=blocked_receipt,
    )
    return R1BPromotionOutcome(
        status="BLOCKED",
        record_id=candidate.record.record_id,
        durable_write_path="none",
        commit_request_id=cr.commit_request_id,
        blocked_commit_receipt_id=blocked_id,
        blocked_reason_codes=blocked_codes,
        missing_contract_fields=tuple(missing),
        governance_receipt=gov_bundle.to_dict(),
    )


def write_uwg_admitted_projection(
    *,
    projection_root: Path,
    candidate: R1BCachePromotionCandidate,
    outcome: R1BPromotionOutcome,
) -> Path:
    """Persist UWG-admitted R1B bundle under durable projection (not fixture SSOT)."""
    assert outcome.status == "ADMITTED"
    assert outcome.uwg_commit_receipt_id

    root = projection_root / "durable" / "uwg_admitted"
    intents = root / "intents"
    chunks = root / "chunks"
    receipts = root / "receipts"
    for d in (intents, chunks, receipts):
        d.mkdir(parents=True, exist_ok=True)

    bundle = {
        "schema_version": candidate.record.schema_version,
        "storage_subsystem": R1B_STORAGE_SUBSYSTEM,
        "storage_tier": "uwg_admitted_durable_projection",
        "durable_write_path": outcome.durable_write_path,
        "uwg_commit_receipt_id": outcome.uwg_commit_receipt_id,
        "commit_request_id": outcome.commit_request_id,
        "governance_receipt": outcome.governance_receipt,
        "parent_intent_record": candidate.record.to_dict(),
        "child_chunks": [c.to_dict() for c in candidate.chunks],
        "post_exit_eligibility_receipt": candidate.post_exit_eligibility,
        "source_run_id": candidate.source_run_id,
        "x3_disposition_ref": candidate.x3_disposition_ref,
        "proof_eligibility_ref": candidate.proof_eligibility_ref,
        "c0_fact_vectors_consulted": False,
        "admitted_at_utc": _utc_now(),
    }
    intent_path = intents / f"{candidate.record.record_id}.json"
    intent_path.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path = receipts / f"{candidate.record.record_id}_uwg_commit.json"
    receipt_path.write_text(json.dumps(outcome.to_dict(), indent=2) + "\n", encoding="utf-8")
    parent_chunks = chunks / candidate.record.record_id
    parent_chunks.mkdir(parents=True, exist_ok=True)
    for ch in candidate.chunks:
        (parent_chunks / f"{ch.chunk_id}.json").write_text(
            json.dumps(ch.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return intent_path


def write_blocked_promotion_receipt(
    *,
    projection_root: Path,
    candidate: R1BCachePromotionCandidate,
    outcome: R1BPromotionOutcome,
) -> Path:
    """Persist blocked UWG admission receipt (no durable cache truth)."""
    blocked_dir = projection_root / "durable" / "blocked_writes"
    blocked_dir.mkdir(parents=True, exist_ok=True)
    path = blocked_dir / f"{candidate.record.record_id}_blocked.json"
    payload = {
        "storage_tier": "blocked_uwg_admission",
        "not_durable_production_truth": True,
        "candidate_record_id": candidate.record.record_id,
        "promotion_outcome": outcome.to_dict(),
        "governance_receipt": outcome.governance_receipt,
        "post_exit_eligibility": candidate.post_exit_eligibility,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def promote_and_project_r1b_cache(
    *,
    candidate: R1BCachePromotionCandidate,
    projection_root: Path,
    fixture_store: Any | None = None,
    gateway: Any | None = None,
    mirror_fixture_on_blocked: bool = True,
) -> R1BPromotionOutcome:
    """UWG admission then durable projection; optional fixture mirror for tests."""
    outcome = promote_r1b_cache_via_uwg(candidate, gateway=gateway)
    if outcome.status == "ADMITTED":
        write_uwg_admitted_projection(
            projection_root=projection_root,
            candidate=candidate,
            outcome=outcome,
        )
        from apps_rg.cache.r1b_derived_index import project_durable_to_derived_index

        project_durable_to_derived_index(projection_root)
        if fixture_store is not None:
            _write_fixture_mirror(fixture_store, candidate)
            outcome.fixture_mirror_written = True
        return outcome

    write_blocked_promotion_receipt(
        projection_root=projection_root,
        candidate=candidate,
        outcome=outcome,
    )
    if mirror_fixture_on_blocked and fixture_store is not None and candidate.cache_admissible:
        _write_fixture_mirror(fixture_store, candidate)
        outcome.fixture_mirror_written = True
    return outcome


def _write_fixture_mirror(store: Any, candidate: R1BCachePromotionCandidate) -> None:
    """File-backed mirror for tests — explicitly non-durable production truth."""
    store.write_intent(candidate.record)
    for ch in candidate.chunks:
        store.write_chunk(ch)


__all__ = [
    "R1BCachePromotionCandidate",
    "R1BPromotionOutcome",
    "build_r1b_commit_bundle",
    "build_r1b_promotion_candidate",
    "promote_and_project_r1b_cache",
    "promote_r1b_cache_via_uwg",
    "write_blocked_promotion_receipt",
    "write_uwg_admitted_projection",
]
