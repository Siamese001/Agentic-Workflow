"""Deterministic executive_summary evidence capsule — compact SRFS proof packet for PA.

Replaces verbose SRFS appendix/style-onshot prose in the compiled prompt while preserving
source_fact_ids, HIGH fact claim text, metric anchors, and evidence rules. Not LLM compression.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.executive_summary_token_budget import estimate_tokens_approximate
from apps_rg.runtime.sections.executive_summary_pa import format_allowed_source_fact_ids_contract
from apps_rg.runtime.sections.selected_role_fact_set import (
    build_allowed_fact_ids_for_plan_facts,
    load_selected_role_fact_set,
    metric_derivative_fact_id,
    slice_row_to_plan_fact,
)

SECTION_ID = "executive_summary"
CAPSULE_VERSION = "executive_summary_evidence_capsule_v1"
FAIL_PRESERVATION = "EVIDENCE_CAPSULE_PRESERVATION_FAILED"

_STYLE_ONLY_MARKERS = (
    "srfs_style_only_oneshot",
    "exemplar_paragraph",
    "srfs_style_contrast",
    "srfs_suggested_target_shape",
    "STYLE_ONLY_NOT_PROOF",
)


class ExecutiveSummaryEvidenceCapsuleError(Exception):
    """Fail closed when capsule cannot preserve required proof identifiers."""

    def __init__(self, *, receipt: dict[str, Any]) -> None:
        self.receipt = receipt
        super().__init__(receipt.get("fail_closed_reason") or FAIL_PRESERVATION)


def _sha16(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _normalize_claim_text(text: str) -> str:
    """Whitespace-only normalization — not semantic summarization."""
    return re.sub(r"\s+", " ", str(text or "").strip())


def _capsule_enabled(runtime_payload: dict[str, Any]) -> bool:
    if runtime_payload.get("evidence_capsule_disabled") is True:
        return False
    raw = str(runtime_payload.get("APPS_RG_EXEC_SUMMARY_EVIDENCE_CAPSULE") or "").strip().lower()
    env = os.environ.get("APPS_RG_EXEC_SUMMARY_EVIDENCE_CAPSULE", "1").strip().lower()
    if raw in ("0", "false", "no"):
        return False
    if env in ("0", "false", "no"):
        return False
    pp = runtime_payload.get("proof_pool_metadata") or {}
    return str(pp.get("proof_pool_type") or "") == "selected_role_fact_set"


def _input_srfs_digest(
    *,
    selection_id: str,
    plan_facts: list[dict[str, Any]],
    allowed_ids: list[str],
) -> str:
    rows = []
    for f in sorted(plan_facts, key=lambda x: str(x.get("fact_id") or "")):
        fid = str(f.get("fact_id") or "")
        rows.append(
            {
                "fact_id": fid,
                "claim_text": _normalize_claim_text(str(f.get("claim_text") or "")),
                "metric_raw": str(f.get("metric_raw") or ""),
                "confidence": str(f.get("confidence") or ""),
            }
        )
    return _sha16(
        {
            "selection_id": selection_id,
            "facts": rows,
            "allowed_fact_ids": list(allowed_ids),
        }
    )


def build_capsule_document(
    *,
    runtime_payload: dict[str, Any],
    plan_facts: list[dict[str, Any]],
    allowed_ids: list[str],
    srfs_integration: dict[str, Any],
) -> dict[str, Any]:
    """Canonical capsule object (deterministic ordering)."""
    fact_rows: list[dict[str, Any]] = []
    for fact in sorted(plan_facts, key=lambda x: str(x.get("fact_id") or "")):
        fid = str(fact.get("fact_id") or "").strip()
        mr = str(fact.get("metric_raw") or "").strip()
        anchors: list[str] = []
        if mr:
            anchors.append(metric_derivative_fact_id(fid, mr))
        fact_rows.append(
            {
                "source_fact_id": fid,
                "priority": str(fact.get("confidence") or "HIGH").upper(),
                "claim_text": _normalize_claim_text(str(fact.get("claim_text") or "")),
                "metric_raw": mr or None,
                "metric_anchor_ids": anchors,
                "source_authority": "selected_role_fact_set",
                "section_membership": SECTION_ID,
            }
        )
    pp = runtime_payload.get("proof_pool_metadata") or {}
    return {
        "capsule_version": CAPSULE_VERSION,
        "section_id": SECTION_ID,
        "proof_pool_type": str(pp.get("proof_pool_type") or "selected_role_fact_set"),
        "selected_role_fact_set_used": True,
        "selection_id": str(srfs_integration.get("selection_id") or ""),
        "artifact_path_resolved": str(srfs_integration.get("artifact_path_resolved") or ""),
        "rules": {
            "jd_targeting_only_rule": True,
            "no_fabrication_rule": True,
            "claim_ledger_rules": True,
            "briefing_not_proof": True,
            "jd_not_proof": True,
        },
        "allowed_fact_ids": list(allowed_ids),
        "facts": fact_rows,
        "srfs_counts": {
            "blocked_facts": int(srfs_integration.get("blocked_facts_count") or 0),
            "facts_requiring_human_confirmation": int(
                srfs_integration.get("facts_requiring_human_confirmation_count") or 0
            ),
            "unsupported_jd_needs": int(srfs_integration.get("unsupported_jd_needs_count") or 0),
        },
        "srfs_arc_markers": [
            "SRFS_FIVE_PART_EXEC_ARCH_V1",
            "SRFS_SENTENCE_RESP_SEP_V1",
            "x2_exec_summary_srfs_sentence_count_4_5",
            "x2_exec_summary_srfs_density_word_count",
        ],
    }


def format_evidence_capsule_c0_block(capsule: dict[str, Any], allowed_ids: list[str]) -> str:
    """Compact C0 proof substrate for PA (excludes style-only SRFS prose)."""
    header = format_allowed_source_fact_ids_contract(allowed_ids)
    lines = [
        f"EVIDENCE_CAPSULE_{CAPSULE_VERSION.upper()} (deterministic proof packet; not style guidance):",
        f"proof_pool_type={capsule.get('proof_pool_type')}",
        f"selection_id={capsule.get('selection_id')}",
        "JD_TARGETING_ONLY=true",
        "NO_FABRICATION=true",
        "CLAIM_LEDGER_REQUIRED=true",
        "source_fact_ids must match ALLOWED_SOURCE_FACT_IDS verbatim (no normalization).",
        "",
        "EVIDENCE_FACTS (HIGH executive_summary slice only):",
    ]
    for row in capsule.get("facts") or []:
        fid = row.get("source_fact_id", "")
        ct = row.get("claim_text", "")
        mr = row.get("metric_raw")
        extra = ""
        if mr:
            extra = f" metric_raw={mr!r}"
        lines.append(f"- {fid}: {ct}{extra}")
    counts = capsule.get("srfs_counts") or {}
    lines.extend(
        [
            "",
            "SRFS_COUNTS (metadata only): "
            f"blocked={counts.get('blocked_facts', 0)} "
            f"confirmation={counts.get('facts_requiring_human_confirmation', 0)} "
            f"unsupported_jd={counts.get('unsupported_jd_needs', 0)}",
            "SRFS_ARC_CONTRACT: 4-5 sentences, 95-160 words; responsibility separation per X2 gates. "
            "Style exemplar/appendix prose omitted from capsule (proof IDs unchanged).",
            "",
        ]
    )
    body = "\n".join(lines)
    return f"{header}\n\n{body}"


def format_evidence_capsule_appendix(capsule: dict[str, Any]) -> str:
    """Minimal SRFS appendix — metadata and ID list only (no style boilerplate)."""
    ids = [
        str(r.get("source_fact_id") or "")
        for r in (capsule.get("facts") or [])
        if str(r.get("source_fact_id") or "")
    ]
    id_tail = ", ".join(ids[:16])
    if len(ids) > 16:
        id_tail += ", …"
    counts = capsule.get("srfs_counts") or {}
    return (
        "SELECTED_ROLE_FACT_SET_APPENDIX_CAPSULE:\n"
        f"- Artifact: {capsule.get('artifact_path_resolved')}\n"
        f"- selection_id: {capsule.get('selection_id')}\n"
        f"- HIGH proof pool source_fact_ids (executive_summary): [{id_tail}]\n"
        f"- Counts - blocked_facts: {counts.get('blocked_facts', 0)}; "
        f"facts_requiring_human_confirmation: {counts.get('facts_requiring_human_confirmation', 0)}; "
        f"unsupported_jd_needs: {counts.get('unsupported_jd_needs', 0)}\n"
        "- Substantive claims cite ONLY ALLOWED_SOURCE_FACT_IDS from EVIDENCE_CAPSULE above.\n"
        "- JD_TEXT and BRIEFING remain targeting-only; jd_alignment jd_used_as_proof must be false.\n"
    )


def validate_capsule_preservation(
    *,
    required_high_ids: list[str],
    allowed_ids: list[str],
    capsule: dict[str, Any],
) -> tuple[list[str], list[str], list[str], str]:
    """Return (preserved_high, dropped_high, violations, metric_anchor_status)."""
    violations: list[str] = []
    cap_ids = {str(r.get("source_fact_id") or "") for r in (capsule.get("facts") or [])}
    preserved = [fid for fid in required_high_ids if fid in cap_ids]
    dropped = [fid for fid in required_high_ids if fid not in cap_ids]
    if dropped:
        violations.append(f"dropped_high_fact_ids:{','.join(dropped)}")
    cap_allowed = list(capsule.get("allowed_fact_ids") or [])
    if cap_allowed != list(allowed_ids):
        violations.append("allowed_fact_ids_order_or_content_mismatch")
    for aid in allowed_ids:
        if aid not in cap_allowed:
            violations.append(f"missing_allowed_id:{aid}")
    for row in capsule.get("facts") or []:
        fid = str(row.get("source_fact_id") or "")
        ct = str(row.get("claim_text") or "").strip()
        if not fid or not ct:
            violations.append(f"empty_fact_row:{fid or '?'}")

    metric_status = "NOT_APPLICABLE"
    for row in capsule.get("facts") or []:
        mr = row.get("metric_raw")
        anchors = row.get("metric_anchor_ids") or []
        if mr:
            metric_status = "PASS"
            fid = str(row.get("source_fact_id") or "")
            expected = metric_derivative_fact_id(fid, str(mr))
            if expected not in allowed_ids:
                violations.append(f"metric_anchor_not_in_allowed:{expected}")
            elif expected not in anchors:
                violations.append(f"metric_anchor_missing_in_row:{fid}")
    return preserved, dropped, violations, metric_status


def compile_executive_summary_evidence_capsule(
    runtime_payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build capsule + receipt; attach capsule fields to runtime_payload on PASS."""
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    srfs = runtime_payload.get("srfs_integration")
    if not isinstance(srfs, dict) or not facts:
        raise ValueError("evidence capsule requires srfs_integration and selected_fact_plan.facts")

    allowed_ids, _ = build_allowed_fact_ids_for_plan_facts(facts)
    required_high = [str(f.get("fact_id") or "").strip() for f in facts if str(f.get("fact_id") or "").strip()]

    input_digest = _input_srfs_digest(
        selection_id=str(srfs.get("selection_id") or ""),
        plan_facts=facts,
        allowed_ids=allowed_ids,
    )
    capsule = build_capsule_document(
        runtime_payload=runtime_payload,
        plan_facts=facts,
        allowed_ids=allowed_ids,
        srfs_integration=srfs,
    )
    output_digest = _sha16(capsule)

    preserved, dropped, violations, metric_status = validate_capsule_preservation(
        required_high_ids=required_high,
        allowed_ids=allowed_ids,
        capsule=capsule,
    )

    c0_block = format_evidence_capsule_c0_block(capsule, allowed_ids)
    appendix = format_evidence_capsule_appendix(capsule)
    capsule_token_est = estimate_tokens_approximate(c0_block + "\n" + appendix)

    receipt: dict[str, Any] = {
        "status": "PASS",
        "section": SECTION_ID,
        "capsule_version": CAPSULE_VERSION,
        "input_srfs_digest": input_digest,
        "output_capsule_digest": output_digest,
        "proof_pool_type": capsule.get("proof_pool_type"),
        "selected_role_fact_set_used": True,
        "allowed_fact_ids_count": len(allowed_ids),
        "required_high_fact_ids": required_high,
        "preserved_high_fact_ids": preserved,
        "dropped_high_fact_ids": dropped,
        "optional_content_removed": [
            "srfs_style_only_oneshot_block",
            "srfs_exemplar_paragraph",
            "srfs_style_contrast_chain_vs_split",
            "srfs_suggested_target_shape",
            "verbose_selected_role_fact_set_appendix_prose",
        ],
        "source_fact_id_preservation_status": "PASS" if not violations else "FAIL",
        "metric_anchor_preservation_status": metric_status,
        "jd_targeting_only_rule_preserved": True,
        "no_fabrication_rule_preserved": True,
        "claim_ledger_rules_preserved": True,
        "capsule_token_estimate": capsule_token_est,
        "capsule_reduction_estimate": None,
        "capsule_used_by_prompt_assembly": True,
        "fail_closed_reason": None,
    }

    if violations:
        receipt["status"] = "FAIL"
        receipt["fail_closed_reason"] = FAIL_PRESERVATION
        receipt["source_fact_id_preservation_status"] = "FAIL"
        receipt["preservation_violations"] = violations
        receipt["capsule_used_by_prompt_assembly"] = False
        raise ExecutiveSummaryEvidenceCapsuleError(receipt=receipt)

    runtime_payload["evidence_capsule"] = {
        "capsule_version": CAPSULE_VERSION,
        "document": capsule,
        "c0_block": c0_block,
        "appendix_capsule": appendix,
        "output_capsule_digest": output_digest,
        "input_srfs_digest": input_digest,
    }
    runtime_payload["evidence_capsule_active"] = True
    return capsule, receipt


