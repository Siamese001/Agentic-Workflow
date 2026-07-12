"""Content-addressed E5 receipt bundles for apps_rg governed L2."""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from apps_rg.runtime.bindings.l2_authority_contracts import (
    AuthorityGateReceipt,
    FrozenExecutionRoom,
    L2AuthorityError,
    ReceiptBundleResult,
    SignedAppsRgL2ExecutionPacket,
    _jsonable,
    _string,
    _tuple_strings,
    sha256_hex,
)


def compute_attempt_output_digest(attempt_receipt: Any) -> str:
    return sha256_hex(
        {
            "result_class": _string(
                getattr(getattr(attempt_receipt, "result_class", ""), "value", "")
                or getattr(attempt_receipt, "result_class", "")
            ),
            "return_code": getattr(attempt_receipt, "return_code", None),
            "proposed_state_diff": getattr(
                attempt_receipt,
                "proposed_state_diff",
                {},
            )
            or {},
            "local_check_results": getattr(
                attempt_receipt,
                "local_check_results",
                {},
            )
            or {},
            "error_summary": _string(
                getattr(attempt_receipt, "error_summary", "")
            ),
        }
    )


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            _jsonable(payload),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _receipt_payload(
    validation_output: Any,
    gate_receipts: Sequence[AuthorityGateReceipt],
) -> dict[str, Any]:
    payload = _jsonable(validation_output)
    if not isinstance(payload, dict):
        payload = {"validation_output": payload}
    payload["authority_gate_receipts"] = [
        _jsonable(item) for item in gate_receipts
    ]
    payload["gate_refs"] = [item.ref for item in gate_receipts]
    payload["unknown_never_pass"] = True
    return payload


def finalize_content_addressed_bundle(
    *,
    artifact_dir: Path,
    packet: SignedAppsRgL2ExecutionPacket,
    frozen_room: FrozenExecutionRoom,
    gate_receipts: Sequence[AuthorityGateReceipt],
    prep_output: Any,
    validation_output: Any,
    attempt_receipt: Any | None,
    heal_receipt: Any | None,
    sealed: Any,
) -> ReceiptBundleResult:
    """Write receipts, hash their content, and return the final seal."""
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    files: dict[str, Any] = {
        "l2_execution_packet.json": packet,
        "frozen_execution_context.json": frozen_room,
        "prep_receipt.json": prep_output,
        "validation_receipt.json": _receipt_payload(
            validation_output,
            gate_receipts,
        ),
    }
    if attempt_receipt is not None:
        files["attempt_receipt.json"] = attempt_receipt
    if heal_receipt is not None:
        files["heal_receipt.json"] = heal_receipt
    for name, payload in files.items():
        _write_json(root / name, payload)

    receipt_hashes = {
        name: sha256_hex(_jsonable(payload))
        for name, payload in sorted(files.items())
    }
    seal_payload = {
        "packet_digest": packet.packet_digest,
        "packet_signature": packet.packet_signature,
        "frozen_room_digest": frozen_room.room_digest,
        "receipt_hashes": receipt_hashes,
        "request_id": _string(getattr(sealed, "request_id", "")),
        "run_id": _string(getattr(sealed, "run_id", "")),
        "trace_id": _string(getattr(sealed, "trace_id", "")),
        "route_id": packet.route_id,
        "workflow_id": packet.workflow_id,
        "node_id": packet.node_id,
        "step_id": packet.step_id,
        "prompt_hash": packet.prompt_hash,
        "policy_hash": packet.policy_hash,
        "blueprint_hash": packet.blueprint_hash,
        "replay_key": packet.replay_key,
        "generated_content_digest": sha256_hex(
            _string(getattr(sealed, "generated_content", ""))
        ),
        "proposed_state_diff_digest": sha256_hex(
            getattr(sealed, "proposed_state_diff", {}) or {}
        ),
        "evidence_refs": _tuple_strings(
            getattr(sealed, "evidence_refs", ())
        ),
        "provider_receipts": _tuple_strings(
            getattr(sealed, "provider_receipts", ())
        ),
        "model_call_refs": _tuple_strings(
            getattr(sealed, "model_call_refs", ())
        ),
        "gate_refs": tuple(receipt.ref for receipt in gate_receipts),
        "state_diff_authorized": False,
        "is_uwg_write_authority": False,
    }
    final_seal_digest = sha256_hex(seal_payload)
    audit_refs = tuple(getattr(sealed, "audit_refs", ()) or ()) + (
        f"l2_packet:{packet.packet_digest}",
        f"frozen_execution_room:{frozen_room.room_digest}",
        *(
            f"receipt:{name}:{digest}"
            for name, digest in sorted(receipt_hashes.items())
        ),
    )
    gate_refs = tuple(getattr(sealed, "gate_verdict_refs", ()) or ()) + tuple(
        receipt.ref for receipt in gate_receipts
    )
    snapshot_refs = tuple(getattr(sealed, "snapshot_refs", ()) or ()) + (
        packet.packet_digest,
        frozen_room.room_digest,
    )
    final_sealed = replace(
        sealed,
        compilation_hash=final_seal_digest,
        prompt_artifact_digest=packet.prompt_hash,
        sovereign_execution_receipt=f"l2_packet:{packet.packet_digest}",
        audit_refs=tuple(dict.fromkeys(audit_refs)),
        gate_verdict_refs=tuple(dict.fromkeys(gate_refs)),
        snapshot_refs=tuple(dict.fromkeys(snapshot_refs)),
        audit_manifest_ref="l2_receipt_bundle.json",
        state_diff_authorized=False,
        is_uwg_write_authority=False,
    )
    _write_json(root / "seal_receipt.json", final_sealed)
    receipt_hashes["seal_receipt.json"] = sha256_hex(_jsonable(final_sealed))

    manifest_without_digest = {
        "schema_version": "apps_rg.l2_receipt_bundle.v2",
        "request_id": packet.request_id,
        "run_id": packet.run_id,
        "trace_id": packet.trace_id,
        "route_id": packet.route_id,
        "packet_digest": packet.packet_digest,
        "packet_signature": packet.packet_signature,
        "frozen_room_digest": frozen_room.room_digest,
        "seal_digest": final_seal_digest,
        "receipt_hashes": dict(sorted(receipt_hashes.items())),
        "gate_refs": [receipt.ref for receipt in gate_receipts],
        "unknown_never_pass": True,
        "state_diff_authorized": False,
        "is_uwg_write_authority": False,
    }
    bundle = dict(manifest_without_digest)
    bundle["bundle_digest"] = sha256_hex(manifest_without_digest)
    _write_json(root / "l2_receipt_bundle.json", bundle)
    return ReceiptBundleResult(sealed=final_sealed, bundle=bundle)


