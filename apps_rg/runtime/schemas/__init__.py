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
    l5_certification_packet_digest: str = ""
    l5_certification_packet_ref: str = ""
    l5_runtime_binding_digest: str = ""
    l5_certification_verified: bool = False
    l5_certification_verification_digest: str = ""


__all__ = ["SectionCacheWriteProposal"]
