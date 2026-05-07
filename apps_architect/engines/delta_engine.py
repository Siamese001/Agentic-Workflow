"""Delta computation engine — compares patterns against repo reality.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W3.P2.

Compares a PatternCollection (from scanners) against the current repo state
to detect drift, missing patterns, stale patterns, and new patterns.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from apps_architect.types.architect_types import (
    DeltaEntry,
    DeltaReport,
    DeltaType,
    Pattern,
    PatternCollection,
    Severity,
)

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _file_exists_and_digest(source_ref: str) -> tuple[bool, str]:
    """Check if a source file exists and return its SHA256 digest."""
    try:
        fp = _REPO_ROOT / source_ref
        if fp.exists():
            content = fp.read_bytes()
            digest = hashlib.sha256(content).hexdigest()[:16]
            return True, digest
    except Exception:
        pass
    return False, ""


def _rule_file_has_pattern(source_ref: str, pattern: Pattern) -> bool:
    """Check if a rule file contains the pattern's content markers."""
    try:
        fp = _REPO_ROOT / source_ref
        if not fp.exists():
            return False
        text = fp.read_text(encoding="utf-8")
        return pattern.summary.lower() in text.lower() or pattern.content_digest in text
    except Exception:
        return False


class DeltaEngine:
    """Computes delta between collected patterns and current repo state."""

    def __init__(self, repo_root: str | Path | None = None) -> None:
        self._repo_root = Path(repo_root) if repo_root else _REPO_ROOT

    def compute(self, collection: PatternCollection) -> DeltaReport:
        entries: list[DeltaEntry] = []
        new_count = stale_count = missing_count = drift_count = 0

        for pattern in collection.patterns:
            entry = self._classify(pattern)
            entries.append(entry)
            if entry.delta_type == DeltaType.NEW_PATTERN:
                new_count += 1
            elif entry.delta_type == DeltaType.STALE_PATTERN:
                stale_count += 1
            elif entry.delta_type == DeltaType.MISSING_PATTERN:
                missing_count += 1
            elif entry.delta_type == DeltaType.DRIFT_DETECTED:
                drift_count += 1

        return DeltaReport(
            entries=tuple(entries),
            total_patterns=len(collection.patterns),
            new_count=new_count,
            stale_count=stale_count,
            missing_count=missing_count,
            drift_count=drift_count,
        )

    def _classify(self, pattern: Pattern) -> DeltaEntry:
        source_ref = pattern.source_ref

        if source_ref.startswith("adg:"):
            return DeltaEntry(
                delta_type=DeltaType.NEW_PATTERN,
                pattern=pattern,
                current_state="ADG-derived pattern — structural truth",
                recommendation=f"Review ADG hotspot: {pattern.summary}",
                severity=Severity.ADVISORY,
            )

        exists, current_digest = _file_exists_and_digest(source_ref)
        if not exists:
            return DeltaEntry(
                delta_type=DeltaType.MISSING_PATTERN,
                pattern=pattern,
                current_state=f"Source file not found: {source_ref}",
                recommendation=f"Create or restore: {source_ref}",
                severity=Severity.RECOMMENDED,
            )

        if current_digest != pattern.content_digest:
            return DeltaEntry(
                delta_type=DeltaType.DRIFT_DETECTED,
                pattern=pattern,
                current_state=f"Content changed (digest: {current_digest})",
                recommendation=f"Review drift in {source_ref}",
                severity=Severity.ADVISORY,
            )

        return DeltaEntry(
            delta_type=DeltaType.NEW_PATTERN,
            pattern=pattern,
            current_state="Pattern exists and matches",
            recommendation="No action needed",
            severity=Severity.ADVISORY,
        )


__all__ = ["DeltaEngine"]
