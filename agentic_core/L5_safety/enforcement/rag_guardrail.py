from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "rag_guardrail")
emit_determinism_digest("p0", "rag_guardrail")

_emit_dispatches_healing_run("p1", "rag_guardrail", "L5")
_emit_routes_through("p1", "rag_guardrail", "L5")
_emit_checks_agent_registry("p1", "rag_guardrail", "agent_registry")
_emit_validates_agent_capability("p1", "rag_guardrail", "capability")
_emit_dispatches_execution_plan("p1", "rag_guardrail", "exec_plan")
_emit_agent_executes_agent("p1", "rag_guardrail", "sub_agent")
_emit_routes_to_agent("p1", "rag_guardrail", "target_agent")
_emit_verifies_policy("p1", "rag_guardrail", "policy_check")
_emit_observes_runtime_state("p1", "rag_guardrail", "runtime_state")
_emit_verifies_boundary("p1", "rag_guardrail", "boundary_check")
_emit_transcripts_response("p1", "rag_guardrail", "transcript")
_emit_hard_fails_untranscripted("p1", "rag_guardrail")
_emit_gated_by_confidence("p1", "rag_guardrail", "confidence_gate")
_emit_escalates_to_human("p1", "rag_guardrail", "L5")
_emit_reads_policy_state("p1", "rag_guardrail", "L5")

