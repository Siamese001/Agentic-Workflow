"""Deterministic X2 gates for unify_narrative runtime slice (single role sentence)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    EM_DASH,
    FIRST_PERSON_PATTERN,
    GENERIC_FILLER,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_json_parse_valid,
    check_judge_rows_present,
    check_judge_schema_valid,
    has_jd_phrase_copy,
    split_sentences,
)
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS
from apps_rg.runtime.validators.narrative_identity_x2 import narrative_leaks_candidate_name_tokens


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

    leaks_name, name_hit = narrative_leaks_candidate_name_tokens(narrative_sentence, candidate_name)
    add(
        "x2_unify_narrative_no_candidate_name_tokens",
        not leaks_name,
        name_hit or "none",
        "absent",
        "Candidate name must not appear in the role narrative sentence.",
    )

    ledger_ids = _ledger_fact_ids(claim_ledger)
    unify_roots = set(UNIFY_BULLET_IDS)
    supported = bool(claim_ledger) and bool(ledger_ids)
    supported = supported and ledger_ids <= unify_roots
    supported = supported and all(str(fid).startswith("bul_unify_") for fid in ledger_ids)
    add(
        "x2_unify_narrative_source_supported",
        supported,
        sorted(ledger_ids),
        "bul_unify_*",
        "claim_ledger must map to Unify bullet facts only.",
    )

    serialized = json.dumps(parsed_output or {}, sort_keys=True).lower()
    scope_ids = _ledger_fact_ids(claim_ledger) | set(
        re.findall(r"bul_unify_\d{3}", serialized)
    )
    scope_ok = all(s.startswith("bul_unify_") for s in scope_ids) and not any(
        p in serialized for p in ("bul_ibm_", "bul_insurtech_", "bul_ey_")
    )
    add("x2_unify_narrative_unify_only_fact_scope", scope_ok, sorted(scope_ids), "bul_unify_*", "Non-Unify fact scope.")

    add("x2_no_ibm_fact_leakage", "bul_ibm_" not in serialized, "bul_ibm_", "absent", "IBM leakage.")
    add("x2_no_insurtech_fact_leakage", "bul_insurtech_" not in serialized, "bul_insurtech_", "absent", "InsurTech leakage.")
    add("x2_no_ey_fact_leakage", "bul_ey_" not in serialized, "bul_ey_", "absent", "EY leakage.")

    jd_copy, jd_phrase = has_jd_phrase_copy(narrative_sentence, jd_text)
    add("x2_no_jd_only_claims", not jd_copy, jd_phrase or "none", "no long JD copy", "JD phrase copied as proof.")

    companion = companion_bullet_texts or ""
    if runtime_generation_status == "MOCKED":
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
        finalized_dependency_ok = bool(companion.strip()) and companion_bullets_status == "ACCEPTED_FINALIZED"
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

    return gates
