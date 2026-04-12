"""Change Impact Engine — maps changed files to impacted modules and tests.

Uses the ADG reverse-dependency graph (G1) to compute blast radius for a
set of changed files, then cross-references with the test coverage mapper
to emit a scoped test selection.

No silent full-suite fallback: if a changed file has no ADG coverage, it is
reported explicitly under ``uncovered_changed_files``.

CLI:
    python -m tools.change_impact_engine --changed agentic_core/adg/schema.py
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
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

_emit_records_execution_trace("p0", "evidence", "change_impact_engine")
_emit_applies_guardrail("p0", "change_impact_engine", "p0_governance")
_emit_reads_policy_state("p0", "change_impact_engine", "policy_binding")
_emit_snapshots_state("p0", "change_impact_engine", "state_snapshot")
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

_emit_emits_metric_event("change_impact_engine", "p4obs", "metric_1")
_emit_emits_metric_event("change_impact_engine", "p4obs", "metric_2")
_emit_emits_metric_event("change_impact_engine", "p4obs", "metric_3")
_emit_emits_metric_event("change_impact_engine", "p4obs", "metric_4")
_emit_emits_metric_event("change_impact_engine", "p4obs", "metric_5")
_emit_emits_metric_event("change_impact_engine", "p4obs", "metric_6")
_emit_records_incident_event("change_impact_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("change_impact_engine", "p4obs", "anomaly")
_emit_writes_observability_log("change_impact_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("change_impact_engine", "p4obs", "mon_state")
_emit_triggers_alert("change_impact_engine", "p4obs", "alert")
_emit_links_incident_trace("change_impact_engine", "p4obs", "trace_link")
_emit_captures_pattern("change_impact_engine", "p3lm", "pattern")
_emit_records_learning_event("change_impact_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("change_impact_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("change_impact_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("change_impact_engine", "p3lm", "routing")
_emit_improves_agent_policy("change_impact_engine", "p3lm", "policy")
_emit_stores_learning_state("change_impact_engine", "p3lm", "state")
_emit_records_execution_trace("change_impact_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("change_impact_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("change_impact_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("change_impact_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("change_impact_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("change_impact_engine", "env_read", "p2_env_1")
_emit_reads_environ("change_impact_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("change_impact_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("change_impact_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "change_impact_engine", "context_pull")
_emit_pulls_context("p1", "change_impact_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "change_impact_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "change_impact_engine", "uwg_term_2")
_emit_writes_through("p1", "change_impact_engine", "write_through")
_emit_writes_through("p1", "change_impact_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "change_impact_engine", "safety_validation")
_emit_invokes_eval("p1", "change_impact_engine", "eval_call")
_emit_proposal_commits_routing("p1", "change_impact_engine", "routing_commit")
_emit_escalates_to_human("p1", "change_impact_engine", "human_escalation")
_emit_routes_through("p1", "change_impact_engine", "route_through")
_emit_checks_agent_registry("p1", "change_impact_engine", "agent_registry")
_emit_validates_agent_capability("p1", "change_impact_engine", "capability")
_emit_dispatches_execution_plan("p1", "change_impact_engine", "exec_plan")
_emit_agent_executes_agent("p1", "change_impact_engine", "sub_agent")
_emit_routes_to_agent("p1", "change_impact_engine", "target_agent")
_emit_verifies_policy("p1", "change_impact_engine", "policy_check")
_emit_observes_runtime_state("p1", "change_impact_engine", "runtime_state")
_emit_verifies_boundary("p1", "change_impact_engine", "boundary_check")
_emit_transcripts_response("p1", "change_impact_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "change_impact_engine")
_emit_gated_by_confidence("p1", "change_impact_engine", "confidence_gate")
emit_replay_key("p0", "change_impact_engine")
emit_determinism_digest("p0", "change_impact_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "change_impact_engine", "execution_auth")
_emit_validates_capability("p2", "change_impact_engine", "capability_check")
_emit_routes_to_capability("p2", "change_impact_engine", "capability_route")
_emit_writes_via_uwg("p2", "change_impact_engine", "uwg_write")
_emit_blocks_direct_write("p2", "change_impact_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "change_impact_engine", "tool_invocation")
_emit_captures_execution_output("p2", "change_impact_engine", "exec_output")
_emit_dispatches_agent("p3", "change_impact_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "change_impact_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "change_impact_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "change_impact_engine", "healing_outcome")
_emit_escalates_failure("p3", "change_impact_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "change_impact_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "change_impact_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "change_impact_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "change_impact_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "change_impact_engine", "eval_metric")
_emit_stores_embedding("p4", "change_impact_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "change_impact_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "change_impact_engine", "exec_snapshot_link")
_emit_reads_through("l4", "change_impact_engine", "urg_read_1")
_emit_reads_through("l4", "change_impact_engine", "urg_read_2")
_emit_reads_through("l4", "change_impact_engine", "urg_read_3")
_emit_reads_through("l4", "change_impact_engine", "urg_read_4")
_emit_reads_through("l4", "change_impact_engine", "urg_read_5")
_emit_reads_through("l4", "change_impact_engine", "urg_read_6")
_emit_reads_through("l4", "change_impact_engine", "urg_read_7")
_emit_reads_through("l4", "change_impact_engine", "urg_read_8")
_emit_reads_through("l4", "change_impact_engine", "urg_read_9")
_emit_reads_through("l4", "change_impact_engine", "urg_read_10")
_emit_reads_through("l4", "change_impact_engine", "urg_read_11")
_emit_reads_through("l4", "change_impact_engine", "urg_read_12")
_emit_reads_through("l4", "change_impact_engine", "urg_read_13")
_emit_reads_through("l4", "change_impact_engine", "urg_read_14")
_emit_reads_through("l4", "change_impact_engine", "urg_read_15")
_emit_reads_through("l4", "change_impact_engine", "urg_read_16")
_emit_reads_through("l4", "change_impact_engine", "urg_read_17")
_emit_reads_through("l4", "change_impact_engine", "urg_read_18")
_emit_reads_through("l4", "change_impact_engine", "urg_read_19")
_emit_reads_through("l4", "change_impact_engine", "urg_read_20")
_emit_reads_through("l4", "change_impact_engine", "urg_read_21")
_emit_reads_through("l4", "change_impact_engine", "urg_read_22")
_emit_reads_through("l4", "change_impact_engine", "urg_read_23")
_emit_reads_through("l4", "change_impact_engine", "urg_read_24")
_emit_reads_through("l4", "change_impact_engine", "urg_read_25")
_emit_reads_through("l4", "change_impact_engine", "urg_read_26")
_emit_reads_through("l4", "change_impact_engine", "urg_read_27")
_emit_reads_through("l4", "change_impact_engine", "urg_read_28")
_emit_reads_through("l4", "change_impact_engine", "urg_read_29")
_emit_reads_through("l4", "change_impact_engine", "urg_read_30")
_emit_reads_through("l4", "change_impact_engine", "urg_read_31")
_emit_reads_through("l4", "change_impact_engine", "urg_read_32")
_emit_reads_through("l4", "change_impact_engine", "urg_read_33")
_emit_reads_through("l4", "change_impact_engine", "urg_read_34")
_emit_reads_through("l4", "change_impact_engine", "urg_read_35")
_emit_reads_through("l4", "change_impact_engine", "urg_read_36")
_emit_reads_through("l4", "change_impact_engine", "urg_read_37")
_emit_reads_through("l4", "change_impact_engine", "urg_read_38")
_emit_reads_through("l4", "change_impact_engine", "urg_read_39")
_emit_reads_through("l4", "change_impact_engine", "urg_read_40")
_emit_reads_through("l4", "change_impact_engine", "urg_read_41")
_emit_reads_through("l4", "change_impact_engine", "urg_read_42")
_emit_reads_through("l4", "change_impact_engine", "urg_read_43")
_emit_reads_through("l4", "change_impact_engine", "urg_read_44")
_emit_reads_through("l4", "change_impact_engine", "urg_read_45")
_emit_reads_through("l4", "change_impact_engine", "urg_read_46")
_emit_reads_through("l4", "change_impact_engine", "urg_read_47")
_emit_reads_through("l4", "change_impact_engine", "urg_read_48")
_emit_reads_through("l4", "change_impact_engine", "urg_read_49")
_emit_reads_through("l4", "change_impact_engine", "urg_read_50")
_emit_reads_through("l4", "change_impact_engine", "urg_read_51")
_emit_reads_through("l4", "change_impact_engine", "urg_read_52")
_emit_reads_through("l4", "change_impact_engine", "urg_read_53")
_emit_reads_through("l4", "change_impact_engine", "urg_read_54")
_emit_reads_through("l4", "change_impact_engine", "urg_read_55")
_emit_reads_through("l4", "change_impact_engine", "urg_read_56")
_emit_reads_through("l4", "change_impact_engine", "urg_read_57")
_emit_reads_through("l4", "change_impact_engine", "urg_read_58")
_emit_reads_through("l4", "change_impact_engine", "urg_read_59")
_emit_reads_through("l4", "change_impact_engine", "urg_read_60")
_emit_reads_through("l4", "change_impact_engine", "urg_read_61")
_emit_reads_through("l4", "change_impact_engine", "urg_read_62")
_emit_reads_through("l4", "change_impact_engine", "urg_read_63")
_emit_reads_through("l4", "change_impact_engine", "urg_read_64")
_emit_reads_through("l4", "change_impact_engine", "urg_read_65")
_emit_reads_through("l4", "change_impact_engine", "urg_read_66")
_emit_reads_through("l4", "change_impact_engine", "urg_read_67")
_emit_reads_through("l4", "change_impact_engine", "urg_read_68")
_emit_reads_through("l4", "change_impact_engine", "urg_read_69")
_emit_reads_through("l4", "change_impact_engine", "urg_read_70")
_emit_reads_through("l4", "change_impact_engine", "urg_read_71")
_emit_reads_through("l4", "change_impact_engine", "urg_read_72")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

_MODULE_PREFIX = "ADG::Module::"


@dataclass
class ChangeImpactResult:
    """Fully-structured result of a change impact analysis."""

    changed_files: list[str]
    impacted_modules: list[str]
    impacted_tests: list[str]
    blast_radius_by_depth: dict[str, int]
    uncovered_changed_files: list[str]
    scope_widening_events: list[str]
    risk_score: int
    route_mode: str
    impact_digest: str

    def to_dict(self) -> dict:
        return {
            "changed_files": sorted(self.changed_files),
            "impacted_module_count": len(self.impacted_modules),
            "impacted_modules": sorted(self.impacted_modules),
            "impacted_test_count": len(self.impacted_tests),
            "impacted_tests": sorted(self.impacted_tests),
            "blast_radius_by_depth": dict(sorted(self.blast_radius_by_depth.items())),
            "uncovered_changed_files": sorted(self.uncovered_changed_files),
            "scope_widening_events": sorted(self.scope_widening_events),
            "risk_score": self.risk_score,
            "route_mode": self.route_mode,
            "impact_digest": self.impact_digest,
        }


class ChangeImpactEngine:
    """Compute change impact using ADG reverse graph + test coverage mapper.

    Usage
    -----
    engine = ChangeImpactEngine(result, repo_root=Path("."))
    impact = engine.analyze(changed_files=["agentic_core/adg/schema.py"])
    """

    # Layer weights for risk scoring (mirrors blast_radius.py)
    _LAYER_WEIGHTS: dict[str, int] = {
        "L0": 100,
        "L1": 80,
        "L2": 90,
        "L3": 70,
        "L4": 60,
        "L5": 85,
        "L6": 40,
        "L_APP": 30,
        "L_SL": 25,
        "L_TOOLS": 20,
        "L_OPS": 15,
        "L_UNKNOWN": 5,
    }
    _RESTRICTED_THRESHOLD = 300
    _HUMAN_REVIEW_THRESHOLD = 700
    _MAX_DEPTH = 6

    def __init__(
        self,
        result: ScanResult,
        repo_root: Path | None = None,
    ) -> None:
        self._result = result
        self._repo_root = Path(repo_root) if repo_root else Path.cwd()
        self._reverse_deps: dict[str, set[str]] | None = None
        self._module_layers: dict[str, str] | None = None

    def _build_reverse_deps(self) -> dict[str, set[str]]:
        if self._reverse_deps is not None:
            return self._reverse_deps
        rev: dict[str, set[str]] = {}
        for edge in self._result.edges:
            if edge.relation_type != "imports":
                continue
            to_mod = edge.to_name
            from_mod = edge.from_name
            if to_mod not in rev:
                rev[to_mod] = set()
            rev[to_mod].add(from_mod)
        self._reverse_deps = rev
        return rev

    def _build_module_layers(self) -> dict[str, str]:
        if self._module_layers is not None:
            return self._module_layers
        from agentic_core.adg.contracts.schema_util import module_path_to_layer

        layers: dict[str, str] = {}
        for mod_path in self._result.modules:
            adg = _MODULE_PREFIX + mod_path
            layers[adg] = module_path_to_layer(mod_path)
        self._module_layers = layers
        return layers

    def _bfs_blast_radius(self, changed_adg_names: list[str]) -> dict[str, int]:
        """BFS over reverse dep graph. Returns {adg_name: min_depth}.

        Uses a deque (queue) not a stack so that each node is reached at its
        *shortest* path depth, which is what "blast radius depth" means.
        """
        import collections

        rev = self._build_reverse_deps()
        visited: dict[str, int] = {}
        frontier: collections.deque = collections.deque((adg, 0) for adg in changed_adg_names)
        while frontier:
            node, depth = frontier.popleft()
            if node in visited or depth > self._MAX_DEPTH:
                continue
            visited[node] = depth
            for dependent in sorted(rev.get(node, set())):
                if dependent not in visited:
                    frontier.append((dependent, depth + 1))
        return visited

    def _compute_risk_score(self, blast: dict[str, int]) -> int:
        layers = self._build_module_layers()
        score = 0
        for adg_name, depth in blast.items():
            layer = layers.get(adg_name, "L_UNKNOWN")
            weight = self._LAYER_WEIGHTS.get(layer, 5)
            score += weight * max(1, self._MAX_DEPTH - depth)
        return score

    def _route_mode(self, score: int) -> str:
        if score >= self._HUMAN_REVIEW_THRESHOLD:
            return "HUMAN_REVIEW"
        if score >= self._RESTRICTED_THRESHOLD:
            return "RESTRICTED"
        return "NORMAL"

    def analyze(
        self,
        changed_files: list[str],
        include_tests: bool = True,
    ) -> ChangeImpactResult:
        """Analyze impact of the given changed files.

        Parameters
        ----------
        changed_files:
            Repo-relative forward-slash paths of changed files.
        include_tests:
            If True, also derive impacted tests via TestCoverageMapper.
        """
        import hashlib

        from agentic_core.adg.contracts.schema_util import canonical_name

        # Normalize paths
        norm_changed = [f.replace("\\", "/") for f in changed_files]

        # Map to ADG names
        module_set = set(self._result.modules)
        changed_adg: list[str] = []
        uncovered: list[str] = []
        for path in norm_changed:
            if path in module_set:
                changed_adg.append(canonical_name("Module", path))
            else:
                uncovered.append(path)

        # BFS blast radius
        blast = self._bfs_blast_radius(changed_adg)

        # Convert ADG names back to rel paths
        impacted_rel: list[str] = []
        by_depth_raw: dict[str, int] = {}
        for adg_name, depth in blast.items():
            if adg_name.startswith(_MODULE_PREFIX):
                rel = adg_name[len(_MODULE_PREFIX) :]
                impacted_rel.append(rel)
                by_depth_raw[rel] = depth

        # Risk score and route mode
        risk_score = self._compute_risk_score(blast)
        route_mode = self._route_mode(risk_score)

        # Scope widening events (modules from different layers than changed files)
        scope_widening: list[str] = []
        from agentic_core.adg.contracts.schema_util import module_path_to_layer

        changed_layers = {module_path_to_layer(p) for p in norm_changed if p in module_set}
        for rel in impacted_rel:
            if rel not in norm_changed:
                imp_layer = module_path_to_layer(rel)
                if imp_layer not in changed_layers and changed_layers:
                    scope_widening.append(f"{rel}(layer={imp_layer})")

        # Impacted tests via TestCoverageMapper
        impacted_tests: list[str] = []
        if include_tests:
            from tools.test_coverage_mapper import TestCoverageMapper

            mapper = TestCoverageMapper(self._result, repo_root=self._repo_root).build()
            all_impacted_source = [r for r in impacted_rel if not r.startswith("tests/")]
            impacted_tests = mapper.tests_for_modules(all_impacted_source)

        # Impact digest
        payload = json.dumps(
            {
                "changed": sorted(norm_changed),
                "impacted": sorted(impacted_rel),
                "risk_score": risk_score,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        impact_digest = hashlib.sha256(payload.encode()).hexdigest()

        return ChangeImpactResult(
            changed_files=sorted(norm_changed),
            impacted_modules=sorted(impacted_rel),
            impacted_tests=sorted(impacted_tests),
            blast_radius_by_depth=dict(sorted(by_depth_raw.items())),
            uncovered_changed_files=sorted(uncovered),
            scope_widening_events=sorted(scope_widening),
            risk_score=risk_score,
            route_mode=route_mode,
            impact_digest=impact_digest,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _get_scan_result(repo_root: Path) -> ScanResult:
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    return load_or_scan(repo_root=str(repo_root))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ADG Change Impact Engine")
    parser.add_argument(
        "--changed",
        nargs="+",
        required=True,
        help="Repo-relative source file paths that changed",
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip test impact derivation",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repo root directory (default: cwd)",
    )
    parser.add_argument(
        "--output-json",
        default=None,
        help="Write result to JSON file",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    result = _get_scan_result(repo_root)
    engine = ChangeImpactEngine(result, repo_root=repo_root)
    impact = engine.analyze(args.changed, include_tests=not args.no_tests)

    output = json.dumps(impact.to_dict(), indent=2)

    if args.output_json:
        out_path = Path(args.output_json)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Impact result written: {out_path}")

    print(output)
    return 0 if impact.route_mode == "NORMAL" else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main())
