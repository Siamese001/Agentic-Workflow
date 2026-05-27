"""W4 — delta_class mapping, G5 scope gate, cycles v2 receipts, operator stderr."""

from __future__ import annotations

import re
import sys
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
    dimension_major_fail_on_judge,
    major_failed_dimension_ids_from_judges,
)
from apps_rg.runtime.sections.executive_summary_candidate_pool import (
    SCORES_FRESHNESS_CARRIED_FORWARD,
    SCORES_FRESHNESS_FULL_PANEL,
)
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    _holistic_judge_score,
    _is_model_backed_soft_fail,
    _normalize_judge_list,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    exploratory_full_paragraph_regen_enabled,
)
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences

JUDGE_REMEDIATION_CYCLES_SCHEMA_V2 = "executive_summary_judge_remediation_cycles_v2"
JUDGE_REMEDIATION_CYCLES_SCHEMA_VERSION = 2

DELTA_CLASS_S6_FORWARD_SYNTHESIS = "S6_forward_synthesis"
DELTA_CLASS_CONNECTIVE_S2_S5 = "connective_S2_S5"
DELTA_CLASS_LEDGER_METRIC_SYNC = "ledger_metric_sync"
DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL = "dimension_executive_signal"
DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH = "exploratory_full_paragraph"
DELTA_CLASS_RESUME_VOICE_HUMANIZE = "resume_voice_humanize"
DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE = "executive_signal_and_voice_v1"
DELTA_CLASS_ATS_TARGETING_WITHOUT_STUFFING = "ats_targeting_without_stuffing"
DELTA_CLASS_ANTI_OVERFIT_REDUCE_JD_ECHO = "anti_overfit_reduce_jd_echo"
DELTA_CLASS_DETERMINISTIC_ALIGNMENT_STRUCTURE = "deterministic_alignment_structure"
DELTA_CLASS_EVIDENCE_UTILIZATION_WEAVE = "evidence_utilization_weave"

# G5 sentence-edit budgets (24k context). Looser than 16k-era caps; exploratory still caps at 6.
_DELTA_CLASS_BUDGET: dict[str, int] = {
    DELTA_CLASS_S6_FORWARD_SYNTHESIS: 3,
    DELTA_CLASS_CONNECTIVE_S2_S5: 5,
    DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL: 5,
    DELTA_CLASS_LEDGER_METRIC_SYNC: 0,
    DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH: 6,
    DELTA_CLASS_RESUME_VOICE_HUMANIZE: 5,
    DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE: 6,
    DELTA_CLASS_ATS_TARGETING_WITHOUT_STUFFING: 4,
    DELTA_CLASS_ANTI_OVERFIT_REDUCE_JD_ECHO: 4,
    DELTA_CLASS_DETERMINISTIC_ALIGNMENT_STRUCTURE: 2,
    DELTA_CLASS_EVIDENCE_UTILIZATION_WEAVE: 5,
}

_S6_THIN_CODE_MARKERS = frozenset(
    {
        "s6_thin_recap",
        "s6_forward_synthesis_slightly_thin",
        "s6_thin",
    },
)


def _operator_pass_floor(operator_judge_pass_floor: float | None) -> float | None:
    if operator_judge_pass_floor is not None:
        return operator_judge_pass_floor
    from apps_rg.runtime.sections.executive_summary_repair_policy import judge_pass_floor_0_to_5

    return judge_pass_floor_0_to_5()


def _holistic_below_operator_floor(
    judge: dict[str, Any],
    operator_judge_pass_floor: float | None,
) -> bool:
    floor = _operator_pass_floor(operator_judge_pass_floor)
    if floor is None:
        return False
    score = _holistic_judge_score(judge)
    return score is not None and score + 1e-9 < floor


