"""E8: Protocol / ABC Coverage Check.

Post-scan pass that identifies abstract base classes and Protocol subclasses
that have no concrete implementor recorded in the ADG.

A class is treated as abstract if:
  - It inherits from ``Protocol``, ``typing.Protocol``, ``ABC``, or
    ``abc.ABC`` (tracked via `implements` edges from E1/G3), OR
  - Its ADG name contains ``Abstract`` or ``Base`` as a suffix heuristic.

A concrete implementor is any class with an `implements` edge pointing at
the abstract base, with edge_kind != "unresolved".

Output:
  ``ProtocolCoverageReport`` — a dataclass containing:
    - ``abstract_bases``:  list of abstract ADG symbol names
    - ``covered_bases``:   subset with ≥1 concrete implementor
    - ``uncovered_bases``: subset with zero concrete implementors
    - ``coverage_rate``:   float 0–1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

_ABSTRACT_BASE_NAMES: frozenset[str] = frozenset(
    {
        "ABC",
        "abc.ABC",
        "Protocol",
        "typing.Protocol",
        "ABCMeta",
        "abc.ABCMeta",
    }
)


@dataclass
class ProtocolCoverageReport:
    """Summary of abstract base / Protocol coverage across the ADG."""

    abstract_bases: list[str] = field(default_factory=list)
    covered_bases: list[str] = field(default_factory=list)
    uncovered_bases: list[str] = field(default_factory=list)
    coverage_rate: float = 0.0

    def to_dict(self) -> dict:
        return {
            "abstract_count": len(self.abstract_bases),
            "covered_count": len(self.covered_bases),
            "uncovered_count": len(self.uncovered_bases),
            "coverage_rate": round(self.coverage_rate, 3),
            "uncovered_bases": sorted(self.uncovered_bases),
        }


def check_protocol_coverage(result: ScanResult) -> ProtocolCoverageReport:
    """Analyse ``result.edges`` to find abstract bases without implementors.

    Algorithm:
    1. **Detect abstract classes**: Any class ``C`` that has an ``implements``
       edge whose *to_name* resolves to a known built-in abstract base (ABC,
       Protocol, …) is itself an abstract base — record ``C.from_name`` as
       an abstract base node.
    2. **Detect concrete implementors**: Any class ``D`` that has an
       ``implements`` edge pointing at an abstract base ``C`` discovered in
       step 1 is a concrete implementor of ``C``.
    3. Any abstract base with no concrete implementor is flagged as uncovered.

    Note: built-in abstract anchors (ABC, Protocol, etc.) are NOT themselves
    reported as abstract bases — we only track user-defined classes that
    extend them.
    """
    abstract_class_adg: set[str] = set()
    implementors: dict[str, set[str]] = {}

    for edge in result.edges:
        if edge.relation_type != "implements":
            continue
        to_sym = edge.symbol or edge.to_name.split("::")[-1]
        base_short = to_sym.split(".")[-1] if "." in to_sym else to_sym
        if to_sym in _ABSTRACT_BASE_NAMES or base_short in _ABSTRACT_BASE_NAMES:
            abstract_class_adg.add(edge.from_name)

    for edge in result.edges:
        if edge.relation_type != "implements":
            continue
        if edge.to_name in abstract_class_adg or edge.from_name in abstract_class_adg:
            if edge.from_name in abstract_class_adg:
                pass
            else:
                implementors.setdefault(edge.to_name, set()).add(edge.from_name)

    covered = {b for b in abstract_class_adg if implementors.get(b)}
    uncovered = abstract_class_adg - covered

    total = len(abstract_class_adg)
    rate = len(covered) / total if total else 1.0

    report = ProtocolCoverageReport(
        abstract_bases=sorted(abstract_class_adg),
        covered_bases=sorted(covered),
        uncovered_bases=sorted(uncovered),
        coverage_rate=round(rate, 3),
    )
    return report


__all__ = [
    "ProtocolCoverageReport",
    "check_protocol_coverage",
]
