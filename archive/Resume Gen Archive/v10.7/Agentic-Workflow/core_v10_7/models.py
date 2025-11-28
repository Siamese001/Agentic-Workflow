"""Pydantic models shared across the v10.7 workflow."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseToolOutput(BaseModel):
    status: str = Field("success", description="Indicates tool execution status")


class DraftStrategyOutput(BaseToolOutput):
    feedback: str = Field(..., description="Strategic feedback on the draft")


class RedTeamOutput(BaseToolOutput):
    weaknesses_found: List[str] = Field(..., description="List of identified weaknesses")


class RefineSectionOutput(BaseToolOutput):
    refined_text: str = Field(..., description="The new, refined text for the section")


class AddMetricsOutput(BaseToolOutput):
    suggestions: List[str] = Field(..., description="Specific suggestions for adding metrics")


class QAClaimOutput(BaseToolOutput):
    unsupported_claims: int = Field(..., ge=0, description="Count of claims not supported by the master resume")
    feedback: str = Field(..., description="NLI feedback and analysis")


class QAToneOutput(BaseToolOutput):
    tone_match: bool = Field(..., description="Whether the draft's tone matches the required tone")
    current_tone: str = Field(..., description="The detected tone of the draft")


class QAThematicAlignmentOutput(BaseToolOutput):
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Score from 0.0 to 1.0 for thematic alignment")
    feedback: str = Field(..., description="Feedback on alignment")


class QASemanticEntailmentOutput(BaseToolOutput):
    entailment_score: float = Field(..., ge=0.0, le=1.0, description="Semantic entailment score with the job description")


class QANarrativeThreadOutput(BaseModel):
    narrative_clear: bool = Field(..., description="Whether a clear career narrative was detected")


class QAJDSkillsOutput(BaseToolOutput):
    keyword_coverage: float = Field(..., ge=0.0, le=1.0, description="Percentage of JD keywords found in the draft")
    missing_keywords: List[str] = Field(..., description="List of important missing keywords")


class QASignalScoreOutput(BaseToolOutput):
    avg_signal_score: float = Field(..., ge=0.0, le=10.0, description="Average signal-to-noise score (0-10)")


class QATenureOutput(BaseToolOutput):
    gaps_found: int = Field(..., ge=0, description="Number of unexplained tenure gaps")
    overlaps_found: int = Field(..., ge=0, description="Number of overlapping job dates")


class QAMissedOpportunitiesOutput(BaseToolOutput):
    opportunities_found: List[str] = Field(..., description="List of relevant experiences that were omitted")


class QAAdversarialOutput(BaseToolOutput):
    red_flags: List[str] = Field(..., description="List of red flags a skeptical hiring manager would find")


class QABiasOutput(BaseModel):
    bias_detected: bool
    patterns: List[str]
    bias_score: float
    dynamic_rules_applied: int


class PlannerAssessment(BaseModel):
    planner_name: str = Field(..., description="Name of the specialist planner issuing the assessment")
    vote: str = Field(..., description="Planner vote (e.g., 'approve', 'revise', 'escalate')")
    rationale: str = Field(..., description="Summary of why the planner issued this vote")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the vote (0.0-1.0)")
    recommended_actions: List[str] = Field(default_factory=list, description="Optional action items suggested by the planner")


class ScenarioSimulationResult(BaseModel):
    scenario_name: str = Field(..., description="Name of the simulated scenario stress test")
    risk_level: str = Field(..., description="Qualitative risk classification (e.g., low, medium, high)")
    impact_score: float = Field(..., ge=0.0, le=1.0, description="Estimated impact score between 0 and 1")
    summary: str = Field(..., description="Short narrative of simulation findings")
    mitigation_actions: List[str] = Field(default_factory=list, description="Recommended mitigations derived from the scenario")


class StrategyPlan(BaseModel):
    strategy_name: str = Field(..., description="A brief, descriptive name for the strategy")
    focus_areas: List[str] = Field(..., description="The main themes to emphasize")
    key_achievements_to_highlight: List[str] = Field(..., description="Specific achievements to feature")
    tone: str = Field(..., description="The desired tone (e.g., 'professional', 'technical', 'leadership')")
    planner_assessments: List[PlannerAssessment] = Field(default_factory=list, description="Assessments gathered from specialist planners")
    aggregated_decision: str = Field("undecided", description="Coordinator decision synthesized from planner votes")
    aggregated_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score for the aggregated decision")
    aggregated_rationale: Optional[str] = Field(None, description="Coordinator rationale for the aggregated decision")
    feedback_signals: List[str] = Field(default_factory=list, description="Signals or adjustments applied from downstream feedback")
    scenario_simulations: List[ScenarioSimulationResult] = Field(default_factory=list, description="Stress test results")
    coordinator_summary: Optional[str] = Field(None, description="High-level summary generated by the strategy coordinator")


class GeneratedPrompts(BaseModel):
    bullet_generation_prompt: str
    critique_prompt: str


class BulletList(BaseModel):
    verified_bullets: List[str] = Field(..., description="List of fact-checked, high-quality bullets")


class CritiqueResult(BaseModel):
    score: float = Field(..., ge=0.0, le=10.0, description="Quality score from 0-10")
    suggestions: List[str] = Field(..., description="Specific suggestions for improvement")


class HILAmbiguityReport(BaseModel):
    ambiguity_detected: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    question_for_human: str = Field(..., description="The specific question to ask the human")


class PersonaReviewDecision(BaseModel):
    persona: str = Field(..., description="Persona name (e.g., Legal, Brand, SME)")
    approval: bool = Field(..., description="True if the persona approves the change")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence in the persona decision")
    key_concerns: List[str] = Field(default_factory=list, description="Top issues raised by the persona")
    proposed_actions: List[str] = Field(default_factory=list, description="Specific actions requested by the persona")
    escalation_recommended: bool = Field(
        False,
        description="True if the persona recommends escalating to a specialist human reviewer",
    )


class PersonaConsensus(BaseModel):
    approved: bool = Field(..., description="True if consensus favors accepting the edit")
    rationale: str = Field(..., description="Narrative summary of the negotiation outcome")
    negotiated_actions: List[str] = Field(default_factory=list, description="Actions agreed upon during negotiation")
    persona_votes: List[PersonaReviewDecision] = Field(
        default_factory=list,
        description="Detailed breakdown of each persona's vote and rationale",
    )


class HILFeedbackIntent(BaseModel):
    intent_id: str = Field(..., description="Stable identifier for the clustered feedback intent")
    summary: str = Field(..., description="Human-readable description of the intent")
    severity: str = Field(..., description="Qualitative severity (e.g., 'critical', 'minor')")
    recommended_owner: str = Field(..., description="Suggested owner (Strategy, Drafting, Legal, etc.)")
    exemplar_quotes: List[str] = Field(default_factory=list, description="Representative human quotes for the intent")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the clustering")


class HILReconciliationResult(BaseModel):
    integrated_text: str = Field(..., description="Reconciled text ready to merge into the draft")
    change_log: List[str] = Field(default_factory=list, description="Bullet log of applied changes")
    unresolved_questions: List[str] = Field(default_factory=list, description="Open questions that need human follow-up")


class HILFeedbackRoute(BaseModel):
    next_step: str = Field(..., description="The graph node to jump to")
    payload: Optional[str] = Field(None, description="Corrected text or data from the human")
    intent_clusters: List[HILFeedbackIntent] = Field(default_factory=list, description="Clustered intents extracted from human feedback")
    delegated_specialists: List[str] = Field(default_factory=list, description="List of human specialists requested for escalation")
    persona_consensus: Optional[PersonaConsensus] = Field(None, description="Negotiated consensus between virtual personas")
    reconciliation: Optional[HILReconciliationResult] = Field(
        None,
        description="Latest reconciliation result from specialist feedback",
    )


class ConstitutionalReviewResult(BaseModel):
    review_passed: bool = Field(..., description="True if the output passes all constitutional principles")
    violations_found: List[str] = Field(..., description="A list of principles that were violated")
    feedback: str = Field(..., description="Specific feedback on how to correct the violations")


__all__ = [
    "BaseToolOutput",
    "DraftStrategyOutput",
    "RedTeamOutput",
    "RefineSectionOutput",
    "AddMetricsOutput",
    "QAClaimOutput",
    "QAToneOutput",
    "QAThematicAlignmentOutput",
    "QASemanticEntailmentOutput",
    "QANarrativeThreadOutput",
    "QAJDSkillsOutput",
    "QASignalScoreOutput",
    "QATenureOutput",
    "QAMissedOpportunitiesOutput",
    "QAAdversarialOutput",
    "QABiasOutput",
    "PlannerAssessment",
    "ScenarioSimulationResult",
    "StrategyPlan",
    "GeneratedPrompts",
    "BulletList",
    "CritiqueResult",
    "HILAmbiguityReport",
    "PersonaReviewDecision",
    "PersonaConsensus",
    "HILFeedbackIntent",
    "HILReconciliationResult",
    "HILFeedbackRoute",
    "ConstitutionalReviewResult",
]