def build_authority_rejection_seal(
    prompt_artifact: Any,
    error: L2AuthorityError,
) -> Any:
    """Create a provider-free sealed rejection for authority failures."""
    from agentic_core.runtime.contracts.origin import Origin
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact

    payload = {
        "status": "REJECTED",
        "decisive_reason_code": error.code,
        "reason": error.reason,
        "field": error.field_name,
    }
    digest = sha256_hex(
        {
            "request_id": _string(getattr(prompt_artifact, "request_id", "")),
            "run_id": _string(getattr(prompt_artifact, "run_id", "")),
            "trace_id": _string(getattr(prompt_artifact, "trace_id", "")),
            "rejection": payload,
        }
    )
    return SealedL2Artifact(
        request_id=_string(getattr(prompt_artifact, "request_id", "")),
        run_id=_string(getattr(prompt_artifact, "run_id", "")),
        app_id=_string(getattr(prompt_artifact, "app_id", "")) or "apps_rg",
        trace_id=_string(getattr(prompt_artifact, "trace_id", "")),
        execution_status="rejected",
        generated_content=json.dumps(payload, sort_keys=True),
        generated_content_origin=Origin.SYSTEM_INTERNAL,
        proposed_state_diff={"rejection": payload},
        state_diff_authorized=False,
        tenant_id=_string(getattr(prompt_artifact, "tenant_id", "")),
        sandbox_required=bool(
            getattr(prompt_artifact, "sandbox_required", False)
        ),
        egress_policy_ref=_string(
            getattr(prompt_artifact, "egress_policy_ref", "")
        ),
        allowed_tools=_tuple_strings(
            getattr(prompt_artifact, "allowed_tools", ())
        ),
        allowed_models=_tuple_strings(
            getattr(prompt_artifact, "allowed_models", ())
        ),
        allowed_networks=_tuple_strings(
            getattr(prompt_artifact, "allowed_networks", ())
        ),
        allowed_file_roots=_tuple_strings(
            getattr(prompt_artifact, "allowed_file_roots", ())
        ),
        prompt_artifact_digest=_string(
            getattr(prompt_artifact, "compilation_hash", "")
        ),
        schema_version=(
            _string(getattr(prompt_artifact, "schema_version", "")) or "W6.0"
        ),
        compilation_hash=digest,
        audit_refs=(f"l2_authority_rejection:{error.code}",),
        gate_verdict_refs=("G11:FAIL", "G12:FAIL"),
        replay_key=_string(getattr(prompt_artifact, "replay_key", "")),
        snapshot_refs=_tuple_strings(
            getattr(prompt_artifact, "snapshot_refs", ())
        ),
        is_uwg_write_authority=False,
        l5_certification_ref=_string(
            getattr(prompt_artifact, "l5_certification_ref", "")
        ),
        evidence_refs=(),
        prompt_refs=(),
        provider_receipts=(),
        model_call_refs=(),
        replay_manifest=_string(
            getattr(prompt_artifact, "replay_manifest_ref", "")
        ),
    )


def write_authority_rejection_bundle(
    artifact_dir: Path,
    sealed: Any,
    error: L2AuthorityError,
) -> Mapping[str, Any]:
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    rejection = {
        "schema_version": "apps_rg.l2_authority_rejection.v1",
        "decisive_reason_code": error.code,
        "reason": error.reason,
        "field": error.field_name,
        "provider_invoked": False,
        "state_diff_authorized": False,
        "is_uwg_write_authority": False,
    }
    _write_json(root / "authority_rejection_receipt.json", rejection)
    _write_json(root / "seal_receipt.json", sealed)
    hashes = {
        "authority_rejection_receipt.json": sha256_hex(rejection),
        "seal_receipt.json": sha256_hex(_jsonable(sealed)),
    }
    manifest = {
        "schema_version": "apps_rg.l2_receipt_bundle.v2",
        "request_id": _string(getattr(sealed, "request_id", "")),
        "run_id": _string(getattr(sealed, "run_id", "")),
        "trace_id": _string(getattr(sealed, "trace_id", "")),
        "execution_status": "rejected",
        "provider_invoked": False,
        "receipt_hashes": hashes,
        "state_diff_authorized": False,
        "is_uwg_write_authority": False,
    }
    manifest["bundle_digest"] = sha256_hex(manifest)
    _write_json(root / "l2_receipt_bundle.json", manifest)
    return manifest


__all__ = [
    "build_authority_rejection_seal",
    "compute_attempt_output_digest",
    "finalize_content_addressed_bundle",
    "write_authority_rejection_bundle",
]
