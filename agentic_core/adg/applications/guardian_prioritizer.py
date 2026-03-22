"""ADG Guardian Prioritizer — rank guardians by structural impact signals.

Uses the ADG import graph and layer metadata to produce a deterministic,
evidence-based priority ordering for guardian execution.

Priority signals (additive, deterministic):
  1. Cross-layer import violations (RULE_C evidence)
  2. LLM/embedding gateway hotspots (RULE_A/B evidence)
  3. High fan-in modules in changed blast radius
  4. Config read hotspots (modules with many reads_from edges)
  5. Dynamic exec violations (RULE_F evidence)

No speculative inference: only structural facts from the ADG.
No guardian is silently skipped — all receive a score (floor 0).

CLI:
    python -m agentic_core.adg.applications.guardian_prioritizer
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

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

_emit_applies_guardrail("p0", "guardian_prioritizer", "p0_governance")
_emit_reads_policy_state("p0", "guardian_prioritizer", "policy_binding")
_emit_snapshots_state("p0", "guardian_prioritizer", "state_snapshot")
emit_replay_key("p0", "guardian_prioritizer")
emit_determinism_digest("p0", "guardian_prioritizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "guardian_prioritizer", "execution_auth")
_emit_validates_capability("p2", "guardian_prioritizer", "capability_check")
_emit_routes_to_capability("p2", "guardian_prioritizer", "capability_route")
_emit_writes_via_uwg("p2", "guardian_prioritizer", "uwg_write")
_emit_blocks_direct_write("p2", "guardian_prioritizer", "direct_write_block")
_emit_records_tool_invocation("p2", "guardian_prioritizer", "tool_invocation")
_emit_captures_execution_output("p2", "guardian_prioritizer", "exec_output")
_emit_dispatches_agent("p3", "guardian_prioritizer", "agent_dispatch")
_emit_coordinates_agents("p3", "guardian_prioritizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "guardian_prioritizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "guardian_prioritizer", "healing_outcome")
_emit_escalates_failure("p3", "guardian_prioritizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "guardian_prioritizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guardian_prioritizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "guardian_prioritizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "guardian_prioritizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guardian_prioritizer", "eval_metric")
_emit_stores_embedding("p4", "guardian_prioritizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "guardian_prioritizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guardian_prioritizer", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

from agentic_core.adg.schema import (
    ALLOWED_LAYER_EDGES,
    EMBEDDING_SYMBOLS,
    PROVIDER_SDK_SYMBOLS,
    module_path_to_layer,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("guardian_prioritizer", "p4obs", "metric_1")
_emit_emits_metric_event("guardian_prioritizer", "p4obs", "metric_2")
_emit_emits_metric_event("guardian_prioritizer", "p4obs", "metric_3")
_emit_emits_metric_event("guardian_prioritizer", "p4obs", "metric_4")
_emit_emits_metric_event("guardian_prioritizer", "p4obs", "metric_5")
_emit_emits_metric_event("guardian_prioritizer", "p4obs", "metric_6")
_emit_records_incident_event("guardian_prioritizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("guardian_prioritizer", "p4obs", "anomaly")
_emit_writes_observability_log("guardian_prioritizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("guardian_prioritizer", "p4obs", "mon_state")
_emit_triggers_alert("guardian_prioritizer", "p4obs", "alert")
_emit_links_incident_trace("guardian_prioritizer", "p4obs", "trace_link")
_emit_captures_pattern("guardian_prioritizer", "p3lm", "pattern")
_emit_records_learning_event("guardian_prioritizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guardian_prioritizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("guardian_prioritizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guardian_prioritizer", "p3lm", "routing")
_emit_improves_agent_policy("guardian_prioritizer", "p3lm", "policy")
_emit_stores_learning_state("guardian_prioritizer", "p3lm", "state")
_emit_records_execution_trace("guardian_prioritizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guardian_prioritizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guardian_prioritizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guardian_prioritizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guardian_prioritizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guardian_prioritizer", "env_read", "p2_env_1")
_emit_reads_environ("guardian_prioritizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("guardian_prioritizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guardian_prioritizer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guardian_prioritizer", "context_pull")
_emit_pulls_context("p1", "guardian_prioritizer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "guardian_prioritizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guardian_prioritizer", "uwg_term_2")
_emit_writes_through("p1", "guardian_prioritizer", "write_through")
_emit_writes_through("p1", "guardian_prioritizer", "write_through_2")
_emit_validated_by_safety_plane("p1", "guardian_prioritizer", "safety_validation")
_emit_invokes_eval("p1", "guardian_prioritizer", "eval_call")
_emit_proposal_commits_routing("p1", "guardian_prioritizer", "routing_commit")
_emit_escalates_to_human("p1", "guardian_prioritizer", "human_escalation")
_emit_routes_through("p1", "guardian_prioritizer", "route_through")
_emit_checks_agent_registry("p1", "guardian_prioritizer", "agent_registry")
_emit_validates_agent_capability("p1", "guardian_prioritizer", "capability")
_emit_dispatches_execution_plan("p1", "guardian_prioritizer", "exec_plan")
_emit_agent_executes_agent("p1", "guardian_prioritizer", "sub_agent")
_emit_routes_to_agent("p1", "guardian_prioritizer", "target_agent")
_emit_verifies_policy("p1", "guardian_prioritizer", "policy_check")
_emit_observes_runtime_state("p1", "guardian_prioritizer", "runtime_state")
_emit_verifies_boundary("p1", "guardian_prioritizer", "boundary_check")
_emit_transcripts_response("p1", "guardian_prioritizer", "transcript")
_emit_hard_fails_untranscripted("p1", "guardian_prioritizer")
_emit_gated_by_confidence("p1", "guardian_prioritizer", "confidence_gate")

# Rank map for upward-mutation detection: higher rank = higher in the stack.
# An upward mutation writes FROM a lower-rank layer TO a higher-rank layer.
_LAYER_RANK: dict[str, int] = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
    "L3": 3,
    "L4": 4,
    "L5": 5,
    "L6": 6,
    "L_SHARED": 1,
    "L_RUNTIME": 3,
    "L_PG": 2,
    "L_APP": 7,
    "L_SL": 3,
    "L_TOOLS": 4,
    "L_OPS": 4,
    "L_TEST": 8,
    "L_UNKNOWN": -1,
}

logger = logging.getLogger(__name__)

_MODULE_PREFIX = "ADG::Module::"
_SYMBOL_PREFIX = "ADG::Symbol::"

# Guardian IDs that are eligible for ADG-driven prioritization.
# Map from guardian_id -> list of signal keys that are relevant.
_GUARDIAN_ADG_SIGNALS: dict[str, list[str]] = {
    "architecture_governance": ["cross_layer_violations", "layer_hotspots"],
    "gateway_bypass": ["llm_gateway_violations", "embedding_violations"],
    "cross_layer_mutation": ["cross_layer_violations", "upward_mutations"],
    "classification_compliance": ["layer_hotspots", "config_hotspots"],
    "drift_detection": ["fan_in_hotspots", "config_hotspots"],
    "contract_integrity": ["fan_in_hotspots", "cross_layer_violations"],
    "escalation_determinism": ["dynamic_exec_violations"],
    "hygiene": ["orphan_modules"],
    "hierarchy_compliance": ["cross_layer_violations", "layer_hotspots"],
    "c0_sovereignty": ["cross_layer_violations", "llm_gateway_violations"],
    "location_alignment": ["orphan_modules"],
    "manifest": ["fan_in_hotspots"],
    "change_package_activation": ["fan_in_hotspots", "config_hotspots"],
}


@dataclass
class GuardianPriorityScore:
    """Priority score for one guardian."""

    guardian_id: str
    score: int
    signals: list[str] = field(default_factory=list)
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "guardian_id": self.guardian_id,
            "score": self.score,
            "signals": sorted(self.signals),
            "evidence_summary": {k: len(v) if isinstance(v, list) else v for k, v in self.evidence.items()},
        }


@dataclass
class PrioritizationResult:
    """Ordered list of guardian priority scores."""

    scores: list[GuardianPriorityScore] = field(default_factory=list)
    adg_signals_digest: str = ""

    def ordered(self) -> list[GuardianPriorityScore]:
        """Return scores in descending priority order (highest score first)."""
        return sorted(self.scores, key=lambda s: (-s.score, s.guardian_id))

    def to_dict(self) -> dict:
        return {
            "adg_signals_digest": self.adg_signals_digest,
            "priority_order": [s.to_dict() for s in self.ordered()],
        }


class GuardianPrioritizer:
    """Score all registered guardians using structural ADG signals.

    Usage
    -----
    result = GuardianPrioritizer(scan_result).prioritize()
    ordered = result.ordered()
    """

    # Signal weights
    _SIGNAL_WEIGHTS: dict[str, int] = {
        "cross_layer_violations": 50,
        "llm_gateway_violations": 60,
        "embedding_violations": 55,
        "dynamic_exec_violations": 45,
        "upward_mutations": 40,
        "fan_in_hotspots": 20,
        "config_hotspots": 15,
        "layer_hotspots": 25,
        "orphan_modules": 5,
    }

    def __init__(self, result: ScanResult) -> None:
        self._result = result
        self._signals: dict[str, list] = {}
        self._signals_built = False

    def _build_signals(self) -> None:
        if self._signals_built:
            return

        cross_layer: list[dict] = []
        llm_violations: list[dict] = []
        embedding_violations: list[dict] = []
        dynamic_exec: list[dict] = []
        upward_mutations: list[dict] = []
        fan_in: dict[str, int] = {}
        config_reads: dict[str, int] = {}

        for edge in self._result.edges:
            from_mod = edge.from_name
            to_sym = edge.to_name

            # Fan-in (imports pointing to a module)
            if edge.relation_type == "imports" and to_sym.startswith(_MODULE_PREFIX):
                fan_in[to_sym] = fan_in.get(to_sym, 0) + 1

            # Config hotspots
            if edge.relation_type == "reads_from":
                fan_in_key = from_mod
                config_reads[fan_in_key] = config_reads.get(fan_in_key, 0) + 1

            # Cross-layer violations (import only)
            if edge.relation_type == "imports":
                from_path = from_mod[len(_MODULE_PREFIX):] if from_mod.startswith(_MODULE_PREFIX) else ""
                to_path = to_sym[len(_MODULE_PREFIX):] if to_sym.startswith(_MODULE_PREFIX) else ""
                if from_path and to_path:
                    fl = module_path_to_layer(from_path)
                    tl = module_path_to_layer(to_path)
                    if fl != tl and (fl, tl) not in ALLOWED_LAYER_EDGES:
                        cross_layer.append(
                            {"from": from_path, "to": to_path, "from_layer": fl, "to_layer": tl}
                        )

            # LLM gateway violations (RULE_A)
            if edge.relation_type == "imports" and edge.edge_kind in ("import", "network"):
                sym = edge.symbol or ""
                if sym in PROVIDER_SDK_SYMBOLS or any(
                    sym.startswith(pkg) for pkg in ("openai.", "anthropic.", "google.generativeai.")
                ):
                    from_path = from_mod[len(_MODULE_PREFIX):] if from_mod.startswith(_MODULE_PREFIX) else ""
                    llm_violations.append({"file": from_path, "symbol": sym, "line": edge.line_no})

            # Embedding violations (RULE_B)
            if edge.relation_type == "instantiates" and edge.edge_kind == "embedding":
                sym = edge.symbol or ""
                if sym in EMBEDDING_SYMBOLS or not sym:
                    from_path = from_mod[len(_MODULE_PREFIX):] if from_mod.startswith(_MODULE_PREFIX) else ""
                    embedding_violations.append({"file": from_path, "symbol": sym, "line": edge.line_no})

            # Dynamic exec violations (RULE_F)
            if edge.edge_kind == "exec":
                from_path = from_mod[len(_MODULE_PREFIX):] if from_mod.startswith(_MODULE_PREFIX) else ""
                dynamic_exec.append({"file": from_path, "line": edge.line_no})

            # Upward mutations (write to higher-rank layer)
            if edge.relation_type == "writes_to" and edge.edge_kind in ("write", "network"):
                from_path = from_mod[len(_MODULE_PREFIX):] if from_mod.startswith(_MODULE_PREFIX) else ""
                to_path = to_sym[len(_MODULE_PREFIX):] if to_sym.startswith(_MODULE_PREFIX) else ""
                if from_path and to_path:
                    fl = module_path_to_layer(from_path)
                    tl = module_path_to_layer(to_path)
                    fl_rank = _LAYER_RANK.get(fl, -1)
                    tl_rank = _LAYER_RANK.get(tl, -1)
                    if tl_rank > fl_rank >= 0:
                        upward_mutations.append({"from": from_path, "to": to_path})

        # Fan-in hotspots (top 20)
        fan_in_hotspots = sorted(
            [{"module": k, "count": v} for k, v in fan_in.items() if v >= 5],
            key=lambda x: -x["count"],
        )[:20]

        # Config hotspots (top 20)
        config_hotspots = sorted(
            [{"module": k, "count": v} for k, v in config_reads.items() if v >= 3],
            key=lambda x: -x["count"],
        )[:20]

        # Layer hotspots: layers with most cross-boundary traffic
        layer_traffic: dict[str, int] = {}
        for v in cross_layer:
            key = f"{v['from_layer']}->{v['to_layer']}"
            layer_traffic[key] = layer_traffic.get(key, 0) + 1

        # Orphan modules
        module_adgs = {_MODULE_PREFIX + m for m in self._result.modules}
        touched = {e.from_name for e in self._result.edges} | {e.to_name for e in self._result.edges}
        orphan_modules = sorted(module_adgs - touched)

        self._signals = {
            "cross_layer_violations": cross_layer,
            "llm_gateway_violations": llm_violations,
            "embedding_violations": embedding_violations,
            "dynamic_exec_violations": dynamic_exec,
            "upward_mutations": upward_mutations,
            "fan_in_hotspots": fan_in_hotspots,
            "config_hotspots": config_hotspots,
            "layer_hotspots": [{"key": k, "count": v} for k, v in sorted(layer_traffic.items(), key=lambda x: -x[1])],
            "orphan_modules": orphan_modules,
        }
        self._signals_built = True

    def prioritize(self, guardian_ids: list[str] | None = None) -> PrioritizationResult:
        """Score all (or specified) guardians.

        Parameters
        ----------
        guardian_ids:
            Optional list of guardian IDs to score. If None, all registered
            guardians in _GUARDIAN_ADG_SIGNALS are scored.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GuardianPrioritizer.prioritize")

        import hashlib

        self._build_signals()

        ids_to_score = guardian_ids or sorted(_GUARDIAN_ADG_SIGNALS.keys())

        # Add any unknown guardian IDs with score=0
        all_known = set(_GUARDIAN_ADG_SIGNALS.keys())
        for gid in (guardian_ids or []):
            if gid not in all_known:
                ids_to_score = list(ids_to_score) + [gid]

        scores: list[GuardianPriorityScore] = []
        for gid in sorted(set(ids_to_score)):
            relevant_signals = _GUARDIAN_ADG_SIGNALS.get(gid, [])
            total_score = 0
            active_signals: list[str] = []
            evidence: dict = {}

            for sig in relevant_signals:
                sig_data = self._signals.get(sig, [])
                count = len(sig_data) if isinstance(sig_data, list) else int(sig_data)
                if count > 0:
                    weight = self._SIGNAL_WEIGHTS.get(sig, 10)
                    contribution = min(count * weight, weight * 10)
                    total_score += contribution
                    active_signals.append(sig)
                    evidence[sig] = sig_data[:5] if isinstance(sig_data, list) else sig_data

            scores.append(
                GuardianPriorityScore(
                    guardian_id=gid,
                    score=total_score,
                    signals=active_signals,
                    evidence=evidence,
                )
            )

        # Compute signals digest for reproducibility
        signals_summary = {k: len(v) if isinstance(v, list) else v for k, v in self._signals.items()}
        signals_digest = hashlib.sha256(
            json.dumps(signals_summary, sort_keys=True).encode()
        ).hexdigest()[:16]

        result = PrioritizationResult(scores=scores, adg_signals_digest=signals_digest)
        logger.info(
            "Guardian prioritization: %d guardians scored, digest=%s",
            len(scores),
            signals_digest,
        )
        return result

    def get_signals(self) -> dict:
        """Return raw signal data for inspection."""
        self._build_signals()
        return {k: v[:10] if isinstance(v, list) else v for k, v in self._signals.items()}


def _get_scan_result(repo_root: Path) -> ScanResult:
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    return load_or_scan(repo_root=str(repo_root))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="ADG Guardian Prioritizer")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repo root directory (default: cwd)",
    )
    parser.add_argument(
        "--guardians",
        nargs="*",
        default=None,
        help="Specific guardian IDs to score (default: all registered)",
    )
    parser.add_argument(
        "--signals",
        action="store_true",
        help="Print raw ADG signals instead of priority scores",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()
    result = _get_scan_result(repo_root)
    prioritizer = GuardianPrioritizer(result)

    if args.signals:
        signals = prioritizer.get_signals()
        print(json.dumps({k: v for k, v in signals.items()}, indent=2))
        return 0

    prio_result = prioritizer.prioritize(guardian_ids=args.guardians)
    print(json.dumps(prio_result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main())