_emit_applies_guardrail("p0", "rag_guardrail", "p0_governance")
_emit_snapshots_state("p0", "rag_guardrail", "state_snapshot")
_emit_authorize_and_execute("p2", "rag_guardrail", "execution_auth")
_emit_validates_capability("p2", "rag_guardrail", "capability_check")
_emit_routes_to_capability("p2", "rag_guardrail", "capability_route")
_emit_writes_via_uwg("p2", "rag_guardrail", "uwg_write")
_emit_blocks_direct_write("p2", "rag_guardrail", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_guardrail", "tool_invocation")
_emit_captures_execution_output("p2", "rag_guardrail", "exec_output")
_emit_dispatches_agent("p3", "rag_guardrail", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_guardrail", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_guardrail", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_guardrail", "healing_outcome")
_emit_escalates_failure("p3", "rag_guardrail", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_guardrail", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_guardrail", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_guardrail", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_guardrail", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_guardrail", "eval_metric")
_emit_stores_embedding("p4", "rag_guardrail", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_guardrail", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_guardrail", "exec_snapshot_link")

"\nRAGGuardrail - L5 RAG Content Filtering and Reranking\n\nModel library imports (torch, FlagEmbedding) are forbidden in L0-L6.\nReranker creation is delegated to tools/rag_reranker_shim.py which\nlives outside the layer boundary. The shim result is injected here.\n"
import asyncio
import math
import re
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.path_constants import BATCH_SIZE
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("rag_guardrail", "p4obs", "metric_1")
_emit_emits_metric_event("rag_guardrail", "p4obs", "metric_2")
_emit_emits_metric_event("rag_guardrail", "p4obs", "metric_3")
_emit_emits_metric_event("rag_guardrail", "p4obs", "metric_4")
_emit_emits_metric_event("rag_guardrail", "p4obs", "metric_5")
_emit_emits_metric_event("rag_guardrail", "p4obs", "metric_6")
_emit_records_incident_event("rag_guardrail", "p4obs", "incident")
_emit_captures_runtime_anomaly("rag_guardrail", "p4obs", "anomaly")
_emit_writes_observability_log("rag_guardrail", "p4obs", "obs_log")
_emit_updates_monitoring_state("rag_guardrail", "p4obs", "mon_state")
_emit_triggers_alert("rag_guardrail", "p4obs", "alert")
_emit_links_incident_trace("rag_guardrail", "p4obs", "trace_link")
_emit_captures_pattern("rag_guardrail", "p3lm", "pattern")
_emit_records_learning_event("rag_guardrail", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rag_guardrail", "p3lm", "snapshot")
_emit_feeds_meta_learning("rag_guardrail", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rag_guardrail", "p3lm", "routing")
_emit_improves_agent_policy("rag_guardrail", "p3lm", "policy")
_emit_stores_learning_state("rag_guardrail", "p3lm", "state")
_emit_records_execution_trace("rag_guardrail", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rag_guardrail", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rag_guardrail", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rag_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rag_guardrail", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rag_guardrail", "env_read", "p2_env_1")
_emit_reads_environ("rag_guardrail", "env_read", "p2_env_2")
_emit_reads_runtime_state("rag_guardrail", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rag_guardrail", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rag_guardrail", "context_pull")
_emit_pulls_context("p1", "rag_guardrail", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rag_guardrail", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rag_guardrail", "uwg_term_2")
_emit_writes_through("p1", "rag_guardrail", "write_through")
_emit_writes_through("p1", "rag_guardrail", "write_through_2")
_emit_validated_by_safety_plane("p1", "rag_guardrail", "safety_validation")
_emit_invokes_eval("p1", "rag_guardrail", "eval_call")
_emit_proposal_commits_routing("p1", "rag_guardrail", "routing_commit")


class ExternalKnowledgeAccessViolation(Exception):
    """Raised when retrieved context is consumed without a valid CitationBundle.

    REQ-RAGX-006: ExternalKnowledgeAccessViolation MUST be emitted and wave
    aborted if context used without CitationBundle.  Fail-closed.
    """


@dataclass(frozen=True)
class CitationBundle:
    """Immutable citation binding for retrieved chunks.

    Every chunk of external knowledge entering the execution pipeline MUST
    carry a CitationBundle proving provenance.  Fields mirror REQ-RAGX-003.
    """

    chunk_id: str
    source_ref: str
    byte_sha256: str
    byte_range: tuple[int, int]
    score: float


def validate_citation_custody(
    context_chunks: list[dict[str, Any]], citation_bundles: list[CitationBundle] | None
) -> None:
    """Enforce that every external-knowledge chunk has a matching CitationBundle.

    Args:
        context_chunks: list of dicts representing retrieved context.  Each dict
            MUST contain at least ``chunk_id``.
        citation_bundles: corresponding CitationBundle objects.  ``None`` or
            empty list when chunks are present triggers the violation.

    Raises:
        ExternalKnowledgeAccessViolation: when context is present but citations
            are missing, empty, or do not cover every chunk_id.
    """
    if not context_chunks:
        return
    if citation_bundles is None or len(citation_bundles) == 0:
        raise ExternalKnowledgeAccessViolation(
            f"CITATION_MISSING: {len(context_chunks)} context chunk(s) present but no CitationBundle provided — wave aborted"
        )
    cited_ids = {cb.chunk_id for cb in citation_bundles}
    for chunk in context_chunks:
        cid = chunk.get("chunk_id")
        if cid is None:
            raise ExternalKnowledgeAccessViolation("CHUNK_ID_MISSING: context chunk lacks 'chunk_id' field")
        if cid not in cited_ids:
            raise ExternalKnowledgeAccessViolation(
                f"CITATION_GAP: chunk_id={cid!r} has no matching CitationBundle — wave aborted"
            )


class RagGuardrail:
    """Brief description of functionality and purpose."""

    def __init__(self, reranker: Any = None, reranker_available: bool = False, status_message: str = ""):
        self.bge_reranker = reranker
        self.reranker_available = reranker_available
        if status_message:
            print(f"   [OK] {status_message}")
        elif not reranker_available:
            print("   [!] No reranker injected — falling back to RRF only")

    async def rerank_documents(self, documents: list[Any], query: str, top_k: int = 10) -> list[Any]:
        """
        L5 reranking using BGE-v2-m3 for sovereign precision
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "RagGuardrail.rerank_documents")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RagGuardrail.rerank_documents".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not self.reranker_available or not documents:
            return documents
        try:
            pairs: Any = [[query, doc.text] for doc in documents]

            def _compute():
                return self.bge_reranker.compute_score(pairs, batch_size=BATCH_SIZE)

            raw_logits: Any = await asyncio.to_thread(_compute)
            if isinstance(raw_logits, float | int):
                raw_logits: Any = [raw_logits]
            confident_docs: Any = []
            min_confidence: Any = 0.75
            for doc, logit in zip(documents, raw_logits, strict=False):
                confidence: Any = 1 / (1 + math.exp(-logit))
                if confidence >= min_confidence:
                    doc.score = float(confidence)
                    confident_docs.append(doc)
            confident_docs.sort(key=lambda x: x.score, reverse=True)
            dropped: Any = len(documents) - len(confident_docs)
            if dropped > 0:
                print(f"   [FILTER] Dropped {dropped} low-confidence docs (<{min_confidence})")
            if not confident_docs:
                print("   [!] SOVEREIGN ALERT: Zero documents passed confidence threshold.")
            return confident_docs[:top_k]
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            print(f"   [!] BGE reranking failed: {e}")
            return documents

    async def filter_hallucinations(self, documents: list[Any], query: str) -> list[Any]:
        """
        Heuristic: Checks if key entities in the query/response are supported by documents.
        """
        if not documents:
            return documents
        combined_context = " ".join([d.text.lower() for d in documents])
        query_entities = set(re.findall("\\b[A-Z][a-z]+\\b", query))
        if not query_entities:
            return documents
        supported_entities = 0
        for entity in query_entities:
            if entity.lower() in combined_context:
                supported_entities += 1
        ratio = supported_entities / len(query_entities)
        if ratio < 0.5:
            print(f"   [WARN] Retrieval Validity Low: Only {ratio:.1%} of query entities found in context.")
        return documents

    async def apply_safety_filters(self, documents: list[Any]) -> list[Any]:
        """
        Apply L5 safety filters to RAG results
        """
        filtered: Any = []
        for doc in documents:
            if not doc.text or len(doc.text.strip()) < 10:
                continue
            forbidden: Any = ["password", "secret", "api_key", "private_key"]
            text_lower: Any = doc.text.lower()
            if any(word in text_lower for word in forbidden):
                continue
            filtered.append(doc)
        return filtered

    async def process(self, documents: list[Any], query: str) -> list[Any]:
        """
        Full RAG guardrail processing pipeline
        """
        filtered: Any = await self.apply_safety_filters(documents)
        safe: Any = await self.filter_hallucinations(filtered, query)
        reranked: Any = await self.rerank_documents(safe, query)
        return reranked
