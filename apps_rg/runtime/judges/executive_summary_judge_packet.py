"""Executive-summary GRADE_ONLY JudgePacket for X1D judges (apps_rg only)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
    dimension_gate_map,
    generation_law_digest_text,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_claim_ledger_orphan_source_ids,
    check_exec_summary_evidence_utilization,
    check_exec_summary_mechanical_opener_stack,
    check_exec_summary_meta_filler_patterns,
    check_exec_summary_no_credential_dump,
    check_exec_summary_no_mechanism_inventory,
    check_exec_summary_paragraph_max_words,
    check_exec_summary_robotic_transition_stack,
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
- **DISPLAY_OVERRIDE PARITY (CRITICAL):** When an `allowed_fact_packet` row carries a non-empty
  `display_override_text` field, treat the **UNION** of `claim_text` + `display_override_text` as the
  authorized fact substrate for that fact_id. The generator (PROVIDER_MODEL) is contractually required by X2 gate
  `x2_exec_summary_display_override_compliance` to emit the override text verbatim. Phrases drawn from
  `display_override_text` are **NOT unsupported extensions** and MUST NOT be cited as "extending beyond
  fact scope" or as inferential stretches. Grade fidelity to the union, not to `claim_text` alone.
- **GRAPH_PROOF_REFS (CRITICAL):** When a row carries `graph_proof_refs.claim_support_graph_refs`, grade
  `factual_support` against the UNION of `claim_text`, `display_override_text` (if any), and sentences that
  demonstrate skills listed in `claim_support_graph_refs`. Treat `graph_proof_refs.source_resume_files` as
  authoritative provenance for resume-backed skill claims — not as optional decoration.
- Return ONLY the required structured judge JSON schema (no markdown fences, no prose).
""".strip()

