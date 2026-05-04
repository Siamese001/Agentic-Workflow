"""L4 durable provenance record for research briefs.

DS-3 (plan apps-research-deferred-scope-b7e3d2 W3, phase 3.2).

``ResearchBriefRecord`` is the L4-side provenance snapshot committed
through :class:`agentic_core.L4_state.uwg.durable_write_gateway.DurableWriteGateway`
after each ``GovernedResearchRun.run_governed_e2e()`` call.

It carries the minimal evidence required for auditability:

- run identity (``run_id``, ``trace_id``)
- topic and routing decision (``topic``, ``l0_intent``, ``l0_confidence``)
- grounding facts (``grounded``, ``citation_count``, ``disposition``)
- FEC v1.1 binding (``research_depth_profile``, ``fec_context_digest``)
- commit provenance back-ref (``commit_receipt_ref``)

This record is NOT the full ``GovernedE2ERunRecord`` — it is a
lightweight provenance snapshot suitable for L4 audit. The full run
record lives in the caller's response object and OTEL traces.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

_RECORD_SCHEMA_VERSION = "research-brief-1.0"


@dataclass(frozen=True)
class ResearchBriefRecord:
    """Immutable provenance snapshot committed to L4 after a research run.

    Fields
    ------
    record_id:
        Unique identity of this provenance record (UUID or derived from run_id).
    run_id:
        ``GovernedE2ERunRecord.run_id`` — correlates back to the full run.
    trace_id:
        ``ResearchRequest.trace_id`` for cross-layer correlation.
    topic:
        Research topic verbatim from the request.
    l0_intent:
        Intent label assigned by the L0 router.
    l0_confidence:
        L0 routing confidence (0.0–1.0).
    grounded:
        True when the gate result reports ``grounded_replayable=True``.
    citation_count:
        Citation anchors produced by the run.
    disposition:
        ``WeakSupportDisposition.value`` — proceed / refine / abstain / escalate.
    research_depth_profile:
        Depth profile used (e.g. ``DOSSIER``).  Empty string when absent.
    fec_context_digest:
        SHA-256 of the FEC run context dict (for replay verification).
        Empty string when no FEC context was produced.
    committed_at:
        ISO-8601 timestamp of the UWG commit.
    commit_receipt_ref:
        ``UWGCommitReceipt.commit_receipt_id`` on success; ``"BLOCKED"`` or
        ``"COMMIT_FAILED"`` on failure.
    schema_version:
        Record schema version for forward-compat.
    audit_refs:
        Tuple of UWG/audit receipt IDs attached to this record (may be empty
        if the UWG call was fail-soft degraded).
    """

    record_id: str
    run_id: str
    trace_id: str
    topic: str
    l0_intent: str
    l0_confidence: float
    grounded: bool
    citation_count: int
    disposition: str
    research_depth_profile: str = ""
    fec_context_digest: str = ""
    committed_at: str = ""
    commit_receipt_ref: str = ""
    schema_version: str = _RECORD_SCHEMA_VERSION
    audit_refs: Tuple[str, ...] = field(default_factory=tuple)


__all__ = [
    "ResearchBriefRecord",
    "_RECORD_SCHEMA_VERSION",
]
