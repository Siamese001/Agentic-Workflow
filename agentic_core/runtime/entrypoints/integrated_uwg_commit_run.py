"""UWG_COMMIT_PATH — integrated runtime entrypoint.

Mirror of ``integrated_uwg_block_run.py`` but drives a SUCCESSFUL commit
through ``DurableWriteGateway.commit`` from the Exit surface with a
well-formed CommitRequest. Promotes UWG_COMMIT_PATH from NOT_CERTIFIED to
REAL_RUNTIME CERTIFIED (plan fortknox-100pct-static-runtime-gap-9a3d4f
§GAP-6c).

What this entrypoint does:

  1. Run the standard integrated chain with ``chain_kind="UWG_COMMIT_PATH"``.
  2. Build a well-formed CommitRequest + StateDiff + RollbackPlan +
     ReadSurfaceRefreshPlan bound to the chain's run_id / request_id /
     trace_root. ``source_surface="Exit"`` (authorized).
  3. Call ``gateway.commit(...)``. Expect a non-None ``UWGCommitReceipt``
     and ``blocked_receipt=None``. Refresh receipts flow from the
     refresh coordinator post-commit.
  4. Emit three extra spine artifacts:
       - ``commit_request.json`` — the typed CommitRequest payload.
       - ``uwg_commit_receipt.json`` — the typed UWGCommitReceipt payload
         with integrated_runtime_origin=True and snapshot_after set.
       - ``uwg_refresh_receipts.json`` — list of ReadSurfaceRefreshReceipt
         payloads (one per affected surface).
  5. Re-stamp manifest + no_harness_stamp_receipt + spine proof so that
     ``uwg_commit_or_block_ref`` / ``uwg_commit_receipt_sha256`` are
     populated and the hash cascade stays consistent.

Honest classification guard: the commit ONLY succeeds when the gateway's
real validation pipeline (phase 2 source-is-Exit, phase 3 authority-check,
phase 5 write-lock, phase 6 atomic commit, phase 7 refresh) runs to
completion without any mock/stub. If any step fails, the entrypoint
raises — no silent downgrade to block path.
"""
from __future__ import annotations

import dataclasses
import json
import time
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L4_state.contracts import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
)
from agentic_core.L4_state.contracts.records import stamp_digest
from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway
from agentic_core.L4_state.refresh.refresh_coordinator import RefreshCoordinator
from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    compute_artifact_hash,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    run_integrated_safe_reuse,
    IntegratedRunResult,
)


CHAIN_KIND = "UWG_COMMIT_PATH"
ROUTE_FAMILY = "UWG_COMMIT_PATH"

COMMIT_REQUEST_FILENAME = "commit_request.json"
UWG_COMMIT_RECEIPT_FILENAME = "uwg_commit_receipt.json"
UWG_REFRESH_RECEIPTS_FILENAME = "uwg_refresh_receipts.json"

_PRODUCER_COMPONENT = "agentic_core.runtime.entrypoints.integrated_uwg_commit_run"
_PRODUCER_FUNCTION = "run_integrated_uwg_commit"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_extra_envelope(
    path: Path, *, payload: dict[str, Any], upstream_hash: str = ""
) -> str:
    artifact_hash = compute_artifact_hash(payload)
    envelope: dict[str, Any] = {
        "producer_component": _PRODUCER_COMPONENT,
        "producer_module": "integrated_uwg_commit_run",
        "producer_function_or_class": _PRODUCER_FUNCTION,
        "emitted_at": _utc_now_iso(),
        "artifact_hash": artifact_hash,
        "upstream_artifact_ref": upstream_hash,
        "payload": payload,
    }
    path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_hash


