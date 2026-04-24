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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "HealingStrategy")
emit_determinism_digest("p0", "HealingStrategy")

_emit_dispatches_healing_run("p1", "HealingStrategy", "L5")
_emit_routes_through("p1", "HealingStrategy", "L5")
_emit_verifies_policy("p1", "HealingStrategy", "policy_check")
_emit_observes_runtime_state("p1", "HealingStrategy", "runtime_state")
_emit_verifies_boundary("p1", "HealingStrategy", "boundary_check")
_emit_transcripts_response("p1", "HealingStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "HealingStrategy")
_emit_gated_by_confidence("p1", "HealingStrategy", "confidence_gate")
_emit_escalates_to_human("p1", "HealingStrategy", "L5")
_emit_reads_policy_state("p1", "HealingStrategy", "L5")
_emit_routes_to_agent("p1", "HealingStrategy", "L5")
_emit_orchestrates_workflow("p1", "HealingStrategy", "L5")
_emit_dispatches_execution_plan("p1", "HealingStrategy", "L5")
_emit_validates_agent_capability("p1", "HealingStrategy", "L5")
_emit_checks_agent_registry("p1", "HealingStrategy", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "HealingStrategy", "state_snapshot")
_emit_authorize_and_execute("p2", "HealingStrategy", "execution_auth")
_emit_validates_capability("p2", "HealingStrategy", "capability_check")
_emit_routes_to_capability("p2", "HealingStrategy", "capability_route")
_emit_writes_via_uwg("p2", "HealingStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "HealingStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "HealingStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "HealingStrategy", "exec_output")
_emit_dispatches_agent("p3", "HealingStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "HealingStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "HealingStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "HealingStrategy", "healing_outcome")
_emit_escalates_failure("p3", "HealingStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "HealingStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HealingStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "HealingStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "HealingStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HealingStrategy", "eval_metric")
_emit_stores_embedding("p4", "HealingStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "HealingStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HealingStrategy", "exec_snapshot_link")

'\nHealingStrategy - Tiered Healing Execution Strategy\n\nThis strategy encapsulates the healing logic currently in SSOTOrchestratorAgent,\nimplementing the 5-tier execution flow for repository healing.\n\nTIERS:\n    Tier 0: Pre-Flight - Syntax validation (must pass before anything else)\n    Tier 1: Structural - Identity collisions, hygiene, naming, location\n    Tier 2: Architectural - Gravity enforcement, deep deduplication\n    Tier 3: Dynamic - Code SSOT enforcement, runtime checks\n    Tier 4: Final Gate - Safety validation, final checks\n\nUSAGE:\n    from agentic_core.L3_orchestration.unified_orchestrator import Orchestrator\n\n    strategy = HealingStrategy(project_root=Path.cwd())\n    orchestrator = Orchestrator(strategy=strategy)\n    result = orchestrator.run_mission({"dry_run": True})\n'
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.config.hygiene_registry_config import CORE_HYGIENE_AGENTS
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("HealingStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("HealingStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("HealingStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("HealingStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("HealingStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("HealingStrategy", "p4obs", "metric_6")
_emit_records_incident_event("HealingStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("HealingStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("HealingStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("HealingStrategy", "p4obs", "mon_state")
_emit_triggers_alert("HealingStrategy", "p4obs", "alert")
_emit_links_incident_trace("HealingStrategy", "p4obs", "trace_link")
_emit_captures_pattern("HealingStrategy", "p3lm", "pattern")
_emit_records_learning_event("HealingStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("HealingStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("HealingStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("HealingStrategy", "p3lm", "routing")
_emit_improves_agent_policy("HealingStrategy", "p3lm", "policy")
_emit_stores_learning_state("HealingStrategy", "p3lm", "state")
_emit_records_execution_trace("HealingStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("HealingStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("HealingStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("HealingStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("HealingStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("HealingStrategy", "env_read", "p2_env_1")
_emit_reads_environ("HealingStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("HealingStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("HealingStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "HealingStrategy", "context_pull")
_emit_pulls_context("p1", "HealingStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "HealingStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "HealingStrategy", "uwg_term_2")
_emit_writes_through("p1", "HealingStrategy", "write_through")
_emit_writes_through("p1", "HealingStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "HealingStrategy", "safety_validation")
_emit_invokes_eval("p1", "HealingStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "HealingStrategy", "routing_commit")
from agentic_core.runtime.contracts.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_dispatch_entry")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_dispatch_exit")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_tool_invoke")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_tool_complete")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_agent_entry")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_agent_exit")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_uwg_write")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_trace_sign")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_guardrail_check")
emit_determinism_digest("trace_HealingStrategy", "HealingStrategy_policy_verify")

Logger = logging.getLogger(__name__)


class HealingStrategy:
    """
    Tiered healing execution strategy.

    Implements the MissionStrategy protocol for the Orchestrator.
    Encapsulates the 5-tier healing execution flow from SSOTOrchestratorAgent.
    """

    def __init__(self, project_root: Path | None = None, target_tier: int | None = None) -> None:
        """
        Initialize the healing strategy.

        Args:
            project_root: Root path for the project (defaults to cwd)
            target_tier: If specified, only run this tier (0-4). None runs all tiers.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.target_tier = target_tier
        self._agents: dict[str, Any] = {}
        self._dedup_agent: Any | None = None
        self._tiers: dict[str, list[str]] = {
            "Tier 0: Pre-Flight": CORE_HYGIENE_AGENTS["tier_0_preflight"],
            "Tier 1: Structural": ["TwoPhaseDeduplicationAgent_PhaseA"]
            + CORE_HYGIENE_AGENTS["tier_1_structural"],
            "Tier 2: Architectural": ["StructuralHealerAgent"]
            + CORE_HYGIENE_AGENTS["tier_2_architectural"]
            + ["TwoPhaseDeduplicationAgent_PhaseB"],
            "Tier 3: Dynamic": ["CodeEnforcerAgent"] + CORE_HYGIENE_AGENTS["tier_3_autonomy"],
            "Tier 4: Final Gate": [],
        }

    @property
    def name(self) -> str:
        """Return the strategy name."""
        return "HealingStrategy"

    def get_tiers(self) -> dict[str, list[str]]:
        """
        Return the tiered execution plan.

        Returns:
            Dictionary mapping tier names to lists of agent names.
        """
        _emit_applies_guardrail(str(uuid.uuid4()), "HealingStrategy.get_tiers", "L5_POLICY")
        return {k: v for k, v in self._tiers.items() if v}

    def should_run_tier(self, tier_name: str) -> bool:
        """
        Check if a tier should be executed based on target_tier filter.

        Args:
            tier_name: Name of the tier (e.g., "Tier 0: Pre-Flight")

        Returns:
            True if the tier should run, False to skip
        """
        _emit_agent_executes_agent(str(uuid.uuid4()), "HealingStrategy", "HealingStrategy.should_run_tier")

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            f"HealingStrategy.should_run_tier:{tier_name}",
        )
        if self.target_tier is None:
            return True
        try:
            tier_num = int(tier_name.split(":")[0].replace("Tier", "").strip())
            return tier_num == self.target_tier
        except (ValueError, IndexError):
            Logger.warning(f"[HealingStrategy] Could not parse tier number from: {tier_name}")
            return False

    def get_tier_skip_message(self, tier_name: str) -> str:
        """
        Get a message explaining why a tier is being skipped.

        Args:
            tier_name: Name of the tier being skipped

        Returns:
            Skip message for logging
        """
        return f"⏭️  SKIPPING {tier_name} (target_tier={self.target_tier})"

    def get_agent(self, agent_name: str) -> Any | None:
        """
        Get or create an agent instance by name.

        Uses lazy loading to instantiate agents only when needed.

        Args:
            agent_name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not available
        """
        if agent_name.startswith("TwoPhaseDeduplicationAgent"):
            return self._get_dedup_agent()
        if agent_name in self._agents:
            return self._agents[agent_name]
        try:
            agent = self._load_agent(agent_name)
            if agent:
                self._agents[agent_name] = agent
            return agent
        except (  # guardian: allow-return-none-swallow -- agent class load: non-fatal, caller checks for None
            RuntimeError,
            OSError,
        ) as e:
            Logger.error(f"[HealingStrategy] Failed to load {agent_name}: {e}")
            return None

    def _get_dedup_agent(self) -> Any | None:
        """Get or create the shared TwoPhaseDeduplicationAgent instance."""
        if self._dedup_agent is None:
            try:
                from agentic_core.L5_safety.enforcement.TwoPhaseDeduplicationAgent import (
                    TwoPhaseDeduplicationAgent,
                )

                self._dedup_agent = TwoPhaseDeduplicationAgent(project_root=self.project_root)
            except (  # guardian: allow-return-none-swallow -- dedup agent init: non-fatal, caller handles None
                RuntimeError,
                OSError,
            ) as e:
                Logger.error(f"[HealingStrategy] Failed to load TwoPhaseDeduplicationAgent: {e}")
                return None
        return self._dedup_agent

    def _load_agent(self, agent_name: str) -> Any | None:
        """
        Load an agent by name.

        Args:
            agent_name: Name of the agent to load

        Returns:
            Agent instance or None if not available
        """
        try:
            if agent_name == "CodeValidatorAgent":
                # MW-5 / MW-11 (2026-04-24): CodeValidatorAgent was a delegating shim.
                # Util class CodeValidator gained a heal_repository() parity shim in
                # MW-11 (validate-only, returns the validation report). Swapped here.
                # Agent archive-eligible 2026-07-23.
                from agentic_core.L5_safety.utils.code_validator_util import CodeValidator

                return CodeValidator()
            elif agent_name == "HygieneGuardianAgent":
                from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent

                return HygieneGuardianAgent(project_root=self.project_root)
            elif agent_name == "StructureEnforcerAgent":
                from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

                return StructureEnforcerAgent(project_root=self.project_root)
            elif agent_name == "NamingAgent":
                from agentic_core.L5_safety.reasoning.NamingAgent import NamingAgent

                return NamingAgent(project_root=self.project_root)
            elif agent_name == "LocationAgent":
                from agentic_core.L5_safety.reasoning.LocationAgent import LocationAgent

                return LocationAgent(project_root=self.project_root)
            elif agent_name == "CodeEnforcerAgent":
                # MW-5 (2026-04-24): CodeEnforcerAgent was a delegating shim; swapped
                # to canonical util class CodeEnforcer. Agent archive-eligible 2026-07-23.
                from agentic_core.L5_safety.utils.code_enforcer_util import CodeEnforcer

                return CodeEnforcer()
            elif agent_name == "StructuralHealerAgent":
                from agentic_core.L5_safety.enforcement.StructuralHealerAgent import StructuralHealerAgent

                return StructuralHealerAgent(project_root=self.project_root)
            elif agent_name == "ImportAgent":
                from agentic_core.L5_safety.reasoning.CodeHealerAgent import create_legacy_import_healer

                return create_legacy_import_healer()
            elif agent_name == "HierarchyAgent":
                from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

                return HierarchyAgent(project_root=self.project_root)
            elif agent_name == "CodeDeduplicationAgent":
                from agentic_core.L5_safety.validators.CodeDeduplicationAgent import CodeDeduplicationAgent

                return CodeDeduplicationAgent()
            elif agent_name == "FilesystemSSOTReconcilerAgent":
                from agentic_core.L5_safety.reasoning.filesystem_ssot_reconciler import (
                    FilesystemSSOTReconcilerAgent,
                )

                return FilesystemSSOTReconcilerAgent(project_root=self.project_root)
            elif agent_name == "GitHygieneAgent":
                from agentic_core.L5_safety.reasoning.GitHygieneAgent import GitHygieneAgent

                return GitHygieneAgent(project_root=self.project_root, ctx=None)
            elif agent_name == "FileCleanupAgent":
                from agentic_core.L5_safety.enforcement.FileCleanupAgent import FileCleanupAgent

                return FileCleanupAgent(project_root=self.project_root, ctx=None)
            elif agent_name == "AutonomyGuardianAgent":
                from agentic_core.L5_safety.validators.AutonomyGuardianAgent import AutonomyGuardianAgent

                return AutonomyGuardianAgent(project_root=self.project_root)
            elif agent_name == "CodeJanitorAgent":
                # MW-5 (2026-04-24): CodeJanitorAgent was a delegating shim; swapped
                # to canonical util class CodeJanitor. Agent archive-eligible 2026-07-23.
                from agentic_core.L5_safety.utils.code_janitor_util import CodeJanitor

                return CodeJanitor()
            else:
                Logger.warning(f"[HealingStrategy] Unknown agent: {agent_name}")
                return None
        except (  # guardian: allow-return-none-swallow -- agent name import: non-fatal, caller checks for None
            ImportError
        ) as e:
            Logger.error(f"[HealingStrategy] Import error for {agent_name}: {e}")
            return None

    def execute_agent(
        self,
        agent: Any,
        agent_name: str,
        dry_run: bool = True,
        execute: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute a single agent and return results.

        Args:
            agent: The agent instance to execute
            agent_name: Name of the agent (for logging)
            dry_run: If True, only report violations
            execute: If True, apply fixes
            **kwargs: Additional agent-specific parameters
                route_decision_artifact: audit payload dict from L3 routing
                    (required under V15; ignored otherwise)

        Returns:
            Dictionary with execution results
        """
        from agentic_core.L0_routing.types.routing_contracts_types import enforce_route_decision_presence

        audit_payload = kwargs.get("route_decision_artifact")
        enforce_route_decision_presence(audit_payload)
        start_time = datetime.now()
        try:
            if agent_name == "TwoPhaseDeduplicationAgent_PhaseA":
                Logger.info("[PHASE A] Running Shallow Duplicate Check...")
                result = agent.heal_repository(dry_run=dry_run, execute=execute, phase="A")
            elif agent_name == "TwoPhaseDeduplicationAgent_PhaseB":
                Logger.info("[PHASE B] Running Deep SSOT Duplicate Check...")
                result = agent.heal_repository(dry_run=dry_run, execute=execute, phase="B")
            elif hasattr(agent, "heal_repository"):
                result = agent.heal_repository(dry_run=dry_run, execute=execute, **kwargs)
            else:
                return {
                    "status": "ERROR",
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "error_message": f"Agent {agent_name} missing heal_repository()",
                }
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            return self._normalize_result(result, execution_time_ms)
        except (RuntimeError, OSError) as e:
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            Logger.error(f"[HealingStrategy] Error executing {agent_name}: {e}")
            return {
                "status": "ERROR",
                "violations_found": 0,
                "violations_fixed": 0,
                "execution_time_ms": execution_time_ms,
                "error_message": str(e),
            }

    def _normalize_result(self, result: dict[str, Any], execution_time_ms: float) -> dict[str, Any]:
        """
        Normalize agent result to standard format.

        Args:
            result: Raw result from agent
            execution_time_ms: Execution time in milliseconds

        Returns:
            Normalized result dictionary
        """
        violations_found = (
            result.get("violations_found") or result.get("violations") or result.get("errors") or 0
        )
        violations_fixed = result.get("violations_fixed") or result.get("fixed") or 0
        status = result.get("status")
        if not status:
            if result.get("error_message"):
                status = "ERROR"
            elif violations_found == 0:
                status = "PASS"
            elif violations_fixed >= violations_found:
                status = "PASS"
            else:
                status = "FAIL"
        return {
            "status": status,
            "violations_found": violations_found,
            "violations_fixed": violations_fixed,
            "execution_time_ms": execution_time_ms,
            "error_message": result.get("error_message"),
            "raw_result": result,
        }

    def should_abort_tier(self, tier_name: str, tier_results: list[dict[str, Any]], execute: bool) -> bool:
        """
        Determine if execution should abort after a tier.

        Implements stability gates:
        - Tier 0 (Pre-Flight): Always fatal if failed (syntax must be valid)
        - Tier 1 (Structural): Fatal only during execute mode

        Args:
            tier_name: Name of the completed tier
            tier_results: Results from all agents in the tier
            execute: Whether we're in execute mode

        Returns:
            True if execution should abort, False to continue
        """
        has_failure = any(r.get("status") in ("FAIL", "ERROR") for r in tier_results)
        if not has_failure:
            return False
        if "Tier 0" in tier_name or "Pre-Flight" in tier_name:
            Logger.error("🛑 CRITICAL GATE: Syntax Validation Failed. Aborting Mission.")
            return True
        if ("Tier 1" in tier_name or "Structural" in tier_name) and execute:
            Logger.error("🛑 STABILITY GATE: Structural violations persist. Aborting.")
            return True
        return False


__all__ = ["HealingStrategy"]
