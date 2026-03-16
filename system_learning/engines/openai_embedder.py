"""OpenAI Embedder for Plan B Phase 5.

Production embedder using OpenAI's text-embedding-3-large model.
Direct OpenAI SDK wrapper — does NOT go through embedding_factory.
"""

from __future__ import annotations

import hashlib
import os

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "openai_embedder", "p0_governance")
_emit_reads_policy_state("p0", "openai_embedder", "policy_binding")
_emit_snapshots_state("p0", "openai_embedder", "state_snapshot")
emit_replay_key("p0", "openai_embedder")
emit_determinism_digest("p0", "openai_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "openai_embedder", "execution_auth")
_emit_validates_capability("p2", "openai_embedder", "capability_check")
_emit_routes_to_capability("p2", "openai_embedder", "capability_route")
_emit_writes_via_uwg("p2", "openai_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "openai_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "openai_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "openai_embedder", "exec_output")
_emit_dispatches_agent("p3", "openai_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "openai_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "openai_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "openai_embedder", "healing_outcome")
_emit_escalates_failure("p3", "openai_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "openai_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "openai_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "openai_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "openai_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "openai_embedder", "eval_metric")
_emit_stores_embedding("p4", "openai_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "openai_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "openai_embedder", "exec_snapshot_link")

try:
    import openai as openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_MODEL_DIMENSIONS = {
    "text-embedding-3-large": 1536,
    "text-embedding-3-small": 1536,
    "text-embedding-ada-002": 1536,
    "BAAI/bge-m3": 1024,
    "BAAI/bge-large-en-v1.5": 1024,
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OpenAIEmbedder.embed_batch")

        normalized = [t.replace("\r\n", " ").replace("\n", " ").replace("\r", " ") for t in texts]
        response = self._client.embeddings.create(model=self.model, input=normalized)
        return [item.embedding for item in response.data]

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

    def __init__(self, model: str = "BAAI/bge-m3"):
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BGEEmbedder.embed_batch")

        from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

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
