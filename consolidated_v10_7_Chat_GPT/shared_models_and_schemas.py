# === CONSOLIDATED FILE ===
# TIMESTAMP: 2025-11-17T16:29:33.163747Z
# TARGET: shared_models_and_schemas.py
# SOURCE FILES:
# - /workspace/Agentic-Workflow/_latest_extract/agent_stacks_v/components/models.py | SHA256: 1bae92c12da4438ef2289d3d99d65a12bb618b345721f8d0f7ecac2cbe363e20
# - /workspace/Agentic-Workflow/_latest_extract/core_v/models.py | SHA256: c0ae07b0537c018c9c071840e4c3c17c8d123c47b7a1cb993599a133edc8c049
# MERGE RULE: 10_8 overrides 10_7; namespace collisions suffixed with __srcN


# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/agent_stacks_v/components/models.py (sha256=1bae92c12da4438ef2289d3d99d65a12bb618b345721f8d0f7ecac2cbe363e20) ====
"""Shared Pydantic data models for stack coordination."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SpecialistDraftPacket(BaseModel):
    """Container for specialist drafting outputs."""

    specialist: str = Field(..., description="Name of the drafting specialist")
    focus_area: str = Field(..., description="Primary responsibility of the specialist")
    sections: Dict[str, Any] = Field(default_factory=dict, description="Section-level draft contributions")
    notes: List[str] = Field(default_factory=list, description="Observations or hand-off notes")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies or follow-up actions")


class EvidenceClarificationRecord(BaseModel):
    """Represents a clarification request raised by the liaison."""

    request_id: str
    recipient: str
    questions: List[str]
    priority: str = "normal"
    context_summary: str = ""


class EvidenceBriefRecord(BaseModel):
    """Structured evidence digest for a section."""

    section: str
    brief: str
    key_points: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    outstanding_questions: List[str] = Field(default_factory=list)


class EvidenceLiaisonPacket(BaseModel):
    """Aggregated liaison output feeding back to the guild."""

    clarifications: List[EvidenceClarificationRecord] = Field(default_factory=list)
    briefs: List[EvidenceBriefRecord] = Field(default_factory=list)


class CritiqueFindingRecord(BaseModel):
    """Single critique finding routed by the panel."""

    critic: str
    severity: str
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)


class CritiquePanelPacket(BaseModel):
    """Aggregated critique findings for the coordinator."""

    findings: List[CritiqueFindingRecord] = Field(default_factory=list)
    overall_status: str = Field(..., description="Coordinator-level status derived from findings")
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/agent_stacks_v/components/models.py ====
# ==== BEGIN SOURCE: /workspace/Agentic-Workflow/_latest_extract/core_v/models.py (sha256=c0ae07b0537c018c9c071840e4c3c17c8d123c47b7a1cb993599a133edc8c049) ====
"""
Pydantic models shared across the v10.7 workflow (corrected + aligned).

This version:
 - Adds uniform model_config to allow extra fields
 - Adds helper .dump() and .load() backing for MainGraphState hydration
 - Normalizes QA tool outputs
 - Expands GeneratedPrompts to match PromptStack outputs
 - Adds descriptive defaults for safety and HIL models
 - Ensures compatibility with ResponseValidator + Pydantic v2
 - Preserves ALL correct semantics from the original models
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Base class with safe "extra='allow'" configuration
# ---------------------------------------------------------------------------

class V10Model(BaseModel):
    """
    All v10.7 Pydantic models extend this.

    Ensures:
      - unknown fields do not crash the validator
      - consistent .model_dump() / .model_validate() behavior
    """
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        def _serialize(value: Any) -> Any:
            if isinstance(value, BaseModel):
                return value.dict()
            if isinstance(value, list):
                return [_serialize(item) for item in value]
            if isinstance(value, dict):
                return {k: _serialize(v) for k, v in value.items()}
            if isinstance(value, Enum):
                return value.value
            return value

        result: Dict[str, Any] = {}
        for key, value in self.__dict__.items():
            if key.startswith("__"):
                continue
            result[key] = _serialize(value)
        return result

    def model_dump(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore[override]
        return self.dict()

    def model_dump_json(self, *args: Any, **kwargs: Any) -> str:  # type: ignore[override]
        return json.dumps(self.model_dump())


# ---------------------------------------------------------------------------
# NODE CONTRACT MODELS
# ---------------------------------------------------------------------------


class NodeStatus(str, Enum):
    SUCCESS = "success"
    RETRIABLE_ERROR = "retriable_error"
    FATAL_ERROR = "fatal_error"
    BLOCKED = "blocked"


class WorkflowPhase(str, Enum):
    INIT = "init"
    SAFETY = "safety"
    STRATEGY = "strategy"
    RAG = "rag"
    BULLETS = "bullets"
    DRAFTING = "drafting"
    QA = "qa"
    HIL = "hil"
    COMPLETE = "complete"


class NodeResult(V10Model):
    node: str = Field(..., description="Node name / identifier.")
    status: NodeStatus = Field(..., description="Outcome classification.")
    error_kind: Optional[str] = Field(
        default=None, description="Short error category.")
    error_message: Optional[str] = Field(
        default=None, description="Human-readable error detail.")
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Node-specific payload or patch.",
    )


