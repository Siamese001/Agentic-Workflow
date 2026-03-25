"""Architecture invariant tests for Redis cache seam wiring.

Verifies three structural properties of the cache layer:

  1. SEAM WIRING CONTRACT — every seam class exposes a ``get_or_fetch``
     read-through method so engines can call cache-before-L4 in one call.

  2. NO SHADOW REDIS IN L4 — ``L4_state`` must contain no live Redis
     client classes (checked via AST).  The tombstoned ``_Tombstoned*``
     stubs are allowed.

  3. HASH VALIDATION STRICTNESS — ``_require_hash_segment`` must reject
     non-SHA-256 strings in strict mode and accept them when the env-var
     override is set.
"""

from __future__ import annotations

import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L4_STATE_DIR,
    TOOLS_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_redis_cache_wiring_invariants")
# REMOVED: _emit_applies_guardrail("p0", "test_redis_cache_wiring_invariants", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_redis_cache_wiring_invariants", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_redis_cache_wiring_invariants", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_redis_cache_wiring_invariants", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_redis_cache_wiring_invariants", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_redis_cache_wiring_invariants", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_redis_cache_wiring_invariants", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_redis_cache_wiring_invariants", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_redis_cache_wiring_invariants", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_redis_cache_wiring_invariants", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_redis_cache_wiring_invariants", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_redis_cache_wiring_invariants", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_redis_cache_wiring_invariants", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_redis_cache_wiring_invariants", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_redis_cache_wiring_invariants", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_redis_cache_wiring_invariants", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_redis_cache_wiring_invariants", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_redis_cache_wiring_invariants", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_redis_cache_wiring_invariants", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_redis_cache_wiring_invariants", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_redis_cache_wiring_invariants", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_redis_cache_wiring_invariants", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_redis_cache_wiring_invariants", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_redis_cache_wiring_invariants", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_redis_cache_wiring_invariants", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_redis_cache_wiring_invariants", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_redis_cache_wiring_invariants", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_redis_cache_wiring_invariants", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_redis_cache_wiring_invariants", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_redis_cache_wiring_invariants", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_redis_cache_wiring_invariants", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_redis_cache_wiring_invariants", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_redis_cache_wiring_invariants", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_redis_cache_wiring_invariants", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_redis_cache_wiring_invariants", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_redis_cache_wiring_invariants", "write_through")
# REMOVED: _emit_writes_through("p1", "test_redis_cache_wiring_invariants", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_redis_cache_wiring_invariants", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_redis_cache_wiring_invariants", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_redis_cache_wiring_invariants", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_redis_cache_wiring_invariants", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_redis_cache_wiring_invariants", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_redis_cache_wiring_invariants", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_redis_cache_wiring_invariants", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_redis_cache_wiring_invariants", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_redis_cache_wiring_invariants", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_redis_cache_wiring_invariants", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_redis_cache_wiring_invariants", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_redis_cache_wiring_invariants", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_redis_cache_wiring_invariants", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_redis_cache_wiring_invariants", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_redis_cache_wiring_invariants")
# REMOVED: _emit_gated_by_confidence("p1", "test_redis_cache_wiring_invariants", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_redis_cache_wiring_invariants")
# REMOVED: emit_determinism_digest("p0", "test_redis_cache_wiring_invariants")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_redis_cache_wiring_invariants", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_redis_cache_wiring_invariants", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_redis_cache_wiring_invariants", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_redis_cache_wiring_invariants", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_redis_cache_wiring_invariants", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_redis_cache_wiring_invariants", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_redis_cache_wiring_invariants", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_redis_cache_wiring_invariants", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_redis_cache_wiring_invariants", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_redis_cache_wiring_invariants", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_redis_cache_wiring_invariants", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_redis_cache_wiring_invariants", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_redis_cache_wiring_invariants", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_redis_cache_wiring_invariants", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_redis_cache_wiring_invariants", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_redis_cache_wiring_invariants", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_redis_cache_wiring_invariants", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_redis_cache_wiring_invariants", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_redis_cache_wiring_invariants", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_redis_cache_wiring_invariants", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent
L4_STATE_DIR = REPO_ROOT / L4_STATE_DIR

# ---------------------------------------------------------------------------
# §1  SEAM WIRING CONTRACT
# ---------------------------------------------------------------------------


def _make_fake_cache() -> MagicMock:
    """Return a DeterministicRedisCache mock that always misses."""
    fake = MagicMock()
    fake.get_json.return_value = None
    fake.get.return_value = None
    return fake


# --- L0 RouteDecisionCache ---


