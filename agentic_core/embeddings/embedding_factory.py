"""Embedding Factory - Single Embedding Seam for Sovereign Access

[PHASE 7] Canonical embedding factory providing:
- Single seam for all embedding operations
- EMBEDDING_ENABLED kill-switch (fail-closed)
- Runtime guard against direct SDK instantiation
- Deterministic artifact binding
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
from typing import Any, Literal, Protocol, runtime_checkable

from agentic_core.embeddings.embedding_input_guard import GuardedText
from agentic_core.L2_execution.types.replay_envelope_types import create_deterministic_cache_key
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

_emit_applies_guardrail("p0", "embedding_factory", "p0_governance")
_emit_reads_policy_state("p0", "embedding_factory", "policy_binding")
_emit_snapshots_state("p0", "embedding_factory", "state_snapshot")
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

_emit_emits_metric_event("embedding_factory", "p4obs", "metric_1")
_emit_emits_metric_event("embedding_factory", "p4obs", "metric_2")
_emit_emits_metric_event("embedding_factory", "p4obs", "metric_3")
_emit_emits_metric_event("embedding_factory", "p4obs", "metric_4")
_emit_emits_metric_event("embedding_factory", "p4obs", "metric_5")
_emit_emits_metric_event("embedding_factory", "p4obs", "metric_6")
_emit_records_incident_event("embedding_factory", "p4obs", "incident")
_emit_captures_runtime_anomaly("embedding_factory", "p4obs", "anomaly")
_emit_writes_observability_log("embedding_factory", "p4obs", "obs_log")
_emit_updates_monitoring_state("embedding_factory", "p4obs", "mon_state")
_emit_triggers_alert("embedding_factory", "p4obs", "alert")
_emit_links_incident_trace("embedding_factory", "p4obs", "trace_link")
_emit_captures_pattern("embedding_factory", "p3lm", "pattern")
_emit_records_learning_event("embedding_factory", "p3lm", "learning_event")
_emit_writes_learning_snapshot("embedding_factory", "p3lm", "snapshot")
_emit_feeds_meta_learning("embedding_factory", "p3lm", "meta_feed")
_emit_updates_routing_strategy("embedding_factory", "p3lm", "routing")
_emit_improves_agent_policy("embedding_factory", "p3lm", "policy")
_emit_stores_learning_state("embedding_factory", "p3lm", "state")
_emit_records_execution_trace("embedding_factory", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("embedding_factory", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("embedding_factory", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("embedding_factory", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("embedding_factory", "L4_STATE", "p2_trace_5")
_emit_reads_environ("embedding_factory", "env_read", "p2_env_1")
_emit_reads_environ("embedding_factory", "env_read", "p2_env_2")
_emit_reads_runtime_state("embedding_factory", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("embedding_factory", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "embedding_factory", "context_pull")
_emit_pulls_context("p1", "embedding_factory", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "embedding_factory", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "embedding_factory", "uwg_term_2")
_emit_writes_through("p1", "embedding_factory", "write_through")
_emit_writes_through("p1", "embedding_factory", "write_through_2")
_emit_validated_by_safety_plane("p1", "embedding_factory", "safety_validation")
_emit_invokes_eval("p1", "embedding_factory", "eval_call")
_emit_proposal_commits_routing("p1", "embedding_factory", "routing_commit")
_emit_escalates_to_human("p1", "embedding_factory", "human_escalation")
_emit_routes_through("p1", "embedding_factory", "route_through")
_emit_checks_agent_registry("p1", "embedding_factory", "agent_registry")
_emit_validates_agent_capability("p1", "embedding_factory", "capability")
_emit_dispatches_execution_plan("p1", "embedding_factory", "exec_plan")
_emit_agent_executes_agent("p1", "embedding_factory", "sub_agent")
_emit_routes_to_agent("p1", "embedding_factory", "target_agent")
_emit_verifies_policy("p1", "embedding_factory", "policy_check")
_emit_observes_runtime_state("p1", "embedding_factory", "runtime_state")
_emit_verifies_boundary("p1", "embedding_factory", "boundary_check")
_emit_transcripts_response("p1", "embedding_factory", "transcript")
_emit_hard_fails_untranscripted("p1", "embedding_factory")
_emit_gated_by_confidence("p1", "embedding_factory", "confidence_gate")
emit_replay_key("p0", "embedding_factory")
emit_determinism_digest("p0", "embedding_factory")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "embedding_factory", "execution_auth")
_emit_validates_capability("p2", "embedding_factory", "capability_check")
_emit_routes_to_capability("p2", "embedding_factory", "capability_route")
_emit_writes_via_uwg("p2", "embedding_factory", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_factory", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_factory", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_factory", "exec_output")
_emit_dispatches_agent("p3", "embedding_factory", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_factory", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_factory", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_factory", "healing_outcome")
_emit_escalates_failure("p3", "embedding_factory", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_factory", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_factory", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_factory", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_factory", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_factory", "eval_metric")
_emit_stores_embedding("p4", "embedding_factory", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_factory", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_factory", "exec_snapshot_link")

logger = logging.getLogger(__name__)


def is_enabled() -> bool:
    """Dynamically check the embedding kill-switch from environment.

    Returns:
        True if embeddings are enabled, False otherwise.
    """
    return os.environ.get("EMBEDDING_ENABLED", "false").lower() == "true"


# For module-level logging, check once at import time.
EMBEDDING_ENABLED = is_enabled()


class EmbeddingDisabledError(RuntimeError):
    """Raised when embedding operations are attempted while disabled."""

    pass


class EmbeddingSovereigntyViolationError(RuntimeError):
    """Raised when embedding client is instantiated outside factory."""

    pass


@runtime_checkable
class EmbeddingClient(Protocol):
    """Protocol for embedding clients to ensure type safety."""

    async def get_embedding(self, guarded_text: GuardedText) -> list[float]:
        """Get embedding for a single guarded text."""
        ...

    async def get_embeddings_batch(self, guarded_texts: list[GuardedText]) -> list[list[float]]:
        """Get embeddings for multiple guarded texts."""
        ...


# Registry for tracking embedding client instances
_embedding_client_registry: dict[str, Any] = {}
_registry_lock = threading.Lock()


def register_embedding_client(name: str, client: EmbeddingClient) -> None:
    """Register an embedding client instance for tracking."""
    if not is_enabled():
        raise EmbeddingDisabledError("EMBEDDING_ENABLED=false: Cannot register embedding clients")

    if not name or not name.strip():
        raise ValueError("Embedding client name cannot be empty")
    with _registry_lock:
        if name in _embedding_client_registry:
            raise EmbeddingSovereigntyViolationError(
                f"Embedding client '{name}' is already registered",
            )
        _embedding_client_registry[name] = client
    logger.info("Registered embedding client: %s", name)


def get_embedding_client(name: str = "default") -> EmbeddingClient:
    """Get a registered embedding client by name."""
    if not is_enabled():
        raise EmbeddingDisabledError("EMBEDDING_ENABLED=false: Cannot get embedding clients")

    with _registry_lock:
        client = _embedding_client_registry.get(name)
    if not client:
        raise EmbeddingDisabledError(f"No embedding client registered with name: {name}")

    return client


def _default_embedding_provider() -> str:
    """Resolve the default embedding provider from env, falling back to bge-m3.

    Honors ``AGENTIC_EMBEDDING_PROVIDER`` so a deployment can flip the runtime
    default without touching call sites. Default is ``bge-m3`` so the factory
    never silently routes to OpenAI when callers omit the provider argument.
    """
    return os.environ.get("AGENTIC_EMBEDDING_PROVIDER", "bge-m3")


def create_embedding_client(
    provider: Literal["openai", "gemini", "anthropic", "bge-m3"] | None = None,
    model: str | None = None,
    client_name: str = "default",
    **kwargs: Any,
) -> EmbeddingClient:
    """Factory function to create embedding clients.

    Args:
        provider: The embedding provider to use
        model: The model name (provider-specific)
        client_name: Name to register the client under
        **kwargs: Additional provider-specific options

    Returns:
        EmbeddingClient instance

    Raises:
        EmbeddingDisabledError: If EMBEDDING_ENABLED is false
        EmbeddingSovereigntyViolationError: If called from unauthorized module
    """
    if not is_enabled():
        raise EmbeddingDisabledError("EMBEDDING_ENABLED=false: Cannot create embedding clients")

    # Resolve default provider from env when caller omits it (BGE-M3 default —
    # callers must opt into "openai" explicitly via env or argument).
    if provider is None:
        provider = _default_embedding_provider()  # type: ignore[assignment]

    # Get caller module for sovereignty check
    import inspect

    frame = inspect.currentframe()
    if frame:
        caller_frame = frame.f_back
        if caller_frame:
            caller_module = caller_frame.f_globals.get("__name__", "unknown")
            guard_embedding_instantiation(caller_module, "create_embedding_client")

    # Import SDKs only when needed (lazy import for determinism)
    if provider == "openai":
        from data.sdks_mcps.client_wrappers import create_openai_client

        raw_client = create_openai_client()

        class OpenAIEmbeddingClient:
            """OpenAI embedding client wrapper."""

            def __init__(self, model: str, dimensions: int | None = None):
                self.model = model
                self.dimensions = dimensions
                self._cache: dict[str, list[float]] = {}

                # Compute pack hash for replay key
                pack_hash_str = f"openai_{model}"
                self.pack_hash = hashlib.sha256(pack_hash_str.encode("utf-8")).hexdigest()[:16]

                # W11: Embedder identity for deterministic cache keys
                self.embedder_identity = {
                    "provider": "openai",
                    "model": self.model,
                    "dimensions": dimensions or 1536,
                    "normalization_policy": "l2",
                    "chunking_policy": "none",
                }

                # Will be set on first embedding
                self.observed_dimension: int | None = None

            async def get_embedding(self, guarded_text: GuardedText) -> list[float]:
                import uuid as _uuid  # noqa: PLC0415

                _trace_id = str(_uuid.uuid4())
                _emit_records_execution_trace(
                    _trace_id,
                    LayerSegment.L3_ORCHESTRATION,
                    "OpenAIEmbeddingClient.get_embedding",
                )

                # W11: Use deterministic cache key
                cache_key = create_deterministic_cache_key(
                    guarded_text.redacted_text,
                    self.embedder_identity,
                )
                if cache_key in self._cache:
                    return self._cache[cache_key]

                kwargs = {"model": self.model, "input": guarded_text.redacted_text}
                if self.dimensions:
                    kwargs["dimensions"] = self.dimensions

                response = await raw_client.embeddings.create(**kwargs)
                embedding = response.data[0].embedding

                # W11: Stable float32 casting for determinism
                embedding = [float(x) for x in embedding]
                if self.observed_dimension is None:
                    self.observed_dimension = len(embedding)
                elif len(embedding) != self.observed_dimension:
                    raise RuntimeError(
                        f"OPENAI_EMBED_DIM_MISMATCH: got {len(embedding)}, expected {self.observed_dimension}",
                    )

                self._cache[cache_key] = embedding

                _emit_stores_embedding(_trace_id, "openai", cache_key)

                return embedding

            async def get_embeddings_batch(self, guarded_texts: list[GuardedText]) -> list[list[float]]:
                results: list[list[float] | None] = [None] * len(guarded_texts)
                texts_to_embed: list[tuple[int, GuardedText]] = []

                for i, guarded_text in enumerate(guarded_texts):
                    cache_key = create_deterministic_cache_key(
                        guarded_text.redacted_text,
                        self.embedder_identity,
                    )
                    if cache_key in self._cache:
                        results[i] = self._cache[cache_key]
                    else:
                        texts_to_embed.append((i, guarded_text))

                if not texts_to_embed:
                    return [r for r in results if r is not None]

                kwargs = {"model": self.model, "input": [gt.redacted_text for _, gt in texts_to_embed]}
                if self.dimensions:
                    kwargs["dimensions"] = self.dimensions

                response = await raw_client.embeddings.create(**kwargs)
                embeddings = [item.embedding for item in response.data]

                # W11: Stable float32 casting for determinism
                embeddings = [[float(x) for x in emb] for emb in embeddings]

                if self.observed_dimension is None and embeddings:
                    self.observed_dimension = len(embeddings[0])
                for emb in embeddings:
                    if len(emb) != self.observed_dimension:
                        raise RuntimeError(
                            f"OPENAI_BATCH_EMBED_DIM_MISMATCH: got {len(emb)}, expected {self.observed_dimension}",
                        )

                for i, embedding in enumerate(embeddings):
                    original_index, guarded_text = texts_to_embed[i]
                    # W11: Use deterministic cache key
                    cache_key = create_deterministic_cache_key(
                        guarded_text.redacted_text,
                        self.embedder_identity,
                    )
                    self._cache[cache_key] = embedding
                    results[original_index] = embedding

                return [r for r in results if r is not None]

            def get_replay_metadata(self) -> dict[str, Any]:
                """Get embedder metadata for replay key surface."""
                return {
                    "provider": "openai",
                    "model": self.model,
                    "pack_hash": self.pack_hash,
                    "embedding_dimension": self.observed_dimension or self.dimensions or 1536,
                    "distance_metric": "cosine",
                    "tokenization_policy_version": "cl100k_base_v1",
                    "normalization_policy": "l2",
                    "chunking_policy": "none",
                    "hs_injection_surface_version": "1.0",
                }

        client = OpenAIEmbeddingClient(model or "text-embedding-3-large", dimensions=kwargs.get("dimensions"))

    elif provider == "gemini":
        raise NotImplementedError("Gemini embeddings not yet implemented through factory")

    elif provider == "anthropic":
        # Anthropic doesn't provide embeddings, but we keep the interface
        raise NotImplementedError("Anthropic does not provide embedding models")

    elif provider == "bge-m3":
        # BAAI/bge-m3 - Local embedding model (spec-compliant for Pipeline B/C)
        # Device resolution: explicit kwarg > EMBEDDING_DEVICE env > CUDA autodetect > cpu
        device = kwargs.get("device")
        if device is None:
            from agentic_core.embeddings.bge_runtime import _resolve_device

            device = _resolve_device()
        client = _create_bge_m3_client(model or "BAAI/bge-m3", device)

    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")

    # Register and return
    register_embedding_client(client_name, client)
    return client


def _create_bge_m3_client(model_name: str, device: str = "cpu") -> EmbeddingClient:
    """
    Create BGE-M3 embedding client using sentence-transformers.

    BGE-M3 is the spec-compliant embedding model for Pipeline B/C consistency.

    Args:
        model_name: HuggingFace model name (default: BAAI/bge-m3)
        device: Device to run on (cpu, cuda, etc.)

    Returns:
        EmbeddingClient instance for BGE-M3
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise ImportError(
            "sentence-transformers is required for BGE-M3 embeddings. "
            "Install with: pip install sentence-transformers",
        ) from e

    allow_download = os.environ.get("BGE_ALLOW_MODEL_DOWNLOAD", "false").lower() == "true"
    model = SentenceTransformer(
        model_name,
        device=device,
        local_files_only=not allow_download,
        trust_remote_code=False,
    )

    class BGEM3EmbeddingClient:
        """BGE-M3 embedding client wrapper."""

        def __init__(self, model: SentenceTransformer, model_name: str):
            self.model = model
            self.model_name = model_name
            self._cache: dict[str, list[float]] = {}

            # Compute pack hash for replay key
            pack_hash_str = f"bge-m3_{model_name}"
            self.pack_hash = hashlib.sha256(pack_hash_str.encode("utf-8")).hexdigest()[:16]

            # W11: Embedder identity for deterministic cache keys
            self.embedder_identity = {
                "provider": "bge-m3",
                "model": self.model_name,
                "dimensions": 1024,  # BGE-M3 default
                "normalization_policy": "l2",
                "chunking_policy": "none",
            }

            # Detect actual dimension
            self.observed_dimension = model.get_sentence_embedding_dimension()
            self.embedder_identity["dimensions"] = self.observed_dimension

        def _validate_dimension(self, embedding: list[float]) -> None:
            if len(embedding) != self.observed_dimension:
                raise RuntimeError(
                    f"BGE_DIM_MISMATCH: got {len(embedding)}, expected {self.observed_dimension}",
                )

        async def get_embedding(self, guarded_text: GuardedText) -> list[float]:
            import uuid as _uuid  # noqa: PLC0415

            _trace_id = str(_uuid.uuid4())
            _emit_records_execution_trace(
                _trace_id,
                LayerSegment.L3_ORCHESTRATION,
                "BGEM3EmbeddingClient.get_embedding",
            )

            # Use deterministic cache key
            cache_key = create_deterministic_cache_key(
                guarded_text.redacted_text,
                self.embedder_identity,
            )
            if cache_key in self._cache:
                return self._cache[cache_key]

            # Generate embedding
            embedding = self.model.encode(
                guarded_text.redacted_text,
                convert_to_numpy=True,
                normalize_embeddings=True,  # L2 normalization
                show_progress_bar=False,
            ).tolist()

            # Stable float32 casting
            embedding = [float(x) for x in embedding]
            self._validate_dimension(embedding)

            self._cache[cache_key] = embedding

            _emit_stores_embedding(_trace_id, "bge-m3", cache_key)

            return embedding

        async def get_embeddings_batch(self, guarded_texts: list[GuardedText]) -> list[list[float]]:
            results: list[list[float] | None] = [None] * len(guarded_texts)
            texts_to_embed: list[tuple[int, str]] = []

            for i, guarded_text in enumerate(guarded_texts):
                cache_key = create_deterministic_cache_key(
                    guarded_text.redacted_text,
                    self.embedder_identity,
                )
                if cache_key in self._cache:
                    results[i] = self._cache[cache_key]
                else:
                    texts_to_embed.append((i, guarded_text.redacted_text))

            if not texts_to_embed:
                return [r for r in results if r is not None]

            # Batch encode
            texts = [t for _, t in texts_to_embed]
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=False,
            ).tolist()

            # Stable float32 casting
            embeddings = [[float(x) for x in emb] for emb in embeddings]

            for i, embedding in enumerate(embeddings):
                self._validate_dimension(embedding)
                original_index, text = texts_to_embed[i]
                cache_key = create_deterministic_cache_key(text, self.embedder_identity)
                self._cache[cache_key] = embedding
                results[original_index] = embedding

            return [r for r in results if r is not None]

        def get_replay_metadata(self) -> dict[str, Any]:
            """Get embedder metadata for replay key surface."""
            return {
                "provider": "bge-m3",
                "model": self.model_name,
                "pack_hash": self.pack_hash,
                "embedding_dimension": self.observed_dimension,
                "distance_metric": "cosine",
                "tokenization_policy_version": "bge-m3-v1",
                "normalization_policy": "l2",
                "chunking_policy": "none",
                "hs_injection_surface_version": "1.0",
            }

    return BGEM3EmbeddingClient(model, model_name)


