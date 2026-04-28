"""PDP — ADG-first dependency analysis decision (P6).

Pure decision primitive extracted from ``post_cascade_adg_audit.py``. The
hook remains the PEP (reads stdin, writes to violation log, decides exit
code). This module is the PDP: given observed facts about a Cascade
response, produce a verdict.

Constitutional §28: the fallback ladder is
    (1) adg_sqlite MCP  → (2) direct SQLite  → (3) grep (only after 1+2 fail)

Verdicts:
    COMPLIANT        — ADG MCP or direct SQLite used; no grep-for-deps
    INFO_BYPASS      — bypass env set; log but do not flag
    WARNING          — ADG MCP used AND grep appeared (possibly supplementary)
    ERROR            — partial compliance (health checked but no SQLite tier)
    CRITICAL_SILENT  — grep-for-deps with no §28 excuse (silent fallback)
    CRITICAL_SKIP_SQLITE — grep used when SQLite snapshot was reachable

No I/O, no subprocess, no env access in this module. All inputs are
observed facts passed in by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AdgFirstVerdict(str, Enum):
    COMPLIANT = "compliant"
    INFO_BYPASS = "info_bypass"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL_SILENT = "critical_silent"
    CRITICAL_SKIP_SQLITE = "critical_skip_sqlite"


@dataclass(frozen=True)
class AdgFirstDecision:
    """Decision packet emitted by the ADG-first PDP.

    Attributes:
        verdict: Categorical verdict (see AdgFirstVerdict).
        severity: String label matching the post_cascade_adg_audit log
            format ("info", "warning", "error", "critical").
        is_blocking: True when enforcement should exit 2 (block the
            response). False for advisory outcomes.
        rationale: Short human-readable explanation suitable for log
            records and stderr banners.
    """

    verdict: AdgFirstVerdict
    severity: str
    is_blocking: bool
    rationale: str


def classify_grep_for_deps(
    *,
    grep_for_deps_present: bool,
    adg_mcp_used: bool,
    adg_health_checked: bool,
    degraded_fallback_declared: bool,
    sqlite_direct_used: bool,
    adg_snapshot_present: bool,
    bypass_set: bool,
) -> AdgFirstDecision:
    """Classify a Cascade response's ADG-first compliance.

    All inputs are booleans describing observed facts. Returns a single
    decision packet. Caller (PEP) is responsible for logging and exit-code
    enforcement.
    """
    if not grep_for_deps_present:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.COMPLIANT,
            severity="info",
            is_blocking=False,
            rationale="no grep-for-deps invocations detected",
        )

    if bypass_set:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.INFO_BYPASS,
            severity="info",
            is_blocking=False,
            rationale="ADG_SQLITE_FALLBACK_BYPASS env var set",
        )

    if sqlite_direct_used and adg_mcp_used:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.COMPLIANT,
            severity="info",
            is_blocking=False,
            rationale="compliant §28: both MCP and SQLite tiers exercised",
        )

    if sqlite_direct_used:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.COMPLIANT,
            severity="info",
            is_blocking=False,
            rationale="compliant §28: direct SQLite used",
        )

    if adg_mcp_used:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.WARNING,
            severity="warning",
            is_blocking=False,
            rationale="ADG MCP used; grep appeared (possibly supplementary)",
        )

    if adg_snapshot_present:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.CRITICAL_SKIP_SQLITE,
            severity="critical",
            is_blocking=True,
            rationale="§28 violation: ADG SQLite snapshot reachable but grep used",
        )

    if adg_health_checked and degraded_fallback_declared:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.COMPLIANT,
            severity="info",
            is_blocking=False,
            rationale="compliant legacy protocol: health + DEGRADED_FALLBACK reason",
        )

    if adg_health_checked or degraded_fallback_declared:
        return AdgFirstDecision(
            verdict=AdgFirstVerdict.ERROR,
            severity="error",
            is_blocking=False,
            rationale="partial compliance: only one of (health check, fallback reason)",
        )

    return AdgFirstDecision(
        verdict=AdgFirstVerdict.CRITICAL_SILENT,
        severity="critical",
        is_blocking=True,
        rationale="silent fallback: no ADG MCP, no health check, no DEGRADED_FALLBACK reason",
    )
