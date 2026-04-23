"""Card dataclasses + metadata contracts.

Each card is a small, embedding-ready document. Rich metadata carries the
exact ADG provenance so downstream retrieval (HybridSearchEngine) can rerank
candidates by structural importance.

All cards share a minimal ``SemanticCard`` envelope:

- ``card_kind``: one of ``CardKind``
- ``card_id``: stable deterministic id (``<kind>:<natural-key>``)
- ``document``: prose text Chroma will embed
- ``metadata``: dict of primitive values only (Chroma constraint)
- ``snapshot_id``: ADG snapshot the card was derived from
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CardKind(str, Enum):
    """Four card kinds projected from ADG truth."""

    SYMBOL = "symbol"
    PATH = "path"
    VIOLATION = "violation"
    HOTSPOT = "hotspot"


@dataclass(frozen=True)
class SemanticCard:
    """Base envelope — all emitters return subclasses of this shape."""

    card_kind: CardKind
    card_id: str
    document: str
    metadata: dict[str, Any]
    snapshot_id: str

    def chroma_id(self) -> str:
        """Deterministic id used as the ChromaDB primary key."""

        return f"{self.card_kind.value}:{self.card_id}"


@dataclass(frozen=True)
class SymbolCard(SemanticCard):
    """Per-symbol card: name, layer, file, neighbor + centrality summary."""

    card_kind: CardKind = field(default=CardKind.SYMBOL, init=False)


@dataclass(frozen=True)
class PathCard(SemanticCard):
    """Per-path card: gateway bypass or chokepoint bridge, with criticality."""

    card_kind: CardKind = field(default=CardKind.PATH, init=False)


@dataclass(frozen=True)
class ViolationCard(SemanticCard):
    """Per-violation card: category, severity, evidence, proximity context."""

    card_kind: CardKind = field(default=CardKind.VIOLATION, init=False)


@dataclass(frozen=True)
class HotspotCard(SemanticCard):
    """Per-hotspot card: centrality + debt + archetype classification."""

    card_kind: CardKind = field(default=CardKind.HOTSPOT, init=False)


# ---------------------------------------------------------------------------
# Shared metadata helpers (primitives only — Chroma requirement)
# ---------------------------------------------------------------------------


_PRIMITIVE_TYPES: tuple[type, ...] = (str, int, float, bool)


def coerce_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """Coerce values into Chroma-safe primitives.

    Chroma rejects ``None`` and non-primitive metadata. Missing values become
    empty strings; unsupported types are stringified.
    """

    out: dict[str, Any] = {}
    for key, value in meta.items():
        if value is None:
            out[key] = ""
        elif isinstance(value, _PRIMITIVE_TYPES):
            out[key] = value
        else:
            out[key] = str(value)
    return out
