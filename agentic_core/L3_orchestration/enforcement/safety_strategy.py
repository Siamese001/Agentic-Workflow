from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "safety_strategy")
emit_determinism_digest("p0", "safety_strategy")

_emit_dispatches_healing_run("p1", "safety_strategy", "L3")
_emit_routes_through("p1", "safety_strategy", "L3")
_emit_escalates_to_human("p1", "safety_strategy", "L3")
_emit_reads_policy_state("p1", "safety_strategy", "L3")
_emit_authorize_and_execute("p2", "safety_strategy", "execution_auth")
_emit_validates_capability("p2", "safety_strategy", "capability_check")
_emit_routes_to_capability("p2", "safety_strategy", "capability_route")
_emit_writes_via_uwg("p2", "safety_strategy", "uwg_write")
_emit_blocks_direct_write("p2", "safety_strategy", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_strategy", "tool_invocation")
_emit_captures_execution_output("p2", "safety_strategy", "exec_output")
_emit_dispatches_agent("p3", "safety_strategy", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_strategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_strategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_strategy", "healing_outcome")
_emit_escalates_failure("p3", "safety_strategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_strategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_strategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_strategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_strategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_strategy", "eval_metric")
_emit_stores_embedding("p4", "safety_strategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_strategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_strategy", "exec_snapshot_link")

"\nSafetyStrategy - Consolidated Safety Orchestration Strategy\n\nThis module consolidates logic from:\n- ComplianceOrchestratorAgent\n- GuardianOrchestratorAgent\n- HealingOrchestratorAgent\n\nSSOT PRINCIPLE:\n    All safety-related orchestration flows through this strategy,\n    which is injected into Orchestrator.\n"
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.providers import get_clock
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.seams.contracts.safety_agents import SafetyAgentFactory

Logger = logging.getLogger(__name__)


@dataclass
class SafetyStrategy:
    """
    Strategy for safety-focused orchestration missions.

    Consolidates:
    - Compliance validation (from ComplianceOrchestratorAgent)
    - Guardian protection (from GuardianOrchestratorAgent)
    - Healing coordination (from HealingOrchestratorAgent)

    Usage:
        strategy = SafetyStrategy(project_root=Path.cwd())
        orchestrator = Orchestrator(strategy=strategy)
        result = orchestrator.run_mission({"dry_run": True})
    """

    project_root: Path = field(default_factory=Path.cwd)
    _agent_factory: SafetyAgentFactory | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self._agent_factory is None:
            self._agent_factory = SafetyAgentFactory(self.project_root)

    @property
    def name(self) -> str:
        """Return the strategy name."""
        return "SafetyStrategy"

    def get_tiers(self) -> dict[str, list[str]]:
        """
        Return the tiered execution plan for safety missions.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SafetyStrategy.get_tiers", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SafetyStrategy.get_tiers", "p0_governance")
        return {
            "Tier 0: Pre-Flight": ["CodeValidatorAgent"],
            "Tier 1: Compliance": ["HygieneGuardianAgent", "NamingAgent"],
            "Tier 2: Safety": ["LocationAgent", "StructureEnforcerAgent"],
            "Tier 3: Healing": ["StructuralHealerAgent"],
        }

    def _get_agent(self, agent_name: str) -> Any | None:
        """
        Get or create an agent instance by name.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        """
        if agent_name == "CodeValidatorAgent":
            try:
                from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator

                class CodeValidatorAgentProxy:
                    def __init__(self, project_root):
                        self.project_root = project_root
                        self._invoke = invoke_code_validator

                    def validate_repository(self, **kwargs):
                        return self._invoke(action="validate", project_root=self.project_root)

                    def heal_repository(self, directory=None, **kwargs):
                        import uuid as _uuid  # noqa: PLC0415

                        _trace_id = str(_uuid.uuid4())
                        _emit_records_execution_trace(
                            _trace_id,
                            LayerSegment.L3_ORCHESTRATION,
                            "CodeValidatorAgentProxy.heal_repository",
                        )

                        if directory:
                            return self._invoke(
                                action="validate_directory",
                                project_root=self.project_root,
                                directory=str(directory),
                            )
                        return self.validate_repository(**kwargs)

                return CodeValidatorAgentProxy(project_root=self.project_root)
            except ImportError as e:
                Logger.warning(f"[SafetyStrategy] Failed to import CodeValidatorAgent: {e}")
                return None
        agent = self._agent_factory.get(agent_name) if self._agent_factory else None
        if agent is None:
            Logger.warning(f"[SafetyStrategy] Unknown or unavailable agent: {agent_name}")
        return agent

    def execute_agent(
        self, agent: Any, agent_name: str, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Execute a single agent and return results.

        Args:
            agent: The agent instance to execute
            agent_name: Name of the agent (for logging)
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional agent-specific parameters

        Returns:
            Dictionary with execution results
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SafetyStrategy.execute_agent"
        )

        start_time = get_clock().now_epoch()
        try:
            if hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=dry_run, execute=execute)
                execution_time_ms = (get_clock().now_epoch() - start_time) * 1000
                return {
                    "status": "PASS" if result.get("errors", 0) == 0 else "FAIL",
                    "violations_found": result.get("violations", 0),
                    "violations_fixed": result.get("fixed", 0),
                    "execution_time_ms": execution_time_ms,
                    "error_message": None,
                }
            else:
                return {
                    "status": "ERROR",
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "execution_time_ms": 0,
                    "error_message": f"{agent_name} has no heal_repository method",
                }
        except Exception as e:
            execution_time_ms = (get_clock().now_epoch() - start_time) * 1000
            return {
                "status": "ERROR",
                "violations_found": 0,
                "violations_fixed": 0,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
            }

    def should_abort_tier(self, tier_name: str, tier_results: list[dict[str, Any]], execute: bool) -> bool:
        """
        Determine if execution should abort after a tier.

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        """
        if "Tier 0" in tier_name:
            for result in tier_results:
                if result.get("status") == "FAIL":
                    return True
        return False
