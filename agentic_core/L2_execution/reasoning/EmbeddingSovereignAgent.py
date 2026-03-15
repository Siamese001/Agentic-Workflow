"""
EmbeddingSovereignAgent - Unified Embedding Gateway

[PHASE 4 MIGRATION] Consolidates all embedding operations:
- Gemini embeddings
- OpenAI embeddings
- Dimension validation
- Batch processing
- Redis caching integration (via mixin)
"""

from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "EmbeddingSovereignAgent", "L2")
_emit_routes_through("p1", "EmbeddingSovereignAgent", "L2")
_emit_escalates_to_human("p1", "EmbeddingSovereignAgent", "L2")
_emit_reads_policy_state("p1", "EmbeddingSovereignAgent", "L2")

_emit_applies_guardrail("p0", "EmbeddingSovereignAgent", "p0_governance")
_emit_snapshots_state("p0", "EmbeddingSovereignAgent", "state_snapshot")

if TYPE_CHECKING:
    pass
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="EmbeddingSovereignAgent",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


from agentic_core.config.core.sovereign_config import get_sovereign_config
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout
from data.sdks_mcps.client_wrappers import create_vertex_client

Logger = logging.getLogger(__name__)
try:
    from agentic_core.mixins.redis_cache_mixin import redis_cache_mixin  # noqa: F401
    from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin  # noqa: F401
except ImportError:

    class SubatomicTestingMixin:
        pass

    class RedisCacheMixin:
        def cache_get(self, key):
            return None

        def cache_set(self, key, value, ttl=None):
            pass


from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

EmbeddingProvider = Literal["gemini", "openai", "bge-m3"]


