"""Summary ADG shim with stable aggregation helpers."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SummaryAdg:
    """Small placeholder object used by import-and-contract tests."""

    state: dict[str, Any] = field(default_factory=dict)

    def run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = dict(payload or {})
        nodes = int(normalized.get("nodes", self.state.get("nodes", 0)) or 0)
        edges = int(normalized.get("edges", self.state.get("edges", 0)) or 0)
        summary = normalized.get("summary") or self.state.get("summary") or f"nodes={nodes}, edges={edges}"
        self.state.update({"nodes": nodes, "edges": edges, "summary": summary})
        for key, value in normalized.items():
            if key not in {"nodes", "edges", "summary"}:
                self.state[key] = value
        return deepcopy(self.state)

    def density(self) -> float:
        nodes = max(1, int(self.state.get("nodes", 0) or 0))
        edges = int(self.state.get("edges", 0) or 0)
        return float(edges / nodes)


def validate_summary_adg() -> bool:
    probe = SummaryAdg()
    state = probe.run({"nodes": 4, "edges": 8})
    return state.get("summary") == "nodes=4, edges=8" and probe.density() == 2.0