def _synthesis_s6_thin_signal(judge: dict[str, Any]) -> bool:
    """True when judge feedback targets thin/generic S6 despite pass=true on synthesis_quality."""
    dv = judge.get("dimension_verdicts")
    if isinstance(dv, dict):
        syn = dv.get("synthesis_quality")
        if isinstance(syn, dict):
            codes = {str(c).lower() for c in (syn.get("codes") or []) if str(c).strip()}
            if codes & _S6_THIN_CODE_MARKERS:
                return True
            if syn.get("pass") is True and str(syn.get("severity") or "").lower() == "minor":
                return True
    flags = {str(f).lower() for f in (judge.get("quality_flags") or []) if str(f).strip()}
    if flags & _S6_THIN_CODE_MARKERS:
        return True
    blob = " ".join(
        str(x)
        for x in (
            *(judge.get("findings") or []),
            *(judge.get("remediation_suggestions") or []),
            str(judge.get("rationale") or ""),
        )
    ).lower()
    if "s6" in blob and any(tok in blob for tok in ("thin", "generic", "forward synthesis", "recap")):
        return True
    return False


def _soft_failed_provider_keys(soft: list[dict[str, Any]]) -> set[str]:
    return {
        str(j.get("provider_key") or "").strip()
        for j in soft
        if str(j.get("provider_key") or "").strip()
    }


_RESUME_VOICE_PROSE_MARKERS = (
    "resume voice",
    "mechanical opener",
    "mechanical phrasing",
    "additionally",
    "furthermore",
    "repetition",
    "repetitive",
    "robotic",
    "stilted",
    "formulaic",
    "humanize",
    "humanise",
    "connective tissue",
)