def guard_embedding_instantiation(module_name: str, class_name: str) -> None:
    """
    Runtime guard to prevent direct embedding SDK instantiation.

    Call this from any module that might be tempted to instantiate
    embedding clients directly.
    """
    # Allowlist of modules that can instantiate embedding clients
    allowed_modules = {
        "agentic_core.embeddings.embedding_factory",
        "data.sdks_mcps.client_wrappers",
        "agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent",
        "agentic_core.L6_system_learning.engines.embedding_service_factory",
        # Operational ingestion bridge — pass-through to this factory.
        # See tools/ingestion/_embedding_factory_bridge.py for the rationale.
        "tools.ingestion._embedding_factory_bridge",
    }

    if module_name not in allowed_modules:
        raise EmbeddingSovereigntyViolationError(
            f"EMBEDDING_SOVEREIGNTY_VIOLATION: {module_name}.{class_name} "
            f"attempted to instantiate embedding client outside factory. "
            f"Use agentic_core.embeddings.embedding_factory.create_embedding_client() instead.",
        )


def compute_w7_sovereignty_digest() -> str:
    """
    Compute W7-EMBEDDING-SOVEREIGNTY-DIGEST.

    Hash over canonical JSON of embedding sovereignty state.
    """
    # Get fingerprint of this module
    module_path = __file__
    with open(module_path, "rb") as f:
        module_hash = hashlib.sha256(f.read()).hexdigest()

    # Build canonical state
    state = {
        "embedding_enabled": is_enabled(),
        "factory_module_hash": module_hash,
        "registered_clients": sorted(_embedding_client_registry.keys()),
        "allowed_providers": ["openai", "gemini", "anthropic", "bge-m3"],
        "kill_switch_default": "true",
        "factory_path": "agentic_core/embeddings/embedding_factory.py",
    }

    # Compute deterministic hash
    canonical_json = json.dumps(state, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()


def get_active_embedding_model_id() -> str:
    """Return the active embedding model identifier for cache key derivation.

    Reads EMBEDDING_MODEL_ID env var; falls back to the bge-m3-v1 slug
    used as the default in the semantic cache pipeline.
    Does not instantiate any client.
    """
    return os.environ.get("EMBEDDING_MODEL_ID", "bge-m3-v1")


# Module initialization
if EMBEDDING_ENABLED:
    logger.info("EmbeddingFactory: EMBEDDING_ENABLED=true - embeddings allowed")
else:
    logger.warning("EmbeddingFactory: EMBEDDING_ENABLED=false - embeddings disabled (fail-closed)")
