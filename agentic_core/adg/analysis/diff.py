"""Enhancement 7: Historical graph diff engine.

Compares two CanonicalSnapshots (ADG(t-1) vs ADG(t)) and emits a
structured GraphDiff with:
  - new_edges / removed_edges
  - new_violations / resolved_violations
  - new_coverage / removed_coverage
  - risk_delta (signed int: positive = more violations)
  - summary string for CI output
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "diff", "p0_governance")
_emit_reads_policy_state("p0", "diff", "policy_binding")
_emit_snapshots_state("p0", "diff", "state_snapshot")
emit_replay_key("p0", "diff")
emit_determinism_digest("p0", "diff")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

if TYPE_CHECKING:
    from agentic_core.adg.analysis.snapshot import CanonicalSnapshot
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class GraphDiff:
    """Structured diff between two ADG snapshots.

    All edge lists contain (from_name, relation_type, to_name) tuples.
    """

    commit_before: str = ""
    commit_after: str = ""
    hash_before: str = ""
    hash_after: str = ""

    new_edges: list[tuple[str, str, str]] = field(default_factory=list)
    removed_edges: list[tuple[str, str, str]] = field(default_factory=list)

    new_violations: list[tuple[str, str, str]] = field(default_factory=list)
    resolved_violations: list[tuple[str, str, str]] = field(default_factory=list)

    new_coverage: list[tuple[str, str, str]] = field(default_factory=list)
    removed_coverage: list[tuple[str, str, str]] = field(default_factory=list)

    new_calls: list[tuple[str, str, str]] = field(default_factory=list)
    removed_calls: list[tuple[str, str, str]] = field(default_factory=list)

    new_governance: list[tuple[str, str, str]] = field(default_factory=list)
    removed_governance: list[tuple[str, str, str]] = field(default_factory=list)

    node_delta: int = 0
    edge_delta: int = 0
    risk_delta: int = 0

    is_identical: bool = False

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GraphDiff.summary")

        if self.is_identical:
            return f"ADG unchanged (hash={self.hash_after[:12]})"
        parts = []
        if self.new_edges:
            parts.append(f"+{len(self.new_edges)} edges")
        if self.removed_edges:
            parts.append(f"-{len(self.removed_edges)} edges")
        if self.new_violations:
            parts.append(f"+{len(self.new_violations)} violations")
        if self.resolved_violations:
            parts.append(f"-{len(self.resolved_violations)} violations (resolved)")
        if self.risk_delta > 0:
            parts.append(f"risk_delta=+{self.risk_delta} [WORSE]")
        elif self.risk_delta < 0:
            parts.append(f"risk_delta={self.risk_delta} [IMPROVED]")
        return "ADG diff: " + ", ".join(parts) if parts else "ADG: structural changes (no violations)"

    def to_dict(self) -> dict:
        return {
            "commit_before": self.commit_before,
            "commit_after": self.commit_after,
            "hash_before": self.hash_before,
            "hash_after": self.hash_after,
            "is_identical": self.is_identical,
            "node_delta": self.node_delta,
            "edge_delta": self.edge_delta,
            "risk_delta": self.risk_delta,
            "summary": self.summary,
            "new_edges": [list(e) for e in self.new_edges],
            "removed_edges": [list(e) for e in self.removed_edges],
            "new_violations": [list(e) for e in self.new_violations],
            "resolved_violations": [list(e) for e in self.resolved_violations],
            "new_coverage": [list(e) for e in self.new_coverage],
            "removed_coverage": [list(e) for e in self.removed_coverage],
            "new_calls": [list(e) for e in self.new_calls],
            "removed_calls": [list(e) for e in self.removed_calls],
            "new_governance": [list(e) for e in self.new_governance],
            "removed_governance": [list(e) for e in self.removed_governance],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def diff_snapshots(before: CanonicalSnapshot, after: CanonicalSnapshot) -> GraphDiff:
    """Compute a structured GraphDiff between two CanonicalSnapshots.

    Args:
        before: The older snapshot (ADG at t-1).
        after: The newer snapshot (ADG at t).

    Returns:
        GraphDiff with categorised new/removed edges and risk delta.
    """
    diff = GraphDiff(
        commit_before=before.commit_sha,
        commit_after=after.commit_sha,
        hash_before=before.graph_hash,
        hash_after=after.graph_hash,
    )

    if before.graph_hash == after.graph_hash:
        diff.is_identical = True
        return diff

    before_set: set[tuple[str, str, str]] = set(before.canonical_edge_order)
    after_set: set[tuple[str, str, str]] = set(after.canonical_edge_order)

    added = sorted(after_set - before_set)
    removed = sorted(before_set - after_set)

    diff.new_edges = added
    diff.removed_edges = removed
    diff.node_delta = after.node_count - before.node_count
    diff.edge_delta = after.edge_count - before.edge_count

    def _filter(edges: list[tuple[str, str, str]], relation: str) -> list[tuple[str, str, str]]:
        return [e for e in edges if e[1] == relation]

    def _filter_multi(edges: list[tuple[str, str, str]], *relations: str) -> list[tuple[str, str, str]]:
        return [e for e in edges if e[1] in relations]

    diff.new_violations = _filter(added, "violates")
    diff.resolved_violations = _filter(removed, "violates")
    diff.new_coverage = _filter(added, "covers")
    diff.removed_coverage = _filter(removed, "covers")
    diff.new_calls = _filter(added, "calls")
    diff.removed_calls = _filter(removed, "calls")
    diff.new_governance = _filter_multi(added, "writes_through", "routes_through")
    diff.removed_governance = _filter_multi(removed, "writes_through", "routes_through")

    diff.risk_delta = len(diff.new_violations) - len(diff.resolved_violations)

    return diff