def _judge_prose_blob(judge: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("findings", "fail_reasons", "remediation_suggestions", "quality_flags"):
        val = judge.get(key)
        if isinstance(val, list):
            parts.extend(str(x) for x in val if str(x).strip())
        elif isinstance(val, str) and val.strip():
            parts.append(val)
    rationale = str(judge.get("rationale") or "").strip()
    if rationale:
        parts.append(rationale)
    return " ".join(parts).lower()


def _resume_voice_prose_signal(judge: dict[str, Any]) -> bool:
    """True when judge prose targets voice/mechanical tone (even if only executive_signal dim failed)."""
    dv = judge.get("dimension_verdicts")
    if isinstance(dv, dict):
        voice = dv.get("resume_voice")
        if isinstance(voice, dict) and voice.get("pass") is False:
            return True
    blob = _judge_prose_blob(judge)
    return any(marker in blob for marker in _RESUME_VOICE_PROSE_MARKERS)


def _soft_judges_have_resume_voice_prose(soft: list[dict[str, Any]]) -> bool:
    return any(_resume_voice_prose_signal(j) for j in soft)


def _executive_signal_and_voice_composite_eligible(
    soft: list[dict[str, Any]],
    failed_dims: list[str],
) -> bool:
    """True when voice + substantive (exec signal or synthesis) fail together."""
    dims = set(failed_dims)
    if "resume_voice" not in dims:
        return False
    if not dims.intersection({"executive_signal", "synthesis_quality"}):
        return False
    if len(_soft_failed_provider_keys(soft)) >= 2:
        return True
    return any(
        dimension_major_fail_on_judge(j, "resume_voice")
        and (
            dimension_major_fail_on_judge(j, "executive_signal")
            or dimension_major_fail_on_judge(j, "synthesis_quality")
        )
        for j in soft
    )


def format_sentence_allowlist_label(allowlist: frozenset[int]) -> str:
    """Human label for allowed sentences (1-based S1..S6)."""
    if not allowlist:
        return "no sentences"
    ordered = sorted(allowlist)
    if len(ordered) == 1:
        return f"S{ordered[0]}"
    if ordered == list(range(ordered[0], ordered[-1] + 1)):
        return f"S{ordered[0]}–S{ordered[-1]}"
    return ", ".join(f"S{i}" for i in ordered)


def format_edit_budget_line(
    delta_class: str,
    allowlist: frozenset[int],
) -> str:
    """Prescriptive EDIT_BUDGET tied to G5v2 allowlist (W4.2)."""
    if not allowlist:
        return (
            f"EDIT_BUDGET: no resume_display_text sentence edits; ledger/metric alignment only; "
            f"delta_class={delta_class}; freeze all sentences verbatim."
        )
    label = format_sentence_allowlist_label(allowlist)
    idx_csv = ", ".join(str(i) for i in sorted(allowlist))
    return (
        f"EDIT_BUDGET: you may change {label} (indexes {idx_csv}) and claim_ledger rows they cite; "
        f"freeze all other sentences verbatim; delta_class={delta_class}."
    )


def resolve_delta_class(
    x1d_judges: list[Any],
    *,
    operator_judge_pass_floor: float | None = None,
) -> str:
    """Map soft-failed judges to a single delta class for this regen cycle."""
    if exploratory_full_paragraph_regen_enabled():
        return DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH

    soft = [j for j in _normalize_judge_list(x1d_judges) if _is_model_backed_soft_fail(j)]
    failed_dims = major_failed_dimension_ids_from_judges(soft, judge_filter=_is_model_backed_soft_fail)
    floor = _operator_pass_floor(operator_judge_pass_floor)

    if _executive_signal_and_voice_composite_eligible(soft, failed_dims):
        return DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE

    if _soft_failed_provider_keys(soft) == {"anthropic_claude"} and any(
        _synthesis_s6_thin_signal(j) for j in soft
    ):
        if _regen_citations_exceed_s6_only(soft):
            return DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE
        return DELTA_CLASS_S6_FORWARD_SYNTHESIS

    if not failed_dims:
        if any(
            _holistic_below_operator_floor(j, floor) and _synthesis_s6_thin_signal(j) for j in soft
        ):
            return DELTA_CLASS_S6_FORWARD_SYNTHESIS
        if soft and floor is not None and all(_holistic_below_operator_floor(j, floor) for j in soft):
            if any(_synthesis_s6_thin_signal(j) for j in soft):
                return DELTA_CLASS_S6_FORWARD_SYNTHESIS
        return DELTA_CLASS_CONNECTIVE_S2_S5

    if failed_dims == ["resume_voice"]:
        return DELTA_CLASS_RESUME_VOICE_HUMANIZE

    if failed_dims == ["evidence_utilization"]:
        return DELTA_CLASS_EVIDENCE_UTILIZATION_WEAVE

    if failed_dims == ["ats_alignment_without_keyword_stuffing"]:
        return DELTA_CLASS_ATS_TARGETING_WITHOUT_STUFFING

    if failed_dims == ["anti_overfit"] or (
        "anti_overfit" in failed_dims
        and any(
            "jd" in str(j.get("rationale") or "").lower()
            or "job description" in str(j.get("rationale") or "").lower()
            for j in soft
        )
    ):
        return DELTA_CLASS_ANTI_OVERFIT_REDUCE_JD_ECHO

    if failed_dims == ["deterministic_alignment"]:
        return DELTA_CLASS_DETERMINISTIC_ALIGNMENT_STRUCTURE

    if failed_dims == ["synthesis_quality"]:
        if _regen_citations_exceed_s6_only(soft):
            return DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE
        return DELTA_CLASS_S6_FORWARD_SYNTHESIS

    if "resume_voice" in failed_dims:
        return DELTA_CLASS_RESUME_VOICE_HUMANIZE

    if "executive_signal" in failed_dims:
        if _soft_judges_have_resume_voice_prose(soft):
            return DELTA_CLASS_RESUME_VOICE_HUMANIZE
        return DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL

    if set(failed_dims) <= {"resume_voice", "synthesis_quality", "evidence_utilization"}:
        return DELTA_CLASS_CONNECTIVE_S2_S5

    if "synthesis_quality" in failed_dims and len(failed_dims) == 1:
        if _regen_citations_exceed_s6_only(soft):
            return DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE
        return DELTA_CLASS_S6_FORWARD_SYNTHESIS

    return DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL


def format_delta_class_regen_instruction(
    delta_class: str,
    *,
    allowlist: frozenset[int] | None = None,
) -> str:
    """Narrow delta instruction — no default full S2–S6 rewrite unless exploratory."""
    scope = ""
    if allowlist:
        label = format_sentence_allowlist_label(allowlist)
        scope = f" Target {label} only (indexes {', '.join(str(i) for i in sorted(allowlist))})."
    budget = max_sentence_edits_for_delta_class(delta_class)
    if delta_class == DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL:
        return (
            f"executive_signal: revise at most {budget} sentences to improve SVP platform/governance arc; "
            f"same allowed facts; jd_used_as_proof=false.{scope}"
        )
    if delta_class == DELTA_CLASS_RESUME_VOICE_HUMANIZE:
        return (
            f"resume_voice_humanize: reword allowed sentences for natural executive tone; "
            f"preserve facts, metrics, and source_fact_ids.{scope}"
        )
    if delta_class == DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE:
        return (
            "executive_signal_and_voice_v1: (1) executive_signal — S1 = one SVP IT strategy thesis; "
            "S2–S5 = one causal arc with dollar/percent metrics in display for S3–S5 (not claim_text alone); "
            "(2) resume_voice — vary S2–S5 connective openers (avoid formulaic From/Against/Complementing/On chains); "
            "third person, active voice, no Additionally/Furthermore; "
            "(3) synthesis_quality — S5 must surface FSA/quant foundation with a concrete metric or outcome; "
            f"S6 = forward enterprise IT direction grounded in proof (no cover-letter Looking ahead opener).{scope}"
        )
    instructions = {
        DELTA_CLASS_S6_FORWARD_SYNTHESIS: (
            "synthesis_quality: revise S6 forward synthesis (and claim_ledger rows it touches only); "
            f"keep non-target sentences verbatim unless a cited metric must align.{scope}"
        ),
        DELTA_CLASS_CONNECTIVE_S2_S5: (
            "connective_S2_S5: reword openers for allowed sentences only; preserve facts, metrics, "
            f"and source_fact_ids; no employer inventory stack.{scope}"
        ),
        DELTA_CLASS_LEDGER_METRIC_SYNC: (
            "ledger_metric_sync: deterministic metric alignment only (no new claims)."
        ),
        DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH: (
            "exploratory_full_paragraph: full six-sentence rewrite allowed (exploratory flag on)."
        ),
        DELTA_CLASS_ATS_TARGETING_WITHOUT_STUFFING: (
            "ats_targeting_without_stuffing: tighten role relevance without JD keyword stuffing; "
            "jd_used_as_proof=false."
        ),
        DELTA_CLASS_ANTI_OVERFIT_REDUCE_JD_ECHO: (
            "anti_overfit_reduce_jd_echo: remove mirrored JD phrasing; keep targeting in relevance only."
        ),
        DELTA_CLASS_DETERMINISTIC_ALIGNMENT_STRUCTURE: (
            "deterministic_alignment_structure: ledger/metric alignment only (no new claims)."
        ),
        DELTA_CLASS_EVIDENCE_UTILIZATION_WEAVE: (
            "evidence_utilization_weave: weave unused allowed facts into prose and claim_ledger; "
            "no dropped source_fact_ids."
        ),
    }
    return instructions.get(
        delta_class,
        format_delta_class_regen_instruction(DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL),
    )


_EXEC_SUMMARY_SENTENCE_COUNT = 6


def max_sentence_edits_for_delta_class(delta_class: str) -> int:
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        regen_artificial_caps_enabled,
    )

    if not regen_artificial_caps_enabled():
        return int(_DELTA_CLASS_BUDGET.get(delta_class, _EXEC_SUMMARY_SENTENCE_COUNT))
    return int(_DELTA_CLASS_BUDGET.get(delta_class, 5))