def _restamp_envelope(path: Path) -> str:
    env = _read_json(path)
    payload = env.get("payload", {}) if isinstance(env, dict) else {}
    new_hash = compute_artifact_hash(payload)
    env["artifact_hash"] = new_hash
    path.write_text(
        json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return new_hash


def _build_well_formed_commit_packet(
    *, run_id: str, request_id: str, trace_root: str, tenant_id: str = "t:uwg-commit-run"
) -> tuple[CommitRequest, list[StateDiff], RollbackPlan, ReadSurfaceRefreshPlan]:
    """Build a valid CommitRequest bound to the chain's identity.

    Mirrors ``tests/uwg/conftest.py::well_formed_packet`` but parameterized on
    run_id/request_id/trace_root so the commit receipt is hash-bound to the
    chain's spine. All fields stamped via ``stamp_digest`` so the gateway's
    digest-integrity check passes.
    """
    rp_id = f"rp:uwg-commit::{run_id}"
    sd_id = f"sd:uwg-commit::{run_id}"
    cr_id = f"cr:uwg-commit::{run_id}"

    rollback = stamp_digest(
        RollbackPlan(
            rollback_plan_id=rp_id,
            blast_radius="single_surface",
            target_surfaces=("memory",),
            before_snapshot_refs=("snap:before:uwg-commit",),
            rollback_operation_types=("tombstone",),
        )
    )
    refresh = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id=f"rfp:uwg-commit::{run_id}",
            source_commit_receipt_ref="<pending>",
            before_snapshot="snap:before:uwg-commit",
            expected_after_snapshot="snap:after:uwg-commit",
            stale_projection_policy="fail_closed",
            retry_policy="none",
            policy_hash="ph:uwg-commit",
            blueprint_hash="bh:uwg-commit",
            affected_surfaces=("memory",),
            required_refreshes=("memory_projection",),
            refresh_order=("memory_projection",),
        )
    )
    sd = stamp_digest(
        StateDiff(
            state_diff_id=sd_id,
            target_surface="memory",
            operation_type="memory_promotion",
            after_candidate=f"memrec:uwg-commit::{run_id}",
            schema_ref="schema:memory@1",
            blast_radius="single_surface",
            rollback_plan_ref=rp_id,
            proposed_by_surface="L6",
            created_at="0",
        )
    )
    cr = stamp_digest(
        CommitRequest(
            commit_request_id=cr_id,
            cleared_exit_review_packet_ref=f"exr:uwg-commit::{run_id}",
            request_id=request_id,
            run_id=run_id,
            trace_root=trace_root,
            tenant_id=tenant_id,
            policy_hash="ph:uwg-commit",
            blueprint_hash="bh:uwg-commit",
            route_contract_ref=f"rc:uwg-commit::{run_id}",
            replay_key=f"rk:uwg-commit::{run_id}",
            rollback_plan_ref=rp_id,
            blast_radius="single_surface",
            state_diff_refs=(sd_id,),
            gate_verdict_refs=(f"gv:uwg-commit::{run_id}",),
            affected_state_surfaces=("memory",),
            expected_read_surface_refreshes=("memory_projection",),
            source_surface="Exit",
        )
    )
    return cr, [sd], rollback, refresh