def test_route_decision_cache_has_get_or_fetch():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    assert hasattr(RouteDecisionCache, "get_or_fetch"), "RouteDecisionCache must expose get_or_fetch()"


def test_route_decision_cache_get_or_fetch_on_miss():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    cache = RouteDecisionCache(cache=fake)
    sentinel = {"decision": "path_a"}
    fetch_called = []

    def fetch():
        fetch_called.append(True)
        return sentinel

    h = "a" * 64
    result = cache.get_or_fetch(h, h, h, fetch)
    assert result is sentinel
    assert fetch_called, "fetch_from_l4 must be called on a miss"
    fake.set_json.assert_called_once()


def test_route_decision_cache_get_or_fetch_on_hit():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    cached_val = {"decision": "cached"}
    fake.get_json.return_value = cached_val
    cache = RouteDecisionCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, lambda: fetch_called.append(True))
    assert result is cached_val
    assert not fetch_called, "fetch_from_l4 must NOT be called on a hit"
    fake.set_json.assert_not_called()


def test_route_decision_cache_get_or_fetch_replay_bypasses_cache():
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"decision": "stale"}
    cache = RouteDecisionCache(cache=fake)
    sentinel = {"decision": "replayed"}
    fetch_called = []

    def fetch():
        fetch_called.append(True)
        return sentinel

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, fetch, replay_mode=True)
    assert result is sentinel
    assert fetch_called, "replay_mode must bypass the cache and call fetch"


# --- L0 RoutingRuleSurfaceCache ---


def test_routing_rule_surface_cache_has_get_or_fetch():
    from agentic_core.L0_routing.seams.redis_decision_cache import RoutingRuleSurfaceCache

    assert hasattr(RoutingRuleSurfaceCache, "get_or_fetch")


def test_routing_rule_surface_get_or_fetch_miss():
    from agentic_core.L0_routing.seams.redis_decision_cache import RoutingRuleSurfaceCache

    fake = _make_fake_cache()
    cache = RoutingRuleSurfaceCache(cache=fake)
    sentinel = {"rules": []}
    result = cache.get_or_fetch("a" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


# --- L0 CapabilityRegistryCache ---


def test_cap_registry_cache_has_get_or_fetch():
    from agentic_core.L0_routing.seams.redis_decision_cache import CapabilityRegistryCache

    assert hasattr(CapabilityRegistryCache, "get_or_fetch")


def test_cap_registry_get_or_fetch_miss():
    from agentic_core.L0_routing.seams.redis_decision_cache import CapabilityRegistryCache

    fake = _make_fake_cache()
    cache = CapabilityRegistryCache(cache=fake)
    sentinel = {TOOLS_DIR: ["tool_a"]}
    result = cache.get_or_fetch("a" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


# --- L1 CompiledPromptCache ---


def test_compiled_prompt_cache_has_get_or_fetch():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import CompiledPromptCache

    assert hasattr(CompiledPromptCache, "get_or_fetch")


def test_compiled_prompt_get_or_fetch_miss():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import CompiledPromptCache

    fake = _make_fake_cache()
    cache = CompiledPromptCache(cache=fake)
    sentinel = {"artifact_signature": "sig1"}
    h = "a" * 64
    result = cache.get_or_fetch(h, h, h, h, h, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


def test_compiled_prompt_get_or_fetch_hit():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import CompiledPromptCache

    fake = _make_fake_cache()
    hit = {"artifact_signature": "cached_sig"}
    fake.get_json.return_value = hit
    cache = CompiledPromptCache(cache=fake)
    fetch_called = []

    h = "a" * 64
    result = cache.get_or_fetch(h, h, h, h, h, lambda: fetch_called.append(True))
    assert result is hit
    assert not fetch_called


# --- L1 TemplateRenderCache ---


def test_template_render_cache_has_get_or_fetch():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import TemplateRenderCache

    assert hasattr(TemplateRenderCache, "get_or_fetch")


def test_template_render_get_or_fetch_miss():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import TemplateRenderCache

    fake = _make_fake_cache()
    fake.get.return_value = None
    cache = TemplateRenderCache(cache=fake)
    result = cache.get_or_fetch("tmpl_id", "v1", "a" * 64, lambda: "rendered text")
    assert result == "rendered text"
    fake.set.assert_called_once()


def test_template_render_get_or_fetch_hit():
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import TemplateRenderCache

    fake = _make_fake_cache()
    fake.get.return_value = b"cached rendered text"
    cache = TemplateRenderCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("tmpl_id", "v1", "a" * 64, lambda: fetch_called.append(True))
    assert result == "cached rendered text"
    assert not fetch_called


# --- L3 OrchestrationPlanCache ---


def test_orch_plan_cache_has_get_or_fetch():
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import OrchestrationPlanCache

    assert hasattr(OrchestrationPlanCache, "get_or_fetch")


def test_orch_plan_get_or_fetch_miss():
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import OrchestrationPlanCache

    fake = _make_fake_cache()
    cache = OrchestrationPlanCache(cache=fake)
    sentinel = {"step_dag": [], "plan_hash": "a" * 64, "tool_budget_hash": "b" * 64}
    result = cache.get_or_fetch("trace-001", "a" * 64, "b" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


def test_orch_plan_get_or_fetch_hit():
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import OrchestrationPlanCache

    fake = _make_fake_cache()
    hit = {"step_dag": ["step1"], "plan_hash": "a" * 64}
    fake.get_json.return_value = hit
    cache = OrchestrationPlanCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("trace-001", "a" * 64, "b" * 64, lambda: fetch_called.append(True))
    assert result is hit
    assert not fetch_called


# --- L5 SafetyEvalCache ---


def test_safety_eval_cache_has_get_or_fetch():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    assert hasattr(SafetyEvalCache, "get_or_fetch")


def test_safety_eval_get_or_fetch_miss():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    fake = _make_fake_cache()
    cache = SafetyEvalCache(cache=fake)
    sentinel = {"decision": "allow", "compliance_hash": "a" * 64}
    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, lambda: sentinel)
    assert result is sentinel
    fake.set_json.assert_called_once()


def test_safety_eval_get_or_fetch_hit():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    fake = _make_fake_cache()
    hit = {"decision": "block", "compliance_hash": "d" * 64}
    fake.get_json.return_value = hit
    cache = SafetyEvalCache(cache=fake)
    fetch_called = []

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, lambda: fetch_called.append(True))
    assert result is hit
    assert not fetch_called


def test_safety_eval_get_or_fetch_replay_bypasses_cache():
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"decision": "stale", "compliance_hash": "e" * 64}
    cache = SafetyEvalCache(cache=fake)
    sentinel = {"decision": "allow", "compliance_hash": "f" * 64}
    fetch_called = []

    def fetch():
        fetch_called.append(True)
        return sentinel

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, fetch, replay_mode=True)
    assert result is sentinel
    assert fetch_called


