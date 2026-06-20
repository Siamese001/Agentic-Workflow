"""apps_architect type definitions — Pattern, PatternCollection, delta types.

Plan: ``.codex/plans/apps-architect-pattern-hardening-d7e4f9.md`` W3.P1.
Brought forward to W2 as engines depend on Pattern objects.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Tuple


class PatternType(str, Enum):
    PLAN = "PLAN"
    RULE = "RULE"
    CORE = "CORE"
    LAYER = "LAYER"
    ADG_VIOLATION = "ADG_VIOLATION"
    SKILL = "SKILL"


class DeltaType(str, Enum):
    NEW_PATTERN = "NEW_PATTERN"
    STALE_PATTERN = "STALE_PATTERN"
    MISSING_PATTERN = "MISSING_PATTERN"
    DRIFT_DETECTED = "DRIFT_DETECTED"


class Severity(str, Enum):
    ADVISORY = "advisory"
    RECOMMENDED = "recommended"
    REQUIRED = "required"


@dataclass(frozen=True)
class Pattern:
    pattern_id: str
    pattern_type: PatternType
    source_ref: str
    content_digest: str
    first_seen: datetime
    last_seen: datetime
    schema_version: str = "1.0"
    summary: str = ""
    tags: Tuple[str, ...] = ()

    @classmethod
    def from_source(
        cls,
        pattern_type: PatternType,
        source_ref: str,
        content: str,
        summary: str = "",
        tags: Tuple[str, ...] = (),
    ) -> Pattern:
        now = datetime.now(timezone.utc)
        content_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        pattern_id = hashlib.sha256(
            f"{source_ref}:{content_digest}".encode("utf-8")
        ).hexdigest()[:12]
        return cls(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            source_ref=source_ref,
            content_digest=content_digest,
            first_seen=now,
            last_seen=now,
            summary=summary,
            tags=tags,
        )


@dataclass(frozen=True)
class PatternCollection:
    patterns: Tuple[Pattern, ...]
    collection_digest: str
    scan_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_patterns(cls, patterns: Tuple[Pattern, ...]) -> PatternCollection:
        combined = "|".join(sorted(p.pattern_id for p in patterns))
        digest = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]
        return cls(patterns=patterns, collection_digest=digest)


@dataclass(frozen=True)
class DeltaEntry:
    delta_type: DeltaType
    pattern: Pattern
    current_state: str = ""
    recommendation: str = ""
    severity: Severity = Severity.ADVISORY


@dataclass(frozen=True)
class DeltaReport:
    entries: Tuple[DeltaEntry, ...]
    scan_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_patterns: int = 0
    new_count: int = 0
    stale_count: int = 0
    missing_count: int = 0
    drift_count: int = 0


__all__ = [
    "PatternType",
    "DeltaType",
    "Severity",
    "Pattern",
    "PatternCollection",
    "DeltaEntry",
    "DeltaReport",
]
