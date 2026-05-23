"""Executive-summary GRADE_ONLY JudgePacket for X1D judges (apps_rg only)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    check_claim_ledger_orphan_source_ids,
    check_exec_summary_evidence_utilization,
    check_exec_summary_meta_filler_patterns,
    check_exec_summary_no_credential_dump,
    check_exec_summary_no_mechanism_inventory,
    check_exec_summary_paragraph_max_words,
    check_exec_summary_sentence_count_6,
    collect_unused_allowed_fact_ids,
)

JUDGE_PACKET_VERSION = "executive_summary_judge_packet_v1"
JUDGE_RUBRIC_REF = "apps_rg/runtime/judges/executive_summary_judge_packet.py#SRFS_GRADE_ONLY_RUBRIC"
GRAPH_ONLY_JUDGE_RUBRIC_REF = (
    "apps_rg/runtime/judges/executive_summary_judge_packet.py#GRAPH_ONLY_GRADE_ONLY_RUBRIC"
)

GRADE_ONLY_INSTRUCTION = """
You are grading a generated executive summary candidate produced by a separate generator.
judge_task: GRADE_ONLY

Mandatory rules:
- Do NOT write a new executive summary.
- Do NOT rewrite or edit the candidate text.
- Do NOT add claims, metrics, credentials, or facts.
- JD_TEXT and BRIEFING are targeting context only — never proof.
- Grade only against the rubric, allowed_fact_packet (graph proof pool), and candidate_output.
- **deterministic_gate_summary is authoritative for X2 gates.** If a gate shows `"pass": true`, you MUST NOT
  claim that gate failed or cite retired criteria (five-part S1–S5 arc, mandatory S5 credential sentence, etc.).
- Return ONLY the required structured judge JSON schema (no markdown fences, no prose).
""".strip()

SRFS_GRADE_ONLY_RUBRIC = """
Rubric dimensions (SRFS executive summary — product shape **exactly 6 sentences**, one paragraph, max 140 words):
1. factual_support: claims supported by allowed_fact_packet and candidate claim_ledger source_fact_ids.
2. executive_signal: SVP-level platform/governance/commercialization synthesis, not bullet stacks.
3. resume_voice: credible third-person executive prose; penalize recruiter filler, "this individual", "Additionally/Furthermore" chains.
4. ats_alignment_without_keyword_stuffing: JD shapes emphasis only; no JD-as-proof.
5. anti_overfit: no unsupported metrics/credentials; no target company as candidate experience.
6. synthesis_quality: **exactly six** integrated sentences with optional composition themes (identity, platform/governance,
   scale/commercialization, outcomes, implied credibility). **Not** a fixed S1–S5 slot checklist. Fewer than six sentences
   is a decisive failure (aligned with x2_exec_summary_sentence_count_6). **Concise alone is insufficient** when
   evidence_utilization lists unused high-confidence facts or prose reads as stacked bullets. Credential facts are
   **optional** — omit rather than inventory AWS/Databricks/FSA/Basel/CCAR labels.
7. evidence_utilization: penalize under-use of allowed_fact_packet when unused_fact_ids is non-empty and synthesis is thin.
8. deterministic_alignment: **only** penalize gates that show `"pass": false` in deterministic_gate_summary.

Retired criteria (do NOT fail the candidate for these alone):
- Mandatory five-sentence arc or missing "S5 credibility sentence"
- S2 mechanism-only / S4 outcomes slot mandates from legacy SRFS shape gate
- Requiring Fellow of the Society of Actuaries or cert list in the paragraph

