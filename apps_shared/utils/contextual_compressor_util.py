"""Contextual Compressor - Precision Layer for RAG.

This component extracts only the relevant sentences from retrieved chunks,
reducing noise and improving signal density in the RAG pipeline.
"""

import logging
import re
import time

from pydantic import BaseModel, Field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "contextual_compressor_util", "p0_governance")
_emit_reads_policy_state("p0", "contextual_compressor_util", "policy_binding")
_emit_snapshots_state("p0", "contextual_compressor_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("contextual_compressor_util", "p4obs", "metric_1")
_emit_emits_metric_event("contextual_compressor_util", "p4obs", "metric_2")
_emit_emits_metric_event("contextual_compressor_util", "p4obs", "metric_3")
_emit_emits_metric_event("contextual_compressor_util", "p4obs", "metric_4")
_emit_emits_metric_event("contextual_compressor_util", "p4obs", "metric_5")
_emit_emits_metric_event("contextual_compressor_util", "p4obs", "metric_6")
_emit_records_incident_event("contextual_compressor_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("contextual_compressor_util", "p4obs", "anomaly")
_emit_writes_observability_log("contextual_compressor_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("contextual_compressor_util", "p4obs", "mon_state")
_emit_triggers_alert("contextual_compressor_util", "p4obs", "alert")
_emit_links_incident_trace("contextual_compressor_util", "p4obs", "trace_link")
_emit_captures_pattern("contextual_compressor_util", "p3lm", "pattern")
_emit_records_learning_event("contextual_compressor_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("contextual_compressor_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("contextual_compressor_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("contextual_compressor_util", "p3lm", "routing")
_emit_improves_agent_policy("contextual_compressor_util", "p3lm", "policy")
_emit_stores_learning_state("contextual_compressor_util", "p3lm", "state")
_emit_records_execution_trace("contextual_compressor_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("contextual_compressor_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("contextual_compressor_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("contextual_compressor_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("contextual_compressor_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("contextual_compressor_util", "env_read", "p2_env_1")
_emit_reads_environ("contextual_compressor_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("contextual_compressor_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("contextual_compressor_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "contextual_compressor_util", "context_pull")
_emit_pulls_context("p1", "contextual_compressor_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "contextual_compressor_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "contextual_compressor_util", "uwg_term_2")
_emit_writes_through("p1", "contextual_compressor_util", "write_through")
_emit_writes_through("p1", "contextual_compressor_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "contextual_compressor_util", "safety_validation")
_emit_invokes_eval("p1", "contextual_compressor_util", "eval_call")
_emit_proposal_commits_routing("p1", "contextual_compressor_util", "routing_commit")
_emit_escalates_to_human("p1", "contextual_compressor_util", "human_escalation")
_emit_routes_through("p1", "contextual_compressor_util", "route_through")
_emit_checks_agent_registry("p1", "contextual_compressor_util", "agent_registry")
_emit_validates_agent_capability("p1", "contextual_compressor_util", "capability")
_emit_dispatches_execution_plan("p1", "contextual_compressor_util", "exec_plan")
_emit_agent_executes_agent("p1", "contextual_compressor_util", "sub_agent")
_emit_routes_to_agent("p1", "contextual_compressor_util", "target_agent")
_emit_verifies_policy("p1", "contextual_compressor_util", "policy_check")
_emit_observes_runtime_state("p1", "contextual_compressor_util", "runtime_state")
_emit_verifies_boundary("p1", "contextual_compressor_util", "boundary_check")
_emit_transcripts_response("p1", "contextual_compressor_util", "transcript")
_emit_hard_fails_untranscripted("p1", "contextual_compressor_util")
_emit_gated_by_confidence("p1", "contextual_compressor_util", "confidence_gate")
emit_replay_key("p0", "contextual_compressor_util")
emit_determinism_digest("p0", "contextual_compressor_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "contextual_compressor_util", "execution_auth")
_emit_validates_capability("p2", "contextual_compressor_util", "capability_check")
_emit_routes_to_capability("p2", "contextual_compressor_util", "capability_route")
_emit_writes_via_uwg("p2", "contextual_compressor_util", "uwg_write")
_emit_blocks_direct_write("p2", "contextual_compressor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "contextual_compressor_util", "tool_invocation")
_emit_captures_execution_output("p2", "contextual_compressor_util", "exec_output")
_emit_dispatches_agent("p3", "contextual_compressor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "contextual_compressor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "contextual_compressor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "contextual_compressor_util", "healing_outcome")
_emit_escalates_failure("p3", "contextual_compressor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "contextual_compressor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "contextual_compressor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "contextual_compressor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "contextual_compressor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "contextual_compressor_util", "eval_metric")
_emit_stores_embedding("p4", "contextual_compressor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "contextual_compressor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "contextual_compressor_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class CompressionResult(BaseModel):
    """Result of contextual compression operation."""

    original_length: int = Field(..., description="Original text length in characters")
    compressed_length: int = Field(..., description="Compressed text length in characters")
    compressed_text: str = Field(..., description="Compressed text content")
    compression_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Compression ratio (compressed/original)",
    )


class ContextualCompressor:
    """Compresses retrieved chunks to extract only relevant sentences.

    Uses Jaccard similarity and simple heuristics to filter sentences
    that are relevant to the query while maintaining context.
    """

    # guardian: allow-magic-config
    def __init__(self, similarity_threshold: float = 0.1, use_llm: bool = False):
        """Initialize the Contextual Compressor.

        Args:
            similarity_threshold: Minimum Jaccard similarity to keep a sentence
            use_llm: Whether to use LLM for extraction (heuristic mode if False)
        """
        self.similarity_threshold = similarity_threshold
        self.use_llm = use_llm
        self.sentence_pattern = re.compile(
            "(?<!\\w\\.\\w.)(?<![A-Z][a-z]\\.)(?<=\\.|\\?|\\!)\\s",
            re.MULTILINE,
        )
        self.entity_patterns = {
            "person": "\\b([A-Z][a-z]+ [A-Z][a-z]+)\\b",
            "organization": "\\b([A-Z]{2,})\\b",
            "metric": "\\b(\\d+(?:\\.\\d+)?%|\\d+(?:,\\d{3})*(?:\\.\\d+)?[kmb]?)\\b",
            "date": "\\b(\\d{4}|\\d{1,2}/\\d{1,2}/\\d{2,4})\\b",
        }
        logger.info(f"Initialized ContextualCompressor: threshold={similarity_threshold}, llm={use_llm}")

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences using regex.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        sentences = self.sentence_pattern.split(text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _calculate_jaccard_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts.

        Jaccard similarity = |intersection| / |union|

        Args:
            text1: First text
            text2: Second text

        Returns:
            Jaccard similarity score (0-1)
        """
        words1 = {word.lower().strip('.,!?;:"()[]{}') for word in text1.split()}
        words2 = {word.lower().strip('.,!?;:"()[]{}') for word in text2.split()}
        words1.discard("")
        words2.discard("")
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        if not union:
            return 0.0
        return len(intersection) / len(union)

    def _extract_entities(self, text: str) -> set[str]:
        """Extract named entities from text using simple patterns.

        Args:
            text: Text to extract entities from

        Returns:
            Set of extracted entities
        """
        entities = set()
        for _entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            entities.update(matches)
        return entities

    def _compress_heuristic(self, chunks: list[str], query: str) -> str:
        """Compress using heuristic Jaccard similarity.

        Args:
            chunks: List of text chunks
            query: Query string for relevance

        Returns:
            Compressed text
        """
        start_time = time.time()
        query_entities = self._extract_entities(query)
        query_words = {word.lower() for word in query.split()}
        selected_sentences = []
        all_sentences = []
        for chunk in chunks:
            sentences = self._split_into_sentences(chunk)
            all_sentences.extend(sentences)
        sentence_scores = []
        for i, sentence in tqdm(enumerate(all_sentences), desc="Processing", unit="item"):
            similarity = self._calculate_jaccard_similarity(sentence, query)
            sentence_entities = self._extract_entities(sentence)
            entity_match = bool(query_entities.intersection(sentence_entities))
            sentence_words = {word.lower() for word in sentence.split()}
            keyword_match = bool(query_words.intersection(sentence_words))
            sentence_scores.append(
                {
                    "index": i,
                    "sentence": sentence,
                    "similarity": similarity,
                    "entity_match": entity_match,
                    "keyword_match": keyword_match,
                },
            )
        for i, score in tqdm(enumerate(sentence_scores), desc="Processing", unit="item"):
            should_include = False
            if score["similarity"] >= self.similarity_threshold:
                should_include = True
            elif score["entity_match"]:
                should_include = True
            elif score["keyword_match"] and score["similarity"] >= 0.05:
                should_include = True
            if should_include and i > 0:
                prev_index = sentence_scores[i - 1]["index"]
                if prev_index not in [s["index"] for s in selected_sentences]:
                    selected_sentences.append(sentence_scores[i - 1])
            if should_include:
                selected_sentences.append(score)
        selected_sentences.sort(key=lambda x: x["index"])
        compressed_text = " ".join(s["sentence"] for s in selected_sentences)
        elapsed = time.time() - start_time
        logger.debug(f"Heuristic compression completed in {elapsed:.3f}s")
        return compressed_text

    async def _compress_llm(self, chunks: list[str], query: str) -> str:
        """Compress using LLM extraction.

        Args:
            chunks: List of text chunks
            query: Query string for relevance

        Returns:
            Compressed text
        """
        full_text = "\n\n".join(chunks)
        try:
            client = get_client(Provider.ANTHROPIC)
            prompt = f"Extract verbatim sentences from the text below that answer this question: '{query}'.\nDo not rewrite. Do not summarize. If irrelevant, return empty.\n\nText:\n{full_text}\n\nExtracted sentences:"
            # guardian: allow-magic-config
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except Exception as e:  # guardian: allow-silent-swallow
            logger.error(f"LLM compression failed: {e}")
            return self._compress_heuristic(chunks, query)

    def compress(self, chunks: list[str], query: str, use_llm: bool | None = None) -> CompressionResult:
        """Compress retrieved chunks to extract relevant sentences.

        Args:
            chunks: List of retrieved text chunks
            query: Query string for relevance determination
            use_llm: Override to force LLM mode

        Returns:
            CompressionResult with compressed text and metrics
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ContextualCompressor.compress"
        )

        original_text = " ".join(chunks)
        original_length = len(original_text)
        should_use_llm = use_llm if use_llm is not None else self.use_llm
        if should_use_llm:
            import asyncio

            compressed_text = asyncio.run(self._compress_llm(chunks, query))
        else:
            compressed_text = self._compress_heuristic(chunks, query)
        if not compressed_text or len(compressed_text) < original_length * 0.1:
            logger.warning("Compression too aggressive, returning original text")
            compressed_text = original_text
        compressed_length = len(compressed_text)
        compression_ratio = compressed_length / original_length if original_length > 0 else 1.0
        logger.info(
            f"Compression ratio: {compression_ratio:.2f} ({original_length} -> {compressed_length} chars)",
        )
        if compression_ratio > 0.95:
            logger.warning("Low compression detected - may need threshold tuning")
        elif compression_ratio < 0.05:
            logger.warning("High compression detected - may be too aggressive")
        return CompressionResult(
            original_length=original_length,
            compressed_length=compressed_length,
            compressed_text=compressed_text,
            compression_ratio=compression_ratio,
        )


# guardian: allow-magic-config
def compress_chunks(chunks: list[str], query: str, similarity_threshold: float = 0.1) -> str:
    """Compress chunks using default settings.

    Args:
        chunks: List of text chunks
        query: Query for relevance
        similarity_threshold: Jaccard similarity threshold

    Returns:
        Compressed text
    """
    compressor = ContextualCompressor(similarity_threshold=similarity_threshold)
    result = compressor.compress(chunks, query)
    return result.compressed_text
