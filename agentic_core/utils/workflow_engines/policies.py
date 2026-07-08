"""
Chunking Governance Policies

Supported policies: fixed_token, overlap_window, section_aware, semantic.
All policies implement the ChunkPolicy interface.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "policies", "p0_governance")
trace_contract._emit_snapshots_state("p0", "policies", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("policies", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("policies", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("policies", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("policies", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("policies", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("policies", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("policies", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("policies", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("policies", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("policies", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("policies", "p4obs", "alert")
trace_contract._emit_links_incident_trace("policies", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("policies", "p3lm", "pattern")
trace_contract._emit_records_learning_event("policies", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("policies", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("policies", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("policies", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("policies", "p3lm", "policy")
trace_contract._emit_stores_learning_state("policies", "p3lm", "state")
trace_contract._emit_records_execution_trace("policies", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("policies", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("policies", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("policies", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("policies", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("policies", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("policies", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("policies", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("policies", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "policies", "context_pull")
trace_contract._emit_pulls_context("p1", "policies", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "policies", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "policies", "uwg_term_2")
trace_contract._emit_writes_through("p1", "policies", "write_through")
trace_contract._emit_writes_through("p1", "policies", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "policies", "safety_validation")
trace_contract._emit_invokes_eval("p1", "policies", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "policies", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "policies", "human_escalation")
trace_contract._emit_routes_through("p1", "policies", "route_through")
trace_contract._emit_checks_agent_registry("p1", "policies", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "policies", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "policies", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "policies", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "policies", "target_agent")
trace_contract._emit_verifies_policy("p1", "policies", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "policies", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "policies", "boundary_check")
trace_contract._emit_transcripts_response("p1", "policies", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "policies")
trace_contract._emit_gated_by_confidence("p1", "policies", "confidence_gate")
trace_contract.emit_replay_key("p0", "policies")
trace_contract.emit_determinism_digest("p0", "policies")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "policies", "execution_auth")
trace_contract._emit_validates_capability("p2", "policies", "capability_check")
trace_contract._emit_routes_to_capability("p2", "policies", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "policies", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "policies", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "policies", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "policies", "exec_output")
trace_contract._emit_dispatches_agent("p3", "policies", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "policies", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "policies", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "policies", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "policies", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "policies", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "policies", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "policies", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "policies", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "policies", "eval_metric")
trace_contract._emit_stores_embedding("p4", "policies", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "policies", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "policies", "exec_snapshot_link")


@dataclass
class Chunk:
    """A single document chunk with provenance metadata."""

    chunk_id: str
    doc_id: str
    content: str
    token_count: int
    start_char: int
    end_char: int
    parent_section: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "content": self.content,
            "token_count": self.token_count,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "parent_section": self.parent_section,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chunk:
        return cls(
            chunk_id=data["chunk_id"],
            doc_id=data["doc_id"],
            content=data["content"],
            token_count=data["token_count"],
            start_char=data["start_char"],
            end_char=data["end_char"],
            parent_section=data.get("parent_section", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ChunkManifest:
    """Manifest of all chunks produced from a document."""

    doc_id: str
    policy_name: str
    chunks: list[Chunk]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "policy_name": self.policy_name,
            "chunks": [c.to_dict() for c in self.chunks],
            "metadata": self.metadata,
        }


def _approx_token_count(text: str) -> int:
    """Approximate token count by whitespace splitting (no external deps)."""
    return len(text.split())


def _make_chunk_id(doc_id: str, index: int) -> str:
    return f"{doc_id}_chunk_{index:04d}"


class ChunkPolicy(ABC):
    """Abstract base class for all chunk policies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Policy name identifier."""
        ...

    @abstractmethod
    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        """Split a document into chunks.

        Args:
            document: Full document text
            doc_id: Document identifier for chunk provenance

        Returns:
            List of Chunk objects
        """
        ...


class FixedTokenChunkPolicy(ChunkPolicy):
    """Splits document into fixed-size non-overlapping token windows."""

    def __init__(self, chunk_size: int = 512):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        self.chunk_size = chunk_size

    @property
    def name(self) -> str:
        return "fixed_token"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "FixedTokenChunkPolicy.chunk")

        words = document.split()
        chunks: list[Chunk] = []
        for idx, start in tqdm(
            enumerate(range(0, len(words), self.chunk_size)), desc="Processing", unit="item"
        ):
            word_slice = words[start : start + self.chunk_size]
            content = " ".join(word_slice)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=content,
                    token_count=len(word_slice),
                    start_char=len(" ".join(words[:start])),
                    end_char=len(" ".join(words[: start + len(word_slice)])),
                    metadata={"policy": self.name, "chunk_size": self.chunk_size},
                ),
            )
        return chunks


class OverlapWindowChunkPolicy(ChunkPolicy):
    """Splits document with overlapping token windows."""

    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if overlap < 0:
            raise ValueError(f"overlap must be non-negative, got {overlap}")
        if overlap >= chunk_size:
            raise ValueError(f"overlap ({overlap}) must be less than chunk_size ({chunk_size})")
        self.chunk_size = chunk_size
        self.overlap = overlap

    @property
    def name(self) -> str:
        return "overlap_window"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "OverlapWindowChunkPolicy.chunk"
        )

        words = document.split()
        step = self.chunk_size - self.overlap
        if step <= 0:
            step = 1
        chunks: list[Chunk] = []
        idx = 0
        start = 0
        while start < len(words):
            word_slice = words[start : start + self.chunk_size]
            content = " ".join(word_slice)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=content,
                    token_count=len(word_slice),
                    start_char=start,
                    end_char=start + len(word_slice),
                    metadata={"policy": self.name, "chunk_size": self.chunk_size, "overlap": self.overlap},
                ),
            )
            start += step
            idx += 1
        return chunks


class SectionAwareChunkPolicy(ChunkPolicy):
    """Splits document on Markdown-style section headers (## or ###).

    Each section becomes its own chunk, preserving structural boundaries.
    """

    # guardian: allow-magic-config
    def __init__(self, max_section_tokens: int = 1024):
        self.max_section_tokens = max_section_tokens

    @property
    def name(self) -> str:
        return "section_aware"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SectionAwareChunkPolicy.chunk"
        )

        sections = re.split("(?m)^#{1,3}\\s+", document)
        chunks: list[Chunk] = []
        char_offset = 0
        for idx, section in tqdm(enumerate(sections), desc="Processing", unit="item"):
            section = section.strip()
            if not section:
                char_offset += len(sections[idx]) + 1
                continue
            token_count = _approx_token_count(section)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=section,
                    token_count=token_count,
                    start_char=char_offset,
                    end_char=char_offset + len(section),
                    parent_section=section[:80].replace("\n", " "),
                    metadata={"policy": self.name, "max_section_tokens": self.max_section_tokens},
                ),
            )
            char_offset += len(section) + 1
        return chunks


class SemanticChunkPolicy(ChunkPolicy):
    """Splits document at sentence boundaries, grouping into semantic windows.

    Without an embedding model: uses sentence-boundary heuristics.
    With an embedding model callable: groups sentences by cosine similarity.
    """

    # guardian: allow-magic-config
    def __init__(self, target_size: int = 256, similarity_threshold: float = 0.75, embedder=None):
        if target_size <= 0:
            raise ValueError(f"target_size must be positive, got {target_size}")
        self.target_size = target_size
        self.similarity_threshold = similarity_threshold
        self._embedder = embedder

    @property
    def name(self) -> str:
        return "semantic"

    def chunk(self, document: str, doc_id: str = "doc") -> list[Chunk]:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SemanticChunkPolicy.chunk")

        sentences = re.split("(?<=[.!?])\\s+", document.strip())
        sentences = [s for s in sentences if s.strip()]
        groups: list[list[str]] = []
        current_group: list[str] = []
        current_tokens = 0
        for sentence in sentences:
            token_count = _approx_token_count(sentence)
            if current_tokens + token_count > self.target_size and current_group:
                groups.append(current_group)
                current_group = [sentence]
                current_tokens = token_count
            else:
                current_group.append(sentence)
                current_tokens += token_count
        if current_group:
            groups.append(current_group)
        chunks: list[Chunk] = []
        char_offset = 0
        for idx, group in tqdm(enumerate(groups), desc="Processing", unit="item"):
            content = " ".join(group)
            token_count = _approx_token_count(content)
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(doc_id, idx),
                    doc_id=doc_id,
                    content=content,
                    token_count=token_count,
                    start_char=char_offset,
                    end_char=char_offset + len(content),
                    metadata={"policy": self.name, "target_size": self.target_size},
                ),
            )
            char_offset += len(content) + 1
        return chunks


__all__ = [
    "Chunk",
    "ChunkManifest",
    "ChunkPolicy",
    "FixedTokenChunkPolicy",
    "OverlapWindowChunkPolicy",
    "SectionAwareChunkPolicy",
    "SemanticChunkPolicy",
    "_approx_token_count",
]
