"""Shared pre-provider block artifacts for section lanes with missing upstream evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
)
from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run
from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

BLOCKED_STATUS = "REQUIRED_PROOF_ABSENT"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _blocked_exceptions() -> tuple[type[BaseException], ...]:
    from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError
    from apps_rg.runtime.spine.c0_fec_compose import SectionFecBridgePreconditionError
    from apps_rg.runtime.spine.section_c0_retrieve import StopAsEvidenceGapError

    return (
        C0EvidenceGapError,
        SectionFecBridgePreconditionError,
        StopAsEvidenceGapError,
    )


def write_required_proof_absent_artifacts(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    provider: str,
    temperature: float,
    max_tokens: int,
    runtime_payload: dict[str, Any],
    reason: str,
    output_filename: str = "",
) -> dict[str, Any]:
    """Write a non-certifying lane bundle when upstream C0/FEC proof is absent."""
    sid = str(section_id)
    provider_name = str(provider or "")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    runtime_payload["runtime_generation_status"] = BLOCKED_STATUS
    runtime_payload["blocked_before_provider"] = True
    runtime_payload["upstream_evidence_gap_reason"] = reason

    x2 = [
        {
            "gate_id": f"x2_{sid}_required_proof_present",
            "pass": False,
            "severity": "block",
            "reason": reason,
        }
    ]
    x3 = {
        "x3_code": "X3_BLOCK",
        "pass": False,
        "pass_": False,
        "runtime_generation_status": BLOCKED_STATUS,
        "product_quality_status": "FAIL",
        "decisive_reason": reason,
        "authorization_scope": "PLUMBING_ONLY",
        "required_remediation": [reason],
    }
    l2 = {
        "run_id": str(runtime_payload.get("run_id") or ""),
        "section_id": sid,
        "runtime_generation_status": BLOCKED_STATUS,
        "product_quality_status": "FAIL",
        "product_quality_reason": reason,
        "claim_ledger": [],
        "selected_fact_plan": runtime_payload.get("selected_fact_plan") or {},
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "self_check": {"blocked_reason": reason},
    }
    provider_req = {
        "provider_requested": provider_name,
        "provider_attempted": False,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "mock_fallback_allowed": False,
        "blocked_before_provider": True,
    }
    provider_resp = {
        "provider_requested": provider_name,
        "provider_attempted": False,
        "provider_available": False,
        "runtime_generation_status": BLOCKED_STATUS,
        "exact_provider_error": reason,
    }
    output_text = f"{sid}: {BLOCKED_STATUS}: {reason}"

    _write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    _write_json(artifact_dir / "provider_request.json", provider_req)
    _write_json(artifact_dir / "provider_response.json", provider_resp)
    _write_json(artifact_dir / "real_l2_generation_result.json", provider_resp)
    _write_json(artifact_dir / "l2_output.json", l2)
    _write_json(artifact_dir / "parsed_output.json", {"parsed": None, "parse_error": reason})
    _write_json(artifact_dir / "claim_ledger.json", [])
    _write_json(
        artifact_dir / "canonical_claim_ledger_v2.json",
        build_canonical_claim_ledger_v2_payload([], parse_status="BLOCKED", invalid_reason=reason),
    )
    _write_json(artifact_dir / "text_claim_coverage.json", {"status": "BLOCKED", "reason": reason})
    _write_json(
        artifact_dir / "x2_gate_outputs.json",
        {"gates": x2, "x2_failed": 1, "x2_passed": 0, "failed_gates": [x2[0]["gate_id"]]},
    )
    _write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": []})
    # Single-spine authority (E2E-14): route the x3 mirror through the spine finalize helper
    # rather than writing x3_disposition.json raw. This is a pre-provider proof-absent block with
    # no sealed L2, so exit receipts are skipped (default); the spine still owns the mirror.
    finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id=sid,
        runtime_payload=runtime_payload,
        x3_result=x3,
    )
    _write_json(
        artifact_dir / "l6_shadow_eval_package.json",
        {"section_id": sid, "status": "BLOCKED", "reason": reason},
    )
    _write_json(
        artifact_dir / "section_metric_receipt.json",
        {"lane_id": sid, "runtime_generation_status": BLOCKED_STATUS, "x3_code": "X3_BLOCK"},
    )
    _write_json(
        artifact_dir / "upstream_evidence_gap.json",
        {
            "schema_version": "upstream_evidence_gap_v1",
            "section_id": sid,
            "runtime_generation_status": BLOCKED_STATUS,
            "reason": reason,
            "provider_attempted": False,
        },
    )
    if output_filename:
        (artifact_dir / output_filename).write_text("", encoding="utf-8")
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")

    finalize_runtime_proof_run(
        repo_root,
        sid,
        provider_name,
        artifact_dir,
        run_id=str(runtime_payload.get("run_id") or ""),
        section_id=sid,
        runtime_generation_status=BLOCKED_STATUS,
        provider_requested=provider_name,
        provider_attempted=False,
    )
    return {
        "artifact_dir": str(artifact_dir),
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": output_text,
    }


def wire_spine_c0_fec_or_block(
    *,
    repo_root: Path,
    artifact_dir: Path,
    section_id: str,
    front_spine: Any,
    pool: Any,
    runtime_payload: dict[str, Any],
    provider: str,
    temperature: float,
    max_tokens: int,
    output_filename: str = "",
) -> dict[str, Any] | None:
    """Run FEC compose, or return a blocked lane context for upstream evidence gaps."""
    from apps_rg.runtime.spine.c0_fec_compose import wire_spine_c0_fec_for_section

    try:
        wire_spine_c0_fec_for_section(
            artifact_dir=artifact_dir,
            section_id=section_id,
            front_spine=front_spine,
            pool=pool,
            runtime_payload=runtime_payload,
        )
    except _blocked_exceptions() as exc:
        return write_required_proof_absent_artifacts(
            repo_root=repo_root,
            artifact_dir=artifact_dir,
            section_id=section_id,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            runtime_payload=runtime_payload,
            reason=f"required upstream proof absent for {section_id}: {exc}",
            output_filename=output_filename,
        )
    return None


__all__ = [
    "BLOCKED_STATUS",
    "wire_spine_c0_fec_or_block",
    "write_required_proof_absent_artifacts",
]
