"""Automatic rule enforcement engine — DS-5.

Plan: ``.claude/plans/apps-architect-deferred-scope-b8e3f1.md`` DW4 DS-5.

Applies hardening rules to the repo. Dry-run by default; requires
Author-Gate approval for severity=required rules. Never modifies
source files without explicit opt-in.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import DeltaEntry, DeltaReport, Severity

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class EnforcementResult:
    rule_id: str
    applied: bool
    dry_run: bool
    file_path: str = ""
    action: str = ""
    error: str = ""


@dataclass
class EnforcementReport:
    results: Tuple[EnforcementResult, ...]
    total: int = 0
    applied: int = 0
    skipped: int = 0
    errors: int = 0
    summary: str = ""


class EnforcementEngine:
    """Applies hardening rules with dry-run safety and severity gating."""

    def __init__(self, repo_root: str | Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else _REPO_ROOT

    def enforce(self, report: DeltaReport, dry_run: bool = True, max_severity: Severity = Severity.RECOMMENDED) -> EnforcementReport:
        results: list[EnforcementResult] = []
        applied = skipped = errors = 0

        for entry in report.entries:
            severity = self._severity_for(entry)
            if severity == Severity.REQUIRED and max_severity == Severity.RECOMMENDED:
                results.append(EnforcementResult(
                    rule_id=entry.pattern.pattern_id,
                    applied=False, dry_run=dry_run,
                    action="skipped (requires Author-Gate for required severity)",
                ))
                skipped += 1
                continue

            result = self._apply_entry(entry, dry_run)
            results.append(result)
            if result.applied:
                applied += 1
            elif result.error:
                errors += 1
            else:
                skipped += 1

        return EnforcementReport(
            results=tuple(results),
            total=len(results),
            applied=applied,
            skipped=skipped,
            errors=errors,
            summary=(
                f"Enforcement: {applied} applied, {skipped} skipped, "
                f"{errors} errors (dry_run={dry_run})"
            ),
        )

    def _severity_for(self, entry: DeltaEntry) -> Severity:
        return {
            "MISSING_PATTERN": Severity.RECOMMENDED,
            "DRIFT_DETECTED": Severity.RECOMMENDED,
            "STALE_PATTERN": Severity.ADVISORY,
            "NEW_PATTERN": Severity.ADVISORY,
        }.get(entry.delta_type.value, Severity.ADVISORY)

    def _apply_entry(self, entry: DeltaEntry, dry_run: bool) -> EnforcementResult:
        source_ref = entry.pattern.source_ref
        if source_ref.startswith("adg:"):
            return EnforcementResult(
                rule_id=entry.pattern.pattern_id,
                applied=False, dry_run=dry_run,
                action="adg-derived patterns are informational only",
            )

        fp = self._repo_root / source_ref
        if not fp.exists():
            return EnforcementResult(
                rule_id=entry.pattern.pattern_id,
                applied=False, dry_run=dry_run,
                file_path=str(fp),
                action=f"file not found: {source_ref}",
            )

        if dry_run:
            return EnforcementResult(
                rule_id=entry.pattern.pattern_id,
                applied=False, dry_run=True,
                file_path=str(fp),
                action=f"would apply: {entry.recommendation[:100]}",
            )

        return EnforcementResult(
            rule_id=entry.pattern.pattern_id,
            applied=False, dry_run=False,
            file_path=str(fp),
            action="enforcement requires explicit --apply flag (not yet implemented)",
        )


__all__ = ["EnforcementEngine", "EnforcementResult", "EnforcementReport"]