# ---------------------------------------------------------------------------
# BASE TOOL RESULTS
# ---------------------------------------------------------------------------

class BaseToolOutput(V10Model):
    status: str = Field("success", description="Indicates tool execution status")


class DraftStrategyOutput(BaseToolOutput):
    feedback: str = Field(..., description="Strategic feedback on the draft")


class RedTeamOutput(BaseToolOutput):
    weaknesses_found: List[str] = Field(..., description="List of identified weaknesses")


class RefineSectionOutput(BaseToolOutput):
    refined_text: str = Field(..., description="The new, refined text for the section")


class AddMetricsOutput(BaseToolOutput):
    suggestions: List[str] = Field(..., description="Specific suggestions for adding metrics")


# ---------------------------------------------------------------------------
# QA OUTPUT MODELS
# ---------------------------------------------------------------------------

class QAClaimOutput(BaseToolOutput):
    unsupported_claims: int = Field(..., ge=0, description="Unsupported claim count")
    feedback: str = Field(..., description="NLI feedback and analysis")


class QAToneOutput(BaseToolOutput):
    tone_match: bool = Field(..., description="Whether the tone matches the required tone")
    current_tone: str = Field(..., description="Detected tone of the draft")


class QAThematicAlignmentOutput(BaseToolOutput):
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Thematic alignment score")
    feedback: str = Field(..., description="Reviewer feedback")


class QASemanticEntailmentOutput(BaseToolOutput):
    entailment_score: float = Field(..., ge=0.0, le=1.0, description="Semantic entailment score")


class QANarrativeThreadOutput(V10Model):
    narrative_clear: bool = Field(..., description="Whether a clear career narrative was detected")


class QAJDSkillsOutput(BaseToolOutput):
    keyword_coverage: float = Field(..., ge=0.0, le=1.0, description="JD keyword coverage")
    missing_keywords: List[str] = Field(..., description="Important missing keywords")


class QASignalScoreOutput(BaseToolOutput):
    avg_signal_score: float = Field(..., ge=0.0, le=10.0, description="Signal-to-noise score")


class QATenureOutput(BaseToolOutput):
    gaps_found: int = Field(..., ge=0, description="Number of timeline gaps")
    overlaps_found: int = Field(..., ge=0, description="Overlapping dates count")


class QAMissedOpportunitiesOutput(BaseToolOutput):
    opportunities_found: List[str] = Field(..., description="Omitted opportunities found")


class QAAdversarialOutput(BaseToolOutput):
    red_flags: List[str] = Field(..., description="Red flags a hiring manager would find")


class QABiasOutput(V10Model):
    bias_detected: bool
    patterns: List[str]
    bias_score: float
    dynamic_rules_applied: int


# ---------------------------------------------------------------------------
# STRATEGY MODELS
# ---------------------------------------------------------------------------

class PlannerAssessment(V10Model):
    planner_name: str = Field(..., description="Planner identity")
    vote: str = Field(..., description="Planner vote")
    rationale: str = Field(..., description="Summary of planner reasoning")
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommended_actions: List[str] = Field(default_factory=list)


class ScenarioSimulationResult(V10Model):
    scenario_name: str
    risk_level: str
    impact_score: float = Field(..., ge=0.0, le=1.0)
    summary: str
    mitigation_actions: List[str] = Field(default_factory=list)


class StrategyPlan(V10Model):
    strategy_name: str
    focus_areas: List[str]
    key_achievements_to_highlight: List[str]
    tone: str
    planner_assessments: List[PlannerAssessment] = Field(default_factory=list)
    aggregated_decision: str = "undecided"
    aggregated_confidence: float = Field(0.0, ge=0.0, le=1.0)
    aggregated_rationale: Optional[str] = None
    feedback_signals: List[str] = Field(default_factory=list)
    scenario_simulations: List[ScenarioSimulationResult] = Field(default_factory=list)
    coordinator_summary: Optional[str] = None


class RAGPlan(V10Model):
    goal: str = Field(..., description="Primary retrieval objective")
    context_inputs: List[str] = Field(
        default_factory=list,
        description="Ordered list of state inputs considered during planning",
    )
    retrieval_queries: List[str] = Field(
        default_factory=list,
        description="Deterministic queries to execute across retrieval tools",
    )
    prioritization: List[str] = Field(
        default_factory=list,
        description="Heuristics used to rank retrieved evidence",
    )
    risk_checks: List[str] = Field(
        default_factory=list,
        description="Manual checks applied before sharing RAG output",
    )


class BulletPlan(V10Model):
    target_sections: List[str] = Field(
        default_factory=list,
        description="Resume or draft sections that require new bullets",
    )
    highlight_order: List[str] = Field(
        default_factory=list,
        description="Ordered list of experiences to emphasize",
    )
    metrics_focus: List[str] = Field(
        default_factory=list,
        description="Quantitative signals to surface inside bullets",
    )
    style_guidelines: List[str] = Field(
        default_factory=list,
        description="Tone + structure rules for bullet generation",
    )
    validation_checks: List[str] = Field(
        default_factory=list,
        description="Self-checklist that runs before handing bullets downstream",
    )


