"""Origin / data-boundary typing — W6 Concern #6.

Per plan w6-emit-contract-enrichment-d8b2a4 §W3 P3.1, decision D7:
  - ``Origin`` enum classifies every text payload by its trust boundary.
  - ``OriginTaggedContent`` wraps any string payload with its origin label
    and an optional source reference.

Airlock doctrine (ADR-023 §6):
  USER_INTENT   — verbatim user text; treated as intent, never as data
                  to be executed or trusted without HITL clearance.
  RETRIEVED_DATA — text retrieved from external/internal stores via C0;
                  trusted only up to the evidence confidence score.
  TOOL_OUTPUT   — structured output from a tool call; inspected for schema
                  compliance before further use.
  MODEL_GENERATION — output produced by an LLM; not authoritative until
                  certified by the Exit gate.
  HUMAN_REVIEW_DATA — content that has passed HITL review; carries full
                  trust within its cleared scope.
  SYSTEM_INTERNAL — system-generated metadata (timestamps, IDs, hashes);
                  no external trust required.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Origin(str, Enum):
    """Trust-boundary classification for every text payload in the emit chain.

    String-valued so instances serialise cleanly to JSON / YAML without
    extra conversion.
    """

    USER_INTENT = "USER_INTENT"
    RETRIEVED_DATA = "RETRIEVED_DATA"
    TOOL_OUTPUT = "TOOL_OUTPUT"
    MODEL_GENERATION = "MODEL_GENERATION"
    HUMAN_REVIEW_DATA = "HUMAN_REVIEW_DATA"
    SYSTEM_INTERNAL = "SYSTEM_INTERNAL"


@dataclass(frozen=True, slots=True)
class OriginTaggedContent:
    """Text payload decorated with its trust-boundary origin.

    Args:
        content: The raw text payload.
        origin: Trust-boundary classification (``Origin`` enum member).
        source_ref: Optional opaque reference to the upstream source
            (e.g. an EvidenceItem source URL, a tool call ID, or a
            HITL clearance ref).  Empty string = not provided.
    """

    content: str
    origin: Origin
    source_ref: str = ""

    def is_user_controlled(self) -> bool:
        """Return True if content originates directly from user input."""
        return self.origin == Origin.USER_INTENT

    def is_externally_retrieved(self) -> bool:
        """Return True if content came from C0 retrieval."""
        return self.origin == Origin.RETRIEVED_DATA

    def requires_hitl_clearance(self) -> bool:
        """Return True if this origin class requires HITL before use."""
        return self.origin in (Origin.USER_INTENT, Origin.MODEL_GENERATION)


__all__ = [
    "Origin",
    "OriginTaggedContent",
]