# 1-based sentence indexes (S1=1 … S6=6) permitted when judges omit cited_sentence_indexes.
_DELTA_CLASS_DEFAULT_ALLOWLIST: dict[str, frozenset[int]] = {
    DELTA_CLASS_CONNECTIVE_S2_S5: frozenset({2, 3, 4, 5}),
    DELTA_CLASS_S6_FORWARD_SYNTHESIS: frozenset({6}),
    DELTA_CLASS_LEDGER_METRIC_SYNC: frozenset(),
    DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL: frozenset({2, 3, 4, 5, 6}),
    DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH: frozenset({1, 2, 3, 4, 5, 6}),
    DELTA_CLASS_RESUME_VOICE_HUMANIZE: frozenset({2, 3, 4, 5, 6}),
    DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE: frozenset({1, 2, 3, 4, 5, 6}),
    DELTA_CLASS_ATS_TARGETING_WITHOUT_STUFFING: frozenset({1, 2, 3, 4, 5, 6}),
    DELTA_CLASS_ANTI_OVERFIT_REDUCE_JD_ECHO: frozenset({1, 2, 3, 4, 5, 6}),
    DELTA_CLASS_DETERMINISTIC_ALIGNMENT_STRUCTURE: frozenset({1, 2, 3, 4, 5, 6}),
    DELTA_CLASS_EVIDENCE_UTILIZATION_WEAVE: frozenset({2, 3, 4, 5, 6}),
}

