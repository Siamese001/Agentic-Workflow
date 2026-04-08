"""Anti-pattern registry runtime — pure in-memory registry with deduplication.

Tracks every anti-pattern occurrence detected by the ADG static scanner:
  caller → registers_antipattern → AntipatternRegistry
  caller → classifies_antipattern → PatternClassifier

Data structures only — no side-effects on import. No telemetry emitters.
Telemetry is handled by antipattern_telemetry.py adapter (optional).
"""

from __future__ import annotations

import threading

from agentic_core.adg.runtime.antipattern_types import (
    _SEVERITY_MAP,
    AntipatternCategory,
    AntipatternRecord,
    AntipatternRegistryReport,
    AntipatternSeverity,
    SuppressionRecord,
)

# Re-export for backward compatibility
__all__ = [
    "AntipatternSeverity",
    "AntipatternCategory",
    "AntipatternRecord",
    "AntipatternRegistryReport",
    "SuppressionRecord",
    "AntipatternRegistry",
]


class AntipatternRegistry:
    """G21 runtime registry: records and classifies anti-pattern occurrences.

    Pure in-memory registry with:
    - Deterministic fingerprinting (no UUID, no wall-clock)
    - Thread-safe operations
    - Deduplication by fingerprint
    - Suppression with audit trail (reason required)

    Lifecycle:
        registry = AntipatternRegistry(agent_id, run_id)
        registry.register(AntipatternCategory.SILENT_EXCEPTION_SWALLOW, "foo.py", 42)
        registry.suppress(record, reason="false positive", reviewer="alice")
        report = registry.snapshot()
    """

    def __init__(self, agent_id: str, run_id: str) -> None:
        self._agent_id = agent_id
        self._run_id = run_id
        self._report = AntipatternRegistryReport(agent_id=agent_id, run_id=run_id)
        self._lock = threading.Lock()
        self._fingerprints: set[str] = set()

    @property
    def report(self) -> AntipatternRegistryReport:
        """Return the current report (direct reference, not a copy).

        For a thread-safe snapshot, use snapshot() instead.
        """
        return self._report

    def register(
        self,
        category: AntipatternCategory,
        source_file: str = "",
        line_start: int = 0,
        line_end: int = 0,
        column_start: int = 0,
        symbol: str = "",
        description: str = "",
        severity: AntipatternSeverity | None = None,
        rule_id: str = "",
        scanner: str = "",
        evidence_hash: str = "",
    ) -> AntipatternRecord:
        """Register a detected anti-pattern with deduplication.

        Returns the existing record if this fingerprint was already registered,
        otherwise creates and returns a new record.

        Thread-safe.
        """
        resolved_severity = severity or _SEVERITY_MAP.get(category, AntipatternSeverity.MEDIUM)

        record = AntipatternRecord(
            agent_id=self._agent_id,
            run_id=self._run_id,
            category=category,
            severity=resolved_severity,
            source_file=source_file,
            line_start=line_start,
            line_end=line_end,
            column_start=column_start,
            symbol=symbol,
            description=description,
            rule_id=rule_id,
            scanner=scanner,
            evidence_hash=evidence_hash,
        )

        with self._lock:
            if record.fingerprint in self._fingerprints:
                # Return existing record with same fingerprint
                for existing in self._report.records:
                    if existing.fingerprint == record.fingerprint:
                        return existing
            # New record
            self._fingerprints.add(record.fingerprint)
            self._report.records.append(record)
            return record

    def suppress(
        self,
        record: AntipatternRecord,
        reason: str,
        reviewer: str = "",
        ticket: str = "",
    ) -> None:
        """Mark a detected anti-pattern as reviewed and suppressed.

        Requires a reason string for audit trail.

        Thread-safe.
        """
        if not reason:
            raise ValueError("Suppress requires a reason for audit trail")

        suppression = SuppressionRecord(reason=reason, reviewer=reviewer, ticket=ticket)

        with self._lock:
            # Find the record in our report and update it
            found = False
            for r in self._report.records:
                if r.fingerprint == record.fingerprint:
                    r.suppression = suppression
                    found = True
                    break
            if not found:
                raise ValueError(f"Record with fingerprint {record.fingerprint} not found in registry")

    def classify(self, edge_kind: str) -> AntipatternCategory | None:
        """Map an ADG edge kind string to an AntipatternCategory, or None if not a pattern."""
        # Exact match first
        for cat in AntipatternCategory:
            if cat.value == edge_kind:
                return cat
        # Fallback: normalized match (underscores to hyphens, etc.)
        normalized = edge_kind.replace("-", "_").lower()
        for cat in AntipatternCategory:
            if cat.value.replace("-", "_").lower() == normalized:
                return cat
        return None

    def register_from_edge_kind(
        self,
        edge_kind: str,
        source_file: str = "",
        line_start: int = 0,
        line_end: int = 0,
        symbol: str = "",
    ) -> AntipatternRecord | None:
        """Convenience: register an anti-pattern directly from an ADG edge kind string."""
        category = self.classify(edge_kind)
        if category is None:
            return None
        return self.register(
            category,
            source_file=source_file,
            line_start=line_start,
            line_end=line_end,
            symbol=symbol,
        )

    def snapshot(self) -> AntipatternRegistryReport:
        """Return a thread-safe copy of the current report.

        Use this for read operations that need isolation from concurrent writes.
        """
        with self._lock:
            return AntipatternRegistryReport(
                agent_id=self._agent_id,
                run_id=self._run_id,
                records=list(self._report.records),  # Copy the list
            )