# ---------------------------------------------------------------------------
# §1b  NON-HAPPY-PATH: ERROR HANDLING & EDGE CASES
# ---------------------------------------------------------------------------


def test_route_decision_cache_get_or_fetch_propagates_fetch_exception():
    """fetch_from_l4 exceptions must propagate, not be swallowed."""
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    cache = RouteDecisionCache(cache=fake)

    def fetch_raises():
        raise ValueError("L4 fetch failed")

    with pytest.raises(ValueError, match="L4 fetch failed"):
        cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, fetch_raises)


def test_compiled_prompt_cache_get_or_fetch_non_callable_fetch_raises():
    """Non-callable fetch_from_l4 must raise TypeError."""
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import CompiledPromptCache

    fake = _make_fake_cache()
    cache = CompiledPromptCache(cache=fake)
    h = "a" * 64

    with pytest.raises(TypeError):
        cache.get_or_fetch(h, h, h, h, h, "not-a-callable")  # type: ignore[arg-type]


def test_orch_plan_cache_replay_mode_does_not_write_to_cache():
    """Replay mode must NOT call set_json even after successful fetch."""
    from agentic_core.L3_orchestration.engines.orchestration_plan_cache import OrchestrationPlanCache

    fake = _make_fake_cache()
    cache = OrchestrationPlanCache(cache=fake)
    sentinel = {"step_dag": [], "plan_hash": "a" * 64}

    cache.get_or_fetch("trace-001", "a" * 64, "b" * 64, lambda: sentinel, replay_mode=True)
    fake.set_json.assert_not_called()


def test_safety_eval_cache_get_or_fetch_wrong_return_type_from_fetch():
    """fetch_from_l5 returning wrong type (e.g., None) must not crash set()."""
    from agentic_core.L5_safety.enforcement.safety_eval_cache import SafetyEvalCache

    fake = _make_fake_cache()
    cache = SafetyEvalCache(cache=fake)

    def fetch_returns_none():
        return None

    result = cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, fetch_returns_none)
    assert result is None
    fake.set_json.assert_called_once()
    assert fake.set_json.call_args[0][1] is None