_SENTENCE_REF_RE = re.compile(
    r"\bS\s*([1-6])\b(?:\s*[-–—]\s*S?\s*([1-6]))?",
    re.IGNORECASE,
)
_SENTENCES_RANGE_RE = re.compile(
    r"\bsentences?\s+([1-6])\s*[-–—]\s*([1-6])\b",
    re.IGNORECASE,
)


def _normalize_cited_sentence_index(raw: Any) -> int | None:
    """Map judge citation to 1-based index (S1=1). Accepts 0-based S1=0."""
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return None
    if n == 0:
        return 1
    if 1 <= n <= _EXEC_SUMMARY_SENTENCE_COUNT:
        return n
    return None


def _expand_sentence_range(start: int, end: int) -> set[int]:
    lo, hi = min(start, end), max(start, end)
    lo = max(1, min(lo, _EXEC_SUMMARY_SENTENCE_COUNT))
    hi = max(1, min(hi, _EXEC_SUMMARY_SENTENCE_COUNT))
    return set(range(lo, hi + 1))


def infer_sentence_indexes_from_text(text: str) -> set[int]:
    """Infer 1-based sentence indexes from judge prose (S2, S2–S5, sentence 6)."""
    found: set[int] = set()
    blob = str(text or "")
    for match in _SENTENCE_REF_RE.finditer(blob):
        a = int(match.group(1))
        b = match.group(2)
        if b is not None:
            found |= _expand_sentence_range(a, int(b))
        else:
            norm = _normalize_cited_sentence_index(a)
            if norm is not None:
                found.add(norm)
    for match in _SENTENCES_RANGE_RE.finditer(blob):
        found |= _expand_sentence_range(int(match.group(1)), int(match.group(2)))
    return found


def _judge_text_blobs(judge: dict[str, Any]) -> list[str]:
    parts: list[str] = []
    for key in ("findings", "fail_reasons", "remediation_suggestions", "quality_flags"):
        val = judge.get(key)
        if isinstance(val, list):
            parts.extend(str(x) for x in val if str(x).strip())
        elif isinstance(val, str) and val.strip():
            parts.append(val)
    rationale = str(judge.get("rationale") or "").strip()
    if rationale:
        parts.append(rationale)
    return parts


def _cited_indexes_from_soft_judges(soft: list[dict[str, Any]]) -> set[int]:
    cited: set[int] = set()
    for judge in soft:
        if not _is_model_backed_soft_fail(judge):
            continue
        cited_raw = judge.get("cited_sentence_indexes") or []
        if isinstance(cited_raw, list):
            for raw in cited_raw:
                norm = _normalize_cited_sentence_index(raw)
                if norm is not None:
                    cited.add(norm)
        for blob in _judge_text_blobs(judge):
            cited |= infer_sentence_indexes_from_text(blob)
    return cited


def _regen_citations_exceed_s6_only(soft: list[dict[str, Any]]) -> bool:
    """True when judge cited/inferred indexes include sentences outside S6."""
    cited = _cited_indexes_from_soft_judges(soft)
    return bool(cited - {6})


