#!/usr/bin/env python3
"""Migrate legacy R1B bundles additively through transactional UWG.

The source bundle is never modified. Each legacy payload is committed to a
migration-quarantine L4 surface, then frozen. A later reviewed X3C promotion is
required before it can become cache-admissible read truth.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    stamp_digest,
)
from agentic_core.L4_state.storage.sqlite_backend import SQLiteL4Backend
from agentic_core.L4_state.uwg.durable_write_gateway import compute_state_diffs_digest
from agentic_core.L4_state.uwg.transactional_durable_write_gateway import (
    TransactionalDurableWriteGateway,
)

MIGRATION_SURFACE = "l4.apps_rg.r1b_semantic_cache.migration_quarantine"


def _packet(
    path: Path,
) -> tuple[
    CommitRequest,
    list[StateDiff],
    RollbackPlan,
    ReadSurfaceRefreshPlan,
    dict[str, Any],
]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"legacy bundle is not an object: {path}")
    source_digest = compute_deterministic_digest(payload)
    record_id = str(
        ((payload.get("parent_intent_record") or {}).get("record_id"))
        or payload.get("record_id")
        or path.stem
    )
    rollback = stamp_digest(
        RollbackPlan(
            rollback_plan_id=f"rp:r1b-migration:{source_digest}",
            blast_radius="single_surface",
            target_surfaces=(MIGRATION_SURFACE,),
            before_snapshot_refs=("snapshot:r1b-migration:before",),
            rollback_operation_types=("tombstone",),
        )
    )
    diff = stamp_digest(
        StateDiff(
            state_diff_id=f"sd:r1b-migration:{source_digest}",
            target_surface=MIGRATION_SURFACE,
            operation_type="version_insert",
            after_candidate=f"legacy-r1b:{record_id}:sha256:{source_digest}",
            schema_ref="schema:apps_rg.r1b_migration_quarantine@1",
            blast_radius="single_surface",
            rollback_plan_ref=rollback.rollback_plan_id,
            proposed_by_surface="Exit",
            created_at="migration",
            replay_refs=(source_digest,),
            audit_refs=(str(path),),
        )
    )
    diff_hash = compute_state_diffs_digest([diff])
    clearance = f"migration-clearance:{source_digest}"
    request_id = f"cr:r1b-migration:{source_digest}"
    signature = compute_deterministic_digest(
        {
            "commit_request_id": request_id,
            "staged_diff_hash": diff_hash,
            "clearance_proof_id": clearance,
        }
    )
    request = stamp_digest(
        CommitRequest(
            commit_request_id=request_id,
            cleared_exit_review_packet_ref=clearance,
            request_id=f"migration:{record_id}",
            run_id=f"migration:{source_digest}",
            trace_root=f"trace:migration:{source_digest}",
            tenant_id="apps_rg",
            policy_hash="policy:r1b-migration-quarantine-v1",
            blueprint_hash="blueprint:l4-transactional-migration-v1",
            route_contract_ref="route:apps_rg:r1b_migration_quarantine",
            replay_key=f"r1b-migration:{source_digest}",
            rollback_plan_ref=rollback.rollback_plan_id,
            blast_radius="single_surface",
            state_diff_refs=(diff.state_diff_id,),
            gate_verdict_refs=("gate:r1b-migration:quarantine-only",),
            l5_certification_ref=f"l5:r1b-migration:{source_digest}",
            affected_state_surfaces=(MIGRATION_SURFACE,),
            expected_read_surface_refreshes=(
                "r1b_migration_quarantine_projection",
            ),
            audit_refs=(str(path),),
            registry_digest_set=(
                "registry:r1b-migration-policy-v1",
                "registry:r1b-migration-schema-v1",
            ),
            capability_token_ref="capability:admin:r1b-migration-quarantine",
            clearance_proof_id=clearance,
            validator_receipt_id=f"validator:r1b-migration:{source_digest}",
            staged_diff_hash=diff_hash,
            commit_request_signature=signature,
        )
    )
    refresh = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id=f"rfp:r1b-migration:{source_digest}",
            source_commit_receipt_ref="<pending>",
            before_snapshot="snapshot:r1b-migration:before",
            expected_after_snapshot="snapshot:r1b-migration:after",
            stale_projection_policy="fail_closed",
            retry_policy="manual_review",
            policy_hash=request.policy_hash,
            blueprint_hash=request.blueprint_hash,
            affected_surfaces=(MIGRATION_SURFACE,),
            required_refreshes=("r1b_migration_quarantine_projection",),
            refresh_order=("r1b_migration_quarantine_projection",),
        )
    )
    canonical_payload = {
        "migration_status": "MIGRATED_QUARANTINED",
        "cache_admissible": False,
        "source_path": str(path),
        "source_digest": source_digest,
        "legacy_payload": payload,
    }
    return request, [diff], rollback, refresh, canonical_payload


def migrate_bundle(
    path: Path, *, gateway: TransactionalDurableWriteGateway
) -> dict[str, Any]:
    request, diffs, rollback, refresh, payload = _packet(path)
    gateway.stage_state_payload(
        commit_request_id=request.commit_request_id,
        state_diff_id=diffs[0].state_diff_id,
        payload=payload,
    )
    gateway.stage_projection_context(
        commit_request_id=request.commit_request_id,
        context={"source_path": str(path), "quarantine_only": True},
    )
    receipt, blocked, _pending = gateway.commit(
        commit_request=request,
        state_diffs=diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )
    if receipt is None:
        return {
            "path": str(path),
            "status": "BLOCKED",
            "reason_codes": list(
                getattr(blocked, "blocked_reason_codes", ()) or ()
            ),
        }
    backend = gateway.canonical_backend
    assert backend is not None
    versions = backend.get_state_versions(receipt.commit_receipt_id)
    lifecycle_event_ids = [
        gateway.transition_state_lifecycle(
            state_version_id=row["state_version_id"],
            source_commit_receipt_id=receipt.commit_receipt_id,
            target_stage="frozen",
            reason="legacy migration quarantine pending review",
        )
        for row in versions
    ]
    return {
        "path": str(path),
        "status": "MIGRATED_QUARANTINED",
        "source_commit_receipt_ref": receipt.commit_receipt_id,
        "content_hash": receipt.content_hash,
        "state_version_ids": [row["state_version_id"] for row in versions],
        "lifecycle_event_ids": lifecycle_event_ids,
        "source_file_modified": False,
        "cache_admissible": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default="artifacts/apps_rg/r1b_semantic_cache",
        help="Legacy R1B projection root",
    )
    parser.add_argument("--sqlite-path", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    backend = SQLiteL4Backend(args.sqlite_path or None)
    gateway = TransactionalDurableWriteGateway(canonical_backend=backend)
    intents = Path(args.root) / "durable" / "uwg_admitted" / "intents"
    paths = sorted(intents.glob("*.json")) if intents.is_dir() else []
    rows: list[dict[str, Any]] = []
    for path in paths:
        if args.dry_run:
            rows.append(
                {
                    "path": str(path),
                    "dry_run": True,
                    "source_file_would_be_modified": False,
                }
            )
        else:
            rows.append(migrate_bundle(path, gateway=gateway))
    print(
        json.dumps(
            {
                "bundles_seen": len(rows),
                "migration_surface": MIGRATION_SURFACE,
                "rows": rows,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if all(row.get("status") != "BLOCKED" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
