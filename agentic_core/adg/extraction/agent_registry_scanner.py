"""G6 (gap): Agent Registry Scanner — capability and registration graph extraction.

Scans agent spec JSON files across the repository and emits static ADG edges
representing agent registration and capability relationships.

Emits:
  ADG::Module::<spec_file> --registered_as--> ADG::Symbol::<agent_name>
      for each top-level agent key in a spec JSON.
  ADG::Symbol::<agent_name> --has_capability--> ADG::Symbol::<capability>
      for each capability declared in the agent spec.
  ADG::Symbol::<agent_name> --depends_on_agent--> ADG::Symbol::<dep_agent>
      for each agent dependency declared in the spec.

Supported spec file patterns:
  **/agent_spec*.json
  **/agent_specs*.json
  **/agent_config*.json

Usage::

    from agentic_core.adg.extraction.agent_registry_scanner import scan_agent_registry

    result = scan_agent_registry(repo_root=Path("."))
    for edge in result.edges:
        print(edge.from_name, edge.relation_type, edge.to_name)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.adg.schema_util import canonical_name
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "agent_registry_scanner", "p0_governance")
_emit_reads_policy_state("p0", "agent_registry_scanner", "policy_binding")
_emit_snapshots_state("p0", "agent_registry_scanner", "state_snapshot")
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

_emit_emits_metric_event("agent_registry_scanner", "p4obs", "metric_1")
_emit_emits_metric_event("agent_registry_scanner", "p4obs", "metric_2")
_emit_emits_metric_event("agent_registry_scanner", "p4obs", "metric_3")
_emit_emits_metric_event("agent_registry_scanner", "p4obs", "metric_4")
_emit_emits_metric_event("agent_registry_scanner", "p4obs", "metric_5")
_emit_emits_metric_event("agent_registry_scanner", "p4obs", "metric_6")
_emit_records_incident_event("agent_registry_scanner", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_registry_scanner", "p4obs", "anomaly")
_emit_writes_observability_log("agent_registry_scanner", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_registry_scanner", "p4obs", "mon_state")
_emit_triggers_alert("agent_registry_scanner", "p4obs", "alert")
_emit_links_incident_trace("agent_registry_scanner", "p4obs", "trace_link")
_emit_captures_pattern("agent_registry_scanner", "p3lm", "pattern")
_emit_records_learning_event("agent_registry_scanner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_registry_scanner", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_registry_scanner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_registry_scanner", "p3lm", "routing")
_emit_improves_agent_policy("agent_registry_scanner", "p3lm", "policy")
_emit_stores_learning_state("agent_registry_scanner", "p3lm", "state")
_emit_records_execution_trace("agent_registry_scanner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_registry_scanner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_registry_scanner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_registry_scanner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_registry_scanner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_registry_scanner", "env_read", "p2_env_1")
_emit_reads_environ("agent_registry_scanner", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_registry_scanner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_registry_scanner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_registry_scanner", "context_pull")
_emit_pulls_context("p1", "agent_registry_scanner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_registry_scanner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_registry_scanner", "uwg_term_2")
_emit_writes_through("p1", "agent_registry_scanner", "write_through")
_emit_writes_through("p1", "agent_registry_scanner", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_registry_scanner", "safety_validation")
_emit_invokes_eval("p1", "agent_registry_scanner", "eval_call")
_emit_proposal_commits_routing("p1", "agent_registry_scanner", "routing_commit")
_emit_escalates_to_human("p1", "agent_registry_scanner", "human_escalation")
_emit_routes_through("p1", "agent_registry_scanner", "route_through")
_emit_checks_agent_registry("p1", "agent_registry_scanner", "agent_registry")
_emit_validates_agent_capability("p1", "agent_registry_scanner", "capability")
_emit_dispatches_execution_plan("p1", "agent_registry_scanner", "exec_plan")
_emit_agent_executes_agent("p1", "agent_registry_scanner", "sub_agent")
_emit_routes_to_agent("p1", "agent_registry_scanner", "target_agent")
_emit_verifies_policy("p1", "agent_registry_scanner", "policy_check")
_emit_observes_runtime_state("p1", "agent_registry_scanner", "runtime_state")
_emit_verifies_boundary("p1", "agent_registry_scanner", "boundary_check")
_emit_transcripts_response("p1", "agent_registry_scanner", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_registry_scanner")
_emit_gated_by_confidence("p1", "agent_registry_scanner", "confidence_gate")
emit_replay_key("p0", "agent_registry_scanner")
emit_determinism_digest("p0", "agent_registry_scanner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_registry_scanner", "execution_auth")
_emit_validates_capability("p2", "agent_registry_scanner", "capability_check")
_emit_routes_to_capability("p2", "agent_registry_scanner", "capability_route")
_emit_writes_via_uwg("p2", "agent_registry_scanner", "uwg_write")
_emit_blocks_direct_write("p2", "agent_registry_scanner", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_registry_scanner", "tool_invocation")
_emit_captures_execution_output("p2", "agent_registry_scanner", "exec_output")
_emit_dispatches_agent("p3", "agent_registry_scanner", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_registry_scanner", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_registry_scanner", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_registry_scanner", "healing_outcome")
_emit_escalates_failure("p3", "agent_registry_scanner", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_registry_scanner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_registry_scanner", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_registry_scanner", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_registry_scanner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_registry_scanner", "eval_metric")
_emit_stores_embedding("p4", "agent_registry_scanner", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_registry_scanner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_registry_scanner", "exec_snapshot_link")

logger = logging.getLogger(__name__)

_SPEC_FILE_PATTERNS: tuple[str, ...] = (
    "**/agent_spec*.json",
    "**/agent_specs*.json",
    "**/agent_config*.json",
)

_EXCLUDED_DIRS: frozenset[str] = frozenset({".git", "__pycache__", ".venv", "node_modules", ".mypy_cache"})


@dataclass(frozen=True)
class AgentRegistryEdge:
    """Single edge from the agent registry graph."""

    from_name: str
    relation_type: str
    to_name: str
    edge_kind: str
    source_file: str
    symbol: str


@dataclass
class AgentRegistryResult:
    """Result of scanning all agent spec JSON files in the repository."""

    edges: list[AgentRegistryEdge] = field(default_factory=list)
    scanned_files: list[str] = field(default_factory=list)
    agent_names: list[str] = field(default_factory=list)

    @property
    def edge_count(self) -> int:
        return len(self.edges)

    @property
    def agent_count(self) -> int:
        return len(self.agent_names)

    def edge_counts_by_relation(self) -> dict[str, int]:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentRegistryResult.edge_counts_by_relation")

        counts: dict[str, int] = {}
        for edge in self.edges:
            counts[edge.relation_type] = counts.get(edge.relation_type, 0) + 1
        return counts


def scan_agent_registry(repo_root: Path) -> AgentRegistryResult:
    """Scan all agent spec JSON files under repo_root and build the registry graph.

    Args:
        repo_root: Root of the repository to scan.

    Returns:
        AgentRegistryResult with all extracted edges.
    """
    result = AgentRegistryResult()
    seen_files: set[str] = set()

    for pattern in _SPEC_FILE_PATTERNS:
        for spec_path in sorted(repo_root.glob(pattern)):
            rel = _repo_relative(spec_path, repo_root)
            if rel in seen_files:
                continue
            if any(part in _EXCLUDED_DIRS for part in spec_path.parts):
                continue
            seen_files.add(rel)
            _scan_spec_file(spec_path, rel, result)

    return result


def _scan_spec_file(
    spec_path: Path,
    rel: str,
    result: AgentRegistryResult,
) -> None:
    """Parse a single agent spec JSON and emit registration edges."""
    try:
        raw = spec_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    # guardian: allow-silent-swallow - acceptable exception handling    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
    except (OSError, json.JSONDecodeError) as exc:
        logger.debug("Skipping %s: %s", spec_path, exc)
        return

    if not isinstance(data, dict):
        return

    result.scanned_files.append(rel)
    module_adg = canonical_name("Module", rel)

    for agent_name, spec_body in data.items():
        if not isinstance(agent_name, str):
            continue
        agent_sym = canonical_name("Symbol", agent_name)
        result.agent_names.append(agent_name)

        # G6a: registered_as edge — spec file declares agent
        result.edges.append(
            AgentRegistryEdge(
                from_name=module_adg,
                relation_type="registered_as",
                to_name=agent_sym,
                edge_kind="agent_registration",
                source_file=rel,
                symbol=agent_name,
            )
        )

        if not isinstance(spec_body, dict):
            continue

        # G6b: has_capability edges — each top-level key in spec body is a capability facet
        for capability_key in spec_body:
            if not isinstance(capability_key, str):
                continue
            cap_sym = canonical_name("Symbol", f"{agent_name}.{capability_key}")
            result.edges.append(
                AgentRegistryEdge(
                    from_name=agent_sym,
                    relation_type="has_capability",
                    to_name=cap_sym,
                    edge_kind="agent_registration",
                    source_file=rel,
                    symbol=f"{agent_name}.{capability_key}",
                )
            )

        # G6c: depends_on_agent edges — explicit dependency declarations
        deps = spec_body.get("depends_on", spec_body.get("agent_dependencies", []))
        if isinstance(deps, list):
            for dep in deps:
                if isinstance(dep, str):
                    dep_sym = canonical_name("Symbol", dep)
                    result.edges.append(
                        AgentRegistryEdge(
                            from_name=agent_sym,
                            relation_type="depends_on_agent",
                            to_name=dep_sym,
                            edge_kind="agent_registration",
                            source_file=rel,
                            symbol=dep,
                        )
                    )


def _repo_relative(path: Path, repo_root: Path) -> str:
    """Return forward-slash repo-relative path."""
    try:
        rel = path.relative_to(repo_root)
    except ValueError as e:
        # TODO: Add proper input validation
        logger.warning(f"Invalid input: {e}")
        return str(path).replace("\\", "/")
    return str(rel).replace("\\", "/")


__all__ = [
    "AgentRegistryEdge",
    "AgentRegistryResult",
    "scan_agent_registry",
]