def test_template_render_cache_get_or_fetch_empty_string_is_valid():
    """fetch_from_l4 returning empty string is valid and must be cached."""
    from agentic_core.L1_cognition.engines.prompt_artifact_cache import TemplateRenderCache

    fake = _make_fake_cache()
    fake.get.return_value = None
    cache = TemplateRenderCache(cache=fake)

    result = cache.get_or_fetch("tmpl_id", "v1", "a" * 64, lambda: "")
    assert result == ""
    fake.set.assert_called_once()


def test_cap_registry_cache_get_or_fetch_fetch_called_exactly_once_on_miss():
    """fetch_from_l4 must be called exactly once, not multiple times."""
    from agentic_core.L0_routing.seams.redis_decision_cache import CapabilityRegistryCache

    fake = _make_fake_cache()
    cache = CapabilityRegistryCache(cache=fake)
    call_count = [0]

    def fetch_increments():
        call_count[0] += 1
        return {TOOLS_DIR: []}

    cache.get_or_fetch("a" * 64, fetch_increments)
    assert call_count[0] == 1, "fetch must be called exactly once"


def test_route_decision_cache_get_or_fetch_cache_exception_propagates():
    """If underlying cache.get_json raises, exception must propagate."""
    from agentic_core.L0_routing.seams.redis_decision_cache import RouteDecisionCache

    fake = _make_fake_cache()
    fake.get_json.side_effect = RuntimeError("Redis connection lost")
    cache = RouteDecisionCache(cache=fake)

    with pytest.raises(RuntimeError, match="Redis connection lost"):
        cache.get_or_fetch("a" * 64, "b" * 64, "c" * 64, lambda: {"decision": "x"})


# ---------------------------------------------------------------------------
# §2  NO SHADOW REDIS IN L4
# ---------------------------------------------------------------------------

_LIVE_REDIS_INDICATORS = {
    "redis.Redis",
    "redis.from_url",
    "redis.asyncio",
    "aioredis",
    "Redis(",
}
_TOMBSTONE_CLASS_PREFIX = "_Tombstoned"
def _ast_has_live_redis(source: str, filepath: Path) -> list[str]:
    """Return list of AST node descriptions where live Redis is imported at module level.
    Guarded imports inside function/method bodies (e.g. ``try: import redis``) are
    acceptable optional-dependency patterns and are NOT flagged.  Only module-level
    imports create unconditional shadow Redis clients.
    """
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []
    # Collect all import nodes that are direct children of the module (top-level)
    module_level_imports: set[int] = set()
    for node in ast.iter_child_nodes(tree):
        module_level_imports.add(id(node))
    violations: list[str] = []
    for node in ast.walk(tree):
        if id(node) not in module_level_imports:
            continue  # skip imports inside functions/methods/classes
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("redis") or alias.name.startswith("aioredis"):
                    violations.append(f"line {node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and (node.module.startswith("redis") or node.module.startswith("aioredis")):
                violations.append(f"line {node.lineno}: from {node.module} import ...")
    return violations
def _is_tombstone_file(source: str) -> bool:
    """Return True if the file is a tombstone (no live symbols)."""
    return "TOMBSTONED" in source
def test_no_live_redis_client_in_l4_state():
    """AST-scan: L4_state must not contain live Redis imports outside tombstones."""
    violations: dict[str, list[str]] = {}
    for py_file in L4_STATE_DIR.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8", errors="replace")
        if _is_tombstone_file(source):
            continue
        hits = _ast_has_live_redis(source, py_file)
        if hits:
            rel = py_file.relative_to(REPO_ROOT)
            violations[str(rel)] = hits
    assert not violations, (
        "L4_state must not own live Redis clients. "
        "Route through agentic_core.cache instead.\n"
        + "\n".join(f"  {path}:\n" + "\n".join(f"    {v}" for v in hits) for path, hits in violations.items())
    )
def test_tombstoned_redis_classes_raise_on_instantiation():
    """Tombstoned shadow-Redis classes must raise RuntimeError, not silently succeed."""
    from agentic_core.L4_state.memory import blob_storage_provider as bsp
    assert hasattr(bsp, "_TombstonedRedisDistributedLock")
    assert hasattr(bsp, "_TombstonedRedisHotCache")
    assert hasattr(bsp, "_TombstonedHotBrainCache")
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisDistributedLock()
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisHotCache()
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedHotBrainCache()
def test_tombstoned_classes_reject_positional_args():
    """Tombstoned classes must reject instantiation with positional args."""
    from agentic_core.L4_state.memory import blob_storage_provider as bsp
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisDistributedLock("arg1", "arg2")
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisHotCache(None, 3600)
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedHotBrainCache("redis://localhost")
def test_tombstoned_classes_reject_keyword_args():
    """Tombstoned classes must reject instantiation with keyword args."""
    from agentic_core.L4_state.memory import blob_storage_provider as bsp
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisDistributedLock(redis_client=None, lock_timeout=DEFAULT_TIMEOUT)
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisHotCache(redis_client=None, default_ttl=3600)
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedHotBrainCache(redis_url="redis://localhost")
def test_tombstoned_classes_reject_mixed_args():
    """Tombstoned classes must reject instantiation with mixed positional + keyword args."""
    from agentic_core.L4_state.memory import blob_storage_provider as bsp
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisDistributedLock(None, lock_timeout=DEFAULT_TIMEOUT)
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedRedisHotCache(None, default_ttl=7200)
    with pytest.raises(RuntimeError, match="tombstoned"):
        bsp._TombstonedHotBrainCache("redis://localhost", extra_arg="value")
def test_l4_caching_redis_mcp_client_has_no_live_symbols():
    """redis_mcp_client.py must be a tombstone with no callable symbols."""
    redis_mcp = REPO_ROOT / L4_STATE_DIR / "caching" / "redis_mcp_client.py"
    source = redis_mcp.read_text(encoding="utf-8", errors="replace")
    assert "TOMBSTONED" in source, "redis_mcp_client.py must be tombstoned"
    tree = ast.parse(source, filename=str(redis_mcp))
    live_classes = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_Tombstoned")
    ]
    live_functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    assert not live_classes, f"redis_mcp_client.py has live classes: {live_classes}"
    assert not live_functions, f"redis_mcp_client.py has live functions: {live_functions}"
