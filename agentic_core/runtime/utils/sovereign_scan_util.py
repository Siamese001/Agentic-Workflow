from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "sovereign_scan_util", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_scan_util", "policy_binding")
_emit_snapshots_state("p0", "sovereign_scan_util", "state_snapshot")
emit_replay_key("p0", "sovereign_scan_util")
emit_determinism_digest("p0", "sovereign_scan_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "sovereign_scan_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_scan_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_scan_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_scan_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_scan_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_scan_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_scan_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_scan_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_scan_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_scan_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_scan_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_scan_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_scan_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_scan_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_scan_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_scan_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_scan_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_scan_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_scan_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_scan_util", "exec_snapshot_link")

'SovereignScanner - Centralized single-pass repository mapper.\n\n[Phase 5] Provides shared intelligence layer for L5 agents.\nReduces I/O by sharing a single scan result across all agents.\n\nUsage:\n    scanner = SovereignScanner(project_root)\n    repo_map = scanner.scan_repository()\n\n    # Get files for a specific territory\n    agentic_core_files = scanner.get_root_files("agentic_core")\n'
import logging
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignScanner.reset_instance")

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
        from agentic_core.utils.file_cache import FileCache

        from agentic_core.config.core.registry_config import SOVEREIGN_REGISTRY

        cache = FileCache.get_instance(self.project_root)
        self._all_files = list(cache.get_python_files())
        for root_name in SOVEREIGN_REGISTRY.keys():
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
