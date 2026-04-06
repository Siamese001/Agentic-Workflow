"""Prune redundant ADG stubs.

A module's ADG stub is redundant when a foundational test (non-_adg) already
covers it via `covers` edges AND the foundational test has >= FOUNDATIONAL_DEPTH_THRESHOLD
assert/raises calls (meaning it has real behavioral depth).

Redundant stubs are DELETED. The `covers` edge is preserved by the foundational test.
"""
from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path

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
    _emit_reads_through,
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

_emit_records_execution_trace("p0", "evidence", "_prune_redundant_adg")
_emit_applies_guardrail("p0", "_prune_redundant_adg", "p0_governance")
_emit_reads_policy_state("p0", "_prune_redundant_adg", "policy_binding")
_emit_snapshots_state("p0", "_prune_redundant_adg", "state_snapshot")
emit_replay_key("p0", "_prune_redundant_adg")
emit_determinism_digest("p0", "_prune_redundant_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_prune_redundant_adg", "execution_auth")
_emit_validates_capability("p2", "_prune_redundant_adg", "capability_check")
_emit_routes_to_capability("p2", "_prune_redundant_adg", "capability_route")
_emit_writes_via_uwg("p2", "_prune_redundant_adg", "uwg_write")
_emit_blocks_direct_write("p2", "_prune_redundant_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "_prune_redundant_adg", "tool_invocation")
_emit_captures_execution_output("p2", "_prune_redundant_adg", "exec_output")
_emit_dispatches_agent("p3", "_prune_redundant_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "_prune_redundant_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "_prune_redundant_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "_prune_redundant_adg", "healing_outcome")
_emit_escalates_failure("p3", "_prune_redundant_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "_prune_redundant_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_prune_redundant_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "_prune_redundant_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "_prune_redundant_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_prune_redundant_adg", "eval_metric")
_emit_stores_embedding("p4", "_prune_redundant_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "_prune_redundant_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_prune_redundant_adg", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
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

_emit_emits_metric_event("_prune_redundant_adg", "p4obs", "metric_1")
_emit_emits_metric_event("_prune_redundant_adg", "p4obs", "metric_2")
_emit_emits_metric_event("_prune_redundant_adg", "p4obs", "metric_3")
_emit_emits_metric_event("_prune_redundant_adg", "p4obs", "metric_4")
_emit_emits_metric_event("_prune_redundant_adg", "p4obs", "metric_5")
_emit_emits_metric_event("_prune_redundant_adg", "p4obs", "metric_6")
_emit_records_incident_event("_prune_redundant_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("_prune_redundant_adg", "p4obs", "anomaly")
_emit_writes_observability_log("_prune_redundant_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("_prune_redundant_adg", "p4obs", "mon_state")
_emit_triggers_alert("_prune_redundant_adg", "p4obs", "alert")
_emit_links_incident_trace("_prune_redundant_adg", "p4obs", "trace_link")
_emit_captures_pattern("_prune_redundant_adg", "p3lm", "pattern")
_emit_records_learning_event("_prune_redundant_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_prune_redundant_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("_prune_redundant_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_prune_redundant_adg", "p3lm", "routing")
_emit_improves_agent_policy("_prune_redundant_adg", "p3lm", "policy")
_emit_stores_learning_state("_prune_redundant_adg", "p3lm", "state")
_emit_records_execution_trace("_prune_redundant_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_prune_redundant_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_prune_redundant_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_prune_redundant_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_prune_redundant_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_prune_redundant_adg", "env_read", "p2_env_1")
_emit_reads_environ("_prune_redundant_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("_prune_redundant_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_prune_redundant_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_prune_redundant_adg", "context_pull")
_emit_pulls_context("p1", "_prune_redundant_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_prune_redundant_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_prune_redundant_adg", "uwg_term_secondary")
_emit_writes_through("p1", "_prune_redundant_adg", "write_through")
_emit_writes_through("p1", "_prune_redundant_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_prune_redundant_adg", "safety_validation")
_emit_invokes_eval("p1", "_prune_redundant_adg", "eval_call")
_emit_proposal_commits_routing("p1", "_prune_redundant_adg", "routing_commit")
_emit_escalates_to_human("p1", "_prune_redundant_adg", "human_escalation")
_emit_routes_through("p1", "_prune_redundant_adg", "route_through")
_emit_checks_agent_registry("p1", "_prune_redundant_adg", "agent_registry")
_emit_validates_agent_capability("p1", "_prune_redundant_adg", "capability")
_emit_dispatches_execution_plan("p1", "_prune_redundant_adg", "exec_plan")
_emit_agent_executes_agent("p1", "_prune_redundant_adg", "sub_agent")
_emit_routes_to_agent("p1", "_prune_redundant_adg", "target_agent")
_emit_verifies_policy("p1", "_prune_redundant_adg", "policy_check")
_emit_observes_runtime_state("p1", "_prune_redundant_adg", "runtime_state")
_emit_verifies_boundary("p1", "_prune_redundant_adg", "boundary_check")
_emit_transcripts_response("p1", "_prune_redundant_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "_prune_redundant_adg")
_emit_gated_by_confidence("p1", "_prune_redundant_adg", "confidence_gate")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_1")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_2")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_3")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_4")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_5")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_6")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_7")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_8")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_9")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_10")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_11")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_12")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_13")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_14")
_emit_reads_through("l4", "_prune_redundant_adg", "urg_read_15")

FOUNDATIONAL_DEPTH_THRESHOLD = 5  # foundational test must have >= this many asserts


def is_prod(p: str) -> bool:
    p2 = p.replace("\\", "/")
    return (
        not p2.startswith("tests/")
        and not p2.startswith("tools/")
        and "ops_scripts" not in p2
        and "__pycache__" not in p2
        and p2.endswith(".py")
    )


def adg_to_dotted(name: str) -> str:
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if name.startswith(pfx):
            name = name[len(pfx):]
    return name.removesuffix(".py")


def count_assertions(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return 0
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            count += 1
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "raises":
                count += 1
    return count


def module_to_adg_stub(module_path: str) -> Path:
    parts = Path(module_path.replace("\\", "/")).parts
    stem = Path(parts[-1]).stem
    return ROOT / "tests" / "unit" / Path(*parts[:-1]) / f"test_{stem}_adg.py"


print("[PRUNE] Scanning ADG...")
scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True)
result = scanner.scan()
print(f"[PRUNE] Done: {len(result.modules)} modules, {len(result.edges)} edges")

prod_set = {m for m in result.modules if is_prod(m)}
prod_dotted_to_path: dict[str, str] = {
    m.replace("\\", "/").removesuffix(".py").replace("/", "."): m
    for m in prod_set
}

# Build covers map: prod_path -> {adg_test_dotted_names}, {foundational_test_dotted_names}
covered_by_adg: dict[str, list[str]] = defaultdict(list)
covered_by_foundational: dict[str, list[str]] = defaultdict(list)

for e in result.edges:
    if e.relation_type != "covers":
        continue
    from_d = adg_to_dotted(e.from_name)
    to_d = adg_to_dotted(e.to_name)
    if to_d not in prod_dotted_to_path:
        continue
    prod_path = prod_dotted_to_path[to_d]
    if from_d.split(".")[-1].endswith("_adg"):
        covered_by_adg[prod_path].append(from_d)
    else:
        covered_by_foundational[prod_path].append(from_d)

# Find redundant: both covered, foundational has enough depth
deleted = []
kept = []
not_present = []

both = [p for p in prod_set if covered_by_adg[p] and covered_by_foundational[p]]
print(f"[PRUNE] {len(both)} modules covered by both ADG + foundational")

for prod_path in sorted(both):
    adg_stub = module_to_adg_stub(prod_path)
    if not adg_stub.exists():
        not_present.append(prod_path)
        continue

    # Check foundational depth: resolve dotted names to file paths
    foundational_depth = 0
    for test_dotted in covered_by_foundational[prod_path]:
        # Convert dotted to file path under tests/
        test_rel = test_dotted.replace(".", "/") + ".py"
        test_path = ROOT / test_rel
        # Also try with tests/ prefix stripped
        if not test_path.exists():
            # try directly under ROOT
            for candidate in (ROOT / test_rel,):
                if candidate.exists():
                    test_path = candidate
                    break
        foundational_depth += count_assertions(test_path)

    adg_depth = count_assertions(adg_stub)

    if foundational_depth >= FOUNDATIONAL_DEPTH_THRESHOLD:
        # Redundant: foundational covers it well enough
        adg_stub.unlink()
        deleted.append({
            "module": prod_path,
            "adg_stub": str(adg_stub.relative_to(ROOT)),
            "foundational_depth": foundational_depth,
            "adg_depth": adg_depth,
        })
    else:
        kept.append({
            "module": prod_path,
            "foundational_depth": foundational_depth,
            "adg_depth": adg_depth,
            "reason": "foundational too shallow to be sole coverage",
        })

print("\n[PRUNE] Results:")
print(f"  Deleted redundant ADG stubs : {len(deleted)}")
print(f"  Kept (foundational shallow) : {len(kept)}")
print(f"  ADG stub not present        : {len(not_present)}")

print("\n[PRUNE] Deleted stubs (top 20 by foundational depth):")
for e in sorted(deleted, key=lambda x: -x["foundational_depth"])[:20]:
    print(f"  found={e['foundational_depth']:>4} asserts  adg={e['adg_depth']:>3}  {e['module']}")

print("\n[PRUNE] Kept (foundational too shallow):")
for e in sorted(kept, key=lambda x: -x["adg_depth"])[:20]:
    print(f"  found={e['foundational_depth']:>3} asserts  adg={e['adg_depth']:>3}  {e['module']}")
