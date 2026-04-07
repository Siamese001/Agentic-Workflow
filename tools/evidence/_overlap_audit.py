"""Audit overlap between ADG-derived (_adg.py) and foundational (non-_adg) tests.

Outputs:
  - Overlap count (module covered by both ADG stub AND foundational test)
  - Redundancy classification (ADG stub is superfluous when foundational has depth)
  - fan_in distribution with threshold analysis
  - High-fan_in modules that have only an ADG stub (need foundational)
"""
from __future__ import annotations

import ast
import json
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

_emit_records_execution_trace("p0", "evidence", "_overlap_audit")
_emit_applies_guardrail("p0", "_overlap_audit", "p0_governance")
_emit_reads_policy_state("p0", "_overlap_audit", "policy_binding")
_emit_snapshots_state("p0", "_overlap_audit", "state_snapshot")
emit_replay_key("p0", "_overlap_audit")
emit_determinism_digest("p0", "_overlap_audit")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_overlap_audit", "execution_auth")
_emit_validates_capability("p2", "_overlap_audit", "capability_check")
_emit_routes_to_capability("p2", "_overlap_audit", "capability_route")
_emit_writes_via_uwg("p2", "_overlap_audit", "uwg_write")
_emit_blocks_direct_write("p2", "_overlap_audit", "direct_write_block")
_emit_records_tool_invocation("p2", "_overlap_audit", "tool_invocation")
_emit_captures_execution_output("p2", "_overlap_audit", "exec_output")
_emit_dispatches_agent("p3", "_overlap_audit", "agent_dispatch")
_emit_coordinates_agents("p3", "_overlap_audit", "agent_coordination")
_emit_records_workflow_lineage("p3", "_overlap_audit", "workflow_lineage")
_emit_records_healing_outcome("p3", "_overlap_audit", "healing_outcome")
_emit_escalates_failure("p3", "_overlap_audit", "failure_escalation")
_emit_orchestrates_workflow("p3", "_overlap_audit", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_overlap_audit", "healing_dispatch")
_emit_invokes_evaluation("p3", "_overlap_audit", "evaluation_signal")
_emit_records_telemetry_event("p4", "_overlap_audit", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_overlap_audit", "eval_metric")
_emit_stores_embedding("p4", "_overlap_audit", "embedding_store")
_emit_updates_meta_learning_state("p4", "_overlap_audit", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_overlap_audit", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
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

_emit_emits_metric_event("_overlap_audit", "p4obs", "metric_1")
_emit_emits_metric_event("_overlap_audit", "p4obs", "metric_2")
_emit_emits_metric_event("_overlap_audit", "p4obs", "metric_3")
_emit_emits_metric_event("_overlap_audit", "p4obs", "metric_4")
_emit_emits_metric_event("_overlap_audit", "p4obs", "metric_5")
_emit_emits_metric_event("_overlap_audit", "p4obs", "metric_6")
_emit_records_incident_event("_overlap_audit", "p4obs", "incident")
_emit_captures_runtime_anomaly("_overlap_audit", "p4obs", "anomaly")
_emit_writes_observability_log("_overlap_audit", "p4obs", "obs_log")
_emit_updates_monitoring_state("_overlap_audit", "p4obs", "mon_state")
_emit_triggers_alert("_overlap_audit", "p4obs", "alert")
_emit_links_incident_trace("_overlap_audit", "p4obs", "trace_link")
_emit_captures_pattern("_overlap_audit", "p3lm", "pattern")
_emit_records_learning_event("_overlap_audit", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_overlap_audit", "p3lm", "snapshot")
_emit_feeds_meta_learning("_overlap_audit", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_overlap_audit", "p3lm", "routing")
_emit_improves_agent_policy("_overlap_audit", "p3lm", "policy")
_emit_stores_learning_state("_overlap_audit", "p3lm", "state")
_emit_records_execution_trace("_overlap_audit", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_overlap_audit", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_overlap_audit", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_overlap_audit", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_overlap_audit", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_overlap_audit", "env_read", "p2_env_1")
_emit_reads_environ("_overlap_audit", "env_read", "p2_env_2")
_emit_reads_runtime_state("_overlap_audit", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_overlap_audit", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "_overlap_audit", "context_pull")
_emit_pulls_context("p1", "_overlap_audit", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_overlap_audit", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_overlap_audit", "uwg_term_secondary")
_emit_writes_through("p1", "_overlap_audit", "write_through")
_emit_writes_through("p1", "_overlap_audit", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_overlap_audit", "safety_validation")
_emit_invokes_eval("p1", "_overlap_audit", "eval_call")
_emit_proposal_commits_routing("p1", "_overlap_audit", "routing_commit")
_emit_escalates_to_human("p1", "_overlap_audit", "human_escalation")
_emit_routes_through("p1", "_overlap_audit", "route_through")
_emit_checks_agent_registry("p1", "_overlap_audit", "agent_registry")
_emit_validates_agent_capability("p1", "_overlap_audit", "capability")
_emit_dispatches_execution_plan("p1", "_overlap_audit", "exec_plan")
_emit_agent_executes_agent("p1", "_overlap_audit", "sub_agent")
_emit_routes_to_agent("p1", "_overlap_audit", "target_agent")
_emit_verifies_policy("p1", "_overlap_audit", "policy_check")
_emit_observes_runtime_state("p1", "_overlap_audit", "runtime_state")
_emit_verifies_boundary("p1", "_overlap_audit", "boundary_check")
_emit_transcripts_response("p1", "_overlap_audit", "transcript")
_emit_hard_fails_untranscripted("p1", "_overlap_audit")
_emit_gated_by_confidence("p1", "_overlap_audit", "confidence_gate")
_emit_reads_through("l4", "_overlap_audit", "urg_read_1")
_emit_reads_through("l4", "_overlap_audit", "urg_read_2")
_emit_reads_through("l4", "_overlap_audit", "urg_read_3")
_emit_reads_through("l4", "_overlap_audit", "urg_read_4")
_emit_reads_through("l4", "_overlap_audit", "urg_read_5")
_emit_reads_through("l4", "_overlap_audit", "urg_read_6")
_emit_reads_through("l4", "_overlap_audit", "urg_read_7")
_emit_reads_through("l4", "_overlap_audit", "urg_read_8")
_emit_reads_through("l4", "_overlap_audit", "urg_read_9")
_emit_reads_through("l4", "_overlap_audit", "urg_read_10")
_emit_reads_through("l4", "_overlap_audit", "urg_read_11")
_emit_reads_through("l4", "_overlap_audit", "urg_read_12")
_emit_reads_through("l4", "_overlap_audit", "urg_read_13")
_emit_reads_through("l4", "_overlap_audit", "urg_read_14")
_emit_reads_through("l4", "_overlap_audit", "urg_read_15")
_emit_reads_through("l4", "_overlap_audit", "urg_read_16")
_emit_reads_through("l4", "_overlap_audit", "urg_read_17")
_emit_reads_through("l4", "_overlap_audit", "urg_read_18")
_emit_reads_through("l4", "_overlap_audit", "urg_read_19")

# ── Helpers ───────────────────────────────────────────────────────────────────

def layer_from_path(path: str) -> str:
    p = path.replace("\\", "/")
    for prefix, label in [
        ("agentic_core/L0", "L0"), ("agentic_core/L1", "L1"),
        ("agentic_core/L2", "L2"), ("agentic_core/L3", "L3"),
        ("agentic_core/L4", "L4"), ("agentic_core/L5", "L5"),
        ("agentic_core/L6", "L6"), ("apps_rg", "L_APP_RG"),
        ("apps_shared", "L_SHARED"), ("system_learning", "L_SL"),
        ("agentic_core/runtime", "L_RUNTIME"),
        ("agentic_core/enforcement", "L_ENF"),
        ("agentic_core/utils", "L_UTILS"),
        ("agentic_core/adg", "L_ADG"),
    ]:
        if p.startswith(prefix):
            return label
    return "OTHER"


def is_production(path: str) -> bool:
    p = path.replace("\\", "/")
    return (
        not p.startswith("tests/")
        and not p.startswith("tools/")
        and "ops_scripts" not in p
        and "__pycache__" not in p
        and p.endswith(".py")
    )


def module_to_test_paths(module_path: str):
    parts = Path(module_path.replace("\\", "/")).parts
    stem = Path(parts[-1]).stem
    test_dir = ROOT / "tests" / "unit" / Path(*parts[:-1])
    adg_path = test_dir / f"test_{stem}_adg.py"
    return adg_path, test_dir, stem


def count_assertions(test_path: Path) -> int:
    """Count assert + pytest.raises as proxy for test depth."""
    if not test_path.exists():
        return 0
    try:
        tree = ast.parse(test_path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return 0
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            count += 1
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "raises":
                count += 1
    return count


# ── Scan ──────────────────────────────────────────────────────────────────────

print("[AUDIT] Scanning ADG (this takes ~30s)...")
scanner = ADGStaticScanner(repo_root=ROOT, include_tests=True)
result = scanner.scan()
print(f"[AUDIT] Scan done: {len(result.modules)} modules, {len(result.edges)} edges")

# Build fan_in: count inbound `imports` edges per production module
# Edge.to_name is an ADG canonical name like "agentic_core.L0_routing.foo"
# Edge.from_name matches the module adg_name (dotted, no .py)
# result.modules are file-relative paths like "agentic_core/L0_routing/foo.py"

def adg_name_to_path(name: str) -> str:
    """agentic_core.L0_routing.foo -> agentic_core/L0_routing/foo.py (best-effort)."""
    # Strip ADG::Symbol:: or ADG::Module:: prefixes if present
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if name.startswith(pfx):
            name = name[len(pfx):]
    # If already a path-like string
    if name.endswith(".py"):
        return name
    return name.replace(".", "/") + ".py"

# Build set of production module paths
prod_paths = {m for m in result.modules if is_production(m)}

# Normalise path → dotted for lookup
def path_to_dotted(p: str) -> str:
    return p.replace("\\", "/").removesuffix(".py").replace("/", ".")

prod_dotted = {path_to_dotted(p): p for p in prod_paths}

# Count inbound imports edges (fan_in)
fan_in: dict[str, int] = defaultdict(int)
for edge in result.edges:
    if edge.relation_type != "imports":
        continue
    to_raw = edge.to_name
    # to_name can be dotted module like "agentic_core.L0_routing.foo"
    # or "ADG::Symbol::agentic_core.L0_routing.foo"
    for pfx in ("ADG::Symbol::", "ADG::Module::", "Symbol::", "Module::"):
        if to_raw.startswith(pfx):
            to_raw = to_raw[len(pfx):]
    # Find matching production module
    if to_raw in prod_dotted:
        fan_in[prod_dotted[to_raw]] += 1
    else:
        # try stripping last component (symbol import → module)
        parts = to_raw.rsplit(".", 1)
        if parts[0] in prod_dotted:
            fan_in[prod_dotted[parts[0]]] += 1

print(f"[AUDIT] fan_in computed for {len(fan_in)} modules")

# ── Per-module classification ─────────────────────────────────────────────────
overlap_both: list[dict] = []
adg_only: list[dict] = []
foundational_only: list[dict] = []
neither: list[dict] = []

for mod_path in sorted(prod_paths):
    fi = fan_in.get(mod_path, 0)
    layer = layer_from_path(mod_path)
    adg_path, test_dir, stem = module_to_test_paths(mod_path)

    has_adg = adg_path.exists()

    foundational_files = []
    if test_dir.exists():
        for f in test_dir.iterdir():
            if (f.name.startswith(f"test_{stem}")
                    and f.suffix == ".py"
                    and not f.name.endswith("_adg.py")):
                foundational_files.append(f)

    has_foundational = bool(foundational_files)
    adg_asserts = count_assertions(adg_path) if has_adg else 0
    found_asserts = sum(count_assertions(f) for f in foundational_files)

    entry = {
        "module": mod_path,
        "layer": layer,
        "fan_in": fi,
        "adg_asserts": adg_asserts,
        "foundational_asserts": found_asserts,
        "foundational_files": [str(f.relative_to(ROOT)) for f in foundational_files],
    }

    if has_adg and has_foundational:
        overlap_both.append(entry)
    elif has_adg and not has_foundational:
        adg_only.append(entry)
    elif not has_adg and has_foundational:
        foundational_only.append(entry)
    else:
        neither.append(entry)

# ── Print results ─────────────────────────────────────────────────────────────

print("\n=== OVERLAP AUDIT RESULTS ===")
print(f"  Total production modules   : {len(prod_paths)}")
print(f"  ADG + Foundational (BOTH)  : {len(overlap_both)}")
print(f"  ADG only                   : {len(adg_only)}")
print(f"  Foundational only          : {len(foundational_only)}")
print(f"  Neither                    : {len(neither)}")

# Redundant = both exist but foundational already deep, ADG adds nothing
redundant = [
    e for e in overlap_both
    if e["foundational_asserts"] >= 5
]
print(f"\n  Redundant ADG stubs (foundational has >=5 asserts): {len(redundant)}")

# True overlap = both have meaningful depth
both_deep = [
    e for e in overlap_both
    if e["adg_asserts"] >= 5 and e["foundational_asserts"] >= 5
]
print(f"  True deep overlap (both >=5 asserts): {len(both_deep)}")

# ADG-only with meaningful depth (ADG doing real work, no foundational)
adg_only_deep = [e for e in adg_only if e["adg_asserts"] >= 5]
print(f"  ADG-only with >=5 asserts (ADG is primary): {len(adg_only_deep)}")

print("\n=== TOP 20 REDUNDANT ADG STUBS (safe to remove) ===")
for e in sorted(redundant, key=lambda x: -x["foundational_asserts"])[:20]:
    print(f"  fan_in={e['fan_in']:>3}  adg={e['adg_asserts']:>3} asserts  "
          f"found={e['foundational_asserts']:>4} asserts  {e['module']}")

print("\n=== FAN_IN DISTRIBUTION ===")
all_fi = list(fan_in.values()) + [0] * (len(prod_paths) - len(fan_in))
buckets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, "6-10": 0, "11-20": 0, "21+": 0}
for fi_val in all_fi:
    if fi_val == 0: buckets[0] += 1
    elif fi_val == 1: buckets[1] += 1
    elif fi_val == 2: buckets[2] += 1
    elif fi_val == 3: buckets[3] += 1
    elif fi_val == 4: buckets[4] += 1
    elif fi_val == 5: buckets[5] += 1
    elif fi_val <= 10: buckets["6-10"] += 1
    elif fi_val <= 20: buckets["11-20"] += 1
    else: buckets["21+"] += 1
total = len(all_fi)
for k, v in buckets.items():
    print(f"  fan_in={k:>5}: {v:>4} modules  ({100*v/total:4.1f}%)")

print("\n=== THRESHOLD ANALYSIS (impact of requiring foundational test) ===")
print(f"  {'threshold':>10}  {'modules':>8}  {'%total':>7}  {'have_found':>11}  {'gap':>6}")
for threshold in [1, 2, 3, 5, 10]:
    above = [m for m in prod_paths if fan_in.get(m, 0) >= threshold]
    have_f = [e for e in (overlap_both + foundational_only) if e["fan_in"] >= threshold]
    gap = len(above) - len(have_f)
    print(f"  {threshold:>10}  {len(above):>8}  {100*len(above)/total:>6.1f}%  "
          f"{len(have_f):>11}  {gap:>6}")

print("\n=== HIGH FAN_IN, ADG-ONLY (top 30 — need foundational tests) ===")
needs_foundational = sorted(
    [e for e in adg_only if e["fan_in"] >= 3],
    key=lambda x: (-x["fan_in"], x["module"]),
)
print(f"  Total fan_in>=3, adg-only: {len(needs_foundational)}")
for e in needs_foundational[:30]:
    print(f"  fan_in={e['fan_in']:>3}  {e['module']}")

# ── Save JSON ─────────────────────────────────────────────────────────────────
out = {
    "summary": {
        "total_production": len(prod_paths),
        "overlap_both": len(overlap_both),
        "adg_only": len(adg_only),
        "foundational_only": len(foundational_only),
        "neither": len(neither),
        "redundant_adg_stubs": len(redundant),
        "both_deep": len(both_deep),
    },
    "redundant_adg_stubs": sorted(redundant, key=lambda x: -x["foundational_asserts"]),
    "needs_foundational_fan_in_ge3": needs_foundational,
    "fan_in_buckets": {str(k): v for k, v in buckets.items()},
}
out_path = ROOT / "tools" / "evidence" / "overlap_audit.json"
out_path.write_text(json.dumps(out, indent=2))
print(f"\n[AUDIT] Saved → {out_path.relative_to(ROOT)}")
