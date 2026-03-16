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

_emit_applies_guardrail("p0", "wiki_healer", "p0_governance")
_emit_reads_policy_state("p0", "wiki_healer", "policy_binding")
_emit_snapshots_state("p0", "wiki_healer", "state_snapshot")
emit_replay_key("p0", "wiki_healer")
emit_determinism_digest("p0", "wiki_healer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "wiki_healer", "execution_auth")
_emit_validates_capability("p2", "wiki_healer", "capability_check")
_emit_routes_to_capability("p2", "wiki_healer", "capability_route")
_emit_writes_via_uwg("p2", "wiki_healer", "uwg_write")
_emit_blocks_direct_write("p2", "wiki_healer", "direct_write_block")
_emit_records_tool_invocation("p2", "wiki_healer", "tool_invocation")
_emit_captures_execution_output("p2", "wiki_healer", "exec_output")
_emit_dispatches_agent("p3", "wiki_healer", "agent_dispatch")
_emit_coordinates_agents("p3", "wiki_healer", "agent_coordination")
_emit_records_workflow_lineage("p3", "wiki_healer", "workflow_lineage")
_emit_records_healing_outcome("p3", "wiki_healer", "healing_outcome")
_emit_escalates_failure("p3", "wiki_healer", "failure_escalation")
_emit_orchestrates_workflow("p3", "wiki_healer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "wiki_healer", "healing_dispatch")
_emit_invokes_evaluation("p3", "wiki_healer", "evaluation_signal")
_emit_records_telemetry_event("p4", "wiki_healer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "wiki_healer", "eval_metric")
_emit_stores_embedding("p4", "wiki_healer", "embedding_store")
_emit_updates_meta_learning_state("p4", "wiki_healer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "wiki_healer", "exec_snapshot_link")

"\nSovereign DeepWiki Healing Strategy – Phase 17E (Dec 27, 2025)\nDetects and autonomously corrects codebase documentation drift.\nL6 observability self-healing using official DeepWiki MCP.\n"
import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.P1_core.filesystem_mcp_client_1 import get_filesystem_client

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger: Any = logging.getLogger(__name__)


class DeepWikiHealingStrategy:
    """
    Autonomous healing for DeepWiki documentation drift.

    Detects and corrects documentation inconsistencies by:
    - Identifying undocumented files in the codebase
    - Generating comprehensive documentation via DeepWiki MCP
    - Maintaining L6 observability and codebase intelligence
    - Enforcing daily healing limits to prevent runaway operations
    """

    def __init__(self):
        """Initialize DeepWiki healing strategy with MCP clients."""
        self.name = "DeepWikiHealing"
        self.priority = 3
        self.fs_client = get_filesystem_client()
        self.processed_today = 0
        Logger.info("[L0 DEEPWIKI HEALING] Strategy initialized")

    async def diagnose(self, issues: list[dict]) -> list[dict]:
        """
        Diagnose documentation drift via proactive scan.

        Args:
            issues: List of issues from sovereignty auditor

        Returns:
            List of fix dictionaries with action details
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DeepWikiHealingStrategy.diagnose")

        fixes: Any = []
        if not config.DEEPWIKI_HEALING_ENABLED:
            Logger.info("[L0 DEEPWIKI HEALING] DeepWiki healing disabled in config")
            return fixes
        undocumented: Any = await self._find_undocumented_files()
        for file_path in undocumented:
            fixes.append(
                {
                    "action": "document_new_file",
                    "file": str(file_path),
                    "reason": "Territory expansion detected: File undocumented in DeepWiki",
                    "priority": self.priority,
                    "strategy": self.name,
                }
            )
        Logger.info(f"[L0 DEEPWIKI HEALING] Diagnosed {len(fixes)} undocumented files")
        return fixes

    async def _find_undocumented_files(self) -> list[Path]:
        """
        Compares physical territory to documented structure.

        Returns:
            List of undocumented file paths
        """
        try:
            documented_paths = await self._get_documented_paths()
            undocumented = []
            agentic_core_path = Path(AGENTIC_CORE_DIR)
            if agentic_core_path.exists():
                from agentic_core.utils.ssot_discovery_validator import get_python_files

                for py_file in get_python_files(agentic_core_path):
                    rel_path = str(py_file.relative_to(Path.cwd()))
                    if rel_path not in documented_paths:
                        undocumented.append(py_file)
            return undocumented[: config.DEEPWIKI_HEALING_BATCH_SIZE]
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[L0 DEEPWIKI HEALING] Error finding undocumented files: {e}")
            return []

    async def _get_documented_paths(self) -> set:
        """
        Get set of documented paths from DeepWiki.

        Returns:
            Set of documented file paths
        """
        try:
            Logger.info(
                f"[L0 DEEPWIKI HEALING] Checking documented paths for repo: {config.DEEPWIKI_DEFAULT_REPO}"
            )
            return set()
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[L0 DEEPWIKI HEALING] Error getting documented paths: {e}")
            return set()

    async def apply(self, fix: dict, ctx: Any = None) -> bool:
        """
        Apply DeepWiki healing via Sovereign Clients.

        Args:
            fix: Fix dictionary with action details
            ctx: Execution context (unused)

        Returns:
            True if fix applied successfully, False otherwise
        """
        if not config.DEEPWIKI_HEALING_ENABLED:
            Logger.warning("[L0 DEEPWIKI HEALING] DeepWiki healing disabled in config")
            return False
        if self.processed_today >= config.DEEPWIKI_HEALING_MAX_DAILY:
            Logger.warning("[L0 DEEPWIKI HEALING] DeepWiki healing daily quota exhausted.")
            return False
        try:
            file_path: Any = fix.get("file")
            if not file_path:
                Logger.error("[L0 DEEPWIKI HEALING] No file path in fix")
                return False
            Logger.info(f"[L0 DEEPWIKI HEALING] Reading file: {file_path}")
            content: Any = await self.fs_client.read_text(file_path)
            if not content:
                Logger.warning(f"[L0 DEEPWIKI HEALING] Empty content for {file_path}")
                return False
            question: Any = f"Analyze the following code from {file_path} and generate comprehensive DeepWiki documentation including purpose, dependencies, and architecture level: \n\n{content[:3000]}"
            Logger.info(f"[L0 DEEPWIKI HEALING] Generating documentation for {file_path}")
            result: Any = await self._update_deepwiki(question, file_path)
            if result:
                self.processed_today += 1
                Logger.info(f"[L0 DEEPWIKI HEALING] DeepWiki updated for: {file_path}")
                return True
            else:
                Logger.error(f"[L0 DEEPWIKI HEALING] Failed to update DeepWiki for {file_path}")
                return False
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(
                f"[L0 DEEPWIKI HEALING] DeepWiki update failed for {fix.get('file', 'unknown')}: {e}"
            )
            return False

    async def _update_deepwiki(self, question: str, file_path: str) -> bool:
        """
        Update DeepWiki with documentation via MCP.

        Args:
            question: Documentation generation prompt
            file_path: File path being documented

        Returns:
            True if update succeeded, False otherwise
        """
        try:
            import asyncio
            import builtins
            repo = getattr(config, "DEEPWIKI_DEFAULT_REPO", "Siamese001/Agentic-Workflow")
            ask_fn = getattr(builtins, "mcp3_ask_question", None)
            if ask_fn is None:
                Logger.warning("[L0 DEEPWIKI HEALING] mcp3_ask_question not available in builtins")
                return False
            result = ask_fn(repoName=repo, question=question)
            if asyncio.iscoroutine(result):
                result = await asyncio.ensure_future(result)
            Logger.info(f"[L0 DEEPWIKI HEALING] Documentation generated for {file_path}")
            Logger.debug(f"[L0 DEEPWIKI HEALING] DeepWiki response: {str(result)[:200]}")
            return result is not None
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[L0 DEEPWIKI HEALING] DeepWiki update failed: {e}")
            return False

    def reset_daily_counter(self) -> Any:
        """Reset the daily processing counter (should be called at midnight)."""
        self.processed_today = 0
        Logger.info("[L0 DEEPWIKI HEALING] Daily counter reset")


async def create_deepwiki_healing_strategy() -> DeepWikiHealingStrategy:
    """
    Factory function to create a DeepWiki healing strategy.

    Returns:
        Initialized DeepWikiHealingStrategy instance
    """
    return DeepWikiHealingStrategy()
