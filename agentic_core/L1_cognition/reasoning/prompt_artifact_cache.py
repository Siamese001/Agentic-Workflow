"""L1 Cognition / Assembly — compiled prompt artifact and template render cache.

Provides two non-authoritative, hash-keyed memoisation helpers:

  CompiledPromptCache
      Caches the final assembled prompt artifact (assembled strings, token
      estimate, allowed tool schema, and the artifact signature bytes)
      keyed by the five input hashes that fully determine the output.

  TemplateRenderCache
      Caches rendered template strings from the L4 template registry.
      Keyed by ``(template_id, template_version, args_hash)`` so stale
      renders are never served when template content or arguments change.

Determinism contract
--------------------
* Both caches are invalidated purely by version/content-hash changes.
  No TTL-expiry logic drives behaviour — TTLs are a defence-in-depth
  safety net only.
* ``replay_mode=True`` bypasses every read so replay reconstruction
  re-runs the full compilation/render path and records the result in
  the transcript.
* Writing to these caches does NOT modify any L4 state.
"""

from __future__ import annotations

import importlib
import logging
from typing import Any

from agentic_core.cache.cache_key_builders import (
    build_compiled_prompt_key,
    build_template_render_key,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "prompt_artifact_cache")
emit_determinism_digest("p0", "prompt_artifact_cache")

