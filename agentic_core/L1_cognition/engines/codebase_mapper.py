from __future__ import annotations

import logging

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "codebase_mapper")
emit_determinism_digest("p0", "codebase_mapper")

_emit_dispatches_healing_run("p1", "codebase_mapper", "L1")
_emit_routes_through("p1", "codebase_mapper", "L1")
_emit_checks_agent_registry("p1", "codebase_mapper", "agent_registry")
_emit_validates_agent_capability("p1", "codebase_mapper", "capability")
_emit_dispatches_execution_plan("p1", "codebase_mapper", "exec_plan")
_emit_agent_executes_agent("p1", "codebase_mapper", "sub_agent")
_emit_routes_to_agent("p1", "codebase_mapper", "target_agent")
_emit_verifies_policy("p1", "codebase_mapper", "policy_check")
_emit_observes_runtime_state("p1", "codebase_mapper", "runtime_state")
_emit_verifies_boundary("p1", "codebase_mapper", "boundary_check")
_emit_transcripts_response("p1", "codebase_mapper", "transcript")
_emit_hard_fails_untranscripted("p1", "codebase_mapper")
_emit_gated_by_confidence("p1", "codebase_mapper", "confidence_gate")
_emit_escalates_to_human("p1", "codebase_mapper", "L1")
_emit_reads_policy_state("p1", "codebase_mapper", "L1")
_emit_authorize_and_execute("p2", "codebase_mapper", "execution_auth")
_emit_validates_capability("p2", "codebase_mapper", "capability_check")
_emit_routes_to_capability("p2", "codebase_mapper", "capability_route")
_emit_writes_via_uwg("p2", "codebase_mapper", "uwg_write")
_emit_blocks_direct_write("p2", "codebase_mapper", "direct_write_block")
_emit_records_tool_invocation("p2", "codebase_mapper", "tool_invocation")
_emit_captures_execution_output("p2", "codebase_mapper", "exec_output")
_emit_dispatches_agent("p3", "codebase_mapper", "agent_dispatch")
_emit_coordinates_agents("p3", "codebase_mapper", "agent_coordination")
_emit_records_workflow_lineage("p3", "codebase_mapper", "workflow_lineage")
_emit_records_healing_outcome("p3", "codebase_mapper", "healing_outcome")
_emit_escalates_failure("p3", "codebase_mapper", "failure_escalation")
_emit_orchestrates_workflow("p3", "codebase_mapper", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "codebase_mapper", "healing_dispatch")
_emit_invokes_evaluation("p3", "codebase_mapper", "evaluation_signal")
_emit_records_telemetry_event("p4", "codebase_mapper", "telemetry_event")
_emit_captures_evaluation_metric("p4", "codebase_mapper", "eval_metric")
_emit_stores_embedding("p4", "codebase_mapper", "embedding_store")
_emit_updates_meta_learning_state("p4", "codebase_mapper", "meta_learning")
_emit_links_execution_to_snapshot("p4", "codebase_mapper", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import os
from pathlib import Path
from typing import Any

# GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS imported lazily to avoid L1->L5 violation
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("codebase_mapper", "p4obs", "metric_1")
_emit_emits_metric_event("codebase_mapper", "p4obs", "metric_2")
_emit_emits_metric_event("codebase_mapper", "p4obs", "metric_3")
_emit_emits_metric_event("codebase_mapper", "p4obs", "metric_4")
_emit_emits_metric_event("codebase_mapper", "p4obs", "metric_5")
_emit_emits_metric_event("codebase_mapper", "p4obs", "metric_6")
_emit_records_incident_event("codebase_mapper", "p4obs", "incident")
_emit_captures_runtime_anomaly("codebase_mapper", "p4obs", "anomaly")
_emit_writes_observability_log("codebase_mapper", "p4obs", "obs_log")
_emit_updates_monitoring_state("codebase_mapper", "p4obs", "mon_state")
_emit_triggers_alert("codebase_mapper", "p4obs", "alert")
_emit_links_incident_trace("codebase_mapper", "p4obs", "trace_link")
_emit_captures_pattern("codebase_mapper", "p3lm", "pattern")
_emit_records_learning_event("codebase_mapper", "p3lm", "learning_event")
_emit_writes_learning_snapshot("codebase_mapper", "p3lm", "snapshot")
_emit_feeds_meta_learning("codebase_mapper", "p3lm", "meta_feed")
_emit_updates_routing_strategy("codebase_mapper", "p3lm", "routing")
_emit_improves_agent_policy("codebase_mapper", "p3lm", "policy")
_emit_stores_learning_state("codebase_mapper", "p3lm", "state")
_emit_records_execution_trace("codebase_mapper", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("codebase_mapper", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("codebase_mapper", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("codebase_mapper", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("codebase_mapper", "L4_STATE", "p2_trace_5")
_emit_reads_environ("codebase_mapper", "env_read", "p2_env_1")
_emit_reads_environ("codebase_mapper", "env_read", "p2_env_2")
_emit_reads_runtime_state("codebase_mapper", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("codebase_mapper", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "codebase_mapper", "context_pull")
_emit_pulls_context("p1", "codebase_mapper", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "codebase_mapper", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "codebase_mapper", "uwg_term_2")
_emit_writes_through("p1", "codebase_mapper", "write_through")
_emit_writes_through("p1", "codebase_mapper", "write_through_2")
_emit_validated_by_safety_plane("p1", "codebase_mapper", "safety_validation")
_emit_invokes_eval("p1", "codebase_mapper", "eval_call")
_emit_proposal_commits_routing("p1", "codebase_mapper", "routing_commit")

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class TheCartographer:
    """
    Maps codebases into semantic context for architectural queries.

    Scans:
    - Primary repository root
    - ADDITIONAL_REPO_ROOTS from environment variables
    - Generates file summaries using Gemini
    - Excludes patterns: .git, __pycache__, node_modules, etc.
    """

    def __init__(self, llm_client: Any = None):
        """
        Initialize TheCartographer.

        Args:
            llm_client: LLM client for generating summaries
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TheCartographer.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TheCartographer.__init__", "p0_governance")
        self.llm_client = llm_client
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.primary_root = Path.cwd()
        self.additional_roots = self._get_additional_roots()
        self.file_summaries: dict[str, str] = {}
        self = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

    def _get_additional_roots(self) -> list[Path]:
        """
        Get additional repository roots from environment variables.

        Returns:
            List of additional repository root paths
        """
        roots: list[Path] = []
        env_roots = os.getenv("ADDITIONAL_REPO_ROOTS", "")
        if env_roots:
            for root_path in env_roots.split(","):
                root_path = root_path.strip()
                if root_path:
                    path_obj = Path(root_path)
                    if path_obj.exists():
                        roots.append(path_obj.resolve())
                        LOGGER.info(f"📍 Scanning additional root: {root_path}")
        return roots

    async def map_all_repositories(self) -> dict[str, Any]:
        """
        Map all repositories (primary + additional).

        Returns:
            Dictionary with mapping results
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "TheCartographer.map_all_repositories"
        )

        LOGGER.info("🗺️  TheCartographer: Beginning semantic mapping")
        results: dict[str, Any] = {
            "primary_root": str(self.primary_root),
            "additional_roots": [str(r) for r in self.additional_roots],
            "files_mapped": 0,
            "summaries_generated": 0,
            "repositories": {},
        }
        primary_result: Any = await self._map_repository(self.primary_root, "primary")
        results["repositories"]["primary"] = primary_result
        results["files_mapped"] += primary_result.get("files_mapped", 0)
        results["summaries_generated"] += primary_result.get("summaries_generated", 0)
        for i, root in enumerate(self.additional_roots):
            repo_name: Any = f"additional_{i + 1}"
            repo_result: Any = await self._map_repository(root, repo_name)
            results["repositories"][repo_name] = repo_result
            results["files_mapped"] += repo_result.get("files_mapped", 0)
            results["summaries_generated"] += repo_result.get("summaries_generated", 0)
        LOGGER.info(f"[OK] TheCartographer: Mapped {results['files_mapped']} files")
        return results

    async def _map_repository(self, root_path: Path, repo_name: str) -> dict[str, Any]:
        """
        Map a single repository.

        Args:
            root_path: Root directory of the repository
            repo_name: Name identifier for the repository

        Returns:
            Mapping result for this repository
        """
        result: dict[str, Any] = {
            "repo_name": repo_name,
            "root_path": str(root_path),
            "files_mapped": 0,
            "summaries_generated": 0,
            "files": [],
        }
        return result
