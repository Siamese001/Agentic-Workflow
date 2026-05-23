"""Deterministic executive_summary evidence capsule — compact graph proof packet for PA.

Replaces verbose appendix/style-onshot prose in the compiled prompt while preserving
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
    metric_derivative_fact_id,
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
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    return bool(facts)


def _proof_pool_context_from_payload(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    pp = runtime_payload.get("proof_pool_metadata") or {}
    if not isinstance(pp, dict):
        pp = {}
    ss = pp.get("selection_scope")
    if not isinstance(ss, dict):
        ss = {}
    allowed = list(runtime_payload.get("allowed_fact_ids") or [])
    return {
        "selection_id": str(ss.get("selection_id") or pp.get("selection_id") or "").strip(),
        "executive_summary_selected_fact_ids": allowed,
        "blocked_facts_count": int(pp.get("blocked_facts_count") or 0),
        "facts_requiring_human_confirmation_count": int(
            pp.get("facts_requiring_human_confirmation_count") or 0
        ),
        "unsupported_jd_needs_count": int(pp.get("unsupported_jd_needs_count") or 0),
    }


def _input_proof_pool_digest(
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
    pool_context: dict[str, Any],
) -> dict[str, Any]:
    """Canonical capsule object (deterministic ordering)."""
    pp = runtime_payload.get("proof_pool_metadata") or {}
    if not isinstance(pp, dict):
        pp = {}
    ea = pp.get("evidence_authority") if isinstance(pp.get("evidence_authority"), dict) else {}
    authority_label = str(
        ea.get("authority") or ea.get("type") or "augmented_skills_graph"
    ).strip() or "augmented_skills_graph"
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
                "source_authority": authority_label,
                "section_membership": SECTION_ID,
            }
        )
    graph_used = bool(plan_facts)
    pool_counts = {
        "blocked_facts": int(pool_context.get("blocked_facts_count") or 0),
        "facts_requiring_human_confirmation": int(
            pool_context.get("facts_requiring_human_confirmation_count") or 0
        ),
        "unsupported_jd_needs": int(pool_context.get("unsupported_jd_needs_count") or 0),
    }
    return {
        "capsule_version": CAPSULE_VERSION,
        "section_id": SECTION_ID,
        "proof_pool_type": str(pp.get("proof_pool_type") or "augmented_skills_graph"),
        "graph_proof_pool_used": graph_used,
        "selected_role_fact_set_used": False,
        "selection_id": str(pool_context.get("selection_id") or ""),
        "evidence_authority": authority_label,
        "rules": {
            "jd_targeting_only_rule": True,
            "no_fabrication_rule": True,
            "claim_ledger_rules": True,
            "briefing_not_proof": True,
            "jd_not_proof": True,
        },
        "allowed_fact_ids": list(allowed_ids),
        "facts": fact_rows,
        "proof_pool_counts": pool_counts,
        "srfs_counts": pool_counts,
        "product_arc_markers": [
            "x2_exec_summary_sentence_count_6",
            "x2_exec_summary_paragraph_max_words",
        ],
        "srfs_arc_markers": [
            "x2_exec_summary_sentence_count_6",
            "x2_exec_summary_paragraph_max_words",
        ],
    }


def format_evidence_capsule_c0_block(
    capsule: dict[str, Any],
    allowed_ids: list[str],
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> str:
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
    graph_pa = (
        runtime_payload.get("graph_targeting_for_pa")
        if isinstance(runtime_payload, dict)
        else None
    )
    overload_by_fact: dict[str, dict[str, Any]] = {}
    if isinstance(graph_pa, dict):
        for row in graph_pa.get("overloaded_fact_compression") or []:
            if isinstance(row, dict) and str(row.get("fact_id") or "").strip():
                overload_by_fact[str(row["fact_id"])] = row
    for row in capsule.get("facts") or []:
        fid = row.get("source_fact_id", "")
        ct = row.get("claim_text", "")
        mr = row.get("metric_raw")
        extra = ""
        if mr:
            extra = f" metric_raw={mr!r}"
        ovl = overload_by_fact.get(fid)
        if ovl:
            phrases = "; ".join(ovl.get("executive_capability_phrases") or [])
            extra += (
                f" OUTCOME_FRAMING_REQUIRED=true max_mechanism_terms=2;"
                f" prefer_capability_phrases=[{phrases}];"
                " do_not_echo_full_mechanism_inventory_from_claim_text."
            )
        lines.append(f"- {fid}: {ct}{extra}")
    compression = runtime_payload.get("c04_exec_summary_compression") if isinstance(runtime_payload, dict) else None
    if isinstance(graph_pa, dict) and graph_pa.get("receipt_only_json_expansion_excluded_from_pa"):
        lines.extend(
            [
                "",
                "GRAPH_TARGETING_FOR_PA (claim support only; JSON expansion refs are receipt-only):",
                f"targeting_pillars={','.join(graph_pa.get('targeting_graph_refs') or [])}",
                f"mechanism_vocabulary_cap={graph_pa.get('mechanism_vocabulary_cap')}",
            ]
        )
        for row in graph_pa.get("overloaded_fact_compression") or []:
            if not isinstance(row, dict):
                continue
            lines.append(
                f"- {row.get('fact_id')}: use executive_capability_phrases="
                f"{row.get('executive_capability_phrases')}; "
                f"max_mechanism_terms={row.get('pa_mechanism_terms_max_per_sentence')}"
            )
    if isinstance(compression, dict) and compression.get("pa_instruction"):
        lines.append(f"C04_COMPRESSION_INSTRUCTION: {compression.get('pa_instruction')}")
    if isinstance(runtime_payload, dict):
        gtc = runtime_payload.get("graph_targeting_capsule")
        if isinstance(gtc, dict):
            from apps_rg.runtime.c0.exec_summary_graph_targeting_capsule import (
                format_graph_targeting_capsule_for_pa,
            )

            lines.extend(["", format_graph_targeting_capsule_for_pa(gtc)])

    counts = capsule.get("proof_pool_counts") or capsule.get("srfs_counts") or {}
    lines.extend(
        [
            "",
            "PROOF_POOL_COUNTS (metadata only): "
            f"blocked={counts.get('blocked_facts', 0)} "
            f"confirmation={counts.get('facts_requiring_human_confirmation', 0)} "
            f"unsupported_jd={counts.get('unsupported_jd_needs', 0)}",
            "PRODUCT_ARC_CONTRACT: exactly 6 sentences, fit_to_evidence, max 140 words; responsibility separation per X2 gates. "
            "Style exemplar/appendix prose omitted from capsule (proof IDs unchanged).",
            "",
        ]
    )
    body = "\n".join(lines)
    return f"{header}\n\n{body}"


def format_evidence_capsule_appendix(capsule: dict[str, Any]) -> str:
    """Minimal graph proof appendix — metadata and ID list only (no style boilerplate)."""
    ids = [
        str(r.get("source_fact_id") or "")
        for r in (capsule.get("facts") or [])
        if str(r.get("source_fact_id") or "")
    ]
    id_tail = ", ".join(ids[:16])
    if len(ids) > 16:
        id_tail += ", …"
    counts = capsule.get("proof_pool_counts") or capsule.get("srfs_counts") or {}
    authority = str(capsule.get("evidence_authority") or "augmented_skills_graph")
    return (
        "GRAPH_PROOF_POOL_APPENDIX_CAPSULE:\n"
        f"- proof_pool_type: {capsule.get('proof_pool_type')}\n"
        f"- evidence_authority: {authority} (in-memory; no JSON file authority)\n"
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
    if not facts:
        raise ValueError("evidence capsule requires selected_fact_plan.facts")
    pool_context = _proof_pool_context_from_payload(runtime_payload)

    allowed_ids, _ = build_allowed_fact_ids_for_plan_facts(facts)
    required_high = [str(f.get("fact_id") or "").strip() for f in facts if str(f.get("fact_id") or "").strip()]

    input_digest = _input_proof_pool_digest(
        selection_id=str(pool_context.get("selection_id") or ""),
        plan_facts=facts,
        allowed_ids=allowed_ids,
    )
    capsule = build_capsule_document(
        runtime_payload=runtime_payload,
        plan_facts=facts,
        allowed_ids=allowed_ids,
        pool_context=pool_context,
    )
    output_digest = _sha16(capsule)

    preserved, dropped, violations, metric_status = validate_capsule_preservation(
        required_high_ids=required_high,
        allowed_ids=allowed_ids,
        capsule=capsule,
    )

    c0_block = format_evidence_capsule_c0_block(capsule, allowed_ids, runtime_payload=runtime_payload)
    appendix = format_evidence_capsule_appendix(capsule)
    capsule_token_est = estimate_tokens_approximate(c0_block + "\n" + appendix)

    receipt: dict[str, Any] = {
        "status": "PASS",
        "section": SECTION_ID,
        "capsule_version": CAPSULE_VERSION,
        "input_proof_pool_digest": input_digest,
        "input_srfs_digest": input_digest,
        "output_capsule_digest": output_digest,
        "proof_pool_type": capsule.get("proof_pool_type"),
        "graph_proof_pool_used": True,
        "selected_role_fact_set_used": False,
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
        "input_proof_pool_digest": input_digest,
        "input_srfs_digest": input_digest,
    }
    runtime_payload["evidence_capsule_active"] = True
    return capsule, receipt


def load_srfs_and_build_capsule_from_path(
    runtime_payload: dict[str, Any],
    srfs_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Removed: SRFS JSON file authority is not permitted on the product path."""
    _ = runtime_payload
    raise ExecutiveSummaryEvidenceCapsuleError(
        receipt={
            "status": "FAIL",
            "fail_closed_reason": "srfs_json_file_authority_removed",
            "srfs_path": str(srfs_path),
        }
    )


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
