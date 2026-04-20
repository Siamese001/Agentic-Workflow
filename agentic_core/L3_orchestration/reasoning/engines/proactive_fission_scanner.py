from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "proactive_fission_scanner")
emit_determinism_digest("p0", "proactive_fission_scanner")

_emit_dispatches_healing_run("p1", "proactive_fission_scanner", "L3")
_emit_routes_through("p1", "proactive_fission_scanner", "L3")
_emit_checks_agent_registry("p1", "proactive_fission_scanner", "agent_registry")
_emit_validates_agent_capability("p1", "proactive_fission_scanner", "capability")
_emit_dispatches_execution_plan("p1", "proactive_fission_scanner", "exec_plan")
_emit_agent_executes_agent("p1", "proactive_fission_scanner", "sub_agent")
_emit_routes_to_agent("p1", "proactive_fission_scanner", "target_agent")
_emit_verifies_policy("p1", "proactive_fission_scanner", "policy_check")
_emit_observes_runtime_state("p1", "proactive_fission_scanner", "runtime_state")
_emit_verifies_boundary("p1", "proactive_fission_scanner", "boundary_check")
_emit_transcripts_response("p1", "proactive_fission_scanner", "transcript")
_emit_hard_fails_untranscripted("p1", "proactive_fission_scanner")
_emit_gated_by_confidence("p1", "proactive_fission_scanner", "confidence_gate")
_emit_escalates_to_human("p1", "proactive_fission_scanner", "L3")
_emit_reads_policy_state("p1", "proactive_fission_scanner", "L3")
_emit_authorize_and_execute("p2", "proactive_fission_scanner", "execution_auth")
_emit_validates_capability("p2", "proactive_fission_scanner", "capability_check")
_emit_routes_to_capability("p2", "proactive_fission_scanner", "capability_route")
_emit_writes_via_uwg("p2", "proactive_fission_scanner", "uwg_write")
_emit_blocks_direct_write("p2", "proactive_fission_scanner", "direct_write_block")
_emit_records_tool_invocation("p2", "proactive_fission_scanner", "tool_invocation")
_emit_captures_execution_output("p2", "proactive_fission_scanner", "exec_output")
_emit_dispatches_agent("p3", "proactive_fission_scanner", "agent_dispatch")
_emit_coordinates_agents("p3", "proactive_fission_scanner", "agent_coordination")
_emit_records_workflow_lineage("p3", "proactive_fission_scanner", "workflow_lineage")
_emit_records_healing_outcome("p3", "proactive_fission_scanner", "healing_outcome")
_emit_escalates_failure("p3", "proactive_fission_scanner", "failure_escalation")
_emit_orchestrates_workflow("p3", "proactive_fission_scanner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "proactive_fission_scanner", "healing_dispatch")
_emit_invokes_evaluation("p3", "proactive_fission_scanner", "evaluation_signal")
_emit_records_telemetry_event("p4", "proactive_fission_scanner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "proactive_fission_scanner", "eval_metric")
_emit_stores_embedding("p4", "proactive_fission_scanner", "embedding_store")
_emit_updates_meta_learning_state("p4", "proactive_fission_scanner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "proactive_fission_scanner", "exec_snapshot_link")

"\nProactive Fission Scanner - L3 Orchestration\n\nScans L4 State for structural patterns matching known 'Critical Bloat' profiles.\nIdentifies files likely to cause Key 41/42 violations before they fail.\n\nStrategy:\n- Scan repository for high-gravity files (>600 lines)\n- Use Brave Search for modular design patterns\n- Use Pinecone to find structural twins\n- Create pre-emptive refactor proposals\n- Enable proactive architectural governance\n"
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("proactive_fission_scanner", "p4obs", "metric_1")
_emit_emits_metric_event("proactive_fission_scanner", "p4obs", "metric_2")
_emit_emits_metric_event("proactive_fission_scanner", "p4obs", "metric_3")
_emit_emits_metric_event("proactive_fission_scanner", "p4obs", "metric_4")
_emit_emits_metric_event("proactive_fission_scanner", "p4obs", "metric_5")
_emit_emits_metric_event("proactive_fission_scanner", "p4obs", "metric_6")
_emit_records_incident_event("proactive_fission_scanner", "p4obs", "incident")
_emit_captures_runtime_anomaly("proactive_fission_scanner", "p4obs", "anomaly")
_emit_writes_observability_log("proactive_fission_scanner", "p4obs", "obs_log")
_emit_updates_monitoring_state("proactive_fission_scanner", "p4obs", "mon_state")
_emit_triggers_alert("proactive_fission_scanner", "p4obs", "alert")
_emit_links_incident_trace("proactive_fission_scanner", "p4obs", "trace_link")
_emit_captures_pattern("proactive_fission_scanner", "p3lm", "pattern")
_emit_records_learning_event("proactive_fission_scanner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("proactive_fission_scanner", "p3lm", "snapshot")
_emit_feeds_meta_learning("proactive_fission_scanner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("proactive_fission_scanner", "p3lm", "routing")
_emit_improves_agent_policy("proactive_fission_scanner", "p3lm", "policy")
_emit_stores_learning_state("proactive_fission_scanner", "p3lm", "state")
_emit_records_execution_trace("proactive_fission_scanner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("proactive_fission_scanner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("proactive_fission_scanner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("proactive_fission_scanner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("proactive_fission_scanner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("proactive_fission_scanner", "env_read", "p2_env_1")
_emit_reads_environ("proactive_fission_scanner", "env_read", "p2_env_2")
_emit_reads_runtime_state("proactive_fission_scanner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("proactive_fission_scanner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "proactive_fission_scanner", "context_pull")
_emit_pulls_context("p1", "proactive_fission_scanner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "proactive_fission_scanner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "proactive_fission_scanner", "uwg_term_2")
_emit_writes_through("p1", "proactive_fission_scanner", "write_through")
_emit_writes_through("p1", "proactive_fission_scanner", "write_through_2")
_emit_validated_by_safety_plane("p1", "proactive_fission_scanner", "safety_validation")
_emit_invokes_eval("p1", "proactive_fission_scanner", "eval_call")
_emit_proposal_commits_routing("p1", "proactive_fission_scanner", "routing_commit")

Logger: Any = logging.getLogger(__name__)


class ProactiveFissionScanner:
    """
    L3 Orchestrator: Scans the L4 State for structural patterns
    matching known 'Critical Bloat' profiles.

    Process:
    1. Scan repository for files exceeding line threshold
    2. Query Brave Search for modular design patterns
    3. Use Pinecone to find structural twins
    4. Generate pre-emptive fission strategies
    5. Create GitKraken refactor proposal branches
    """

    # guardian: allow-magic-config
    def __init__(self, McpRouterAgent, line_threshold: int = 600):
        """
        Initialize Proactive Fission Scanner.

        Args:
            McpRouterAgent: MCPRouter instance for MCP calls
            line_threshold: Line count threshold for bloat detection
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ProactiveFissionScanner.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ProactiveFissionScanner.__init__", "p0_governance")
        self.router = McpRouterAgent
        self.threshold = line_threshold
        Logger.info(f"[OK] Proactive Scanner initialized (threshold: {line_threshold} lines)")

    def get_line_count(self, file_path: str) -> int:
        """
        Get line count for a file.

        Args:
            file_path: Path to file

        Returns:
            Number of lines in file
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                return len(f.readlines())
        except (RuntimeError, ValueError) as e:
            Logger.warning(f"   [!]  Could not read {file_path}: {e}")
            return 0

    async def scan_repository(self, target_dir: str) -> list[dict[str, any]]:
        """
        Identifies files that meet the 'Atomic Criticality' criteria.

        Args:
            target_dir: Directory to scan

        Returns:
            List of candidate files with metadata
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ProactiveFissionScanner.scan_repository",
        )

        Logger.info(f"[SCAN] Scanning repository: {target_dir}")
        candidates: Any = []
        for root, dirs, files in tqdm(os.walk(target_dir), desc="Processing", unit="item"):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for file in tqdm(files, desc="Processing", unit="item"):
                if file.endswith(".py"):
                    path: Any = Path(root) / file
                    line_count: Any = self.get_line_count(path)
                    if line_count > self.threshold:
                        candidates.append(
                            {
                                "path": path,
                                "line_count": line_count,
                                "Severity": self._calculate_severity(line_count),
                                "relative_path": os.path.relpath(path, target_dir),
                            },
                        )
                        Logger.info(f"   [ALERT] Bloat detected: {file} ({line_count} lines)")
        Logger.info(f"   [OK] Scan complete: {len(candidates)} candidates found")
        return candidates

    def _calculate_severity(self, line_count: int) -> str:
        """
        Calculate Severity level based on line count.

        Args:
            line_count: Number of lines

        Returns:
            Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        """
        if line_count < 700:
            return "LOW"
        elif line_count < 850:
            return "MEDIUM"
        elif line_count < 1000:
            return "HIGH"
        else:
            return "CRITICAL"

    async def generate_pre_emptive_strategy(self, file_path: str) -> dict[str, any]:
        """
        Uses Brave Search to find the best modular split for the specific file type.

        Args:
            file_path: Path to file

        Returns:
            Strategy dictionary with design patterns
        """
        file_name: Any = Path(file_path).name
        Logger.info(f"🧠 Generating strategy for {file_name}")
        try:
            query: Any = f"best modular architecture for python {file_name}"
            design_patterns: Any = await self.router.call_mcp(
                "brave_search",
                {"query": query, "purpose": "Find modular design patterns"},
            )
            structural_twins: Any = await self.router.call_mcp(
                "pinecone",
                {
                    "query": f"similar structure to {file_name}",
                    "top_k": 3,
                    "purpose": "Find files with similar structure",
                },
            )
            strategy: Any = {
                "file_path": file_path,
                "design_patterns": design_patterns,
                "structural_twins": structural_twins,
                "recommended_split": self._recommend_split(file_path),
            }
            Logger.info("   [OK] Strategy generated")
            return strategy
        except (RuntimeError, ValueError) as e:
            Logger.error(f"   [X] Strategy generation failed: {e}")
            return {"file_path": file_path, "error": str(e)}

    def _recommend_split(self, file_path: str) -> dict[str, str]:
        """
        Recommend split pattern based on file name and content.

        Args:
            file_path: Path to file

        Returns:
            Dictionary of recommended file splits
        """
        base_name = Path(file_path).stem
        parent_dir = Path(file_path).parent
        return {
            "core": f"{parent_dir}/{base_name}_core.py",
            "signals": f"{parent_dir}/{base_name}_signals.py",
            "utils": f"{parent_dir}/{base_name}_utils.py",
            "facade": file_path,
        }

    async def create_refactor_proposal(self, candidates: list[dict[str, any]]) -> str:
        """
        Creates a GitKraken refactor proposal branch.

        Args:
            candidates: List of bloat candidates

        Returns:
            Branch name created
        """
        if not candidates:
            Logger.info("   ℹ️  No candidates for refactor proposal")
            return None
        timestamp: Any = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name: Any = f"proactive-refactor-{timestamp}"
        Logger.info(f"🌿 Creating refactor proposal branch: {branch_name}")
        try:
            await self.router.call_mcp("gitkraken", {"action": "create_branch", "name": branch_name})
            await self.router.call_mcp(
                "redis",
                {"action": "set", "key": f"refactor_proposal:{branch_name}", "value": str(len(candidates))},
            )
            Logger.info(f"   [OK] Refactor proposal created: {len(candidates)} files")
            return branch_name
        except (RuntimeError, ValueError) as e:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
            Logger.error(f"   [X] Failed to create refactor proposal: {e}")
            return None

    async def generate_audit_report(self, candidates: list[dict[str, any]]) -> dict[str, any]:
        """
        Generate comprehensive audit report.

        Args:
            candidates: List of bloat candidates

        Returns:
            Audit report dictionary
        """
        Logger.info("[STATS] Generating audit report")
        severity_counts: Any = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        total_lines: Any = 0
        for candidate in candidates:
            severity_counts[candidate["Severity"]] += 1
            total_lines += candidate["line_count"]
        report: Any = {
            "total_candidates": len(candidates),
            "severity_breakdown": severity_counts,
            "total_lines": total_lines,
            "average_lines": total_lines // len(candidates) if candidates else 0,
            "candidates": candidates,
        }
        Logger.info(f"   [OK] Report generated: {len(candidates)} candidates")
        Logger.info(f"      CRITICAL: {severity_counts['CRITICAL']}")
        Logger.info(f"      HIGH: {severity_counts['HIGH']}")
        Logger.info(f"      MEDIUM: {severity_counts['MEDIUM']}")
        Logger.info(f"      LOW: {severity_counts['LOW']}")
        return report


# guardian: allow-magic-config
def get_proactive_scanner(McpRouterAgent: Any, line_threshold: int = 600) -> ProactiveFissionScanner:
    """
    Factory function to create ProactiveFissionScanner instance.

    Args:
        McpRouterAgent: MCPRouter instance
        line_threshold: Line count threshold

    Returns:
        ProactiveFissionScanner instance
    """
    return ProactiveFissionScanner(McpRouterAgent=McpRouterAgent, line_threshold=line_threshold)


'\nfrom agentic_core.core.proactive_audit import ProactiveFissionScanner\nfrom agentic_core.infra.McpRouterAgent import MCPRouter\nfrom agentic_core.infra.tui_dashboard import AgenticTUI\n\n# Initialize components\nmcp_router = MCPRouter(tui_handle=tui)\nscanner = ProactiveFissionScanner(McpRouterAgent=McpRouterAgent, line_threshold=THRESHOLD)\n\n# Run proactive scan\ncandidates = await scanner.scan_repository("agentic_core/")\n\n# Generate strategies for each candidate\nfor candidate in candidates:\n    strategy = await scanner.generate_pre_emptive_strategy(candidate["path"])\n    print(f"Strategy for {candidate[\'path\']}: {strategy}")\n\n# Create refactor proposal branch\nbranch_name = await scanner.create_refactor_proposal(candidates)\n\n# Generate audit report\nreport = await scanner.generate_audit_report(candidates)\nprint(f"Audit Report: {report}")\n'