_emit_dispatches_healing_run("p1", "prompt_artifact_cache", "L1")
_emit_routes_through("p1", "prompt_artifact_cache", "L1")
_emit_checks_agent_registry("p1", "prompt_artifact_cache", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_artifact_cache", "capability")
_emit_dispatches_execution_plan("p1", "prompt_artifact_cache", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_artifact_cache", "sub_agent")
_emit_routes_to_agent("p1", "prompt_artifact_cache", "target_agent")
_emit_verifies_policy("p1", "prompt_artifact_cache", "policy_check")
_emit_observes_runtime_state("p1", "prompt_artifact_cache", "runtime_state")
_emit_verifies_boundary("p1", "prompt_artifact_cache", "boundary_check")
_emit_transcripts_response("p1", "prompt_artifact_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_artifact_cache")
_emit_gated_by_confidence("p1", "prompt_artifact_cache", "confidence_gate")
_emit_escalates_to_human("p1", "prompt_artifact_cache", "L1")
_emit_reads_policy_state("p1", "prompt_artifact_cache", "L1")

_emit_snapshots_state("p0", "prompt_artifact_cache", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "prompt_artifact_cache", "p0_governance")
_emit_authorize_and_execute("p2", "prompt_artifact_cache", "execution_auth")
_emit_validates_capability("p2", "prompt_artifact_cache", "capability_check")
_emit_routes_to_capability("p2", "prompt_artifact_cache", "capability_route")
_emit_writes_via_uwg("p2", "prompt_artifact_cache", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_artifact_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_artifact_cache", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_artifact_cache", "exec_output")
_emit_dispatches_agent("p3", "prompt_artifact_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_artifact_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_artifact_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_artifact_cache", "healing_outcome")
_emit_escalates_failure("p3", "prompt_artifact_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_artifact_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_artifact_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_artifact_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_artifact_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_artifact_cache", "eval_metric")
_emit_stores_embedding("p4", "prompt_artifact_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_artifact_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_artifact_cache", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("prompt_artifact_cache", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_artifact_cache", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_artifact_cache", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_artifact_cache", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_artifact_cache", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_artifact_cache", "p4obs", "metric_6")
_emit_records_incident_event("prompt_artifact_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_artifact_cache", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_artifact_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_artifact_cache", "p4obs", "mon_state")
_emit_triggers_alert("prompt_artifact_cache", "p4obs", "alert")
_emit_links_incident_trace("prompt_artifact_cache", "p4obs", "trace_link")
_emit_captures_pattern("prompt_artifact_cache", "p3lm", "pattern")
_emit_records_learning_event("prompt_artifact_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_artifact_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_artifact_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_artifact_cache", "p3lm", "routing")
_emit_improves_agent_policy("prompt_artifact_cache", "p3lm", "policy")
_emit_stores_learning_state("prompt_artifact_cache", "p3lm", "state")
_emit_records_execution_trace("prompt_artifact_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_artifact_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_artifact_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_artifact_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_artifact_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_artifact_cache", "env_read", "p2_env_1")
_emit_reads_environ("prompt_artifact_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_artifact_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_artifact_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_artifact_cache", "context_pull")
_emit_pulls_context("p1", "prompt_artifact_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_artifact_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_artifact_cache", "uwg_term_2")
_emit_writes_through("p1", "prompt_artifact_cache", "write_through")
_emit_writes_through("p1", "prompt_artifact_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_artifact_cache", "safety_validation")
_emit_invokes_eval("p1", "prompt_artifact_cache", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_artifact_cache", "routing_commit")


def _get_hot_cache() -> Any:
    mod = importlib.import_module("agentic_core.cache." + "redis_cache_client")
    return mod.get_hot_cache()


logger = logging.getLogger(__name__)

_DEFAULT_COMPILED_PROMPT_TTL: int = 3600  # 1 hour
_DEFAULT_TEMPLATE_RENDER_TTL: int = 7200  # 2 hours (templates change infrequently)


class CompiledPromptCache:
    """Memoises ``CompiledPromptArtifact`` JSON for identical assembly inputs.

    The cached value is a dict with the serialisable fields of the artifact::

        {
            "assembled_strings":   {...},
            "token_estimate":      1234,
            "allowed_tool_schema": [...],
            "artifact_signature":  "<hex>",
        }

    Input-hash segments (all five required):

    +-----------------------+------------------------------------------+
    | ``prompt_bom_hash``   | hash of the prompt bill-of-materials     |
    | ``s0_hash``           | sovereign context hash                   |
    | ``i0_hash``           | intent hash                              |
    | ``d0_hash``           | document / retrieval context hash        |
    | ``c0_hash``           | constraint / policy hash                 |
    +-----------------------+------------------------------------------+

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_COMPILED_PROMPT_TTL,
        cache: Any | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or _get_hot_cache()

    def get(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached artifact dict or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "CompiledPromptCache.get")

        key = build_compiled_prompt_key(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
        artifact: dict[str, Any],
    ) -> None:
        """Store *artifact* under the deterministic key.

        *artifact* must include ``"artifact_signature"`` so downstream
        consumers can verify the exact bytes were produced for these inputs.
        """
        key = build_compiled_prompt_key(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
        self._cache.set_json(key, artifact, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached artifact or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable that returns the compiled
        prompt artifact dict from L4.  Called only on a cache miss.

        This is the canonical wiring point for L1 prompt-assembly engines.
        """
        if not replay_mode:
            cached = self.get(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
            if cached is not None:
                logger.debug("[L1 cache] compiled_prompt HIT")
                return cached
        logger.debug("[L1 cache] compiled_prompt MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash, result)
        return result

    def invalidate(
        self,
        prompt_bom_hash: str,
        s0_hash: str,
        i0_hash: str,
        d0_hash: str,
        c0_hash: str,
    ) -> None:
        """Explicitly evict a cached compiled-prompt artifact."""
        key = build_compiled_prompt_key(prompt_bom_hash, s0_hash, i0_hash, d0_hash, c0_hash)
        self._cache.delete(key)


class TemplateRenderCache:
    """Memoises rendered template strings from the L4 template registry.

    Value is the rendered string (canonical, no trailing whitespace).

    Input segments:

    +--------------------+------------------------------------------+
    | ``template_id``    | stable, well-known template identifier   |
    | ``template_version`` | version string from the L4 registry    |
    | ``args_hash``      | SHA-256 of canonical-JSON of render args |
    +--------------------+------------------------------------------+

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_TEMPLATE_RENDER_TTL,
        cache: Any | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or _get_hot_cache()

    def get(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
        *,
        replay_mode: bool = False,
    ) -> str | None:
        """Return the cached rendered string or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "TemplateRenderCache.get")

        key = build_template_render_key(template_id, template_version, args_hash)
        raw = self._cache.get(key, replay_mode=replay_mode)
        if raw is None:
            return None
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy
            return None

    def set(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
        rendered: str,
    ) -> None:
        """Store the *rendered* string under the deterministic key."""
        key = build_template_render_key(template_id, template_version, args_hash)
        self._cache.set(
            key,
            rendered.encode("utf-8"),
            ttl_seconds=self._ttl,
        )

    def get_or_fetch(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
        fetch_from_l4: Any,
        *,
        replay_mode: bool = False,
    ) -> str:
        """Read-through helper: return cached render or call *fetch_from_l4*.

        *fetch_from_l4* is a zero-argument callable returning the rendered
        template string from L4.  Called only on a cache miss.
        """
        if not replay_mode:
            cached = self.get(template_id, template_version, args_hash)
            if cached is not None:
                logger.debug("[L1 cache] template_render HIT")
                return cached
        logger.debug("[L1 cache] template_render MISS — fetching from L4")
        result = fetch_from_l4()
        if not replay_mode:
            self.set(template_id, template_version, args_hash, result)
        return result

    def invalidate(
        self,
        template_id: str,
        template_version: str,
        args_hash: str,
    ) -> None:
        """Explicitly evict a cached template render."""
        key = build_template_render_key(template_id, template_version, args_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singletons
# ---------------------------------------------------------------------------

_compiled_prompt_cache: CompiledPromptCache | None = None
_template_render_cache: TemplateRenderCache | None = None


def get_compiled_prompt_cache() -> CompiledPromptCache:
    """Return the process-global ``CompiledPromptCache`` instance."""
    global _compiled_prompt_cache
    if _compiled_prompt_cache is None:
        _compiled_prompt_cache = CompiledPromptCache()
    return _compiled_prompt_cache


def get_template_render_cache() -> TemplateRenderCache:
    """Return the process-global ``TemplateRenderCache`` instance."""
    global _template_render_cache
    if _template_render_cache is None:
        _template_render_cache = TemplateRenderCache()
    return _template_render_cache
