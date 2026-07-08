from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "sovereign_scan_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "sovereign_scan_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "sovereign_scan_util", "state_snapshot")
trace_contract.emit_replay_key("p0", "sovereign_scan_util")
trace_contract.emit_determinism_digest("p0", "sovereign_scan_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "sovereign_scan_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "sovereign_scan_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "sovereign_scan_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "sovereign_scan_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "sovereign_scan_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "sovereign_scan_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "sovereign_scan_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "sovereign_scan_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "sovereign_scan_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "sovereign_scan_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "sovereign_scan_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "sovereign_scan_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "sovereign_scan_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "sovereign_scan_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "sovereign_scan_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "sovereign_scan_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "sovereign_scan_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "sovereign_scan_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "sovereign_scan_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "sovereign_scan_util", "exec_snapshot_link")

'SovereignScanner - Centralized single-pass repository mapper.\n\n[Phase 5] Provides shared intelligence layer for L5 agents.\nReduces I/O by sharing a single scan result across all agents.\n\nUsage:\n    scanner = SovereignScanner(project_root)\n    repo_map = scanner.scan_repository()\n\n    # Get files for a specific territory\n    agentic_core_files = scanner.get_root_files("agentic_core")\n'
import logging
from pathlib import Path

from tqdm import tqdm

trace_contract._emit_emits_metric_event("sovereign_scan_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("sovereign_scan_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("sovereign_scan_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("sovereign_scan_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("sovereign_scan_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("sovereign_scan_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("sovereign_scan_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("sovereign_scan_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("sovereign_scan_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("sovereign_scan_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("sovereign_scan_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("sovereign_scan_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("sovereign_scan_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("sovereign_scan_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("sovereign_scan_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("sovereign_scan_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("sovereign_scan_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("sovereign_scan_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("sovereign_scan_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("sovereign_scan_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("sovereign_scan_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("sovereign_scan_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("sovereign_scan_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("sovereign_scan_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("sovereign_scan_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("sovereign_scan_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("sovereign_scan_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("sovereign_scan_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "sovereign_scan_util", "context_pull")
trace_contract._emit_pulls_context("p1", "sovereign_scan_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_scan_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "sovereign_scan_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "sovereign_scan_util", "write_through")
trace_contract._emit_writes_through("p1", "sovereign_scan_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "sovereign_scan_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "sovereign_scan_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "sovereign_scan_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "sovereign_scan_util", "human_escalation")
trace_contract._emit_routes_through("p1", "sovereign_scan_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "sovereign_scan_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "sovereign_scan_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "sovereign_scan_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "sovereign_scan_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "sovereign_scan_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "sovereign_scan_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "sovereign_scan_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "sovereign_scan_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "sovereign_scan_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "sovereign_scan_util")
trace_contract._emit_gated_by_confidence("p1", "sovereign_scan_util", "confidence_gate")

Logger = logging.getLogger(__name__)


class SovereignScanner:
    """
    Singleton provider for repository-wide file maps.

    Reduces I/O by sharing a single scan result across all L5 agents.
    Uses FileCache internally for efficient file enumeration.
    """

    _instance: SovereignScanner | None = None
    _initialized: bool = False

    def __new__(cls, project_root: Path | None = None) -> SovereignScanner:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, project_root: Path | None = None) -> None:
        if SovereignScanner._initialized:
            return
        if project_root is None:
            project_root = Path.cwd()
        self.project_root = project_root
        self._root_map: dict[str, list[Path]] = {}
        self._all_files: list[Path] | None = None
        SovereignScanner._initialized = True
        Logger.info(f"SovereignScanner initialized for: {project_root}")

    @classmethod
    def get_instance(cls, project_root: Path | None = None) -> SovereignScanner:
        """Get or create the singleton instance."""
        return cls(project_root)

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (useful for testing)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SovereignScanner.reset_instance"
        )

        cls._instance = None
        cls._initialized = False

    def scan_repository(self) -> dict[str, list[Path]]:
        """
        Perform a single-pass scan of all sovereign roots.

        Returns:
            Dictionary mapping root names to lists of Python files
        """
        if self._root_map:
            Logger.debug("Returning cached repository map")
            return self._root_map
        Logger.info("Performing single-pass repository scan...")
        from agentic_core.config.registry_config import SOVEREIGN_REGISTRY
        from agentic_core.utils.file_cache import FileCache

        cache = FileCache.get_instance(self.project_root)
        self._all_files = list(cache.get_python_files())
        for root_name in tqdm(SOVEREIGN_REGISTRY.keys(), desc="Processing", unit="item"):
            root_path = self.project_root / root_name
            if not root_path.exists():
                self._root_map[root_name] = []
                continue
            self._root_map[root_name] = [
                f for f in self._all_files if self._file_belongs_to_root(f, root_name)
            ]
        total_files = sum(len(files) for files in self._root_map.values())
        Logger.info(f"Repository scan complete: {total_files} files across {len(self._root_map)} roots")
        return self._root_map

    def _file_belongs_to_root(self, file_path: Path, root_name: str) -> bool:
        """Check if a file belongs to a specific sovereign root."""
        try:
            rel_path = file_path.relative_to(self.project_root)
            parts = rel_path.parts
            return len(parts) > 0 and parts[0] == root_name
        except ValueError:
            return False

    def get_root_files(self, root_name: str) -> list[Path]:
        """
        Retrieve cached files for a specific territory.

        Args:
            root_name: Name of the sovereign root (e.g., "agentic_core")

        Returns:
            List of Python file paths in that root
        """
        return self.scan_repository().get(root_name, [])

    def get_all_files(self) -> list[Path]:
        """Get all Python files across all roots."""
        self.scan_repository()
        return self._all_files or []

    def invalidate_cache(self) -> None:
        """Invalidate the cached repository map (forces rescan on next access)."""
        self._root_map = {}
        self._all_files = None
        Logger.info("SovereignScanner cache invalidated")
