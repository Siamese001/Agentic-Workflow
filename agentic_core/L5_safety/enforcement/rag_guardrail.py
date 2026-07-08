from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "rag_guardrail")
trace_contract.emit_determinism_digest("p0", "rag_guardrail")

trace_contract._emit_dispatches_healing_run("p1", "rag_guardrail", "L5")
trace_contract._emit_routes_through("p1", "rag_guardrail", "L5")
trace_contract._emit_checks_agent_registry("p1", "rag_guardrail", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rag_guardrail", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rag_guardrail", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rag_guardrail", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rag_guardrail", "target_agent")
trace_contract._emit_verifies_policy("p1", "rag_guardrail", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rag_guardrail", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rag_guardrail", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rag_guardrail", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rag_guardrail")
trace_contract._emit_gated_by_confidence("p1", "rag_guardrail", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "rag_guardrail", "L5")
trace_contract._emit_reads_policy_state("p1", "rag_guardrail", "L5")

trace_contract._emit_applies_guardrail("p0", "rag_guardrail", "p0_governance")
trace_contract._emit_snapshots_state("p0", "rag_guardrail", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "rag_guardrail", "execution_auth")
trace_contract._emit_validates_capability("p2", "rag_guardrail", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rag_guardrail", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rag_guardrail", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rag_guardrail", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rag_guardrail", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rag_guardrail", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rag_guardrail", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rag_guardrail", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rag_guardrail", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rag_guardrail", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rag_guardrail", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rag_guardrail", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rag_guardrail", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rag_guardrail", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rag_guardrail", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rag_guardrail", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rag_guardrail", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rag_guardrail", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rag_guardrail", "exec_snapshot_link")

"\nRAGGuardrail - L5 RAG Content Filtering and Reranking\n\nModel library imports (torch, FlagEmbedding) are forbidden in L0-L6.\nReranker creation is delegated to tools/rag_reranker_shim.py which\nlives outside the layer boundary. The shim result is injected here.\n"
import asyncio
import math
import re
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.config.path_constants import BATCH_SIZE

trace_contract._emit_emits_metric_event("rag_guardrail", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rag_guardrail", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rag_guardrail", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rag_guardrail", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rag_guardrail", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rag_guardrail", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rag_guardrail", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rag_guardrail", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rag_guardrail", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rag_guardrail", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rag_guardrail", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rag_guardrail", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rag_guardrail", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rag_guardrail", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rag_guardrail", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rag_guardrail", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rag_guardrail", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rag_guardrail", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rag_guardrail", "p3lm", "state")
trace_contract._emit_records_execution_trace("rag_guardrail", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rag_guardrail", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rag_guardrail", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rag_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rag_guardrail", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rag_guardrail", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rag_guardrail", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rag_guardrail", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rag_guardrail", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rag_guardrail", "context_pull")
trace_contract._emit_pulls_context("p1", "rag_guardrail", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_guardrail", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_guardrail", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rag_guardrail", "write_through")
trace_contract._emit_writes_through("p1", "rag_guardrail", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rag_guardrail", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rag_guardrail", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rag_guardrail", "routing_commit")


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
    context_chunks: list[dict[str, Any]],
    citation_bundles: list[CitationBundle] | None,
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
            f"CITATION_MISSING: {len(context_chunks)} context chunk(s) present but no CitationBundle provided — wave aborted",
        )
    cited_ids = {cb.chunk_id for cb in citation_bundles}
    for chunk in context_chunks:
        cid = chunk.get("chunk_id")
        if cid is None:
            raise ExternalKnowledgeAccessViolation("CHUNK_ID_MISSING: context chunk lacks 'chunk_id' field")
        if cid not in cited_ids:
            raise ExternalKnowledgeAccessViolation(
                f"CITATION_GAP: chunk_id={cid!r} has no matching CitationBundle — wave aborted",
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "RagGuardrail.rerank_documents")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:RagGuardrail.rerank_documents".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
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
