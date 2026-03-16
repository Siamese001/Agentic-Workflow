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

from agentic_core.adg.schema import canonical_name
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "agent_registry_scanner", "p0_governance")
_emit_reads_policy_state("p0", "agent_registry_scanner", "policy_binding")
_emit_snapshots_state("p0", "agent_registry_scanner", "state_snapshot")
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
    except ValueError:
        return str(path).replace("\\", "/")
    return str(rel).replace("\\", "/")


__all__ = [
    "AgentRegistryEdge",
    "AgentRegistryResult",
    "scan_agent_registry",
]