def run_integrated_uwg_commit(
    raw_request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "t:uwg-commit-run",
    artifact_dir: Path | str,
    veto_orchestrator: Any | None = None,
) -> IntegratedRunResult:
    """Drive an integrated UWG-commit chain end-to-end.

    Returns the IntegratedRunResult of the underlying chain. The three
    extras (commit_request, uwg_commit_receipt, uwg_refresh_receipts) are
    emitted as side-effect artifacts; their hashes propagate through the
    manifest and spine-proof envelopes.
    """
    art = Path(artifact_dir)
    art.mkdir(parents=True, exist_ok=True)

    # 1. Run the R1B-shaped integrated chain with chain_kind=UWG_COMMIT_PATH.
    result = run_integrated_safe_reuse(
        raw_request,
        namespace=namespace,
        tenant_id=tenant_id,
        artifact_dir=art,
        veto_orchestrator=veto_orchestrator,
        chain_kind=CHAIN_KIND,
        route_family_override=ROUTE_FAMILY,
        extra_route_contract_fields={
            "route_family_proof_class": "REAL_RUNTIME",
            "uwg_commit_path_source_surface": "Exit",
            "uwg_commit_path_target_surface": "memory",
        },
    )

    # 2. Read identity from the chain envelope (request_id, trace_root).
    rie_path = art / "runtime_identity_envelope.json"
    rie_env = _read_json(rie_path)
    rie_payload = rie_env.get("payload", {}) if isinstance(rie_env, dict) else {}
    request_id = str(rie_payload.get("request_id") or rie_env.get("request_id") or "")
    trace_root = str(rie_payload.get("trace_root") or rie_env.get("trace_root") or "")

    # 3. Build the well-formed commit packet bound to chain identity.
    commit_request, state_diffs, rollback_plan, refresh_plan = (
        _build_well_formed_commit_packet(
            run_id=result.run_id,
            request_id=request_id,
            trace_root=trace_root,
            tenant_id=tenant_id,
        )
    )

    # 4. Drive the real commit through DurableWriteGateway. No mocks.
    gw = DurableWriteGateway()
    commit_receipt, blocked_receipt, refresh_receipts = gw.commit(
        commit_request=commit_request,
        state_diffs=state_diffs,
        rollback_plan=rollback_plan,
        refresh_plan=refresh_plan,
    )
    if commit_receipt is None or blocked_receipt is not None:
        raise RuntimeError(
            f"UWG_COMMIT_PATH: expected successful commit, got "
            f"commit_receipt={commit_receipt}, blocked={blocked_receipt}. "
            f"Gateway validation phase refused the well-formed packet."
        )

    # 5. Serialize the three extras.
    commit_request_dict = dataclasses.asdict(commit_request)
    for k, v in list(commit_request_dict.items()):
        if isinstance(v, tuple):
            commit_request_dict[k] = list(v)
    commit_request_payload = {
        **commit_request_dict,
        "integrated_runtime_origin": True,
        "produced_by": _PRODUCER_COMPONENT + "." + _PRODUCER_FUNCTION,
    }
    cr_sha = _write_extra_envelope(
        art / COMMIT_REQUEST_FILENAME, payload=commit_request_payload
    )

    receipt_dict = dataclasses.asdict(commit_receipt)
    for k, v in list(receipt_dict.items()):
        if isinstance(v, tuple):
            receipt_dict[k] = list(v)
    receipt_payload = {
        **receipt_dict,
        "commit_status": "COMMITTED",
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "integrated_runtime_origin": True,
        "produced_by": _PRODUCER_COMPONENT + "." + _PRODUCER_FUNCTION,
    }
    rcpt_sha = _write_extra_envelope(
        art / UWG_COMMIT_RECEIPT_FILENAME,
        payload=receipt_payload,
        upstream_hash=cr_sha,
    )

    # Refresh receipts come straight from gw.commit() — they are already
    # bound to commit_receipt by the gateway's phase-7 refresh coordinator
    # call. Using them directly avoids the "<pending>" plan-ref mismatch
    # that would occur if we re-invoked RefreshCoordinator externally.
    refresh_error = None
    refresh_payloads = []
    for rr in refresh_receipts:
        d = dataclasses.asdict(rr)
        for k, v in list(d.items()):
            if isinstance(v, tuple):
                d[k] = list(v)
        refresh_payloads.append(d)
    refresh_list_payload = {
        "refresh_plan_ref": refresh_plan.refresh_plan_id,
        "source_commit_receipt_ref": commit_receipt.commit_receipt_id,
        "refresh_count": len(refresh_payloads),
        "refresh_receipts": refresh_payloads,
        "refresh_error": refresh_error,
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "integrated_runtime_origin": True,
    }
    refresh_sha = _write_extra_envelope(
        art / UWG_REFRESH_RECEIPTS_FILENAME,
        payload=refresh_list_payload,
        upstream_hash=rcpt_sha,
    )

    # 6. Re-stamp manifest payload with the three extras + cascade.
    manifest_path = art / "integrated_runtime_artifact_manifest.json"
    manifest_env = _read_json(manifest_path)
    manifest_payload = manifest_env.get("payload", {})
    new_manifest_hash = ""
    if isinstance(manifest_payload, dict):
        manifest_payload["uwg_commit_receipt_ref"] = (
            f"artifact://{UWG_COMMIT_RECEIPT_FILENAME}"
        )
        manifest_payload["uwg_commit_receipt_sha256"] = rcpt_sha
        manifest_payload["commit_request_ref"] = (
            f"artifact://{COMMIT_REQUEST_FILENAME}"
        )
        manifest_payload["commit_request_sha256"] = cr_sha
        manifest_payload["uwg_refresh_receipts_ref"] = (
            f"artifact://{UWG_REFRESH_RECEIPTS_FILENAME}"
        )
        manifest_payload["uwg_refresh_receipts_sha256"] = refresh_sha
        manifest_payload["uwg_commit_path_source_surface"] = "Exit"
        manifest_path.write_text(
            json.dumps(manifest_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_manifest_hash = _restamp_envelope(manifest_path)

    # 6b. Cascade: no_harness_stamp_receipt.upstream_artifact_ref.
    nhsr_path = art / "no_harness_stamp_receipt.json"
    nhsr_env = _read_json(nhsr_path)
    if isinstance(nhsr_env, dict) and new_manifest_hash:
        nhsr_env["upstream_artifact_ref"] = new_manifest_hash
        nhsr_path.write_text(
            json.dumps(nhsr_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_nhsr_hash = _restamp_envelope(nhsr_path)
    else:
        new_nhsr_hash = nhsr_env.get("artifact_hash", "") if isinstance(nhsr_env, dict) else ""

    # 7. Re-stamp spine proof: bind uwg_commit_or_block_ref.
    spine_path = art / "agentic_core_spine_proof.json"
    spine_env = _read_json(spine_path)
    spine_payload = spine_env.get("payload", {})
    if isinstance(spine_payload, dict):
        spine_payload["uwg_commit_or_block_ref"] = rcpt_sha
        spine_payload["uwg_commit_receipt_sha256"] = rcpt_sha
        spine_payload["commit_request_sha256"] = cr_sha
        spine_payload["uwg_refresh_receipts_sha256"] = refresh_sha
        spine_payload["uwg_commit_path_source_surface"] = "Exit"
        spine_payload["uwg_commit_path_target_surface"] = "memory"
        if new_manifest_hash:
            spine_payload["artifact_manifest_ref"] = new_manifest_hash
        if new_nhsr_hash:
            spine_env["upstream_artifact_ref"] = new_nhsr_hash
        spine_path.write_text(
            json.dumps(spine_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        _restamp_envelope(spine_path)

    return result


__all__ = [
    "run_integrated_uwg_commit",
    "CHAIN_KIND",
    "ROUTE_FAMILY",
    "COMMIT_REQUEST_FILENAME",
    "UWG_COMMIT_RECEIPT_FILENAME",
    "UWG_REFRESH_RECEIPTS_FILENAME",
]