SRFS_GRADE_ONLY_RUBRIC = """
Rubric dimensions (SRFS executive summary — product shape **exactly 6 sentences**, one paragraph, max 140 words):
1. factual_support: claims supported by allowed_fact_packet and candidate claim_ledger source_fact_ids.
2. executive_signal: SVP-level platform/governance/partner-motion synthesis, not bullet stacks.
3. resume_voice: credible third-person executive prose; penalize recruiter filler, "this individual", "Additionally/Furthermore" chains, generic AI-company prose, and anything that would fail a Head of Talent Acquisition screen.
4. ats_alignment_without_keyword_stuffing: JD shapes emphasis only; no JD-as-proof. When allowed facts
   lack EA/interop/federated proof IDs, penalize only if prose invents those themes or ignores documented
   gap_notes — not for absence alone when generation_law_digest requires gap_notes. Reward company-DNA specificity when the
   packet supports partner ecosystem, adoption motion, commercial fit, or a clean Head of Talent Acquisition screen.
5. anti_overfit: no unsupported metrics/credentials; no target company as candidate experience; no repeated metric inventory
   or company-name mirroring; no AI-authenticity dead giveaways such as em dashes, buzzword soup, or template phrasing.
6. synthesis_quality: **exactly six** integrated sentences with optional composition themes (identity, platform/governance,
   partner motion, adoption motion, outcomes, implied credibility). **Not** a fixed S1–S5 slot checklist. Fewer than six sentences
   is a decisive failure (aligned with x2_exec_summary_sentence_count_6). **Concise alone is insufficient** when
   evidence_utilization lists unused high-confidence facts, repeated metric surfaces recur across sentences, or prose reads as stacked bullets.
   Credential facts are **optional** — omit vendor cert inventories (AWS/Databricks/Associate-level labels); one FSA rigor weave is allowed
   when X2 passes (C0.3 phase-1, not a cert dump). Penalize AWS+FSA stacks or certification laundry lists. For SVP IT strategy targets,
   penalize metric-inventory S3–S5 and reward connective emphasis on enterprise architecture, partner ecosystems, adoption motion, and
   multi-year IT strategy (JD targeting only — never JD-as-proof). Sentence 6 must integrate the arc, not recap prior sentences thinly.
   Keep the cadence human enough to pass a Head of Talent Acquisition screen without machine-generated tells.
7. evidence_utilization: penalize under-use of allowed_fact_packet when unused_fact_ids is non-empty and synthesis is thin; reward
   distinct evidence themes instead of reusing the same proof surface repeatedly.
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
   **For rows carrying `display_override_text`, the authorized substrate is the UNION of `claim_text` +
   `display_override_text`. Phrases from `display_override_text` are deterministically authorized — do NOT
   flag them as unsupported, inferential, or out-of-scope extensions; the generator was X2-required to emit
   them verbatim. When `graph_proof_refs.claim_support_graph_refs` is non-empty, also authorize prose that
   demonstrates those skill nodes; `graph_proof_refs.source_resume_files` is authoritative provenance.
   Cite a `factual_support` failure only when prose deviates from the full authorized union (claim +
   override + graph skill refs).**
2. executive_signal: SVP-level platform/governance/partner-motion synthesis, not bullet stacks.
3. resume_voice: credible executive prose; no recruiter filler, meta narration, or generic AI-company prose, and nothing that would fail a Head of Talent Acquisition screen.
4. ats_alignment_without_keyword_stuffing: JD shapes emphasis only; no JD-as-proof. When allowed facts
   lack EA/interop/federated proof IDs, penalize only if prose invents those themes or ignores documented
   gap_notes — not for absence alone when generation_law_digest requires gap_notes. Reward company-DNA specificity when the
   packet supports partner ecosystem, adoption motion, commercial fit, or a clean Head of Talent Acquisition screen.
5. anti_overfit: no unsupported metrics/credentials; no target company as candidate experience; no repeated metric inventory
   or company-name mirroring; no AI-authenticity dead giveaways such as em dashes, buzzword soup, or template phrasing.
   **`display_override_text` content is NOT an unsupported credential/metric — it is X2-authorized
   substrate. Do not cite override phrases (e.g. "FSA-chartered", "informing data governance and AI
   strategy at scale") as anti_overfit violations.**
6. synthesis_quality: **exactly six** integrated sentences (X2 band); reward connective SVP IT strategy emphasis when
   ledger-backed; penalize thin recap S6, repeated metric surfaces, and bullet-stacked prose. **Do not** soft-penalize
   credential/metric inventory, unused_fact_ids weave targets, or mechanism dumps when the mapped deterministic gate shows `"pass": true`.
   Keep the cadence human enough to pass a Head of Talent Acquisition screen without machine-generated tells.
7. evidence_utilization: when `x2_exec_summary_evidence_utilization` is `"pass": true`, unused_fact_ids are optional weave
   targets — not proof gaps. Penalize under-use only when that gate is `"pass": false` or synthesis is decisively thin;
   reward distinct evidence themes instead of the same metric repeated in multiple sentences.
8. deterministic_alignment: **only** penalize gates that show `"pass": false` in deterministic_gate_summary. Never cite
   retired five-part/S1–S5 arc mandates when gates passed.

Residual quality (always in scope — not closed by X2 alone):
- executive clarity, narrative coherence, commercial fit, usefulness, unsupported phrasing outside ledger scope.

Decisive failure triggers (must align with deterministic_gate_summary failures when cited):
- unsupported business metric or credential (when x2 gates failed or decisive unsupported claim)
- JD or briefing used as proof
- first-person narrative
- obvious rewrite recommendation that invents new claims
""".strip()

def _required_judge_output_schema_text() -> str:
    from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
        required_judge_output_dimension_block,
    )

    return f"""
Return ONLY one compact JSON object:
{{"score_scale":"0_to_5","score":0.0,"threshold":4.0,"pass":true,"decisive_failure":false,
 "findings":["short strings"],"cited_sentence_indexes":[1],
 "remediation_suggestions":[],"rationale":"one short paragraph",
 "fail_reasons":[],"unsupported_claims":[],"quality_flags":[],
 {required_judge_output_dimension_block()}}}
score_scale must be 0_to_5 or 0_to_1 with in-range score/threshold.
""".strip()


