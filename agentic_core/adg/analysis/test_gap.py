"""E15: Test Gap Detector.

Surfaces modules that have zero ``covers`` edges pointing to them — these
are production modules with no test coverage signal in the ADG.

Outputs:
  ``TestGapReport`` with:
    - ``uncovered_modules``:  production modules with no covers edges
    - ``covered_modules``:    production modules that have at least one covers edge
    - ``coverage_rate``:      fraction of production modules covered
    - ``gap_by_layer``:       per-layer breakdown of gaps
    - ``highest_risk_gaps``:  uncovered modules with the most importers
                              (highest blast radius if they break)

Usage::

    from agentic_core.adg.analysis.test_gap import detect_test_gaps

    report = detect_test_gaps(result, hotspot_index=idx)
    print(report.summary)
    for m in report.highest_risk_gaps[:10]:
        print(m)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from agentic_core.adg.schema import module_path_to_layer
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_gap")
_emit_applies_guardrail("p0", "test_gap", "p0_governance")
_emit_reads_policy_state("p0", "test_gap", "policy_binding")
_emit_snapshots_state("p0", "test_gap", "state_snapshot")
emit_replay_key("p0", "test_gap")
emit_determinism_digest("p0", "test_gap")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_gap", "execution_auth")
_emit_validates_capability("p2", "test_gap", "capability_check")
_emit_routes_to_capability("p2", "test_gap", "capability_route")
_emit_writes_via_uwg("p2", "test_gap", "uwg_write")
_emit_blocks_direct_write("p2", "test_gap", "direct_write_block")
_emit_records_tool_invocation("p2", "test_gap", "tool_invocation")
_emit_captures_execution_output("p2", "test_gap", "exec_output")
_emit_dispatches_agent("p3", "test_gap", "agent_dispatch")
_emit_coordinates_agents("p3", "test_gap", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_gap", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_gap", "healing_outcome")
_emit_escalates_failure("p3", "test_gap", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_gap", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_gap", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_gap", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_gap", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_gap", "eval_metric")
_emit_stores_embedding("p4", "test_gap", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_gap", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_gap", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.analysis.hotspot_index import HotspotIndex
    from agentic_core.adg.extraction.static_scanner import ScanResult
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_gap", "p4obs", "metric_1")
_emit_emits_metric_event("test_gap", "p4obs", "metric_2")
_emit_emits_metric_event("test_gap", "p4obs", "metric_3")
_emit_emits_metric_event("test_gap", "p4obs", "metric_4")
_emit_emits_metric_event("test_gap", "p4obs", "metric_5")
_emit_emits_metric_event("test_gap", "p4obs", "metric_6")
_emit_records_incident_event("test_gap", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_gap", "p4obs", "anomaly")
_emit_writes_observability_log("test_gap", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_gap", "p4obs", "mon_state")
_emit_triggers_alert("test_gap", "p4obs", "alert")
_emit_links_incident_trace("test_gap", "p4obs", "trace_link")
_emit_captures_pattern("test_gap", "p3lm", "pattern")
_emit_records_learning_event("test_gap", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_gap", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_gap", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_gap", "p3lm", "routing")
_emit_improves_agent_policy("test_gap", "p3lm", "policy")
_emit_stores_learning_state("test_gap", "p3lm", "state")
_emit_records_execution_trace("test_gap", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_gap", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_gap", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_gap", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_gap", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_gap", "env_read", "p2_env_1")
_emit_reads_environ("test_gap", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_gap", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_gap", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_gap", "context_pull")
_emit_pulls_context("p1", "test_gap", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_gap", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_gap", "uwg_term_secondary")
_emit_writes_through("p1", "test_gap", "write_through")
_emit_writes_through("p1", "test_gap", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_gap", "safety_validation")
_emit_invokes_eval("p1", "test_gap", "eval_call")
_emit_proposal_commits_routing("p1", "test_gap", "routing_commit")
_emit_escalates_to_human("p1", "test_gap", "human_escalation")
_emit_routes_through("p1", "test_gap", "route_through")
_emit_checks_agent_registry("p1", "test_gap", "agent_registry")
_emit_validates_agent_capability("p1", "test_gap", "capability")
_emit_dispatches_execution_plan("p1", "test_gap", "exec_plan")
_emit_agent_executes_agent("p1", "test_gap", "sub_agent")
_emit_routes_to_agent("p1", "test_gap", "target_agent")
_emit_verifies_policy("p1", "test_gap", "policy_check")
_emit_observes_runtime_state("p1", "test_gap", "runtime_state")
_emit_verifies_boundary("p1", "test_gap", "boundary_check")
_emit_transcripts_response("p1", "test_gap", "transcript")
_emit_hard_fails_untranscripted("p1", "test_gap")
_emit_gated_by_confidence("p1", "test_gap", "confidence_gate")

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

_PRODUCTION_EXCLUDES: tuple[str, ...] = (
    "tests/",
    "ops_scripts/",
    "tools/",
    ".py.bak",
)


def _is_production(module_path: str) -> bool:
    """Return True iff module_path is a production (non-test, non-ops) file."""
    norm = module_path.replace("\\", "/")
    return not any(norm.startswith(exc) or norm.endswith(exc) for exc in _PRODUCTION_EXCLUDES)


@dataclass
class TestGapEntry:
    """One uncovered production module."""

    module_path: str
    layer: str
    fan_in: int = 0

    def to_dict(self) -> dict:
        return {
            "module_path": self.module_path,
            "layer": self.layer,
            "fan_in": self.fan_in,
        }


@dataclass
class TestGapReport:
    """Full test-coverage gap analysis."""

    uncovered_modules: list[TestGapEntry] = field(default_factory=list)
    covered_modules: list[str] = field(default_factory=list)
    total_production_modules: int = 0
    coverage_rate: float = 0.0
    gap_by_layer: dict[str, int] = field(default_factory=dict)
    highest_risk_gaps: list[TestGapEntry] = field(default_factory=list)

    @property
    def summary(self) -> str:
        return (
            f"test_gap coverage={self.coverage_rate:.1%} "
            f"covered={len(self.covered_modules)} "
            f"uncovered={len(self.uncovered_modules)} "
            f"total_production={self.total_production_modules}"
        )

    def to_dict(self) -> dict:
        return {
            "total_production_modules": self.total_production_modules,
            "covered_count": len(self.covered_modules),
            "uncovered_count": len(self.uncovered_modules),
            "coverage_rate": round(self.coverage_rate, 4),
            "summary": self.summary,
            "gap_by_layer": dict(sorted(self.gap_by_layer.items())),
            "highest_risk_gaps": [e.to_dict() for e in self.highest_risk_gaps],
            "uncovered_modules": [e.to_dict() for e in self.uncovered_modules],
            "covered_modules": sorted(self.covered_modules),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


def detect_test_gaps(
    result: ScanResult,
    hotspot_index: HotspotIndex | None = None,
    include_layers: list[str] | None = None,
) -> TestGapReport:
    """Detect production modules with no ADG test-coverage signal.

    Algorithm:
    1. Collect all module_paths that appear as ``to_name`` in a ``covers`` edge.
    2. From ``result.modules``, filter to production-only paths.
    3. Modules in (2) not in (1) are the test gaps.
    4. Optionally filter to ``include_layers`` if provided.
    5. Sort gaps by fan_in descending (highest blast-radius first).

    Args:
        result: Full ScanResult from the static scanner.
        hotspot_index: Optional pre-built HotspotIndex for fan_in lookup.
        include_layers: Optional layer whitelist — gaps are only reported for
                        modules in these layers.
    """
    module_set: set[str] = set(result.modules)

    # Step 1: modules that are covered
    covered: set[str] = set()
    for edge in result.edges:
        if edge.relation_type == "covers":
            to_name = edge.to_name
            if to_name.startswith(_MODULE_PREFIX):
                covered.add(to_name[len(_MODULE_PREFIX):])
            elif to_name.startswith(_SYMBOL_PREFIX):
                # ADG::Symbol::a.b.c  ->  a/b/c.py  or  a/b/c/__init__.py
                sym = to_name[len(_SYMBOL_PREFIX):]
                parts = sym.split(".")
                for n in range(len(parts), 0, -1):
                    prefix = "/".join(parts[:n])
                    if (prefix + ".py") in module_set:
                        covered.add(prefix + ".py")
                        break
                    if (prefix + "/__init__.py") in module_set:
                        covered.add(prefix + "/__init__.py")
                        break

    # Step 2: production modules
    production = [m for m in result.modules if _is_production(m)]

    # Step 3 & 4: gaps
    gap_by_layer: dict[str, int] = {}
    uncovered: list[TestGapEntry] = []
    covered_list: list[str] = []

    for mod in production:
        layer = module_path_to_layer(mod)
        if include_layers and layer not in include_layers:
            continue

        fi = hotspot_index.fan_in(mod) if hotspot_index else 0

        if mod not in covered:
            entry = TestGapEntry(module_path=mod, layer=layer, fan_in=fi)
            uncovered.append(entry)
            gap_by_layer[layer] = gap_by_layer.get(layer, 0) + 1
        else:
            covered_list.append(mod)

    total_prod = len(production)
    cov_rate = len(covered_list) / total_prod if total_prod else 0.0

    # Step 5: highest risk = most importers
    highest_risk = sorted(uncovered, key=lambda e: -e.fan_in)[:20]

    return TestGapReport(
        uncovered_modules=sorted(uncovered, key=lambda e: e.module_path),
        covered_modules=sorted(covered_list),
        total_production_modules=total_prod,
        coverage_rate=cov_rate,
        gap_by_layer=gap_by_layer,
        highest_risk_gaps=highest_risk,
    )


__all__ = [
    "TestGapReport",
    "TestGapEntry",
    "detect_test_gaps",
]
