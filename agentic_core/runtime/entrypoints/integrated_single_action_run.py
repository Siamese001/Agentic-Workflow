"""R4_SINGLE_ACTION — integrated runtime entrypoint.

W4.2 closure of plan fortknox-100pct-static-runtime-gap-9a3d4f §GAP-6b.

Drives a real single-action L2 invocation. The action is a deterministic
hash-based tool — no network, no LLM — but it executes for real (not a
stub) and produces real tool_invocations entries with input_hash,
output_hash, and an authorization receipt referencing a committed
ToolRegistryRecord surrogate.

The substrate is honest at the following levels:

  - Tool is a real callable that consumes input bytes and returns a
    real sha256 hash. Deterministic, reproducible, verifiable.
  - Tool authorization is a real gate: the caller must hold a
    capability-token whose target tool_id matches the one being
    invoked. No token ⇒ authorization fails ⇒ chain fails closed.
  - The sealed_l2_artifact.json emitted has structural_only=False and
    tool_invocations is a non-empty list of real execution records.

What is NOT in scope for W4.2:

  - Real LLM / model invocation — not required for the single-action
    semantic. Can be layered on later by extending the tool registry.
  - Full tool-registry schema with ToolRegistryRecord rows in UWG —
    the committed TOOL_REGISTRY_RECORDS constant below is the
    development surrogate.
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    compute_artifact_hash,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    run_integrated_safe_reuse,
    IntegratedRunResult,
)


CHAIN_KIND = "R4_SINGLE_ACTION"
ROUTE_FAMILY = "R4_SINGLE_ACTION"

SEALED_L2_ARTIFACT_FILENAME = "sealed_l2_artifact.json"
TOOL_AUTHORIZATION_RECEIPT_FILENAME = "tool_authorization_receipt.json"

_PRODUCER_COMPONENT = "agentic_core.runtime.entrypoints.integrated_single_action_run"
_PRODUCER_FUNCTION = "run_integrated_single_action"


# Development surrogate for a ToolRegistryRecord. Committed to the repo
# so every run reproduces the same tool binding.
TOOL_REGISTRY_RECORDS: dict[str, dict[str, Any]] = {
    "tool::hash_bytes::v1": {
        "tool_id": "tool::hash_bytes::v1",
        "tool_name": "hash_bytes",
        "tool_class": "deterministic_compute",
        "required_capability": "cap::deterministic_compute",
        "schema_version": "1.0.0",
        "output_contract_sha256": hashlib.sha256(b"sha256_hex_output_v1").hexdigest(),
    },
}


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_extra_envelope(
    path: Path, *, payload: dict[str, Any], upstream_hash: str = ""
) -> str:
    artifact_hash = compute_artifact_hash(payload)
    envelope = {
        "producer_component": _PRODUCER_COMPONENT,
        "producer_module": "integrated_single_action_run",
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


def _authorize_tool(
    *, tool_id: str, required_capability: str, caller_capabilities: tuple[str, ...]
) -> dict[str, Any]:
    """Real authorization gate. Fail-closed on missing capability."""
    if tool_id not in TOOL_REGISTRY_RECORDS:
        return {
            "authorization_status": "DENIED",
            "reason": f"tool_id {tool_id!r} not in TOOL_REGISTRY_RECORDS",
            "tool_id": tool_id,
            "authorized_at_utc": _utc_now_iso(),
        }
    if required_capability not in caller_capabilities:
        return {
            "authorization_status": "DENIED",
            "reason": f"caller missing required_capability {required_capability!r}",
            "tool_id": tool_id,
            "authorized_at_utc": _utc_now_iso(),
        }
    registry_entry = TOOL_REGISTRY_RECORDS[tool_id]
    return {
        "authorization_status": "GRANTED",
        "tool_id": tool_id,
        "tool_registry_record_sha256": hashlib.sha256(
            json.dumps(registry_entry, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "required_capability": required_capability,
        "caller_capabilities": list(caller_capabilities),
        "authorized_at_utc": _utc_now_iso(),
    }


def _invoke_tool(tool_id: str, input_bytes: bytes) -> dict[str, Any]:
    """Real tool execution. For hash_bytes: returns sha256 hex of input.

    Deterministic, reproducible — every run with the same input yields
    the same output_hash. That is the substrate guarantee.
    """
    if tool_id != "tool::hash_bytes::v1":
        raise ValueError(f"unknown tool_id: {tool_id}")
    output_bytes = hashlib.sha256(input_bytes).hexdigest().encode("ascii")
    return {
        "tool_invocation_id": f"inv::{uuid.uuid4()}",
        "tool_id": tool_id,
        "input_bytes_sha256": hashlib.sha256(input_bytes).hexdigest(),
        "input_byte_length": len(input_bytes),
        "output_payload": output_bytes.decode("ascii"),
        "output_payload_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "output_byte_length": len(output_bytes),
        "deterministic": True,
        "invoked_at_utc": _utc_now_iso(),
    }


def run_integrated_single_action(
    raw_request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "t:r4-single-action-run",
    artifact_dir: Path | str,
    tool_id: str = "tool::hash_bytes::v1",
    tool_input: bytes = b"R4_SINGLE_ACTION canonical input for L2 invocation",
    caller_capabilities: tuple[str, ...] = ("cap::deterministic_compute",),
    veto_orchestrator: Any | None = None,
) -> IntegratedRunResult:
    """Drive an integrated R4_SINGLE_ACTION chain end-to-end.

    Emits two family extras:
      - tool_authorization_receipt.json — real cap-token auth result
      - sealed_l2_artifact.json — typed sealed artifact with
        structural_only=False and a non-empty tool_invocations list.
    """
    art = Path(artifact_dir)
    art.mkdir(parents=True, exist_ok=True)

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
            "r4_single_action_tool_id": tool_id,
        },
    )

    rie_env = _read_json(art / "runtime_identity_envelope.json")
    rie_payload = rie_env.get("payload", {}) if isinstance(rie_env, dict) else {}
    request_id = str(rie_payload.get("request_id") or rie_env.get("request_id") or "")
    trace_root = str(rie_payload.get("trace_root") or rie_env.get("trace_root") or "")

    # 1. Authorize the tool invocation.
    required_cap = TOOL_REGISTRY_RECORDS[tool_id]["required_capability"]
    auth = _authorize_tool(
        tool_id=tool_id,
        required_capability=required_cap,
        caller_capabilities=caller_capabilities,
    )
    auth_payload = {
        **auth,
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "integrated_runtime_origin": True,
        "produced_by": _PRODUCER_COMPONENT + "." + _PRODUCER_FUNCTION,
    }
    auth_sha = _write_extra_envelope(
        art / TOOL_AUTHORIZATION_RECEIPT_FILENAME, payload=auth_payload
    )
    if auth["authorization_status"] != "GRANTED":
        raise RuntimeError(
            f"R4_SINGLE_ACTION: tool authorization DENIED — {auth.get('reason')}"
        )

    # 2. Execute the real tool.
    invocation = _invoke_tool(tool_id, tool_input)

    # 3. Emit typed sealed L2 artifact.
    sealed_payload = {
        "sealed_l2_artifact_id": f"seal::l2::{result.run_id}",
        "schema_version": "1.0.0",
        "structural_only": False,
        "tool_invocations": [invocation],
        "tool_invocation_count": 1,
        "tool_authorizations": [
            {
                "tool_id": tool_id,
                "tool_registry_record_sha256": auth["tool_registry_record_sha256"],
                "authorization_receipt_ref": auth_sha,
                "required_capability": required_cap,
            }
        ],
        "model_invocations": [],  # not in scope for W4.2
        "model_invocation_count": 0,
        "l2_execution_deterministic": True,
        "run_id": result.run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "integrated_runtime_origin": True,
        "produced_by": _PRODUCER_COMPONENT + "." + _PRODUCER_FUNCTION,
    }
    sealed_sha = _write_extra_envelope(
        art / SEALED_L2_ARTIFACT_FILENAME,
        payload=sealed_payload,
        upstream_hash=auth_sha,
    )

    # 4. Cascade manifest + spine.
    manifest_path = art / "integrated_runtime_artifact_manifest.json"
    manifest_env = _read_json(manifest_path)
    manifest_payload = manifest_env.get("payload", {})
    new_manifest_hash = ""
    if isinstance(manifest_payload, dict):
        manifest_payload["tool_authorization_receipt_ref"] = (
            f"artifact://{TOOL_AUTHORIZATION_RECEIPT_FILENAME}"
        )
        manifest_payload["tool_authorization_receipt_sha256"] = auth_sha
        manifest_payload["sealed_l2_artifact_ref"] = (
            f"artifact://{SEALED_L2_ARTIFACT_FILENAME}"
        )
        manifest_payload["sealed_l2_artifact_sha256"] = sealed_sha
        manifest_payload["r4_tool_id"] = tool_id
        manifest_payload["r4_tool_invocation_count"] = 1
        manifest_path.write_text(
            json.dumps(manifest_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_manifest_hash = _restamp_envelope(manifest_path)

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

    spine_path = art / "agentic_core_spine_proof.json"
    spine_env = _read_json(spine_path)
    spine_payload = spine_env.get("payload", {})
    if isinstance(spine_payload, dict):
        spine_payload["sealed_l2_artifact_sha256"] = sealed_sha
        spine_payload["tool_authorization_receipt_sha256"] = auth_sha
        spine_payload["r4_tool_id"] = tool_id
        spine_payload["r4_tool_invocation_count"] = 1
        spine_payload["r4_l2_structural_only"] = False
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
    "run_integrated_single_action",
    "CHAIN_KIND",
    "ROUTE_FAMILY",
    "SEALED_L2_ARTIFACT_FILENAME",
    "TOOL_AUTHORIZATION_RECEIPT_FILENAME",
    "TOOL_REGISTRY_RECORDS",
]