def build_regen_sentence_allowlist(
    x1d_judges: list[dict[str, Any]],
    delta_class: str,
) -> tuple[frozenset[int], dict[str, Any]]:
    """Union cited indexes from soft-failed judges + delta_class fallback."""
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        regen_artificial_caps_enabled,
    )

    caps_disabled = not regen_artificial_caps_enabled()

    from_judge: set[int] = set()
    per_judge: list[dict[str, Any]] = []
    for judge in _normalize_judge_list(x1d_judges):
        if not _is_model_backed_soft_fail(judge):
            continue
        provider = str(judge.get("provider_key") or judge.get("provider_name") or "?")
        cited_raw = judge.get("cited_sentence_indexes") or []
        cited_norm: list[int] = []
        if isinstance(cited_raw, list):
            for raw in cited_raw:
                norm = _normalize_cited_sentence_index(raw)
                if norm is not None:
                    from_judge.add(norm)
                    cited_norm.append(norm)
        inferred: set[int] = set()
        for blob in _judge_text_blobs(judge):
            inferred |= infer_sentence_indexes_from_text(blob)
        from_judge |= inferred
        per_judge.append(
            {
                "provider_key": provider,
                "cited_sentence_indexes": cited_norm,
                "inferred_sentence_indexes": sorted(inferred),
            },
        )

    fallback = _DELTA_CLASS_DEFAULT_ALLOWLIST.get(
        delta_class,
        _DELTA_CLASS_DEFAULT_ALLOWLIST[DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL],
    )
    sources: list[str] = []
    allow = set(from_judge)
    if from_judge:
        sources.append("judge_cited_or_inferred")
    if fallback:
        allow |= set(fallback)
        sources.append("delta_class_fallback")
    if not allow and fallback is not None:
        allow = set(fallback)
    if delta_class == DELTA_CLASS_S6_FORWARD_SYNTHESIS:
        s6_only = _DELTA_CLASS_DEFAULT_ALLOWLIST[DELTA_CLASS_S6_FORWARD_SYNTHESIS]
        if allow - s6_only:
            allow = set(s6_only)
            sources = ["delta_class_s6_strict"]
    meta = {
        "allowlist_sources": sources or ["delta_class_fallback"],
        "judge_allowlist_contributions": per_judge,
        "delta_class_fallback_indexes": sorted(fallback),
        "regen_caps_disabled": caps_disabled,
    }
    if caps_disabled and "regen_caps_disabled" not in meta["allowlist_sources"]:
        meta["allowlist_sources"] = [*meta["allowlist_sources"], "regen_caps_disabled"]
    return frozenset(allow), meta


def count_sentence_edits(prior_resume: str, after_resume: str) -> tuple[int, dict[str, Any]]:
    """Count positional sentence slots whose normalized text changed."""
    prior_s = [s.strip() for s in split_sentences(str(prior_resume or "")) if s.strip()]
    after_s = [s.strip() for s in split_sentences(str(after_resume or "")) if s.strip()]
    edited = 0
    edited_indices: list[int] = []
    for idx in range(max(len(prior_s), len(after_s))):
        p = prior_s[idx] if idx < len(prior_s) else ""
        a = after_s[idx] if idx < len(after_s) else ""
        if p != a:
            edited += 1
            edited_indices.append(idx + 1)
    return edited, {
        "prior_sentence_count": len(prior_s),
        "after_sentence_count": len(after_s),
        "edited_sentence_count": edited,
        "edited_sentence_indices": edited_indices,
    }


def evaluate_g5_delta_scope(
    prior_resume: str,
    after_resume: str,
    delta_class: str,
) -> dict[str, Any]:
    """G5 legacy — numeric sentence-edit budget (advisory when v2 runs)."""
    budget = max_sentence_edits_for_delta_class(delta_class)
    edited, detail = count_sentence_edits(prior_resume, after_resume)
    passed = edited <= budget
    receipt: dict[str, Any] = {
        "schema": "executive_summary_g5_delta_scope_v1",
        "passed": passed,
        "reject_gate": None if passed else "delta_scope_violation",
        "delta_class": delta_class,
        "max_sentence_edits_allowed": budget,
        "gate_mode": "legacy_sentence_budget",
        **detail,
    }
    if not passed:
        receipt["failure_reason"] = (
            f"edited_sentence_count={edited} exceeds budget={budget} for delta_class={delta_class}"
        )
    return receipt


