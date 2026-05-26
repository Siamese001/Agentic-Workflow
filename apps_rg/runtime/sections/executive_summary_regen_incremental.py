"""W3 — incremental regen anchor + PRIOR_ATTEMPT / STILL_FAILING delta lines."""

from __future__ import annotations

import json
import re
from typing import Any

from apps_rg.runtime.judges.executive_summary_x1d_dimension_verdicts import (
    dimension_major_fail_on_judge,
)
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences


def _normalize_judge_list(judges: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for judge in judges:
        if isinstance(judge, dict):
            out.append(judge)
        else:
            to_dict = getattr(judge, "to_dict", None)
            if callable(to_dict):
                out.append(to_dict())
    return out


def _judge_by_provider_key(judges: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for j in _normalize_judge_list(judges):
        pk = str(j.get("provider_key") or j.get("judge_id") or "").strip()
        if pk:
            out[pk] = j
    return out


def _is_model_backed_soft_fail(judge: dict[str, Any]) -> bool:
    if judge.get("evaluator_mode") != "MODEL_BACKED":
        return False
    if judge.get("pass") is True:
        return False
    status = str(judge.get("provider_status") or "").upper()
    return status in {"MODEL_BACKED_FAIL", "FAIL", "FAILED"}


def _soft_failed_model_judges(x1d_judges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [j for j in _normalize_judge_list(x1d_judges) if _is_model_backed_soft_fail(j)]

_ADDITIONALLY_RE = re.compile(r"\b(Additionally|Furthermore)\b", re.IGNORECASE)
_FORMULAIC_OPENER_RE = re.compile(
    r"^\s*(From|Against|Complementing|On|Building on)\b",
    re.IGNORECASE,
)

_DIMENSION_ORDER = (
    "executive_signal",
    "synthesis_quality",
    "resume_voice",
    "evidence_utilization",
    "factual_support",
    "ats_alignment_without_keyword_stuffing",
    "anti_overfit",
    "deterministic_alignment",
)


def format_regen_anchor_assistant_content(
    *,
    anchor_parsed: dict[str, Any] | None = None,
    anchor_raw_json: str = "",
    resume_fallback: str = "",
) -> str:
    """Full JSON assistant turn for SameAuthorityRegenRunner anchor slot."""
    if anchor_parsed and str(anchor_parsed.get("resume_display_text") or "").strip():
        payload = {k: v for k, v in anchor_parsed.items() if k != "selected_fact_plan"}
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    raw = str(anchor_raw_json or "").strip()
    if raw.startswith("{"):
        return raw
    resume = str(resume_fallback or "").strip()
    if resume:
        return json.dumps(
            {"resume_display_text": resume, "claim_ledger": []},
            ensure_ascii=False,
            separators=(",", ":"),
        )
    return ""


def _truncate_sentence(text: str, limit: int = 120) -> str:
    cleaned = " ".join(str(text or "").split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def summarize_prior_attempt_sentence_lines(
    *,
    baseline_resume_display_text: str,
    prior_attempt_resume_display_text: str,
) -> list[str]:
    """One summary per sentence that differs from publish baseline (scratch)."""
    baseline_s = [
        s.strip()
        for s in split_sentences(str(baseline_resume_display_text or ""))
        if s.strip()
    ]
    prior_s = [
        s.strip()
        for s in split_sentences(str(prior_attempt_resume_display_text or ""))
        if s.strip()
    ]
    if not prior_s:
        return []
    summaries: list[str] = []
    for idx in range(max(len(baseline_s), len(prior_s))):
        base = baseline_s[idx] if idx < len(baseline_s) else ""
        prior = prior_s[idx] if idx < len(prior_s) else ""
        if not prior or prior == base:
            continue
        summaries.append(f"S{idx + 1}: {_truncate_sentence(prior)}")
    return summaries


def _finding_addressed_by_prior_attempt(finding: str, prior_resume: str) -> bool:
    blob = str(finding or "")
    prior = str(prior_resume or "")
    lower = blob.lower()
    if ("additionally" in lower or "furthermore" in lower) and not _ADDITIONALLY_RE.search(prior):
        return True
    if "formulaic" in lower or "mechanical" in lower or "connective" in lower:
        prior_s = [s.strip() for s in split_sentences(prior) if s.strip()]
        if prior_s and not any(_FORMULAIC_OPENER_RE.match(s) for s in prior_s[1:5]):
            return True
    if "bullet stack" in lower or "bullet-stack" in lower:
        prior_s = [s.strip() for s in split_sentences(prior) if s.strip()]
        if len(prior_s) >= 4:
            short = sum(1 for s in prior_s[1:5] if len(s.split()) <= 14)
            if short < 3:
                return True
    return False


def still_failing_after_prior_attempt_lines(
    *,
    prior_cycle_judges: list[dict[str, Any]] | None,
    current_soft_judges: list[dict[str, Any]],
    prior_attempt_resume_display_text: str = "",
) -> list[str]:
    """Dimensions and judge critiques that persist after the last regen attempt."""
    if not prior_cycle_judges:
        return []
    prior_by_key = _judge_by_provider_key(_normalize_judge_list(prior_cycle_judges))
    lines: list[str] = []
    prior_resume = str(prior_attempt_resume_display_text or "")
    for judge in current_soft_judges:
        pk = str(judge.get("provider_key") or "").strip()
        if not pk:
            continue
        prior_judge = prior_by_key.get(pk)
        if prior_judge is None:
            continue
        still_dims = [
            dim
            for dim in _DIMENSION_ORDER
            if dimension_major_fail_on_judge(judge, dim)
            and dimension_major_fail_on_judge(prior_judge, dim)
        ]
        if still_dims:
            lines.append(f"{pk}: dimensions still failing: {', '.join(still_dims)}")
        for finding in judge.get("findings") or []:
            text = str(finding).strip()
            if not text or _finding_addressed_by_prior_attempt(text, prior_resume):
                continue
            if len(text) > 200:
                text = text[:197].rstrip() + "..."
            lines.append(f"{pk}: {text}")
    return lines[:8]


def collect_prior_attempt_incremental_delta_lines(
    *,
    baseline_resume_display_text: str,
    prior_attempt_resume_display_text: str,
    prior_cycle_judges: list[dict[str, Any]] | None,
    current_x1d_judges: list[dict[str, Any]],
) -> list[str]:
    """PRIOR_ATTEMPT_SUMMARY + STILL_FAILING_AFTER_PRIOR_ATTEMPT lines (cycle ≥2)."""
    prior_resume = str(prior_attempt_resume_display_text or "").strip()
    if not prior_resume:
        return []
    lines: list[str] = []
    summaries = summarize_prior_attempt_sentence_lines(
        baseline_resume_display_text=baseline_resume_display_text,
        prior_attempt_resume_display_text=prior_resume,
    )
    if summaries:
        lines.append("PRIOR_ATTEMPT_SUMMARY: " + " | ".join(summaries[:6]))
    soft = _soft_failed_model_judges(current_x1d_judges)
    for ln in still_failing_after_prior_attempt_lines(
        prior_cycle_judges=prior_cycle_judges,
        current_soft_judges=soft,
        prior_attempt_resume_display_text=prior_resume,
    ):
        lines.append(f"STILL_FAILING_AFTER_PRIOR_ATTEMPT: {ln}")
    return lines


def filter_verbatim_feedback_for_prior_attempt(
    feedback_lines: list[str],
    *,
    prior_attempt_resume_display_text: str,
) -> list[str]:
    """Drop judge lines whose cited issue appears fixed in the prior regen attempt."""
    prior_resume = str(prior_attempt_resume_display_text or "")
    if not prior_resume.strip():
        return list(feedback_lines)
    kept: list[str] = []
    for line in feedback_lines:
        if not line.startswith("- ") or " finding:" not in line:
            kept.append(line)
            continue
        finding = line.split(" finding:", 1)[-1].strip()
        if _finding_addressed_by_prior_attempt(finding, prior_resume):
            continue
        kept.append(line)
    return kept


__all__ = [
    "collect_prior_attempt_incremental_delta_lines",
    "filter_verbatim_feedback_for_prior_attempt",
    "format_regen_anchor_assistant_content",
    "still_failing_after_prior_attempt_lines",
    "summarize_prior_attempt_sentence_lines",
]
