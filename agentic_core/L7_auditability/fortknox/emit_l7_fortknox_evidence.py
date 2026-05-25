"""Fort Knox L7 evidence emitter — row-specific RTC-REQ projections.

Emits one Fort Knox-admissible evidence file per RTC-REQ row that L7 can
substantiate from the on-disk HOW trace and chain artifacts.  Each
evidence file is a typed, hash-bound, run-bound record that names:

    - the specific RTC requirement ID it satisfies
    - the claim type and control category
    - the artifact class (runtime, chain, gate, span, ...)
    - the command that produced the evidence
    - the approved verifier whose exit code is part of the proof
    - the source artifact that anchors the claim, by ref + sha256
    - the run identity (run_id / request_id / trace_root)
    - a deterministic digest over the evidence body

The verifier ``ops_scripts/ci/verify_l7_fortknox_evidence.py`` rejects:

    - linked_req_ids-only evidence (no row-specific assertion)
    - generic all_pass rollups
    - unapproved verifier commands
    - static-only artifacts repurposed as runtime claims
    - runtime claims without run_id/request_id/trace_root
    - OTEL claims without span payload fields
    - artifact-hash mismatch (recomputed != stored)
    - evidence pointer mismatch (file referenced but absent)

Output directory:
    artifacts/certification/integrated_runtime/<chain>/fortknox_l7_evidence/

Per-row file:
    RTC-REQ-<id>__l7_evidence.json

This module performs no routing, no retrieval, no orchestration, no
execution, no judgment, no L4 write.  It is a pure projection of HOW
trace + chain artifacts into Fort Knox-admissible row evidence.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

# RTC-REQ → stage_id mapping per the user's spec.
ROW_TO_STAGE: Mapping[str, str] = {
    "RTC-REQ-090": "U0_INTAKE",
    "RTC-REQ-091": "L1_PLAN",
    "RTC-REQ-092": "L0_ROUTE",
    "RTC-REQ-093": "C0_CONTEXT",
    "RTC-REQ-094": "PROMPT_ASSEMBLY",
    "RTC-REQ-095": "L2_EXECUTE",
    "RTC-REQ-096": "EXIT_X3",
    "RTC-REQ-097": "L6_RUNTIME_EXHAUST",
}

# Special rows that draw evidence from HOW-trace forbidden-action assertions
# rather than a single stage's RAN/BYPASSED status.
ROW_TO_FORBIDDEN_ASSERTION: Mapping[str, tuple[str, str, str]] = {
    # (stage_id, assertion_name, claim_subject)
    "RTC-REQ-070": ("L2_EXECUTE", "no_l4_write_from_l2",
                    "no_direct_durable_write_from_L2"),
    "RTC-REQ-071": ("L6_RUNTIME_EXHAUST", "no_l4_write_from_l6",
                    "no_direct_durable_write_from_L6"),
    "RTC-REQ-080": ("EXIT_X3", "unknown_never_pass",
                    "unknown_gate_verdict_never_treated_as_pass"),
}

# RTC-REQ-081: NOT_APPLICABLE requires reason — drawn from the UWG_L4 stage
# when status=NOT_APPLICABLE (mutation not requested).
ROW_RTC_REQ_081 = "RTC-REQ-081"
ROW_RTC_REQ_123 = "RTC-REQ-123"

APPROVED_VERIFIERS: frozenset[str] = frozenset({
    "ops_scripts.ci.verify_agentic_core_how_trace",
    "ops_scripts.ci.verify_integrated_runtime_artifact_chain",
    "ops_scripts.ci.verify_integrated_runtime_entrypoint",
    "ops_scripts.ci.verify_integrated_runtime_exit_x3",
    "ops_scripts.ci.verify_integrated_runtime_no_harness_stamp",
    "ops_scripts.ci.verify_l3_runtime_or_bypass",
    "ops_scripts.ci.verify_l3_static_dag_proof",
    "ops_scripts.ci.verify_c0_evidence_or_bypass",
    "ops_scripts.ci.verify_pa_artifact_or_bypass",
    "ops_scripts.ci.verify_l2_sealed_artifact",
    "ops_scripts.ci.verify_g01_g29_coverage",
    "ops_scripts.ci.verify_uwg_blocked_commit_receipts",
    "ops_scripts.ci.check_synthetic_trace_flag",
    "ops_scripts.ci.verify_spine_proof_bundle",
    "ops_scripts.ci.verify_integrated_runtime_manifest_exact_refs",
    "ops_scripts.ci.verify_l7_fortknox_evidence",
})


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_envelope(p: Path) -> Mapping[str, Any] | None:
    if not p.exists():
        return None
    try:
        env = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow -- P1 ADG burndown
        return None
    return env if isinstance(env, dict) else None


def _payload(env: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if env is None:
        return {}
    p = env.get("payload")
    return p if isinstance(p, Mapping) else {}


def _file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        blob = path.read_bytes()
    except OSError:
        return ""
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def _digest(payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k != "deterministic_digest"}
    blob = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return f"sha256:{hashlib.sha256(blob.encode('utf-8')).hexdigest()}"


def _stage(stages: list[Mapping[str, Any]], sid: str) -> Mapping[str, Any] | None:
    for s in stages:
        if s.get("stage_id") == sid:
            return s
    return None


def _row_evidence_for_stage(
    *,
    req_id: str,
    stage_id: str,
    stages: list[Mapping[str, Any]],
    how_trace_payload: Mapping[str, Any],
    artifact_dir: Path,
    chain_kind: str,
    approved_verifier: str,
    verifier_exit_code: int,
) -> dict[str, Any]:
    stage = _stage(stages, stage_id)
    if stage is None:
        raise ValueError(
            f"emit_l7_fortknox_evidence: stage {stage_id!r} missing from HOW trace"
        )
    out_refs = list(stage.get("output_artifact_refs", []))
    primary_artifact_filename = ""
    if out_refs:
        primary_artifact_filename = out_refs[0].replace("artifact://", "")
    primary_path = (
        artifact_dir / primary_artifact_filename if primary_artifact_filename else None
    )
    src_ref = (
        f"artifact://{primary_artifact_filename}"
        if primary_artifact_filename else ""
    )
    src_sha256 = _file_sha256(primary_path) if primary_path is not None else ""
    payload_ptr = (
        f"{artifact_dir.name}/{primary_artifact_filename}"
        if primary_artifact_filename else ""
    )
    artifact_payload_sha256 = src_sha256
    assertion_result = (
        "PASS" if stage.get("status") in {"RAN", "BYPASSED",
                                          "STRUCTURAL_ONLY",
                                          "NOT_APPLICABLE"}
        else "FAIL"
    )
    body: dict[str, Any] = {
        "schema_version": "1.0",
        "req_id": req_id,
        "claim_type": "runtime_stage_evidence",
        "control": f"L7_AUDITABILITY::stage::{stage_id}",
        "artifact_class": "runtime_chain_artifact",
        "generated_by_command": (
            "python -m agentic_core.L7_auditability.fortknox.emit_l7_fortknox_evidence "
            f"--artifact-dir {artifact_dir.as_posix()}"
        ),
        "approved_verifier": approved_verifier,
        "verifier_exit_code": int(verifier_exit_code),
        "assertion_result": assertion_result,
        "run_id": str(how_trace_payload.get("run_id") or ""),
        "request_id": str(how_trace_payload.get("request_id") or ""),
        "trace_root": str(how_trace_payload.get("trace_root") or ""),
        "source_artifact_ref": src_ref,
        "source_artifact_sha256": src_sha256,
        "evidence_payload_pointer": payload_ptr,
        "artifact_payload_sha256": artifact_payload_sha256,
        "last_verified_utc": _utc_now(),
        "chain_kind": chain_kind,
        "stage_id": stage_id,
        "stage_status": str(stage.get("status") or ""),
        "stage_why": str(stage.get("why_ran_or_bypassed") or ""),
        "forbidden_action_assertions": list(
            stage.get("forbidden_action_assertions", [])
        ),
    }
    body["deterministic_digest"] = _digest(body)
    return body


def _row_evidence_forbidden(
    *,
    req_id: str,
    stage_id: str,
    assertion_name: str,
    claim_subject: str,
    stages: list[Mapping[str, Any]],
    how_trace_payload: Mapping[str, Any],
    artifact_dir: Path,
    chain_kind: str,
    approved_verifier: str,
    verifier_exit_code: int,
) -> dict[str, Any]:
    stage = _stage(stages, stage_id)
    if stage is None:
        raise ValueError(
            f"emit_l7_fortknox_evidence: stage {stage_id!r} missing for {req_id}"
        )
    matching = [
        a for a in stage.get("forbidden_action_assertions", [])
        if isinstance(a, Mapping) and a.get("assertion") == assertion_name
    ]
    if not matching:
        raise ValueError(
            f"emit_l7_fortknox_evidence: stage[{stage_id}] has no "
            f"forbidden_action_assertion {assertion_name!r} for {req_id}"
        )
    result = str(matching[0].get("result") or "UNKNOWN")
    out_refs = list(stage.get("output_artifact_refs", []))
    primary = out_refs[0].replace("artifact://", "") if out_refs else ""
    primary_path = artifact_dir / primary if primary else None
    src_ref = f"artifact://{primary}" if primary else ""
    src_sha256 = _file_sha256(primary_path) if primary_path is not None else ""
    body: dict[str, Any] = {
        "schema_version": "1.0",
        "req_id": req_id,
        "claim_type": "runtime_forbidden_action_assertion",
        "control": f"L7_AUDITABILITY::forbidden::{claim_subject}",
        "artifact_class": "runtime_forbidden_action_assertion",
        "generated_by_command": (
            "python -m agentic_core.L7_auditability.fortknox.emit_l7_fortknox_evidence "
            f"--artifact-dir {artifact_dir.as_posix()}"
        ),
        "approved_verifier": approved_verifier,
        "verifier_exit_code": int(verifier_exit_code),
        "assertion_result": result,
        "run_id": str(how_trace_payload.get("run_id") or ""),
        "request_id": str(how_trace_payload.get("request_id") or ""),
        "trace_root": str(how_trace_payload.get("trace_root") or ""),
        "source_artifact_ref": src_ref,
        "source_artifact_sha256": src_sha256,
        "evidence_payload_pointer": (
            f"{artifact_dir.name}/{primary}" if primary else ""
        ),
        "artifact_payload_sha256": src_sha256,
        "last_verified_utc": _utc_now(),
        "chain_kind": chain_kind,
        "stage_id": stage_id,
        "asserted_subject": claim_subject,
        "asserted_result": result,
    }
    body["deterministic_digest"] = _digest(body)
    return body


def _row_evidence_na_reason(
    *,
    stages: list[Mapping[str, Any]],
    how_trace_payload: Mapping[str, Any],
    artifact_dir: Path,
    chain_kind: str,
    approved_verifier: str,
    verifier_exit_code: int,
) -> dict[str, Any]:
    """RTC-REQ-081: NOT_APPLICABLE requires reason. We sample UWG_L4."""
    stage = _stage(stages, "UWG_L4")
    if stage is None:
        raise ValueError(
            "emit_l7_fortknox_evidence: UWG_L4 stage missing for RTC-REQ-081"
        )
    status = str(stage.get("status") or "")
    why = str(stage.get("why_ran_or_bypassed") or "")
    result = "PASS" if (status != "NOT_APPLICABLE" or why) else "FAIL"
    body: dict[str, Any] = {
        "schema_version": "1.0",
        "req_id": ROW_RTC_REQ_081,
        "claim_type": "runtime_not_applicable_reason",
        "control": "L7_AUDITABILITY::na_reason::UWG_L4",
        "artifact_class": "runtime_stage_na_assertion",
        "generated_by_command": (
            "python -m agentic_core.L7_auditability.fortknox.emit_l7_fortknox_evidence "
            f"--artifact-dir {artifact_dir.as_posix()}"
        ),
        "approved_verifier": approved_verifier,
        "verifier_exit_code": int(verifier_exit_code),
        "assertion_result": result,
        "run_id": str(how_trace_payload.get("run_id") or ""),
        "request_id": str(how_trace_payload.get("request_id") or ""),
        "trace_root": str(how_trace_payload.get("trace_root") or ""),
        "source_artifact_ref": "artifact://agentic_core_how_trace.json",
        "source_artifact_sha256": _file_sha256(
            artifact_dir / "agentic_core_how_trace.json"
        ),
        "evidence_payload_pointer": f"{artifact_dir.name}/agentic_core_how_trace.json",
        "artifact_payload_sha256": _file_sha256(
            artifact_dir / "agentic_core_how_trace.json"
        ),
        "last_verified_utc": _utc_now(),
        "chain_kind": chain_kind,
        "stage_id": "UWG_L4",
        "stage_status": status,
        "stage_why": why,
    }
    body["deterministic_digest"] = _digest(body)
    return body


def _row_evidence_payload_hash(
    *,
    artifact_dir: Path,
    how_trace_payload: Mapping[str, Any],
    chain_kind: str,
    approved_verifier: str,
    verifier_exit_code: int,
) -> dict[str, Any]:
    """RTC-REQ-123: artifact payload content-hash validation.

    Recomputes the canonical-JSON hash of the HOW trace payload and
    compares to the stored deterministic_digest.  Result PASS only if
    the recomputed digest matches.
    """
    stored = str(how_trace_payload.get("deterministic_digest") or "")
    recomputed = _digest(how_trace_payload)
    result = "PASS" if stored and stored == recomputed else "FAIL"
    body: dict[str, Any] = {
        "schema_version": "1.0",
        "req_id": ROW_RTC_REQ_123,
        "claim_type": "artifact_payload_hash_validation",
        "control": "L7_AUDITABILITY::payload_hash::HOW_TRACE",
        "artifact_class": "runtime_artifact_hash",
        "generated_by_command": (
            "python -m agentic_core.L7_auditability.fortknox.emit_l7_fortknox_evidence "
            f"--artifact-dir {artifact_dir.as_posix()}"
        ),
        "approved_verifier": approved_verifier,
        "verifier_exit_code": int(verifier_exit_code),
        "assertion_result": result,
        "run_id": str(how_trace_payload.get("run_id") or ""),
        "request_id": str(how_trace_payload.get("request_id") or ""),
        "trace_root": str(how_trace_payload.get("trace_root") or ""),
        "source_artifact_ref": "artifact://agentic_core_how_trace.json",
        "source_artifact_sha256": _file_sha256(
            artifact_dir / "agentic_core_how_trace.json"
        ),
        "evidence_payload_pointer": f"{artifact_dir.name}/agentic_core_how_trace.json",
        "artifact_payload_sha256": _file_sha256(
            artifact_dir / "agentic_core_how_trace.json"
        ),
        "last_verified_utc": _utc_now(),
        "chain_kind": chain_kind,
        "stored_deterministic_digest": stored,
        "recomputed_deterministic_digest": recomputed,
    }
    body["deterministic_digest"] = _digest(body)
    return body


def emit_l7_fortknox_evidence(
    artifact_dir: Path,
    *,
    approved_verifier: str = "ops_scripts.ci.verify_agentic_core_how_trace",
    verifier_exit_code: int = 0,
) -> tuple[Path, list[Path]]:
    """Emit one Fort Knox L7 evidence file per RTC-REQ.

    Returns the output directory and the list of files written.
    Raises ValueError on any structural inconsistency in the HOW trace.
    """
    if approved_verifier not in APPROVED_VERIFIERS:
        raise ValueError(
            f"emit_l7_fortknox_evidence: approved_verifier "
            f"{approved_verifier!r} not in approved set"
        )

    ht_env = _read_envelope(artifact_dir / "agentic_core_how_trace.json")
    if ht_env is None:
        raise ValueError(
            "emit_l7_fortknox_evidence: agentic_core_how_trace.json not found "
            f"in {artifact_dir}"
        )
    ht_payload = _payload(ht_env)
    stages = list(ht_payload.get("stages", []))
    chain_kind = str(ht_payload.get("chain_kind") or "")
    _ALLOWED_CHAIN_KINDS = {
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
    if not stages or chain_kind not in _ALLOWED_CHAIN_KINDS:
        raise ValueError(
            "emit_l7_fortknox_evidence: HOW trace malformed (no stages or "
            f"unknown chain_kind={chain_kind!r})"
        )

    out_dir = artifact_dir / "fortknox_l7_evidence"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    # Stage rows.
    for req_id, stage_id in ROW_TO_STAGE.items():
        body = _row_evidence_for_stage(
            req_id=req_id,
            stage_id=stage_id,
            stages=stages,
            how_trace_payload=ht_payload,
            artifact_dir=artifact_dir,
            chain_kind=chain_kind,
            approved_verifier=approved_verifier,
            verifier_exit_code=verifier_exit_code,
        )
        out = out_dir / f"{req_id}__l7_evidence.json"
        out.write_text(
            json.dumps(body, indent=2, sort_keys=True, default=str),
            encoding="utf-8",
        )
        written.append(out)

    # Forbidden-action rows (RTC-REQ-070, 071, 080).
    for req_id, (stage_id, assertion_name, claim_subject) in ROW_TO_FORBIDDEN_ASSERTION.items():
        body = _row_evidence_forbidden(
            req_id=req_id,
            stage_id=stage_id,
            assertion_name=assertion_name,
            claim_subject=claim_subject,
            stages=stages,
            how_trace_payload=ht_payload,
            artifact_dir=artifact_dir,
            chain_kind=chain_kind,
            approved_verifier=approved_verifier,
            verifier_exit_code=verifier_exit_code,
        )
        out = out_dir / f"{req_id}__l7_evidence.json"
        out.write_text(
            json.dumps(body, indent=2, sort_keys=True, default=str),
            encoding="utf-8",
        )
        written.append(out)

    # RTC-REQ-081: NA reason.
    body = _row_evidence_na_reason(
        stages=stages,
        how_trace_payload=ht_payload,
        artifact_dir=artifact_dir,
        chain_kind=chain_kind,
        approved_verifier=approved_verifier,
        verifier_exit_code=verifier_exit_code,
    )
    out = out_dir / f"{ROW_RTC_REQ_081}__l7_evidence.json"
    out.write_text(
        json.dumps(body, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    written.append(out)

    # RTC-REQ-123: payload hash.
    body = _row_evidence_payload_hash(
        artifact_dir=artifact_dir,
        how_trace_payload=ht_payload,
        chain_kind=chain_kind,
        approved_verifier=approved_verifier,
        verifier_exit_code=verifier_exit_code,
    )
    out = out_dir / f"{ROW_RTC_REQ_123}__l7_evidence.json"
    out.write_text(
        json.dumps(body, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    written.append(out)

    return out_dir, written


def main(argv: list[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Emit L7 Fort Knox evidence")
    p.add_argument(
        "--artifact-dir",
        required=False,
        default="artifacts/certification/integrated_runtime/latest",
        help="Path to integrated-runtime artifact directory.",
    )
    p.add_argument(
        "--verifier",
        required=False,
        default="ops_scripts.ci.verify_agentic_core_how_trace",
        help="Approved verifier whose exit code anchors the proof.",
    )
    p.add_argument(
        "--exit-code", type=int, default=0,
        help="Exit code observed from the approved verifier (proof anchor).",
    )
    args = p.parse_args(argv[1:])
    art_dir = Path(args.artifact_dir).resolve()
    out_dir, written = emit_l7_fortknox_evidence(
        art_dir,
        approved_verifier=args.verifier,
        verifier_exit_code=args.exit_code,
    )
    print(
        f"[emit_l7_fortknox_evidence] artifact_dir={art_dir} "
        f"out_dir={out_dir} files={len(written)}"
    )
    for f in written:
        print(f"  {f.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))


__all__ = [
    "APPROVED_VERIFIERS",
    "ROW_TO_FORBIDDEN_ASSERTION",
    "ROW_TO_STAGE",
    "emit_l7_fortknox_evidence",
]