Decisive failure triggers (must be supported by allowed facts and deterministic_gate_summary failures when cited):
- unsupported business metric or credential in prose
- JD or briefing used as proof
- first-person narrative
- credential/certification inventory block (x2_exec_summary_no_credential_dump alignment)
- mechanism inventory in opening sentence or comma-chain architecture dump
- obvious rewrite recommendation that invents new claims
""".strip()

# Judge hallucination guard: legacy rubric phrases that must not drive decisive_failure when X2 snapshot all pass.
_RETIRED_JUDGE_CRITERIA_FRAGMENTS = (
    "five-sentence arc",
    "five sentence arc",
    "s1 thesis",
    "s2 mechanism",
    "s3 lifecycle",
    "s4 outcomes",
    "s5 credibility",
    "mandatory s5",
    "missing s5",
    "srfs_sentence_responsibility",
    "sentence responsibility shape",
    "s2 mechanism-only",
    "mechanism-only sentence",
)

GRAPH_ONLY_GRADE_ONLY_RUBRIC = """
Rubric dimensions (graph-only C0.3 augmented skills graph authority, non-SRFS lane):
1. factual_support: claims supported by allowed_fact_packet and candidate claim_ledger source_fact_ids only.
2. executive_signal: SVP-level platform/governance/commercialization synthesis, not bullet stacks.
3. resume_voice: credible executive prose; no recruiter filler or meta narration.
4. ats_alignment_without_keyword_stuffing: JD shapes emphasis only; no JD-as-proof.
5. anti_overfit: no unsupported metrics/credentials; no target company as candidate experience.
6. synthesis_quality: **six dense executive sentences** (same band as X2); integrated narrative flow;
   penalize orphan source_fact_ids not in allowed_fact_packet and bare credential inventory.
7. deterministic_alignment: respect deterministic_gate_summary — penalize failed density, orphans, or scope violations.

Decisive failure triggers:
- unsupported business metric or credential
- JD or briefing used as proof
- first-person narrative
- obvious rewrite recommendation that invents new claims
""".strip()

REQUIRED_JUDGE_OUTPUT_SCHEMA = """
Return ONLY one compact JSON object:
{"score_scale":"0_to_5","score":0.0,"threshold":4.0,"pass":true,"decisive_failure":false,
 "findings":["short strings"],"cited_sentence_indexes":[1],
 "remediation_suggestions":[],"rationale":"one short paragraph",
 "fail_reasons":[],"unsupported_claims":[],"quality_flags":[]}
score_scale must be 0_to_5 or 0_to_1 with in-range score/threshold.
""".strip()


def enrich_allowed_fact_packet_for_judges(
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> list[dict[str, Any]]:
    """Include metric-derivative rows so X1D judges see the same allowlist as X2."""
    from apps_rg.runtime.sections.selected_role_fact_set import metric_derivative_fact_id

    by_id: dict[str, dict[str, Any]] = {
        str(f.get("fact_id")): dict(f) for f in plan_facts if str(f.get("fact_id") or "").strip()
    }
    out: list[dict[str, Any]] = [dict(f) for f in plan_facts]
    for fid in sorted(allowed_fact_ids):
        if fid in by_id:
            continue
        base = fid.split("_metric_")[0]
        parent = by_id.get(base)
        if not parent:
            continue
        mr = str(parent.get("metric_raw") or "").strip()
        if not mr or metric_derivative_fact_id(base, mr) != fid:
            continue
        derivative = dict(parent)
        derivative["fact_id"] = fid
        derivative["has_metric"] = True
        out.append(derivative)
        by_id[fid] = derivative
    return out


def _collect_source_fact_ids(claim_ledger: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            s = str(fid).strip()
            if s and s not in seen:
                seen.add(s)
                ids.append(s)
    return ids


def build_deterministic_gate_summary(
    *,
    resume_display_text: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Pre-judge X2 gate snapshot aligned with live product-shape gates (exactly six sentences, max 140 words)."""
    sent_ok, sent_reason = check_exec_summary_sentence_count_6(resume_display_text)
    cred_ok, cred_reason = check_exec_summary_no_credential_dump(resume_display_text)
    mech_ok, mech_reason = check_exec_summary_no_mechanism_inventory(resume_display_text)
    bounds_ok, bounds_reason = check_exec_summary_paragraph_max_words(
        resume_display_text, parsed_output
    )
    meta_ok, meta_reason = check_exec_summary_meta_filler_patterns(resume_display_text)
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        resume_display_text, parsed_output
    )
    orphan_ok, orphan_reason = check_claim_ledger_orphan_source_ids(claim_ledger, allowed_fact_ids)
    parse_ok = bool(parsed_output) and not (parsed_output or {}).get("parse_error")
    ledger_nonempty = all(
        isinstance(r, dict) and str(r.get("claim_text") or "").strip() for r in claim_ledger
    )
    return {
        "x2_exec_summary_sentence_count_6": {
            "pass": sent_ok,
            "detail": sent_reason or "ok",
        },
        "x2_exec_summary_paragraph_max_words": {
            "pass": bounds_ok,
            "detail": bounds_reason or "ok",
        },
        "x2_exec_summary_no_credential_dump": {
            "pass": cred_ok,
            "detail": cred_reason or "ok",
        },
        "x2_exec_summary_no_mechanism_inventory": {
            "pass": mech_ok,
            "detail": mech_reason or "ok",
        },
        "x2_exec_summary_meta_filler_zero": {
            "pass": meta_ok,
            "detail": meta_reason or "ok",
        },
        "x2_exec_summary_evidence_utilization": {
            "pass": util_ok,
            "detail": util_reason or "ok",
        },
        "x2_schema_valid": {"pass": parse_ok, "detail": "parsed_output_present" if parse_ok else "parse_missing"},
        "x2_json_parse_valid": {"pass": parse_ok, "detail": "ok" if parse_ok else "json_parse_failed"},
        "x2_claim_ledger_claim_text_non_empty": {
            "pass": ledger_nonempty,
            "detail": "ok" if ledger_nonempty else "empty_claim_text",
        },
        "x2_claim_ledger_orphan_zero": {
            "pass": orphan_ok,
            "detail": orphan_reason or "ok",
        },
        "product_shape_note": {
            "pass": True,
            "detail": "exactly 6 sentences; composition heuristics; no mandatory S1-S5 arc",
        },
    }


