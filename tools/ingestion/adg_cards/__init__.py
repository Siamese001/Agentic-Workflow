"""ADG semantic card projection package.

Projects ADG SQLite truth (nodes, violations, materialized views) into curated
semantic cards suitable for ChromaDB embedding. Replaces the raw-edge-bulk
ingestion pattern (tools/ingestion/ingest_adg.py) with a small, high-signal
document set: symbol / path / violation / hotspot cards.

Doctrinal basis: Wave E plan at
`docs/archive/windsurf/legacy-tree/plans/wave-e-adg-card-projection-2df148.md` and the 2026-04-06
assessment at `docs/archive/windsurf/legacy-tree/plans/adg-chromadb-retrieval-assessment-8a3f2b.md`.
"""

from tools.ingestion.adg_cards.types import (
    CardKind,
    HotspotCard,
    PathCard,
    SemanticCard,
    SymbolCard,
    ViolationCard,
    coerce_metadata,
)

__all__ = [
    "CardKind",
    "HotspotCard",
    "PathCard",
    "SemanticCard",
    "SymbolCard",
    "ViolationCard",
    "coerce_metadata",
]
