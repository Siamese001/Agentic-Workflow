"""Enhancement 9: Edge confidence and provenance scoring.

Assigns each ADG Edge a confidence score (0.0–1.0) and a provenance
label describing how the edge was derived.

Confidence tiers (from most to least certain):
  1.00  ast_import        - explicit import statement (hard syntactic fact)
  0.95  ast_call_internal - call to known-imported internal symbol
  0.90  ast_inheritance   - class Base(Parent) inheritance (syntactic)
  0.85  ast_composition   - self.x = Foo() in __init__
  0.80  ast_config_read   - os.getenv / config attribute read
  0.75  ast_governance    - writes_through/routes_through (symbol heuristic)
  0.70  ast_call_dynamic  - dynamic exec / eval / importlib
  0.65  naming_heuristic  - test covers edge derived from naming convention
  0.60  layer_violation   - post-scan inferred from layer rule mismatch

These are static analysis confidence scores. Runtime trace edges
(if added in the future) would carry 0.90+ independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import Edge

Provenance = str


_RELATION_TO_PROVENANCE: dict[str, tuple[float, Provenance]] = {
    "imports": (1.00, "ast_import"),
    "implements": (0.90, "ast_inheritance"),
    "instantiates": (0.85, "ast_composition"),
    "reads_from": (0.80, "ast_config_read"),
    "calls": (0.95, "ast_call_internal"),
    "writes_to": (0.95, "ast_call_internal"),
    "invokes_provider": (0.90, "ast_call_internal"),
    "writes_through": (0.75, "ast_governance"),
    "routes_through": (0.75, "ast_governance"),
    "covers": (0.65, "naming_heuristic"),
    "violates": (0.60, "layer_violation"),
    "produces": (0.85, "ast_composition"),
    "consumes": (0.85, "ast_composition"),
    "influences": (0.70, "ast_call_dynamic"),
    "bypasses": (0.70, "ast_call_dynamic"),
    "allows": (0.80, "ast_config_read"),
    "belongs_to_layer": (1.00, "ast_import"),
    "dynamic_exec": (0.70, "ast_call_dynamic"),
}

_EDGE_KIND_ADJUSTMENT: dict[str, float] = {
    "dynamic_exec": -0.05,
    "network": -0.05,
    "embedding": +0.00,
    "retrieval": +0.00,
    "decision": +0.00,
    "write": +0.00,
    "call": +0.00,
    "import": +0.00,
}


@dataclass
class EdgeConfidence:
    """Confidence metadata for a single ADG edge."""

    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    line_no: int
    symbol: str
    confidence: float
    provenance: Provenance

    def to_dict(self) -> dict:
        return {
            "from_name": self.from_name,
            "relation_type": self.relation_type,
            "to_name": self.to_name,
            "edge_kind": self.edge_kind,
            "source_file": self.source_file,
            "line_no": self.line_no,
            "symbol": self.symbol,
            "confidence": round(self.confidence, 4),
            "provenance": self.provenance,
        }


def score_edge(edge: "Edge") -> EdgeConfidence:
    """Assign confidence and provenance to a single edge."""
    base_confidence, provenance = _RELATION_TO_PROVENANCE.get(
        edge.relation_type, (0.60, "naming_heuristic")
    )
    adjustment = _EDGE_KIND_ADJUSTMENT.get(edge.edge_kind, 0.0)
    confidence = max(0.0, min(1.0, base_confidence + adjustment))

    return EdgeConfidence(
        from_name=edge.from_name,
        relation_type=edge.relation_type,
        to_name=edge.to_name,
        edge_kind=edge.edge_kind,
        source_file=edge.source_file,
        line_no=edge.line_no,
        symbol=edge.symbol,
        confidence=confidence,
        provenance=provenance,
    )


def score_edges(edges: list["Edge"]) -> list[EdgeConfidence]:
    """Score all edges in a list, returning EdgeConfidence objects sorted by
    (from_name, relation_type, to_name) for determinism."""
    scored = [score_edge(e) for e in edges]
    return sorted(scored, key=lambda ec: (ec.from_name, ec.relation_type, ec.to_name, ec.line_no))


def confidence_summary(scored: list[EdgeConfidence]) -> dict:
    """Return a summary dict with confidence tier breakdown."""
    tiers = {"high": 0, "medium": 0, "low": 0}
    provenance_counts: dict[str, int] = {}
    total = len(scored)

    for ec in scored:
        if ec.confidence >= 0.90:
            tiers["high"] += 1
        elif ec.confidence >= 0.75:
            tiers["medium"] += 1
        else:
            tiers["low"] += 1
        provenance_counts[ec.provenance] = provenance_counts.get(ec.provenance, 0) + 1

    return {
        "total_edges": total,
        "confidence_tiers": tiers,
        "provenance_breakdown": dict(sorted(provenance_counts.items())),
        "average_confidence": round(sum(ec.confidence for ec in scored) / total, 4) if total else 0.0,
    }
