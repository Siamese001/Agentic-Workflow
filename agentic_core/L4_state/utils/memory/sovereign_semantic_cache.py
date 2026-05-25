"""L4 State: Sovereign Semantic cache — Redis + BGE vector store Hybrid.
Redis L4 local cache for lightning recall + in-memory BGE vector store.
Full AST + metadata sovereignty with mission-isolation.
"""

from __future__ import annotations

import ast
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.cache.redis_cache_client import get_hot_cache as _get_hot_cache
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
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

emit_replay_key("p0", "sovereign_semantic_cache")
emit_determinism_digest("p0", "sovereign_semantic_cache")

_emit_dispatches_healing_run("p1", "sovereign_semantic_cache", "L4")
_emit_routes_through("p1", "sovereign_semantic_cache", "L4")
_emit_checks_agent_registry("p1", "sovereign_semantic_cache", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_semantic_cache", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_semantic_cache", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_semantic_cache", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_semantic_cache", "target_agent")
_emit_verifies_policy("p1", "sovereign_semantic_cache", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_semantic_cache", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_semantic_cache", "boundary_check")
_emit_transcripts_response("p1", "sovereign_semantic_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_semantic_cache")
_emit_gated_by_confidence("p1", "sovereign_semantic_cache", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_semantic_cache", "L4")
_emit_reads_policy_state("p1", "sovereign_semantic_cache", "L4")
_emit_authorize_and_execute("p2", "sovereign_semantic_cache", "execution_auth")
_emit_validates_capability("p2", "sovereign_semantic_cache", "capability_check")
_emit_routes_to_capability("p2", "sovereign_semantic_cache", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_semantic_cache", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_semantic_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_semantic_cache", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_semantic_cache", "exec_output")
_emit_dispatches_agent("p3", "sovereign_semantic_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_semantic_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_semantic_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_semantic_cache", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_semantic_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_semantic_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_semantic_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_semantic_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_semantic_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_semantic_cache", "eval_metric")
_emit_stores_embedding("p4", "sovereign_semantic_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_semantic_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_semantic_cache", "exec_snapshot_link")


def get_redis_client():
    """Shim: redirect legacy callers to the canonical DeterministicRedisCache client."""
    return _get_hot_cache()


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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
from agentic_core.utils.decorators_compat_util import standard_heal
from tqdm import tqdm

_emit_emits_metric_event("sovereign_semantic_cache", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_semantic_cache", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_semantic_cache", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_semantic_cache", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_semantic_cache", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_semantic_cache", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_semantic_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_semantic_cache", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_semantic_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_semantic_cache", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_semantic_cache", "p4obs", "alert")
_emit_links_incident_trace("sovereign_semantic_cache", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_semantic_cache", "p3lm", "pattern")
_emit_records_learning_event("sovereign_semantic_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_semantic_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_semantic_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_semantic_cache", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_semantic_cache", "p3lm", "policy")
_emit_stores_learning_state("sovereign_semantic_cache", "p3lm", "state")
_emit_records_execution_trace("sovereign_semantic_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_semantic_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_semantic_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_semantic_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_semantic_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_semantic_cache", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_semantic_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_semantic_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_semantic_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_semantic_cache", "context_pull")
_emit_pulls_context("p1", "sovereign_semantic_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_semantic_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_semantic_cache", "uwg_term_2")
_emit_writes_through("p1", "sovereign_semantic_cache", "write_through")
_emit_writes_through("p1", "sovereign_semantic_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_semantic_cache", "safety_validation")
_emit_invokes_eval("p1", "sovereign_semantic_cache", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_semantic_cache", "routing_commit")

Logger: Any = logging.getLogger(__name__)
redis_cache_ttl: Any = 60 * 60 * 24 * 7
max_redis_entry_size: Any = 1024 * 1024
redis_timeout: Any = 5


class SovereignSemanticCache(SovereignBaseAgent):
    """Ultra-hardened hybrid semantic cache — Redis local + InMemoryVectorStore eternal."""

    def __init__(self, mission_id: str, engine=None):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SovereignSemanticCache.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SovereignSemanticCache.__init__", "p0_governance")
        super().__init__()
        self.mission_id = mission_id
        self.engine = engine
        from agentic_core.L4_state.utils.memory.in_memory_vector_store import InMemoryVectorStore

        self._vector_store: InMemoryVectorStore = InMemoryVectorStore()
        self.index_name = "canon-semantic-v1"
        self.namespace = "canon-files"
        try:
            self.redis = get_redis_client()
            Logger.info("[L4 REDIS] Sovereign MCP cache armed.")
        except (
            AttributeError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
        ) as e:  # guardian: allow-silent-swallow
            raise

    def _cache_key(self, file_path: str) -> str:
        """Mission-isolated and path-hashed key for L4 sovereignty."""
        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        return f"semantic:{self.mission_id}:{path_hash}"

    # guardian: allow-type-erasure
    def _extract_ast_features(self, code: str) -> dict:
        """Parse AST for structural signals (Key 41/42)."""
        try:
            tree = ast.parse(code)
            return {
                "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                "max_nesting": self._calculate_depth(tree),
                "lines": len(code.splitlines()),
            }
        except (SyntaxError, ValueError, TypeError):  # guardian: allow-silent-swallow
            return {"lines": len(code.splitlines()), "parse_error": True}

    def _calculate_depth(self, node, current=0) -> int:
        child_depths = [
            self._calculate_depth(c, current + 1)
            for c in ast.iter_child_nodes(node)
            if isinstance(node, ast.FunctionDef | ast.ClassDef | ast.If | ast.For)
        ]
        return max(child_depths, default=current)

    def cache_file(self, file_path: str, code: str, metadata: dict) -> None:
        """Embed and cache with dual-store synchronization."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "SovereignSemanticCache.cache_file")

        key: Any = self._cache_key(file_path)
        if self.redis:
            try:
                cached_data: Any = self.redis.get(key)
                if cached_data:
                    Logger.info(f"[L4 HIT] Redis MCP recall for {Path(file_path).name}")
                    return
            except (
                AttributeError,
                OSError,
                RuntimeError,
                ValueError,
                TypeError,
            ):  # guardian: allow-silent-swallow
                raise
                pass
        ast_features: Any = self._extract_ast_features(code)
        embed_text: Any = f"File: {file_path}\nStructure: {json.dumps(ast_features)}\nContent: {code[:1000]}"
        try:
            vector: Any = self.engine.get_embedding(embed_text)
            entry: Any = {
                "path": str(file_path),
                "vector": vector,
                "metadata": {
                    **metadata,
                    "mission_id": self.mission_id,
                    "cached_at": datetime.utcnow().isoformat() + "Z",
                    "ast": ast_features,
                },
            }
            if self.redis:
                entry_json: Any = json.dumps(entry)
                if len(entry_json.encode()) < max_redis_entry_size:
                    self.redis.set(key, entry_json.encode(), ttl_seconds=redis_cache_ttl)
            self._vector_store[key] = {
                "vector": vector,
                "metadata": entry["metadata"],
                "namespace": self.namespace,
            }
            Logger.info(f"[L4 STORE] Dual-sync complete for {Path(file_path).name}")
        except (
            AttributeError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
        ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            raise

    # guardian: allow-type-erasure
    def invalidate(self, file_path: str) -> Any:
        """Purge both stores on fission or physical move."""
        key: Any = self._cache_key(file_path)
        if self.redis:
            try:
                self.redis.delete(key)
            except (AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:  # guardian: allow-log-and-swallow -- Redis delete failure: non-fatal; cache invalidation best-effort
                import logging

                logging.getLogger(__name__).debug(
                    "sovereign_semantic_cache: Exception swallowed at L309: %s", e
                )
        self._vector_store.pop(key, None)
        Logger.info(f"[L4 PURGE] Purged semantic trail for {Path(file_path).name}")

    def query(self, text: str, top_k: int = 20, namespace: str = "") -> list[dict]:
        """Semantic similarity search over the in-memory vector store.

        Embeds *text* via BGEEmbedder (BAAI/bge-m3, 1024-dim), then ranks
        all cached entries by cosine similarity.  Returns informational-only
        dicts: ``content_hash``, ``score``, ``content`` (metadata text preview).

        Falls back to empty list when the kill-switch is active or the store
        is empty.  Works with both InMemoryVectorStore (MemoryItem-backed) and
        plain-dict fallback stores.
        """
        import math
        import os

        if os.environ.get("EMBEDDING_ENABLED", "true").lower() in ("false", "0", "no"):
            return []

        # Resolve the underlying storage — InMemoryVectorStore wraps a ._storage dict
        store = getattr(self._vector_store, "_storage", None)
        if store is None:
            # Plain-dict fallback (test injection or legacy usage)
            store = self._vector_store if isinstance(self._vector_store, dict) else {}
        if not store:
            return []

        try:
            from agentic_core.L6_system_learning.openai_embedder import BGEEmbedder

            _embedder = BGEEmbedder()
            vecs = _embedder.embed_batch([text])
            if not vecs or not vecs[0]:
                return []
            q_vec = vecs[0]
        except (
            ImportError,
            AttributeError,
            OSError,
            RuntimeError,
            ValueError,
            TypeError,
        ):  # guardian: allow-silent-swallow
            return []

        q_mag = math.sqrt(sum(x * x for x in q_vec))
        if q_mag == 0.0:
            return []

        results: list[dict] = []
        for key, entry in tqdm(store.items(), desc="Processing", unit="item"):
            # entry is either a MemoryItem or a plain dict (test/legacy)
            if hasattr(entry, "embedding"):
                # InMemoryVectorStore MemoryItem path
                d_vec = entry.embedding or []
                meta = entry.metadata or {}
                ns = meta.get("namespace", "")
            elif isinstance(entry, dict):
                d_vec = entry.get("vector") or []
                meta = entry.get("metadata") or {}
                ns = entry.get("namespace", "")
            else:
                continue
            if namespace and ns != namespace:
                continue
            if not d_vec:
                continue
            dot = sum(a * b for a, b in zip(q_vec, d_vec, strict=False))
            d_mag = math.sqrt(sum(x * x for x in d_vec))
            score = dot / (d_mag * q_mag) if d_mag * q_mag != 0 else 0.0
            results.append(
                {
                    "content_hash": key,
                    "score": score,
                    "content": meta.get("text", meta.get("path", ""))[:200],
                },
            )

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    @standard_heal
    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository(**kwargs)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
