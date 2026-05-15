"""apps_rg runtime schemas — inert evidence carriers (no UWG activation here)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionCacheWriteProposal:
    """Inert proposed_state_diff evidence for semantic cache admission.

    Not a write request. Surfaced on ExitBindingResult for future X3C → UWG
    paths only. UWG is the sole write-admission surface for durable cache.
    """

    section_id: str
    cache_key: str
    content_digest: str
    metadata_ref: str
    proposal_status: str = "PENDING_UWG"


__all__ = ["SectionCacheWriteProposal"]
