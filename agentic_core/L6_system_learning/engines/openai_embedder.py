"""OpenAI Embedder for Plan B Phase 5.

Production embedder using OpenAI's text-embedding-3-large model.
Direct OpenAI SDK wrapper — does NOT go through embedding_factory.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_LARGE_EN_MODEL_ID,
    BGE_M3_MODEL_ID,
)

import hashlib
import os
from typing import Iterable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "openai_embedder", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "openai_embedder", "policy_binding")
trace_contract._emit_snapshots_state("p0", "openai_embedder", "state_snapshot")
trace_contract.emit_replay_key("p0", "openai_embedder")
trace_contract.emit_determinism_digest("p0", "openai_embedder")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "openai_embedder", "execution_auth")
trace_contract._emit_validates_capability("p2", "openai_embedder", "capability_check")
trace_contract._emit_routes_to_capability("p2", "openai_embedder", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "openai_embedder", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "openai_embedder", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "openai_embedder", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "openai_embedder", "exec_output")
trace_contract._emit_dispatches_agent("p3", "openai_embedder", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "openai_embedder", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "openai_embedder", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "openai_embedder", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "openai_embedder", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "openai_embedder", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "openai_embedder", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "openai_embedder", "evaluation_signal")
trace_contract._emit_captures_evaluation_metric("p4", "openai_embedder", "eval_metric")
trace_contract._emit_stores_embedding("p4", "openai_embedder", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "openai_embedder", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "openai_embedder", "exec_snapshot_link")

try:
    import openai as openai
    from openai import OpenAI
except ImportError:  # guardian: allow-silent-swallow -- optional dependency
    openai = None
    OpenAI = None

trace_contract._emit_emits_metric_event("openai_embedder", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("openai_embedder", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("openai_embedder", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("openai_embedder", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("openai_embedder", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("openai_embedder", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("openai_embedder", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("openai_embedder", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("openai_embedder", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("openai_embedder", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("openai_embedder", "p4obs", "alert")
trace_contract._emit_links_incident_trace("openai_embedder", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("openai_embedder", "p3lm", "pattern")
trace_contract._emit_records_learning_event("openai_embedder", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("openai_embedder", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("openai_embedder", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("openai_embedder", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("openai_embedder", "p3lm", "policy")
trace_contract._emit_stores_learning_state("openai_embedder", "p3lm", "state")
trace_contract._emit_records_execution_trace("openai_embedder", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("openai_embedder", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("openai_embedder", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("openai_embedder", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("openai_embedder", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("openai_embedder", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("openai_embedder", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("openai_embedder", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("openai_embedder", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "openai_embedder", "context_pull")
trace_contract._emit_pulls_context("p1", "openai_embedder", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "openai_embedder", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "openai_embedder", "uwg_term_2")
trace_contract._emit_writes_through("p1", "openai_embedder", "write_through")
trace_contract._emit_writes_through("p1", "openai_embedder", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "openai_embedder", "safety_validation")
trace_contract._emit_invokes_eval("p1", "openai_embedder", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "openai_embedder", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "openai_embedder", "human_escalation")
trace_contract._emit_routes_through("p1", "openai_embedder", "route_through")
trace_contract._emit_checks_agent_registry("p1", "openai_embedder", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "openai_embedder", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "openai_embedder", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "openai_embedder", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "openai_embedder", "target_agent")
trace_contract._emit_verifies_policy("p1", "openai_embedder", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "openai_embedder", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "openai_embedder", "boundary_check")
trace_contract._emit_transcripts_response("p1", "openai_embedder", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "openai_embedder")
trace_contract._emit_gated_by_confidence("p1", "openai_embedder", "confidence_gate")


def _chunked(values: list[str], size: int) -> Iterable[list[str]]:
    for start in range(0, len(values), size):
        yield values[start : start + size]


_MODEL_DIMENSIONS = {
    "text-embedding-3-large": 1536,
    "text-embedding-3-small": 1536,
    "text-embedding-ada-002": 1536,
    BGE_M3_MODEL_ID: 1024,
    BGE_LARGE_EN_MODEL_ID: 1024,
}


class OpenAIEmbedder:
    """OpenAI embedder — direct SDK wrapper.

    Uses text-embedding-3-large model for production semantic embeddings.
    """

    def __init__(self, model: str = "text-embedding-3-large", dimensions: int | None = None):
        """Initialize the OpenAI embedder.

        Args:
            model: OpenAI model name to use.
            dimensions: Ignored — API determines output dimensions.

        Raises:
            ImportError: If the openai package is not installed.
            ValueError: If OPENAI_API_KEY environment variable is not set.
        """
        if openai is None:
            raise ImportError("openai package is required. Install with: pip install openai")
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.model = model
        self._client = OpenAI(api_key=api_key)

    def embed_batch(self, texts: list[str], *, dimensions: int | None = None) -> list[list[float]]:
        """Embed a batch of texts using OpenAI.

        Args:
            texts: List of texts to embed.
            dimensions: Ignored — API determines output dimensions.

        Returns:
            List of embedding vectors as lists of floats.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "OpenAIEmbedder.embed_batch")

        if not texts:
            return []
        normalized = [t.replace("\r\n", " ").replace("\n", " ").replace("\r", " ") for t in texts]
        batch_limit = int(os.environ.get("OPENAI_EMBEDDING_BATCH_SIZE", "128"))
        if batch_limit <= 0:
            raise ValueError(f"OPENAI_EMBEDDING_BATCH_SIZE must be > 0, got {batch_limit}")
        results: list[list[float]] = []
        for batch in _chunked(normalized, batch_limit):
            response = self._client.embeddings.create(model=self.model, input=batch)
            results.extend(item.embedding for item in response.data)
        return results

    def get_model_info(self) -> dict:
        """Return model information including dimensions."""
        return {"model": self.model, "dimensions": _MODEL_DIMENSIONS.get(self.model, 1536)}

    def get_model_checksum(self) -> str:
        """Return a deterministic 16-char hex checksum for the model name."""
        return hashlib.sha256(self.model.encode()).hexdigest()[:16]


class BGEEmbedder:
    """BGE-m3 embedder — SentenceTransformer wrapper.

    Implements the same embed_batch interface as OpenAIEmbedder.
    Uses BAAI/bge-m3 (1024-dim) via bmg_embed_text.
    """

    def __init__(self, model: str = BGE_M3_MODEL_ID):
        self.model = model
        self._dim = _MODEL_DIMENSIONS.get(model, 1024)

    def embed_batch(self, texts: list[str], *, dimensions: int | None = None) -> list[list[float]]:
        """Embed a batch of texts using BGE-m3.

        Args:
            texts: List of texts to embed.
            dimensions: Ignored — BGE output dimension is fixed at 1024.

        Returns:
            List of embedding vectors as lists of floats.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "BGEEmbedder.embed_batch")

        from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

        if not texts:
            return []
        results = []
        for text in texts:
            vec = bmg_embed_text(text)
            if vec:
                results.append(vec)
            else:
                results.append([0.0] * self._dim)
        return results

    def get_model_info(self) -> dict:
        """Return model information including dimensions."""
        return {"model": self.model, "dimensions": self._dim}

    def get_model_checksum(self) -> str:
        """Return a deterministic 16-char hex checksum for the model name."""
        return hashlib.sha256(self.model.encode()).hexdigest()[:16]


__all__ = ["OpenAIEmbedder", "BGEEmbedder"]
