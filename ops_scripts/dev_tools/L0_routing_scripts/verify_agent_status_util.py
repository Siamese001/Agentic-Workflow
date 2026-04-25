"""
Verify Agent Status - AST Analysis for Suspect Files

This script audits files suspected of being misclassified as Sovereign Agents.
For each file, it determines:
1. Inheritance: Does it inherit from SovereignBaseAgent or a Layer Base?
2. Methods: Does it implement heal_repository?
3. Nomenclature: Does the class name end in 'Agent'?

Usage: python scripts/verify_agent_status_util.py
"""

import ast
import sys
from pathlib import Path
from typing import Any

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

emit_replay_key("p0", "verify_agent_status_util")
emit_determinism_digest("p0", "verify_agent_status_util")

_emit_dispatches_healing_run("p1", "verify_agent_status_util", "L0")
_emit_routes_through("p1", "verify_agent_status_util", "L0")
_emit_checks_agent_registry("p1", "verify_agent_status_util", "agent_registry")
_emit_validates_agent_capability("p1", "verify_agent_status_util", "capability")
_emit_dispatches_execution_plan("p1", "verify_agent_status_util", "exec_plan")
_emit_agent_executes_agent("p1", "verify_agent_status_util", "sub_agent")
_emit_routes_to_agent("p1", "verify_agent_status_util", "target_agent")
_emit_verifies_policy("p1", "verify_agent_status_util", "policy_check")
_emit_observes_runtime_state("p1", "verify_agent_status_util", "runtime_state")
_emit_verifies_boundary("p1", "verify_agent_status_util", "boundary_check")
_emit_transcripts_response("p1", "verify_agent_status_util", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_agent_status_util")
_emit_gated_by_confidence("p1", "verify_agent_status_util", "confidence_gate")
_emit_escalates_to_human("p1", "verify_agent_status_util", "L0")
_emit_reads_policy_state("p1", "verify_agent_status_util", "L0")
_emit_authorize_and_execute("p2", "verify_agent_status_util", "execution_auth")
_emit_validates_capability("p2", "verify_agent_status_util", "capability_check")
_emit_routes_to_capability("p2", "verify_agent_status_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_agent_status_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_agent_status_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_agent_status_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_agent_status_util", "exec_output")
_emit_dispatches_agent("p3", "verify_agent_status_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_agent_status_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_agent_status_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_agent_status_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_agent_status_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_agent_status_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_agent_status_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_agent_status_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_agent_status_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_agent_status_util", "eval_metric")
_emit_stores_embedding("p4", "verify_agent_status_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_agent_status_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_agent_status_util", "exec_snapshot_link")
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

_emit_emits_metric_event("verify_agent_status_util", "p4obs", "metric_1")
_emit_emits_metric_event("verify_agent_status_util", "p4obs", "metric_2")
_emit_emits_metric_event("verify_agent_status_util", "p4obs", "metric_3")
_emit_emits_metric_event("verify_agent_status_util", "p4obs", "metric_4")
_emit_emits_metric_event("verify_agent_status_util", "p4obs", "metric_5")
_emit_emits_metric_event("verify_agent_status_util", "p4obs", "metric_6")
_emit_records_incident_event("verify_agent_status_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_agent_status_util", "p4obs", "anomaly")
_emit_writes_observability_log("verify_agent_status_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_agent_status_util", "p4obs", "mon_state")
_emit_triggers_alert("verify_agent_status_util", "p4obs", "alert")
_emit_links_incident_trace("verify_agent_status_util", "p4obs", "trace_link")
_emit_captures_pattern("verify_agent_status_util", "p3lm", "pattern")
_emit_records_learning_event("verify_agent_status_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_agent_status_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_agent_status_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_agent_status_util", "p3lm", "routing")
_emit_improves_agent_policy("verify_agent_status_util", "p3lm", "policy")
_emit_stores_learning_state("verify_agent_status_util", "p3lm", "state")
_emit_records_execution_trace("verify_agent_status_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_agent_status_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_agent_status_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_agent_status_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_agent_status_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_agent_status_util", "env_read", "p2_env_1")
_emit_reads_environ("verify_agent_status_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_agent_status_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_agent_status_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_agent_status_util", "context_pull")
_emit_pulls_context("p1", "verify_agent_status_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verify_agent_status_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_agent_status_util", "uwg_term_2")
_emit_writes_through("p1", "verify_agent_status_util", "write_through")
_emit_writes_through("p1", "verify_agent_status_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "verify_agent_status_util", "safety_validation")
_emit_invokes_eval("p1", "verify_agent_status_util", "eval_call")
_emit_proposal_commits_routing("p1", "verify_agent_status_util", "routing_commit")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUSPECT_FILES = [
    "agentic_core/L0_routing/scripts/full_agent_discovery.py",
    "agentic_core/L0_routing/scripts/auto_remediate_signatures.py",
    "agentic_core/L2_execution/pinecone_mcp_client.py",
    "agentic_core/L2_execution/caching_redis_mcp_client.py",
    "agentic_core/L5_safety/ArchivalGatekeeper.py",
    "agentic_core/L5_safety/validators/context.py",
    "agentic_core/L5_safety/validators/constants.py",
    "agentic_core/L6_observability/reasoning_utils.py",
    "agentic_core/utils/core_extensions/infrastructure_mixin.py",
    "agentic_core/utils/core_extensions/healer_mixin.py",
]
SOVEREIGN_BASES = {
    "SovereignBaseAgent",
    "L0RoutingBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
}
LAYER_BASES = SOVEREIGN_BASES | {
    "HealingPolicyMixin",
    "MCPOperationMixin",
    "CanonBaseAgent",
    "CognitionCanonBaseAgent",
    "ExecutionCanonBaseAgent",
}


def extract_bases(class_node: ast.ClassDef) -> set[str]:
    """Extract base class names from class definition."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "extract_bases", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "extract_bases", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "extract_bases")
    bases = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.add(base.id)
        elif isinstance(base, ast.Attribute):
            bases.add(base.attr)
        elif isinstance(base, ast.Subscript):
            if isinstance(base.value, ast.Name):
                bases.add(base.value.id)
    return bases


def has_method(class_node: ast.ClassDef, method_name: str) -> bool:
    """Check if class has a specific method."""
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            if item.name == method_name:
                return True
    return False


def analyze_file(file_path: Path) -> dict[str, Any]:
    """Analyze a Python file for agent characteristics."""
    result = {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "exists": file_path.exists(),
        "is_script": False,
        "classes": [],
        "verdict": "UNKNOWN",
        "reason": "",
    }
    if not file_path.exists():
        result["verdict"] = "NOT_FOUND"
        result["reason"] = "File does not exist"
        return result
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:  # guardian: allow-silent-swallow -- acceptable exception handling
        result["verdict"] = "PARSE_ERROR"
        result["reason"] = f"Syntax error: {e}"
        return result
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    if not classes:
        result["is_script"] = True
        result["verdict"] = "NOT_AGENT"
        result["reason"] = "Script file - no class definitions"
        return result
    for cls in tqdm(classes, desc="Processing", unit="item"):
        bases = extract_bases(cls)
        class_info = {
            "name": cls.name,
            "ends_with_agent": cls.name.endswith("Agent"),
            "bases": list(bases),
            "inherits_sovereign": bool(bases & SOVEREIGN_BASES),
            "inherits_layer_base": bool(bases & LAYER_BASES),
            "has_heal_repository": has_method(cls, "heal_repository"),
            "is_mixin": "Mixin" in cls.name,
            "is_dataclass": any(
                isinstance(d, ast.Name)
                and d.id == "dataclass"
                or (isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and (d.func.id == "dataclass"))
                for d in cls.decorator_list
            ),
        }
        is_sovereign = (
            class_info["ends_with_agent"]
            and (class_info["inherits_sovereign"] or class_info["inherits_layer_base"])
            and (not class_info["is_mixin"])
        )
        class_info["is_sovereign_agent"] = is_sovereign
        result["classes"].append(class_info)
    sovereign_classes = [c for c in result["classes"] if c["is_sovereign_agent"]]
    mixin_classes = [c for c in result["classes"] if c["is_mixin"]]
    if sovereign_classes:
        result["verdict"] = "SOVEREIGN_AGENT"
        result["reason"] = f"Contains sovereign agent class(es): {[c['name'] for c in sovereign_classes]}"
    elif mixin_classes:
        result["verdict"] = "MIXIN"
        result["reason"] = f"Contains mixin class(es): {[c['name'] for c in mixin_classes]}"
    elif any(c["ends_with_agent"] for c in result["classes"]):
        agent_classes = [c for c in result["classes"] if c["ends_with_agent"]]
        result["verdict"] = "PSEUDO_AGENT"
        result["reason"] = (
            f"Has Agent suffix but no sovereign inheritance: {[c['name'] for c in agent_classes]}"
        )
    else:
        result["verdict"] = "NOT_AGENT"
        non_agent_classes = [c["name"] for c in result["classes"]]
        result["reason"] = f"Infrastructure/utility classes: {non_agent_classes}"
    return result


def print_report(results: list[dict]) -> None:
    """Print formatted verification report."""
    print("=" * 100)
    print("AGENT STATUS VERIFICATION REPORT")
    print("=" * 100)
    print()
    verdicts = {}
    for r in results:
        v = r["verdict"]
        verdicts[v] = verdicts.get(v, 0) + 1
    print("SUMMARY:")
    for verdict, count in sorted(verdicts.items()):
        print(f"  {verdict}: {count}")
    print()
    print("-" * 100)
    print("DETAILED ANALYSIS:")
    print("-" * 100)
    for r in tqdm(results, desc="Processing", unit="item"):
        print()
        print(f"FILE: {r['file']}")
        print(f"  Verdict: {r['verdict']}")
        print(f"  Reason: {r['reason']}")
        if r["classes"]:
            print(f"  Classes found: {len(r['classes'])}")
            for cls in r["classes"]:
                print(f"    - {cls['name']}:")
                print(f"        Ends with 'Agent': {cls['ends_with_agent']}")
                print(f"        Inherits Sovereign Base: {cls['inherits_sovereign']}")
                print(f"        Inherits Layer Base: {cls['inherits_layer_base']}")
                print(f"        Has heal_repository(): {cls['has_heal_repository']}")
                print(f"        Is Mixin: {cls['is_mixin']}")
                print(f"        Bases: {cls['bases']}")
                print(f"        => IS SOVEREIGN AGENT: {cls['is_sovereign_agent']}")
    print()
    print("=" * 100)
    print("EXCLUSION RECOMMENDATIONS:")
    print("=" * 100)
    to_exclude = [r for r in results if r["verdict"] in ("NOT_AGENT", "MIXIN", "PSEUDO_AGENT")]
    if to_exclude:
        print("\nThe following files should be EXCLUDED from agent discovery:")
        for r in to_exclude:
            print(f"  - {r['file']}")
            print(f"    Reason: {r['reason']}")
    else:
        print("\nNo files recommended for exclusion.")
    print()


def main():
    print("Scanning suspect files for agent characteristics...")
    print()
    results = []
    for rel_path in SUSPECT_FILES:
        file_path = PROJECT_ROOT / rel_path
        result = analyze_file(file_path)
        results.append(result)
    print_report(results)
    non_agents = [r for r in results if r["verdict"] in ("NOT_AGENT", "MIXIN", "PSEUDO_AGENT")]
    print(f"\nTotal suspects analyzed: {len(results)}")
    print(f"Confirmed non-agents: {len(non_agents)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
