"""Deterministic X2 gates for ibm_narrative runtime slice (single IBM role sentence)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

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
from apps_rg.runtime.qwen_offline_contract_stub import offline_contract_stub_enabled
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS, UNIFY_RUNTIME_TERM_PATTERNS
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


def _iter_source_fact_id_tokens(raw: Any) -> list[str]:
    """Normalize ``source_fact_ids`` to discrete fact-id tokens.

    L2 output may emit a single id as a string (``\"bul_ibm_001\"``); iterating
    that string character-wise is invalid. Lists/tuples/sets iterate elements.
    Comma-separated strings split safely after strip (empty parts dropped).
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        if "," in s:
            return [p.strip() for p in s.split(",") if p.strip()]
        return [s]
    if isinstance(raw, (list, tuple, set)):
        out: list[str] = []
        for x in raw:
            sx = str(x).strip()
            if sx:
                out.append(sx)
        return out
    sx = str(raw).strip()
    return [sx] if sx else []


def _ledger_fact_ids(claim_ledger: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for claim in claim_ledger:
        for fid in _iter_source_fact_id_tokens(claim.get("source_fact_ids")):
            ids.add(str(fid).split("_metric_")[0])
        if claim.get("source_fact_id"):
            ids.add(str(claim["source_fact_id"]).split("_metric_")[0])
    return ids


def _count_metric_hits(narrative: str) -> int:
    nl = narrative.lower()
    hits = 0
    if "$15m" in nl or re.search(r"\$15\s*m", narrative, re.I):
        hits += 1
    if "99.9%" in narrative:
        hits += 1
    if re.search(r"\b30\s*%", narrative):
        hits += 1
    if re.search(r"\b25\s*%", narrative):
        hits += 1
    if re.search(r"\b50\s*%", narrative):
        hits += 1
    return hits


REAL_L2_MOCK_LANGUAGE_BANNED_SUBSTRINGS: tuple[str, ...] = (
    "mocked_runtime_slice",
    "provider not requested",
    "mock fallback",
    "mocked judge",
    "plumbing only",
    "test-only",
    "plumbing_only",
)

IBM_NARRATIVE_THEME_TRIGGERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "bul_ibm_001",
        (
            "regulated financial",
            "financial services",
            "analytics platform",
            "enterprise reliability",
            "enterprise-scale",
            "financial-sector",
            "regulated sector",
        ),
    ),
    (
        "bul_ibm_002",
        (
            "migration",
            "modernization",
            "modernizing",
            "migrating",
            "cloud modernization",
            "infrastructure modernization",
        ),
    ),
    (
        "bul_ibm_003",
        (
            "reusable platform",
            "shared services",
            "lifecycle management",
            "operational burden",
        ),
    ),
    (
        "bul_ibm_004",
        (
            "lineage",
            "observability",
            "instrumentation",
            "distributed data",
        ),
    ),
    (
        "bul_ibm_005",
        (
            "partnership",
            "hyperscaler",
            "hyperscalers",
            "alliance",
            "ecosystems",
            "ecosystem",
        ),
    ),
)


def ibm_narrative_material_fact_ids_for_sentence(narrative_sentence: str) -> frozenset[str]:
    nl = narrative_sentence.lower().strip()
    ids: set[str] = set()
    for fid, phrases in IBM_NARRATIVE_THEME_TRIGGERS:
        if any(p in nl for p in phrases):
            ids.add(fid)
    return frozenset(ids)


IBM_RESUME_JARGON_BANNED_PHRASES: tuple[str, ...] = (
    "concentrated enterprise",
    "reliability posture",
    "migration cadence",
    "client-facing instrumentation",
    "stayed predictable",
)


def _product_fields_haystack_for_mock_language_gate(
    *,
    narrative_sentence: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
) -> str:
    parts: list[str] = [str(narrative_sentence or "")]
    if isinstance(parsed_output, dict):
        for key in ("change_log", "gap_notes", "self_check"):
            parts.append(json.dumps(parsed_output.get(key), sort_keys=True, default=str))
    for row in claim_ledger or []:
        if isinstance(row, dict):
            parts.append(str(row.get("claim_text") or ""))
            parts.append(json.dumps(row, sort_keys=True, default=str))
    return "\n".join(parts).lower()


def _companion_ibm_bullets_have_metrics(companion_bullet_texts: str) -> bool:
    c = companion_bullet_texts.lower()
    return (
        ("$15m" in c or "$15 m" in c)
        and "99.9%" in c
        and "30%" in c
        and "25%" in c
        and "50%" in c
    )


