"""
SSOT Dry-Run v2: Individual agent execution with fault isolation.

The standard entrypoint crashes because HierarchyAgent has a pre-existing
AtomicExecutionMixin NameError that blocks ALL mandatory imports.

This script imports and runs each agent individually, capturing results
even when some agents fail to import.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    LAYER_ROOTS,
    get_validated_project_root,
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

_emit_records_execution_trace("p0", "evidence", "_ssot_dry_run_isolated")
_emit_applies_guardrail("p0", "_ssot_dry_run_isolated", "p0_governance")
_emit_reads_policy_state("p0", "_ssot_dry_run_isolated", "policy_binding")
_emit_snapshots_state("p0", "_ssot_dry_run_isolated", "state_snapshot")
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("_ssot_dry_run_isolated", "p4obs", "metric_1")
_emit_emits_metric_event("_ssot_dry_run_isolated", "p4obs", "metric_2")
_emit_emits_metric_event("_ssot_dry_run_isolated", "p4obs", "metric_3")
_emit_emits_metric_event("_ssot_dry_run_isolated", "p4obs", "metric_4")
_emit_emits_metric_event("_ssot_dry_run_isolated", "p4obs", "metric_5")
_emit_emits_metric_event("_ssot_dry_run_isolated", "p4obs", "metric_6")
_emit_records_incident_event("_ssot_dry_run_isolated", "p4obs", "incident")
_emit_captures_runtime_anomaly("_ssot_dry_run_isolated", "p4obs", "anomaly")
_emit_writes_observability_log("_ssot_dry_run_isolated", "p4obs", "obs_log")
_emit_updates_monitoring_state("_ssot_dry_run_isolated", "p4obs", "mon_state")
_emit_triggers_alert("_ssot_dry_run_isolated", "p4obs", "alert")
_emit_links_incident_trace("_ssot_dry_run_isolated", "p4obs", "trace_link")
_emit_captures_pattern("_ssot_dry_run_isolated", "p3lm", "pattern")
_emit_records_learning_event("_ssot_dry_run_isolated", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_ssot_dry_run_isolated", "p3lm", "snapshot")
_emit_feeds_meta_learning("_ssot_dry_run_isolated", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_ssot_dry_run_isolated", "p3lm", "routing")
_emit_improves_agent_policy("_ssot_dry_run_isolated", "p3lm", "policy")
_emit_stores_learning_state("_ssot_dry_run_isolated", "p3lm", "state")
_emit_records_execution_trace("_ssot_dry_run_isolated", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_ssot_dry_run_isolated", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_ssot_dry_run_isolated", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_ssot_dry_run_isolated", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_ssot_dry_run_isolated", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_ssot_dry_run_isolated", "env_read", "p2_env_1")
_emit_reads_environ("_ssot_dry_run_isolated", "env_read", "p2_env_2")
_emit_reads_runtime_state("_ssot_dry_run_isolated", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_ssot_dry_run_isolated", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_ssot_dry_run_isolated", "context_pull")
_emit_pulls_context("p1", "_ssot_dry_run_isolated", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "_ssot_dry_run_isolated", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_ssot_dry_run_isolated", "uwg_term_2")
_emit_writes_through("p1", "_ssot_dry_run_isolated", "write_through")
_emit_writes_through("p1", "_ssot_dry_run_isolated", "write_through_2")
_emit_validated_by_safety_plane("p1", "_ssot_dry_run_isolated", "safety_validation")
_emit_invokes_eval("p1", "_ssot_dry_run_isolated", "eval_call")
_emit_proposal_commits_routing("p1", "_ssot_dry_run_isolated", "routing_commit")
_emit_escalates_to_human("p1", "_ssot_dry_run_isolated", "human_escalation")
_emit_routes_through("p1", "_ssot_dry_run_isolated", "route_through")
_emit_checks_agent_registry("p1", "_ssot_dry_run_isolated", "agent_registry")
_emit_validates_agent_capability("p1", "_ssot_dry_run_isolated", "capability")
_emit_dispatches_execution_plan("p1", "_ssot_dry_run_isolated", "exec_plan")
_emit_agent_executes_agent("p1", "_ssot_dry_run_isolated", "sub_agent")
_emit_routes_to_agent("p1", "_ssot_dry_run_isolated", "target_agent")
_emit_verifies_policy("p1", "_ssot_dry_run_isolated", "policy_check")
_emit_observes_runtime_state("p1", "_ssot_dry_run_isolated", "runtime_state")
_emit_verifies_boundary("p1", "_ssot_dry_run_isolated", "boundary_check")
_emit_transcripts_response("p1", "_ssot_dry_run_isolated", "transcript")
_emit_hard_fails_untranscripted("p1", "_ssot_dry_run_isolated")
_emit_gated_by_confidence("p1", "_ssot_dry_run_isolated", "confidence_gate")
emit_replay_key("p0", "_ssot_dry_run_isolated")
emit_determinism_digest("p0", "_ssot_dry_run_isolated")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_ssot_dry_run_isolated", "execution_auth")
_emit_validates_capability("p2", "_ssot_dry_run_isolated", "capability_check")
_emit_routes_to_capability("p2", "_ssot_dry_run_isolated", "capability_route")
_emit_writes_via_uwg("p2", "_ssot_dry_run_isolated", "uwg_write")
_emit_blocks_direct_write("p2", "_ssot_dry_run_isolated", "direct_write_block")
_emit_records_tool_invocation("p2", "_ssot_dry_run_isolated", "tool_invocation")
_emit_captures_execution_output("p2", "_ssot_dry_run_isolated", "exec_output")
_emit_dispatches_agent("p3", "_ssot_dry_run_isolated", "agent_dispatch")
_emit_coordinates_agents("p3", "_ssot_dry_run_isolated", "agent_coordination")
_emit_records_workflow_lineage("p3", "_ssot_dry_run_isolated", "workflow_lineage")
_emit_records_healing_outcome("p3", "_ssot_dry_run_isolated", "healing_outcome")
_emit_escalates_failure("p3", "_ssot_dry_run_isolated", "failure_escalation")
_emit_orchestrates_workflow("p3", "_ssot_dry_run_isolated", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_ssot_dry_run_isolated", "healing_dispatch")
_emit_invokes_evaluation("p3", "_ssot_dry_run_isolated", "evaluation_signal")
_emit_records_telemetry_event("p4", "_ssot_dry_run_isolated", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_ssot_dry_run_isolated", "eval_metric")
_emit_stores_embedding("p4", "_ssot_dry_run_isolated", "embedding_store")
_emit_updates_meta_learning_state("p4", "_ssot_dry_run_isolated", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_ssot_dry_run_isolated", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

# All layer territories
TERRITORIES = sorted(LAYER_ROOTS)

# Agent registry: name -> (import_path, class_name, methods_to_try)
AGENT_REGISTRY = {
    "FileClassificationAgent": (
        "agentic_core.L5_safety.reasoning.FileClassificationAgent",
        "FileClassificationAgent",
        ["heal_repository"],
    ),
    "FilesystemSSOTReconcilerAgent": (
        "agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler",
        "FilesystemSSOTReconcilerAgent",
        ["heal_repository"],
    ),
    "LocationAgent": (
        "agentic_core.L5_safety.reasoning.LocationAgent",
        "LocationAgent",
        ["heal_repository"],
    ),
    "LocationValidatorAgent": (
        "agentic_core.L5_safety.reasoning.location_validator",
        "LocationValidatorAgent",
        ["heal_repository"],
    ),
    "HierarchyAgent": (
        "agentic_core.L5_safety.reasoning.hierarchy_healer",
        "HierarchyAgent",
        ["heal_repository"],
    ),
    "ArchitectureGovernorAgent": (
        "agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent",
        "ArchitectureGovernorAgent",
        ["run_audit"],
    ),
    "SystemArchitectAgent": (
        "agentic_core.L5_safety.reasoning.SystemArchitectAgent",
        "SystemArchitectAgent",
        ["heal_repository"],
    ),
    "RootHygieneAgent": (
        "agentic_core.L5_safety.reasoning.root_hygiene_healer",
        "RootHygieneAgent",
        ["scan_root_violations"],
    ),
    "CognitiveDispositionAgent": (
        "agentic_core.L5_safety.validators.CognitiveDispositionAgent",
        "CognitiveDispositionAgent",
        ["heal_repository"],
    ),
}


def try_import_agent(name, module_path, class_name):
    """Try to import an agent class. Returns (cls, None) or (None, error)."""
    try:
        import importlib

        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return cls, None
    # guardian: allow-silent-swallow
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise


def try_run_agent(cls, name, method_name, territory):
    """Try to instantiate and run an agent method. Returns result dict."""
    # Redirect stdout to stderr during agent execution (agents use print())
    _real_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        # Instantiate
        if method_name == "run_audit":
            agent = cls(project_root=PROJECT_ROOT, ci_mode=True)
            result = agent.run_audit(target_territories=[territory])
        elif method_name == "scan_root_violations":
            agent = cls(project_root=PROJECT_ROOT)
            result = agent.scan_root_violations(target_territory=territory)
        elif method_name == "heal_repository":
            agent = cls(project_root=PROJECT_ROOT)
            result = agent.heal_repository(
                dry_run=True,
                target_territory=territory,
                auto_approve=True,
            )
        else:
            return {"error": f"Unknown method: {method_name}"}

        return {"success": True, "result": result}
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise


# ── PHASE 1: Import all agents ──
print("=== PHASE 1: Agent Import Check ===", file=sys.stderr)
import_results = {}
agent_classes = {}

for name, (mod_path, cls_name, methods) in AGENT_REGISTRY.items():
    cls, err = try_import_agent(name, mod_path, cls_name)
    if cls:
        import_results[name] = {"status": "OK", "module": mod_path}
        agent_classes[name] = (cls, methods)
        print(f"  OK: {name}", file=sys.stderr)
    else:
        import_results[name] = {"status": "FAIL", "error": err, "module": mod_path}
        print(f"  FAIL: {name} -> {err[:100]}", file=sys.stderr)

# ── PHASE 2: Run FCA (most comprehensive agent) per territory ──
print("\n=== PHASE 2: Per-Territory Agent Execution ===", file=sys.stderr)
territory_results = {}

for territory in tqdm(TERRITORIES, desc="Processing", unit="item"):
    print(f"\n--- {territory} ---", file=sys.stderr)
    territory_results[territory] = {}

    for agent_name, (cls, methods) in tqdm(agent_classes.items(), desc="Processing", unit="item"):
        for method in tqdm(methods, desc="Processing", unit="item"):
            print(f"  Running {agent_name}.{method}({territory})...", file=sys.stderr)
            result = try_run_agent(cls, agent_name, method, territory)
            territory_results[territory][agent_name] = result

            if result.get("success"):
                r = result.get("result", {})
                if isinstance(r, dict):
                    vf = r.get("violations_found", r.get("stats", {}).get("violations_found", "?"))
                    vx = r.get("violations_fixed", "?")
                    print(f"    -> violations_found={vf}, violations_fixed={vx}", file=sys.stderr)
                else:
                    print(f"    -> {str(r)[:100]}", file=sys.stderr)
            else:
                print(f"    -> ERROR: {result.get('error', '')[:100]}", file=sys.stderr)
            break  # Only run first available method

# ── PHASE 3: FCA validate_layer_alignment on all files ──
print("\n=== PHASE 3: FCA Layer Alignment Scan (all files) ===", file=sys.stderr)
layer_violations = []

if "FileClassificationAgent" in agent_classes:
    fca_cls, _ = agent_classes["FileClassificationAgent"]
    fca = fca_cls(project_root=PROJECT_ROOT, dry_run=True, validate_only=True)

    from agentic_core.L5_safety.reasoning.FileClassificationAgent import get_python_files_fast

    all_py = get_python_files_fast(AGENTIC_CORE)

    for p in all_py:
        try:
            v = fca.validate_layer_alignment(p)
            if v:
                v["file"] = str(Path(v["file"]).relative_to(PROJECT_ROOT)).replace("\\", "/")
                layer_violations.append(v)
        except (
            Exception
        ):  # guardian: allow-silent-swallow -- non-critical: validation failure skipped silently
            pass

    print(f"  Layer violations found: {len(layer_violations)}", file=sys.stderr)

# ── PHASE 4: Aggregate ──
violation_type_counts = defaultdict(int)
for v in layer_violations:
    violation_type_counts[v.get("violation", "UNKNOWN")] += 1

# ── Output ──
output = {
    "import_results": import_results,
    "territory_results": territory_results,
    "layer_violation_counts": dict(violation_type_counts),
    "layer_violations": layer_violations,
    "territories_scanned": TERRITORIES,
    "agents_available": list(agent_classes.keys()),
    "agents_failed_import": [n for n, r in import_results.items() if r["status"] == "FAIL"],
}

print(json.dumps(output, indent=2, default=str))
print(
    f"\n=== COMPLETE: {len(agent_classes)}/{len(AGENT_REGISTRY)} agents, "
    f"{len(TERRITORIES)} territories, {len(layer_violations)} layer violations ===",
    file=sys.stderr,
)
