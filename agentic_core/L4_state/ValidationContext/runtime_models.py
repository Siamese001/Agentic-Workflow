from __future__ import annotations
"""Shared models and enums for the Agentic Workflow runtime.

This file contains all shared data structures that are used across multiple
modules to avoid circular imports. This file must NOT import from any
runtime.* modules - only from pydantic, enum, and typing.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Type
from pydantic import BaseModel, Field

Logger = logging.getLogger(__name__)


# ============================================================================
# SubatomicHop Models
# ============================================================================

class MicroStage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""
    PRE_CHECK = "PRE_CHECK"     # Validate inputs and context
    THINK = "THINK"             # Plan the execution (CoT)
    ACT = "ACT"                 # Execute the tool/LLM call
    CRITIQUE = "CRITIQUE"       # Review and validate output
    COMMIT = "COMMIT"           # Write to state/memory


class HopState(Enum):
    """Overall state of a Subatomic Hop."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NEGOTIATING = "NEGOTIATING"  # For Phase 4


class RetryPolicy(BaseModel):
    """Retry policy for micro-stages."""
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: List[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )


class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage."""
    hop_id: str
    stage: MicroStage
    timestamp: float
    state: HopState
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class StageTransition(BaseModel):
    """Record of a stage transition."""
    from_stage: Optional[MicroStage] = None
    to_stage: MicroStage
    timestamp: float
    reason: Optional[str] = None


# ============================================================================
# Prompt Injection Models
# ============================================================================

class InjectionType(Enum):
    """Types of prompt injections."""
    # Original built-in types
    TONE_ENHANCEMENT = "tone_enhancement"
    ROLE_SPECIFICATION = "role_specification"
    CONTEXT_GROUNDING = "context_grounding"
    FORMAT_ENHANCEMENT = "format_enhancement"
    CONSTRAINT_ENFORCEMENT = "constraint_enforcement"
    EXAMPLE_INJECTION = "example_injection"
    METADATA_ENRICHMENT = "metadata_enrichment"
    STRUCTURE_IMPROVEMENT = "structure_improvement"
    
    # Instructional injection types - Framing Layer
    GOAL_STATE_ALIGNMENT = "goal_state_alignment"
    SUCCESS_CRITERIA_SPECIFICATION = "success_criteria_specification"
    TASK_MODE_SPECIFICATION = "task_mode_specification"
    SCOPE_BOUNDARY_DEFINITION = "scope_boundary_definition"
    COST_CONSTRAINT_SPECIFICATION = "cost_constraint_specification"
    
    # Instructional injection types - Context Layer
    UNTRUSTED_WRAPPING_DETECTION = "untrusted_wrapping_detection"
    CANONICALIZATION_ENFORCEMENT = "canonicalization_enforcement"
    CONTEXTUAL_PRUNING = "contextual_pruning"
    CONSISTENCY_VALIDATION = "consistency_validation"
    ORDERING_PRESERVATION = "ordering_preservation"
    
    # Instructional injection types - Reasoning Layer
    FAILURE_ANTICIPATION = "failure_anticipation"
    MULTI_BRANCH_REASONING = "multi_branch_reasoning"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    REASON_THEN_ANSWER = "reason_then_answer"
    ERROR_SIMULATION = "error_simulation"
    
    # Instructional injection types - Tooling Layer
    FEEDBACK_LOOP_INTEGRATION = "feedback_loop_integration"
    EVIDENCE_BINDING = "evidence_binding"
    RECONCILIATION_ENFORCEMENT = "reconciliation_enforcement"
    SHADOW_VALIDATION = "shadow_validation"
    MODEL_AWARENESS = "model_awareness"
    
    # Instructional injection types - Safety Layer
    INJECTION_SHIELDING = "injection_shielding"
    DATA_INSTRUCTION_SEPARATION = "data_instruction_separation"
    CONSTITUTIONAL_GUARDRAILS = "constitutional_guardrails"
    DELEGATION_GUARDS = "delegation_guards"
    ADVERSARIAL_MODE = "adversarial_mode"
    
    # Instructional injection types - Output Layer
    JSON_ONLY_OUTPUT = "json_only_output"
    SCHEMA_ENFORCEMENT = "schema_enforcement"
    STABILITY_CONTRACTS = "stability_contracts"
    ERROR_ENVELOPES = "error_envelopes"
    MINIMALITY_CONSTRAINTS = "minimality_constraints"


class InjectionScope(BaseModel):
    """Scope where injection should be applied."""
    hop_types: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)
    contexts: Dict[str, Any] = Field(default_factory=dict)


class InjectionPattern(BaseModel):
    """A single prompt injection pattern."""
    id: str
    name: str
    type: InjectionType
    description: str
    template: str
    variables: List[str] = Field(default_factory=list)
    scope: InjectionScope = Field(default_factory=InjectionScope)
    priority: int = Field(default=0, ge=0, le=10)
    enabled: bool = True
    
    class Config:
        use_enum_values = True


class InjectionMatch(BaseModel):
    """Result of matching injections to context."""
    injection: InjectionPattern
    relevance_score: float = Field(ge=0.0, le=1.0)
    variable_values: Dict[str, Any] = Field(default_factory=dict)


class InjectionConfig(BaseModel):
    """Configuration for injection loader."""
    injection_dir: Path = Field(default=Path("./injections"))
    max_injections_per_hop: int = Field(default=5, ge=1, le=10)
    relevance_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    enable_caching: bool = True
    auto_reload: bool = True


# ============================================================================
# Additional Shared Types
# ============================================================================

class ValidationResult(BaseModel):
    """Result of a validation operation."""
    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Result of an execution operation."""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: Optional[float] = None


# Type Aliases
# Common type aliases for better readability
ContextData = Dict[str, Any]
StageData = Dict[str, Any]
InjectionVariables = Dict[str, Any]
HopTypes = List[str]
StageList = List[str]
