"""PromptEnvelope — handoff contract from C0 retrieval to Prompt Assembly.

The PromptEnvelope packages verified evidence, citation anchors, replay
metadata, and assembly status into a single immutable handoff object that
the Prompt Assembly stage consumes without re-fetching any data.

Architecture reference:
  - C5_Retrieval_Prompt_Assembly.md §C0.5 Prompt Envelope Handoff
  - C1_Deterministic_Replay_Execution_Integrity.md §Replay Metadata Propagation
  - 05_Live_Runtime_Exit_Control.md §Sealed Folder (downstream consumer)

Design invariants:
  - C0 produces the envelope; Prompt Assembly consumes it.  No other layer writes.
  - Citation anchors are stable references for inline prompt formatting.
  - replay_key + policy_hash are sealed here; downstream must not mutate them.
  - When assembly_status.status == "abstain", the Assembly stage MUST NOT
    generate a response and must route to the HITL / refine path.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    Citation,
    ContradictionStatus,
    EvidenceContract,
    NextActionHint,
    VerifiedChunk,
)


# ---------------------------------------------------------------------------
# PromptAssemblyStatus
# ---------------------------------------------------------------------------


class AssemblyStatusCode:
    """Status codes for ``PromptAssemblyStatus.status``."""

    READY = "ready"
    OVERFLOW = "overflow"  # context exceeds token budget
    WEAK_SUPPORT = "weak_support"  # support_score below assembly threshold
    ABSTAIN = "abstain"  # evidence too weak or conflicting
    PARTIAL = "partial"  # some must-use chunks missing


@dataclass
class PromptAssemblyStatus:
    """Build-time status of the prompt envelope.

    Attributes
    ----------
    assembly_id : str
        Stable identifier for this assembly attempt.
    status : str
        One of ``AssemblyStatusCode`` constants.
    token_estimate : int
        Estimated token count of the assembled context block.
    overflow : bool
        True when token_estimate > budget (token budget not stored here).
    citations_required : bool
        True when at least one must-use chunk requires an inline citation.
    contradiction_flags_present : bool
        True when any verified chunk has ``contradiction_flag == True``.
    must_use_chunks_present : int
        Count of must-use chunks included in the envelope.
    optional_chunks_present : int
        Count of optional chunks included in the envelope.
    """

    assembly_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = AssemblyStatusCode.READY
    token_estimate: int = 0
    overflow: bool = False
    citations_required: bool = False
    contradiction_flags_present: bool = False
    must_use_chunks_present: int = 0
    optional_chunks_present: int = 0


# ---------------------------------------------------------------------------
# PromptEnvelope
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptEnvelope:
    """Immutable handoff from C0 retrieval to Prompt Assembly.

    Attributes
    ----------
    envelope_id : str
        Stable identifier for this envelope instance.
    trace_id : str
        Trace identifier propagated from the originating query.
    query_id : str
        Originating query identifier.
    verified_chunks : tuple[VerifiedChunk, ...]
        Ordered, immutable tuple of verified chunks (must-use first).
    cited_spans : tuple[Citation, ...]
        Flat citation list for inline anchor rendering.
    coverage_score : float
        Coverage score from the evidence contract.
    gaps : tuple[str, ...]
        Query aspects not covered (for Assembly to annotate or pass to refine).
    contradiction_status : str
        Propagated from ``EvidenceContract.contradiction_status``.
    abstain_recommended : bool
        When True, Assembly stage MUST NOT generate; route to refine/HITL.
    next_action_hint : str
        One of ``NextActionHint`` constants.
    task_spec : str
        Task specification / instruction from the routing layer.
    system_blocks : tuple[str, ...]
        Ordered static system-prompt blocks to be prepended.
    replay_key : str
        Sealed replay key; immutable after envelope creation.
    policy_hash : str
        Hash of governance policy at time of retrieval.
    plan_id : str
        Retrieval plan identifier for audit tracing.
    assembly_status : PromptAssemblyStatus
        Build-time assembly diagnostics.
    metadata : dict
        Arbitrary envelope-level metadata.
    """

    envelope_id: str
    trace_id: str
    query_id: str
    verified_chunks: tuple[VerifiedChunk, ...]
    cited_spans: tuple[Citation, ...]
    coverage_score: float
    gaps: tuple[str, ...]
    contradiction_status: str
    abstain_recommended: bool
    next_action_hint: str
    task_spec: str
    system_blocks: tuple[str, ...]
    replay_key: str
    policy_hash: str
    plan_id: str
    assembly_status: PromptAssemblyStatus
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_ready(self) -> bool:
        """True when Assembly may proceed (not abstain, not overflow)."""
        return not self.abstain_recommended and self.assembly_status.status not in (
            AssemblyStatusCode.ABSTAIN,
            AssemblyStatusCode.OVERFLOW,
        )

    @property
    def must_use_chunks(self) -> list[VerifiedChunk]:
        """Return only must-use chunks."""
        return [c for c in self.verified_chunks if c.is_must_use]

    @property
    def optional_chunks(self) -> list[VerifiedChunk]:
        """Return only optional chunks."""
        return [c for c in self.verified_chunks if not c.is_must_use]


# ---------------------------------------------------------------------------
# PromptEnvelopeFactory
# ---------------------------------------------------------------------------


class PromptEnvelopeFactory:
    """Construct a ``PromptEnvelope`` from an ``EvidenceContract``.

    The factory translates the mutable ``EvidenceContract`` produced by
    ``EvidenceContractBuilder`` into the immutable ``PromptEnvelope`` that
    the Prompt Assembly stage consumes.

    Args:
        token_budget: Maximum token budget for the context block.
            Overflow is flagged but not truncated here — Assembly truncates.
        words_per_token: Rough words-per-token ratio for estimation.
    """

    def __init__(
        self,
        token_budget: int = 4096,
        words_per_token: float = 0.75,
    ) -> None:
        self.token_budget = token_budget
        self.words_per_token = words_per_token

    def from_contract(
        self,
        contract: EvidenceContract,
        trace_id: str,
        task_spec: str = "",
        system_blocks: list[str] | None = None,
    ) -> PromptEnvelope:
        """Build a ``PromptEnvelope`` from a completed ``EvidenceContract``.

        Args:
            contract: Completed C0.4 evidence contract.
            trace_id: Trace identifier from the originating request.
            task_spec: Task instruction string from routing layer.
            system_blocks: Static system-prompt blocks to prepend.

        Returns:
            Immutable ``PromptEnvelope``.
        """
        # Token estimate from verified chunks
        total_words = sum(len(c.content.split()) for c in contract.verified_chunks)
        token_estimate = int(total_words / self.words_per_token)
        overflow = token_estimate > self.token_budget

        # Contradiction flags
        contradiction_flags = any(c.contradiction_flag for c in contract.verified_chunks)

        # Assembly status
        if contract.abstain_recommended:
            status_code = AssemblyStatusCode.ABSTAIN
        elif overflow:
            status_code = AssemblyStatusCode.OVERFLOW
        elif contract.support_score < 0.3:
            status_code = AssemblyStatusCode.WEAK_SUPPORT
        else:
            status_code = AssemblyStatusCode.READY

        assembly_status = PromptAssemblyStatus(
            status=status_code,
            token_estimate=token_estimate,
            overflow=overflow,
            citations_required=bool(contract.citations),
            contradiction_flags_present=contradiction_flags,
            must_use_chunks_present=sum(1 for c in contract.verified_chunks if c.is_must_use),
            optional_chunks_present=sum(1 for c in contract.verified_chunks if not c.is_must_use),
        )

        replay_meta = contract.replay_metadata or {}

        return PromptEnvelope(
            envelope_id=str(uuid.uuid4()),
            trace_id=trace_id,
            query_id=contract.query_id,
            verified_chunks=tuple(contract.verified_chunks),
            cited_spans=tuple(contract.citations),
            coverage_score=contract.coverage_score,
            gaps=tuple(contract.gaps),
            contradiction_status=contract.contradiction_status,
            abstain_recommended=contract.abstain_recommended,
            next_action_hint=contract.next_action_hint,
            task_spec=task_spec,
            system_blocks=tuple(system_blocks or []),
            replay_key=replay_meta.get("replay_key", ""),
            policy_hash=replay_meta.get("policy_hash", ""),
            plan_id=replay_meta.get("plan_id", ""),
            assembly_status=assembly_status,
            metadata={
                "support_score": contract.support_score,
                "citation_count": len(contract.citations),
                "verified_chunk_count": len(contract.verified_chunks),
            },
        )


__all__ = [
    "AssemblyStatusCode",
    "ContradictionStatus",
    "NextActionHint",
    "PromptAssemblyStatus",
    "PromptEnvelope",
    "PromptEnvelopeFactory",
]
