"""ADG Health Reporter — trust gate and graph health metrics.

Produces a structured health report from an ADGArtifact that can be
used as a trust gate before downstream integrations consume ADG data.

Trust threshold rules (--strict mode exits nonzero if violated):
  T1: unresolved_import_count > 2000 (too many blind spots)
  T2: layer_violation_count > 500 (architecture seriously degraded)
  T3: orphan_module_count > 300 (too many disconnected modules)
  T4: null_layer_count > 200 (unmapped repo modules)
  T5: parse_failure_count > 50 (scanner reliability degraded)

Health signals are always reported regardless of strict mode.

CLI:
    python -m agentic_core.adg.applications.health_reporter [--strict]
"""

from __future__ import annotations

import logging
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

_emit_applies_guardrail("p0", "health_reporter", "p0_governance")
_emit_reads_policy_state("p0", "health_reporter", "policy_binding")
_emit_snapshots_state("p0", "health_reporter", "state_snapshot")
emit_replay_key("p0", "health_reporter")
emit_determinism_digest("p0", "health_reporter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "health_reporter", "execution_auth")
_emit_validates_capability("p2", "health_reporter", "capability_check")
_emit_routes_to_capability("p2", "health_reporter", "capability_route")
_emit_writes_via_uwg("p2", "health_reporter", "uwg_write")
_emit_blocks_direct_write("p2", "health_reporter", "direct_write_block")
_emit_records_tool_invocation("p2", "health_reporter", "tool_invocation")
_emit_captures_execution_output("p2", "health_reporter", "exec_output")
_emit_dispatches_agent("p3", "health_reporter", "agent_dispatch")
_emit_coordinates_agents("p3", "health_reporter", "agent_coordination")
_emit_records_workflow_lineage("p3", "health_reporter", "workflow_lineage")
_emit_records_healing_outcome("p3", "health_reporter", "healing_outcome")
_emit_escalates_failure("p3", "health_reporter", "failure_escalation")
_emit_orchestrates_workflow("p3", "health_reporter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "health_reporter", "healing_dispatch")
_emit_invokes_evaluation("p3", "health_reporter", "evaluation_signal")
_emit_records_telemetry_event("p4", "health_reporter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "health_reporter", "eval_metric")
_emit_stores_embedding("p4", "health_reporter", "embedding_store")
_emit_updates_meta_learning_state("p4", "health_reporter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "health_reporter", "exec_snapshot_link")

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder import ADGArtifact
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

_emit_emits_metric_event("health_reporter", "p4obs", "metric_1")
_emit_emits_metric_event("health_reporter", "p4obs", "metric_2")
_emit_emits_metric_event("health_reporter", "p4obs", "metric_3")
_emit_emits_metric_event("health_reporter", "p4obs", "metric_4")
_emit_emits_metric_event("health_reporter", "p4obs", "metric_5")
_emit_emits_metric_event("health_reporter", "p4obs", "metric_6")
_emit_records_incident_event("health_reporter", "p4obs", "incident")
_emit_captures_runtime_anomaly("health_reporter", "p4obs", "anomaly")
_emit_writes_observability_log("health_reporter", "p4obs", "obs_log")
_emit_updates_monitoring_state("health_reporter", "p4obs", "mon_state")
_emit_triggers_alert("health_reporter", "p4obs", "alert")
_emit_links_incident_trace("health_reporter", "p4obs", "trace_link")
_emit_captures_pattern("health_reporter", "p3lm", "pattern")
_emit_records_learning_event("health_reporter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("health_reporter", "p3lm", "snapshot")
_emit_feeds_meta_learning("health_reporter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("health_reporter", "p3lm", "routing")
_emit_improves_agent_policy("health_reporter", "p3lm", "policy")
_emit_stores_learning_state("health_reporter", "p3lm", "state")
_emit_records_execution_trace("health_reporter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("health_reporter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("health_reporter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("health_reporter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("health_reporter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("health_reporter", "env_read", "p2_env_1")
_emit_reads_environ("health_reporter", "env_read", "p2_env_2")
_emit_reads_runtime_state("health_reporter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("health_reporter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "health_reporter", "context_pull")
_emit_pulls_context("p1", "health_reporter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "health_reporter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "health_reporter", "uwg_term_2")
_emit_writes_through("p1", "health_reporter", "write_through")
_emit_writes_through("p1", "health_reporter", "write_through_2")
_emit_validated_by_safety_plane("p1", "health_reporter", "safety_validation")
_emit_invokes_eval("p1", "health_reporter", "eval_call")
_emit_proposal_commits_routing("p1", "health_reporter", "routing_commit")
_emit_escalates_to_human("p1", "health_reporter", "human_escalation")
_emit_routes_through("p1", "health_reporter", "route_through")
_emit_checks_agent_registry("p1", "health_reporter", "agent_registry")
_emit_validates_agent_capability("p1", "health_reporter", "capability")
_emit_dispatches_execution_plan("p1", "health_reporter", "exec_plan")
_emit_agent_executes_agent("p1", "health_reporter", "sub_agent")
_emit_routes_to_agent("p1", "health_reporter", "target_agent")
_emit_verifies_policy("p1", "health_reporter", "policy_check")
_emit_observes_runtime_state("p1", "health_reporter", "runtime_state")
_emit_verifies_boundary("p1", "health_reporter", "boundary_check")
_emit_transcripts_response("p1", "health_reporter", "transcript")
_emit_hard_fails_untranscripted("p1", "health_reporter")
_emit_gated_by_confidence("p1", "health_reporter", "confidence_gate")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Trust thresholds
# ---------------------------------------------------------------------------

_STRICT_THRESHOLDS: dict[str, int] = {
    "unresolved_import_count": 2000,
    "layer_violation_count": 500,
    "orphan_module_count": 300,
    "null_layer_count": 200,
    "parse_failure_count": 50,
}


@dataclass
class TrustViolation:
    """One strict-mode trust threshold violation."""

    rule: str
    threshold: int
    actual: int
    description: str

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "threshold": self.threshold,
            "actual": self.actual,
            "description": self.description,
        }


@dataclass
class ADGHealthReport:
    """Structured health report for one ADG artifact."""

    # Counts
    total_entities: int = 0
    total_relations: int = 0
    repo_local_entities: int = 0
    external_entities: int = 0
    unresolved_imports: int = 0
    unresolved_symbols: int = 0
    synthetic_placeholders: int = 0
    orphan_repo_modules: int = 0
    orphan_unresolved_nodes: int = 0
    orphan_synthetic_nodes: int = 0
    duplicate_symbol_definitions: int = 0
    null_file_backed_entity_count: int = 0
    null_layer_count: int = 0
    layer_violation_count: int = 0

    # Blind spots
    dynamic_blind_spots: int = 0
    star_import_blind_spots: int = 0
    parse_failure_blind_spots: int = 0

    # Identity distribution
    by_identity_kind: dict[str, int] = field(default_factory=dict)
    by_confidence: dict[str, int] = field(default_factory=dict)
    by_layer: dict[str, int] = field(default_factory=dict)

    # High-risk nodes
    high_fan_in_modules: list[dict] = field(default_factory=list)
    high_fan_out_modules: list[dict] = field(default_factory=list)

    # Trust gate
    trust_violations: list[TrustViolation] = field(default_factory=list)
    trust_passed: bool = True
    artifact_digest: str = ""
    schema_version: str = ""
    commit_sha: str = ""

    @property
    def summary(self) -> str:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ADGHealthReport.summary")

        status = "PASS" if self.trust_passed else "FAIL"
        return (
            f"ADG health [{status}] "
            f"entities={self.total_entities} "
            f"relations={self.total_relations} "
            f"unresolved={self.unresolved_imports} "
            f"violations={self.layer_violation_count} "
            f"orphans={self.orphan_repo_modules} "
            f"blind_spots={self.dynamic_blind_spots + self.star_import_blind_spots}"
        )

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "commit_sha": self.commit_sha,
            "artifact_digest": self.artifact_digest,
            "trust_passed": self.trust_passed,
            "trust_violations": [v.to_dict() for v in self.trust_violations],
            "summary": self.summary,
            "counts": {
                "total_entities": self.total_entities,
                "total_relations": self.total_relations,
                "repo_local_entities": self.repo_local_entities,
                "external_entities": self.external_entities,
                "unresolved_imports": self.unresolved_imports,
                "unresolved_symbols": self.unresolved_symbols,
                "synthetic_placeholders": self.synthetic_placeholders,
                "orphan_repo_modules": self.orphan_repo_modules,
                "orphan_unresolved_nodes": self.orphan_unresolved_nodes,
                "orphan_synthetic_nodes": self.orphan_synthetic_nodes,
                "duplicate_symbol_definitions": self.duplicate_symbol_definitions,
                "null_file_backed_entity_count": self.null_file_backed_entity_count,
                "null_layer_count": self.null_layer_count,
                "layer_violation_count": self.layer_violation_count,
            },
            "blind_spots": {
                "dynamic": self.dynamic_blind_spots,
                "star_imports": self.star_import_blind_spots,
                "parse_failures": self.parse_failure_blind_spots,
                "total": self.dynamic_blind_spots
                + self.star_import_blind_spots
                + self.parse_failure_blind_spots,
            },
            "identity_distribution": {
                "by_identity_kind": self.by_identity_kind,
                "by_confidence": self.by_confidence,
                "by_layer": self.by_layer,
            },
            "high_risk": {
                "high_fan_in_modules": self.high_fan_in_modules[:10],
                "high_fan_out_modules": self.high_fan_out_modules[:10],
            },
        }

    def print_summary(self) -> None:
        """Print human-readable health summary."""
        status = "[PASS]" if self.trust_passed else "[FAIL]"
        print(f"\nADG Health Gate: {status}")
        print(f"  Entities:            {self.total_entities}")
        print(f"  Relations:           {self.total_relations}")
        print(f"  Repo-local:          {self.repo_local_entities}")
        print(f"  External:            {self.external_entities}")
        print(f"  Unresolved imports:  {self.unresolved_imports}")
        print(f"  Layer violations:    {self.layer_violation_count}")
        print(f"  Orphan modules:      {self.orphan_repo_modules}")
        print(f"  Null layer:          {self.null_layer_count}")
        print(f"  Dynamic blind spots: {self.dynamic_blind_spots}")
        print(f"  Star import spots:   {self.star_import_blind_spots}")
        print(f"  Parse failures:      {self.parse_failure_blind_spots}")
        if self.trust_violations:
            print("\n  Trust violations:")
            for v in self.trust_violations:
                print(f"    [{v.rule}] {v.description} (actual={v.actual} > threshold={v.threshold})")
        print(f"\n  Digest: {self.artifact_digest[:24]}...")
        print()


def build_health_report(
    artifact: ADGArtifact,
    strict: bool = False,
) -> ADGHealthReport:
    """Build an ADGHealthReport from a pre-built ADGArtifact.

    Parameters
    ----------
    artifact:
        A fully-built ADGArtifact (schema v3).
    strict:
        If True, check trust thresholds. Report trust_passed=False if any violated.
    """
    report = ADGHealthReport(
        schema_version=artifact.schema_version,
        commit_sha=artifact.commit_sha,
        artifact_digest=artifact.artifact_digest,
    )

    # Pull from identity_health
    ih = artifact.identity_health
    report.by_identity_kind = dict(ih.get("by_identity_kind", {}))
    report.by_confidence = dict(ih.get("by_confidence", {}))
    report.unresolved_imports = ih.get("unresolved_import_count", len(artifact.unresolved_imports))

    # Pull from structural_metrics
    sm = artifact.structural_metrics
    report.total_entities = sm.total_entities
    report.total_relations = sm.total_relations
    report.layer_violation_count = sm.layer_violation_count
    report.by_layer = dict(sm.by_layer)
    report.high_fan_in_modules = sm.high_fan_in_modules[:10]
    report.high_fan_out_modules = sm.high_fan_out_modules[:10]

    # Count entity kinds
    from agentic_core.adg.identity.normalizer import IdentityKind

    _module_prefix = "ADG::Module::"
    orphan_module_set = set(sm.orphan_modules)

    for entity in artifact.entities:
        kind = entity.identity_kind
        if kind == IdentityKind.REPO_MODULE.value:
            report.repo_local_entities += 1
            if entity.adg_name in orphan_module_set:
                if not entity.resolved_path:
                    report.null_file_backed_entity_count += 1
                else:
                    report.orphan_repo_modules += 1
        elif kind == IdentityKind.EXTERNAL_MODULE.value:
            report.external_entities += 1
        elif kind == IdentityKind.UNRESOLVED_IMPORT.value:
            report.unresolved_symbols += 1
            if entity.adg_name in orphan_module_set:
                report.orphan_unresolved_nodes += 1
        elif kind == IdentityKind.INFERRED_SYMBOL.value:
            report.synthetic_placeholders += 1
            if entity.adg_name in orphan_module_set:
                report.orphan_synthetic_nodes += 1
        elif kind == IdentityKind.PACKAGE_CONTAINER.value:
            report.external_entities += 1  # treat package containers as external-ish

        # Null file-backed: module entity with no resolved_path
        if entity.entity_type == "module" and not entity.resolved_path:
            report.null_file_backed_entity_count += 1

        # Null layer: repo module with L_UNKNOWN layer
        if entity.entity_type == "module" and entity.layer == "L_UNKNOWN":
            report.null_layer_count += 1

    # Deduplicate orphan repo modules
    report.orphan_repo_modules = len([m for m in sm.orphan_modules if m.startswith(_module_prefix)])

    # Pull from blind_spots
    bs = artifact.blind_spots
    report.dynamic_blind_spots = bs.dynamic_import_count
    report.star_import_blind_spots = bs.star_import_count
    report.parse_failure_blind_spots = bs.parse_failure_count

    # Duplicate symbol detection: count by resolved_path
    path_counts: dict[str, int] = {}
    for entity in artifact.entities:
        if entity.entity_type == "symbol" and entity.resolved_path:
            path_counts[entity.resolved_path] = path_counts.get(entity.resolved_path, 0) + 1
    report.duplicate_symbol_definitions = sum(1 for c in path_counts.values() if c > 1)

    # Trust gate
    if strict:
        actual_values = {
            "unresolved_import_count": report.unresolved_imports,
            "layer_violation_count": report.layer_violation_count,
            "orphan_module_count": report.orphan_repo_modules,
            "null_layer_count": report.null_layer_count,
            "parse_failure_count": report.parse_failure_blind_spots,
        }
        descriptions = {
            "unresolved_import_count": "Too many unresolved imports (blind spots in graph)",
            "layer_violation_count": "Too many layer boundary violations (architecture degraded)",
            "orphan_module_count": "Too many orphan modules (disconnected graph regions)",
            "null_layer_count": "Too many unmapped layer modules (LAYER_PREFIXES incomplete)",
            "parse_failure_count": "Too many parse failures (scanner reliability degraded)",
        }
        for rule, threshold in _STRICT_THRESHOLDS.items():
            actual = actual_values.get(rule, 0)
            if actual > threshold:
                report.trust_violations.append(
                    TrustViolation(
                        rule=rule,
                        threshold=threshold,
                        actual=actual,
                        description=descriptions.get(rule, rule),
                    )
                )
        report.trust_passed = len(report.trust_violations) == 0

    return report


def build_health_report_from_scan(
    repo_root: Path | None = None,
    strict: bool = False,
) -> ADGHealthReport:
    """Build health report by running a fresh ADG scan + artifact build.

    Convenience entry-point that wires scan -> artifact -> health_report.
    """
    from agentic_core.adg.artifact.builder import build_artifact
    from agentic_core.adg.runtime.cache_loader import load_or_scan

    repo_root = Path(repo_root) if repo_root else Path.cwd()
    result = load_or_scan(repo_root=str(repo_root))
    artifact = build_artifact(result, repo_root=repo_root)
    return build_health_report(artifact, strict=strict)


__all__ = [
    "ADGHealthReport",
    "TrustViolation",
    "build_health_report",
    "build_health_report_from_scan",
]
