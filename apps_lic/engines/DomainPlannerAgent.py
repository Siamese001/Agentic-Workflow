"""Specialist planner ensemble and coordinator for v10.7 strategies."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from core_v10_7 import (
    BaseAgent,
    PlannerAssessment,
    ScenarioSimulationResult,
    StrategyPlan,
)

if TYPE_CHECKING:
    from core_v10_7 import WorkflowContext


def _truncate(text: str, limit: int = 160) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


class DomainPlannerAgent(BaseAgent):
    """Evaluates strategic alignment with the job domain."""

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
                "Introduce a focus area that explicitly references the job title or company priorities."
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


class RiskAssessorAgent(BaseAgent):
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
            "Low strategic risk detected."
            if not risk_signals
            else "Detected " + ", ".join(risk_signals)
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


class FeasibilityAnalystAgent(BaseAgent):
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


class StrategyScenarioSimulatorAgent(BaseAgent):
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
            any(ch.isdigit() for ch in achievement)
            for achievement in plan.key_achievements_to_highlight
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
            )
        )

        technical_risk = "low" if technical_focus else "medium"
        technical_impact = 0.4 if technical_focus else 0.7
        technical_mitigations = (
            []
            if technical_focus
            else ["Add a focus area covering technical depth or tooling expertise."]
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
            )
        )

        cross_functional_risk = "low" if leadership_focus else "medium"
        cross_functional_impact = 0.3 if leadership_focus else 0.6
        cross_functional_mitigations = (
            []
            if leadership_focus
            else ["Introduce leadership/collaboration narratives into focus areas."]
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
            )
        )

        self.log_feedback(
            workflow_id,
            "strategy_simulation",
            "success",
            {"scenarios": [scenario.model_dump() for scenario in scenarios]},
        )
        return scenarios


class StrategyCoordinatorAgent(BaseAgent):
    """Coordinates specialist planner inputs and produces an aggregated plan."""

    def __init__(self, context: WorkflowContext, debug_mode: bool = False):
        super().__init__(context, debug_mode)
        self.domain_planner = DomainPlannerAgent(context, debug_mode)
        self.risk_assessor = RiskAssessorAgent(context, debug_mode)
        self.feasibility_analyst = FeasibilityAnalystAgent(context, debug_mode)
        self.scenario_simulator = StrategyScenarioSimulatorAgent(context, debug_mode)

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
                f"{assessment.planner_name}: {assessment.vote} ({_truncate(assessment.rationale, 80)})"
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
        feedback_summary = (
            f" Feedback signals: {', '.join(feedback_signals)}." if feedback_signals else ""
        )
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

        qa_feedback = (
            downstream_feedback.get("qa") if isinstance(downstream_feedback, dict) else None
        )
        if isinstance(qa_feedback, dict):
            jd_skills = qa_feedback.get("jd_skills")
            if isinstance(jd_skills, dict):
                missing_keywords = jd_skills.get("missing_keywords")
                if isinstance(missing_keywords, list) and missing_keywords:
                    for keyword in missing_keywords:
                        if keyword not in plan.focus_areas:
                            plan.focus_areas.append(keyword)
                    signals.append(
                        "Augmented focus areas with QA missing keywords: "
                        + ", ".join(missing_keywords[:5])
                    )

        hil_feedback = (
            downstream_feedback.get("hil") if isinstance(downstream_feedback, dict) else None
        )
        if isinstance(hil_feedback, dict):
            payload = hil_feedback.get("payload")
            if isinstance(payload, str) and payload:
                signals.append("HIL payload available for downstream drafting alignment.")

        return signals
