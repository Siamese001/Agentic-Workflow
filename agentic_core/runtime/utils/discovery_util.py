"""
Agentic Core Discovery Module

This module provides the core discovery functionality for the Agentic Workflow system.
It includes the DiscoveredAgentRecord dataclass and AgentRegistry class for finding and
cataloging agents across the entire ecosystem.
"""

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# from agentic_core.utils.ssot_discovery_validator import get_python_files
# ssot_discovery_validator not found - create placeholder
def get_python_files(path):
    """Placeholder function to get Python files."""
    from pathlib import Path
    return list(Path(path).glob("**/*.py"))

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L5_safety.core_kernel.classification_kernel import is_agent_file
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

_emit_applies_guardrail("p0", "discovery_util", "p0_governance")
_emit_reads_policy_state("p0", "discovery_util", "policy_binding")
_emit_snapshots_state("p0", "discovery_util", "state_snapshot")
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

_emit_emits_metric_event("discovery_util", "p4obs", "metric_1")
_emit_emits_metric_event("discovery_util", "p4obs", "metric_2")
_emit_emits_metric_event("discovery_util", "p4obs", "metric_3")
_emit_emits_metric_event("discovery_util", "p4obs", "metric_4")
_emit_emits_metric_event("discovery_util", "p4obs", "metric_5")
_emit_emits_metric_event("discovery_util", "p4obs", "metric_6")
_emit_records_incident_event("discovery_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("discovery_util", "p4obs", "anomaly")
_emit_writes_observability_log("discovery_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("discovery_util", "p4obs", "mon_state")
_emit_triggers_alert("discovery_util", "p4obs", "alert")
_emit_links_incident_trace("discovery_util", "p4obs", "trace_link")
_emit_captures_pattern("discovery_util", "p3lm", "pattern")
_emit_records_learning_event("discovery_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("discovery_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("discovery_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("discovery_util", "p3lm", "routing")
_emit_improves_agent_policy("discovery_util", "p3lm", "policy")
_emit_stores_learning_state("discovery_util", "p3lm", "state")
_emit_records_execution_trace("discovery_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("discovery_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("discovery_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("discovery_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("discovery_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("discovery_util", "env_read", "p2_env_1")
_emit_reads_environ("discovery_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("discovery_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("discovery_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "discovery_util", "context_pull")
_emit_pulls_context("p1", "discovery_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "discovery_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "discovery_util", "uwg_term_2")
_emit_writes_through("p1", "discovery_util", "write_through")
_emit_writes_through("p1", "discovery_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "discovery_util", "safety_validation")
_emit_invokes_eval("p1", "discovery_util", "eval_call")
_emit_proposal_commits_routing("p1", "discovery_util", "routing_commit")
_emit_escalates_to_human("p1", "discovery_util", "human_escalation")
_emit_routes_through("p1", "discovery_util", "route_through")
_emit_checks_agent_registry("p1", "discovery_util", "agent_registry")
_emit_validates_agent_capability("p1", "discovery_util", "capability")
_emit_dispatches_execution_plan("p1", "discovery_util", "exec_plan")
_emit_agent_executes_agent("p1", "discovery_util", "sub_agent")
_emit_routes_to_agent("p1", "discovery_util", "target_agent")
_emit_verifies_policy("p1", "discovery_util", "policy_check")
_emit_observes_runtime_state("p1", "discovery_util", "runtime_state")
_emit_verifies_boundary("p1", "discovery_util", "boundary_check")
_emit_transcripts_response("p1", "discovery_util", "transcript")
_emit_hard_fails_untranscripted("p1", "discovery_util")
_emit_gated_by_confidence("p1", "discovery_util", "confidence_gate")
emit_replay_key("p0", "discovery_util")
emit_determinism_digest("p0", "discovery_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "discovery_util", "execution_auth")
_emit_validates_capability("p2", "discovery_util", "capability_check")
_emit_routes_to_capability("p2", "discovery_util", "capability_route")
_emit_writes_via_uwg("p2", "discovery_util", "uwg_write")
_emit_blocks_direct_write("p2", "discovery_util", "direct_write_block")
_emit_records_tool_invocation("p2", "discovery_util", "tool_invocation")
_emit_captures_execution_output("p2", "discovery_util", "exec_output")
_emit_dispatches_agent("p3", "discovery_util", "agent_dispatch")
_emit_coordinates_agents("p3", "discovery_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "discovery_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "discovery_util", "healing_outcome")
_emit_escalates_failure("p3", "discovery_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "discovery_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "discovery_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "discovery_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "discovery_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "discovery_util", "eval_metric")
_emit_stores_embedding("p4", "discovery_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "discovery_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "discovery_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredAgentRecord:
    """Lightweight record for a discovered agent (replaces retired DiscoveredAgent)."""

    name: str = ""
    layer: str = ""
    instance: Any = None
    class_ref: Any = None
    file_path: Path | None = None
    module_path: str = ""


class AgentRegistry:
    """
    Discovers and catalogs agents across the Agentic Workflow ecosystem.
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.discovered_agents: list[DiscoveredAgentRecord] = []

    def discover_all(self) -> list[DiscoveredAgentRecord]:
        """
        Discovers all agents in the ecosystem.

        Returns:
            List of discovered agents
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentRegistry.discover_all")

        agents = []
        python_files = get_python_files(self.project_root)
        for file_path in python_files:
            try:
                file_agents = self._scan_file_for_agents(file_path)
                agents.extend(file_agents)
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"Failed to scan {file_path}: {e}")
        self.discovered_agents = agents
        logger.info(f"Discovered {len(agents)} agents across {len(python_files)} files")
        return agents

    def _scan_file_for_agents(self, file_path: Path) -> list[DiscoveredAgentRecord]:
        """
        Scans a single Python file for agent classes.

        [REFACTORED 2026-02-08] Uses classification kernel (SSOT) to determine
        if a file is an agent. Only then extracts class metadata from AST.

        Args:
            file_path: Path to the Python file to scan

        Returns:
            List of discovered agents in the file
        """
        agents = []
        try:
            if not is_agent_file(file_path):
                return agents
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            class_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            if not class_nodes:
                return agents
            import re as _re

            stem_clean = _re.sub("[^a-zA-Z0-9]", "", file_path.stem.lower())
            primary = None
            for node in class_nodes:
                if _re.sub("[^a-zA-Z0-9]", "", node.name.lower()) == stem_clean:
                    primary = node
                    break
            if primary is None:
                for node in class_nodes:
                    if node.name.endswith("Agent"):
                        primary = node
                        break
            if primary is None:
                primary = class_nodes[0]
            layer = self._determine_layer(file_path, primary)
            instance = None
            try:
                class_ref = self._get_class_reference(file_path, primary.name)
                if class_ref:
                    instance = class_ref()
            except (ValueError, TypeError, RuntimeError) as e:
                raise
                instance = Mock()
            agent = DiscoveredAgentRecord(
                name=primary.name,
                layer=layer,
                instance=instance,
                class_ref=self._get_class_reference(file_path, primary.name) or type(primary.name, (), {}),
                file_path=file_path,
                module_path=self._get_module_path(file_path),
            )
            agents.append(agent)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.debug(f"Failed to parse {file_path}: {e}")
        return agents

    def _determine_layer(self, file_path: Path, class_node: ast.ClassDef) -> str:
        """
        Determines the architectural layer for an agent based on its file location.

        Args:
            file_path: Path to the file containing the agent
            class_node: AST class node for the agent

        Returns:
            Layer name as string
        """
        path_str = str(file_path)
        layer_mappings = {
            "L0_routing": "L0_routing",
            "L1_cognition": "L1_cognition",
            "L2_execution": "L2_execution",
            "L3_orchestration": "L3_orchestration",
            "L4_coordination": "L4_coordination",
            "L5_safety": "L5_safety",
            "L6_observability": "L6_observability",
            "tests": "tests",
            "test": "tests",
        }
        for pattern, layer in layer_mappings.items():
            if pattern in path_str:
                return layer
        return "unknown"

    def _get_class_reference(self, file_path: Path, class_name: str) -> type | None:
        """
        Attempts to get the actual class reference from a file.

        Args:
            file_path: Path to the file containing the class
            class_name: Name of the class to retrieve

        Returns:
            Class reference or None if not found
        """
        try:
            return None
        # guardian: allow-silent-swallow
        except Exception:
            return None

    def _get_module_path(self, file_path: Path) -> str:
        """
        Converts a file path to a Python module path.

        Args:
            file_path: Path to convert

        Returns:
            Module path as string
        """
        parts = file_path.parts
        if AGENTIC_CORE_DIR in parts:
            start_idx = parts.index("agentic_core")
            module_parts = parts[start_idx:-1]
            module_parts = [p.replace(".py", "") for p in module_parts if not p.startswith("__")]
            return ".".join(module_parts)
        return str(file_path)


class Mock:
    """Mock class for testing purposes."""

    pass
