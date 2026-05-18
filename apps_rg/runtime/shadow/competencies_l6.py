"""L6 shadow handoff for competencies — post-runtime boundary only.

Consumes completed lane artifacts (runtime exhaust). Never mutates the current run,
never contributes to runtime ALLOW, never promotes schema/rubric changes without UWG.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from apps_rg.runtime.shadow.l6_handoff_packet import (
    build_l6_shadow_handoff_dict,
    repo_rel,
    summarize_x2,
)
from apps_rg.runtime.validators.competencies_proof_markers import scan_mock_fixture_markers

SECTION_ID = "competencies"

_REAL_LLM_MOCK_SLICE_OPS = frozenset({"mocked_runtime_slice"})

OBSERVER_LAW_TEXT = (
    "L6 shadow learning observes completed-runtime exhaust only. "
    "No mutation, rescue, healing, or ALLOW contribution for the current run."
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _repair_summary(
    change_log: list[Any],
    *,
    runtime_generation_status: str,
) -> dict[str, Any]:
    """Split normal dispatcher repairs vs REAL_LLM proof anomalies (mock-slice leakage)."""
    ops_norm: Counter[str] = Counter()
    ops_anomaly: Counter[str] = Counter()
    for row in change_log or []:
        if isinstance(row, dict):
            op = str(row.get("operation") or "").strip()
            if not op:
                continue
            if op in _REAL_LLM_MOCK_SLICE_OPS and runtime_generation_status == "REAL_LLM":
                ops_anomaly[op] += 1
            else:
                ops_norm[op] += 1
    return {
        "operation_counts": dict(ops_norm),
        "anomaly_operation_counts": dict(ops_anomaly),
        "entries": len(change_log or []),
    }


def _mock_fixture_marker_summary(
    *,
    runtime_generation_status: str,
    l2: dict[str, Any],
    artifact_dir: Path,
) -> dict[str, Any]:
    hits: list[str] = []
    if runtime_generation_status == "REAL_LLM":
        blobs: list[str] = []
        for gn in l2.get("gap_notes") or []:
            blobs.append(str(gn))
        try:
            blobs.append(json.dumps(l2.get("change_log") or [], sort_keys=True))
        except (TypeError, ValueError):
            blobs.append(str(l2.get("change_log")))
        pr = artifact_dir / "provider_response.json"
        if pr.is_file():
            try:
                pdata = json.loads(pr.read_text(encoding="utf-8"))
                blobs.append(str(pdata.get("raw_model_output") or ""))
            except (OSError, json.JSONDecodeError, TypeError):
                pass
        hits = scan_mock_fixture_markers("\n".join(blobs))
    classification = "n/a_not_real_llm"
    if runtime_generation_status == "REAL_LLM":
        classification = "proof_quality_defect" if hits else "clean"
    return {
        "present": bool(hits),
        "markers_observed": hits,
        "classification": classification,
    }


def _proof_violation_counts(l2: dict[str, Any], x2_failed_ids: set[str]) -> tuple[int, int, int]:
    jd_al = l2.get("jd_alignment") if isinstance(l2.get("jd_alignment"), dict) else {}
    jd_pf = 0
    if jd_al.get("jd_used_as_proof") is True:
        jd_pf += 1
    if "x2_no_jd_only_skills" in x2_failed_ids:
        jd_pf += 1

    br_pf = 0
    if jd_al.get("briefing_used_as_proof") is True:
        br_pf += 1
    if "x2_no_briefing_only_skills" in x2_failed_ids:
        br_pf += 1

    cc_pf = 0
    if jd_al.get("companion_context_used_as_proof") is True:
        cc_pf += 1
    if "x2_competency_companion_context_not_proof" in x2_failed_ids:
        cc_pf += 1

    return jd_pf, br_pf, cc_pf


def build_competencies_shadow_learning(
    *,
    artifact_dir: Path,
    repo_root: Path,
    base_packet: dict[str, Any],
) -> dict[str, Any]:
    """Structured post-boundary learning surface (inert proposals only)."""
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()

    l2_path = ad / "l2_output.json"
    x2_path = ad / "x2_gate_outputs.json"
    x3_path = ad / "x3_disposition.json"

    l2 = _load_json(l2_path) if l2_path.is_file() else {}
    x2blob = _load_json(x2_path) if x2_path.is_file() else {}
    x3blob = _load_json(x3_path) if x3_path.is_file() else {}

    gates = x2blob.get("gates") if isinstance(x2blob.get("gates"), list) else []
    failed_ids = [str(g["gate_id"]) for g in gates if isinstance(g, dict) and g.get("pass") is False]
    failed_set = set(failed_ids)
    x2s = summarize_x2(x2blob if isinstance(x2blob, dict) else {})

    jd_v, br_v, cc_v = _proof_violation_counts(l2 if isinstance(l2, dict) else {}, failed_set)

    removed = l2.get("removed_or_rewritten_terms") if isinstance(l2.get("removed_or_rewritten_terms"), list) else []
    unsupported_patterns: list[str] = []
    for row in removed[:12]:
        if isinstance(row, dict):
            t = str(row.get("original_term") or row.get("term") or "").strip()
            if t:
                unsupported_patterns.append(t[:120])
        elif isinstance(row, str) and row.strip():
            unsupported_patterns.append(row.strip()[:120])

    change_log = l2.get("change_log") if isinstance(l2.get("change_log"), list) else []
    rgs = str(l2.get("runtime_generation_status") or "").strip()
    mock_marker_summary = _mock_fixture_marker_summary(
        runtime_generation_status=rgs,
        l2=l2 if isinstance(l2, dict) else {},
        artifact_dir=ad,
    )

    recommendations: list[str] = []
    if failed_ids:
        recommendations.append(
            f"Future-run: tighten competencies prompt/X2 pairing for failed gates: {', '.join(failed_ids[:8])}"
        )
    if jd_v > 0:
        recommendations.append("Future-run: reinforce jd_used_as_proof=false and jd-only term exclusion in PA slots.")
    if br_v > 0:
        recommendations.append("Future-run: reinforce briefing_used_as_proof=false and briefing-only exclusion.")
    if cc_v > 0:
        recommendations.append("Future-run: reinforce companion_context_used_as_proof=false (U-tier only).")
    if mock_marker_summary.get("present"):
        recommendations.insert(
            0,
            "Future-run: remove mock/test fixture markers from competencies prompts, compiled examples, "
            "or deterministic stubs — REAL_LLM outputs must not echo mocked_runtime_slice / mock slice language.",
        )
    if not recommendations:
        recommendations.append(
            "Future-run: continue monitoring duplicate-variant collapse and claim_ledger ↔ term parity."
        )

    proposals_path = ad / "l6_future_run_proposals.json"
    proposals_body = {
        "section_id": SECTION_ID,
        "inert_until_uwg": True,
        "future_run_recommendations": recommendations,
        "notes": "Proposals are not authoritative; gauntlet + UWG promotion required before adoption.",
    }
    proposals_path.write_text(json.dumps(proposals_body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rca_ref = None
    if failed_ids:
        rca_path = ad / "l6_shadow_rca_sketch.json"
        rca_body = {
            "section_id": SECTION_ID,
            "failed_x2_gate_ids": failed_ids,
            "x2_summary": x2s,
            "inert": True,
        }
        rca_path.write_text(json.dumps(rca_body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        rca_ref = repo_rel(rr, rca_path)

    x1sum = base_packet.get("x1d_summary") if isinstance(base_packet.get("x1d_summary"), dict) else {}
    disagree_note = {
        "decisive_failures": x1sum.get("decisive_failures", []),
        "soft_failed_judges": x1sum.get("soft_failed_judges", []),
        "blocked_judges": x1sum.get("blocked_judges", []),
        "mocked_judges": x1sum.get("mocked_judges", []),
    }

    learning_path = ad / "l6_shadow_learning.json"
    sidecar_rel = repo_rel(rr, learning_path)
    learning = {
        "enabled": True,
        "section_id": SECTION_ID,
        "shadow_learning_sidecar_ref": sidecar_rel,
        "runtime_exhaust_ref": base_packet.get("runtime_proof_run_dir_repo_relative"),
        "current_run_boundary_receipt": {
            "boundary_marker": "post_x3_write_pre_L6_shadow",
            "x3_disposition_ref": base_packet.get("x3_disposition_ref"),
            "x3_code_observed": x3blob.get("x3_code"),
            "frozen_assertion": True,
        },
        "observer_law_receipt": {
            "observer_law": OBSERVER_LAW_TEXT,
            "status": "ACK",
        },
        "eval_readiness_receipt": {
            "runtime_exhaust_artifacts_present": all(
                (ad / name).is_file() for name in ("l2_output.json", "x2_gate_outputs.json", "x3_disposition.json")
            ),
            "shadow_eval_human_gate": "PENDING",
        },
        "completed_eval_record_ref": None,
        "rca_packet_ref": rca_ref,
        "proposal_packet_ref": repo_rel(rr, proposals_path),
        "judge_disagreement_summary": disagree_note,
        "deterministic_gate_failure_summary": {"failed_gate_ids": failed_ids, "failed_count": len(failed_ids)},
        "unsupported_term_patterns": unsupported_patterns,
        "jd_as_proof_violation_count": jd_v,
        "briefing_as_proof_violation_count": br_v,
        "companion_context_as_proof_violation_count": cc_v,
        "repair_action_summary": _repair_summary(change_log, runtime_generation_status=rgs),
        "mock_fixture_marker_summary": mock_marker_summary,
        "future_run_recommendations": recommendations,
        "uwg_promotion_request_ref": None,
        "current_run_mutation_assertion": False,
        "current_run_rescue_assertion": False,
        "runtime_allow_contribution": False,
    }
    learning_path.write_text(json.dumps(learning, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return learning


def build_l6_shadow_package(
    *,
    artifact_dir: Path,
    repo_root: Path,
    prompt_id: str,
    temperature: float | None,
    max_tokens: int | None,
) -> dict[str, Any]:
    pkt = build_l6_shadow_handoff_dict(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        section_id=SECTION_ID,
        prompt_id=prompt_id,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    pkt["l6_shadow_learning"] = build_competencies_shadow_learning(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        base_packet=pkt,
    )
    return pkt


__all__ = [
    "OBSERVER_LAW_TEXT",
    "SECTION_ID",
    "build_competencies_shadow_learning",
    "build_l6_shadow_package",
]