def run_ibm_narrative_x2_gates(
    *,
    narrative_sentence: str,
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    jd_text: str,
    runtime_generation_status: str,
    companion_bullet_texts: str | None,
    candidate_name: str = "",
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
    allowed_fact_ids: list[str] | None = None,
    test_only_mock_provider: bool = False,
    artifacts_dir: Any | None = None,
    text_claim_coverage: dict[str, Any] | None = None,
    srfs_source_fact_slice_gate_active: bool = False,
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
        "x2_ibm_narrative_exactly_one_sentence",
        exactly_one,
        len(sentences),
        1,
        "Must be exactly one sentence.",
    )

    leaks_name, name_hit = narrative_leaks_candidate_name_tokens(narrative_sentence, candidate_name)
    add(
        "x2_ibm_narrative_no_candidate_name_tokens",
        not leaks_name,
        name_hit or "none",
        "absent",
        "Candidate name must not appear in the role narrative sentence.",
    )

    ledger_ids = _ledger_fact_ids(claim_ledger)
    ibm_roots = set(IBM_BULLET_IDS)
    supported = bool(claim_ledger) and bool(ledger_ids)
    supported = supported and ledger_ids <= ibm_roots
    supported = supported and all(str(fid).startswith("bul_ibm_") for fid in ledger_ids)
    add(
        "x2_ibm_narrative_source_supported",
        supported,
        sorted(ledger_ids),
        "bul_ibm_*",
        "claim_ledger must map to IBM bullet facts only.",
    )

    allow_runtime = {str(x).strip() for x in (allowed_fact_ids or []) if str(x).strip()}
    bad_allow_tokens: list[str] = []
    if allowed_fact_ids is None:
        add(
            "x2_claim_ledger_source_fact_ids_allow_list",
            True,
            "skipped_no_runtime_allow_list",
            "invoke_with_runtime_allowed_fact_ids",
            None,
        )
    elif not allow_runtime:
        add(
            "x2_claim_ledger_source_fact_ids_allow_list",
            False,
            "empty_allow_list",
            "non_empty_allow_list",
            "runtime_payload allowed_fact_ids was empty",
        )
    else:
        for claim in claim_ledger:
            if not isinstance(claim, dict):
                continue
            for tok in _iter_source_fact_id_tokens(claim.get("source_fact_ids")):
                st = str(tok).strip()
                if st and st not in allow_runtime:
                    bad_allow_tokens.append(st)
        allow_ok = not bad_allow_tokens
        add(
            "x2_claim_ledger_source_fact_ids_allow_list",
            allow_ok,
            bad_allow_tokens or "all_tokens_in_allowed_fact_ids",
            sorted(allow_runtime),
            None
            if allow_ok
            else f"claim_ledger source_fact_ids outside runtime allow-list: {bad_allow_tokens}",
        )

    ledger_text_ok, ledger_text_reason = check_claim_ledger_claim_text_non_empty(claim_ledger)
    add(
        "x2_claim_ledger_claim_text_non_empty",
        ledger_text_ok,
        ledger_text_reason or "all_rows_non_empty",
        "non_empty_claim_text_each_row",
        ledger_text_reason,
    )

    serialized = json.dumps(parsed_output or {}, sort_keys=True).lower()
    scope_ids = _ledger_fact_ids(claim_ledger) | set(re.findall(r"bul_ibm_\d{3}", serialized))
    scope_ok = all(s.startswith("bul_ibm_") for s in scope_ids) and not any(
        p in serialized for p in ("bul_unify_", "bul_insurtech_", "bul_ey_", "bul_early_career_")
    )
    add(
        "x2_ibm_narrative_ibm_only_fact_scope",
        scope_ok,
        sorted(scope_ids),
        "bul_ibm_*",
        "Non-IBM fact scope in payload.",
    )

    add(
        "x2_no_unify_fact_leakage",
        "bul_unify_" not in serialized,
        "bul_unify_",
        "absent",
        "Unify bullet fact leakage detected.",
    )
    add("x2_no_insurtech_fact_leakage", "bul_insurtech_" not in serialized, "bul_insurtech_", "absent", "InsurTech leakage.")
    add("x2_no_ey_fact_leakage", "bul_ey_" not in serialized, "bul_ey_", "absent", "EY leakage.")

    jd_copy, jd_phrase = has_jd_phrase_copy(narrative_sentence, jd_text)
    add("x2_no_jd_only_claims", not jd_copy, jd_phrase or "none", "no long JD copy", "JD phrase copied as proof.")

    jargon_hits = [p for p in IBM_RESUME_JARGON_BANNED_PHRASES if p in narrative_sentence.lower()]
    add(
        "x2_ibm_narrative_weak_resume_jargon_phrases",
        not jargon_hits,
        jargon_hits or "none",
        "absent_durable_weak_phrases",
        None
        if not jargon_hits
        else f"Weak/consulting-stacked phrasing not allowed in sentence: {jargon_hits}",
    )

    theme_required = ibm_narrative_material_fact_ids_for_sentence(narrative_sentence)
    missing_themes = sorted(theme_required - ledger_ids)
    add(
        "x2_ibm_narrative_claim_theme_coverage",
        not missing_themes,
        {"themes_detected": sorted(theme_required), "missing_in_ledger_union": missing_themes},
        "ledger_covers_all_detected_themes",
        None
        if not missing_themes
        else (
            "narrative_sentence material themes require matching bul_ibm_* in claim_ledger union; "
            f"missing: {missing_themes}"
        ),
    )

    companion = companion_bullet_texts or ""
    metric_hits = _count_metric_hits(narrative_sentence)
    if companion and _companion_ibm_bullets_have_metrics(companion):
        repetition_ok = metric_hits == 0
        add(
            "x2_no_metric_repetition_unless_justified",
            repetition_ok,
            metric_hits,
            "0_when_companion_carries_full_IBM_metric_bundle",
            "Do not replay bullet metric tokens when companion IBM bullets include the full KPI bundle.",
        )
    else:
        add(
            "x2_no_metric_repetition_unless_justified",
            True,
            "no companion IBM bullets artifact",
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
    stacked_summary = comma_count >= 5 or narrative_sentence.count(";") >= 2
    add(
        "x2_no_five_bullet_roll_up_tone",
        not stacked_summary,
        comma_count,
        "<5 commas",
        "Reads like stacked bullet summary.",
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

    term_hits = [pat for pat in UNIFY_RUNTIME_TERM_PATTERNS if re.search(pat, narrative_sentence, re.I)]
    add(
        "x2_no_unify_runtime_terms",
        not term_hits,
        term_hits,
        [],
        "Unify runtime vocabulary leaked into IBM narrative.",
    )

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
    add(
        "x2_no_silent_mock_fallback",
        no_silent_mock,
        runtime_generation_status,
        "REAL_LLM",
        "Silent mock fallback detected.",
    )

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

    skip_mock_language_gate = bool(offline_contract_stub_enabled())
    active_mock_language_gate = (
        runtime_generation_status == "REAL_LLM"
        and not test_only_mock_provider
        and not skip_mock_language_gate
    )

    if not active_mock_language_gate:
        add(
            "x2_no_mock_or_plumbing_language_in_real_l2_output",
            True,
            "not_applicable",
            "skipped",
            None,
        )
    else:
        haystack = _product_fields_haystack_for_mock_language_gate(
            narrative_sentence=narrative_sentence,
            parsed_output=parsed_output,
            claim_ledger=claim_ledger,
        )
        offenders = [tok for tok in REAL_L2_MOCK_LANGUAGE_BANNED_SUBSTRINGS if tok in haystack]
        mock_lang_failure = (
            f"L2 payload contains test/plumbing/mock phrasing tokens: {offenders}"
            if offenders
            else None
        )
        add(
            "x2_no_mock_or_plumbing_language_in_real_l2_output",
            not offenders,
            offenders if offenders else "no_stale_mock_terms_detected",
            "no_mock_plumbing_lexicon_tokens",
            mock_lang_failure,
        )

    from apps_rg.runtime.validators.section_input_usage_x2 import append_section_input_usage_x2_gates

    if srfs_source_fact_slice_gate_active and allowed_fact_ids:
        from apps_rg.runtime.sections import selected_role_fact_set as _srfs_w4

        coll_inr = _srfs_w4.collect_source_fact_ids_from_claim_ledger(claim_ledger)
        allow_inr = {str(x).strip() for x in allowed_fact_ids if str(x).strip()}
        ok_inr, env_inr, fail_inr = _srfs_w4.evaluate_srfs_slice_source_fact_gate(
            section_id="ibm_narrative",
            collected_ids=coll_inr,
            allowed_fact_ids=allow_inr,
        )
        add(
            "x2_ibm_narrative_source_fact_ids_within_srfs_slice",
            ok_inr,
            env_inr,
            "srfs_slice_allowlist_exact",
            fail_inr,
        )

    _allow = set(str(x) for x in (allowed_fact_ids or [])) or set(IBM_BULLET_IDS)
    append_section_input_usage_x2_gates(
        gates,
        artifacts_dir=artifacts_dir or Path("artifacts/apps_rg/runtime_proofs/ibm_narrative"),
        allowed_fact_ids=_allow,
        claim_ledger=claim_ledger,
        text_claim_coverage=text_claim_coverage,
    )

    return gates


def count_ibm_narrative_metric_hits(narrative: str) -> int:
    return _count_metric_hits(narrative)


def companion_ibm_bullets_have_full_metric_bundle(companion_bullet_texts: str) -> bool:
    return _companion_ibm_bullets_have_metrics(companion_bullet_texts)


__all__ = [
    "IBM_NARRATIVE_THEME_TRIGGERS",
    "IBM_RESUME_JARGON_BANNED_PHRASES",
    "run_ibm_narrative_x2_gates",
    "count_ibm_narrative_metric_hits",
    "companion_ibm_bullets_have_full_metric_bundle",
    "ibm_narrative_material_fact_ids_for_sentence",
]
