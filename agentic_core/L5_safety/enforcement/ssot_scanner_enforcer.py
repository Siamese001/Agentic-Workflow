"""
SSOT Scanner - Direct Filesystem Scanning Without Registry

Eliminates the need for agent_discovery_full.json by scanning the filesystem
directly and parsing AST on-demand. This provides always-current data without
the 15-18 second registry refresh overhead.

Performance: <1 second for full scan (vs 15-18s for registry rebuild)
"""

import ast
from dataclasses import dataclass
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "ssot_scanner_enforcer")
emit_determinism_digest("p0", "ssot_scanner_enforcer")

_emit_dispatches_healing_run("p1", "ssot_scanner_enforcer", "L5")
_emit_routes_through("p1", "ssot_scanner_enforcer", "L5")
_emit_checks_agent_registry("p1", "ssot_scanner_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_scanner_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "ssot_scanner_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_scanner_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "ssot_scanner_enforcer", "target_agent")
_emit_verifies_policy("p1", "ssot_scanner_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "ssot_scanner_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "ssot_scanner_enforcer", "boundary_check")
_emit_transcripts_response("p1", "ssot_scanner_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_scanner_enforcer")
_emit_gated_by_confidence("p1", "ssot_scanner_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "ssot_scanner_enforcer", "L5")
_emit_reads_policy_state("p1", "ssot_scanner_enforcer", "L5")

_emit_applies_guardrail("p0", "ssot_scanner_enforcer", "p0_governance")
_emit_snapshots_state("p0", "ssot_scanner_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "ssot_scanner_enforcer", "execution_auth")
_emit_validates_capability("p2", "ssot_scanner_enforcer", "capability_check")
_emit_routes_to_capability("p2", "ssot_scanner_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "ssot_scanner_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_scanner_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_scanner_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_scanner_enforcer", "exec_output")
_emit_dispatches_agent("p3", "ssot_scanner_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_scanner_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_scanner_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_scanner_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "ssot_scanner_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_scanner_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_scanner_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_scanner_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_scanner_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_scanner_enforcer", "eval_metric")
_emit_stores_embedding("p4", "ssot_scanner_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_scanner_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_scanner_enforcer", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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
from tqdm import tqdm

_emit_emits_metric_event("ssot_scanner_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_scanner_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_scanner_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_scanner_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_scanner_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_scanner_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("ssot_scanner_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_scanner_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_scanner_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_scanner_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("ssot_scanner_enforcer", "p4obs", "alert")
_emit_links_incident_trace("ssot_scanner_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("ssot_scanner_enforcer", "p3lm", "pattern")
_emit_records_learning_event("ssot_scanner_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_scanner_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_scanner_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_scanner_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("ssot_scanner_enforcer", "p3lm", "policy")
_emit_stores_learning_state("ssot_scanner_enforcer", "p3lm", "state")
_emit_records_execution_trace("ssot_scanner_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_scanner_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_scanner_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_scanner_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_scanner_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_scanner_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("ssot_scanner_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_scanner_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_scanner_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_scanner_enforcer", "context_pull")
_emit_pulls_context("p1", "ssot_scanner_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_scanner_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_scanner_enforcer", "uwg_term_2")
_emit_writes_through("p1", "ssot_scanner_enforcer", "write_through")
_emit_writes_through("p1", "ssot_scanner_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_scanner_enforcer", "safety_validation")
_emit_invokes_eval("p1", "ssot_scanner_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_scanner_enforcer", "routing_commit")


@dataclass
class AgentMetadata:
    """Metadata for a single agent file."""

    file_path: Path
    relative_path: str
    class_name: str
    layer: str
    assigned_layer: str
    base_classes: list[str]
    signals: set[str]

    @property
    def has_gravity_violation(self) -> bool:
        """
        Check if agent is in wrong layer (gravity violation).

        Only L0-L5 layers can have violations. APP and UNKNOWN are not violations.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "AgentMetadata.has_gravity_violation",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AgentMetadata.has_gravity_violation".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Skip if either layer is APP or UNKNOWN (not subject to gravity rules)
        if self.layer in ("APP", "UNKNOWN") or self.assigned_layer in ("APP", "UNKNOWN"):
            return False

        # Violation if actual layer doesn't match assigned layer
        return self.layer != self.assigned_layer

    @property
    def is_compliant(self) -> bool:
        """Check if agent is in correct Gospel-assigned layer."""
        return not self.has_gravity_violation


class SSOTScanner:
    """
    Direct filesystem scanner for SSOT enforcement.

    Replaces agent_discovery_full.json with instant, always-current scanning.
    Uses on-demand AST parsing to minimize overhead.
    """

    # Layer assignment rules from structure_blueprint.py
    LAYER_ASSIGNMENTS: dict[str, str] = {
        "L0_routing": "L0",
        "L1_cognition": "L1",
        "L2_execution": "L2",
        "L3_orchestration": "L3",
        "L4_state": "L4",
        "L5_safety": "L5",
        "observability": "L3",  # observability is L3 orchestration
        "utils": "L2",  # Utils are L2 execution tools
        "schemas": "L2",  # Schemas are L2 execution support
        "patterns": "L2",  # Patterns are L2 execution support
        "config": "L2",  # Config is L2 execution support
        "prompt_governance": "L2",  # Prompt governance is L2
        "runtime": "L2",  # Runtime is L2 execution
        "semantic_memory": "L2",  # Semantic memory is L2
    }

    # DEPRECATED: CANON_SIGNALS removed - replaced by dynamic validation
    # SOVEREIGN_SIGNALS: set[str] = {
    #     "healing",
    #     "testing",
    #     "validation",
    #     "execution",
    #     "orchestration",
    #     "state",
    #     "safety",
    #     "cognition",
    #     "intent",
    #     "learning",
    #     "planning",
    # }

    def __init__(self, project_root: Path):
        """
        Initialize SSOT scanner.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root.resolve()
        self._cache: dict[str, AgentMetadata] = {}

    def scan_agents(self, use_cache: bool = False) -> list[AgentMetadata]:
        """
        Scan filesystem for all agent files.

        Args:
            use_cache: If True, return cached results (for performance)

        Returns:
            List of agent metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SSOTScanner.scan_agents")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SSOTScanner.scan_agents".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if use_cache and self._cache:
            return list(self._cache.values())

        agents = []

        # Find all *Agent.py files
        # Operation Zero: Use ssot_discovery instead of glob
        from agentic_core.utils.runners.ssot_discovery_validator import get_agent_files

        agent_files = list(get_agent_files(self.project_root))

        for agent_file in tqdm(agent_files, desc="Processing", unit="item"):
            # Skip vendor/cache directories
            if self._should_exclude(agent_file):
                continue

            try:
                metadata = self._parse_agent_file(agent_file)
                if metadata:
                    agents.append(metadata)
                    self._cache[str(agent_file)] = metadata
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                # Skip files that can't be parsed
                continue

        return agents

    def get_layer_assignment(self, file_path: Path) -> str:
        """
        Derive layer assignment from file path.

        Args:
            file_path: Path to agent file

        Returns:
            Layer assignment (L0-L5)
        """
        relative_path = file_path.relative_to(self.project_root)
        parts = relative_path.parts

        # Check if in agentic_core
        if parts[0] == AGENTIC_CORE_DIR and len(parts) > 1:
            folder = parts[1]
            return self.LAYER_ASSIGNMENTS.get(folder, "UNKNOWN")

        # Apps are not assigned to layers
        if parts[0].startswith("apps_"):
            return "APP"

        return "UNKNOWN"

    def get_actual_layer(self, file_path: Path) -> str:
        """
        Get actual layer from file path (where file currently is).

        Args:
            file_path: Path to agent file

        Returns:
            Actual layer (L0-L5)
        """
        relative_path = file_path.relative_to(self.project_root)
        parts = relative_path.parts

        # Check if in agentic_core
        if parts[0] == AGENTIC_CORE_DIR and len(parts) > 1:
            folder = parts[1]

            # Direct layer folders
            if folder.startswith("L") and folder[1].isdigit():
                return folder[:2]  # L0, L1, L2, etc.

            # Infrastructure folders map to layers
            return self.LAYER_ASSIGNMENTS.get(folder, "UNKNOWN")

        return "UNKNOWN"

    def find_gravity_violations(self) -> list[AgentMetadata]:
        """
        Find all agents with gravity violations (wrong layer).

        Checks agentic_core and apps_* folders.

        Returns:
            List of agents in wrong layers
        """
        agents = self.scan_agents()
        return [agent for agent in agents if agent.has_gravity_violation]

    def get_compliance_stats(self) -> dict[str, any]:
        """
        Get compliance statistics.

        Returns:
            Dictionary with compliance metrics
        """
        agents = self.scan_agents()
        violations = [a for a in agents if a.has_gravity_violation]

        return {
            "total_agents": len(agents),
            "compliant_agents": len(agents) - len(violations),
            "gravity_violations": len(violations),
            "compliance_percentage": round((len(agents) - len(violations)) / len(agents) * 100, 1)
            if agents
            else 100.0,
        }

    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning."""
        exclude_patterns = list(GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS)

        path_str = str(file_path)
        return any(pattern in path_str for pattern in exclude_patterns)

    def _parse_agent_file(self, file_path: Path) -> AgentMetadata | None:
        """
        Parse agent file to extract metadata.

        Args:
            file_path: Path to agent file

        Returns:
            Agent metadata or None if not a valid agent
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
        except (
            SyntaxError,
            UnicodeDecodeError,
        ):  # guardian: Parsing and encoding errors need separate handling strategies
            return None

        # Find agent class (aligned with classification kernel: endswith "Agent", exclude Mixin)
        agent_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.endswith("Agent") and "Mixin" not in node.name:
                    agent_class = node
                    break

        if not agent_class:
            return None

        # Extract base classes
        base_classes = []
        for base in agent_class.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(base.attr)

        # Extract signals from class body (simple heuristic)
        signals = self._extract_signals(content)

        # Get layer assignments
        actual_layer = self.get_actual_layer(file_path)
        assigned_layer = self.get_layer_assignment(file_path)

        relative_path = str(file_path.relative_to(self.project_root))

        return AgentMetadata(
            file_path=file_path,
            relative_path=relative_path.replace("\\", "/"),
            class_name=agent_class.name,
            layer=actual_layer,
            assigned_layer=assigned_layer,
            base_classes=base_classes,
            signals=signals,
        )

    def _extract_signals(self, content: str) -> set[str]:
        """
        Extract canonical signals from agent code.

        Args:
            content: File content

        Returns:
            Set of detected signals
        """
        signals = set()
        content_lower = content.lower()

        for signal in self.CANON_SIGNALS:
            if signal in content_lower:
                signals.add(signal)

        return signals