def evaluate_g5_delta_scope_v2(
    prior_resume: str,
    after_resume: str,
    delta_class: str,
    *,
    x1d_judges: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """G5v2 — publish gate: edits must stay within judge/delta_class sentence allowlist."""
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        regen_artificial_caps_enabled,
    )

    edited_count, detail = count_sentence_edits(prior_resume, after_resume)
    if not regen_artificial_caps_enabled():
        return {
            "schema": "executive_summary_g5_delta_scope_v2",
            "gate_mode": "disabled",
            "passed": True,
            "reject_gate": None,
            "verdict": "regen_caps_disabled",
            "delta_class": delta_class,
            "allowlist": list(range(1, _EXEC_SUMMARY_SENTENCE_COUNT + 1)),
            "allowlist_passed": True,
            "out_of_allowlist_indices": [],
            "edited_sentence_count": edited_count,
            **detail,
            "allowlist_sources": ["regen_caps_disabled"],
            "g5_legacy_budget_advisory": {
                "schema": "executive_summary_g5_delta_scope_v1",
                "passed": True,
                "gate_mode": "disabled",
            },
        }

    edited_set = set(detail.get("edited_sentence_indices") or [])
    allowlist, allow_meta = build_regen_sentence_allowlist(
        list(x1d_judges or []),
        delta_class,
    )
    allow_sorted = sorted(allowlist)
    out_of_allowlist = sorted(idx for idx in edited_set if idx not in allowlist)
    allowlist_passed = len(out_of_allowlist) == 0
    legacy = evaluate_g5_delta_scope(prior_resume, after_resume, delta_class)

    passed = allowlist_passed
    receipt: dict[str, Any] = {
        "schema": "executive_summary_g5_delta_scope_v2",
        "gate_mode": "allowlist_primary",
        "passed": passed,
        "reject_gate": None if passed else "delta_scope_violation_allowlist",
        "verdict": "allowlist_pass" if passed else "allowlist_violation",
        "delta_class": delta_class,
        "allowlist": allow_sorted,
        "allowlist_passed": allowlist_passed,
        "out_of_allowlist_indices": out_of_allowlist,
        "edited_sentence_count": edited_count,
        **detail,
        **allow_meta,
        "g5_legacy_budget_advisory": legacy,
    }
    if not passed:
        receipt["failure_reason"] = (
            f"edited indices {sorted(edited_set)} include out-of-allowlist {out_of_allowlist}; "
            f"allowlist={allow_sorted}"
        )
    elif not legacy.get("passed"):
        receipt["legacy_budget_warning"] = legacy.get("failure_reason")
    return receipt


def build_judge_remediation_cycles_receipt(
    *,
    max_cycles: int,
    generation_material_digest: str,
    targeting_parity_at_regen_start: Any,
    judge_packet_targeting_audit: dict[str, Any],
    operator_judge_pass_floor: float | None = None,
) -> dict[str, Any]:
    """Cycles receipt envelope (schema v2 only for new runs)."""
    receipt: dict[str, Any] = {
        "schema": JUDGE_REMEDIATION_CYCLES_SCHEMA_V2,
        "schema_version": JUDGE_REMEDIATION_CYCLES_SCHEMA_VERSION,
        "max_cycles": max_cycles,
        "cycles": [],
        "stopped_reason": "",
        "generation_material_digest": generation_material_digest,
        "targeting_parity_at_regen_start": targeting_parity_at_regen_start,
        "judge_packet_targeting_audit": judge_packet_targeting_audit,
    }
    if operator_judge_pass_floor is not None:
        receipt["operator_judge_pass_floor"] = operator_judge_pass_floor
    return receipt


def compute_regen_outcome(
    *,
    cycles: list[dict[str, Any]],
    final_publish_baseline: str | None,
    all_model_backed_judges_pass: bool,
) -> str:
    """Run-level regen outcome for operator receipts (never ``improved`` on false scratch win)."""
    def _cycle_post_gate_accepted(c: dict[str, Any]) -> bool:
        if not c.get("publish_eligible"):
            return False
        if "accepted" in c:
            return bool(c.get("accepted"))
        return bool(c.get("draft_parse_ok"))

    accepted_publishable = [
        c for c in cycles if isinstance(c, dict) and _cycle_post_gate_accepted(c)
    ]
    baseline = str(final_publish_baseline or "scratch").strip() or "scratch"

    if baseline != "scratch":
        if all_model_backed_judges_pass:
            return "improved"
        if accepted_publishable:
            return "no_acceptable_candidate"
        return "floor_not_met"

    if accepted_publishable:
        return "no_acceptable_candidate"
    if cycles:
        return "no_acceptable_candidate"
    if all_model_backed_judges_pass:
        return "improved"
    return "floor_not_met"


def cert_block_for_published_scores_freshness(
    scores_freshness: str,
    *,
    published_candidate_id: str,
    scratch_digest: str,
    published_digest: str,
) -> tuple[bool, str | None]:
    """CERTIFIED guard when published text changed but scores are not full-panel."""
    material_change = (
        published_candidate_id != "scratch"
        or (scratch_digest and published_digest and scratch_digest != published_digest)
    )
    if not material_change:
        return False, None
    if scores_freshness != SCORES_FRESHNESS_FULL_PANEL:
        return True, "stale_non_trigger_scores"
    if scores_freshness == SCORES_FRESHNESS_CARRIED_FORWARD:
        return True, "stale_non_trigger_scores"
    return False, None


