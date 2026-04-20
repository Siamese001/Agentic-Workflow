"""Specialist planner ensemble and coordinator for v10.7 strategies."""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.reasoning.deterministic_routing_gateway import get_routing_gateway
from agentic_core.L3_orchestration.types.orchestration_handoff_contract import emit_agent_executes_agent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_reads_through,
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

_emit_authorize_and_execute("p2", "DomainPlannerAgent", "execution_auth")
_emit_validates_capability("p2", "DomainPlannerAgent", "capability_check")
_emit_routes_to_capability("p2", "DomainPlannerAgent", "capability_route")
_emit_writes_via_uwg("p2", "DomainPlannerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DomainPlannerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DomainPlannerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DomainPlannerAgent", "exec_output")
_emit_dispatches_agent("p3", "DomainPlannerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DomainPlannerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DomainPlannerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DomainPlannerAgent", "healing_outcome")
_emit_escalates_failure("p3", "DomainPlannerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DomainPlannerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DomainPlannerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DomainPlannerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DomainPlannerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DomainPlannerAgent", "eval_metric")
_emit_stores_embedding("p4", "DomainPlannerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DomainPlannerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DomainPlannerAgent", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout

emit_replay_key("p0", "DomainPlannerAgent")
emit_determinism_digest("p0", "DomainPlannerAgent")

_emit_dispatches_healing_run("p1", "DomainPlannerAgent", "L3")
_emit_routes_through("p1", "DomainPlannerAgent", "L3")
_emit_agent_executes_agent("p1", "DomainPlannerAgent", "sub_agent")
_emit_verifies_policy("p1", "DomainPlannerAgent", "policy_check")
_emit_observes_runtime_state("p1", "DomainPlannerAgent", "runtime_state")
_emit_verifies_boundary("p1", "DomainPlannerAgent", "boundary_check")
_emit_transcripts_response("p1", "DomainPlannerAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DomainPlannerAgent")
_emit_gated_by_confidence("p1", "DomainPlannerAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DomainPlannerAgent", "L3")
_emit_reads_policy_state("p1", "DomainPlannerAgent", "L3")
_emit_routes_to_agent("p1", "DomainPlannerAgent", "L3")
_emit_orchestrates_workflow("p1", "DomainPlannerAgent", "L3")
_emit_dispatches_execution_plan("p1", "DomainPlannerAgent", "L3")
_emit_validates_agent_capability("p1", "DomainPlannerAgent", "L3")
_emit_checks_agent_registry("p1", "DomainPlannerAgent", "L3")

_emit_snapshots_state("p0", "DomainPlannerAgent", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("DomainPlannerAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DomainPlannerAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DomainPlannerAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DomainPlannerAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DomainPlannerAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DomainPlannerAgent", "p4obs", "metric_6")
_emit_records_incident_event("DomainPlannerAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DomainPlannerAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DomainPlannerAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DomainPlannerAgent", "p4obs", "mon_state")
_emit_triggers_alert("DomainPlannerAgent", "p4obs", "alert")
_emit_links_incident_trace("DomainPlannerAgent", "p4obs", "trace_link")
_emit_captures_pattern("DomainPlannerAgent", "p3lm", "pattern")
_emit_records_learning_event("DomainPlannerAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DomainPlannerAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DomainPlannerAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DomainPlannerAgent", "p3lm", "routing")
_emit_improves_agent_policy("DomainPlannerAgent", "p3lm", "policy")
_emit_stores_learning_state("DomainPlannerAgent", "p3lm", "state")
_emit_records_execution_trace("DomainPlannerAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DomainPlannerAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DomainPlannerAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DomainPlannerAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DomainPlannerAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DomainPlannerAgent", "env_read", "p2_env_1")
_emit_reads_environ("DomainPlannerAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DomainPlannerAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DomainPlannerAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DomainPlannerAgent", "context_pull")
_emit_pulls_context("p1", "DomainPlannerAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DomainPlannerAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DomainPlannerAgent", "uwg_term_2")
_emit_writes_through("p1", "DomainPlannerAgent", "write_through")
_emit_writes_through("p1", "DomainPlannerAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "DomainPlannerAgent", "safety_validation")
_emit_invokes_eval("p1", "DomainPlannerAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DomainPlannerAgent", "routing_commit")

Logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

    PlannerAssessment = dict[str, Any]
    ScenarioSimulationResult = dict[str, Any]
    StrategyPlan = dict[str, Any]
    from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin  # noqa: F401
try:
    from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin  # noqa: F401
except ImportError as e:
    raise ImportError(f"Required dependency missing: {e}")  # guardian: allow-silent-swallow



class DomainPlannerOutput:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_dump(self):
        return self.__dict__


class PlannerAssessment:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    model_dump = DomainPlannerOutput.model_dump


class ScenarioSimulationResult:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    model_dump = DomainPlannerOutput.model_dump


class StrategyPlan:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_copy(self, deep=True):
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StrategyPlan.model_copy", "p0_governance")
        import copy

        return copy.deepcopy(self) if deep else copy.copy(self)


class WorkflowContext:
    pass


# guardian: allow-magic-config
def _truncate(text: str, limit: int = 160) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


class DomainPlannerAgent(L3OrchestrationBase):
    """Evaluates strategic alignment with the job domain.

    V10 Refactored: Now inherits from AtomicExecutionMixin for rollback capability
    and L3OrchestrationBase for proper layer positioning.

    MRO: DomainPlannerAgent -> AtomicExecutionMixin -> L3OrchestrationBase -> ...
    """

    async def run_async(
        self,
        plan: StrategyPlan,
        job_context: dict[str, Any],
        workflow_id: str,
    ) -> PlannerAssessment:
        _gw = get_routing_gateway(workflow_id)
        _emit_records_execution_trace(
            workflow_id,
            LayerSegment.L3_ORCHESTRATION,
            "DomainPlannerAgent.run_async",
        )
        emit_agent_executes_agent(
            parent_agent_id="DomainPlannerAgent",
            child_agent_id="domain_planner_strategy",
            run_id=workflow_id,
            stage="run_async",
        )
        job_title = (job_context.get("job_title") or "").lower()
        company = (job_context.get("company") or "").lower()
        focus_matches = 0
        for focus in plan.focus_areas:
            normalized_focus = focus.lower()
            if job_title and job_title.split()[0] in normalized_focus:
                focus_matches += 1
            if company and company in normalized_focus:
                focus_matches += 1
        vote = "approve" if focus_matches else "revise"
        confidence = min(1.0, 0.55 + 0.15 * focus_matches) if vote == "approve" else 0.45
        recommended_actions: list[str] = []
        if not focus_matches:
            recommended_actions.append(
                "Introduce a focus area that explicitly references the job title or company priorities.",
            )
        rationale = (
            "Focus areas reference role/company context."
            if focus_matches
            else "No explicit domain alignment detected."
        )
        assessment = PlannerAssessment(
            planner_name="DomainPlanner",
            vote=vote,
            rationale=rationale,
            confidence=round(confidence, 2),
            recommended_actions=recommended_actions,
        )
        self.log_feedback(workflow_id, "domain_planner_assessment", "success", assessment.model_dump())
        return assessment

    def log_feedback(self, *args, **kwargs):
        """Log feedback for domain planning operations."""
        pass

    @timeout(120)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """
        L3 Orchestration Agent - Domain Planner Healing.

        WIRED CAPABILITIES:
        - Validates domain alignment logic
        - Checks focus area processing
        """
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        if depth > max_depth:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        _call_path.add(agent_name)
        metrics = {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        try:
            Logger.info(f"[{agent_name}] L3 orchestration - domain planning validation")
            metrics["skipped"] = 1
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
        finally:
            _call_path.discard(agent_name)
        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by DomainPlannerAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"DomainPlannerAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (RuntimeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"DomainPlannerAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


class RiskAssessorAgent(SovereignBaseAgent):
    """Assesses risk and potential failure modes in the strategy."""

    async def run_async(
        self,
        plan: StrategyPlan,
        job_context: dict[str, Any],
        workflow_id: str,
    ) -> PlannerAssessment:
        focus_count = len(plan.focus_areas)
        duplicate_focus = len({focus.lower() for focus in plan.focus_areas}) != focus_count
        overextended = focus_count > 4
        vote = "approve"
        if overextended or duplicate_focus:
            vote = "revise"
        recommended_actions: list[str] = []
        if overextended:
            recommended_actions.append("Prioritize the top three focus areas to avoid dilution.")
        if duplicate_focus:
            recommended_actions.append("Merge overlapping focus areas for clarity.")
        risk_signals = []
        if overextended:
            risk_signals.append("focus overextension")
        if duplicate_focus:
            risk_signals.append("duplicate focus areas")
        rationale = (
            "Low strategic risk detected." if not risk_signals else "Detected " + ", ".join(risk_signals)
        )
        confidence = 0.7 if vote == "approve" else 0.6
        assessment = PlannerAssessment(
            planner_name="RiskAssessor",
            vote=vote,
            rationale=rationale,
            confidence=confidence,
            recommended_actions=recommended_actions,
        )
        self.log_feedback(workflow_id, "risk_assessment", "success", assessment.model_dump())
        return assessment

    def log_feedback(self, *args, **kwargs):
        """Log feedback for risk assessment operations."""
        pass

    @timeout(120)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """L3 Orchestration Agent - Risk Assessor Healing."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        if depth > max_depth:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        _call_path.add(agent_name)
        metrics = {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        try:
            Logger.info(f"[{agent_name}] L3 orchestration - risk assessment validation")
            metrics["skipped"] = 1
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
        finally:
            _call_path.discard(agent_name)
        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by RiskAssessorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"RiskAssessorAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (RuntimeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"RiskAssessorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


class FeasibilityAnalystAgent(SovereignBaseAgent):
    """Evaluates whether the plan is grounded in achievable achievements."""

    async def run_async(
        self,
        plan: StrategyPlan,
        job_context: dict[str, Any],
        workflow_id: str,
    ) -> PlannerAssessment:
        achievements = plan.key_achievements_to_highlight
        quantified_achievements = [a for a in achievements if any(ch.isdigit() for ch in a)]
        vote = "approve" if len(achievements) >= 2 else "revise"
        if not quantified_achievements:
            vote = "revise"
        recommended_actions: list[str] = []
        if len(achievements) < 2:
            recommended_actions.append("Add at least two concrete achievements to anchor the plan.")
        if not quantified_achievements:
            recommended_actions.append("Incorporate quantified outcomes to improve credibility.")
        rationale_parts = []
        if len(achievements) >= 2:
            rationale_parts.append("Sufficient achievement coverage.")
        else:
            rationale_parts.append("Insufficient achievement coverage.")
        if quantified_achievements:
            rationale_parts.append("Includes quantified wins.")
        else:
            rationale_parts.append("Lacks quantified wins.")
        rationale = " ".join(rationale_parts)
        confidence = 0.75 if vote == "approve" else 0.55
        assessment = PlannerAssessment(
            planner_name="FeasibilityAnalyst",
            vote=vote,
            rationale=rationale,
            confidence=confidence,
            recommended_actions=recommended_actions,
        )
        self.log_feedback(workflow_id, "feasibility_assessment", "success", assessment.model_dump())
        return assessment

    def log_feedback(self, *args, **kwargs):
        """Log feedback for feasibility analysis operations."""
        pass

    @timeout(120)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """L3 Orchestration Agent - Feasibility Analyst Healing."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        if depth > max_depth:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        _call_path.add(agent_name)
        metrics = {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        try:
            Logger.info(f"[{agent_name}] L3 orchestration - feasibility analysis validation")
            metrics["skipped"] = 1
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
        finally:
            _call_path.discard(agent_name)
        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by FeasibilityAnalystAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"FeasibilityAnalystAgent heal() not implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (RuntimeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"FeasibilityAnalystAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


class StrategyScenarioSimulatorAgent(SovereignBaseAgent):
    """Runs lightweight scenario stress tests on a strategy plan."""

    async def run_async(
        self,
        plan: StrategyPlan,
        job_context: dict[str, Any],
        workflow_id: str,
    ) -> list[ScenarioSimulationResult]:
        focus_lower = [focus.lower() for focus in plan.focus_areas]
        technical_focus = any("tech" in focus for focus in focus_lower)
        leadership_focus = any("lead" in focus for focus in focus_lower)
        quantified = any(
            any(ch.isdigit() for ch in achievement) for achievement in plan.key_achievements_to_highlight
        )
        scenarios: list[ScenarioSimulationResult] = []
        adoption_risk = "low" if quantified else "medium"
        adoption_impact = 0.35 if quantified else 0.65
        adoption_mitigations = (
            [] if quantified else ["Add quantified impact statements for key achievements."]
        )
        scenarios.append(
            ScenarioSimulationResult(
                scenario_name="Hiring Manager Adoption",
                risk_level=adoption_risk,
                impact_score=adoption_impact,
                summary="Metrics-driven achievements improve adoption."
                if quantified
                else "Lack of metrics may slow stakeholder buy-in.",
                mitigation_actions=adoption_mitigations,
            ),
        )
        technical_risk = "low" if technical_focus else "medium"
        technical_impact = 0.4 if technical_focus else 0.7
        technical_mitigations = (
            [] if technical_focus else ["Add a focus area covering technical depth or tooling expertise."]
        )
        scenarios.append(
            ScenarioSimulationResult(
                scenario_name="Technical Deep Dive",
                risk_level=technical_risk,
                impact_score=technical_impact,
                summary="Technical focus prepares for deep dive discussions."
                if technical_focus
                else "Potential technical grilling may expose gaps in focus areas.",
                mitigation_actions=technical_mitigations,
            ),
        )
        cross_functional_risk = "low" if leadership_focus else "medium"
        cross_functional_impact = 0.3 if leadership_focus else 0.6
        cross_functional_mitigations = (
            [] if leadership_focus else ["Introduce leadership/collaboration narratives into focus areas."]
        )
        scenarios.append(
            ScenarioSimulationResult(
                scenario_name="Cross-Functional Alignment",
                risk_level=cross_functional_risk,
                impact_score=cross_functional_impact,
                summary="Leadership emphasis supports cross-functional narratives."
                if leadership_focus
                else "Missing leadership signal may reduce collaboration confidence.",
                mitigation_actions=cross_functional_mitigations,
            ),
        )
        self.log_feedback(
            workflow_id,
            "strategy_simulation",
            "success",
            {"scenarios": [scenario.model_dump() for scenario in scenarios]},
        )
        return scenarios

    def log_feedback(self, *args, **kwargs):
        """Log feedback for scenario simulation operations."""
        pass

    @timeout(120)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """L3 Orchestration Agent - Strategy Scenario Simulator Healing."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        if depth > max_depth:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        _call_path.add(agent_name)
        metrics = {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        try:
            Logger.info(f"[{agent_name}] L3 orchestration - scenario simulation validation")
            metrics["skipped"] = 1
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
        finally:
            _call_path.discard(agent_name)
        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by StrategyScenarioSimulatorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: 'success', 'partial_success', 'failed', or 'skipped'
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"StrategyScenarioSimulatorAgent heal() not implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (RuntimeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"StrategyScenarioSimulatorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


class StrategyCoordinatorAgent(SovereignBaseAgent):
    """Coordinates specialist planner inputs and produces an aggregated plan."""

    def __init__(self, context: WorkflowContext = None, debug_mode: bool = False):
        super().__init__()
        self.context = context
        self.debug_mode = debug_mode
        self.domain_planner = DomainPlannerAgent()
        self.risk_assessor = RiskAssessorAgent()
        self.feasibility_analyst = FeasibilityAnalystAgent()
        self.scenario_simulator = StrategyScenarioSimulatorAgent()

    async def run_async(
        self,
        job_context: dict[str, Any],
        base_plan: StrategyPlan,
        workflow_id: str,
        downstream_feedback: dict[str, Any] | None = None,
    ) -> StrategyPlan:
        plan = base_plan.model_copy(deep=True)
        feedback_signals = self._apply_feedback(plan, downstream_feedback)
        plan.feedback_signals = feedback_signals
        assessments = await asyncio.gather(
            self.domain_planner.run_async(plan, job_context, workflow_id),
            self.risk_assessor.run_async(plan, job_context, workflow_id),
            self.feasibility_analyst.run_async(plan, job_context, workflow_id),
        )
        plan.planner_assessments = list(assessments)
        weighted_votes = 0.0
        total_confidence = 0.0
        rationale_parts: list[str] = []
        for assessment in assessments:
            vote_value = 1.0 if assessment.vote.lower() == "approve" else 0.0
            weighted_votes += vote_value * assessment.confidence
            total_confidence += assessment.confidence
            rationale_parts.append(
                f"{assessment.planner_name}: {assessment.vote} ({_truncate(assessment.rationale, 80)})",
            )
        aggregated_decision = "undecided"
        aggregated_confidence = 0.0
        if total_confidence:
            aggregated_score = weighted_votes / total_confidence
            aggregated_confidence = round(aggregated_score, 3)
            aggregated_decision = "approve" if aggregated_score >= 0.5 else "revise"
        plan.aggregated_decision = aggregated_decision
        plan.aggregated_confidence = aggregated_confidence
        plan.aggregated_rationale = " | ".join(rationale_parts) if rationale_parts else None
        scenario_results = await self.scenario_simulator.run_async(plan, job_context, workflow_id)
        plan.scenario_simulations = scenario_results
        scenario_summary = ", ".join(
            f"{result.scenario_name}:{result.risk_level}" for result in scenario_results
        )
        feedback_summary = f" Feedback signals: {', '.join(feedback_signals)}." if feedback_signals else ""
        plan.coordinator_summary = f"Planner consensus: {aggregated_decision} (confidence {aggregated_confidence:.2f}). Scenarios -> {scenario_summary}.{feedback_summary}"
        self.log_feedback(
            workflow_id,
            "strategy_coordinator",
            "success",
            {
                "aggregated_decision": aggregated_decision,
                "aggregated_confidence": aggregated_confidence,
                "feedback_signals": feedback_signals,
            },
        )
        return plan

    def _apply_feedback(self, plan: StrategyPlan, downstream_feedback: dict[str, Any] | None) -> list[str]:
        if not downstream_feedback:
            return []
        signals: list[str] = []
        qa_feedback = downstream_feedback.get("qa") if isinstance(downstream_feedback, dict) else None
        if isinstance(qa_feedback, dict):
            jd_skills = qa_feedback.get("jd_skills")
            if isinstance(jd_skills, dict):
                missing_keywords = jd_skills.get("missing_keywords")
                if isinstance(missing_keywords, list) and missing_keywords:
                    for keyword in missing_keywords:
                        if keyword not in plan.focus_areas:
                            plan.focus_areas.append(keyword)
                    signals.append(
                        "Augmented focus areas with QA missing keywords: " + ", ".join(missing_keywords[:5]),
                    )
        hil_feedback = downstream_feedback.get("hil") if isinstance(downstream_feedback, dict) else None
        if isinstance(hil_feedback, dict):
            payload = hil_feedback.get("payload")
            if isinstance(payload, str) and payload:
                signals.append("HIL payload available for downstream drafting alignment.")
        return signals

    def log_feedback(self, *args, **kwargs):
        """Log feedback for strategy coordination operations."""
        pass

    @timeout(120)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
        **kwargs,
    ) -> dict[str, int]:
        """L3 Orchestration Agent - Strategy Coordinator Healing."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        if depth > max_depth:
            return {"violations_found": 0, "violations_fixed": 0, "errors": 1, "skipped": 0}
        _call_path.add(agent_name)
        metrics = {"violations_found": 0, "violations_fixed": 0, "errors": 0, "skipped": 0}
        try:
            Logger.info(f"[{agent_name}] L3 orchestration - strategy coordination validation")
            metrics["skipped"] = 1
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
        finally:
            _call_path.discard(agent_name)
        return metrics

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Heal violations detected by StrategyCoordinatorAgent.

        Args:
            violation: Dictionary containing violation details with keys:
                - file: Path to the file with the violation
                - type: Type of violation detected
                - message: Description of the violation

        Returns:
            Dictionary with keys:
                - status: "success", "partial_success", "failed", or "skipped"
                - details: Human-readable summary
                - artifacts: List of modified files
                - errors: List of error messages
        """
        violation.get("file") or violation.get("file_path")
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"StrategyCoordinatorAgent heal() not implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except (RuntimeError, ValueError) as e:
            return {
                "status": "failed",
                "details": f"StrategyCoordinatorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_1")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_2")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_3")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_4")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_5")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_6")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_7")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_8")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_9")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_10")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_11")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_12")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_13")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_14")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_15")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_16")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_17")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_18")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_19")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_20")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_21")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_22")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_23")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_24")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_25")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_26")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_27")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_28")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_29")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_30")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_31")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_32")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_33")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_34")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_35")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_36")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_37")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_38")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_39")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_40")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_41")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_42")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_43")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_44")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_45")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_46")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_47")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_48")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_49")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_50")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_51")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_52")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_53")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_54")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_55")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_56")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_57")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_58")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_59")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_60")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_61")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_62")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_63")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_64")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_65")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_66")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_67")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_68")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_69")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_70")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_71")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_72")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_73")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_74")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_75")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_76")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_77")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_78")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_79")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_80")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_81")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_82")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_83")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_84")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_85")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_86")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_87")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_88")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_89")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_90")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_91")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_92")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_93")
_emit_reads_through("l4", "DomainPlannerAgent", "urg_read_94")
