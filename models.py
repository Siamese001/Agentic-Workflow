# FILE: models.py
"""
Unified Runtime Models (v10_10) — TRUE AGENTIC CONTRACTS

This module defines the strict Pydantic schemas required for the 
v10_10 Cognitive Architecture. It enforces Pillar 3 (Typed Contracts)
and serves as the backbone for L1-L5, Governance, and Routing.

CONTAINS:
    1. Core Enums (Phase, Status, SafetyMode)
    2. Governance Schemas (Prompt, Policy, Routing)
    3. Cognitive Contracts (Plan, Strategy, Drafting)
    4. Correction Schemas (Signals, Surfaces)
    5. State & Workflow Schemas (Patch, State, DAG)

Design Constraints:
    • PURE DATA: No logic.
    • STRICT TYPING: Pydantic v2 BaseModel.
    • ZERO LOSS: Supports all domains (Strategy, RAG, Safety, etc.).
"""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional, Generic, TypeVar, Union
from pydantic import BaseModel, Field, ConfigDict

# =============================================================================
# 1. CORE ENUMS
# =============================================================================

class NodeStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    RETRYING = "retrying"

class WorkflowPhase(str, enum.Enum):
    INIT = "init"
    PLANNING = "planning"
    EXECUTING = "executing"
    CORRECTING = "correcting"  # Explicit correction phase
    REVIEWING = "reviewing"
    COMPLETE = "complete"
    FAILED = "failed"

class SafetyMode(str, enum.Enum):
    STRICT = "strict"
    BALANCED = "balanced"
    PERMISSIVE = "permissive"

class ReasoningStrategy(str, enum.Enum):
    DIRECT = "direct"
    COT = "chain_of_thought"
    TOT = "tree_of_thought"
    REFLEXION = "reflexion"

# =============================================================================
# 2. GOVERNANCE & INFRASTRUCTURE SCHEMAS
# =============================================================================

# --- PROMPT REGISTRY (Pillar 13) ---
class PromptVersion(BaseModel):
    """Metadata for a specific version of a prompt."""
    version_id: str
    template: str
    input_variables: List[str]
    model_constraints: Dict[str, Any] = Field(default_factory=dict)
    changelog: str = ""
    
class PromptBundle(BaseModel):
    """A named prompt family (e.g. 'strategy_planner')."""
    bundle_id: str
    current_version: str
    versions: Dict[str, PromptVersion] = Field(default_factory=dict)
    description: str = ""

# --- ROUTING POLICY (Pillar 11) ---
class RoutingRequest(BaseModel):
    """Input to the Routing Engine."""
    task_type: str  # strategy, drafting, etc.
    complexity: str # low, medium, high
    priority: str   # normal, high
    cost_sensitive: bool = False

class RoutingDecision(BaseModel):
    """Output from the Routing Engine."""
    model_id: str
    provider: str   # openai, anthropic
    max_tokens: int
    temperature: float
    reasoning_effort: str = "medium"
    rationale: str

# --- SAFETY POLICY (Pillar 9) ---
class SafetyRule(BaseModel):
    rule_id: str
    description: str
    severity: str # critical, high, medium, low
    category: str

class SafetyPolicy(BaseModel):
    policy_id: str
    mode: SafetyMode
    rules: List[SafetyRule]
    threshold: float

# =============================================================================
# 3. COGNITIVE CONTRACTS (L1 / L2)
# =============================================================================

# --- L1 PLAN ---
class PlanStep(BaseModel):
    step_id: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)

class PlanObject(BaseModel):
    """Strict contract from L1 Planner."""
    workflow_id: str
    objective: str
    mode: str
    complexity: str
    reasoning_strategy: ReasoningStrategy
    steps: List[PlanStep]
    context_pointers: Dict[str, str] = Field(default_factory=dict)
    
    # Flexible bucket for mode-specific params (validated downstream)
    meta: Dict[str, Any] = Field(default_factory=dict)

# --- L2 EXECUTION RESULT ---
PayloadT = TypeVar("PayloadT")

class ExecutionResult(BaseModel, Generic[PayloadT]):
    """Strict contract from L2 Executors."""
    status: NodeStatus
    payload: Optional[PayloadT] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    # Metrics
    latency_ms: float = 0.0
    model_used: Optional[str] = None
    tokens_used: int = 0

# --- DOMAIN SPECIFIC PAYLOADS ---

class StrategyBranch(BaseModel):
    branch_id: str
    name: str
    rationale: str
    steps: List[str]
    score: float = 0.0

class StrategyPayload(BaseModel):
    branches: List[StrategyBranch]
    selected_branch_id: str
    reasoning_trace: str

class DraftSection(BaseModel):
    section_id: str
    content: str
    critique: Optional[str] = None

class DraftingPayload(BaseModel):
    full_text: str
    sections: List[DraftSection]
    tone_compliance: float

class QAFinding(BaseModel):
    finding_id: str
    category: str
    severity: str
    message: str
    location: str

class QAPayload(BaseModel):
    passed: bool
    score: float
    findings: List[QAFinding]
    summary: str

class SafetyFinding(BaseModel):
    rule_id: str
    violated: bool
    confidence: float
    snippet: str

class SafetyPayload(BaseModel):
    blocked: bool
    findings: List[SafetyFinding]
    policy_version: str

# =============================================================================
# 4. SELF-CORRECTION & DIAGNOSTICS (Pillar 5)
# =============================================================================

class CorrectionSignal(BaseModel):
    """A detected issue requiring intervention."""
    signal_id: str
    surface: str  # e.g. "qa_failure", "safety_block"
    severity: float # 0.0 to 1.0
    context: Dict[str, Any]

class CorrectionProposal(BaseModel):
    """Proposed fix from the Correction Engine."""
    action: str   # retry, replan, escalate
    target_node: str
    parameters: Dict[str, Any]
    rationale: str

class MetaProfile(BaseModel):
    """Adaptive memory of the agent."""
    bias_routing_fast: bool = False
    bias_planning_conservative: bool = False
    bias_safety_strict: bool = False
    history: List[Dict[str, Any]] = Field(default_factory=list)

# =============================================================================
# 5. STATE & ORCHESTRATION (Pillar 4 / 7)
# =============================================================================

class StatePatch(BaseModel):
    """Atomic update to L4 State."""
    op: str = "merge" # merge, replace, append
    path: str         # dot-notation path (e.g. "draft_result.sections")
    value: Any

class WorkflowState(BaseModel):
    """The immutable snapshot of the agent's world."""
    workflow_id: str
    phase: WorkflowPhase
    
    # Core Data Buckets
    objective: str
    messages: List[Dict[str, Any]]
    rag_docs: List[Dict[str, Any]]
    
    # Domain Results (Optional, populated as workflow progresses)
    strategy_result: Optional[StrategyPayload] = None
    draft_result: Optional[DraftingPayload] = None
    qa_result: Optional[QAPayload] = None
    safety_result: Optional[SafetyPayload] = None
    
    # Meta
    correction_log: List[CorrectionSignal] = Field(default_factory=list)
    meta_profile: MetaProfile = Field(default_factory=MetaProfile)
    
    # Traceability
    trace_id: str
