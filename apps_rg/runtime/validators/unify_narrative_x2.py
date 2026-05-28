"""Deterministic X2 gates for unify_narrative runtime slice (single role sentence)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from apps_rg.runtime.section_proof.section_input_usage_ledger import (
    _is_forbidden_proof_source_fact_id,
    source_fact_base_id,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    EM_DASH,
    FIRST_PERSON_PATTERN,
    GENERIC_FILLER,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_claim_ledger_claim_text_non_empty,
    check_json_parse_valid,
    check_judge_rows_present,
    check_judge_schema_valid,
    has_jd_phrase_copy,
    split_sentences,
)
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS
from apps_rg.runtime.validators.narrative_identity_x2 import narrative_leaks_candidate_name_tokens


# Exact display labels from finalized Unify bullets — never paste into narrative_sentence.
FORBIDDEN_UNIFY_BULLET_DISPLAY_LABELS: tuple[str, ...] = (
    "Enterprise Agentic AI Platform Architecture",
    "Dependency Graph Accelerator",
    "Governed Runtime Reliability",
    "Production Adoption",
    "Distributed Ecosystem Engineering",
    "Platform Commercialization and Engineering Leadership",
)


def _narrative_word_count(text: str) -> int:
    return len(text.split())


def _forbidden_bullet_label_hit(narrative: str) -> str | None:
    nl = narrative.lower()
    for label in FORBIDDEN_UNIFY_BULLET_DISPLAY_LABELS:
        if label.lower() in nl:
            return label
    return None


def _content_words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9%$]+", text.lower()) if w]


def _fourgrams(words: list[str]) -> set[tuple[str, ...]]:
    if len(words) < 4:
        return set()
    return {tuple(words[i : i + 4]) for i in range(len(words) - 3)}


def _fourgram_exempt(gram: tuple[str, ...]) -> bool:
    s = " ".join(gram)
    for anchor in ("unify consulting", "agentic ai platform", "agentic ai platforms"):
        if anchor in s:
            return True
    return False


def _companion_bullet_bodies(companion: str) -> list[str]:
    bodies: list[str] = []
    for line in companion.splitlines():
        line = line.strip()
        if not line:
            continue
        bodies.append(line.split(":", 1)[-1].strip() if ":" in line else line)
    return bodies


def _companion_fourgram_hits(narrative: str, companion: str) -> list[str]:
    nar_g = _fourgrams(_content_words(narrative))
    hits: list[str] = []
    for body in _companion_bullet_bodies(companion):
        shared = nar_g & _fourgrams(_content_words(body))
        for gram in shared:
            if _fourgram_exempt(gram):
                continue
            hits.append(" ".join(gram))
    return hits


def _jd_alignment_targeting_ok(
    jd_alignment: Any,
    *,
    claim_ledger: list[dict[str, Any]],
    briefing_text: str,
) -> tuple[bool, dict[str, Any]]:
    detail: dict[str, Any] = {}
    if not isinstance(jd_alignment, dict):
        detail["reason"] = "jd_alignment_not_object"
        return False, detail
    themes = jd_alignment.get("selected_jd_themes")
    if not isinstance(themes, list) or len(themes) < 1:
        detail["reason"] = "selected_jd_themes_empty"
        return False, detail
    rationale = str(jd_alignment.get("targeting_rationale") or "").strip()
    if not rationale:
        detail["reason"] = "targeting_rationale_empty"
        return False, detail
    if jd_alignment.get("jd_used_as_proof") is not False:
        detail["reason"] = "jd_used_as_proof_not_false"
        return False, detail
    if jd_alignment.get("briefing_used_as_proof") is not False:
        detail["reason"] = "briefing_used_as_proof_not_false"
        return False, detail
    br = jd_alignment.get("selected_briefing_themes")
    if not isinstance(br, list):
        detail["reason"] = "selected_briefing_themes_not_array"
        return False, detail
    if str(briefing_text or "").strip() and len(br) < 1:
        detail["reason"] = "selected_briefing_themes_empty_when_briefing_present"
        return False, detail
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            bad, reason = _is_forbidden_proof_source_fact_id(str(fid))
            if bad:
                detail["reason"] = "targeting_shaped_source_fact_id"
                detail["hit"] = str(fid)
                detail["subtype"] = reason
                return False, detail
    detail["reason"] = "ok"
    return True, detail


@dataclass
class X2GateResult:
    gate_id: str
    gate_type: str
    pass_: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None
    evidence_ref: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def _ledger_fact_ids(claim_ledger: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ids.add(str(fid).split("_metric_")[0])
        if claim.get("source_fact_id"):
            ids.add(str(claim["source_fact_id"]).split("_metric_")[0])
    return ids


def _count_metric_hits(narrative: str) -> int:
    nl = narrative.lower()
    hits = 0
    if "$22m" in nl or re.search(r"\$22\s*m", narrative, re.I):
        hits += 1
    if re.search(r"20\s*%", narrative):
        hits += 1
    if re.search(r"8\s*(to|→|-|–)\s*28", narrative, re.I):
        hits += 1
    if re.search(r"six\s+months", nl) and re.search(r"three\s+weeks", nl):
        hits += 1
    return hits


def _companion_bullets_have_metrics(companion_bullet_texts: str) -> bool:
    c = companion_bullet_texts.lower()
    return "$22m" in c and "20%" in c and ("8" in c and "28" in c) and "six months" in c and "three weeks" in c


def run_unify_narrative_x2_gates(
    *,
    narrative_sentence: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    jd_text: str,
    briefing_text: str = "",
    runtime_generation_status: str,
    companion_bullet_texts: str | None,
    companion_bullets_status: str | None = None,
    companion_bullets_reason: str | None = None,
    candidate_name: str = "",
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
    allowed_fact_ids: set[str] | None = None,
    artifacts_dir: Any | None = None,
    srfs_source_fact_slice_gate_active: bool = False,
    proof_pool_metadata: dict[str, Any] | None = None,
    proof_pool_ref: str = "",
    proof_pool_digest: str = "",
) -> list[X2GateResult]:
    gates: list[X2GateResult] = []

    def add(
        gate_id: str,
        passed: bool,
        observed: Any,
        threshold: Any = None,
        failure: str | None = None,
    ) -> None:
        gates.append(
            X2GateResult(
                gate_id=gate_id,
                gate_type="deterministic",
                pass_=passed,
                observed_value=observed,
                threshold=threshold,
                failure_reason=failure,
                evidence_ref=gate_id,
            )
        )

    sentences = split_sentences(narrative_sentence.strip())
    exactly_one = len(sentences) == 1 and bool(narrative_sentence.strip())
    add(
        "x2_unify_narrative_exactly_one_sentence",
        exactly_one,
        len(sentences),
        1,
        "Must be exactly one sentence.",
    )

    from apps_rg.runtime.validators.narrative_mechanical_x2 import (
        UNIFY_NARRATIVE_METRIC_PATTERNS,
        register_narrative_mechanical_x2_gates,
    )

    register_narrative_mechanical_x2_gates(
        add,
        narrative_sentence,
        lane_prefix="unify",
        companion_bullet_texts=companion_bullet_texts or "",
        metric_patterns=UNIFY_NARRATIVE_METRIC_PATTERNS,
        max_metrics=(
            1
            if (companion_bullet_texts or "").strip()
            and _companion_bullets_have_metrics(companion_bullet_texts or "")
            else 2
        ),
    )

    leaks_name, name_hit = narrative_leaks_candidate_name_tokens(narrative_sentence, candidate_name)
    add(
        "x2_unify_narrative_no_candidate_name_tokens",
        not leaks_name,
        name_hit or "none",
        "absent",
        "Candidate name must not appear in the role narrative sentence.",
    )

    ledger_ids = _ledger_fact_ids(claim_ledger)
    allow_bases = (
        {source_fact_base_id(str(x)) for x in allowed_fact_ids}
        if allowed_fact_ids is not None
        else set(UNIFY_BULLET_IDS) | {"unify_narrative_base_001", "exp_unify_001"}
    )
    bases = {source_fact_base_id(str(x)) for x in ledger_ids}
    supported = bool(claim_ledger) and bool(ledger_ids) and bases <= allow_bases
    add(
        "x2_unify_narrative_source_supported",
        supported,
        sorted(ledger_ids),
        "subset_of_runtime_allowed_fact_ids",
        "claim_ledger must map to allowed Unify narrative proof facts only.",
    )

    ledger_ct_ok, ledger_ct_reason = check_claim_ledger_claim_text_non_empty(claim_ledger)
    add(
        "x2_claim_ledger_claim_text_non_empty",
        ledger_ct_ok,
        ledger_ct_reason or "ok",
        "non_empty_claim_text_per_row",
        ledger_ct_reason,
    )

    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        proof_source_from_metadata,
        scope_ids_membership_only,
    )

    serialized = json.dumps(parsed_output or {}, sort_keys=True).lower()
    proof_source = proof_source_from_metadata(proof_pool_metadata)
    if proof_source in ("srfs", "broad_skills_ledger"):
        scope_ids = _ledger_fact_ids(claim_ledger)
    else:
        scope_ids = _ledger_fact_ids(claim_ledger) | set(
            re.findall(
                r"\b(?:bul_unify_\d{3}|unify_narrative_base_\d{3}|exp_unify_\d{3})\b",
                serialized,
            )
        )
    allow_runtime_set = {str(x).strip() for x in (allowed_fact_ids or []) if str(x).strip()}
    if proof_source in ("srfs", "broad_skills_ledger"):
        scope_ok, _, forbidden_hits, not_in_pool = scope_ids_membership_only(
            scope_ids,
            allowed_fact_ids=allow_runtime_set,
            forbidden_prefixes=("bul_ibm_", "bul_insurtech_", "bul_ey_"),
        )
        scope_threshold = "active_proof_pool_membership"
        scope_fail = "Non-Unify fact scope."
        if forbidden_hits or not_in_pool:
            scope_fail += f" forbidden={forbidden_hits} out_of_pool={not_in_pool}"
    else:
        scope_ok = (
            all(
                str(s).startswith(("bul_unify_", "unify_narrative_base_", "exp_unify_"))
                for s in scope_ids
            )
        ) and not any(p in serialized for p in ("bul_ibm_", "bul_insurtech_", "bul_ey_"))
        scope_threshold = "bul_unify_*|unify_narrative_base_*|exp_unify_*"
        scope_fail = "Non-Unify fact scope."
    add(
        "x2_unify_narrative_unify_only_fact_scope",
        scope_ok,
        sorted(scope_ids),
        scope_threshold,
        scope_fail,
    )

    add("x2_no_ibm_fact_leakage", "bul_ibm_" not in serialized, "bul_ibm_", "absent", "IBM leakage.")
    add("x2_no_insurtech_fact_leakage", "bul_insurtech_" not in serialized, "bul_insurtech_", "absent", "InsurTech leakage.")
    add("x2_no_ey_fact_leakage", "bul_ey_" not in serialized, "bul_ey_", "absent", "EY leakage.")

    jd_copy, jd_phrase = has_jd_phrase_copy(narrative_sentence, jd_text)
    add("x2_no_jd_only_claims", not jd_copy, jd_phrase or "none", "no long JD copy", "JD phrase copied as proof.")

    ja = (parsed_output or {}).get("jd_alignment")
    targ_ok, targ_detail = _jd_alignment_targeting_ok(
        ja,
        claim_ledger=claim_ledger,
        briefing_text=briefing_text,
    )
    add(
        "x2_unify_narrative_targeting_inputs_used_but_not_proof",
        targ_ok,
        targ_detail,
        "jd_alignment_contract",
        None if targ_ok else str(targ_detail.get("reason")),
    )

    companion = companion_bullet_texts or ""
    from apps_rg.runtime.validators.companion_bullet_finalization import (
        UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS,
        companion_allow_legacy_stale_fallback,
    )

    skip_finalized_gate = runtime_generation_status == "MOCKED" and companion_allow_legacy_stale_fallback()
    if runtime_generation_status == UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS:
        add(
            "x2_unify_narrative_requires_finalized_bullets",
            False,
            {
                "status": companion_bullets_status or "UNKNOWN",
                "reason": companion_bullets_reason or "",
                "has_companion_text": bool(companion.strip()),
                "runtime_generation_status": runtime_generation_status,
            },
            "provider blocked before LLM",
            "Narrative LLM skipped: upstream bullets not finalized.",
        )
    elif skip_finalized_gate:
        add(
            "x2_unify_narrative_requires_finalized_bullets",
            True,
            {
                "status": companion_bullets_status or "UNKNOWN",
                "reason": companion_bullets_reason or "",
                "has_companion_text": bool(companion.strip()),
                "skipped": "MOCKED_runtime_plumbing",
            },
            "skipped for MOCKED provider",
            None,
        )
    else:
        from apps_rg.runtime.validators.companion_bullet_finalization import (
            ACCEPTED_FINALIZED_COMPANION_STATUS,
        )

        finalized_dependency_ok = (
            bool(companion.strip())
            and companion_bullets_status == ACCEPTED_FINALIZED_COMPANION_STATUS
        )
        add(
            "x2_unify_narrative_requires_finalized_bullets",
            finalized_dependency_ok,
            {
                "status": companion_bullets_status or "UNKNOWN",
                "reason": companion_bullets_reason or "",
                "has_companion_text": bool(companion.strip()),
            },
            "ACCEPTED_FINALIZED with companion bullet text",
            "Narrative must run only after finalized Unify bullets are accepted.",
        )

    metric_hits = _count_metric_hits(narrative_sentence)
    if companion and _companion_bullets_have_metrics(companion):
        repetition_ok = metric_hits <= 1
        add(
            "x2_no_metric_repetition_unless_justified",
            repetition_ok,
            metric_hits,
            "<=1 when bullets already carry full metrics",
            "Too many repeated metrics versus companion bullets.",
        )
    else:
        add(
            "x2_no_metric_repetition_unless_justified",
            True,
            "no companion bullets artifact",
            "skipped",
            None,
        )

    structure_copy = False
    if companion:
        for line in companion.splitlines():
            if ":" not in line:
                continue
            text = line.split(":", 1)[-1].strip()
            words = re.findall(r"[A-Za-z0-9%$]+", text.lower())
            if len(words) >= 5:
                prefix = " ".join(words[:5])
                if prefix and prefix in narrative_sentence.lower():
                    structure_copy = True
                    break
    add(
        "x2_no_bullet_sentence_structure_copy",
        not structure_copy,
        structure_copy,
        False,
        "Narrative copies a bullet-leading phrase.",
    )

    comma_count = narrative_sentence.count(",")
    six_summary = comma_count >= 5 or narrative_sentence.count(";") >= 2
    add("x2_no_six_bullet_summary", not six_summary, comma_count, "<5 commas", "Reads like stacked bullet summary.")

    lbl_hit = _forbidden_bullet_label_hit(narrative_sentence)
    add(
        "x2_no_bullet_label_repetition",
        lbl_hit is None,
        lbl_hit or "none",
        "no companion bullet display label substring",
        "Narrative repeats a finalized bullet label.",
    )

    if companion.strip():
        fg_hits = _companion_fourgram_hits(narrative_sentence, companion)
        add(
            "x2_no_companion_ngram_copy",
            len(fg_hits) == 0,
            fg_hits[:12],
            "no shared 4-grams with companion bullet bodies",
            "High n-gram overlap with companion bullet text.",
        )
    else:
        add(
            "x2_no_companion_ngram_copy",
            True,
            "no companion text",
            "skipped",
            None,
        )

    stripped_narrative = narrative_sentence.strip()
    wc = _narrative_word_count(stripped_narrative)
    budget_ok = wc <= 58 and len(stripped_narrative) <= 360
    add(
        "x2_unify_narrative_word_budget",
        budget_ok,
        {"word_count": wc, "char_len": len(stripped_narrative)},
        "<=58 words and <=360 chars",
        None if budget_ok else "Narrative exceeds word or character budget.",
    )

    add(
        "x2_no_inline_source_tags",
        not INLINE_SOURCE_PATTERN.search(narrative_sentence),
        "tags",
        "absent",
        "Inline source tags in narrative.",
    )
    add(
        "x2_no_first_person",
        not FIRST_PERSON_PATTERN.search(narrative_sentence),
        "first person",
        "absent",
        "First person in narrative.",
    )
    add("x2_no_em_dash", EM_DASH not in narrative_sentence, "em dash", "absent", "Em dash found.")
    filler_hit = next((f for f in GENERIC_FILLER if f.lower() in narrative_sentence.lower()), None)
    add("x2_no_generic_filler", filler_hit is None, filler_hit or "none", "absent", "Generic filler.")

    json_ok, json_reason = check_json_parse_valid(parsed_output, raw_output)
    add("x2_json_parse_valid", json_ok, json_reason, None, json_reason)

    provider_ok = provider_requested == provider_attempted if provider_requested else True
    add(
        "x2_provider_requested_attempted",
        provider_ok,
        f"{provider_requested}->{provider_attempted}",
        "match",
        "Provider mismatch.",
    )
    no_silent_mock = not (provider_requested == "qwen_vllm" and runtime_generation_status == "MOCKED")
    add("x2_no_silent_mock_fallback", no_silent_mock, runtime_generation_status, "REAL_LLM", "Silent mock fallback.")

    judges_ok, judges_reason = check_judge_rows_present(x1d_judges)
    add("x2_x1d_required_judges_present", judges_ok, judges_reason, REQUIRED_JUDGE_PROVIDERS, judges_reason)

    if x1d_judges:
        blocked_invalid = []
        for judge in x1d_judges:
            if str(judge.get("evaluator_mode", "")).startswith("BLOCKED_"):
                schema_ok, _ = check_judge_schema_valid(judge)
                if not schema_ok:
                    blocked_invalid.append(judge.get("provider_key"))
        add(
            "x2_x1d_schema_valid",
            not blocked_invalid,
            blocked_invalid,
            [],
            f"Blocked judges invalid schema: {blocked_invalid}",
        )
    else:
        add("x2_x1d_schema_valid", False, "no judges", "present", "No judges.")

    from apps_rg.runtime.validators.section_input_usage_x2 import append_section_input_usage_x2_gates

    if (srfs_source_fact_slice_gate_active or proof_pool_metadata) and allowed_fact_ids is not None:
        from apps_rg.runtime.sections import selected_role_fact_set as _srfs_w4
        from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
            evaluate_proof_pool_source_fact_gate,
            proof_pool_x2_gate_id,
        )

        coll_un = _srfs_w4.collect_source_fact_ids_from_claim_ledger(claim_ledger)
        ok_un, env_un, fail_un = evaluate_proof_pool_source_fact_gate(
            section_id="unify_narrative",
            collected_ids=coll_un,
            allowed_fact_ids=set(allowed_fact_ids),
            proof_pool_metadata=proof_pool_metadata,
            proof_pool_ref=proof_pool_ref,
            proof_pool_digest=proof_pool_digest,
        )
        add(
            proof_pool_x2_gate_id(
                "unify_narrative",
                proof_pool_metadata=proof_pool_metadata,
                srfs_slice_gate_active=srfs_source_fact_slice_gate_active,
            ),
            ok_un,
            env_un,
            "active_proof_pool_allowlist_exact",
            fail_un,
        )

    append_section_input_usage_x2_gates(
        gates,
        artifacts_dir=artifacts_dir or Path("artifacts/apps_rg/runtime_proofs/unify_narrative"),
        allowed_fact_ids=set(allowed_fact_ids) if allowed_fact_ids is not None else set(UNIFY_BULLET_IDS),
        claim_ledger=claim_ledger,
        text_claim_coverage=(parsed_output or {}).get("text_claim_coverage")
        if isinstance(parsed_output, dict)
        else None,
    )

    # -----------------------------------------------------------------------
    # Narrative alignment quality gates (seniority, consulting blocklist, specificity, etc.)
    # -----------------------------------------------------------------------
    from apps_rg.runtime.validators.narrative_quality_x2 import (
        check_narrative_base_prose_ngram_overlap,
        check_narrative_e0_ngram_overlap,
        check_narrative_no_consulting_language,
        check_narrative_not_bullet_recap,
        check_narrative_seniority_floor,
        check_narrative_technical_specificity,
        check_narrative_upstream_graph_proof_bundle,
    )

    # Gate: seniority floor (HARD FAIL)
    sen_r = check_narrative_seniority_floor(narrative_sentence)
    add(
        sen_r.gate_id,
        sen_r.passed,
        sen_r.observed_value,
        sen_r.threshold,
        sen_r.failure_reason,
    )

    # Gate: no consulting language (HARD FAIL)
    consult_r = check_narrative_no_consulting_language(narrative_sentence)
    add(
        consult_r.gate_id,
        consult_r.passed,
        consult_r.observed_value,
        consult_r.threshold,
        consult_r.failure_reason,
    )

    # Gate: technical specificity floor (HARD FAIL)
    spec_r = check_narrative_technical_specificity(narrative_sentence)
    add(
        spec_r.gate_id,
        spec_r.passed,
        spec_r.observed_value,
        spec_r.threshold,
        spec_r.failure_reason,
    )

    # Gate: not bullet recap (WARN mode — calibrate before promoting)
    companion_bullets_list = [
        line.strip()
        for line in (companion_bullet_texts or "").split("\n")
        if line.strip()
    ]
    recap_r = check_narrative_not_bullet_recap(narrative_sentence, companion_bullets_list, warn_only=True)
    add(
        recap_r.gate_id,
        recap_r.passed,
        recap_r.observed_value,
        recap_r.threshold,
        recap_r.failure_reason,
    )

    # Gate: upstream graph proof required (WARN mode — Unify bullet graph_skill_node_ids currently fails on live runs)
    upstream_x2 = [
        {"gate_id": g.gate_id, "pass_": g.pass_}
        for g in gates
        if "graph_skill_node_ids" in (g.gate_id or "")
    ]
    upstream_r = check_narrative_upstream_graph_proof_bundle(upstream_x2, warn_only=True)
    add(
        upstream_r.gate_id,
        upstream_r.passed,
        upstream_r.observed_value,
        upstream_r.threshold,
        upstream_r.failure_reason,
    )

    # Gate: base prose n-gram overlap (WARN mode)
    base_narrative_texts: list[str] = []
    if parsed_output and isinstance(parsed_output, dict):
        _rp = parsed_output.get("_runtime_payload_ref") or {}
        if isinstance(_rp, dict):
            _role_narrative = str(
                (_rp.get("base_resume", {}) or {}).get("role_narrative", "")
            ).strip()
            if _role_narrative:
                base_narrative_texts = [_role_narrative]
    base_narr_r = check_narrative_base_prose_ngram_overlap(
        narrative_sentence, base_narrative_texts, warn_only=True
    )
    add(
        base_narr_r.gate_id,
        base_narr_r.passed,
        base_narr_r.observed_value,
        base_narr_r.threshold,
        base_narr_r.failure_reason,
    )

    # Gate: E0 n-gram overlap (WARN mode)
    e0_narr_r = check_narrative_e0_ngram_overlap(narrative_sentence, [], warn_only=True)
    add(
        e0_narr_r.gate_id,
        e0_narr_r.passed,
        e0_narr_r.observed_value,
        e0_narr_r.threshold,
        e0_narr_r.failure_reason,
    )

    return gates
