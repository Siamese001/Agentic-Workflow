"""E25: Prompt Drift Detector.

Extends E7 (historical graph diff) to the prompt governance plane.
Compares two ScanResults or snapshots to identify:
  - New prompt generators (modules that started producing prompts)
  - Removed prompt generators (modules that stopped producing prompts)
  - Changed slot types (module now generates different slots)
  - New prompt consumers (modules that started consuming prompts)
  - Removed prompt consumers
  - Authority violations introduced by the diff

Output:
  ``PromptDriftReport`` with:
    - ``added_generators``: new generates_prompt edges
    - ``removed_generators``: removed generates_prompt edges
    - ``added_consumers``: new consumes_prompt edges
    - ``removed_consumers``: removed consumes_prompt edges
    - ``authority_delta``: new violations in the new scan vs old scan
    - ``summary``: human-readable drift summary

Usage::

    from agentic_core.adg.analysis.prompt_drift import detect_prompt_drift

    report = detect_prompt_drift(old_result, new_result)
    print(report.summary)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.contracts.schema_util import PROMPT_SLOT_TYPES

# Configuration constants

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

_MODULE_PREFIX = "ADG::Module::"
_PROMPT_RELATIONS = frozenset(
    {"generates_prompt", "consumes_prompt", "assembles_into", "injects_into", "overrides_prompt"},
)


@dataclass
class PromptEdgeDelta:
    """A single added or removed prompt governance edge."""

    delta: str  # "added" or "removed"
    relation_type: str
    from_module: str
    to_name: str
    slot_type: str
    source_file: str
    line_no: int

    def to_dict(self) -> dict:
        return {
            "delta": self.delta,
            "relation_type": self.relation_type,
            "from_module": self.from_module,
            "to_name": self.to_name,
            "slot_type": self.slot_type,
            "source_file": self.source_file,
            "line_no": self.line_no,
        }


@dataclass
class PromptDriftReport:
    """Prompt governance diff between two scan states."""

    added_generators: list[PromptEdgeDelta] = field(default_factory=list)
    removed_generators: list[PromptEdgeDelta] = field(default_factory=list)
    added_consumers: list[PromptEdgeDelta] = field(default_factory=list)
    removed_consumers: list[PromptEdgeDelta] = field(default_factory=list)
    added_assembly: list[PromptEdgeDelta] = field(default_factory=list)
    removed_assembly: list[PromptEdgeDelta] = field(default_factory=list)
    high_risk_changes: list[PromptEdgeDelta] = field(default_factory=list)
    total_added: int = 0
    total_removed: int = 0

    @property
    def summary(self) -> str:
        return (
            f"Prompt drift: +{self.total_added} edges, -{self.total_removed} edges | "
            f"generators: +{len(self.added_generators)}/-{len(self.removed_generators)} | "
            f"consumers: +{len(self.added_consumers)}/-{len(self.removed_consumers)} | "
            f"high_risk: {len(self.high_risk_changes)}"
        )

    def to_dict(self) -> dict:
        return {
            "total_added": self.total_added,
            "total_removed": self.total_removed,
            "high_risk_change_count": len(self.high_risk_changes),
            "summary": self.summary,
            "added_generators": [e.to_dict() for e in self.added_generators],
            "removed_generators": [e.to_dict() for e in self.removed_generators],
            "added_consumers": [e.to_dict() for e in self.added_consumers],
            "removed_consumers": [e.to_dict() for e in self.removed_consumers],
            "added_assembly": [e.to_dict() for e in self.added_assembly],
            "removed_assembly": [e.to_dict() for e in self.removed_assembly],
            "high_risk_changes": [e.to_dict() for e in self.high_risk_changes],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def _extract_slot(symbol: str, to_name: str) -> str:
    """Extract slot type from edge symbol or to_name."""
    if ":" in symbol:
        candidate = symbol.split(":")[0]
        if candidate in PROMPT_SLOT_TYPES:
            return candidate
    # Try from to_name: ADG::PromptSlot::S0::...
    parts = to_name.split("::")
    for part in parts:
        if part in PROMPT_SLOT_TYPES:
            return part
    return ""


def _build_prompt_edge_set(result: ScanResult) -> set[tuple[str, str, str, str]]:
    """Build a frozenset of (from_module, relation_type, to_name, slot_type) tuples."""
    edges: set[tuple[str, str, str, str]] = set()
    for edge in result.edges:
        if edge.relation_type not in _PROMPT_RELATIONS:
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        mod = edge.from_name[len(_MODULE_PREFIX) :]
        slot = _extract_slot(edge.symbol or "", edge.to_name)
        edges.add((mod, edge.relation_type, edge.to_name, slot))
    return edges


def _build_edge_detail_map(result: ScanResult) -> dict[tuple[str, str, str, str], tuple[str, int]]:
    """Map (from_module, relation, to_name, slot) -> (source_file, line_no)."""
    detail: dict[tuple[str, str, str, str], tuple[str, int]] = {}
    for edge in result.edges:
        if edge.relation_type not in _PROMPT_RELATIONS:
            continue
        if not edge.from_name.startswith(_MODULE_PREFIX):
            continue
        mod = edge.from_name[len(_MODULE_PREFIX) :]
        slot = _extract_slot(edge.symbol or "", edge.to_name)
        key = (mod, edge.relation_type, edge.to_name, slot)
        detail[key] = (edge.source_file, edge.line_no)
    return detail


_HIGH_RISK_SLOTS = frozenset({"S0", "D0"})
_HIGH_RISK_RELATIONS = frozenset({"generates_prompt", "overrides_prompt"})


def _is_high_risk(delta: PromptEdgeDelta) -> bool:
    return (
        delta.slot_type in _HIGH_RISK_SLOTS
        or delta.relation_type in _HIGH_RISK_RELATIONS
        or delta.delta == "removed"
        and delta.relation_type == "generates_prompt"
        and delta.slot_type in _HIGH_RISK_SLOTS
    )


def detect_prompt_drift(old_result: ScanResult, new_result: ScanResult) -> PromptDriftReport:
    """Compare two scan results and produce a prompt governance drift report.

    Identifies all added and removed prompt governance edges between scans,
    classifies them by slot type and relation, and flags high-risk changes
    (any modification to S0/D0 slots or authority override edges).
    """
    old_edges = _build_prompt_edge_set(old_result)
    new_edges = _build_prompt_edge_set(new_result)
    old_detail = _build_edge_detail_map(old_result)
    new_detail = _build_edge_detail_map(new_result)

    added_keys = new_edges - old_edges
    removed_keys = old_edges - new_edges

    def _make_delta(key: tuple[str, str, str, str], delta_type: str, detail_map: dict) -> PromptEdgeDelta:
        mod, relation, to_name, slot = key
        source_file, line_no = detail_map.get(key, (mod, 0))
        return PromptEdgeDelta(
            delta=delta_type,
            relation_type=relation,
            from_module=mod,
            to_name=to_name,
            slot_type=slot,
            source_file=source_file,
            line_no=line_no,
        )

    added_generators: list[PromptEdgeDelta] = []
    removed_generators: list[PromptEdgeDelta] = []
    added_consumers: list[PromptEdgeDelta] = []
    removed_consumers: list[PromptEdgeDelta] = []
    added_assembly: list[PromptEdgeDelta] = []
    removed_assembly: list[PromptEdgeDelta] = []
    high_risk: list[PromptEdgeDelta] = []

    for key in sorted(added_keys):
        delta = _make_delta(key, "added", new_detail)
        if key[1] == "generates_prompt":
            added_generators.append(delta)
        elif key[1] == "consumes_prompt":
            added_consumers.append(delta)
        elif key[1] in ("assembles_into", "injects_into"):
            added_assembly.append(delta)
        if _is_high_risk(delta):
            high_risk.append(delta)

    for key in sorted(removed_keys):
        delta = _make_delta(key, "removed", old_detail)
        if key[1] == "generates_prompt":
            removed_generators.append(delta)
        elif key[1] == "consumes_prompt":
            removed_consumers.append(delta)
        elif key[1] in ("assembles_into", "injects_into"):
            removed_assembly.append(delta)
        if _is_high_risk(delta):
            high_risk.append(delta)

    return PromptDriftReport(
        added_generators=added_generators,
        removed_generators=removed_generators,
        added_consumers=added_consumers,
        removed_consumers=removed_consumers,
        added_assembly=added_assembly,
        removed_assembly=removed_assembly,
        high_risk_changes=high_risk,
        total_added=len(added_keys),
        total_removed=len(removed_keys),
    )


__all__ = [
    "PromptDriftReport",
    "PromptEdgeDelta",
    "detect_prompt_drift",
]