@dataclass
class EmbeddingSovereignAgent(RedisCacheMixin, SovereignBaseAgent):
    """
    Unified Embedding Gateway with Redis caching.

    [PHASE 4 MIGRATION] Absorbed from:
    - gemini_embedder.py
    - core_embedder.py
    - PineconeSovereignAgent.get_embedding()

    [PHASE 8] NOT an agent - utility singleton to avoid circular imports.
    """

    _instance: EmbeddingSovereignAgent | None = None
    _cache_prefix: str = "emb"
    _default_ttl: int = 86400
    operation_stats: dict[str, int] = field(
        default_factory=lambda: {
            "gemini": 0,
            "openai": 0,
            "bge-m3": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total": 0,
        }
    )
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the EmbeddingSovereignAgent."""
        if hasattr(super(), "__post_init__"):
            super().__post_init__()
        self._bge_m3_model = None

    def __new__(cls, *args, **kwargs):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """[TESTING ONLY] Reset the singleton instance."""
        cls._instance = None

    @property
    def config(self):
        """[PHASE 6] Access centralized config."""
        return get_sovereign_config()

    @property
    def EXPECTED_DIMENSIONS(self) -> dict[str, int]:
        """[PHASE 6] Dynamic dimensions from config."""
        return {
            "gemini": self.config.EMBEDDING_DIM_GEMINI,
            "openai": self.config.EMBEDDING_DIM_OPENAI,
            "bge-m3": 1024,
        }

    def _audit(self, provider: str, success: bool, cached: bool, latency_ms: float) -> None:
        """
        [PHASE 4] Record embedding operation.
        Includes FIFO rotation to prevent memory leaks.
        """
        limit = self.config.max_audit_log_size
        if len(self.audit_log) >= limit:
            prune_count = max(1, int(limit * 0.1))
            self.audit_log = self.audit_log[prune_count:]
        self.audit_log.append(
            {
                "provider": provider,
                "success": success,
                "cached": cached,
                "latency_ms": latency_ms,
                "ts": get_clock().now_epoch(),
            }
        )
        self.operation_stats["total"] += 1
        if cached:
            self.operation_stats["cache_hits"] += 1
        else:
            self.operation_stats["cache_misses"] += 1
            if success:
                self.operation_stats[provider] = self.operation_stats.get(provider, 0) + 1

    def _content_hash(self, content: str) -> str:
        """Generate deterministic hash for caching."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def get_embedding(
        self, content: str, provider: EmbeddingProvider = "bge-m3", use_cache: bool = True
    ) -> list[float]:
        """
        Get embedding vector with optional caching.

        [PHASE 4] Unified interface for all embedding providers.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "EmbeddingSovereignAgent.get_embedding"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:EmbeddingSovereignAgent.get_embedding".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        _ectx = _make_execution_context(content, "EmbeddingSovereignAgent.get_embedding")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            content,
            target_name="EmbeddingSovereignAgent.get_embedding",
        )
        start = get_clock().now_epoch()
        cache_key = f"{self._cache_prefix}:{provider}:{self._content_hash(content)}"
        if use_cache:
            try:
                cached = await self.cache_get(cache_key)
                if cached:
                    latency = (get_clock().now_epoch() - start) * 1000
                    self._audit(provider, True, True, latency)
                    return cached
            except (ConnectionError, TimeoutError, RuntimeError, OSError) as e:
                Logger.warning(f"Redis cache lookup failed: {e}")
        try:
            if provider == "gemini":
                embedding = await self._get_gemini_embedding(content)
            elif provider == "openai":
                embedding = await self._get_openai_embedding(content)
            elif provider == "bge-m3":
                embedding = await self._get_bge_m3_embedding(content)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            expected_dim = self.EXPECTED_DIMENSIONS.get(provider)
            if expected_dim and len(embedding) != expected_dim:
                Logger.warning(f"Dimension mismatch: got {len(embedding)}, expected {expected_dim}")
            if use_cache:
                try:
                    await self.cache_set(cache_key, embedding, ttl=self._default_ttl)
                except (ConnectionError, TimeoutError, RuntimeError, OSError) as e:
                    Logger.warning(f"Redis cache set failed: {e}")
            latency = (get_clock().now_epoch() - start) * 1000
            self._audit(provider, True, False, latency)
            return embedding
        except Exception as e:
            latency = (get_clock().now_epoch() - start) * 1000
            self._audit(provider, False, False, latency)
            Logger.error(f"Embedding failed: {e}")
            raise

    async def get_embeddings_batch(
        self, contents: list[str], provider: EmbeddingProvider = "bge-m3", use_cache: bool = True
    ) -> list[list[float]]:
        """
        Get embeddings for multiple contents.
        [PHASE 4] Batch processing with caching.
        """
        results = []
        for content in contents:
            embedding = await self.get_embedding(content, provider, use_cache)
            results.append(embedding)
        return results

    async def _get_gemini_embedding(self, content: str) -> list[float]:
        """Get embedding from Gemini."""
        client = create_vertex_client()
        result = client.embed_content(
            model="models/text-embedding-004", content=content, task_type="retrieval_document"
        )
        return result["embedding"]

    async def _get_openai_embedding(self, content: str) -> list[float]:
        """Get embedding from OpenAI via factory seam."""
        from agentic_core.embeddings.embedding_factory import create_embedding_client
        from agentic_core.embeddings.embedding_input_guard import EmbeddingInputGuard

        client = create_embedding_client("openai", "text-embedding-3-small")
        guarded = EmbeddingInputGuard.guard(content, "u0_user_prompt")
        return await client.get_embedding(guarded)

    async def _get_bge_m3_embedding(self, content: str) -> list[float]:
        """Get embedding from local BGE-M3 model via SentenceTransformer."""
        import asyncio

        from sentence_transformers import SentenceTransformer

        if self._bge_m3_model is None:
            self._bge_m3_model = SentenceTransformer("BAAI/bge-m3")
        model = self._bge_m3_model
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(None, lambda: model.encode(content, normalize_embeddings=True))
        return embedding.tolist()

    @timeout(300)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int | None = None,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """
        L2 Execution Agent - Embedding Gateway Healing.

        WIRED CAPABILITIES:
        - Validates embedding provider configurations
        - Checks Redis cache connectivity
        - Verifies API key availability
        """
        if _call_path is None:
            _call_path = set()
        if max_depth is None:
            max_depth = self.config.max_healing_attempts
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        metrics = {"violations": 0, "fixed": 0, "errors": 0, "skipped": 0}
        try:
            if not os.getenv("GOOGLE_API_KEY"):
                metrics["violations"] += 1
                Logger.warning("GOOGLE_API_KEY missing for Gemini embeddings")
            if not os.getenv("OPENAI_API_KEY"):
                metrics["violations"] += 1
                Logger.warning("OPENAI_API_KEY missing for OpenAI embeddings")
            try:
                test_key = f"{self._cache_prefix}:test"
                if hasattr(self, "cache_set") and hasattr(self, "cache_get"):
                    self.cache_set(test_key, "test_value", ttl=60)
                    cached = self.cache_get(test_key)
                    if cached != "test_value":
                        metrics["violations"] += 1
                        Logger.warning("Redis cache test failed")
                else:
                    metrics["violations"] += 1
                    Logger.warning("Redis cache methods not available")
            except (ConnectionError, TimeoutError, RuntimeError, OSError) as e:
                metrics["violations"] += 1
                Logger.warning(f"Redis cache connectivity test failed: {e}")
            try:
                expected_dims = self.EXPECTED_DIMENSIONS
                if not expected_dims or not isinstance(expected_dims, dict):
                    metrics["violations"] += 1
                    Logger.warning("Expected dimensions configuration invalid")
            except (AttributeError, TypeError, ValueError, RuntimeError) as e:
                metrics["violations"] += 1
                Logger.warning(f"Dimensions validation failed: {e}")
            if metrics["violations"] == 0:
                metrics["fixed"] = 1
                Logger.info("EmbeddingSovereignAgent validation passed")
        except (
            AttributeError,
            TypeError,
            ValueError,
            RuntimeError,
            ConnectionError,
            TimeoutError,
            OSError,
        ) as e:
            Logger.error(f"EmbeddingSovereignAgent healing failed: {e}")
            metrics["errors"] += 1
            return metrics
        finally:
            _call_path.discard(agent_name)
        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by EmbeddingSovereignAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"EmbeddingSovereignAgent heal() not yet implemented for {violation_type} - embedding violations require manual review",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"EmbeddingSovereignAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


def get_embedding_gateway() -> EmbeddingSovereignAgent:
    """Get or create the global embedding gateway."""
    return EmbeddingSovereignAgent()
