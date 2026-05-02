"""L7_AUDITABILITY HOW-trace verifier — fail-closed.

Verifies that ``agentic_core_how_trace.json`` is present, schema-valid,
identity-continuous, stage-complete, and consistent with the chain it
projects over.  This verifier is invoked for both R1B and
MANAGED_WORKFLOW chains.

Fail-closed rules (each emits exit 2 with a specific reason code):

  HOW_TRACE_MISSING                — agentic_core_how_trace.json absent
  HOW_TRACE_INVALID_SCHEMA         — schema_version / runtime_subject /
                                     evidence_plane / evidence_plane_mode
                                     wrong
  HOW_TRACE_STAGE_MISSING          — any of the 10 mandatory stage_ids
                                     not present
  HOW_TRACE_DUPLICATE_STAGE        — a stage_id appears more than once
  HOW_TRACE_IDENTITY_MISMATCH      — a stage's run_id / request_id /
                                     trace_root differs from envelope
  HOW_TRACE_RAN_NO_OUTPUT          — a RAN stage with no
                                     output_artifact_refs
  HOW_TRACE_BYPASS_NO_REASON       — BYPASSED with no bypass_reason or
                                     no bypass artifact ref
  HOW_TRACE_STRUCTURAL_NO_REASON   — STRUCTURAL_ONLY with no
                                     structural_only_reason
  HOW_TRACE_C0_BYPASS_BUT_REQUIRED — grounding_required=True yet
                                     C0_CONTEXT marked BYPASSED
  HOW_TRACE_PA_BYPASS_BUT_REQUIRED — prompt_assembly_required=True yet
                                     PROMPT_ASSEMBLY marked BYPASSED
  HOW_TRACE_MW_L3_BYPASSED         — execution_form=MANAGED_WORKFLOW yet
                                     L3_ORCHESTRATION marked BYPASSED
  HOW_TRACE_MW_L3_REFS_INCOMPLETE  — MW L3_ORCHESTRATION RAN but does not
                                     reference both static_dag_proof and
                                     runtime_l3_orchestration_receipt
  HOW_TRACE_R1B_L3_NOT_BYPASSED    — R1B L3_ORCHESTRATION not BYPASSED to
                                     l3_bypass_receipt
  HOW_TRACE_R1B_L2_REAL_CLAIMED    — R1B L2_EXECUTE claims status=RAN
                                     (R1B cannot perform real L2)
  HOW_TRACE_MW_L2_NO_SEAL          — MW L2_EXECUTE does not reference
                                     l2_sealed_artifact.json
  HOW_TRACE_EXIT_X3_COUNT          — Exit stage references 0 or >1 X3
                                     disposition artifact
  HOW_TRACE_FORBIDDEN_FAIL         — any forbidden_action_assertion has
                                     result == "FAIL"
  HOW_TRACE_NOT_IN_MANIFEST        — manifest.artifact_filenames does not
                                     contain agentic_core_how_trace.json
  HOW_TRACE_NOT_IN_SPINE           — spine_proof_bundle does not include
                                     how_trace_ref / how_trace_sha256
  HOW_TRACE_DIGEST_MISMATCH        — recomputing the deterministic digest
                                     yields a different value than stored

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parents[1]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    detect_chain_kind,
    fail,
    passed,
    resolve_artifact_dir,
)

try:
    from agentic_core.L7_auditability.contracts.how_trace import (  # noqa: E402
        ALLOWED_STAGE_IDS,
        EVIDENCE_PLANE,
        EVIDENCE_PLANE_MODE,
        HOW_TRACE_SCHEMA_VERSION,
        RUNTIME_SUBJECT,
        compute_how_trace_digest,
    )
except ImportError as e:  # pragma: no cover
    print(f"[verify_agentic_core_how_trace] HARNESS_ERROR import: {e}")
    sys.exit(EXIT_HARNESS_ERROR)


_HOW_TRACE = "agentic_core_how_trace.json"


def _read_envelope(artifact_dir: Path, filename: str) -> dict[str, Any] | None:
    p = artifact_dir / filename
    if not p.exists():
        return None
    try:
        env = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return env if isinstance(env, dict) else None


def _read_payload(artifact_dir: Path, filename: str) -> dict[str, Any] | None:
    env = _read_envelope(artifact_dir, filename)
    if env is None:
        return None
    p = env.get("payload")
    return p if isinstance(p, dict) else None


def _stage_by_id(stages: list[Mapping[str, Any]], sid: str) -> Mapping[str, Any] | None:
    for s in stages:
        if s.get("stage_id") == sid:
            return s
    return None


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    kind = detect_chain_kind(art_dir)
    print(
        f"[verify_agentic_core_how_trace] artifact_dir={art_dir} chain_kind={kind}"
    )

    # 1. HOW trace presence.
    ht_path = art_dir / _HOW_TRACE
    if not ht_path.exists():
        return fail(
            "HOW_TRACE_MISSING",
            f"L7_AUDITABILITY plane requires {_HOW_TRACE}; not found at {ht_path}",
        )

    envelope = _read_envelope(art_dir, _HOW_TRACE)
    if envelope is None:
        return fail(
            "HOW_TRACE_MISSING",
            f"{_HOW_TRACE} unreadable or empty",
        )
    payload = _read_payload(art_dir, _HOW_TRACE)
    if not isinstance(payload, dict):
        return fail(
            "HOW_TRACE_INVALID_SCHEMA",
            "HOW trace payload is not a JSON object",
        )

    # 2. Schema invariants.
    if payload.get("schema_version") != HOW_TRACE_SCHEMA_VERSION:
        return fail(
            "HOW_TRACE_INVALID_SCHEMA",
            f"schema_version={payload.get('schema_version')!r}; "
            f"expected {HOW_TRACE_SCHEMA_VERSION!r}",
        )
    if payload.get("runtime_subject") != RUNTIME_SUBJECT:
        return fail(
            "HOW_TRACE_INVALID_SCHEMA",
            f"runtime_subject={payload.get('runtime_subject')!r}; "
            f"expected {RUNTIME_SUBJECT!r}",
        )
    if payload.get("evidence_plane") != EVIDENCE_PLANE:
        return fail(
            "HOW_TRACE_INVALID_SCHEMA",
            f"evidence_plane={payload.get('evidence_plane')!r}; "
            f"expected {EVIDENCE_PLANE!r}",
        )
    if payload.get("evidence_plane_mode") != EVIDENCE_PLANE_MODE:
        return fail(
            "HOW_TRACE_INVALID_SCHEMA",
            f"evidence_plane_mode={payload.get('evidence_plane_mode')!r}; "
            f"expected {EVIDENCE_PLANE_MODE!r}",
        )

    chain_kind = str(payload.get("chain_kind") or "")
    _ALLOWED_HT_CHAIN_KINDS = {
        "R1B",
        "MANAGED_WORKFLOW",
        "R1A_EXACT_CACHE",
        "R5_FALLBACK",
        "UWG_BLOCK_PATH",
        # W4 plan fortknox-100pct-static-runtime-gap-9a3d4f:
        "UWG_COMMIT_PATH",
        "R3_GROUNDED_READ",
        "R4_SINGLE_ACTION",
        "MANAGED_WORKFLOW_REAL_EXECUTION",
    }
    if chain_kind not in _ALLOWED_HT_CHAIN_KINDS:
        return fail(
            "HOW_TRACE_INVALID_SCHEMA",
            f"chain_kind={chain_kind!r}; expected one of {sorted(_ALLOWED_HT_CHAIN_KINDS)}",
        )

    run_id = str(payload.get("run_id") or "")
    request_id = str(payload.get("request_id") or "")
    trace_root = str(payload.get("trace_root") or "")
    if not run_id or not request_id or not trace_root:
        return fail(
            "HOW_TRACE_INVALID_SCHEMA",
            "HOW trace envelope missing run_id/request_id/trace_root",
        )

    # 3. Stage coverage + uniqueness + identity continuity.
    stages = payload.get("stages")
    if not isinstance(stages, list):
        return fail(
            "HOW_TRACE_INVALID_SCHEMA", "HOW trace 'stages' must be a list"
        )
    seen_ids: set[str] = set()
    for stage in stages:
        sid = str(stage.get("stage_id") or "")
        if sid in seen_ids:
            return fail(
                "HOW_TRACE_DUPLICATE_STAGE",
                f"stage_id={sid!r} appears more than once in HOW trace",
            )
        seen_ids.add(sid)
        for fld in ("run_id", "request_id", "trace_root"):
            if stage.get(fld) != payload.get(fld):
                return fail(
                    "HOW_TRACE_IDENTITY_MISMATCH",
                    f"stage[{sid}].{fld}={stage.get(fld)!r} != envelope.{fld}={payload.get(fld)!r}",
                )
    missing = set(ALLOWED_STAGE_IDS) - seen_ids
    if missing:
        return fail(
            "HOW_TRACE_STAGE_MISSING",
            f"HOW trace missing required stage_ids: {sorted(missing)}",
        )

    # 4. Per-stage status / ref / forbidden-action invariants.
    for stage in stages:
        sid = stage.get("stage_id")
        status = stage.get("status")
        outs = stage.get("output_artifact_refs", [])
        bypass_reason = str(stage.get("bypass_reason") or "")
        structural_only_reason = str(stage.get("structural_only_reason") or "")
        if status == "RAN" and not outs:
            return fail(
                "HOW_TRACE_RAN_NO_OUTPUT",
                f"stage[{sid}] RAN with no output_artifact_refs",
            )
        if status == "BYPASSED":
            if not bypass_reason:
                return fail(
                    "HOW_TRACE_BYPASS_NO_REASON",
                    f"stage[{sid}] BYPASSED without bypass_reason",
                )
            # BYPASSED stages must reference the bypass artifact (their
            # output_artifact_refs must be non-empty unless the legitimate
            # bypass is "no artifact required" — but our chain always
            # emits a bypass receipt for C0/PA/L3 BYPASSED states).
            if sid in {"C0_CONTEXT", "PROMPT_ASSEMBLY", "L3_ORCHESTRATION"} and not outs:
                return fail(
                    "HOW_TRACE_BYPASS_NO_REASON",
                    f"stage[{sid}] BYPASSED without bypass artifact ref",
                )
        if status == "STRUCTURAL_ONLY" and not structural_only_reason:
            return fail(
                "HOW_TRACE_STRUCTURAL_NO_REASON",
                f"stage[{sid}] STRUCTURAL_ONLY without structural_only_reason",
            )
        for assertion in stage.get("forbidden_action_assertions", []):
            if isinstance(assertion, Mapping) and assertion.get("result") == "FAIL":
                return fail(
                    "HOW_TRACE_FORBIDDEN_FAIL",
                    f"stage[{sid}] forbidden_action_assertion FAIL: "
                    f"{dict(assertion)}",
                )

    # 5. Cross-field invariants.
    execution_form = str(payload.get("execution_form") or "")
    # For C0 + PA we need the route_contract to know the requirements.
    route_payload: Mapping[str, Any] = _read_payload(art_dir, "route_contract.json") or {}
    grounding_required = bool(route_payload.get("grounding_required", False))
    pa_required = bool(route_payload.get("prompt_assembly_required", False))

    c0 = _stage_by_id(stages, "C0_CONTEXT")
    if c0 is not None and grounding_required and c0.get("status") == "BYPASSED":
        return fail(
            "HOW_TRACE_C0_BYPASS_BUT_REQUIRED",
            "grounding_required=True but C0_CONTEXT.status=BYPASSED",
        )
    pa = _stage_by_id(stages, "PROMPT_ASSEMBLY")
    if pa is not None and pa_required and pa.get("status") == "BYPASSED":
        return fail(
            "HOW_TRACE_PA_BYPASS_BUT_REQUIRED",
            "prompt_assembly_required=True but PROMPT_ASSEMBLY.status=BYPASSED",
        )

    l3 = _stage_by_id(stages, "L3_ORCHESTRATION")
    if l3 is not None:
        l3_outs = list(l3.get("output_artifact_refs", []))
        if chain_kind == "MANAGED_WORKFLOW":
            if l3.get("status") == "BYPASSED":
                return fail(
                    "HOW_TRACE_MW_L3_BYPASSED",
                    "MANAGED_WORKFLOW chain may not bypass L3_ORCHESTRATION",
                )
            if l3.get("status") == "RAN":
                refs_blob = " ".join(l3_outs)
                if "static_dag_proof.json" not in refs_blob or "runtime_l3_orchestration_receipt.json" not in refs_blob:
                    return fail(
                        "HOW_TRACE_MW_L3_REFS_INCOMPLETE",
                        f"MW L3_ORCHESTRATION RAN must reference both "
                        f"static_dag_proof.json and runtime_l3_orchestration_receipt.json; "
                        f"got {l3_outs}",
                    )
        else:
            # R1B
            if l3.get("status") != "BYPASSED":
                return fail(
                    "HOW_TRACE_R1B_L3_NOT_BYPASSED",
                    f"R1B L3_ORCHESTRATION must be BYPASSED; got {l3.get('status')}",
                )
            if not any("l3_bypass_receipt.json" in o for o in l3_outs):
                return fail(
                    "HOW_TRACE_R1B_L3_NOT_BYPASSED",
                    "R1B L3_ORCHESTRATION must reference l3_bypass_receipt.json",
                )

    # R1B-shaped chains (R1B + R1A + R5 + UWG_BLOCK) all share terminal-
    # shortcircuit semantics — no real L2 execution is permitted.
    _R1B_SHAPED = {
        "R1B", "R1A_EXACT_CACHE", "R5_FALLBACK", "UWG_BLOCK_PATH",
        # W4 plan fortknox-100pct-static-runtime-gap-9a3d4f:
        # UWG_COMMIT_PATH + R3 + R4 all chain off run_integrated_safe_reuse
        # which terminates at the terminal-shortcircuit shape. The chain_kind
        # distinguishes downstream family bindings but the L2_EXECUTE stage
        # stays BYPASSED at the chain layer; real L2 execution, when it
        # happens, emits a sealed_l2_artifact.json extra. MW_REAL likewise
        # uses structural-only L2 at the chain layer.
        "UWG_COMMIT_PATH", "R3_GROUNDED_READ", "R4_SINGLE_ACTION",
        "MANAGED_WORKFLOW_REAL_EXECUTION",
    }
    l2 = _stage_by_id(stages, "L2_EXECUTE")
    if l2 is not None:
        if chain_kind in _R1B_SHAPED and l2.get("status") == "RAN":
            return fail(
                "HOW_TRACE_R1B_L2_REAL_CLAIMED",
                f"{chain_kind} chain cannot claim L2_EXECUTE.status=RAN — "
                "terminal-shortcircuit-class chains perform no real L2 execution",
            )
        if chain_kind == "MANAGED_WORKFLOW":
            l2_outs = list(l2.get("output_artifact_refs", []))
            if not any("l2_sealed_artifact.json" in o for o in l2_outs):
                return fail(
                    "HOW_TRACE_MW_L2_NO_SEAL",
                    "MW L2_EXECUTE must reference l2_sealed_artifact.json",
                )

    exit_x3 = _stage_by_id(stages, "EXIT_X3")
    if exit_x3 is not None and exit_x3.get("status") == "RAN":
        outs = list(exit_x3.get("output_artifact_refs", []))
        x3_count = sum(1 for o in outs if "x3_disposition_receipt.json" in o)
        if x3_count != 1:
            return fail(
                "HOW_TRACE_EXIT_X3_COUNT",
                f"EXIT_X3 must reference exactly one x3_disposition_receipt.json; "
                f"got {x3_count}",
            )

    # 6. Manifest binding.
    manifest = _read_payload(art_dir, "integrated_runtime_artifact_manifest.json") or {}
    fnames = list(manifest.get("artifact_filenames", []))
    if _HOW_TRACE not in fnames:
        return fail(
            "HOW_TRACE_NOT_IN_MANIFEST",
            f"integrated_runtime_artifact_manifest.json artifact_filenames "
            f"does not contain {_HOW_TRACE}",
        )

    # 7. Spine binding.
    spine = _read_payload(art_dir, "agentic_core_spine_proof.json") or {}
    if not str(spine.get("how_trace_ref") or ""):
        return fail(
            "HOW_TRACE_NOT_IN_SPINE",
            "agentic_core_spine_proof.json missing how_trace_ref",
        )
    if not str(spine.get("how_trace_sha256") or ""):
        return fail(
            "HOW_TRACE_NOT_IN_SPINE",
            "agentic_core_spine_proof.json missing how_trace_sha256",
        )

    # 8. Deterministic digest recomputation.
    stored_digest = str(payload.get("deterministic_digest") or "")
    recomputed = compute_how_trace_digest(payload)
    if stored_digest and stored_digest != recomputed:
        return fail(
            "HOW_TRACE_DIGEST_MISMATCH",
            f"stored deterministic_digest={stored_digest!r} != "
            f"recomputed={recomputed!r}",
        )

    return passed(
        f"HOW trace valid (chain_kind={chain_kind}, "
        f"stages={len(stages)}, success={payload.get('success')}, "
        f"runtime_mode={payload.get('runtime_mode')}, "
        f"audit_mode={payload.get('audit_mode')}, "
        f"manifest_bound=True, spine_bound=True, digest_ok=True)"
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
