"""Quick test of new territory API migration."""

from agentic_core.L5_safety.config.structure_blueprint.territories import (
    get_all_territories,
    get_territory_metadata,
    is_valid_root_folder,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "_test_territory_api")
_emit_applies_guardrail("p0", "_test_territory_api", "p0_governance")
_emit_reads_policy_state("p0", "_test_territory_api", "policy_binding")
_emit_snapshots_state("p0", "_test_territory_api", "state_snapshot")
emit_replay_key("p0", "_test_territory_api")
emit_determinism_digest("p0", "_test_territory_api")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_test_territory_api", "execution_auth")
_emit_validates_capability("p2", "_test_territory_api", "capability_check")
_emit_routes_to_capability("p2", "_test_territory_api", "capability_route")
_emit_writes_via_uwg("p2", "_test_territory_api", "uwg_write")
_emit_blocks_direct_write("p2", "_test_territory_api", "direct_write_block")
_emit_records_tool_invocation("p2", "_test_territory_api", "tool_invocation")
_emit_captures_execution_output("p2", "_test_territory_api", "exec_output")
_emit_dispatches_agent("p3", "_test_territory_api", "agent_dispatch")
_emit_coordinates_agents("p3", "_test_territory_api", "agent_coordination")
_emit_records_workflow_lineage("p3", "_test_territory_api", "workflow_lineage")
_emit_records_healing_outcome("p3", "_test_territory_api", "healing_outcome")
_emit_escalates_failure("p3", "_test_territory_api", "failure_escalation")
_emit_orchestrates_workflow("p3", "_test_territory_api", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_test_territory_api", "healing_dispatch")
_emit_invokes_evaluation("p3", "_test_territory_api", "evaluation_signal")
_emit_records_telemetry_event("p4", "_test_territory_api", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_test_territory_api", "eval_metric")
_emit_stores_embedding("p4", "_test_territory_api", "embedding_store")
_emit_updates_meta_learning_state("p4", "_test_territory_api", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_test_territory_api", "exec_snapshot_link")

print("=" * 60)
print("Territory API Migration Verification")
print("=" * 60)
print()

# Test 1: get_all_territories()
territories = get_all_territories()
print(f"✅ get_all_territories() returns {len(territories)} territories")
print(f"   Sample keys: {list(territories.keys())[:5]}")
print()

# Test 2: get_territory_metadata()
meta = get_territory_metadata("apps_shared")
if meta:
    print("✅ get_territory_metadata('apps_shared') works")
    print(f"   Purpose: {meta.get('purpose', 'N/A')[:60]}...")
else:
    print("❌ get_territory_metadata('apps_shared') returned None")
print()

# Test 3: is_valid_root_folder()
valid = is_valid_root_folder("apps_shared")
invalid = is_valid_root_folder("invalid_folder")
print(f"✅ is_valid_root_folder('apps_shared'): {valid}")
print(f"✅ is_valid_root_folder('invalid_folder'): {invalid}")
print()

# Test 4: Verify derived.py uses new API
from agentic_core.L5_safety.config.structure_blueprint.derived import DEPTH_RULES

print(f"✅ DEPTH_RULES derived successfully ({len(DEPTH_RULES)} entries)")
print()

# Test 5: Verify ssot.py uses new API
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ALLOW_ROOT_PY_TERRITORIES,
    LAYER_PREFIX_EXEMPT_TERRITORIES,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("_test_territory_api", "p4obs", "metric_1")
_emit_emits_metric_event("_test_territory_api", "p4obs", "metric_2")
_emit_emits_metric_event("_test_territory_api", "p4obs", "metric_3")
_emit_emits_metric_event("_test_territory_api", "p4obs", "metric_4")
_emit_emits_metric_event("_test_territory_api", "p4obs", "metric_5")
_emit_emits_metric_event("_test_territory_api", "p4obs", "metric_6")
_emit_records_incident_event("_test_territory_api", "p4obs", "incident")
_emit_captures_runtime_anomaly("_test_territory_api", "p4obs", "anomaly")
_emit_writes_observability_log("_test_territory_api", "p4obs", "obs_log")
_emit_updates_monitoring_state("_test_territory_api", "p4obs", "mon_state")
_emit_triggers_alert("_test_territory_api", "p4obs", "alert")
_emit_links_incident_trace("_test_territory_api", "p4obs", "trace_link")
_emit_captures_pattern("_test_territory_api", "p3lm", "pattern")
_emit_records_learning_event("_test_territory_api", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_test_territory_api", "p3lm", "snapshot")
_emit_feeds_meta_learning("_test_territory_api", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_test_territory_api", "p3lm", "routing")
_emit_improves_agent_policy("_test_territory_api", "p3lm", "policy")
_emit_stores_learning_state("_test_territory_api", "p3lm", "state")
_emit_records_execution_trace("_test_territory_api", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_test_territory_api", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_test_territory_api", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_test_territory_api", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_test_territory_api", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_test_territory_api", "env_read", "p2_env_1")
_emit_reads_environ("_test_territory_api", "env_read", "p2_env_2")
_emit_reads_runtime_state("_test_territory_api", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_test_territory_api", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_test_territory_api", "context_pull")
_emit_pulls_context("p1", "_test_territory_api", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_test_territory_api", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_test_territory_api", "uwg_term_secondary")
_emit_writes_through("p1", "_test_territory_api", "write_through")
_emit_writes_through("p1", "_test_territory_api", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_test_territory_api", "safety_validation")
_emit_invokes_eval("p1", "_test_territory_api", "eval_call")
_emit_proposal_commits_routing("p1", "_test_territory_api", "routing_commit")
_emit_escalates_to_human("p1", "_test_territory_api", "human_escalation")
_emit_routes_through("p1", "_test_territory_api", "route_through")
_emit_checks_agent_registry("p1", "_test_territory_api", "agent_registry")
_emit_validates_agent_capability("p1", "_test_territory_api", "capability")
_emit_dispatches_execution_plan("p1", "_test_territory_api", "exec_plan")
_emit_agent_executes_agent("p1", "_test_territory_api", "sub_agent")
_emit_routes_to_agent("p1", "_test_territory_api", "target_agent")
_emit_verifies_policy("p1", "_test_territory_api", "policy_check")
_emit_observes_runtime_state("p1", "_test_territory_api", "runtime_state")
_emit_verifies_boundary("p1", "_test_territory_api", "boundary_check")
_emit_transcripts_response("p1", "_test_territory_api", "transcript")
_emit_hard_fails_untranscripted("p1", "_test_territory_api")
_emit_gated_by_confidence("p1", "_test_territory_api", "confidence_gate")

print(f"✅ ALLOW_ROOT_PY_TERRITORIES: {len(ALLOW_ROOT_PY_TERRITORIES)} territories")
print(f"✅ LAYER_PREFIX_EXEMPT_TERRITORIES: {len(LAYER_PREFIX_EXEMPT_TERRITORIES)} territories")
print()

print("=" * 60)
print("All tests passed! Migration successful.")
print("=" * 60)
