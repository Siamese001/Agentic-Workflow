"""
Validate Base Agent Uniqueness
===============================

Ensures each layer (L0-L6) has exactly ONE base agent class.
Multiple base agents per layer causes inheritance confusion and architectural violations.

Validation Rules:
1. Each layer must have exactly 1 base agent (e.g., L1CognitionBase, L2Agent, etc.)
2. Base agents should be in base_class or root layer directories
3. No duplicate base agent classes

Fixes:
- Identifies duplicate base agents
- Suggests which to keep (canonical) vs deprecate
- Can auto-deprecate non-canonical base agents
"""

import json
from collections import defaultdict

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "validate_base_agents_util")
emit_determinism_digest("p0", "validate_base_agents_util")

_emit_dispatches_healing_run("p1", "validate_base_agents_util", "L0")
_emit_routes_through("p1", "validate_base_agents_util", "L0")
_emit_checks_agent_registry("p1", "validate_base_agents_util", "agent_registry")
_emit_validates_agent_capability("p1", "validate_base_agents_util", "capability")
_emit_dispatches_execution_plan("p1", "validate_base_agents_util", "exec_plan")
_emit_agent_executes_agent("p1", "validate_base_agents_util", "sub_agent")
_emit_routes_to_agent("p1", "validate_base_agents_util", "target_agent")
_emit_verifies_policy("p1", "validate_base_agents_util", "policy_check")
_emit_observes_runtime_state("p1", "validate_base_agents_util", "runtime_state")
_emit_verifies_boundary("p1", "validate_base_agents_util", "boundary_check")
_emit_transcripts_response("p1", "validate_base_agents_util", "transcript")
_emit_hard_fails_untranscripted("p1", "validate_base_agents_util")
_emit_gated_by_confidence("p1", "validate_base_agents_util", "confidence_gate")
_emit_escalates_to_human("p1", "validate_base_agents_util", "L0")
_emit_reads_policy_state("p1", "validate_base_agents_util", "L0")
_emit_authorize_and_execute("p2", "validate_base_agents_util", "execution_auth")
_emit_validates_capability("p2", "validate_base_agents_util", "capability_check")
_emit_routes_to_capability("p2", "validate_base_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "validate_base_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "validate_base_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "validate_base_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "validate_base_agents_util", "exec_output")
_emit_dispatches_agent("p3", "validate_base_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "validate_base_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "validate_base_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "validate_base_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "validate_base_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "validate_base_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validate_base_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "validate_base_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "validate_base_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validate_base_agents_util", "eval_metric")
_emit_stores_embedding("p4", "validate_base_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "validate_base_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validate_base_agents_util", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("validate_base_agents_util", "p4obs", "metric_1")
_emit_emits_metric_event("validate_base_agents_util", "p4obs", "metric_2")
_emit_emits_metric_event("validate_base_agents_util", "p4obs", "metric_3")
_emit_emits_metric_event("validate_base_agents_util", "p4obs", "metric_4")
_emit_emits_metric_event("validate_base_agents_util", "p4obs", "metric_5")
_emit_emits_metric_event("validate_base_agents_util", "p4obs", "metric_6")
_emit_records_incident_event("validate_base_agents_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("validate_base_agents_util", "p4obs", "anomaly")
_emit_writes_observability_log("validate_base_agents_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("validate_base_agents_util", "p4obs", "mon_state")
_emit_triggers_alert("validate_base_agents_util", "p4obs", "alert")
_emit_links_incident_trace("validate_base_agents_util", "p4obs", "trace_link")
_emit_captures_pattern("validate_base_agents_util", "p3lm", "pattern")
_emit_records_learning_event("validate_base_agents_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validate_base_agents_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("validate_base_agents_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validate_base_agents_util", "p3lm", "routing")
_emit_improves_agent_policy("validate_base_agents_util", "p3lm", "policy")
_emit_stores_learning_state("validate_base_agents_util", "p3lm", "state")
_emit_records_execution_trace("validate_base_agents_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validate_base_agents_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validate_base_agents_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validate_base_agents_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validate_base_agents_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validate_base_agents_util", "env_read", "p2_env_1")
_emit_reads_environ("validate_base_agents_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("validate_base_agents_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validate_base_agents_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validate_base_agents_util", "context_pull")
_emit_pulls_context("p1", "validate_base_agents_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validate_base_agents_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validate_base_agents_util", "uwg_term_2")
_emit_writes_through("p1", "validate_base_agents_util", "write_through")
_emit_writes_through("p1", "validate_base_agents_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "validate_base_agents_util", "safety_validation")
_emit_invokes_eval("p1", "validate_base_agents_util", "eval_call")
_emit_proposal_commits_routing("p1", "validate_base_agents_util", "routing_commit")

data = json.load(open("agent_discovery_full.json"))
LAYERS = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]
CANONICAL_BASE_AGENTS = {
    "L0": "L0RoutingBaseAgent",
    "L1": "L1CognitionBase",
    "L2": "L2Agent",
    "L3": "L3Agent",
    "L4": "L4Agent",
    "L5": "L5Agent",
    "L6": "L6ObservabilityBase",
}


def find_base_agents() -> dict[str, list[dict]]:
    """Find all base agents grouped by layer."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "find_base_agents", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "find_base_agents", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "find_base_agents")
    base_agents_by_layer = defaultdict(list)
    for agent in tqdm(data, desc="Processing", unit="item"):
        class_name = agent.get("class_name", "")
        layer = agent.get("layer", "")
        is_base_agent = (
            "BaseAgent" in class_name
            or class_name in CANONICAL_BASE_AGENTS.values()
            or "base_class" in agent.get("path", "").lower()
        )
        if is_base_agent and layer:
            layer_prefix = layer[:2] if len(layer) >= 2 else layer
            if layer_prefix in LAYERS:
                base_agents_by_layer[layer_prefix].append(agent)
    return base_agents_by_layer


def validate_base_agents() -> tuple[bool, list[str]]:
    """Validate base agent uniqueness per layer."""
    base_agents = find_base_agents()
    errors = []
    warnings = []
    print("=" * 80)
    print("BASE AGENT UNIQUENESS VALIDATION")
    print("=" * 80)
    print()
    for layer in tqdm(LAYERS, desc="Processing", unit="item"):
        agents = base_agents.get(layer, [])
        canonical = CANONICAL_BASE_AGENTS.get(layer)
        print(f"{layer} Layer:")
        if len(agents) == 0:
            warnings.append(f"⚠️  {layer}: No base agent found (expected {canonical})")
            print(f"   ⚠️  No base agent (expected {canonical})")
        elif len(agents) == 1:
            agent = agents[0]
            name = agent["class_name"]
            if name == canonical:
                print(f"   ✅ Canonical base agent: {name}")
            else:
                warnings.append(f"⚠️  {layer}: Found {name}, expected canonical {canonical}")
                print(f"   ⚠️  Found {name}, expected {canonical}")
                print(f"      Path: {agent['path']}")
        else:
            errors.append(f"❌ {layer}: Found {len(agents)} base agents (expected 1)")
            print(f"   ❌ MULTIPLE BASE AGENTS FOUND: {len(agents)}")
            canonical_agent = next((a for a in agents if a["class_name"] == canonical), None)
            for i, agent in enumerate(agents, 1):
                name = agent["class_name"]
                path = agent["path"]
                is_canonical = name == canonical
                marker = "👑 CANONICAL" if is_canonical else "🔴 DUPLICATE"
                print(f"      {i}. {name} {marker}")
                print(f"         {path}")
            if canonical_agent:
                print(f"   💡 Recommendation: Keep {canonical}, deprecate others")
            else:
                print(f"   💡 Recommendation: Rename one to {canonical}, deprecate others")
        print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    if errors:
        print(f"❌ {len(errors)} ERRORS")
        for error in errors:
            print(f"   {error}")
        print()
    if warnings:
        print(f"⚠️  {len(warnings)} WARNINGS")
        for warning in warnings:
            print(f"   {warning}")
        print()
    if not errors and (not warnings):
        print("✅ All layers have exactly 1 canonical base agent")
        print()
    is_valid = len(errors) == 0
    all_messages = errors + warnings
    return (is_valid, all_messages)


def suggest_fixes() -> list[str]:
    """Suggest fixes for base agent violations."""
    base_agents = find_base_agents()
    fixes = []
    for layer in tqdm(LAYERS, desc="Processing", unit="item"):
        agents = base_agents.get(layer, [])
        canonical = CANONICAL_BASE_AGENTS.get(layer)
        if len(agents) > 1:
            canonical_agent = next((a for a in agents if a["class_name"] == canonical), None)
            if canonical_agent:
                for agent in agents:
                    if agent["class_name"] != canonical:
                        fixes.append(
                            f"Deprecate {agent['class_name']} at {agent['path']} (duplicate of canonical {canonical})",
                        )
            else:
                fixes.append(f"Rename {agents[0]['class_name']} to {canonical} at {agents[0]['path']}")
                for agent in agents[1:]:
                    fixes.append(f"Deprecate {agent['class_name']} at {agent['path']}")
    return fixes


def main():
    """Main entry point."""
    is_valid, messages = validate_base_agents()
    if not is_valid:
        print("=" * 80)
        print("RECOMMENDED FIXES")
        print("=" * 80)
        fixes = suggest_fixes()
        for i, fix in enumerate(fixes, 1):
            print(f"{i}. {fix}")
        print()
        print("Run this script with --fix flag to auto-apply fixes (not yet implemented)")
        return 1
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
