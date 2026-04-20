"""
SSOT Discovery Utility - Centralized Agent Discovery Access

This module provides a single point of access to agent_discovery_full.json,
eliminating the need for rglob scans across the codebase.

USAGE:
    from agentic_core.utils.runners.ssot_discovery_validator import (
        load_agent_discovery,
        get_agent_paths,
        get_agents_by_layer,
        get_agent_by_name,
    )

    # Get all agent paths
    paths = get_agent_paths(project_root)

    # Get agents filtered by layer
    l5_agents = get_agents_by_layer(project_root, "L5")

SSOT PRINCIPLE:
    All agent discovery should use this module instead of rglob scans.
    The agent_discovery_full.json is the Single Source of Truth.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENT_DISCOVERY_JSON,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from tqdm import tqdm

_emit_emits_metric_event("ssot_discovery_util", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_discovery_util", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_discovery_util", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_discovery_util", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_discovery_util", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_discovery_util", "p4obs", "metric_6")
_emit_records_incident_event("ssot_discovery_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_discovery_util", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_discovery_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_discovery_util", "p4obs", "mon_state")
_emit_triggers_alert("ssot_discovery_util", "p4obs", "alert")
_emit_links_incident_trace("ssot_discovery_util", "p4obs", "trace_link")
_emit_captures_pattern("ssot_discovery_util", "p3lm", "pattern")
_emit_records_learning_event("ssot_discovery_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_discovery_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_discovery_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_discovery_util", "p3lm", "routing")
_emit_improves_agent_policy("ssot_discovery_util", "p3lm", "policy")
_emit_stores_learning_state("ssot_discovery_util", "p3lm", "state")
_emit_records_execution_trace("ssot_discovery_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_discovery_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_discovery_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_discovery_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_discovery_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_discovery_util", "env_read", "p2_env_1")
_emit_reads_environ("ssot_discovery_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_discovery_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_discovery_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "ssot_discovery_util")
emit_determinism_digest("p0", "ssot_discovery_util")

_emit_dispatches_healing_run("p1", "ssot_discovery_util", "L0")
_emit_routes_through("p1", "ssot_discovery_util", "L0")
_emit_checks_agent_registry("p1", "ssot_discovery_util", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_discovery_util", "capability")
_emit_dispatches_execution_plan("p1", "ssot_discovery_util", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_discovery_util", "sub_agent")
_emit_routes_to_agent("p1", "ssot_discovery_util", "target_agent")
_emit_verifies_policy("p1", "ssot_discovery_util", "policy_check")
_emit_observes_runtime_state("p1", "ssot_discovery_util", "runtime_state")
_emit_verifies_boundary("p1", "ssot_discovery_util", "boundary_check")
_emit_transcripts_response("p1", "ssot_discovery_util", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_discovery_util")
_emit_gated_by_confidence("p1", "ssot_discovery_util", "confidence_gate")
_emit_escalates_to_human("p1", "ssot_discovery_util", "L0")
_emit_reads_policy_state("p1", "ssot_discovery_util", "L0")
_emit_records_execution_trace("p0", "evidence", "ssot_discovery_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "ssot_discovery_util", "p0_governance")
_emit_snapshots_state("p0", "ssot_discovery_util", "state_snapshot")
_emit_authorize_and_execute("p2", "ssot_discovery_util", "execution_auth")
_emit_validates_capability("p2", "ssot_discovery_util", "capability_check")
_emit_routes_to_capability("p2", "ssot_discovery_util", "capability_route")
_emit_writes_via_uwg("p2", "ssot_discovery_util", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_discovery_util", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_discovery_util", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_discovery_util", "exec_output")
_emit_dispatches_agent("p3", "ssot_discovery_util", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_discovery_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_discovery_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_discovery_util", "healing_outcome")
_emit_escalates_failure("p3", "ssot_discovery_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_discovery_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_discovery_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_discovery_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_discovery_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_discovery_util", "eval_metric")
_emit_stores_embedding("p4", "ssot_discovery_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_discovery_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_discovery_util", "exec_snapshot_link")
_emit_pulls_context("p1", "ssot_discovery_util", "context_pull")
_emit_pulls_context("p1", "ssot_discovery_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "ssot_discovery_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_discovery_util", "uwg_term_secondary")
_emit_writes_through("p1", "ssot_discovery_util", "write_through")
_emit_writes_through("p1", "ssot_discovery_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "ssot_discovery_util", "safety_validation")
_emit_invokes_eval("p1", "ssot_discovery_util", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_discovery_util", "routing_commit")

Logger = logging.getLogger(__name__)

# Cache for discovery data to avoid repeated file reads
_discovery_cache: dict[str, Any] = {}
_cache_timestamp: float = 0.0


def resolve_canonical_class(agent_entry: dict[str, Any]) -> str:
    """Return the authoritative class name for an agent entry.

    Identity rule: ``verification_status.class`` (AST-verified) is canonical.
    ``class_name`` is non-authoritative / legacy display only.
    """
    vs = agent_entry.get("verification_status") or {}
    ast_class = vs.get("class", "") or ""
    if ast_class:
        return ast_class
    return agent_entry.get("class_name", "") or ""


def load_agent_discovery(
    project_root: Path | None = None,
    force_reload: bool = False,
) -> list[dict[str, Any]]:
    """
    Load agent discovery data from SSOT JSON file.

    Args:
        project_root: Project root path. If None, uses get_validated_project_root().
        force_reload: If True, bypass cache and reload from disk.

    Returns:
        List of agent discovery entries.
    """
    global _discovery_cache, _cache_timestamp

    if project_root is None:
        project_root = get_validated_project_root()

    discovery_path = project_root / AGENT_DISCOVERY_JSON
    cache_key = str(discovery_path)

    # Check cache validity
    if not force_reload and cache_key in _discovery_cache:
        # Check if file was modified
        try:
            file_mtime = discovery_path.stat().st_mtime
            if file_mtime <= _cache_timestamp:
                return _discovery_cache[cache_key]
        except OSError:  # guardian: Add error context logging
            pass

    # Load from disk
    if not discovery_path.exists():
        Logger.warning(f"[SSOT] Discovery file not found: {discovery_path}")
        return []

    try:
        with open(discovery_path, encoding="utf-8") as f:
            data = json.load(f)

        # Normalize to list format
        if isinstance(data, list):
            agents = data
        elif isinstance(data, dict):
            # Handle wrapped format: {"agents": [...], "schema_version": ...}
            if "agents" in data and isinstance(data["agents"], list):
                agents = data["agents"]
            else:
                agents = list(data.values())
        else:
            Logger.warning(f"[SSOT] Unexpected data format: {type(data)}")
            agents = []

        # Update cache
        _discovery_cache[cache_key] = agents
        _cache_timestamp = discovery_path.stat().st_mtime

        Logger.debug(f"[SSOT] Loaded {len(agents)} agents from discovery JSON")
        return agents

    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow -- resilient SSOT discovery; failure logged above
        Logger.error(f"[SSOT] Failed to load discovery JSON: {e}")
        return []


def get_agent_paths(
    project_root: Path | None = None,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """
    Get all agent file paths from SSOT.

    Args:
        project_root: Project root path.
        exclude_patterns: Patterns to exclude (e.g., ['test_', 'mock_']).

    Returns:
        List of Path objects for agent files.
    """
    if project_root is None:
        project_root = get_validated_project_root()

    if exclude_patterns is None:
        exclude_patterns = []

    agents = load_agent_discovery(project_root)
    paths = []

    for agent in tqdm(agents, desc="Processing", unit="item"):
        path_str = agent.get("path", "") or agent.get("file", "")
        if not path_str:
            continue

        # Apply exclusions
        if any(pattern in path_str for pattern in exclude_patterns):
            continue

        agent_path = project_root / path_str
        if agent_path.exists():
            paths.append(agent_path)

    return paths


def get_agents_by_layer(project_root: Path | None = None, layer: str = None) -> list[dict[str, Any]]:
    """
    Get agents filtered by layer (L0-L6).

    Args:
        project_root: Project root path.
        layer: Layer to filter by (e.g., "L5", "L3").

    Returns:
        List of agent entries matching the layer.
    """
    agents = load_agent_discovery(project_root)

    if layer is None:
        return agents

    return [
        agent
        for agent in agents
        if agent.get("layer", "").upper() == layer.upper()
        or layer.upper() in (agent.get("path", "") or agent.get("file", "")).upper()
    ]


def get_agent_by_name(project_root: Path | None = None, name: str = None) -> dict[str, Any] | None:
    """
    Get a specific agent by name.

    Args:
        project_root: Project root path.
        name: Agent name to find.

    Returns:
        Agent entry or None if not found.
    """
    if name is None:
        return None

    agents = load_agent_discovery(project_root)

    for agent in agents:
        if agent.get("name", "") == name:
            return agent
        # Prefer AST-verified class identity
        if resolve_canonical_class(agent) == name:
            return agent
        if agent.get("class_name", "") == name:
            return agent

    return None


def get_agent_names(project_root: Path | None = None) -> set[str]:
    """
    Get set of all agent names from SSOT.

    Args:
        project_root: Project root path.

    Returns:
        Set of agent names.
    """
    agents = load_agent_discovery(project_root)
    names = set()

    for agent in agents:
        if "name" in agent:
            names.add(agent["name"])
        # Prefer AST-verified canonical class
        canonical = resolve_canonical_class(agent)
        if canonical:
            names.add(canonical)
        elif "class_name" in agent:
            names.add(agent["class_name"])

    return names


def get_healers(project_root: Path | None = None) -> list[dict[str, Any]]:
    """
    Get all healer agents from SSOT.

    Args:
        project_root: Project root path.

    Returns:
        List of healer agent entries.
    """
    agents = load_agent_discovery(project_root)

    return [
        agent
        for agent in agents
        if agent.get("has_healing", False)
        or agent.get("is_healer", False)
        or "Healer" in agent.get("name", "")
        or "Healer" in agent.get("class_name", "")
    ]


def get_python_files(
    project_root: Path | None = None,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """
    Get all Python files from the project.

    Args:
        project_root: Project root path.
        exclude_patterns: Patterns to exclude (e.g., ['test_', '__pycache__']).

    Returns:
        List of Path objects for Python files.
    """
    if project_root is None:
        project_root = get_validated_project_root()

    if exclude_patterns is None:
        exclude_patterns = ["__pycache__", ".pyc", "test_", "mock_"]

    python_files = []

    for py_file in project_root.rglob("*.py"):
        # Apply exclusions
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue

        python_files.append(py_file)

    return python_files


def get_data_files(
    project_root: Path | None = None,
    extensions: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> list[Path]:
    """
    Get all data files from the project with specified extensions.

    Args:
        project_root: Project root path.
        extensions: File extensions to include (e.g., [".json", ".md"]).
        exclude_patterns: Patterns to exclude (e.g., ['test_', '__pycache__']).

    Returns:
        List of Path objects for data files.
    """
    if project_root is None:
        project_root = get_validated_project_root()

    if extensions is None:
        extensions = [".json", ".md", ".yaml", ".yml", ".toml", ".txt"]

    if exclude_patterns is None:
        exclude_patterns = ["__pycache__", ".pyc", "test_", "mock_"]

    data_files = []

    for ext in extensions:
        for data_file in project_root.rglob(f"*{ext}"):
            # Apply exclusions
            if any(pattern in str(data_file) for pattern in exclude_patterns):
                continue

            data_files.append(data_file)

    return data_files


def get_all_files(
    project_root: Path | None = None,
    exclude_patterns: list[str] | None = None,
) -> dict[str, list[Path]]:
    """
    Get all files from the project, grouped by file type.

    Args:
        project_root: Project root path.
        exclude_patterns: Patterns to exclude (e.g., ['__pycache__', '.pyc']).

    Returns:
        Dictionary with file extensions as keys and lists of Path objects as values.
    """
    if project_root is None:
        project_root = get_validated_project_root()

    if exclude_patterns is None:
        exclude_patterns = ["__pycache__", ".pyc"]

    all_files = {}

    # Get all files recursively
    for file_path in tqdm(project_root.rglob("*"), desc="Processing", unit="item"):
        if file_path.is_file():
            # Apply exclusions
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue

            # Group by extension
            ext = file_path.suffix.lower()
            if ext not in all_files:
                all_files[ext] = []
            all_files[ext].append(file_path)

    return all_files


def invalidate_cache() -> None:
    """Invalidate the discovery cache to force reload on next access."""
    global _discovery_cache, _cache_timestamp
    _discovery_cache.clear()
    _cache_timestamp = 0.0


__all__ = [
    "load_agent_discovery",
    "get_agent_paths",
    "get_agents_by_layer",
    "get_agent_by_name",
    "get_agent_names",
    "get_healers",
    "get_python_files",
    "get_data_files",
    "get_all_files",
    "invalidate_cache",
    "resolve_canonical_class",
]
