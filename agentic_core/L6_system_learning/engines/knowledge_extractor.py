"""C6 Knowledge Extractor - Extract patterns for Master Ledger.

10C-REQ-168: Knowledge Extraction pattern library update rule delta
10C-REQ-169: Master Ledger Commit UWG write locking
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import hashlib
import json


@dataclass
class RuleDelta:
    """Delta for rule update."""

    rule_id: str
    previous_version: str
    new_version: str
    change_type: str  # ADD, MODIFY, DELETE
    diff_summary: str
    source_cases: list[str]


@dataclass
class KnowledgePattern:
    """Extracted knowledge pattern."""

    pattern_id: str
    pattern_type: str
    description: str
    supporting_cases: list[str]
    confidence: float
    extracted_at: float


class KnowledgeExtractor:
    """C6 Knowledge Extractor.

    10C-REQ-168/169: Pattern extraction and ledger commit preparation.
    """

    def __init__(self) -> None:
        self._patterns: list[KnowledgePattern] = []
        self._deltas: list[RuleDelta] = []

    def extract_pattern(
        self,
        pattern_type: str,
        description: str,
        supporting_cases: list[str],
        confidence: float,
        timestamp: float,
    ) -> KnowledgePattern:
        """Extract knowledge pattern from learning cases."""
        # Generate pattern ID from content hash
        content = f"{pattern_type}:{description}:{','.join(supporting_cases)}"
        pattern_id = f"PAT-{hashlib.sha256(content.encode()).hexdigest()[:12]}"

        pattern = KnowledgePattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            description=description,
            supporting_cases=supporting_cases,
            confidence=confidence,
            extracted_at=timestamp,
        )

        self._patterns.append(pattern)
        return pattern

    def generate_rule_delta(
        self,
        rule_id: str,
        previous: dict[str, Any],
        new: dict[str, Any],
        source_cases: list[str],
    ) -> RuleDelta:
        """Generate rule delta for Master Ledger commit."""
        prev_version = previous.get("version", "0.0.0")
        new_version = self._bump_version(prev_version)

        # Determine change type
        if not previous:
            change_type = "ADD"
        elif not new:
            change_type = "DELETE"
        else:
            change_type = "MODIFY"

        # Generate diff summary
        diff_keys = set(previous.keys()) | set(new.keys())
        changes = [k for k in diff_keys if previous.get(k) != new.get(k)]
        diff_summary = f"fields_changed:{','.join(changes)}"

        delta = RuleDelta(
            rule_id=rule_id,
            previous_version=prev_version,
            new_version=new_version,
            change_type=change_type,
            diff_summary=diff_summary,
            source_cases=source_cases,
        )

        self._deltas.append(delta)
        return delta

    def _bump_version(self, version: str) -> str:
        """Bump patch version."""
        parts = version.split(".")
        if len(parts) == 3:
            try:
                major, minor, patch = parts
                new_patch = int(patch) + 1
                return f"{major}.{minor}.{new_patch}"
            except ValueError:  # guardian: allow-silent-swallow -- version parse: falls back to default
                pass
        return "1.0.0"

    def prepare_ledger_commit(
        self,
        delta: RuleDelta,
        gauntlet_passed: bool,
    ) -> dict[str, Any] | None:
        """Prepare commit for Master Ledger via UWG.

        10C-REQ-169: UWG write locking required.
        """
        if not gauntlet_passed:
            return None

        return {
            "commit_type": "rule_update",
            "rule_id": delta.rule_id,
            "version": delta.new_version,
            "change_type": delta.change_type,
            "diff_summary": delta.diff_summary,
            "source_cases": delta.source_cases,
            "requires_uwg": True,
            "lock_required": True,
        }

    def get_extraction_stats(self) -> dict[str, Any]:
        """Get extraction statistics."""
        by_type: dict[str, int] = {}
        for p in self._patterns:
            by_type[p.pattern_type] = by_type.get(p.pattern_type, 0) + 1

        return {
            "patterns_extracted": len(self._patterns),
            "deltas_generated": len(self._deltas),
            "by_pattern_type": by_type,
        }
