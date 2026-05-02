"""Spine verifier — agentic_core_spine_proof.json is well-formed.

Asserts:
  1. agentic_core_spine_proof.json exists and is a valid envelope.
  2. proof_schema_version + harness_schema_version + runtime_subject
     are populated.
  3. run_id, request_id, trace_root are non-empty and identical to the
     RuntimeIdentityEnvelope.
  4. Every non-null ``runtime_*_ref`` / ``artifact_manifest_ref`` /
     ``runtime_exhaust_ref`` points to a file that exists in the run
     directory AND whose envelope ``artifact_hash`` matches the ref.
  5. R1B-specific shape:
       - runtime_l3_receipt_ref is null
       - runtime_l3_bypass_ref is non-null
       - runtime_c0_receipt_ref is non-null (points to C0 BYPASS)
       - runtime_prompt_assembly_ref is non-null (points to PA BYPASS)
       - runtime_exhaust_ref is non-null
       - artifact_manifest_ref is non-null
  6. ``managed_workflow_certified`` is False (this pass does not certify
     MANAGED_WORKFLOW).
  7. Detection-flag invariants:
       - synthetic_trace_detected=True with runtime_mode=production → fail
       - mock_mode_detected=True with runtime_mode=production → fail
       - fixture_mode_detected=True with runtime_mode=production → fail
  8. ``success`` agrees with ``blocking_gaps`` emptiness.

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import json
import sys

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    fail,
    load_envelope,
    load_payload,
    passed,
    resolve_artifact_dir,
)

# Filenames whose artifact_hash should be discoverable from the run dir
# when the corresponding ref in the bundle is non-null. The mapping is
# bundle_field -> filename(s) that could carry that hash.
_REF_TO_FILE: dict[str, tuple[str, ...]] = {
    "runtime_identity_ref": ("runtime_identity_envelope.json",),
    "runtime_intake_ref": ("validated_request.json",),
    "runtime_l1_plan_ref": ("l1_plan_contract.json",),
    "runtime_route_contract_ref": ("route_contract.json",),
    "runtime_l3_bypass_ref": ("l3_bypass_receipt.json",),
    "runtime_l3_receipt_ref": ("runtime_l3_orchestration_receipt.json",),
    "static_dag_ref": ("static_dag_proof.json",),
    "runtime_c0_receipt_ref": (
        "c0_bypass_receipt.json",
        "final_evidence_contract.json",
    ),
    "runtime_prompt_assembly_ref": (
        "prompt_assembly_bypass_receipt.json",
        "compiled_prompt_artifact.json",
    ),
    "runtime_exit_disposition_ref": ("x3_disposition_receipt.json",),
    "runtime_exhaust_ref": ("runtime_exhaust_bundle.json",),
    "uwg_commit_or_block_ref": (
        "uwg_blocked_commit_receipt.json",
        "blocked_commit_receipt.json",
        "uwg_commit_receipt.json",
    ),
    "otel_or_runtime_trace_ref": ("runtime_trace_snapshot.json",),
    "runtime_l2_artifact_ref": ("l2_sealed_artifact.json",),
    "artifact_manifest_ref": ("integrated_runtime_artifact_manifest.json",),
}


def _resolve_ref_hash(art_dir, candidate_files: tuple[str, ...]) -> str | None:
    for fn in candidate_files:
        p = art_dir / fn
        if not p.exists():
            continue
        try:
            env = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        h = env.get("artifact_hash") if isinstance(env, dict) else None
        if isinstance(h, str) and h:
            return h
    return None


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_spine_proof_bundle] artifact_dir={art_dir}")

    # 1: bundle exists and is a well-formed envelope.
    try:
        envelope = load_envelope(art_dir, "agentic_core_spine_proof.json")
    except FileNotFoundError as exc:
        return fail("SPINE_PROOF_MISSING", str(exc))
    bundle = envelope.get("payload", {}) or {}
    if not isinstance(bundle, dict):
        return fail("SPINE_PROOF_PAYLOAD_INVALID", "payload is not a dict")

    # 2: schema fields.
    for key in ("proof_schema_version", "harness_schema_version", "runtime_subject"):
        if not bundle.get(key):
            return fail("SPINE_PROOF_SCHEMA_FIELD_MISSING", f"missing {key}")
    if bundle.get("runtime_subject") != "agentic_core":
        return fail(
            "SPINE_PROOF_RUNTIME_SUBJECT_INVALID",
            f"runtime_subject={bundle.get('runtime_subject')!r}; must be 'agentic_core'",
        )

    # 3: identity continuity vs RuntimeIdentityEnvelope.
    try:
        identity = load_payload(art_dir, "runtime_identity_envelope.json")
    except FileNotFoundError as exc:
        return fail("RUNTIME_IDENTITY_ENVELOPE_MISSING", str(exc))
    for key in ("run_id", "request_id", "trace_root"):
        if not bundle.get(key):
            return fail("SPINE_PROOF_IDENTITY_FIELD_MISSING", f"missing {key}")
        if bundle.get(key) != identity.get(key):
            return fail(
                "SPINE_PROOF_IDENTITY_DIVERGENCE",
                f"{key}: spine={bundle.get(key)!r} != identity={identity.get(key)!r}",
            )
    # Git state continuity: identity and bundle MUST agree.
    if bundle.get("git_commit") != identity.get("git_commit"):
        return fail(
            "SPINE_PROOF_GIT_COMMIT_DIVERGENCE",
            f"spine.git_commit={bundle.get('git_commit')!r} != "
            f"identity.git_commit={identity.get('git_commit')!r}",
        )
    if bool(bundle.get("git_dirty")) != bool(identity.get("git_dirty")):
        return fail(
            "SPINE_PROOF_GIT_DIRTY_DIVERGENCE",
            f"spine.git_dirty={bundle.get('git_dirty')!r} != "
            f"identity.git_dirty={identity.get('git_dirty')!r}",
        )

    # 4: every non-null ref must resolve to an on-disk hash.
    for field, candidates in _REF_TO_FILE.items():
        ref_value = bundle.get(field)
        if ref_value is None or ref_value == "":
            continue  # null is allowed; per-field checks below enforce shape
        found = _resolve_ref_hash(art_dir, candidates)
        if found is None:
            return fail(
                "SPINE_PROOF_REF_TARGET_MISSING",
                f"{field}={ref_value!r} but none of {list(candidates)} exists in run dir",
            )
        if ref_value != found:
            return fail(
                "SPINE_PROOF_REF_HASH_MISMATCH",
                f"{field}={ref_value!r} != on_disk_hash={found!r} "
                f"(searched {list(candidates)})",
            )

    # 5: chain-kind-specific shape.
    chain_kind = str(bundle.get("chain_kind", "R1B"))
    if chain_kind == "MANAGED_WORKFLOW":
        # MW path: runtime L3 receipt is REQUIRED, bypass is null,
        # static DAG ref + sha256 are REQUIRED, AND the ref's target's
        # dag_sha256 must match bundle.static_dag_sha256 for hash binding.
        if bundle.get("runtime_l3_bypass_ref") not in (None, ""):
            return fail(
                "SPINE_PROOF_L3_BYPASS_NOT_NULL_ON_MW",
                "MANAGED_WORKFLOW requires runtime_l3_bypass_ref=null; "
                f"got {bundle.get('runtime_l3_bypass_ref')!r}",
            )
        for required in (
            "runtime_l3_receipt_ref",
            "runtime_l2_artifact_ref",
            "runtime_c0_receipt_ref",
            "runtime_prompt_assembly_ref",
            "runtime_exhaust_ref",
            "artifact_manifest_ref",
            "static_dag_ref",
        ):
            if not bundle.get(required):
                return fail(
                    "SPINE_PROOF_REQUIRED_REF_NULL",
                    f"MANAGED_WORKFLOW requires {required} to be non-null",
                )
        if not bundle.get("static_dag_sha256"):
            return fail(
                "SPINE_PROOF_STATIC_DAG_SHA_MISSING",
                "MANAGED_WORKFLOW requires static_dag_sha256 to be non-empty",
            )
        # Hash-binding: runtime L3 receipt's dag_sha256 MUST equal bundle.static_dag_sha256.
        try:
            l3r = load_payload(art_dir, "runtime_l3_orchestration_receipt.json")
            sdp = load_payload(art_dir, "static_dag_proof.json")
        except FileNotFoundError as exc:
            return fail("MW_ARTIFACT_MISSING", str(exc))
        if l3r.get("dag_sha256") != sdp.get("dag_sha256"):
            return fail(
                "MW_DAG_SHA_DIVERGENCE",
                f"runtime_l3.dag_sha256={l3r.get('dag_sha256')!r} != "
                f"static_dag.dag_sha256={sdp.get('dag_sha256')!r}",
            )
        if bundle.get("static_dag_sha256") != sdp.get("dag_sha256"):
            return fail(
                "MW_BUNDLE_STATIC_DAG_SHA_DIVERGENCE",
                f"bundle.static_dag_sha256={bundle.get('static_dag_sha256')!r} != "
                f"static_dag.dag_sha256={sdp.get('dag_sha256')!r}",
            )
    else:
        # R1B path: runtime L3 receipt must be null, bypass REQUIRED.
        if bundle.get("runtime_l3_receipt_ref") not in (None, ""):
            return fail(
                "SPINE_PROOF_L3_RECEIPT_NOT_NULL",
                "R1B path requires runtime_l3_receipt_ref to be null; "
                f"got {bundle.get('runtime_l3_receipt_ref')!r}",
            )
        for required in (
            "runtime_l3_bypass_ref",
            "runtime_c0_receipt_ref",
            "runtime_prompt_assembly_ref",
            "runtime_exhaust_ref",
            "artifact_manifest_ref",
        ):
            if not bundle.get(required):
                return fail(
                    "SPINE_PROOF_REQUIRED_REF_NULL",
                    f"R1B path requires {required} to be non-null",
                )

    # 5b: otel_or_runtime_trace_ref is required on BOTH chains.
    if not bundle.get("otel_or_runtime_trace_ref"):
        return fail(
            "SPINE_PROOF_OTEL_TRACE_REF_NULL",
            "otel_or_runtime_trace_ref must point to runtime_trace_snapshot.json",
        )

    # 6: managed-workflow honesty.
    # The MW_STRUCTURAL path (chain_kind=MANAGED_WORKFLOW) must keep
    # managed_workflow_certified=False — it is structural-only and may not
    # claim certification. The MW_REAL path (chain_kind=
    # MANAGED_WORKFLOW_REAL_EXECUTION, plan fortknox-100pct-static-runtime-
    # gap-9a3d4f §GAP-6d) is the designed home for the True verdict; it
    # composes R3 + R4 + UWG_COMMIT substrates under a real 29-gate
    # evaluation and may honestly set the flag.
    mw_cert = bundle.get("managed_workflow_certified")
    chain_kind = str(bundle.get("chain_kind", ""))
    if chain_kind == "MANAGED_WORKFLOW_REAL_EXECUTION":
        if mw_cert is not True:
            return fail(
                "SPINE_PROOF_MW_REAL_NOT_CERTIFIED",
                f"MW_REAL chain has managed_workflow_certified={mw_cert!r}; "
                f"expected True",
            )
    else:
        if mw_cert is not False:
            return fail(
                "SPINE_PROOF_MANAGED_WORKFLOW_OVERCLAIM",
                f"managed_workflow_certified={mw_cert!r}; "
                f"must be False for chain_kind={chain_kind!r} until MW_REAL "
                f"substrate is exercised",
            )

    # 7: detection-flag invariants.
    runtime_mode = str(bundle.get("runtime_mode", ""))
    if runtime_mode == "production":
        for flag in ("synthetic_trace_detected", "mock_mode_detected", "fixture_mode_detected"):
            if bool(bundle.get(flag, False)):
                return fail(
                    "SPINE_PROOF_DEV_FLAG_IN_PRODUCTION",
                    f"{flag}=True with runtime_mode=production is forbidden",
                )

    # 8: success agrees with blocking_gaps.
    blocking_gaps = bundle.get("blocking_gaps")
    if not isinstance(blocking_gaps, list):
        return fail("SPINE_PROOF_BLOCKING_GAPS_INVALID",
                    "blocking_gaps must be a list")
    success = bool(bundle.get("success", False))
    if success and blocking_gaps:
        return fail(
            "SPINE_PROOF_SUCCESS_BUT_BLOCKING_GAPS",
            f"success=True but blocking_gaps={blocking_gaps[:5]}",
        )
    if (not success) and not blocking_gaps and int(bundle.get("exit_code", 0)) == 0:
        return fail(
            "SPINE_PROOF_SUCCESS_FALSE_WITHOUT_REASON",
            "success=False with empty blocking_gaps and exit_code=0",
        )

    return passed(
        f"runtime_subject={bundle.get('runtime_subject')}, "
        f"spine_status={bundle.get('agentic_core_spine_status')}, "
        f"runtime_mode={runtime_mode}, blocking_gaps={len(blocking_gaps)}"
    )


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