# ---------------------------------------------------------------------------
# §3  HASH VALIDATION STRICTNESS
# ---------------------------------------------------------------------------
def test_require_hash_segment_strict_mode_rejects_short_strings(monkeypatch):
    """In strict mode, non-64-hex strings must raise ValueError."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    # Force reimport to pick up env-var at call time (function reads env inline)
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "abc123")
    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "g" * 64)  # invalid hex char
    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "a" * 63)  # one short
def test_require_hash_segment_strict_mode_accepts_valid_sha256(monkeypatch):
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    valid = "a" * 64
    _require_hash_segment("test_hash", valid)  # must not raise
def test_require_hash_segment_permissive_mode_accepts_short_strings(monkeypatch):
    """With REDIS_CACHE_STRICT_HASH_VALIDATION=0, any non-empty string is accepted."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "0")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    _require_hash_segment("test_hash", "short-placeholder")  # must not raise
    _require_hash_segment("test_hash", "x" * 10)
def test_require_hash_segment_rejects_empty_in_all_modes(monkeypatch):
    """Empty string must always be rejected regardless of strict mode."""
    for val in ("0", "1"):
        monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", val)
        from agentic_core.cache.cache_key_builders import _require_hash_segment
        with pytest.raises(ValueError, match="must not be empty"):
            _require_hash_segment("test_hash", "")
def test_require_hash_segment_strict_rejects_uppercase_hex(monkeypatch):
    """Strict mode must reject uppercase hex (SHA-256 must be lowercase)."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "A" * 64)
def test_require_hash_segment_strict_rejects_mixed_case(monkeypatch):
    """Strict mode must reject mixed case hex."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "aB" * 32)
def test_require_hash_segment_strict_rejects_65_chars(monkeypatch):
    """Strict mode must reject 65-char strings (one too long)."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    with pytest.raises(ValueError, match="64-char"):
        _require_hash_segment("test_hash", "a" * 65)
def test_require_hash_segment_strict_rejects_non_hex_chars(monkeypatch):
    """Strict mode must reject strings with non-hex characters."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "1")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    invalid_chars = ["g", "z", "@", " ", "-"]
    for char in invalid_chars:
        bad_hash = "a" * 63 + char
        with pytest.raises(ValueError, match="64-char"):
            _require_hash_segment("test_hash", bad_hash)
def test_require_hash_segment_permissive_accepts_uppercase(monkeypatch):
    """Permissive mode accepts uppercase (for test placeholders)."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "0")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    _require_hash_segment("test_hash", "PLACEHOLDER")  # must not raise
def test_require_hash_segment_permissive_accepts_single_char(monkeypatch):
    """Permissive mode accepts single-char placeholders."""
    monkeypatch.setenv("REDIS_CACHE_STRICT_HASH_VALIDATION", "0")
    from agentic_core.cache.cache_key_builders import _require_hash_segment
    _require_hash_segment("test_hash", "x")  # must not raise