REQUIRED_JUDGE_OUTPUT_SCHEMA = _required_judge_output_schema_text()

_MAX_JUDGE_CLAIM_SUPPORT_SKILL_REFS = 6
_MAX_JUDGE_SOURCE_RESUME_FILES = 8
_MAX_JUDGE_EXECUTIVE_CAPABILITY_PHRASES = 3


def _bindings_by_fact_id(bindings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        fid = str(binding.get("fact_id") or "").strip()
        if not fid:
            continue
        out[fid] = binding
        base = fid.split("_metric_", 1)[0]
        out.setdefault(base, binding)
    return out


def _skill_source_resume_files_for_refs(
    skill_ids: list[str],
    *,
    repo_root: Any = None,
) -> list[str]:
    if not skill_ids:
        return []
    from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph

    graph = load_augmented_skills_graph(repo_root=repo_root)
    skill_rows = {
        str(row.get("skill_id") or "").strip(): row
        for row in (graph.get("skill_rows") or [])
        if isinstance(row, dict) and str(row.get("skill_id") or "").strip()
    }
    files: list[str] = []
    seen: set[str] = set()
    for sid in skill_ids:
        row = skill_rows.get(str(sid).strip())
        if not row:
            continue
        for raw in row.get("source_resume_files") or []:
            path = str(raw).strip()
            if path and path not in seen:
                seen.add(path)
                files.append(path)
            if len(files) >= _MAX_JUDGE_SOURCE_RESUME_FILES:
                return files
    return files


def enrich_allowed_fact_packet_for_judges(
    plan_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    *,
    graph_bindings: list[dict[str, Any]] | None = None,
    repo_root: Any = None,
) -> list[dict[str, Any]]:
    """Include metric-derivative rows AND attach C0 display-override text so X1D judges see the same fact substrate as X2/PROVIDER_MODEL.

    Without ``display_override_text``, judges grade against the raw ``claim_text`` and
    flag the authorized override phrases as unsupported extensions, producing structural
    soft-fail loops (closes Bug:ExecSummaryJudgeDisplayOverrideInvisible,
    plan exec-summary-judge-display-override-parity-7c3e8a).
    """
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        FACT_C0_DISPLAY_OVERRIDES,
    )
    from apps_rg.runtime.sections.graph_evidence_contract import metric_derivative_fact_id

    bindings_by_fact = _bindings_by_fact_id(list(graph_bindings or []))
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
    for row in out:
        fid = str(row.get("fact_id") or "").strip()
        if not fid:
            continue
        base = fid.split("_metric_")[0]
        override = str(FACT_C0_DISPLAY_OVERRIDES.get(fid, "") or "").strip()
        if not override and base != fid:
            override = str(FACT_C0_DISPLAY_OVERRIDES.get(base, "") or "").strip()
        if override:
            row["display_override_text"] = override
            row["display_substrate_authority"] = "union_claim_text_and_display_override_text"
        preferred = str(row.get("preferred_c0_display_text") or "").strip()
        if preferred:
            row["preferred_c0_display_text"] = preferred
        binding = bindings_by_fact.get(fid) or bindings_by_fact.get(base)
        if binding:
            claim_refs = list(
                binding.get("claim_support_graph_refs")
                or binding.get("graph_node_refs")
                or []
            )[:_MAX_JUDGE_CLAIM_SUPPORT_SKILL_REFS]
            capability_phrases = list(binding.get("executive_capability_phrases") or [])[
                :_MAX_JUDGE_EXECUTIVE_CAPABILITY_PHRASES
            ]
            source_files = _skill_source_resume_files_for_refs(claim_refs, repo_root=repo_root)
            if claim_refs or source_files:
                row["graph_proof_refs"] = {
                    "claim_support_graph_refs": claim_refs,
                    "source_resume_files": source_files,
                }
            if capability_phrases:
                row["executive_capability_phrases"] = capability_phrases
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
    mechanism_ok, mechanism_reason = check_exec_summary_no_mechanism_inventory(resume_display_text)
    bounds_ok, bounds_reason = check_exec_summary_paragraph_max_words(
        resume_display_text, parsed_output
    )
    meta_ok, meta_reason = check_exec_summary_meta_filler_patterns(resume_display_text)
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        resume_display_text, parsed_output
    )
    from apps_rg.runtime.validators.executive_summary_x2 import check_synthesis_quality

    synthesis_ok, synthesis_reason = check_synthesis_quality(resume_display_text)
    opener_ok, opener_reason = check_exec_summary_mechanical_opener_stack(resume_display_text)
    transition_ok, transition_reason = check_exec_summary_robotic_transition_stack(resume_display_text)
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
            "pass": mechanism_ok,
            "detail": mechanism_reason or "ok",
        },
        "x2_exec_summary_meta_filler_zero": {
            "pass": meta_ok,
            "detail": meta_reason or "ok",
        },
        "x2_exec_summary_evidence_utilization": {
            "pass": util_ok,
            "detail": util_reason or "ok",
        },
        "x2_executive_summary_synthesis_quality": {
            "pass": synthesis_ok,
            "detail": synthesis_reason or "ok",
        },
        "x2_exec_summary_mechanical_opener_stack_zero": {
            "pass": opener_ok,
            "detail": opener_reason or "ok",
        },
        "x2_exec_summary_robotic_transition_stack_zero": {
            "pass": transition_ok,
            "detail": transition_reason or "ok",
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


def gate_id_excluded_from_judge_snapshot(gate_id: str) -> bool:
    """Post-X2 wiring gates must not mutate the GRADE_ONLY packet judges share."""
    from apps_rg.runtime.validators.executive_summary_x2 import POST_X2_X1D_WIRING_GATE_IDS

    gid = str(gate_id or "").strip()
    if not gid:
        return True
    if gid in POST_X2_X1D_WIRING_GATE_IDS:
        return True
    return gid.startswith("x2_x1d_")


def build_deterministic_gate_summary_from_x2_gates(
    x2_gates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Authoritative X2 snapshot for post-X2 judge refresh (content gates only; excludes x1d wiring)."""
    summary: dict[str, Any] = {}
    for gate in x2_gates:
        if not isinstance(gate, dict):
            continue
        gate_id = str(gate.get("gate_id") or "").strip()
        if not gate_id or gate_id_excluded_from_judge_snapshot(gate_id):
            continue
        detail = gate.get("failure_reason")
        if detail is None:
            detail = gate.get("observed_value")
        summary[gate_id] = {
            "pass": bool(gate.get("pass")),
            "detail": str(detail if detail is not None else "ok"),
        }
    if summary:
        summary["product_shape_note"] = {
            "pass": True,
            "detail": f"judge_snapshot_content_gates={len(summary)}",
        }
    return summary


def reconcile_judge_result_against_deterministic_gate_closures(
    result: dict[str, Any],
    deterministic_gate_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    """Suppress only findings mapped to passed deterministic gates; emit reconciliation receipt."""
    if not isinstance(result, dict) or not isinstance(deterministic_gate_summary, dict):
        return result

    original_score = result.get("score")
    original_verdict = bool(result.get("pass"))
    original_findings = [str(f) for f in (result.get("findings") or []) if str(f).strip()]

    from apps_rg.runtime.judges.executive_summary_x1d_gate_closure_map import (
        RECONCILIATION_POLICY_VERSION,
        finding_is_contract_invalid_under_gate_closures,
    )

    suppressed: list[dict[str, Any]] = []
    preserved: list[str] = []
    for finding in original_findings:
        invalid, gate_id, evidence_ref = finding_is_contract_invalid_under_gate_closures(
            finding, deterministic_gate_summary
        )
        if invalid and gate_id and evidence_ref:
            suppressed.append(
                {
                    "finding": finding,
                    "finding_code": None,
                    "suppressing_gate_id": gate_id,
                    "suppressing_gate_pass_evidence_ref": evidence_ref,
                }
            )
        else:
            preserved.append(finding)

    out = dict(result)
    out["findings"] = preserved
    if suppressed:
        out["reconciliation_receipt"] = {
            "original_score": original_score,
            "original_verdict": original_verdict,
            "original_findings": original_findings,
            "suppressed_findings": suppressed,
            "preserved_findings": preserved,
            "final_score": out.get("score"),
            "final_verdict": out.get("pass"),
            "reconciliation_policy_version": RECONCILIATION_POLICY_VERSION,
        }

    if not preserved and suppressed:
        out["decisive_failure"] = False
        try:
            score = float(out.get("score", 0.0))
            threshold = float(out.get("threshold", 4.0))
            if score < threshold:
                out["score"] = threshold
                out["pass"] = True
                if isinstance(out.get("reconciliation_receipt"), dict):
                    out["reconciliation_receipt"]["final_score"] = out["score"]
                    out["reconciliation_receipt"]["final_verdict"] = out["pass"]
        except (TypeError, ValueError):  # guardian: allow-silent-swallow -- P2 burndown: optional score coercion
            pass
    elif preserved:
        out["pass"] = bool(out.get("pass")) and not bool(out.get("decisive_failure"))
        if isinstance(out.get("reconciliation_receipt"), dict):
            out["reconciliation_receipt"]["final_score"] = out.get("score")
            out["reconciliation_receipt"]["final_verdict"] = out.get("pass")

    return out


def _strip_retired_criteria_findings(findings: list[str]) -> tuple[list[str], list[str]]:
    """Remove legacy SRFS slot findings that must not drive fail (Gemini/OpenAI/Anthropic)."""
    preserved: list[str] = []
    stripped: list[str] = []
    for finding in findings:
        text = str(finding).strip()
        if not text:
            continue
        lower = text.lower()
        if any(frag in lower for frag in _RETIRED_JUDGE_CRITERIA_FRAGMENTS):
            stripped.append(text)
        else:
            preserved.append(text)
    return preserved, stripped


def reconcile_grade_only_judge_result(
    result: dict[str, Any],
    deterministic_gate_summary: dict[str, Any] | None,
) -> dict[str, Any]:
    """Retired-criteria reconcile, then deterministic gate-closure reconcile."""
    if not isinstance(result, dict):
        return result
    out = dict(result)
    original_findings = [str(f) for f in (out.get("findings") or []) if str(f).strip()]
    preserved, stripped_retired = _strip_retired_criteria_findings(original_findings)
    if stripped_retired:
        out["findings"] = preserved
        receipt = dict(out.get("reconciliation_receipt") or {})
        receipt["stripped_retired_criteria_findings"] = stripped_retired
        receipt["original_findings"] = original_findings
        out["reconciliation_receipt"] = receipt
        if not preserved and out.get("decisive_failure"):
            out["decisive_failure"] = False
        if not preserved:
            try:
                score = float(out.get("score", 0.0))
                threshold = float(out.get("threshold", 4.0))
                if score < threshold:
                    out["score"] = threshold
                    out["pass"] = True
                    receipt["final_score"] = out["score"]
                    receipt["final_verdict"] = out["pass"]
                    out["reconciliation_receipt"] = receipt
            except (TypeError, ValueError):  # guardian: allow-silent-swallow -- optional score coercion
                pass
    if isinstance(deterministic_gate_summary, dict):
        gate_entries = [
            v for v in deterministic_gate_summary.values() if isinstance(v, dict) and "pass" in v
        ]
        if gate_entries and all(bool(v.get("pass")) for v in gate_entries):
            blob = json.dumps(out, ensure_ascii=False).lower()
            if any(frag in blob for frag in _RETIRED_JUDGE_CRITERIA_FRAGMENTS):
                if out.get("decisive_failure"):
                    out["decisive_failure"] = False
                    findings = list(out.get("findings") or [])
                    findings.append(
                        "Reconciled: judge cited retired five-part/S1-S5 criteria; "
                        "deterministic_gate_summary all pass."
                    )
                    out["findings"] = findings
    return reconcile_judge_result_against_deterministic_gate_closures(
        out, deterministic_gate_summary
    )


def build_canonical_judge_contract(packet: dict[str, Any]) -> dict[str, Any]:
    """Stable canonical contract layer (transport wrappers may differ)."""
    return {
        "judge_packet_version": packet.get("judge_packet_version"),
        "section": packet.get("section"),
        "judge_task": packet.get("judge_task"),
        "grading_instruction": packet.get("grading_instruction") or GRADE_ONLY_INSTRUCTION,
        "proof_boundary": packet.get("proof_boundary") or {},
        "deterministic_gate_summary": packet.get("deterministic_gate_summary") or {},
        "graph_binding_materiality_summary": packet.get("graph_binding_materiality_summary") or {},
        "rubric": packet.get("rubric") or GRAPH_ONLY_GRADE_ONLY_RUBRIC,
        "required_output_schema": packet.get("required_output_schema") or REQUIRED_JUDGE_OUTPUT_SCHEMA,
        "judge_rubric_mode": packet.get("judge_rubric_mode"),
        "generation_law_digest": packet.get("generation_law_digest"),
        "dimension_gate_map": packet.get("dimension_gate_map") or dimension_gate_map(),
    }


def judge_contract_hash(packet: dict[str, Any]) -> str:
    canonical = build_canonical_judge_contract(packet)
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


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
    graph_targeting_capsule: dict[str, Any] | None = None,
    graph_bindings: list[dict[str, Any]] | None = None,
    proof_pool_metadata: dict[str, Any] | None = None,
    graph_binding_materiality_summary: dict[str, Any] | None = None,
    repo_root: Any = None,
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
        graph_bindings=graph_bindings,
        repo_root=repo_root,
    )
    from apps_rg.runtime.graph_skills_utilization_scorer import (
        build_graph_binding_materiality_summary,
    )

    cited_fact_ids = _collect_source_fact_ids(claim_ledger)
    graph_binding_materiality_summary = build_graph_binding_materiality_summary(
        section_id="executive_summary",
        proof_pool_metadata=proof_pool_metadata,
        candidate_output={
            "resume_display_text": resume_display_text,
            "source_fact_ids": cited_fact_ids,
        },
        claim_ledger=claim_ledger,
        parsed_output=parsed_output,
        runtime_payload={
            "section_id": "executive_summary",
            "allowed_fact_ids": sorted(allowed_fact_ids),
            "graph_targeting_for_pa": graph_targeting_capsule or {},
        },
        graph_bindings=graph_bindings or [],
    )
    unused_fact_ids = collect_unused_allowed_fact_ids(claim_ledger, allowed_fact_ids)
    from apps_rg.runtime.validators.executive_summary_x2 import (
        check_judge_packet_display_override_parity,
    )

    parity_ok, parity_reason = check_judge_packet_display_override_parity(
        judge_allowed_fact_packet=judge_allowed_packet,
        cited_fact_ids=cited_fact_ids,
    )
    if isinstance(gate_summary, dict):
        gate_summary = dict(gate_summary)
        gate_summary["x2_executive_summary_judge_packet_display_override_parity"] = {
            "pass": parity_ok,
            "detail": parity_reason or "ok",
        }
    materiality = dict(graph_binding_materiality_summary or {})
    if not materiality and isinstance(proof_pool_metadata, dict):
        from apps_rg.runtime.graph_skills_utilization_scorer import (
            build_graph_binding_materiality_summary,
        )

        materiality = build_graph_binding_materiality_summary(
            section_id="executive_summary",
            proof_pool_metadata=proof_pool_metadata,
            candidate_output={
                "resume_display_text": resume_display_text,
                "source_fact_ids": cited_fact_ids,
            },
            claim_ledger=claim_ledger,
            parsed_output=parsed_output,
        )
    return {
        "judge_packet_version": JUDGE_PACKET_VERSION,
        "section": "executive_summary",
        "judge_task": "GRADE_ONLY",
        "generation_law_digest": generation_law_digest_text(),
        "dimension_gate_map": dimension_gate_map(),
        "candidate_output": {
            "resume_display_text": resume_display_text,
            "claim_ledger": claim_ledger,
            "source_fact_ids": _collect_source_fact_ids(claim_ledger),
        },
        "allowed_fact_packet": judge_allowed_packet,
        "allowed_fact_ids": sorted(allowed_fact_ids),
        "graph_binding_materiality_summary": graph_binding_materiality_summary,
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
            **(
                {"graph_targeting_capsule": dict(graph_targeting_capsule)}
                if isinstance(graph_targeting_capsule, dict)
                else {}
            ),
        },
        "proof_boundary": {
            "jd_is_targeting_context_only": True,
            "briefing_is_targeting_context_only": True,
            "claims_must_be_supported_by_allowed_fact_packet": True,
            "judges_must_not_rewrite": True,
            "judges_must_not_generate_replacement_summary": True,
            "metadata_only_graph_context_is_insufficient": True,
        },
        "graph_binding_materiality_summary": materiality,
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


def write_canonical_judge_contract_artifact(path: Path, packet: dict[str, Any]) -> str:
    """Persist canonical contract + stable digest for transport-parity receipts."""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "judge_contract_hash": judge_contract_hash(packet),
        "canonical_judge_contract": build_canonical_judge_contract(packet),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(body, f, indent=2, ensure_ascii=False, default=str)
    return str(path)


def write_executive_summary_judge_packet(path: Path, packet: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    enriched = dict(packet)
    enriched["judge_packet_hash"] = judge_packet_hash(packet)
    enriched["judge_contract_hash"] = judge_contract_hash(packet)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False, default=str)
    write_canonical_judge_contract_artifact(path.parent / "canonical_judge_contract.json", packet)
    return str(path)


def _evidence_utilization_prompt_block(packet: dict[str, Any]) -> str:
    summary = packet.get("deterministic_gate_summary") or {}
    util = summary.get("x2_exec_summary_evidence_utilization")
    eu = packet.get("evidence_utilization") or {}
    if isinstance(util, dict) and util.get("pass") and (eu.get("unused_fact_ids") or []):
        return (
            "EVIDENCE_UTILIZATION (X2 gate pass:true — unused_fact_ids are optional weave targets, "
            "not defects or proof gaps; do not penalize under-use):"
        )
    return "EVIDENCE_UTILIZATION (deterministic — align with deterministic_gate_summary):"


def render_judge_prompt_from_packet(packet: dict[str, Any]) -> str:
    """Render judge user message from JudgePacket — never the generator compiled_prompt."""
    parts = [
        packet.get("grading_instruction") or GRADE_ONLY_INSTRUCTION,
        "",
        f"JUDGE_TASK: {packet.get('judge_task', 'GRADE_ONLY')}",
        f"SECTION: {packet.get('section', 'executive_summary')}",
        f"JUDGE_CONTRACT_HASH: {judge_contract_hash(packet)}",
        "",
        "PROOF_BOUNDARY:",
        json.dumps(packet.get("proof_boundary") or {}, indent=2),
        "",
        "GRAPH_BINDING_MATERIALITY_SUMMARY:",
        json.dumps(packet.get("graph_binding_materiality_summary") or {}, indent=2),
        "",
        "DETERMINISTIC_GATE_SUMMARY (AUTHORITATIVE — do not contradict pass=true gates):",
        json.dumps(packet.get("deterministic_gate_summary") or {}, indent=2),
        "",
        "GENERATION_LAW_DIGEST (aligned with L2 I0 — judges do not receive full E0/I0):",
        packet.get("generation_law_digest") or generation_law_digest_text(),
        "",
        "DIMENSION_GATE_MAP:",
        json.dumps(packet.get("dimension_gate_map") or dimension_gate_map(), indent=2),
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
        _evidence_utilization_prompt_block(packet),
        json.dumps(eu if (eu := packet.get("evidence_utilization")) else {}, indent=2),
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
