"""Final Evidence Contract — AG-RGGOV-W6 Core Contract

Canonical dataclasses for C0 evidence collection output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from agentic_core.runtime.contracts.origin import Origin, OriginTaggedContent


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """Single evidence item."""

    source: str
    content: str
    content_type: str = "text"  # text, json, html, etc.
    retrieval_timestamp: str = ""
    confidence_score: float = 0.0
    # W3 P3.2: origin/data-boundary tagging (concern #6, D7=Origin enum)
    origin: Origin = Origin.RETRIEVED_DATA


@dataclass(frozen=True, slots=True)
class FinalEvidenceContract:
    """C0 evidence collection output contract.

    Contains collected evidence and sufficiency assessment.
    """

    request_id: str
    run_id: str
    app_id: str
    trace_id: str

    # Evidence content
    evidence_items: tuple[EvidenceItem, ...] = field(default_factory=tuple)
    retrieval_sources: tuple[str, ...] = field(default_factory=tuple)

    # Sufficiency assessment
    support_target_met: bool = False
    support_target_partial: bool = False
    evidence_sufficiency_score: float = 0.0

    # Identity extension
    tenant_id: str = ""  # W1: threaded from RouteContract.tenant_id (D6)

    # Metadata
    evidence_collection_timestamp: str = ""
    contract_version: str = "W6.0"

    # Digest for downstream referencing
    compilation_hash: str = ""
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"FinalEvidenceContract: missing or invalid l5_certification_ref={self.l5_certification_ref!r} "
                "(AG-W0-5=fail_closed)"
            )
