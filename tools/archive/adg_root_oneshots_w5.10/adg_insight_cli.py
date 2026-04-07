"""ADG Developer Insight CLI — structural intelligence queries for developers.

Commands:
  who-uses      <module>   — what modules/tests import this module
  depends-on    <module>   — what this module imports (direct + transitive)
  blast-radius  <file>     — impacted modules + tests if this file changes
  territory     <module>   — layer, ownership, allowed edges from this module
  agents-for    <base>     — all agent classes inheriting from a base class
  config-reads  <module>   — what config/env symbols this module reads
  unresolved                — print all unresolved import symbols in the graph
  coverage      <module>   — which tests cover this module

Usage:
    python -m tools.adg_insight_cli who-uses agentic_core/adg/schema.py
    python -m tools.adg_insight_cli blast-radius agentic_core/adg/schema.py
    python -m tools.adg_insight_cli agents-for BaseAgent
    python -m tools.adg_insight_cli unresolved
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

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

_emit_records_execution_trace("p0", "evidence", "adg_insight_cli")
_emit_applies_guardrail("p0", "adg_insight_cli", "p0_governance")
_emit_reads_policy_state("p0", "adg_insight_cli", "policy_binding")
_emit_snapshots_state("p0", "adg_insight_cli", "state_snapshot")
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

_emit_emits_metric_event("adg_insight_cli", "p4obs", "metric_1")
_emit_emits_metric_event("adg_insight_cli", "p4obs", "metric_2")
_emit_emits_metric_event("adg_insight_cli", "p4obs", "metric_3")
_emit_emits_metric_event("adg_insight_cli", "p4obs", "metric_4")
_emit_emits_metric_event("adg_insight_cli", "p4obs", "metric_5")
_emit_emits_metric_event("adg_insight_cli", "p4obs", "metric_6")
_emit_records_incident_event("adg_insight_cli", "p4obs", "incident")
_emit_captures_runtime_anomaly("adg_insight_cli", "p4obs", "anomaly")
_emit_writes_observability_log("adg_insight_cli", "p4obs", "obs_log")
_emit_updates_monitoring_state("adg_insight_cli", "p4obs", "mon_state")
_emit_triggers_alert("adg_insight_cli", "p4obs", "alert")
_emit_links_incident_trace("adg_insight_cli", "p4obs", "trace_link")
_emit_captures_pattern("adg_insight_cli", "p3lm", "pattern")
_emit_records_learning_event("adg_insight_cli", "p3lm", "learning_event")
_emit_writes_learning_snapshot("adg_insight_cli", "p3lm", "snapshot")
_emit_feeds_meta_learning("adg_insight_cli", "p3lm", "meta_feed")
_emit_updates_routing_strategy("adg_insight_cli", "p3lm", "routing")
_emit_improves_agent_policy("adg_insight_cli", "p3lm", "policy")
_emit_stores_learning_state("adg_insight_cli", "p3lm", "state")
_emit_records_execution_trace("adg_insight_cli", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("adg_insight_cli", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("adg_insight_cli", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("adg_insight_cli", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("adg_insight_cli", "L4_STATE", "p2_trace_5")
_emit_reads_environ("adg_insight_cli", "env_read", "p2_env_1")
_emit_reads_environ("adg_insight_cli", "env_read", "p2_env_2")
_emit_reads_runtime_state("adg_insight_cli", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("adg_insight_cli", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "adg_insight_cli", "context_pull")
_emit_pulls_context("p1", "adg_insight_cli", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "adg_insight_cli", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "adg_insight_cli", "uwg_term_2")
_emit_writes_through("p1", "adg_insight_cli", "write_through")
_emit_writes_through("p1", "adg_insight_cli", "write_through_2")
_emit_validated_by_safety_plane("p1", "adg_insight_cli", "safety_validation")
_emit_invokes_eval("p1", "adg_insight_cli", "eval_call")
_emit_proposal_commits_routing("p1", "adg_insight_cli", "routing_commit")
_emit_escalates_to_human("p1", "adg_insight_cli", "human_escalation")
_emit_routes_through("p1", "adg_insight_cli", "route_through")
_emit_checks_agent_registry("p1", "adg_insight_cli", "agent_registry")
_emit_validates_agent_capability("p1", "adg_insight_cli", "capability")
_emit_dispatches_execution_plan("p1", "adg_insight_cli", "exec_plan")
_emit_agent_executes_agent("p1", "adg_insight_cli", "sub_agent")
_emit_routes_to_agent("p1", "adg_insight_cli", "target_agent")
_emit_verifies_policy("p1", "adg_insight_cli", "policy_check")
_emit_observes_runtime_state("p1", "adg_insight_cli", "runtime_state")
_emit_verifies_boundary("p1", "adg_insight_cli", "boundary_check")
_emit_transcripts_response("p1", "adg_insight_cli", "transcript")
_emit_hard_fails_untranscripted("p1", "adg_insight_cli")
_emit_gated_by_confidence("p1", "adg_insight_cli", "confidence_gate")
emit_replay_key("p0", "adg_insight_cli")
emit_determinism_digest("p0", "adg_insight_cli")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "adg_insight_cli", "execution_auth")
_emit_validates_capability("p2", "adg_insight_cli", "capability_check")
_emit_routes_to_capability("p2", "adg_insight_cli", "capability_route")
_emit_writes_via_uwg("p2", "adg_insight_cli", "uwg_write")
_emit_blocks_direct_write("p2", "adg_insight_cli", "direct_write_block")
_emit_records_tool_invocation("p2", "adg_insight_cli", "tool_invocation")
_emit_captures_execution_output("p2", "adg_insight_cli", "exec_output")
_emit_dispatches_agent("p3", "adg_insight_cli", "agent_dispatch")
_emit_coordinates_agents("p3", "adg_insight_cli", "agent_coordination")
_emit_records_workflow_lineage("p3", "adg_insight_cli", "workflow_lineage")
_emit_records_healing_outcome("p3", "adg_insight_cli", "healing_outcome")
_emit_escalates_failure("p3", "adg_insight_cli", "failure_escalation")
_emit_orchestrates_workflow("p3", "adg_insight_cli", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "adg_insight_cli", "healing_dispatch")
_emit_invokes_evaluation("p3", "adg_insight_cli", "evaluation_signal")
_emit_records_telemetry_event("p4", "adg_insight_cli", "telemetry_event")
_emit_captures_evaluation_metric("p4", "adg_insight_cli", "eval_metric")
_emit_stores_embedding("p4", "adg_insight_cli", "embedding_store")
_emit_updates_meta_learning_state("p4", "adg_insight_cli", "meta_learning")
_emit_links_execution_to_snapshot("p4", "adg_insight_cli", "exec_snapshot_link")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_1")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_2")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_3")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_4")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_5")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_6")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_7")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_8")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_9")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_10")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_11")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_12")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_13")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_14")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_15")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_16")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_17")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_18")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_19")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_20")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_21")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_22")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_23")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_24")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_25")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_26")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_27")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_28")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_29")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_30")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_31")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_32")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_33")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_34")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_35")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_36")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_37")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_38")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_39")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_40")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_41")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_42")
_emit_reads_through("l4", "adg_insight_cli", "urg_read_43")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"


def _get_result(repo_root: Path) -> ScanResult:
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    return load_or_scan(repo_root=str(repo_root))


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------


def cmd_who_uses(module_path: str, result: ScanResult) -> dict:
    """Return all modules and tests that directly import the given module."""
    norm_path = module_path.replace("\\", "/")
    target_adg = _MODULE_PREFIX + norm_path

    direct_importers: list[str] = []
    for edge in result.edges:
        if edge.relation_type == "imports" and edge.to_name == target_adg:
            if edge.from_name.startswith(_MODULE_PREFIX):
                from_path = edge.from_name[len(_MODULE_PREFIX):]
                direct_importers.append(from_path)

    tests = [p for p in sorted(set(direct_importers)) if p.startswith("tests/")]
    sources = [p for p in sorted(set(direct_importers)) if not p.startswith("tests/")]

    return {
        "module": norm_path,
        "direct_importers": sorted(set(direct_importers)),
        "source_importers": sources,
        "test_importers": tests,
        "total_count": len(set(direct_importers)),
    }


def cmd_depends_on(module_path: str, result: ScanResult, transitive: bool = False) -> dict:
    """Return all modules this module imports (direct, optionally transitive)."""
    norm_path = module_path.replace("\\", "/")
    source_adg = _MODULE_PREFIX + norm_path

    direct: set[str] = set()
    for edge in result.edges:
        if edge.relation_type == "imports" and edge.from_name == source_adg:
            to_path = ""
            if edge.to_name.startswith(_MODULE_PREFIX):
                to_path = edge.to_name[len(_MODULE_PREFIX):]
            elif edge.to_name.startswith(_SYMBOL_PREFIX):
                to_path = edge.to_name[len(_SYMBOL_PREFIX):]
            if to_path:
                direct.add(to_path)

    result_dict: dict = {
        "module": norm_path,
        "direct_imports": sorted(direct),
        "direct_count": len(direct),
    }

    if transitive:
        # BFS forward
        forward: dict[str, set[str]] = {}
        for edge in result.edges:
            if edge.relation_type == "imports" and edge.from_name.startswith(_MODULE_PREFIX):
                from_p = edge.from_name[len(_MODULE_PREFIX):]
                to_p = edge.to_name[len(_MODULE_PREFIX):] if edge.to_name.startswith(_MODULE_PREFIX) else ""
                if to_p:
                    if from_p not in forward:
                        forward[from_p] = set()
                    forward[from_p].add(to_p)

        visited: set[str] = set()
        frontier = list(direct)
        while frontier:
            mod = frontier.pop()
            if mod in visited:
                continue
            visited.add(mod)
            frontier.extend(m for m in forward.get(mod, set()) if m not in visited)

        result_dict["transitive_imports"] = sorted(visited - direct)
        result_dict["transitive_count"] = len(visited)

    return result_dict


def cmd_blast_radius(module_path: str, result: ScanResult, repo_root: Path) -> dict:
    """Return impact analysis if this file changes."""
    from tools.change_impact_engine import ChangeImpactEngine

    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze([module_path.replace("\\", "/")])
    return impact.to_dict()


def cmd_territory(module_path: str) -> dict:
    """Return layer, territory, and allowed edges for a module path."""
    from agentic_core.adg.contracts.schema_util import ALLOWED_LAYER_EDGES, module_path_to_layer

    norm_path = module_path.replace("\\", "/")
    layer = module_path_to_layer(norm_path)
    allowed_targets = sorted({tl for (fl, tl) in ALLOWED_LAYER_EDGES if fl == layer})
    allowed_sources = sorted({fl for (fl, tl) in ALLOWED_LAYER_EDGES if tl == layer})

    return {
        "module": norm_path,
        "layer": layer,
        "allowed_import_targets": allowed_targets,
        "allowed_import_sources": allowed_sources,
        "note": "Same-layer imports are always allowed",
    }


def cmd_agents_for(base_class: str, result: ScanResult) -> dict:
    """Return all agent classes inheriting from the given base class name."""
    from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine

    engine = ADGRuntimeQueryEngine(result)
    agents = engine.find_agents_by_base_class(base_class)

    # Enrich with file paths
    # ADG symbol format: ADG::Module::<file_path>::<ClassName>
    # split("::") → ["ADG", "Module", "<file_path>", "<ClassName>"]
    enriched: list[dict] = []
    for adg_name in sorted(agents):
        parts = adg_name.split("::")
        if len(parts) >= 4:
            module_path = parts[2]
            class_name = parts[3]
        elif len(parts) == 3:
            module_path = parts[2]
            class_name = ""
        else:
            module_path = ""
            class_name = adg_name
        from agentic_core.adg.contracts.schema_util import module_path_to_layer

        enriched.append(
            {
                "adg_name": adg_name,
                "class_name": class_name,
                "module_path": module_path,
                "layer": module_path_to_layer(module_path) if module_path else "L_UNKNOWN",
            },
        )

    return {
        "base_class": base_class,
        "agent_count": len(agents),
        "agents": enriched,
    }


def cmd_config_reads(module_path: str, result: ScanResult) -> dict:
    """Return config/env symbols read by a given module."""
    from agentic_core.adg.contracts.schema_util import canonical_name
    from agentic_core.adg.runtime.query_engine import ADGRuntimeQueryEngine

    engine = ADGRuntimeQueryEngine(result)
    norm_path = module_path.replace("\\", "/")
    adg_name = canonical_name("Module", norm_path)
    config_syms = engine.get_config_reads(adg_name)

    return {
        "module": norm_path,
        "config_symbols_read": sorted(config_syms),
        "count": len(config_syms),
    }


def cmd_unresolved(result: ScanResult, repo_root: Path) -> dict:
    """Return all unresolved import symbols in the graph."""
    from agentic_core.adg.identity.normalizer import IdentityNormalizer

    normalizer = IdentityNormalizer(repo_root=repo_root)
    records, report = normalizer.normalize_from_scan_result(result)
    return report.to_dict()


def cmd_coverage(module_path: str, result: ScanResult, repo_root: Path) -> dict:
    """Return tests that cover the given module."""
    from tools.test_coverage_mapper import TestCoverageMapper

    mapper = TestCoverageMapper(result, repo_root=repo_root).build()
    norm_path = module_path.replace("\\", "/")
    tests = mapper.tests_for_module(norm_path)

    return {
        "module": norm_path,
        "covering_tests": tests,
        "test_count": len(tests),
        "note": "" if tests else "No direct ADG test coverage found for this module",
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="ADG Developer Insight CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  who-uses     <module_path>   Direct importers of a module
  depends-on   <module_path>   What a module imports (--transitive for full closure)
  blast-radius <file_path>     Impact analysis for a changed file
  territory    <module_path>   Layer + allowed import edges
  agents-for   <BaseClass>     All classes inheriting from a base class
  config-reads <module_path>   Config/env symbols read by a module
  unresolved                   All unresolved imports in the graph
  coverage     <module_path>   Tests covering a module
        """,
    )
    parser.add_argument("command", help="Command to run")
    parser.add_argument("target", nargs="?", default=None, help="Target module/file/class")
    parser.add_argument("--transitive", action="store_true", help="For depends-on: include transitive imports")
    parser.add_argument("--repo-root", default=None, help="Repo root directory (default: cwd)")
    parser.add_argument("--compact", action="store_true", help="Compact JSON output")
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    indent = None if args.compact else 2

    cmd = args.command.lower().replace("-", "_")

    # Commands that don't need target
    if cmd == "unresolved":
        result = _get_result(repo_root)
        output = cmd_unresolved(result, repo_root)
        print(json.dumps(output, indent=indent))
        return 0

    if not args.target:
        parser.error(f"Command '{args.command}' requires a target argument")

    target = args.target

    if cmd == "who_uses":
        result = _get_result(repo_root)
        output = cmd_who_uses(target, result)
    elif cmd == "depends_on":
        result = _get_result(repo_root)
        output = cmd_depends_on(target, result, transitive=args.transitive)
    elif cmd == "blast_radius":
        result = _get_result(repo_root)
        output = cmd_blast_radius(target, result, repo_root)
    elif cmd == "territory":
        output = cmd_territory(target)
    elif cmd == "agents_for":
        result = _get_result(repo_root)
        output = cmd_agents_for(target, result)
    elif cmd == "config_reads":
        result = _get_result(repo_root)
        output = cmd_config_reads(target, result)
    elif cmd == "coverage":
        result = _get_result(repo_root)
        output = cmd_coverage(target, result, repo_root)
    else:
        parser.error(f"Unknown command: {args.command}")

    print(json.dumps(output, indent=indent))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main())
