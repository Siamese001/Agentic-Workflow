"""Protocol / ABC Coverage Analysis — E8 enhancement.

Detects abstract bases (classes extending Protocol or ABC) and checks
whether they have concrete implementors in the scanned codebase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

_ABSTRACT_MARKERS = frozenset({"Protocol", "ABC", "ABCMeta"})


@dataclass
class ProtocolCoverageReport:
    """Result of a protocol/ABC coverage check."""

    abstract_bases: set[str] = field(default_factory=set)
    covered_bases: set[str] = field(default_factory=set)
    uncovered_bases: set[str] = field(default_factory=set)
    implementors: dict[str, list[str]] = field(default_factory=dict)

    @property
    def coverage_rate(self) -> float:
        if not self.abstract_bases:
            return 1.0
        return len(self.covered_bases) / len(self.abstract_bases)


def check_protocol_coverage(scan_result: ScanResult) -> ProtocolCoverageReport:
    """Analyse *scan_result* edges to find abstract bases and their implementors.

    Pass 1 — identify abstract bases:
        Any class C that has an ``implements`` edge whose target symbol is in
        ``_ABSTRACT_MARKERS`` (e.g. ``Protocol``, ``ABC``) is considered abstract.

    Pass 2 — identify concrete implementors:
        Any class D that has an ``implements`` edge whose target is one of the
        abstract bases found in Pass 1 counts as a concrete implementor.
    """
    report = ProtocolCoverageReport()

    # Pass 1: find abstract bases
    for edge in scan_result.edges:
        if edge.relation_type != "implements":
            continue
        target_short = edge.to_name.rsplit("::", 1)[-1] if "::" in edge.to_name else edge.to_name
        if target_short in _ABSTRACT_MARKERS:
            report.abstract_bases.add(edge.from_name)

    # Pass 2: find concrete implementors of abstract bases
    for edge in scan_result.edges:
        if edge.relation_type != "implements":
            continue
        if edge.to_name in report.abstract_bases:
            report.covered_bases.add(edge.to_name)
            report.implementors.setdefault(edge.to_name, []).append(edge.from_name)

    report.uncovered_bases = report.abstract_bases - report.covered_bases
    return report


__all__ = [
    "ProtocolCoverageReport",
    "check_protocol_coverage",
]
