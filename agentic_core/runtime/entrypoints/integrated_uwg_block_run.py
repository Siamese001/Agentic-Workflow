"""UWG_BLOCK_PATH — integrated runtime entrypoint.

Drives a real blocked commit through ``DurableWriteGateway.reject_direct_write``
inside the governed integrated-runtime spine. The point of this entrypoint
is to graduate UWG_BLOCK_PATH from FIXTURE_ONLY to REAL_RUNTIME — the
existing ``tests/uwg/test_no_direct_l4_write.py`` proves the receipt
emission path in isolation, but no integrated chain previously bound a
blocked-commit receipt to the L7 spine.

What this entrypoint does, in order:

  1. Run the standard integrated chain to ``artifact_dir`` with
     ``chain_kind="UWG_BLOCK_PATH"`` and
     ``route_family_override="UWG_BLOCK_PATH"``. This emits the same 20
     R1B-shaped artifacts (route_contract, bypass receipts, terminal
     packet, x3 receipt, runtime_exhaust, runtime_trace_snapshot, HOW
     trace, coverage matrix, manifest, no_harness_stamp, spine proof).

  2. Drive a typed ``UWGBlockedCommitReceipt`` by calling
     ``DurableWriteGateway.reject_direct_write`` from a non-authorized
     surface ("L0"). The receipt has the same run_id / request_id
     identity as the chain.

  3. Emit two extra spine artifacts:

       - ``commit_request.json`` — the (would-be) commit request that
         the gateway rejected. Carries the run_id/request_id/trace_root
         identity and the attempting_surface field.
       - ``uwg_blocked_commit_receipt.json`` — the typed receipt
         serialized as a payload. Bound by hash to the chain via the
         spine bundle's ``uwg_commit_or_block_ref`` field.

  4. Re-stamp the artifact manifest with the two extras and
     re-emit the spine bundle so that ``uwg_commit_or_block_ref`` and
     ``uwg_block_receipt_sha256`` are populated.

R1A-style "borrow R1B artifacts" is forbidden: every UWG_BLOCK run gets
its own run_id / request_id / trace_root and its own HOW trace + Fort
Knox L7 evidence. The verifier ``verify_uwg_block_path_l7_runtime.py``
asserts the receipt is integrated (not fixture) and bound by hash to the
spine.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from agentic_core.L4_state.contracts.records import UWGBlockedCommitReceipt
from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway
from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    compute_artifact_hash,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    run_integrated_safe_reuse,
    IntegratedRunResult,
)


CHAIN_KIND = "UWG_BLOCK_PATH"
ROUTE_FAMILY = "UWG_BLOCK_PATH"

# Filenames for the two integrated UWG-block extras.
COMMIT_REQUEST_FILENAME = "commit_request.json"
UWG_BLOCKED_COMMIT_RECEIPT_FILENAME = "uwg_blocked_commit_receipt.json"


_PRODUCER_COMPONENT = "agentic_core.runtime.entrypoints.integrated_uwg_block_run"
_PRODUCER_FUNCTION = "run_integrated_uwg_block"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_extra_envelope(
    path: Path, *, payload: dict[str, Any], upstream_hash: str = ""
) -> str:
    """Write a chain-style envelope for an integrated extra artifact.

    The envelope shape mirrors agentic_core.runtime.artifacts.
    integrated_runtime_emitter.emit_artifact so the spine-bundle hash-
    resolution helper can read ``artifact_hash`` from the file.
    """
    artifact_hash = compute_artifact_hash(payload)
    envelope: dict[str, Any] = {
        "producer_component": _PRODUCER_COMPONENT,
        "producer_module": "integrated_uwg_block_run",
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
    """Recompute artifact_hash for an envelope after payload mutation."""
    env = _read_json(path)
    payload = env.get("payload", {}) if isinstance(env, dict) else {}
    new_hash = compute_artifact_hash(payload)
    env["artifact_hash"] = new_hash
    path.write_text(
        json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return new_hash


def run_integrated_uwg_block(
    raw_request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "",
    artifact_dir: Path | str,
    veto_orchestrator: Any | None = None,
    attempting_surface: str = "L0",
    target_surface: str = "memory",
    block_reason: str = "non_uwg_surface_attempted_direct_write",
) -> IntegratedRunResult:
    """Drive an integrated UWG-block chain end-to-end.

    Returns the IntegratedRunResult of the underlying chain. The two
    extras (commit_request, uwg_blocked_commit_receipt) are emitted as
    side-effect artifacts; their hashes are recorded in the artifact
    manifest's ``artifact_hashes`` map at re-stamp time below.
    """
    art = Path(artifact_dir)
    art.mkdir(parents=True, exist_ok=True)

    # 1. Run the R1B-shaped integrated chain with chain_kind=UWG_BLOCK_PATH.
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
            "uwg_block_path_attempted_surface": attempting_surface,
            "uwg_block_path_target_surface": target_surface,
        },
    )

    # 2. Read identity from the chain envelope (request_id, trace_root).
    rie_path = art / "runtime_identity_envelope.json"
    rie_env = _read_json(rie_path)
    rie_payload = rie_env.get("payload", {}) if isinstance(rie_env, dict) else {}
    request_id = str(rie_payload.get("request_id") or rie_env.get("request_id") or "")
    trace_root = str(rie_payload.get("trace_root") or rie_env.get("trace_root") or "")

    # 3. Drive a real blocked commit via DurableWriteGateway. The gateway
    # constructs a typed UWGBlockedCommitReceipt and audit-appends a
    # blocked-attempt record. We capture the receipt and serialize it.
    gw = DurableWriteGateway()
    blocked_receipt: UWGBlockedCommitReceipt = gw.reject_direct_write(
        attempting_surface=attempting_surface,
        target_surface=target_surface,
        reason=block_reason,
        request_id=request_id,
        run_id=result.run_id,
    )

    # 4. Emit the (would-be) commit_request envelope. It documents the
    # request that the gateway rejected — useful for forensic replay.
    identity = {
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
    }
    commit_request_payload = {
        "commit_request_id": f"NO_COMMIT_REQUEST::direct_attempt_by::{attempting_surface}",
        "attempting_surface": attempting_surface,
        "target_surface": target_surface,
        "block_reason": block_reason,
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "would_have_been_committed": False,
        "rejected_by": (
            "agentic_core.L4_state.uwg.durable_write_gateway."
            "DurableWriteGateway.reject_direct_write"
        ),
    }
    cr_sha = _write_extra_envelope(
        art / COMMIT_REQUEST_FILENAME, payload=commit_request_payload
    )

    # 4. Emit the typed UWGBlockedCommitReceipt as the chain artifact.
    receipt_dict = dataclasses.asdict(blocked_receipt)
    # Convert tuple/frozenset fields to lists for JSON.
    for k, v in list(receipt_dict.items()):
        if isinstance(v, tuple):
            receipt_dict[k] = list(v)
    receipt_payload = {
        "blocked_commit_receipt_id": receipt_dict.get("blocked_commit_receipt_id"),
        "commit_request_ref": receipt_dict.get("commit_request_ref"),
        "snapshot_before": receipt_dict.get("snapshot_before"),
        "audit_append_receipt_ref": receipt_dict.get("audit_append_receipt_ref"),
        "blocked_reason_codes": receipt_dict.get("blocked_reason_codes", []),
        "failed_rule_ids": receipt_dict.get("failed_rule_ids", []),
        "state_surfaces_requested": receipt_dict.get(
            "state_surfaces_requested", []
        ),
        "attempting_surface": attempting_surface,
        "target_surface": target_surface,
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "integrated_runtime_origin": True,
        "produced_by": _PRODUCER_COMPONENT + "." + _PRODUCER_FUNCTION,
    }
    rcpt_sha = _write_extra_envelope(
        art / UWG_BLOCKED_COMMIT_RECEIPT_FILENAME,
        payload=receipt_payload,
        upstream_hash=cr_sha,
    )

    # 5. Re-stamp manifest payload (NOT artifact_filenames — those stay
    # at the canonical W2 chain set; extras are bound via dedicated
    # *_ref / *_sha256 fields). Then propagate the new hash through
    # downstream chain links: no_harness_stamp_receipt.upstream_artifact_ref
    # and spine.artifact_manifest_ref / spine.upstream_artifact_ref.
    manifest_path = art / "integrated_runtime_artifact_manifest.json"
    manifest_env = _read_json(manifest_path)
    manifest_payload = manifest_env.get("payload", {})
    new_manifest_hash = ""
    if isinstance(manifest_payload, dict):
        manifest_payload["uwg_blocked_commit_receipt_ref"] = (
            f"artifact://{UWG_BLOCKED_COMMIT_RECEIPT_FILENAME}"
        )
        manifest_payload["uwg_blocked_commit_receipt_sha256"] = rcpt_sha
        manifest_payload["commit_request_ref"] = (
            f"artifact://{COMMIT_REQUEST_FILENAME}"
        )
        manifest_payload["commit_request_sha256"] = cr_sha
        manifest_payload["uwg_block_path_attempting_surface"] = attempting_surface
        manifest_path.write_text(
            json.dumps(manifest_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_manifest_hash = _restamp_envelope(manifest_path)

    # 5b. Cascade: no_harness_stamp_receipt.upstream_artifact_ref must
    # equal the new manifest hash, and its own artifact_hash must be
    # recomputed for the unchanged payload (no payload change here, but
    # we re-stamp anyway for safety).
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

    # 6. Re-stamp spine proof: bind uwg_commit_or_block_ref and refresh
    # artifact_manifest_ref + upstream_artifact_ref to match the new
    # manifest / no_harness hashes. Then recompute spine.artifact_hash.
    spine_path = art / "agentic_core_spine_proof.json"
    spine_env = _read_json(spine_path)
    spine_payload = spine_env.get("payload", {})
    if isinstance(spine_payload, dict):
        spine_payload["uwg_commit_or_block_ref"] = rcpt_sha
        spine_payload["uwg_block_receipt_sha256"] = rcpt_sha
        spine_payload["commit_request_sha256"] = cr_sha
        spine_payload["uwg_block_path_attempting_surface"] = attempting_surface
        spine_payload["uwg_block_path_target_surface"] = target_surface
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
    "run_integrated_uwg_block",
    "CHAIN_KIND",
    "ROUTE_FAMILY",
    "COMMIT_REQUEST_FILENAME",
    "UWG_BLOCKED_COMMIT_RECEIPT_FILENAME",
]
