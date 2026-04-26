"""Context Compaction — summarization and tool-result clearing for long-horizon C0 loops.

Addresses G5 (Anthropic 2025): long-horizon tasks need compaction
(summarize-and-restart), tool-result clearing, and agent-written notes
persisted outside the window.  Without compaction, context overflow
corrupts the evidence contract and the prompt envelope.

Architecture reference:
  - Anthropic — *Effective Context Engineering for AI Agents* (2025)
    §Compaction, §Tool-result clearing, §Structured note-taking
  - C0 Context Engine.md §C0.5 (evidence contract lifecycle)

Design:
  - ``ContextCompactor`` receives a ``PromptEnvelope`` that has exceeded
    token budget and produces a compacted envelope with:
    1. Tool results cleared (replaced by lightweight identifiers)
    2. Optional summary of consumed evidence
    3. Citation provenance preserved across compaction
  - ``CompactionResult`` tracks what was compacted and what was preserved.
  - Integration point: the C0.6 Refine loop checks ``refine_attempt`` on
    the contract; when ``refine_attempt >= max_refine_attempts`` or the
    envelope is in OVERFLOW, compaction fires before the next pass.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any

from agentic_core.knowledge.retrieval.evidence_contract_builder import (
    EvidenceContract,
    EvidenceStatus,
    RefinementDiagnostic,
    VerifiedChunk,
)
from agentic_core.knowledge.retrieval.prompt_envelope import (
    AssemblyStatusCode,
    PromptAssemblyStatus,
    PromptEnvelope,
    PromptEnvelopeFactory,
)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class CompactionRecord:
    """Audit record for a single compaction action.

    Attributes
    ----------
    chunk_id : str
        ID of the compacted chunk.
    action : str
        ``"cleared"`` (tool result removed) or ``"summarized"`` (content
        replaced by summary).
    original_char_count : int
        Character count before compaction.
    compacted_char_count : int
        Character count after compaction.
    provenance_preserved : bool
        True when citation_anchor and source_id survived compaction.
    """

    chunk_id: str
    action: str
    original_char_count: int = 0
    compacted_char_count: int = 0
    provenance_preserved: bool = True


@dataclass
class CompactionResult:
    """Result of a compaction pass on a PromptEnvelope.

    Attributes
    ----------
    compacted_envelope : PromptEnvelope
        The envelope after compaction (may be the same object if no
        compaction was needed).
    records : list[CompactionRecord]
        Audit trail of what was compacted.
    chars_saved : int
        Total character reduction from compaction.
    tool_results_cleared : int
        Number of tool-result chunks that were cleared.
    summaries_produced : int
        Number of chunks that were summarized instead of cleared.
    provenance_intact : bool
        True when all must-use chunks retained citation provenance.
    """

    compacted_envelope: PromptEnvelope
    records: list[CompactionRecord] = field(default_factory=list)
    chars_saved: int = 0
    tool_results_cleared: int = 0
    summaries_produced: int = 0
    provenance_intact: bool = True


# ---------------------------------------------------------------------------
# ContextCompactor
# ---------------------------------------------------------------------------


class ContextCompactor:
    """Compacts a PromptEnvelope that has exceeded token budget.

    Strategies (applied in order):
      1. **Tool-result clearing**: chunks tagged as tool results
         (``evidence_class == BACKGROUND`` and source starts with
         ``"tool_"``) are replaced with a lightweight identifier.
      2. **Optional-chunk summarization**: non-must-use chunks are
         summarized to their first sentence + citation anchor.
      3. **Background pruning**: BACKGROUND-class chunks are dropped
         entirely (citation anchor preserved in ``excluded_with_reasons``).

    Must-use chunks are NEVER compacted — they carry critical evidence.

    Args:
        token_budget : int
            Target token budget for the compacted envelope.
        words_per_token : float
            Words-per-token ratio for estimation.
        max_summary_chars : int
            Maximum characters for a summarized chunk.
    """

    def __init__(
        self,
        token_budget: int = 4096,
        words_per_token: float = 0.75,
        max_summary_chars: int = 200,
    ) -> None:
        self.token_budget = token_budget
        self.words_per_token = words_per_token
        self.max_summary_chars = max_summary_chars

    def compact(self, envelope: PromptEnvelope) -> CompactionResult:
        """Compact an overflowing envelope.

        Args:
            envelope: The envelope to compact.

        Returns:
            ``CompactionResult`` with the compacted envelope and audit trail.
        """
        current_tokens = envelope.assembly_status.token_estimate
        if current_tokens <= self.token_budget:
            return CompactionResult(compacted_envelope=envelope)

        records: list[CompactionRecord] = []
        chars_saved = 0
        tool_results_cleared = 0
        summaries_produced = 0
        provenance_intact = True

        # Work on mutable copies
        chunks = list(envelope.verified_chunks)
        excluded = dict(envelope.excluded_with_reasons)

        # Pass 1: Clear tool-result chunks (BACKGROUND + tool_ source)
        for i, chunk in enumerate(chunks):
            if chunk.is_must_use:
                continue
            is_tool_result = (
                chunk.evidence_class == "background"
                and chunk.source_id.startswith("tool_")
            )
            if not is_tool_result:
                continue

            original_len = len(chunk.content)
            identifier = f"[tool-result:{chunk.chunk_id}]"
            records.append(CompactionRecord(
                chunk_id=chunk.chunk_id,
                action="cleared",
                original_char_count=original_len,
                compacted_char_count=len(identifier),
                provenance_preserved=bool(chunk.citation_anchor),
            ))
            # Replace content with lightweight identifier
            chunks[i] = VerifiedChunk(
                chunk_id=chunk.chunk_id,
                content=identifier,
                source_id=chunk.source_id,
                citation_anchor=chunk.citation_anchor,
                support_score=chunk.support_score,
                is_must_use=False,
                contradiction_flag=chunk.contradiction_flag,
                evidence_class=chunk.evidence_class,
                exclusion_reason=chunk.exclusion_reason,
                provenance=chunk.provenance,
            )
            chars_saved += original_len - len(identifier)
            tool_results_cleared += 1

        # Pass 2: Summarize optional (non-must-use, non-tool) chunks
        for i, chunk in enumerate(chunks):
            if chunk.is_must_use:
                continue
            if chunk.content.startswith("[tool-result:"):
                continue  # already cleared
            if len(chunk.content) <= self.max_summary_chars:
                continue  # already short

            original_len = len(chunk.content)
            summary = self._summarize_chunk(chunk)
            records.append(CompactionRecord(
                chunk_id=chunk.chunk_id,
                action="summarized",
                original_char_count=original_len,
                compacted_char_count=len(summary),
                provenance_preserved=bool(chunk.citation_anchor),
            ))
            chunks[i] = VerifiedChunk(
                chunk_id=chunk.chunk_id,
                content=summary,
                source_id=chunk.source_id,
                citation_anchor=chunk.citation_anchor,
                support_score=chunk.support_score,
                is_must_use=False,
                contradiction_flag=chunk.contradiction_flag,
                evidence_class=chunk.evidence_class,
                exclusion_reason=chunk.exclusion_reason,
                provenance=chunk.provenance,
            )
            chars_saved += original_len - len(summary)
            summaries_produced += 1

        # Pass 3: Prune BACKGROUND chunks if still over budget
        total_words = sum(len(c.content.split()) for c in chunks)
        estimated_tokens = int(total_words / self.words_per_token)

        if estimated_tokens > self.token_budget:
            pruned_chunks = []
            for chunk in chunks:
                if (
                    not chunk.is_must_use
                    and chunk.evidence_class == "background"
                    and estimated_tokens > self.token_budget
                ):
                    records.append(CompactionRecord(
                        chunk_id=chunk.chunk_id,
                        action="pruned",
                        original_char_count=len(chunk.content),
                        compacted_char_count=0,
                        provenance_preserved=bool(chunk.citation_anchor),
                    ))
                    excluded[chunk.chunk_id] = "compaction_pruned: background, over budget"
                    chars_saved += len(chunk.content)
                    estimated_tokens = max(
                        0,
                        estimated_tokens - int(len(chunk.content.split()) / self.words_per_token),
                    )
                    if not chunk.citation_anchor:
                        provenance_intact = False
                else:
                    pruned_chunks.append(chunk)
            chunks = pruned_chunks

        # Rebuild the envelope with compacted chunks
        total_words = sum(len(c.content.split()) for c in chunks)
        new_token_estimate = int(total_words / self.words_per_token)

        new_assembly = PromptAssemblyStatus(
            status=AssemblyStatusCode.READY if new_token_estimate <= self.token_budget else AssemblyStatusCode.OVERFLOW,
            token_estimate=new_token_estimate,
            overflow=new_token_estimate > self.token_budget,
            citations_required=envelope.assembly_status.citations_required,
            contradiction_flags_present=envelope.assembly_status.contradiction_flags_present,
            must_use_chunks_present=sum(1 for c in chunks if c.is_must_use),
            optional_chunks_present=sum(1 for c in chunks if not c.is_must_use),
        )

        compacted = PromptEnvelope(
            envelope_id=envelope.envelope_id,
            trace_id=envelope.trace_id,
            query_id=envelope.query_id,
            verified_chunks=tuple(chunks),
            cited_spans=envelope.cited_spans,
            coverage_score=envelope.coverage_score,
            gaps=envelope.gaps,
            task_spec=envelope.task_spec,
            system_blocks=envelope.system_blocks,
            replay_key=envelope.replay_key,
            policy_hash=envelope.policy_hash,
            plan_id=envelope.plan_id,
            assembly_status=new_assembly,
            evidence_status=envelope.evidence_status,
            recommended_disposition=envelope.recommended_disposition,
            excluded_with_reasons=excluded,
            evidence_classes=envelope.evidence_classes,
            refinement_diagnostics=envelope.refinement_diagnostics,
            refine_attempt=envelope.refine_attempt,
            max_refine_attempts=envelope.max_refine_attempts,
            contradiction_status=envelope.contradiction_status,
            abstain_recommended=envelope.abstain_recommended,
            next_action_hint=envelope.next_action_hint,
            metadata={
                **envelope.metadata,
                "compaction_applied": True,
                "compaction_chars_saved": chars_saved,
                "compaction_tool_results_cleared": tool_results_cleared,
                "compaction_summaries_produced": summaries_produced,
            },
        )

        log.info(
            "Compaction: tokens %d→%d, chars_saved=%d, cleared=%d, summarized=%d",
            current_tokens, new_token_estimate, chars_saved,
            tool_results_cleared, summaries_produced,
        )

        return CompactionResult(
            compacted_envelope=compacted,
            records=records,
            chars_saved=chars_saved,
            tool_results_cleared=tool_results_cleared,
            summaries_produced=summaries_produced,
            provenance_intact=provenance_intact,
        )

    @staticmethod
    def _summarize_chunk(chunk: VerifiedChunk) -> str:
        """Summarize a chunk to its first sentence + citation anchor.

        Preserves the citation anchor so provenance survives compaction.
        """
        content = chunk.content.strip()
        # Take first sentence (up to first period, question mark, or newline)
        for sep in (". ", "? ", "! ", "\n"):
            idx = content.find(sep)
            if idx > 0:
                first_sentence = content[: idx + 1]
                break
        else:
            first_sentence = content[:120]

        anchor = chunk.citation_anchor or ""
        suffix = f" [{anchor}]" if anchor else ""
        result = f"{first_sentence}[...compacted]{suffix}"
        return result[:200]  # hard cap
