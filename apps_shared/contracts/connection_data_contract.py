"""apps_shared.contracts.connection_data_contract — D6-P5 (DS5).

Plan: .windsurf/plans/apps-lic-calibration-holdout-e8f1c4.md W2 DS5-P1

Canonical data contract for mutual-network connection data passed to
MutualNetworkEngine. Callers populate this contract from their
connection-data source; the engine accepts ``list[MutualConnectionItem]``.

Invariants
----------
- Immutable frozen dataclass — no mutable fields.
- No durable state reads or writes.
- No provider API calls.
- No subprocess calls.
- Does NOT embed provider-specific assumptions. The ``relationship_type``
  vocabulary is canonical; unknown values are tolerated (treated as
  ``"unknown"`` with weight 0.1 in the engine).

Relationship type vocabulary
-----------------------------
  direct    — direct 1st-degree professional connection.
  colleague — former or current colleague.
  alumni    — shared educational institution.
  network   — 2nd-degree or indirect professional overlap.
  unknown   — relationship type not determinable from source data.

Field definitions
-----------------
name              : display name of the mutual connection.
company           : current employer of the mutual connection.
                    Empty string = unknown.
role              : current role title of the mutual connection.
                    Empty string = unknown.
relationship_type : canonical relationship type; see vocabulary above.
source_label      : opaque string describing where this item came from
                    (e.g. "linkedin_api", "manual_entry"). Not consumed
                    by the engine; carried for traceability.
"""

from __future__ import annotations

from dataclasses import dataclass

CONTRACT_VERSION: str = "1.0"
CONTRACT_NAME: str = "apps_shared.connection_data"

_VALID_RELATIONSHIP_TYPES: frozenset[str] = frozenset(
    {"direct", "colleague", "alumni", "network", "unknown"}
)


@dataclass(frozen=True)
class MutualConnectionItem:
    """Canonical record of one mutual network connection.

    Attributes
    ----------
    name              : display name of the shared contact.
    company           : current employer; empty = unknown.
    role              : current role title; empty = unknown.
    relationship_type : canonical relationship type (see module docstring).
    source_label      : provenance label; not consumed by engine.
    """

    name: str
    company: str = ""
    role: str = ""
    relationship_type: str = "unknown"
    source_label: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("MutualConnectionItem.name must be non-empty")
        rt = self.relationship_type.lower()
        if rt not in _VALID_RELATIONSHIP_TYPES:
            raise ValueError(
                f"MutualConnectionItem.relationship_type {rt!r} not in "
                f"vocabulary {sorted(_VALID_RELATIONSHIP_TYPES)}"
            )
        object.__setattr__(self, "relationship_type", rt)


@dataclass(frozen=True)
class ConnectionDataSet:
    """Ordered collection of mutual connections for a single recipient.

    Attributes
    ----------
    items        : tuple of MutualConnectionItem records.
    recipient_id : opaque caller-assigned recipient identifier (traceability).
    """

    items: tuple[MutualConnectionItem, ...]
    recipient_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.items, tuple):
            object.__setattr__(self, "items", tuple(self.items))

    @classmethod
    def from_list(
        cls,
        records: list[MutualConnectionItem],
        *,
        recipient_id: str = "",
    ) -> "ConnectionDataSet":
        """Construct from a plain list (convenience)."""
        return cls(items=tuple(records), recipient_id=recipient_id)

    def as_engine_list(self) -> list[MutualConnectionItem]:
        """Return items as a plain list suitable for MutualNetworkEngine."""
        return list(self.items)

    @property
    def connection_count(self) -> int:
        return len(self.items)

    @property
    def has_direct_connection(self) -> bool:
        return any(c.relationship_type == "direct" for c in self.items)


__all__ = [
    "CONTRACT_VERSION",
    "CONTRACT_NAME",
    "VALID_RELATIONSHIP_TYPES",
    "MutualConnectionItem",
    "ConnectionDataSet",
]

VALID_RELATIONSHIP_TYPES = _VALID_RELATIONSHIP_TYPES
