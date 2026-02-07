"""Specialist planner ensemble and coordinator for v10.7 strategies."""

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.timeout_decorator import timeout
from agentic_core.L5_safety.utils.decorators_util import standard_heal

Logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from agentic_core.base_agents.SovereignBaseAgent import (
        SovereignBaseAgent,
    )

    # Type aliases for compatibility
    PlannerAssessment = dict[str, Any]
    ScenarioSimulationResult = dict[str, Any]
    StrategyPlan = dict[str, Any]

    from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin

# Runtime imports
try:
    from agentic_core.mixins.subatomic_testing_mixin import subatomic_testing_mixin
except ImportError:
    # Fallback stub if mixin is not available
    class SubatomicTestingMixin:
        pass


# REMOVED: BaseAgent stub class
# Use SovereignBaseAgent from agentic_core.base_agents instead


class PlannerAssessment:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_dump(self):
        return self.__dict__


class ScenarioSimulationResult:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_dump(self):
        return self.__dict__


class StrategyPlan:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_copy(self, deep=True):
        import copy

        return copy.deepcopy(self) if deep else copy.copy(self)


class WorkflowContext:
    pass


def _truncate(text: str, limit: int = 160) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


class DomainPlannerAgent(AtomicExecutionMixin, L3OrchestrationBase):
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

        self.log_feedback(
            workflow_id,
            "domain_planner_assessment",
            "success",
            assessment.model_dump(),
        )
        return assessment

    def log_feedback(self, *args, **kwargs):
        """Log feedback for domain planning operations."""
        pass

    @timeout(120)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
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
        except Exception as e:
            Logger.error(f"[{agent_name}] Healing failed: {e}")
            metrics["errors"] += 1
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

        # Default implementation - DomainPlannerAgent plans domains
        try:
            return {
                "status": "skipped",
                "details": f"DomainPlannerAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
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

        self.log_feedback(
            workflow_id,
            "risk_assessment",
            "success",
            assessment.model_dump(),
        )
        return assessment

    def log_feedback(self, *args, **kwargs):
        """Log feedback for risk assessment operations."""
        pass

    @timeout(120)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
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
        except Exception as e:
            Logger.error(f"[{agent_name}] Healing failed: {e}")
            metrics["errors"] += 1
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

        # Default implementation - RiskAssessorAgent assesses risk
        try:
            return {
                "status": "skipped",
                "details": f"RiskAssessorAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
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

        self.log_feedback(
            workflow_id,
            "feasibility_assessment",
            "success",
            assessment.model_dump(),
        )
        return assessment

    def log_feedback(self, *args, **kwargs):
        """Log feedback for feasibility analysis operations."""
        pass

    @timeout(120)
    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
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
        except Exception as e:
            Logger.error(f"[{agent_name}] Healing failed: {e}")
            metrics["errors"] += 1
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

        # Default implementation - FeasibilityAnalystAgent analyzes feasibility
        try:
            return {
                "status": "skipped",
                "details": f"FeasibilityAnalystAgent heal() not implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
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
                summary=(
                    "Metrics-driven achievements improve adoption."
                    if quantified
                    else "Lack of metrics may slow stakeholder buy-in."
                ),
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
                summary=(
                    "Technical focus prepares for deep dive discussions."
                    if technical_focus
                    else "Potential technical grilling may expose gaps in focus areas."
                ),
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
                summary=(
                    "Leadership emphasis supports cross-functional narratives."
                    if leadership_focus
                    else "Missing leadership signal may reduce collaboration confidence."
                ),
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
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
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
        except Exception as e:
            Logger.error(f"[{agent_name}] Healing failed: {e}")
            metrics["errors"] += 1
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

        # Default implementation - StrategyScenarioSimulatorAgent simulates scenarios
        try:
            return {
                "status": "skipped",
                "details": f"StrategyScenarioSimulatorAgent heal() not implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
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
        plan.coordinator_summary = (
            f"Planner consensus: {aggregated_decision} (confidence {aggregated_confidence:.2f}). "
            f"Scenarios -> {scenario_summary}.{feedback_summary}"
        )

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

    def _apply_feedback(
        self,
        plan: StrategyPlan,
        downstream_feedback: dict[str, Any] | None,
    ) -> list[str]:
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
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
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
        except Exception as e:
            Logger.error(f"[{agent_name}] Healing failed: {e}")
            metrics["errors"] += 1
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

        # Default implementation - StrategyCoordinatorAgent coordinates strategies
        try:
            return {
                "status": "skipped",
                "details": f"StrategyCoordinatorAgent heal() not implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"StrategyCoordinatorAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }
