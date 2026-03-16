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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
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
    except SyntaxError:
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