def reconcile_grade_only_judge_result(
    result: dict[str, Any],
    deterministic_gate_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    """Downgrade decisive_failure when judges cite retired arc criteria but X2 snapshot gates all pass."""
    if not isinstance(result, dict) or not isinstance(deterministic_gate_summary, dict):
        return result
    gate_entries = [
        v for v in deterministic_gate_summary.values() if isinstance(v, dict) and "pass" in v
    ]
    if not gate_entries or not all(bool(v.get("pass")) for v in gate_entries):
        return result
    blob = json.dumps(result, ensure_ascii=False).lower()
    if not any(frag in blob for frag in _RETIRED_JUDGE_CRITERIA_FRAGMENTS):
        return result
    out = dict(result)
    if out.get("decisive_failure"):
        out["decisive_failure"] = False
        findings = list(out.get("findings") or [])
        findings.append(
            "Reconciled: judge cited retired five-part/S1-S5 criteria; deterministic_gate_summary all pass."
        )
        out["findings"] = findings
        try:
            score = float(out.get("score", 0.0))
            threshold = float(out.get("threshold", 4.0))
            if score < threshold:
                out["score"] = threshold
                out["pass"] = True
        except (TypeError, ValueError):
            pass
    return out


def build_executive_summary_judge_packet(
    *,
    resume_display_text: str,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_packet: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing_text: str,
    parsed_output: dict[str, Any] | None,
    deterministic_gate_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build canonical GRADE_ONLY JudgePacket dict for executive_summary X1D."""
    gate_summary = deterministic_gate_summary or build_deterministic_gate_summary(
        resume_display_text=resume_display_text,
        parsed_output=parsed_output,
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
    )
    rubric = GRAPH_ONLY_GRADE_ONLY_RUBRIC
    rubric_ref = GRAPH_ONLY_JUDGE_RUBRIC_REF
    judge_allowed_packet = enrich_allowed_fact_packet_for_judges(
        list(allowed_fact_packet),
        allowed_fact_ids,
    )
    unused_fact_ids = collect_unused_allowed_fact_ids(claim_ledger, allowed_fact_ids)
    cited_fact_ids = _collect_source_fact_ids(claim_ledger)
    return {
        "judge_packet_version": JUDGE_PACKET_VERSION,
        "section": "executive_summary",
        "judge_task": "GRADE_ONLY",
        "candidate_output": {
            "resume_display_text": resume_display_text,
            "claim_ledger": claim_ledger,
            "source_fact_ids": _collect_source_fact_ids(claim_ledger),
        },
        "allowed_fact_packet": judge_allowed_packet,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "evidence_utilization": {
            "cited_fact_ids": cited_fact_ids,
            "unused_fact_ids": unused_fact_ids,
            "unused_fact_count": len(unused_fact_ids),
            "allowed_fact_count": len(allowed_fact_ids),
        },
        "target_title": target_title,
        "target_company": target_company,
        "targeting_context": {
            "jd_text": jd_text,
            "briefing": briefing_text,
        },
        "proof_boundary": {
            "jd_is_targeting_context_only": True,
            "briefing_is_targeting_context_only": True,
            "claims_must_be_supported_by_allowed_fact_packet": True,
            "judges_must_not_rewrite": True,
            "judges_must_not_generate_replacement_summary": True,
        },
        "deterministic_gate_summary": gate_summary,
        "rubric_ref": rubric_ref,
        "rubric": rubric,
        "judge_rubric_mode": "graph_only_c03",
        "grading_instruction": GRADE_ONLY_INSTRUCTION,
        "required_output_schema": REQUIRED_JUDGE_OUTPUT_SCHEMA,
    }


def judge_packet_hash(packet: dict[str, Any]) -> str:
    canonical = json.dumps(packet, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def write_executive_summary_judge_packet(path: Path, packet: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    enriched = dict(packet)
    enriched["judge_packet_hash"] = judge_packet_hash(packet)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False, default=str)
    return str(path)


def render_judge_prompt_from_packet(packet: dict[str, Any]) -> str:
    """Render judge user message from JudgePacket — never the generator compiled_prompt."""
    parts = [
        packet.get("grading_instruction") or GRADE_ONLY_INSTRUCTION,
        "",
        f"JUDGE_TASK: {packet.get('judge_task', 'GRADE_ONLY')}",
        f"SECTION: {packet.get('section', 'executive_summary')}",
        "",
        "PROOF_BOUNDARY:",
        json.dumps(packet.get("proof_boundary") or {}, indent=2),
        "",
        "DETERMINISTIC_GATE_SUMMARY (AUTHORITATIVE — do not contradict pass=true gates):",
        json.dumps(packet.get("deterministic_gate_summary") or {}, indent=2),
        "",
        packet.get("rubric") or SRFS_GRADE_ONLY_RUBRIC,
        "",
        packet.get("required_output_schema") or REQUIRED_JUDGE_OUTPUT_SCHEMA,
        "",
        "TARGETING_CONTEXT (NOT PROOF):",
        json.dumps(packet.get("targeting_context") or {}, indent=2),
        f"TARGET_TITLE: {packet.get('target_title', '')}",
        f"TARGET_COMPANY: {packet.get('target_company', '')}",
        "",
        "ALLOWED_FACT_PACKET (graph proof pool):",
        json.dumps(packet.get("allowed_fact_packet") or [], separators=(",", ":")),
        "",
        "EVIDENCE_UTILIZATION (deterministic — unused facts are weave targets, not proof gaps):",
        json.dumps(packet.get("evidence_utilization") or {}, indent=2),
        "",
        "CANDIDATE_OUTPUT:",
        json.dumps(packet.get("candidate_output") or {}, indent=2),
    ]
    return "\n".join(parts)


def packet_forbids_generator_prompt_reuse(compiled_prompt: str | None, judge_prompt: str) -> bool:
    """True when judge prompt is not a substring reuse of the L2 generator prompt."""
    if not compiled_prompt:
        return True
    gen = compiled_prompt.strip()
    if len(gen) < 200:
        return True
    return gen[:500] not in judge_prompt