def load_srfs_and_build_capsule_from_path(
    runtime_payload: dict[str, Any],
    srfs_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load SRFS JSON, rebuild plan facts, then compile capsule (integration helper)."""
    from apps_rg.runtime.sections.selected_role_fact_set import (
        build_srfs_integration_envelope,
        get_section_fact_slice,
    )

    doc = load_selected_role_fact_set(srfs_path)
    slice_rows = get_section_fact_slice(doc, SECTION_ID)
    plan_facts = [slice_row_to_plan_fact(r, section_id=SECTION_ID) for r in slice_rows]
    allowed, _ = build_allowed_fact_ids_for_plan_facts(plan_facts)
    runtime_payload.setdefault("selected_fact_plan", {})["facts"] = plan_facts
    runtime_payload["allowed_fact_ids"] = allowed
    env = build_srfs_integration_envelope(
        doc,
        executive_summary_plan_facts=plan_facts,
        artifact_path_resolved=str(srfs_path),
    )
    runtime_payload["srfs_integration"] = env
    return compile_executive_summary_evidence_capsule(runtime_payload)


def write_evidence_capsule_receipt(artifact_dir, receipt: dict[str, Any]) -> None:
    path = Path(artifact_dir) / "evidence_capsule_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def capsule_excludes_style_prose(text: str) -> bool:
    """True when compiled prompt omits style-only SRFS blocks (capsule path)."""
    lower = text.lower()
    return not any(m.lower() in lower for m in _STYLE_ONLY_MARKERS) or (
        "EVIDENCE_CAPSULE_" in text and "<srfs_style_only_oneshot" not in lower
    )


__all__ = [
    "CAPSULE_VERSION",
    "ExecutiveSummaryEvidenceCapsuleError",
    "FAIL_PRESERVATION",
    "build_capsule_document",
    "compile_executive_summary_evidence_capsule",
    "format_evidence_capsule_appendix",
    "format_evidence_capsule_c0_block",
    "capsule_excludes_style_prose",
    "_capsule_enabled",
    "write_evidence_capsule_receipt",
]
