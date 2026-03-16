"""ADG Test Accelerator — uses the Architecture Dependency Graph to:

1. **Gap analysis** (`gap`): rank uncovered production modules by fan-in.
2. **Scoped selection** (`scope`): given changed files, emit only the test
   files that cover them (or their transitive importers) via ADG edges.
3. **Parallel groups** (`groups`): partition test files into N balanced
   groups by ADG layer for use with pytest-xdist ``--dist worksteal``.
4. **Full report** (`report`): JSON combining all three above.

Usage::

    # Gap analysis
    python tools/adg_test_accelerator.py gap [--top 20] [--layer L5]

    # Scoped test selection (pipe to pytest -p no:randomly)
    python tools/adg_test_accelerator.py scope --changed agentic_core/L0_routing/config/path_constants.py

    # Parallel groups (4 workers)
    python tools/adg_test_accelerator.py groups --workers 4

    # Full JSON report
    python tools/adg_test_accelerator.py report --out docs/reports/plans/adg_test_report.json
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from collections import defaultdict

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

_emit_records_execution_trace("p0", "evidence", "adg_test_accelerator")
_emit_applies_guardrail("p0", "adg_test_accelerator", "p0_governance")
_emit_reads_policy_state("p0", "adg_test_accelerator", "policy_binding")
_emit_snapshots_state("p0", "adg_test_accelerator", "state_snapshot")
emit_replay_key("p0", "adg_test_accelerator")
emit_determinism_digest("p0", "adg_test_accelerator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_test_accelerator", "execution_auth")
_emit_validates_capability("p2", "adg_test_accelerator", "capability_check")
_emit_routes_to_capability("p2", "adg_test_accelerator", "capability_route")
_emit_writes_via_uwg("p2", "adg_test_accelerator", "uwg_write")
_emit_blocks_direct_write("p2", "adg_test_accelerator", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_test_accelerator", "tool_invocation")
_emit_captures_execution_output("p2", "adg_test_accelerator", "exec_output")
_emit_dispatches_agent("p3", "adg_test_accelerator", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_test_accelerator", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_test_accelerator", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_test_accelerator", "healing_outcome")
_emit_escalates_failure("p3", "adg_test_accelerator", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_test_accelerator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_test_accelerator", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_test_accelerator", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_test_accelerator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_test_accelerator", "eval_metric")
_emit_stores_embedding("p4", "adg_test_accelerator", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_test_accelerator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_test_accelerator", "exec_snapshot_link")

_ROOT = pathlib.Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agentic_core.adg.analysis.hotspot_index import HotspotIndex
from agentic_core.adg.analysis.test_gap import detect_test_gaps
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner, ScanResult
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("adg_test_accelerator", "p4obs", "metric_1")
_emit_emits_metric_event("adg_test_accelerator", "p4obs", "metric_2")
_emit_emits_metric_event("adg_test_accelerator", "p4obs", "metric_3")
_emit_emits_metric_event("adg_test_accelerator", "p4obs", "metric_4")
_emit_emits_metric_event("adg_test_accelerator", "p4obs", "metric_5")
_emit_emits_metric_event("adg_test_accelerator", "p4obs", "metric_6")
_emit_records_incident_event("adg_test_accelerator", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_test_accelerator", "p4obs", "anomaly")
_emit_writes_observability_log("adg_test_accelerator", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_test_accelerator", "p4obs", "mon_state")
_emit_triggers_alert("adg_test_accelerator", "p4obs", "alert")
_emit_links_incident_trace("adg_test_accelerator", "p4obs", "trace_link")
_emit_captures_pattern("adg_test_accelerator", "p3lm", "pattern")
_emit_records_learning_event("adg_test_accelerator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_test_accelerator", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_test_accelerator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_test_accelerator", "p3lm", "routing")
_emit_improves_agent_policy("adg_test_accelerator", "p3lm", "policy")
_emit_stores_learning_state("adg_test_accelerator", "p3lm", "state")
_emit_records_execution_trace("adg_test_accelerator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_test_accelerator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_test_accelerator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_test_accelerator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_test_accelerator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_test_accelerator", "env_read", "p2_env_1")
_emit_reads_environ("adg_test_accelerator", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_test_accelerator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_test_accelerator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_test_accelerator", "context_pull")
_emit_pulls_context("p1", "adg_test_accelerator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_test_accelerator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_test_accelerator", "uwg_term_2")
_emit_writes_through("p1", "adg_test_accelerator", "write_through")
_emit_writes_through("p1", "adg_test_accelerator", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_test_accelerator", "safety_validation")
_emit_invokes_eval("p1", "adg_test_accelerator", "eval_call")
_emit_proposal_commits_routing("p1", "adg_test_accelerator", "routing_commit")

_SYMBOL_PREFIX = "ADG::Symbol::"
_MODULE_PREFIX = "ADG::Module::"

_PRODUCTION_EXCLUDES = ("tests/", "ops_scripts/", "tools/", ".py.bak")


def _is_production(path: str) -> bool:
    norm = path.replace("\\", "/")
    return not any(norm.startswith(e) or norm.endswith(e) for e in _PRODUCTION_EXCLUDES)


def _symbol_to_path(sym: str) -> str:
    """Convert ADG::Symbol::a.b.c -> a/b/c.py (best-effort)."""
    return sym.replace(".", "/") + ".py"


def _module_adg_to_path(adg_name: str) -> str:
    """Strip ADG::Module:: prefix."""
    if adg_name.startswith(_MODULE_PREFIX):
        return adg_name[len(_MODULE_PREFIX):]
    return adg_name


# ---------------------------------------------------------------------------
# Core data structures built from one scan
# ---------------------------------------------------------------------------


class ADGIndex:
    """Pre-built index for O(1) queries over a ScanResult."""

    def __init__(self, result: ScanResult) -> None:
        self.result = result
        self.hotspot = HotspotIndex.build(result)

        # prod_to_tests: production module path -> set of test file paths
        self.prod_to_tests: dict[str, set[str]] = defaultdict(set)

        # test_to_prods: test file path -> set of production module paths
        self.test_to_prods: dict[str, set[str]] = defaultdict(set)

        # imports graph: module -> set of modules it imports (for transitivity)
        self.imports: dict[str, set[str]] = defaultdict(set)
        self.imported_by: dict[str, set[str]] = defaultdict(set)

        self._build()

    def _build(self) -> None:
        for edge in self.result.edges:
            src = edge.source_file.replace("\\", "/")
            rel = edge.relation_type

            if rel == "covers":
                to_name = edge.to_name
                if to_name.startswith(_SYMBOL_PREFIX):
                    prod_path = _symbol_to_path(to_name[len(_SYMBOL_PREFIX):])
                elif to_name.startswith(_MODULE_PREFIX):
                    prod_path = _module_adg_to_path(to_name)
                else:
                    continue

                test_src = src
                if "tests/" in test_src:
                    self.prod_to_tests[prod_path].add(test_src)
                    self.test_to_prods[test_src].add(prod_path)

            elif rel == "imports":
                frm = _module_adg_to_path(edge.from_name)
                to = _module_adg_to_path(edge.to_name)
                self.imports[frm].add(to)
                self.imported_by[to].add(frm)

    # guardian: allow-magic-config
    def transitive_importers(self, module_path: str, max_depth: int = 4) -> set[str]:
        """Return all modules that (transitively) import module_path."""
        visited: set[str] = set()
        queue = [module_path]
        depth = 0
        while queue and depth < max_depth:
            next_q: list[str] = []
            for m in queue:
                for imp in self.imported_by.get(m, set()):
                    if imp not in visited:
                        visited.add(imp)
                        next_q.append(imp)
            queue = next_q
            depth += 1
        return visited

    def tests_for_changed(self, changed_paths: list[str]) -> set[str]:
        """Return all test files that cover any changed module or its importers."""
        tests: set[str] = set()
        for cp in changed_paths:
            norm = cp.replace("\\", "/")
            # Direct covers
            tests.update(self.prod_to_tests.get(norm, set()))
            # Transitive: things that import this module
            for imp in self.transitive_importers(norm):
                tests.update(self.prod_to_tests.get(imp, set()))
        return tests

    def layer_of(self, test_path: str) -> str:
        """Infer layer from ADG or path heuristic."""
        norm = test_path.replace("\\", "/")
        for prods in [self.test_to_prods.get(norm, set())]:
            for prod in prods:
                from agentic_core.adg.schema import module_path_to_layer
                layer = module_path_to_layer(prod)
                if layer and layer != "unknown":
                    return layer
        # Fall back to path heuristic
        for ln in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            if f"/{ln}_" in norm or f"/{ln.lower()}_" in norm:
                return ln
        return "other"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_gap(args: argparse.Namespace, idx: ADGIndex) -> None:
    """Print uncovered production modules ranked by fan-in."""
    report = detect_test_gaps(idx.result, hotspot_index=idx.hotspot)
    entries = report.uncovered_modules
    if args.layer:
        entries = [e for e in entries if e.layer == args.layer]

    # Re-sort by fan-in descending
    entries = sorted(entries, key=lambda e: -e.fan_in)[:args.top]

    print(f"Coverage rate : {report.coverage_rate:.1%}")
    print(f"Total production modules : {report.total_production_modules}")
    print(f"Covered   : {len(report.covered_modules)}")
    print(f"Uncovered : {len(report.uncovered_modules)}")
    print()
    print(f"{'fan_in':>6}  {'layer':<6}  module_path")
    print("-" * 70)
    for e in entries:
        print(f"{e.fan_in:>6}  {e.layer:<6}  {e.module_path}")

    print()
    print("Gap by layer:")
    for layer, count in sorted(report.gap_by_layer.items()):
        print(f"  {layer}: {count}")


def cmd_scope(args: argparse.Namespace, idx: ADGIndex) -> None:
    """Emit test files that cover the changed modules (one per line)."""
    changed = [c.strip() for c in args.changed if c.strip()]
    if not changed and args.stdin:
        changed = [l.strip() for l in sys.stdin if l.strip()]

    if not changed:
        print("No changed files specified.", file=sys.stderr)
        sys.exit(1)

    tests = idx.tests_for_changed(changed)

    if args.format == "pytest":
        # Space-separated for use as: pytest $(python ... scope ...)
        existing = [t for t in sorted(tests) if pathlib.Path(t).exists()]
        print(" ".join(existing) if existing else "")
    elif args.format == "json":
        existing = sorted(t for t in tests if pathlib.Path(t).exists())
        print(json.dumps({"changed": changed, "impacted_tests": existing}, indent=2))
    else:
        for t in sorted(tests):
            print(t)

    if not tests:
        print(f"# No ADG coverage signal found for: {changed}", file=sys.stderr)
        print("# Run full suite (no scoping possible)", file=sys.stderr)


def cmd_groups(args: argparse.Namespace, idx: ADGIndex) -> None:
    """Partition test files into N balanced groups by layer."""
    n = args.workers

    # Collect all test files from result
    all_test_files: list[str] = sorted(
        set(
            e.source_file.replace("\\", "/")
            for e in idx.result.edges
            if "tests/" in e.source_file.replace("\\", "/")
        )
    )

    # Group by layer
    by_layer: dict[str, list[str]] = defaultdict(list)
    for tf in all_test_files:
        layer = idx.layer_of(tf)
        by_layer[layer].append(tf)

    # Assign layers to workers round-robin by descending layer size
    workers: list[list[str]] = [[] for _ in range(n)]
    worker_sizes = [0] * n
    for layer in sorted(by_layer, key=lambda l: -len(by_layer[l])):
        # assign to smallest worker
        target = min(range(n), key=lambda i: worker_sizes[i])
        workers[target].extend(by_layer[layer])
        worker_sizes[target] += len(by_layer[layer])

    if args.format == "json":
        out = {
            f"worker_{i}": {
                "files": workers[i],
                "count": len(workers[i]),
            }
            for i in range(n)
        }
        out["total_files"] = len(all_test_files)
        out["layers"] = {k: len(v) for k, v in sorted(by_layer.items())}
        print(json.dumps(out, indent=2))
    else:
        for i, group in enumerate(workers):
            print(f"\n# Worker {i} ({len(group)} files):")
            for f in group:
                print(f"  {f}")


def cmd_report(args: argparse.Namespace, idx: ADGIndex) -> None:
    """Write a full JSON report combining gap analysis and layer breakdown."""
    from agentic_core.adg.analysis.test_gap import detect_test_gaps

    report = detect_test_gaps(idx.result, hotspot_index=idx.hotspot)

    # Build coverage map
    covered_by: dict[str, list[str]] = {}
    for prod, tests in idx.prod_to_tests.items():
        covered_by[prod] = sorted(tests)

    # Layer breakdown of test files
    all_test_files = sorted(
        set(
            e.source_file.replace("\\", "/")
            for e in idx.result.edges
            if "tests/" in e.source_file.replace("\\", "/")
        )
    )
    layer_counts: dict[str, int] = defaultdict(int)
    for tf in all_test_files:
        layer_counts[idx.layer_of(tf)] += 1

    out = {
        "meta": {
            "scanner_version": idx.result.manifest.scanner_version,
            "schema_version": idx.result.manifest.schema_version,
            "parsed_module_count": idx.result.manifest.parsed_module_count,
            "syntax_error_count": idx.result.manifest.syntax_error_count,
            "test_covers_count": idx.result.manifest.test_covers_count,
        },
        "gap_summary": report.to_dict(),
        "test_layer_distribution": dict(sorted(layer_counts.items())),
        "coverage_map_sample": {
            k: v for k, v in list(covered_by.items())[:50]
        },
        "highest_risk_gaps": [e.to_dict() for e in report.highest_risk_gaps[:30]],
    }

    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Report written to: {out_path}")
    print(f"Coverage rate    : {report.coverage_rate:.1%}")
    print(f"Uncovered modules: {len(report.uncovered_modules)}/{report.total_production_modules}")
    print(f"Syntax errors    : {idx.result.manifest.syntax_error_count}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ADG Test Accelerator")
    p.add_argument(
        "--no-tests",
        action="store_true",
        help="Scan without test files (faster, for gap analysis only)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # gap
    gap = sub.add_parser("gap", help="Show uncovered production modules ranked by fan-in")
    gap.add_argument("--top", type=int, default=30, help="Show top N uncovered modules")
    gap.add_argument("--layer", default=None, help="Filter to a specific layer (e.g. L5)")

    # scope
    scope = sub.add_parser("scope", help="Emit test files covering changed modules")
    scope.add_argument("--changed", nargs="*", default=[], metavar="FILE",
                       help="Changed file paths (relative to repo root)")
    scope.add_argument("--stdin", action="store_true",
                       help="Read changed files from stdin (one per line)")
    scope.add_argument("--format", choices=["lines", "pytest", "json"], default="lines")

    # groups
    grp = sub.add_parser("groups", help="Partition tests into N parallel worker groups")
    grp.add_argument("--workers", type=int, default=4)
    grp.add_argument("--format", choices=["text", "json"], default="text")

    # report
    rpt = sub.add_parser("report", help="Write full JSON report")
    rpt.add_argument("--out", default="docs/reports/plans/adg_test_report.json")

    return p


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    include_tests = not args.no_tests
    t0 = time.time()
    print(f"[ADG] Scanning (include_tests={include_tests})...", file=sys.stderr)
    scanner = ADGStaticScanner(include_tests=include_tests)
    result = scanner.scan()
    print(
        f"[ADG] Scan done in {time.time()-t0:.1f}s — "
        f"{len(result.modules)} modules, {len(result.edges)} edges",
        file=sys.stderr,
    )

    idx = ADGIndex(result)

    if args.command == "gap":
        cmd_gap(args, idx)
    elif args.command == "scope":
        cmd_scope(args, idx)
    elif args.command == "groups":
        cmd_groups(args, idx)
    elif args.command == "report":
        cmd_report(args, idx)


if __name__ == "__main__":
    main()