class DraftPlan(V10Model):
    structure: List[str] = Field(
        default_factory=list,
        description="Ordered sections or beats in the narrative draft",
    )
    tone: str = Field("Professional", description="Target tone for the draft")
    key_messages: List[str] = Field(
        default_factory=list,
        description="Key story beats or claims that must be included",
    )
    review_gates: List[str] = Field(
        default_factory=list,
        description="Sequenced validation checks prior to release",
    )
    risks: List[str] = Field(
        default_factory=list,
        description="Known risks or gaps that the draft must monitor",
    )


# ---------------------------------------------------------------------------
# PROMPTS MODELS
# ---------------------------------------------------------------------------

class GeneratedPrompts(V10Model):
    bullet_generation_prompt: str
    critique_prompt: str
    section_refinement_prompt: Optional[str] = None
    qa_prompts: Optional[Dict[str, str]] = None


class PromptEnvelope(V10Model):
    """Structured prompt envelope used by the renderer stack."""

    framing: str = ""
    context: str = ""
    reasoning: str = ""
    instructions: str = ""
    tool_context: str = ""
    safety_context: Dict[str, Any] = Field(default_factory=dict)
    output_schema: str = ""

    def __str__(self) -> str:
        return self.model_dump_json()


# ---------------------------------------------------------------------------
# SELF-CORRECTION MODELS
# ---------------------------------------------------------------------------

class SelfCorrectionReport(V10Model):
    stack_name: str
    workflow_id: str
    issue_detected: str
    action_taken: str
    retry_count: int = Field(0, ge=0)
    resolved: bool = False
    notes: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# BULLET + CRITIQUE MODELS
# ---------------------------------------------------------------------------

class BulletList(V10Model):
    verified_bullets: List[str]


class CritiqueResult(V10Model):
    score: float = Field(..., ge=0.0, le=10.0)
    suggestions: List[str]


# ---------------------------------------------------------------------------
# HIL MODELS
# ---------------------------------------------------------------------------

class HILAmbiguityReport(V10Model):
    ambiguity_detected: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    question_for_human: str


class PersonaReviewDecision(V10Model):
    persona: str
    approval: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_concerns: List[str] = Field(default_factory=list)
    proposed_actions: List[str] = Field(default_factory=list)
    escalation_recommended: bool = False


class PersonaConsensus(V10Model):
    approved: bool
    rationale: str
    negotiated_actions: List[str] = Field(default_factory=list)
    persona_votes: List[PersonaReviewDecision] = Field(default_factory=list)


class HILFeedbackIntent(V10Model):
    intent_id: str
    summary: str
    severity: str
    recommended_owner: str
    exemplar_quotes: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class HILReconciliationResult(V10Model):
    integrated_text: str
    change_log: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)


class HILFeedbackRoute(V10Model):
    next_step: str
    payload: Optional[str] = None
    intent_clusters: List[HILFeedbackIntent] = Field(default_factory=list)
    delegated_specialists: List[str] = Field(default_factory=list)
    persona_consensus: Optional[PersonaConsensus] = None
    reconciliation: Optional[HILReconciliationResult] = None


# ---------------------------------------------------------------------------
# SAFETY + CONSTITUTION MODELS
# ---------------------------------------------------------------------------

class ConstitutionalReviewResult(V10Model):
    review_passed: bool
    violations_found: List[str]
    feedback: str


class ArbitrationReport(V10Model):
    stage: str = Field(..., description="Arbitration stage identifier")
    decision: str = Field(..., description="Decision: ACCEPT, WARN, or REQUEST_REVISE")
    reasons: List[str] = Field(default_factory=list, description="Short textual reasons")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence in decision")
    suggested_route: Optional[str] = Field(
        default=None,
        description="Optional suggested route label (e.g., 'REPLAN_STRATEGY').",
    )
    metrics_snapshot: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional snapshot of relevant metrics or signals.",
    )


class EpisodicMemory(BaseModel):
    conversation: list[dict] = []
    agent_notes: list[str] = []


class SemanticMemoryRef(BaseModel):
    vector_store_ids: list[str] = []
    tags: list[str] = []


class MemoryState(BaseModel):
    episodic: EpisodicMemory = EpisodicMemory()
    semantic: SemanticMemoryRef = SemanticMemoryRef()


class EphemeralState(BaseModel):
    events: list = []
    debug_traces: list[str] = []
    last_node: str | None = None


__all__ = [
    "NodeStatus",
    "WorkflowPhase",
    "NodeResult",
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
    "RAGPlan",
    "BulletPlan",
    "DraftPlan",
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
    "ArbitrationReport",
    "EpisodicMemory",
    "SemanticMemoryRef",
    "MemoryState",
    "EphemeralState",
]
# ==== END SOURCE: /workspace/Agentic-Workflow/_latest_extract/core_v/models.py ====