def format_judge_regen_operator_stderr_line(
    *,
    cycle: int,
    reject_gate: str | None,
    g3_verdicts: list[dict[str, Any]] | None,
    operator_floor: float | None,
    final_publish_baseline: str,
    published_min_score: float | None,
) -> str:
    """One-line operator summary for stderr (plan W4.3)."""
    floor_s = f"{operator_floor:.1f}" if operator_floor is not None else "?"
    claude_bits: list[str] = []
    for row in g3_verdicts or []:
        if str(row.get("provider_key") or "") != "anthropic_claude":
            continue
        sb = row.get("score_before")
        sa = row.get("score_after")
        if sb is not None and sa is not None:
            claude_bits.append(f"Claude {sb}→{sa}")
        break
    regression = f" ({', '.join(claude_bits)})" if claude_bits else ""
    if reject_gate:
        return (
            f"Judge regen cycle {cycle} rejected: {reject_gate}{regression} "
            f"(floor {floor_s}). Published {final_publish_baseline} "
            f"(min {published_min_score if published_min_score is not None else '?'})."
        )
    return (
        f"Judge regen cycle {cycle} accepted (floor {floor_s}). "
        f"Published {final_publish_baseline} "
        f"(min {published_min_score if published_min_score is not None else '?'})."
    )


def emit_judge_regen_operator_stderr(line: str) -> None:
    if line.strip():
        print(line.strip(), file=sys.stderr, flush=True)


def min_model_backed_holistic_from_judges(judges: list[dict[str, Any]]) -> float | None:
    scores: list[float] = []
    for j in _normalize_judge_list(judges):
        if j.get("evaluator_mode") != "MODEL_BACKED":
            continue
        hs = _holistic_judge_score(j)
        if hs is not None:
            scores.append(hs)
    return min(scores) if scores else None


def summarize_cycles_for_operator(
    cycles_receipt: dict[str, Any],
    *,
    x1d_judges: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Extract matrix-friendly columns from v2 cycles receipt."""
    cycles = [c for c in (cycles_receipt.get("cycles") or []) if isinstance(c, dict)]
    last = cycles[-1] if cycles else {}
    out: dict[str, Any] = {
        "schema_version": cycles_receipt.get("schema_version"),
        "regen_outcome": cycles_receipt.get("regen_outcome"),
        "final_publish_baseline": cycles_receipt.get("final_publish_baseline"),
        "publish_selected_snapshot_id": cycles_receipt.get("publish_selected_snapshot_id"),
        "published_candidate_digest": cycles_receipt.get("published_candidate_digest"),
        "last_cycle_reject_gate": last.get("reject_gate"),
        "last_cycle_delta_class": last.get("delta_class"),
    }
    if x1d_judges is not None:
        out["published_min_holistic_0_to_5"] = min_model_backed_holistic_from_judges(x1d_judges)
    return out


__all__ = [
    "DELTA_CLASS_CONNECTIVE_S2_S5",
    "DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL",
    "DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE",
    "DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH",
    "DELTA_CLASS_LEDGER_METRIC_SYNC",
    "DELTA_CLASS_S6_FORWARD_SYNTHESIS",
    "JUDGE_REMEDIATION_CYCLES_SCHEMA_V2",
    "JUDGE_REMEDIATION_CYCLES_SCHEMA_VERSION",
    "build_judge_remediation_cycles_receipt",
    "cert_block_for_published_scores_freshness",
    "compute_regen_outcome",
    "count_sentence_edits",
    "emit_judge_regen_operator_stderr",
    "build_regen_sentence_allowlist",
    "evaluate_g5_delta_scope",
    "evaluate_g5_delta_scope_v2",
    "infer_sentence_indexes_from_text",
    "exploratory_full_paragraph_regen_enabled",
    "format_delta_class_regen_instruction",
    "format_edit_budget_line",
    "format_judge_regen_operator_stderr_line",
    "format_sentence_allowlist_label",
    "max_sentence_edits_for_delta_class",
    "min_model_backed_holistic_from_judges",
    "resolve_delta_class",
    "summarize_cycles_for_operator",
]
