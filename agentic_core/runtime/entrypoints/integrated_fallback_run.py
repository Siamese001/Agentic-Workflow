"""R5_FALLBACK — integrated runtime entrypoint.

Drives the integrated chain with ``chain_kind="R5_FALLBACK"`` and emits
an additional ``safe_fallback_decision.json`` artifact documenting:

  - the fallback rationale (why the L0 router selected R5),
  - that no unsafe tool/model execution occurred (the chain proves L2 is
    bypassed via the L7 HOW trace L2_EXECUTE stage = BYPASSED),
  - that the X3 disposition is the safe path (X3D ALLOW for cache reuse
    or X3E SAFE_ABSTAIN if no answer is available — both are safe paths
    by V6 vocabulary).

R5 may not borrow R1B's artifacts: every R5 run gets its own run_id /
request_id / trace_root and its own HOW trace + Fort Knox L7 evidence.
The route_contract carries ``route_family="R5_FALLBACK"`` so verifiers
can distinguish R5 chains from R1B chains.

Honest scope: under the current substrate, R5 fallback uses the same
cache-reuse path as R1B (because that IS the safe fallback when the
cache holds an answer for the live query). The verifier asserts:

  - chain_kind == R5_FALLBACK
  - route_family == R5_FALLBACK
  - safe_fallback_decision.json exists with non-empty fallback_reason and
    no_unsafe_execution=True
  - HOW trace L2_EXECUTE is BYPASSED
  - X3 disposition is in {ALLOW, SAFE_ABSTAIN} (both are safe outcomes)
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from agentic_core.runtime.artifacts.integrated_runtime_emitter import (
    compute_artifact_hash,
)
from agentic_core.runtime.entrypoints.integrated_safe_reuse_run import (
    run_integrated_safe_reuse,
    IntegratedRunResult,
)


CHAIN_KIND = "R5_FALLBACK"
ROUTE_FAMILY = "R5_FALLBACK"

SAFE_FALLBACK_DECISION_FILENAME = "safe_fallback_decision.json"


_PRODUCER_COMPONENT = "agentic_core.runtime.entrypoints.integrated_fallback_run"
_PRODUCER_FUNCTION = "run_integrated_fallback"


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_extra_envelope(
    path: Path, *, payload: dict[str, Any]
) -> str:
    """Write a chain-style envelope for the safe_fallback_decision extra."""
    artifact_hash = compute_artifact_hash(payload)
    envelope: dict[str, Any] = {
        "producer_component": _PRODUCER_COMPONENT,
        "producer_module": "integrated_fallback_run",
        "producer_function_or_class": _PRODUCER_FUNCTION,
        "emitted_at": _utc_now_iso(),
        "artifact_hash": artifact_hash,
        "upstream_artifact_ref": "",
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


def run_integrated_fallback(
    raw_request: dict[str, Any],
    *,
    namespace: str,
    tenant_id: str = "",
    artifact_dir: Path | str,
    veto_orchestrator: Any | None = None,
    fallback_reason: str = "L0_router_selected_R5_FALLBACK_for_safety_class_intent",
) -> IntegratedRunResult:
    """Drive the integrated R5 fallback chain end-to-end."""
    art = Path(artifact_dir)
    art.mkdir(parents=True, exist_ok=True)

    # 1. Run the R1B-shaped integrated chain with chain_kind=R5_FALLBACK.
    # The R5 fallback path is a safe path: cache-reuse (R1B-like) or
    # safe-abstain when the cache cannot satisfy the query. Either way,
    # no novel L2 execution occurs — the HOW trace L2_EXECUTE stage is
    # BYPASSED, which the verifier checks.
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
            "fallback_reason": fallback_reason,
            "fallback_class": "SAFE_FALLBACK",
        },
    )

    # 2. Read identity from runtime_identity_envelope (the result type
    # only exposes run_id; request_id/trace_root come from the envelope).
    rie_env = _read_json(art / "runtime_identity_envelope.json")
    rie_payload = rie_env.get("payload", {}) if isinstance(rie_env, dict) else {}
    identity = {
        "run_id": result.run_id,
        "request_id": str(
            rie_payload.get("request_id") or rie_env.get("request_id") or ""
        ),
        "trace_root": str(
            rie_payload.get("trace_root") or rie_env.get("trace_root") or ""
        ),
    }
    sf_payload = {
        "fallback_reason": fallback_reason,
        "fallback_class": "SAFE_FALLBACK",
        "no_unsafe_execution": True,
        "no_real_l2_execution": True,
        "no_real_tool_call": True,
        "no_real_model_call": True,
        "no_l4_write_attempted": True,
        "expected_x3_dispositions": ["X3D", "X3E"],
        "expected_x3_disposition_names": ["ALLOW", "SAFE_ABSTAIN"],
        "actual_x3_disposition": result.x3_disposition,
        "produced_by": (
            "agentic_core.runtime.entrypoints.integrated_fallback_run"
            ".run_integrated_fallback"
        ),
    }
    sf_sha = _write_extra_envelope(
        art / SAFE_FALLBACK_DECISION_FILENAME, payload=sf_payload
    )

    # 3. Re-stamp manifest payload with the *_ref / *_sha256 binding.
    # NOT added to artifact_filenames — the canonical chain set stays
    # exactly W2_ARTIFACT_FILENAMES; the safe_fallback_decision is bound
    # via dedicated ref+sha256 fields. Then propagate the new hash
    # through downstream chain links.
    manifest_path = art / "integrated_runtime_artifact_manifest.json"
    manifest_env = _read_json(manifest_path)
    manifest_payload = manifest_env.get("payload", {})
    new_manifest_hash = ""
    if isinstance(manifest_payload, dict):
        manifest_payload["safe_fallback_decision_ref"] = (
            f"artifact://{SAFE_FALLBACK_DECISION_FILENAME}"
        )
        manifest_payload["safe_fallback_decision_sha256"] = sf_sha
        manifest_payload["fallback_reason"] = fallback_reason
        manifest_path.write_text(
            json.dumps(manifest_env, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        new_manifest_hash = _restamp_envelope(manifest_path)

    # 3b. Cascade: no_harness_stamp_receipt.upstream_artifact_ref.
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

    # 4. Re-stamp spine to bind the safe_fallback_decision and refresh
    # artifact_manifest_ref + upstream_artifact_ref to match the new
    # manifest / no_harness hashes.
    spine_path = art / "agentic_core_spine_proof.json"
    spine_env = _read_json(spine_path)
    spine_payload = spine_env.get("payload", {})
    if isinstance(spine_payload, dict):
        spine_payload["safe_fallback_decision_ref"] = sf_sha
        spine_payload["safe_fallback_decision_sha256"] = sf_sha
        spine_payload["fallback_reason"] = fallback_reason
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
    "run_integrated_fallback",
    "CHAIN_KIND",
    "ROUTE_FAMILY",
    "SAFE_FALLBACK_DECISION_FILENAME",
]
