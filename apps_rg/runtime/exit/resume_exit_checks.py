"""S6: Deterministic Resume Exit Checks for apps_rg resume-shipping pipeline.

Determines whether a generated/resolved resume artifact is structurally
sendable before manual review or sending.

S6 BOUNDARY (see apps_rg_resume_shipping_s6_deterministic_resume_exit_checks.md):
- Deterministic checks ONLY — no LLM judges
- No PA, C0, L2, provider, model, cache, L4, or L6 calls
- No routing changes
- No agentic_core imports

UNKNOWN is NEVER PASS. Material UNKNOWN blocks sendable=True.

Checks implemented:
  A. HEADLINE_CHECK     — one-line, non-empty, max-length
  B. EXEC_SUMMARY_CHECK — non-empty, min/max length, no placeholder
  C. ROLES_CHECK        — employer/title/narrative present, bullet bounds, ordinals
  D. VERBATIM_CHECK     — education/certifications/early_career preserve_verbatim;
                          hash fields produce WARN when absent (never invented)
  E. SUPPORT_STATUS_CHECK — INSUFFICIENT_SOURCE_SUPPORT/BLOCKED/UNKNOWN block sendable
  F. COMPETENCIES_CHECK — 2-4 word phrases, no empty entries
  G. REQUIRED_SECTIONS_CHECK — all required sections present
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Profile loader
# ---------------------------------------------------------------------------

_PROFILE_PATH = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "config"
    / "domain_contract"
    / "resume_exit_checks_profile.v1.json"
)

_DEFAULT_PROFILE: dict[str, Any] | None = None


def _load_profile() -> dict[str, Any]:
    global _DEFAULT_PROFILE
    if _DEFAULT_PROFILE is None:
        with _PROFILE_PATH.open(encoding="utf-8") as fh:
            _DEFAULT_PROFILE = json.load(fh)
    return _DEFAULT_PROFILE


# ---------------------------------------------------------------------------
# Verdict enum
# ---------------------------------------------------------------------------

class CheckVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# Per-check result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CheckResult:
    """Result of a single deterministic exit check."""
    check_id: str
    section: str
    verdict: CheckVerdict
    decisive_reason: str
    evidence_summary: str = ""
    unknown_reason: str = ""
    failed_fields: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def is_hard_fail(self) -> bool:
        return self.verdict == CheckVerdict.FAIL

    def is_unknown(self) -> bool:
        return self.verdict == CheckVerdict.UNKNOWN

    def is_warn(self) -> bool:
        return self.verdict == CheckVerdict.WARN


# ---------------------------------------------------------------------------
# Aggregate result
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExitCheckSummary:
    """Aggregate deterministic exit check summary for one resume artifact."""
    overall_verdict: CheckVerdict
    hard_fail_present: bool
    unknown_material_present: bool
    warning_present: bool
    sendable: bool
    check_results: tuple[CheckResult, ...]

    def failing_checks(self) -> list[CheckResult]:
        return [r for r in self.check_results if r.verdict == CheckVerdict.FAIL]

    def unknown_checks(self) -> list[CheckResult]:
        return [r for r in self.check_results if r.verdict == CheckVerdict.UNKNOWN]

    def warning_checks(self) -> list[CheckResult]:
        return [r for r in self.check_results if r.verdict == CheckVerdict.WARN]


# ---------------------------------------------------------------------------
# Individual check implementations
# ---------------------------------------------------------------------------

def _check_required_sections(
    artifact: dict[str, Any],
    profile: dict[str, Any],
) -> CheckResult:
    required = profile.get("required_sections", [])
    missing = [s for s in required if s not in artifact]
    if missing:
        return CheckResult(
            check_id="G_REQUIRED_SECTIONS",
            section="top_level",
            verdict=CheckVerdict.FAIL,
            decisive_reason=f"Missing required section(s): {missing}",
            failed_fields=tuple(missing),
            evidence_summary=f"present={[s for s in required if s in artifact]}",
        )
    return CheckResult(
        check_id="G_REQUIRED_SECTIONS",
        section="top_level",
        verdict=CheckVerdict.PASS,
        decisive_reason="All required sections present.",
        evidence_summary=f"sections={required}",
    )


def _check_headline(
    artifact: dict[str, Any],
    profile: dict[str, Any],
) -> CheckResult:
    cfg = profile.get("headline", {})
    max_len = cfg.get("max_length", 200)

    headline = artifact.get("headline")
    if not isinstance(headline, dict):
        return CheckResult(
            check_id="A_HEADLINE",
            section="headline",
            verdict=CheckVerdict.FAIL,
            decisive_reason="headline is missing or not a dict.",
            failed_fields=("headline",),
        )

    text = headline.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return CheckResult(
            check_id="A_HEADLINE",
            section="headline",
            verdict=CheckVerdict.FAIL,
            decisive_reason="headline.text is empty or not a string.",
            failed_fields=("headline.text",),
        )

    if "\n" in text or "\r" in text:
        return CheckResult(
            check_id="A_HEADLINE",
            section="headline",
            verdict=CheckVerdict.FAIL,
            decisive_reason="headline.text contains newline — must be single line.",
            failed_fields=("headline.text",),
            evidence_summary=f"text_repr={repr(text[:80])}",
        )

    if len(text) > max_len:
        return CheckResult(
            check_id="A_HEADLINE",
            section="headline",
            verdict=CheckVerdict.FAIL,
            decisive_reason=f"headline.text exceeds max_length={max_len} (got {len(text)}).",
            failed_fields=("headline.text",),
            evidence_summary=f"length={len(text)}",
        )

    return CheckResult(
        check_id="A_HEADLINE",
        section="headline",
        verdict=CheckVerdict.PASS,
        decisive_reason="Headline is a single non-empty line within length bounds.",
        evidence_summary=f"length={len(text)}",
    )


def _check_executive_summary(
    artifact: dict[str, Any],
    profile: dict[str, Any],
) -> CheckResult:
    cfg = profile.get("executive_summary", {})
    min_len = cfg.get("min_length", 10)
    max_len = cfg.get("max_length", 2000)
    placeholders = {p.upper() for p in cfg.get("empty_placeholder_values", [])}

    es = artifact.get("executive_summary")
    if not isinstance(es, dict):
        return CheckResult(
            check_id="B_EXEC_SUMMARY",
            section="executive_summary",
            verdict=CheckVerdict.FAIL,
            decisive_reason="executive_summary is missing or not a dict.",
            failed_fields=("executive_summary",),
        )

    text = es.get("text", "")
    if not isinstance(text, str):
        return CheckResult(
            check_id="B_EXEC_SUMMARY",
            section="executive_summary",
            verdict=CheckVerdict.FAIL,
            decisive_reason="executive_summary.text is not a string.",
            failed_fields=("executive_summary.text",),
        )

    stripped = text.strip()
    if not stripped or stripped.upper() in placeholders:
        return CheckResult(
            check_id="B_EXEC_SUMMARY",
            section="executive_summary",
            verdict=CheckVerdict.FAIL,
            decisive_reason="executive_summary.text is empty or a placeholder value.",
            failed_fields=("executive_summary.text",),
            evidence_summary=f"value={repr(text[:40])}",
        )

    if len(stripped) < min_len:
        return CheckResult(
            check_id="B_EXEC_SUMMARY",
            section="executive_summary",
            verdict=CheckVerdict.FAIL,
            decisive_reason=f"executive_summary.text too short (min={min_len}, got={len(stripped)}).",
            failed_fields=("executive_summary.text",),
            evidence_summary=f"length={len(stripped)}",
        )

    if len(stripped) > max_len:
        return CheckResult(
            check_id="B_EXEC_SUMMARY",
            section="executive_summary",
            verdict=CheckVerdict.WARN,
            decisive_reason=f"executive_summary.text exceeds max_length={max_len} (got={len(stripped)}).",
            warnings=("executive_summary.text exceeds max_length",),
            evidence_summary=f"length={len(stripped)}",
        )

    return CheckResult(
        check_id="B_EXEC_SUMMARY",
        section="executive_summary",
        verdict=CheckVerdict.PASS,
        decisive_reason="Executive summary is non-empty and within length bounds.",
        evidence_summary=f"length={len(stripped)}",
    )


def _check_roles(
    artifact: dict[str, Any],
    profile: dict[str, Any],
) -> CheckResult:
    cfg = profile.get("roles", {})
    require_employer = cfg.get("require_employer", True)
    require_title = cfg.get("require_title", True)
    require_narrative = cfg.get("require_narrative", True)
    bullet_min = cfg.get("bullet_min_count", 0)
    bullet_max = cfg.get("bullet_max_count", 10)

    roles = artifact.get("roles")
    if roles is None:
        return CheckResult(
            check_id="C_ROLES",
            section="roles",
            verdict=CheckVerdict.FAIL,
            decisive_reason="roles field is missing.",
            failed_fields=("roles",),
        )

    if not isinstance(roles, list):
        return CheckResult(
            check_id="C_ROLES",
            section="roles",
            verdict=CheckVerdict.FAIL,
            decisive_reason="roles is not a list.",
            failed_fields=("roles",),
        )

    failed: list[str] = []
    warnings: list[str] = []

    for i, role in enumerate(roles):
        if not isinstance(role, dict):
            failed.append(f"roles[{i}]: not a dict")
            continue

        if require_employer and not role.get("employer", "").strip():
            failed.append(f"roles[{i}].employer: missing or empty")

        if require_title and not role.get("title", "").strip():
            failed.append(f"roles[{i}].title: missing or empty")

        if require_narrative and not isinstance(role.get("narrative"), str):
            failed.append(f"roles[{i}].narrative: missing or not a string")
        elif require_narrative and not role.get("narrative", "").strip():
            warnings.append(f"roles[{i}].narrative: empty string")

        bullets = role.get("bullets", [])
        if not isinstance(bullets, list):
            failed.append(f"roles[{i}].bullets: not a list")
            continue

        count = len(bullets)
        if count < bullet_min:
            failed.append(f"roles[{i}].bullets: count={count} < min={bullet_min}")
        if count > bullet_max:
            warnings.append(f"roles[{i}].bullets: count={count} > max={bullet_max}")

        seen_ordinals: set[int] = set()
        for j, bullet in enumerate(bullets):
            if not isinstance(bullet, dict):
                failed.append(f"roles[{i}].bullets[{j}]: not a dict")
                continue

            ordinal = bullet.get("ordinal")
            if ordinal is None:
                failed.append(f"roles[{i}].bullets[{j}].ordinal: missing")
            elif not isinstance(ordinal, int) or ordinal < 1:
                failed.append(f"roles[{i}].bullets[{j}].ordinal: invalid ({ordinal!r})")
            elif ordinal in seen_ordinals:
                failed.append(f"roles[{i}].bullets[{j}].ordinal: duplicate ({ordinal})")
            else:
                seen_ordinals.add(ordinal)

            if not bullet.get("source_text") and not bullet.get("rewritten_text"):
                failed.append(
                    f"roles[{i}].bullets[{j}]: no source_text or rewritten_text present"
                )

    if failed:
        return CheckResult(
            check_id="C_ROLES",
            section="roles",
            verdict=CheckVerdict.FAIL,
            decisive_reason=f"{len(failed)} role/bullet field violation(s) found.",
            failed_fields=tuple(failed),
            warnings=tuple(warnings),
            evidence_summary=f"roles_count={len(roles)}, failures={len(failed)}",
        )

    if warnings:
        return CheckResult(
            check_id="C_ROLES",
            section="roles",
            verdict=CheckVerdict.WARN,
            decisive_reason=f"{len(warnings)} role/bullet warning(s) found.",
            warnings=tuple(warnings),
            evidence_summary=f"roles_count={len(roles)}, warnings={len(warnings)}",
        )

    return CheckResult(
        check_id="C_ROLES",
        section="roles",
        verdict=CheckVerdict.PASS,
        decisive_reason="All roles pass structural checks.",
        evidence_summary=f"roles_count={len(roles)}",
    )


def _check_verbatim_preservation(
    artifact: dict[str, Any],
    profile: dict[str, Any],
) -> CheckResult:
    verbatim_sections = profile.get("verbatim_sections", ["education", "certifications", "early_career"])
    hash_cfg = profile.get("hash_check", {})
    warn_when_hash_absent = hash_cfg.get("emit_warn_when_hash_absent", True)

    failed: list[str] = []
    warnings: list[str] = []

    for sec_name in verbatim_sections:
        sec = artifact.get(sec_name)
        if sec is None:
            warnings.append(f"{sec_name}: section absent (WARN — missing verbatim section)")
            continue

        if not isinstance(sec, dict):
            failed.append(f"{sec_name}: not a dict")
            continue

        pv = sec.get("preserve_verbatim")
        if pv is not True:
            failed.append(f"{sec_name}.preserve_verbatim: expected True, got {pv!r}")

        if warn_when_hash_absent:
            entries = sec.get("entries", [])
            for idx, entry in enumerate(entries):
                if not isinstance(entry, dict):
                    continue
                has_hash = "source_hash" in entry or "original_hash" in entry
                if not has_hash:
                    warnings.append(
                        f"{sec_name}.entries[{idx}]: hash fields absent "
                        f"(source_hash/original_hash) — WARN, not PASS-for-hash"
                    )

    for role_idx, role in enumerate(artifact.get("roles", [])):
        if not isinstance(role, dict):
            continue
        pnv = role.get("preserve_narrative_verbatim")
        if pnv is not True and pnv is not None:
            failed.append(
                f"roles[{role_idx}].preserve_narrative_verbatim: "
                f"expected True or absent (default True), got {pnv!r}"
            )
        elif pnv is None:
            pass

    if failed:
        return CheckResult(
            check_id="D_VERBATIM",
            section="verbatim_sections",
            verdict=CheckVerdict.FAIL,
            decisive_reason=f"{len(failed)} verbatim preservation violation(s).",
            failed_fields=tuple(failed),
            warnings=tuple(warnings),
            evidence_summary=f"checked_sections={verbatim_sections}",
        )

    if warnings:
        return CheckResult(
            check_id="D_VERBATIM",
            section="verbatim_sections",
            verdict=CheckVerdict.WARN,
            decisive_reason=f"Verbatim sections present but {len(warnings)} warning(s) (hash fields absent).",
            warnings=tuple(warnings),
            evidence_summary=f"checked_sections={verbatim_sections}",
        )

    return CheckResult(
        check_id="D_VERBATIM",
        section="verbatim_sections",
        verdict=CheckVerdict.PASS,
        decisive_reason="All verbatim sections have preserve_verbatim=True.",
        evidence_summary=f"checked_sections={verbatim_sections}",
    )


def _check_support_status(
    artifact: dict[str, Any],
    profile: dict[str, Any],
) -> CheckResult:
    cfg = profile.get("support_status", {})
    blocking = set(cfg.get("sendable_blocking_values", [
        "INSUFFICIENT_SOURCE_SUPPORT", "BLOCKED", "UNKNOWN"
    ]))
    missing_behavior = cfg.get("missing_support_status_for_rewrite_allowed", "WARN")

    violations: list[str] = []
    warnings: list[str] = []
    unknowns: list[str] = []

    def _scan_value(path: str, val: Any) -> None:
        if isinstance(val, str) and val.upper() in blocking:
            violations.append(f"{path}: support_status={val!r} is blocking")
        elif isinstance(val, str) and val.upper() == "UNKNOWN":
            unknowns.append(f"{path}: support_status=UNKNOWN (never PASS)")

    def _scan_dict(path: str, d: dict[str, Any]) -> None:
        ss = d.get("support_status")
        if ss is not None:
            _scan_value(path, ss)
        elif d.get("rewrite_allowed", False):
            if missing_behavior == "WARN":
                warnings.append(f"{path}: rewrite_allowed=True but support_status absent")
            else:
                unknowns.append(f"{path}: rewrite_allowed=True but support_status absent — treated as UNKNOWN")

    for ri, role in enumerate(artifact.get("roles", [])):
        if not isinstance(role, dict):
            continue
        _scan_dict(f"roles[{ri}]", role)
        for bi, bullet in enumerate(role.get("bullets", [])):
            if not isinstance(bullet, dict):
                continue
            _scan_dict(f"roles[{ri}].bullets[{bi}]", bullet)

    for sec in ("headline", "executive_summary", "competencies"):
        sec_val = artifact.get(sec)
        if isinstance(sec_val, dict):
            _scan_dict(sec, sec_val)

    for vsec in ("education", "certifications", "early_career"):
        sec_val = artifact.get(vsec)
        if isinstance(sec_val, dict):
            for ei, entry in enumerate(sec_val.get("entries", [])):
                if isinstance(entry, dict):
                    _scan_dict(f"{vsec}.entries[{ei}]", entry)

    all_fails = violations + unknowns
    if all_fails:
        return CheckResult(
            check_id="E_SUPPORT_STATUS",
            section="support_status",
            verdict=CheckVerdict.FAIL,
            decisive_reason=f"{len(all_fails)} blocking support_status value(s) found.",
            failed_fields=tuple(all_fails),
            warnings=tuple(warnings),
            evidence_summary=f"blocking={list(blocking)}",
        )

    if warnings:
        return CheckResult(
            check_id="E_SUPPORT_STATUS",
            section="support_status",
            verdict=CheckVerdict.WARN,
            decisive_reason=f"{len(warnings)} missing support_status warning(s).",
            warnings=tuple(warnings),
            evidence_summary=f"blocking={list(blocking)}",
        )

    return CheckResult(
        check_id="E_SUPPORT_STATUS",
        section="support_status",
        verdict=CheckVerdict.PASS,
        decisive_reason="No blocking support_status values found.",
        evidence_summary=f"blocking={list(blocking)}",
    )


def _check_competencies(
    artifact: dict[str, Any],
    profile: dict[str, Any],
) -> CheckResult:
    cfg = profile.get("competencies", {})
    min_words = cfg.get("min_words_per_phrase", 2)
    max_words = cfg.get("max_words_per_phrase", 4)

    comp = artifact.get("competencies")
    if not isinstance(comp, dict):
        return CheckResult(
            check_id="F_COMPETENCIES",
            section="competencies",
            verdict=CheckVerdict.FAIL,
            decisive_reason="competencies is missing or not a dict.",
            failed_fields=("competencies",),
        )

    items = comp.get("items")
    if not isinstance(items, list):
        return CheckResult(
            check_id="F_COMPETENCIES",
            section="competencies",
            verdict=CheckVerdict.FAIL,
            decisive_reason="competencies.items is missing or not a list.",
            failed_fields=("competencies.items",),
        )

    if not items:
        return CheckResult(
            check_id="F_COMPETENCIES",
            section="competencies",
            verdict=CheckVerdict.WARN,
            decisive_reason="competencies.items is empty.",
            warnings=("competencies.items is empty",),
            evidence_summary="count=0",
        )

    failed: list[str] = []
    for idx, phrase in enumerate(items):
        if not isinstance(phrase, str) or not phrase.strip():
            failed.append(f"competencies.items[{idx}]: empty or not a string")
            continue
        word_count = len(phrase.strip().split())
        if word_count < min_words:
            failed.append(
                f"competencies.items[{idx}]={phrase!r}: "
                f"too short ({word_count} word(s), min={min_words})"
            )
        elif word_count > max_words:
            failed.append(
                f"competencies.items[{idx}]={phrase!r}: "
                f"too long ({word_count} words, max={max_words}) — "
                f"must be 2-4 word noun phrase, not a sentence"
            )

    if failed:
        return CheckResult(
            check_id="F_COMPETENCIES",
            section="competencies",
            verdict=CheckVerdict.FAIL,
            decisive_reason=f"{len(failed)} competency phrase(s) violate 2-4 word rule.",
            failed_fields=tuple(failed),
            evidence_summary=f"total={len(items)}, bad={len(failed)}",
        )

    return CheckResult(
        check_id="F_COMPETENCIES",
        section="competencies",
        verdict=CheckVerdict.PASS,
        decisive_reason=f"All {len(items)} competency phrase(s) are 2-4 words.",
        evidence_summary=f"total={len(items)}",
    )


# ---------------------------------------------------------------------------
# Aggregate runner
# ---------------------------------------------------------------------------

def run_exit_checks(
    artifact: dict[str, Any],
    profile: dict[str, Any] | None = None,
) -> ExitCheckSummary:
    """Run all S6 deterministic exit checks against a resume artifact dict.

    Args:
        artifact: Resume artifact as a dict (structured resume format).
        profile:  Optional override profile dict.  Defaults to loading
                  resume_exit_checks_profile.v1.json.

    Returns:
        ExitCheckSummary with overall_verdict, sendable flag, and per-check results.

    UNKNOWN is NEVER PASS. Material UNKNOWN blocks sendable=True.
    """
    if profile is None:
        profile = _load_profile()

    results: list[CheckResult] = [
        _check_required_sections(artifact, profile),
        _check_headline(artifact, profile),
        _check_executive_summary(artifact, profile),
        _check_roles(artifact, profile),
        _check_verbatim_preservation(artifact, profile),
        _check_support_status(artifact, profile),
        _check_competencies(artifact, profile),
    ]

    hard_fail = any(r.verdict == CheckVerdict.FAIL for r in results)
    unknown_material = any(r.verdict == CheckVerdict.UNKNOWN for r in results)
    warn_present = any(r.verdict == CheckVerdict.WARN for r in results)

    if hard_fail:
        overall = CheckVerdict.FAIL
    elif unknown_material:
        overall = CheckVerdict.UNKNOWN
    elif warn_present:
        overall = CheckVerdict.WARN
    else:
        overall = CheckVerdict.PASS

    sendable = (not hard_fail) and (not unknown_material)

    return ExitCheckSummary(
        overall_verdict=overall,
        hard_fail_present=hard_fail,
        unknown_material_present=unknown_material,
        warning_present=warn_present,
        sendable=sendable,
        check_results=tuple(results),
    )
