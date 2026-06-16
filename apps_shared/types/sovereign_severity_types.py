"""
Sovereign Core Contracts – Absolute SSOT for all Pydantic models and data schemas
No inline BaseModel definitions allowed outside schemas/.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    GEMINI_25_PRO_MODEL_ID,
)

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, validator

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

from apps_shared.types.severity_enums import (
    SovereignEventType,
    SovereignSeverity,
    severity_log_levels,
    sovereign_event_categories,
    sovereign_event_type,
    sovereign_severities,
    sovereign_severity,
    to_log_level,
)

import apps_shared.types.governance_declarations as _governance_declarations  # noqa: F401


class sovereign_base_model_types(BaseModel):
    """Base model for all Sovereign entities with strict config."""

    model_config = ConfigDict(strict=True, frozen=True)


SovereignBaseModelTypes = sovereign_base_model_types


class territory(sovereign_base_model_types):
    """Brief description of functionality and purpose."""

    name: str
    depth: int
    path: str
    canon_key: int | None = None


Territory = territory


class agent_message(sovereign_base_model_types):
    """Brief description of functionality and purpose."""

    source: str
    destination: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


AgentMessage = agent_message


class read_file_args(BaseModel):
    """Arguments for reading a file."""

    path: str = Field(..., description="Relative path to the file to read")

    @validator("path")
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


ReadFileArgs = read_file_args


class write_file_args(BaseModel):
    """Arguments for writing to a file."""

    path: str = Field(..., description="Relative path to the file to write")
    content: str = Field(..., description="Content to write to the file")
    create_dirs: bool = Field(default=True, description="Create parent directories if they don't exist")

    @validator("path")
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


WriteFileArgs = write_file_args


class move_file_args(BaseModel):
    """Arguments for moving/renaming a file."""

    source: str = Field(..., description="Relative path to the source file")
    destination: str = Field(..., description="Relative path to the destination")
    overwrite: bool = Field(default=False, description="Overwrite destination if it exists")

    @validator("source", "destination")
    def validate_paths(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Paths must be relative to project root")
        return v


MoveFileArgs = move_file_args


class list_files_args(BaseModel):
    """Arguments for listing files in a directory."""

    path: str = Field(default=".", description="Relative path to the directory to list")
    pattern: str | None = Field(default=None, description="Glob pattern to filter files (e.g., '*.py')")
    recursive: bool = Field(default=False, description="Recursively list subdirectories")

    @validator("path")
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


ListFilesArgs = list_files_args


class execute_command_args(BaseModel):
    """Arguments for executing a shell command."""

    command: str = Field(..., description="Command to execute")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    cwd: str | None = Field(default=None, description="Working directory (relative to project root)")
    timeout: int = Field(default=30, description="Timeout in seconds (max 300)")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")

    @validator("timeout")
    def validate_timeout(cls, v):
        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds to prevent livelocks")
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v

    @validator("cwd")
    def validate_cwd(cls, v):
        if v and Path(v).is_absolute():
            raise ValueError("Working directory must be relative to project root")
        return v


ExecuteCommandArgs = execute_command_args


class delete_file_args(BaseModel):
    """Arguments for deleting a file."""

    path: str = Field(..., description="Relative path to the file to delete")

    @validator("path")
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


DeleteFileArgs = delete_file_args


class create_directory_args(BaseModel):
    """Arguments for creating a directory."""

    path: str = Field(..., description="Relative path to the directory to create")
    parents: bool = Field(default=True, description="Create parent directories if they don't exist")

    @validator("path")
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v


CreateDirectoryArgs = create_directory_args


class agent_thought_process(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """

    reasoning_trace: list[str] = Field(
        ...,
        description="Step-by-step logic leading to the decision. Each step should be clear and atomic.",
    )
    relevant_context_keys: list[str] = Field(...)
    tool_choice: Literal[SEARCH, CODE, ANSWER, DELEGATE, TERMINATE] = Field(
        ...,
        description="The action type to take",
    )
    tool_arguments: dict[str, Any] = Field(default_factory=dict, description="Arguments for the chosen tool")
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this decision (0.0 to 1.0)",
    )

    @field_validator("tool_arguments")
    @classmethod
    def validate_args(cls, v, info):
        """Self-validation inside the schema."""
        tool_choice = info.data.get("tool_choice")
        if tool_choice == "CODE" and "code" not in v:
            raise ValueError("Tool choice CODE requires a 'code' argument.")
        if tool_choice == "SEARCH" and "query" not in v:
            raise ValueError("Tool choice SEARCH requires a 'query' argument.")
        if tool_choice == "DELEGATE" and "subtask" not in v:
            raise ValueError("Tool choice DELEGATE requires a 'subtask' argument.")
        return v


AgentThoughtProcess = agent_thought_process


class code_generation_result(BaseModel):
    """schema for code generation tasks."""

    reasoning: str = Field(..., description="Why this code solves the problem")
    code: str = Field(..., description="The generated Python code")
    dependencies: list[str] = Field(default_factory=list, description="Required pip packages")
    test_cases: list[str] = Field(default_factory=list, description="Test cases to verify the code")
    safety_notes: list[str] = Field(
        default_factory=list,
        description="Potential safety concerns or limitations",
    )


CodeGenerationResult = code_generation_result


class research_result(BaseModel):
    """schema for research tasks."""

    query_understanding: str = Field(..., description="How you interpreted the research question")
    sources: list[dict[str, str]] = Field(..., description="List of sources with 'url' and 'relevance' keys")
    key_findings: list[str] = Field(..., description="Main findings from the research")
    confidence_level: Literal[high, medium, low] = Field(
        ...,
        description="Confidence in the research results",
    )
    follow_up_questions: list[str] = Field(
        default_factory=list,
        description="Suggested follow-up research questions",
    )


ResearchResult = research_result


class consensus_verdict(BaseModel):
    """Result of a consensus deliberation."""

    chosen_plan: str
    consensus_score: float
    dissenting_opinions: list[str] = Field(default_factory=list)
    reasoning: str
    safe_to_proceed: bool


ConsensusVerdict = consensus_verdict


class model_opinion(BaseModel):
    """Individual model's opinion on a plan."""

    model_name: str
    plan: str
    reasoning: str
    risk_assessment: str
    confidence: float


ModelOpinion = model_opinion


class agent_plan(BaseModel):
    """Agent execution plan with reasoning and tool calls."""

    reasoning: str
    tool_calls: list[dict]


AgentPlan = agent_plan


class tone_type(str, Enum):
    """Primary tone types for communication style analysis."""

    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    ENTHUSIASTIC = "enthusiastic"
    DIRECT = "direct"


ToneType = tone_type


class style_profile(BaseModel):
    """Profile defining a communication style."""

    primary_tone: ToneType = Field(..., description="Primary tone type")
    formality_level: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Formality level (0=Casual, 1=Academic)",
    )
    emoji_frequency: float = Field(default=0.2, ge=0.0, le=1.0, description="Emoji usage frequency")
    sentence_length_avg: int = Field(default=15, ge=5, le=50, description="Target words per sentence")
    vocabulary_complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Vocabulary complexity")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in analysis")

    class Config:
        """Pydantic configuration."""

        validate_assignment = True


StyleProfile = style_profile


class generation_config(BaseModel):
    """configuration for LLM generation based on tone profile."""

    system_prompt_fragment: str = Field(..., description="Instruction to inject into prompts")
    temperature_setting: float = Field(..., ge=0.1, le=1.0, description="LLM temperature")
    banned_phrases: list[str] = Field(default_factory=list, description="Phrases to avoid")
    preferred_transitions: list[str] = Field(default_factory=list, description="Preferred transition words")
    max_sentence_length: int = Field(default=25, ge=5, le=100, description="Max words per sentence")

    @validator("temperature_setting")
    def clamp_temperature(cls, v):
        """Ensure temperature is within valid range."""
        return max(0.1, min(1.0, v))


GenerationConfig = generation_config


class micro_stage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""

    INIT = "init"
    THINK = "think"
    ACT = "act"
    CRITIQUE = "critique"
    COMMIT = "commit"


MicroStage = micro_stage


class hop_state(Enum):
    """Overall state of a Subatomic Hop."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


HopState = hop_state


class retry_policy(BaseModel):
    """Retry policy for micro-stages."""

    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: list[micro_stage] = Field(
        default=[micro_stage.THINK, micro_stage.ACT, micro_stage.CRITIQUE],
    )


RetryPolicy = retry_policy


class micro_checkpoint(BaseModel):
    """Checkpoint data for a micro-stage."""

    hop_id: str
    stage: micro_stage
    timestamp: float
    state: HopState
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


MicroCheckpoint = micro_checkpoint


class stage_transition(BaseModel):
    """Record of a stage transition."""

    from_stage: micro_stage | None = None
    to_stage: micro_stage
    timestamp: float
    reason: str | None = None


StageTransition = stage_transition


class injection_type(Enum):
    """Types of prompt injections."""

    SYSTEM = "system"
    USER = "user"
    CONTEXT = "context"
    REASONING = "reasoning"
    TOOLING = "tooling"
    SAFETY = "safety"
    OUTPUT = "output"


InjectionType = injection_type


class injection_scope(BaseModel):
    """Scope where injection should be applied."""

    hop_types: list[str] = Field(default_factory=list)
    stages: list[str] = Field(default_factory=list)
    contexts: dict[str, Any] = Field(default_factory=dict)


InjectionScope = injection_scope


class injection_pattern(BaseModel):
    """A single prompt injection pattern."""

    id: str
    name: str
    type: injection_type
    description: str
    template: str
    variables: list[str] = Field(default_factory=list)
    scope: injection_scope = Field(default_factory=injection_scope)
    priority: int = Field(default=0, ge=0, le=10)
    enabled: bool = True


InjectionPattern = injection_pattern


CORE_CONTRACTS_REGISTRY = {}

import uuid
from datetime import datetime, timezone


class thermal_profile(str, Enum):
    """Predefined thermal configurations for different node types."""

    CREATIVITY_MAX = "creativity_max"
    CREATIVITY_HIGH = "creativity_high"
    BALANCED = "balanced"
    STRUCTURED = "structured"
    PRECISION = "precision"


ThermalProfile = thermal_profile


@dataclass(frozen=True)
class hard_state:
    """
    Immutable, DAG-owned state that the LLM cannot edit directly.

    This contains critical execution metadata, security_scopes, and structural
    information that must remain stable throughout the workflow.
    """

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str | None = None
    node_id: str | None = None
    security_scopes: set = field(default_factory=set)
    file_paths: dict[str, str] = field(default_factory=dict)
    schemas: dict[str, str] = field(default_factory=dict)
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_trace(self, event: str, data: dict[str, Any]) -> HardState:
        """Add an event to the execution trace (returns new instance)."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"HardState.add_trace:{event}"
        )
        new_trace = self.execution_trace + [
            {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "data": data},
        ]
        return HardState(
            execution_id=self.execution_id,
            workflow_id=self.workflow_id,
            node_id=self.node_id,
            security_scopes=self.security_scopes,
            file_paths=self.file_paths,
            schemas=self.schemas,
            execution_trace=new_trace,
            created_at=self.created_at,
        )


HardState = hard_state


@dataclass
class soft_state:
    """
    Mutable, LLM-owned scratchpad for high-temperature creativity.

    This is where the LLM can draft, speculate, and iterate without risking
    system stability. Content here must be validated before promotion to HardState.
    """

    drafts: dict[str, Any] = field(default_factory=dict)
    scratchpad: list[str] = field(default_factory=list)
    creative_variants: list[dict[str, Any]] = field(default_factory=list)
    speculative_content: dict[str, Any] = field(default_factory=dict)
    revision_history: list[dict[str, Any]] = field(default_factory=list)

    def add_draft(self, key: str, content: Any) -> None:
        """Add content to the drafts."""
        self.drafts[key] = content

    def add_scratch_note(self, note: str) -> None:
        """Add a note to the scratchpad."""
        self.scratchpad.append(note)

    def record_revision(self, key: str, old_value: Any, new_value: Any) -> None:
        """Record a revision in the history."""
        self.revision_history.append(
            {
                "key": key,
                "old_value": old_value,
                "new_value": new_value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


SoftState = soft_state


@dataclass
class thermal_config:
    """Dynamic thermal configuration for LLM parameters."""

    profile: ThermalProfile = ThermalProfile.BALANCED
    temperature: float = 0.7
    top_p: float = 0.85
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_tokens: int | None = None
    node_overrides: dict[str, dict[str, float]] = field(default_factory=dict)

    def get_params_for_node(self, node_id: str) -> dict[str, float]:
        """Get thermal parameters for a specific node."""
        if node_id in self.node_overrides:
            return {
                "temperature": self.node_overrides[node_id].get("temperature", self.temperature),
                "top_p": self.node_overrides[node_id].get("top_p", self.top_p),
                "frequency_penalty": self.node_overrides[node_id].get(
                    "frequency_penalty",
                    self.frequency_penalty,
                ),
                "presence_penalty": self.node_overrides[node_id].get(
                    "presence_penalty",
                    self.presence_penalty,
                ),
            }
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }

    def set_node_profile(self, node_id: str, profile: ThermalProfile) -> None:
        """Set a thermal profile for a specific node."""
        profile_configs = {
            ThermalProfile.CREATIVITY_MAX: {"temperature": 0.9, "top_p": 0.95},
            ThermalProfile.CREATIVITY_HIGH: {"temperature": 0.8, "top_p": 0.9},
            ThermalProfile.BALANCED: {"temperature": 0.7, "top_p": 0.85},
            ThermalProfile.STRUCTURED: {"temperature": 0.3, "top_p": 0.7},
            ThermalProfile.PRECISION: {"temperature": 0.1, "top_p": 0.5},
        }
        self.node_overrides[node_id] = profile_configs[profile]


ThermalConfig = thermal_config


@dataclass
class signed_claim:
    """A factual claim with source attribution and confidence score."""

    claim: str
    source: str
    confidence: float
    evidence: str | None = None
    verified_at: datetime | None = None

    def __post_init__(self):
        if self.verified_at is None:
            self.verified_at = datetime.now(timezone.utc)


SignedClaim = signed_claim


class signal_context(BaseModel):
    """
    The Thermostatic Context Passport that enables high-temperature creativity
    while maintaining structural integrity through dual-state isolation.
    """

    hard_state: HardState = Field(default_factory=HardState)
    soft_state: SoftState = Field(default_factory=SoftState)
    thermal_config: ThermalConfig = Field(default_factory=ThermalConfig)
    signed_claims: list[signed_claim] = Field(default_factory=list)
    context_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        arbitrary_types_allowed = True

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.last_modified = datetime.now(timezone.utc)

    def add_signed_claim(
        self,
        claim: str,
        source: str,
        confidence: float,
        evidence: str | None = None,
    ) -> None:
        """Add a signed claim to the context."""
        signed_claim = signed_claim(claim=claim, source=source, confidence=confidence, evidence=evidence)
        self.signed_claims.append(signed_claim)


SignalContext = signal_context


class safety_profile_types(BaseModel):
    """Safety configuration profile used by execution profiles."""

    safety_tier: str = Field(
        default="standard",
        description="Safety tier: standard | strict | relaxed | debug",
    )
    pii_detection_enabled: bool = True
    policy_engine_enabled: bool = True


SafetyProfile = safety_profile_types

SafetyProfileTypes = safety_profile_types


class sim_scenario(BaseModel):
    """Simulation scenario definition."""

    id: str
    description: str
    initial_context: dict[str, Any]
    execution_profile_name: str
    run_count: int


SimScenario = sim_scenario


class sim_outcome(BaseModel):
    """Simulation outcome results."""

    scenario_id: str
    average_scores: dict[str, float]
    safety_incidents: int
    agent_conflict_count: int


SimOutcome = sim_outcome


class hypothesis(BaseModel):
    """Lightweight hypothesis used by the metacognition layer."""

    id: str
    agent_id: str
    content: str
    confidence: float = 0.0
    evidence_ids: list[str] = Field(default_factory=list)
    rationale: str | None = None


Hypothesis = hypothesis


class metacognition_report(BaseModel):
    """Aggregate view over a set of hypotheses and signals."""

    hypotheses: list[Hypothesis] = Field(default_factory=list)
    global_confidence: float = 0.0
    uncertainty_score: float = 0.0
    issues_detected: list[str] = Field(default_factory=list)


MetacognitionReport = metacognition_report


@dataclass
class golden_state_test_case:
    """Single golden-state test case."""

    id: str
    input_text: str
    expected_behavior: str
    metadata: dict[str, Any] = field(default_factory=dict)


GoldenStateTestCase = golden_state_test_case


@dataclass
class judge_verdict:
    """LM-as-a-judge style verdict."""

    score: float
    rating: str
    explanation: str


JudgeVerdict = judge_verdict


@dataclass
class eval_result:
    """Result of running a golden test case through the system."""

    test_id: str
    verdict: JudgeVerdict
    raw_output: str
    reasoning_trace: list[dict[str, Any]] = field(default_factory=list)


EvalResult = eval_result


class golden_case(BaseModel):
    """Golden test case for evaluation."""

    id: str
    input_text: str
    agent_sequence: list[str]
    expected_keypoints: list[str]
    correctness_criteria: dict[str, Any]


GoldenCase = golden_case


class golden_output(BaseModel):
    """Golden test output results."""

    case_id: str
    produced_keypoints: list[str]
    correctness_map: dict[str, bool]
    safety_decisions: dict[str, Any]
    metacognition_summary: dict[str, Any]
    final_verdict: Literal["pass", fail, borderline]


GoldenOutput = golden_output


class budget_profile(BaseModel):
    """High-level budget profile for cost/latency envelopes."""

    max_cost_usd: float = Field(default=0.1, ge=0.0)
    max_latency_ms: int = Field(default=3000, ge=0)


BudgetProfile = budget_profile

CORE_CONTRACTS_REGISTRY.update(
    {
        "ThermalProfile": ThermalProfile,
        "HardState": HardState,
        "SoftState": SoftState,
        "thermal_config": thermal_config,
        "signed_claim": signed_claim,
        "SignalContext": SignalContext,
        "SafetyProfile": SafetyProfile,
        "BudgetProfile": BudgetProfile,
        "SimScenario": SimScenario,
        "SimOutcome": SimOutcome,
        "Hypothesis": Hypothesis,
        "MetacognitionReport": MetacognitionReport,
        "GoldenStateTestCase": GoldenStateTestCase,
        "JudgeVerdict": JudgeVerdict,
        "EvalResult": EvalResult,
        "GoldenCase": GoldenCase,
        "GoldenOutput": GoldenOutput,
    },
)


@dataclass
class llm_response:
    """Standard LLM response format."""

    content: str
    model: str
    usage: dict[str, int] | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] | None = None


LLMResponse = llm_response

LlmResponse = llm_response


class message_type(str, Enum):
    """Message types for agent communication."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


MessageType = message_type


@dataclass
class residual_agent_message:
    """Message in agent conversation (from runtime_shared_models.py)."""

    role: MessageType
    content: str
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    metadata: dict[str, Any] | None = None


ResidualAgentMessage = residual_agent_message


@dataclass
class agent_response:
    """Response from agent execution."""

    message: ResidualAgentMessage
    success: bool
    error: str | None = None
    usage: dict[str, int] | None = None
    metadata: dict[str, Any] | None = None


AgentResponse = agent_response


class residual_validation_result(BaseModel):
    """Validation result for data or operations (from runtime_shared_models.py)."""

    is_valid: bool
    errors: list[str] = []
    warnings: list[str] = []
    metadata: dict[str, Any] = {}


ResidualValidationResult = residual_validation_result


class reasoning_config(BaseModel):
    """configuration for reasoning operations."""

    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: list[str] | None = None


ReasoningConfig = reasoning_config


class hop_status(str, Enum):
    """Status of hop execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


HopStatus = hop_status


class gate_decision(str, Enum):
    """Decision from validation gate."""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


GateDecision = gate_decision


class validation_severity(str, Enum):
    """Severity of validation issue."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


ValidationSeverity = validation_severity


@dataclass
class workflow_checkpoint:
    """Checkpoint in workflow execution."""

    hop_id: str
    status: HopStatus
    data: dict[str, Any]
    timestamp: str
    metadata: dict[str, Any] | None = None


WorkflowCheckpoint = workflow_checkpoint


@dataclass
class thematic_analysis:
    """Analysis of thematic content."""

    theme: str
    confidence: float
    keywords: list[str]
    sentiment: str | None = None


ThematicAnalysis = thematic_analysis


@dataclass
class rag_state:
    """State of RAG operations."""

    query: str
    retrieved_docs: list[dict[str, Any]]
    context: str
    response: str | None = None
    metadata: dict[str, Any] | None = None


RAGState = rag_state

RagState = rag_state


class circuit_state(str, Enum):
    """Circuit breaker state."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


CircuitState = circuit_state

CORE_CONTRACTS_REGISTRY.update(
    {
        "LLMResponse": LLMResponse,
        "MessageType": MessageType,
        "ResidualAgentMessage": ResidualAgentMessage,
        "AgentResponse": AgentResponse,
        "ResidualValidationResult": ResidualValidationResult,
        "ReasoningConfig": ReasoningConfig,
        "HopStatus": HopStatus,
        "GateDecision": GateDecision,
        "ValidationSeverity": ValidationSeverity,
        "WorkflowCheckpoint": WorkflowCheckpoint,
        "ThematicAnalysis": ThematicAnalysis,
        "RAGState": RAGState,
        "CircuitState": CircuitState,
    },
)


@dataclass
class file_paths_config:
    """File paths for data files used by the workflow."""

    master_resume: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "config" / "P1_core" / "data" / "master_resume.json"
        ),
    )
    hyphenation_rules: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "config" / "P1_core" / "data" / "hyphenation_rules.json"
        ),
    )
    app_tracker_schema: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "config" / "P1_core" / "data" / "app_tracker_schema.json"
        ),
    )
    artist_specs: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "config" / "P1_core" / "data" / "artist_specs.json"
        ),
    )
    artist_constraints: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "config" / "P1_core" / "data" / "artist_constraints.json"
        ),
    )
    validator_rules: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "config" / "P1_core" / "data" / "validator_rules.json"
        ),
    )
    prompts: Path = field(
        default_factory=lambda: (
            Path(__file__).parent.parent.parent / "config" / "P1_core" / "data" / "prompts.json"
        ),
    )


FilePathsConfig = file_paths_config


@dataclass
class artist_config:
    """configuration for the Artist Generator (resume content generation)."""

    provenance_split_targets: dict = field(default_factory=dict)
    bullet_word_count_ranges: dict = field(default_factory=dict)
    narrative_config: dict = field(default_factory=dict)


ArtistConfig = artist_config


@dataclass
class validator_config:
    """configuration for validation rules and constraints."""

    forbidden_verbs: list[str] = field(default_factory=list)
    required_sections: set[str] = field(default_factory=set)
    bullet_word_count_sections_to_check: set[str] = field(default_factory=set)
    provenance_split_targets: dict = field(default_factory=dict)
    pipeline_status_enum: list[str] = field(default_factory=list)


ValidatorConfig = validator_config


@dataclass
class prompts_config:
    """configuration for all prompt templates."""

    prompts: dict[str, dict[str, str]] = field(default_factory=dict)

    def get_prompt(self, prompt_name: str, section: str = "default") -> str:
        """Retrieve a prompt template by name and section."""
        if prompt_name not in self.prompts:
            raise KeyError(f"Prompt '{prompt_name}' not found in prompts.json")
        prompt_data = self.prompts[prompt_name]
        if section in prompt_data:
            return prompt_data[section]
        elif "default" in prompt_data:
            return prompt_data["default"]
        else:
            raise KeyError(f"Section '{section}' not found for prompt '{prompt_name}'")


PromptsConfig = prompts_config


@dataclass
class web_rag_config:
    """configuration for Web RAG (Retrieval Augmented Generation)."""

    peers_by_industry: dict = field(
        default_factory=lambda: {
            "Financial Technology": ["JPMorgan", "Goldman Sachs", "Morgan Stanley", "Stripe", "Square"],
            "Healthcare": ["UnitedHealth", "CVS Health", "Anthem", "Cigna", "Humana"],
            "Retail/E-Commerce": ["Amazon", "Walmart", "Target", "Shopify", "eBay"],
            "Software/SaaS": ["Salesforce", "Oracle", "SAP", "Adobe", "Workday"],
            "Technology": ["Google", "Microsoft", "Meta", "Apple", "Amazon"],
        },
    )


WebRagConfig = web_rag_config


@dataclass
class enricher_config:
    """configuration for data enrichment."""

    canonical_verbs: dict = field(
        default_factory=lambda: {
            "led": ["led", "lead", "leading"],
            "built": ["built", "build", "building"],
            "drove": ["drove", "drive", "driving"],
            "launched": ["launched", "launch", "launching"],
            "scaled": ["scaled", "scale", "scaling"],
            "delivered": ["delivered", "deliver", "delivering"],
            "achieved": ["achieved", "achieve", "achieving"],
            "established": ["established", "establish", "establishing"],
            "managed": ["managed", "manage", "managing"],
            "developed": ["developed", "develop", "developing"],
        },
    )


EnricherConfig = enricher_config


@dataclass
class enforcement_rag_config:
    """configuration for RAG system (renamed to avoid conflict with existing RAGState)."""

    MODEL: str = GEMINI_25_PRO_MODEL_ID
    max_tokens: int = 8192
    TEMPERATURE: float = 0.7
    api_max_retries: int = 7
    api_timeout_seconds: int = 120
    api_initial_backoff_seconds: float = 2.0
    api_max_backoff_seconds: float = 64.0
    api_backoff_multiplier: float = 2.0
    api_backoff_jitter: float = 0.1
    phase_max_retries: int = 3
    phase_timeout_seconds: int = 180
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    cache_ttl_days: int = 30
    telemetry_enabled: bool = True
    chroma_collection_name: str = "rag_librarian_v1"
    source_weights: dict[str, float] = field(
        default_factory=lambda: {
            "SOURCE_JD": 1.8,
            "SOURCE_COMPANY_BLOG": 1.5,
            "SOURCE_TARGET_EMPLOYEE": 1.4,
            "SOURCE_GARTNER_MQ": 1.2,
            "SOURCE_PEER_JD": 0.8,
            "SOURCE_GENERIC_PROFILE": 0.5,
            "LOCAL_NLP": 0.2,
        },
    )


EnforcementRAGConfig = enforcement_rag_config

EnforcementRagConfig = enforcement_rag_config


@dataclass
class enforcement_reasoning_config:
    """configuration for reasoning strategies (renamed to avoid conflict with existing ReasoningConfig)."""

    cot_min_paths: int = 2
    tot_branches: int = 3
    min_tot_depth: int = 2
    self_consistency: int = 3
    REFLEXION: bool = True
    max_reflexion_loops: int = 3


EnforcementReasoningConfig = enforcement_reasoning_config


@dataclass
class content_constraints_config:
    """Content-level constraints for word counts, sentence counts, etc."""

    TOTAL_WORD_COUNT_MIN: int = 870
    TOTAL_WORD_COUNT_MAX: int = 1030
    MIN_JD_KEYWORDS: int = 7
    HEADLINE_WORD_COUNT_MIN: int = 8
    HEADLINE_WORD_COUNT_MAX: int = 12
    HEADLINE_COMPONENT_WORDS_MIN: int = 2
    HEADLINE_COMPONENT_WORDS_MAX: int = 4
    EXEC_SUMMARY_SENTENCE_COUNT_MIN: int = 6
    EXEC_SUMMARY_SENTENCE_COUNT_MAX: int = 9
    EXEC_SUMMARY_WORD_COUNT_MIN: int = 140
    EXEC_SUMMARY_WORD_COUNT_MAX: int = 170
    K1_MIN_DIFFERENTIATORS: int = 4
    SKILLS_COUNT_MIN: int = 8
    SKILLS_COUNT_MAX: int = 12
    SKILLS_WORD_COUNT_MIN: int = 1
    SKILLS_WORD_COUNT_MAX: int = 3
    UNIFY_OVERVIEW_WORD_COUNT_MIN: int = 25
    UNIFY_OVERVIEW_WORD_COUNT_MAX: int = 40
    IBM_OVERVIEW_WORD_COUNT_MIN: int = 25
    IBM_OVERVIEW_WORD_COUNT_MAX: int = 35
    TRADERSENSE_NARRATIVE_WORD_COUNT_MIN: int = 40
    TRADERSENSE_NARRATIVE_WORD_COUNT_MAX: int = 60
    EY_NARRATIVE_WORD_COUNT_MIN: int = 40
    EY_NARRATIVE_WORD_COUNT_MAX: int = 60
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MIN: int = 50
    EARLY_CAREER_NARRATIVE_WORD_COUNT_MAX: int = 70
    COVER_LETTER_P1_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P1_WORD_COUNT_MAX: int = 100
    COVER_LETTER_P2_WORD_COUNT_MIN: int = 90
    COVER_LETTER_P2_WORD_COUNT_MAX: int = 120
    COVER_LETTER_P3_WORD_COUNT_MIN: int = 80
    COVER_LETTER_P3_WORD_COUNT_MAX: int = 100
    COVER_LETTER_JD_RELEVANCE_THRESHOLD: float = 0.35


ContentConstraintsConfig = content_constraints_config


@dataclass
class signal_control_config:
    """Signal control thresholds for quality and relevance."""

    K1_MAX_DIFFERENTIATORS: int = 4
    RESUME_MAX_JD_KEYWORDS: int = 16
    CL_MAX_JD_SIMILARITY: float = 0.65


SignalControlConfig = signal_control_config


@dataclass
class prompt_addendum_config:
    """configuration for reasoning prompt addendums."""

    HEADER: str = "\n\n**REASONING IMPLEMENTATION DIRECTIVES (v16.40):**\n\n"
    FOOTER: str = "\nAll directives MUST be followed in the output.\n"


PromptAddendumConfig = prompt_addendum_config


@dataclass
class app_config:
    """Master application configuration containing all sub-configs."""

    paths: FilePathsConfig = field(default_factory=FilePathsConfig)
    content_constraints: ContentConstraintsConfig = field(default_factory=ContentConstraintsConfig)
    signal_constraints: SignalControlConfig = field(default_factory=SignalControlConfig)
    web_rag: WebRagConfig = field(default_factory=WebRagConfig)
    enricher: EnricherConfig = field(default_factory=EnricherConfig)


AppConfig = app_config

CORE_CONTRACTS_REGISTRY.update(
    {
        "FilePathsConfig": FilePathsConfig,
        "ArtistConfig": ArtistConfig,
        "ValidatorConfig": ValidatorConfig,
        "PromptsConfig": PromptsConfig,
        "WebRagConfig": WebRagConfig,
        "EnricherConfig": EnricherConfig,
        "EnforcementRAGConfig": EnforcementRAGConfig,
        "EnforcementReasoningConfig": EnforcementReasoningConfig,
        "ContentConstraintsConfig": ContentConstraintsConfig,
        "SignalControlConfig": SignalControlConfig,
        "PromptAddendumConfig": PromptAddendumConfig,
        "AppConfig": AppConfig,
    },
)


@dataclass
class outreach_mission:
    """Complete mission specification (Input)"""

    mission_id: str
    sender_profile: dict[str, Any]
    recipient_profile: dict[str, Any]
    job_description: dict[str, Any]
    connection_status: str = "not_connected"
    prior_message_count: int = 0
    context: dict[str, Any] = field(default_factory=dict)


OutreachMission = outreach_mission


@dataclass
class profile_analysis:
    """DEPRECATED v13.0: Profile analysis output (kept for backward compatibility)"""

    archetype: str
    confidence: float
    reasoning: str
    key_indicators: list[str]
    needs_manual_override: bool = False


ProfileAnalysis = profile_analysis


@dataclass
class message_claim:
    """Individual claim with confidence"""

    text: str
    confidence: float
    supporting_sources: list[str]
    source_weights: list[float]


MessageClaim = message_claim


@dataclass
class rag_critique:
    """RAG quality critique"""

    confidence_score: float
    gaps_identified: list[str]
    refinement_tasks: list[str]
    reasoning: str
    is_sufficient: bool = False


RAGCritique = rag_critique

RagCritique = rag_critique


@dataclass
class enforcement_rag_result:
    """Single RAG retrieval result with metadata (renamed to avoid conflict)"""

    source: str
    source_type: str
    text: str
    extracted_keywords: list[str]
    source_weight: float
    age_days: int
    recipient_specific: bool
    CONFIDENCE: float = 1.0


EnforcementRAGResult = enforcement_rag_result

EnforcementRagResult = enforcement_rag_result


@dataclass
class sender_grounding_whitelists:
    """Output of SenderGroundingAgent for claim validation"""

    team_members: list[str] = field(default_factory=list)
    products: list[str] = field(default_factory=list)
    case_studies: list[str] = field(default_factory=list)
    quantifiable_achievements: list[str] = field(default_factory=list)
    raw_evidence: dict[str, list[str]] = field(default_factory=dict)


SenderGroundingWhitelists = sender_grounding_whitelists


@dataclass
class research_context:
    """DEPRECATED v13.0: Research context output (kept for backward compatibility)"""

    recipient_insights: list[str]
    company_context: list[str]
    recent_activity: list[str]
    rag_results: list[EnforcementRAGResult]
    sender_grounding: SenderGroundingWhitelists | None = None
    adversarial_findings: list[str] = field(default_factory=list)


ResearchContext = research_context


@dataclass
class message_scaffold:
    """DEPRECATED v13.0: Message scaffold output (kept for backward compatibility)"""

    route: str
    archetype: str
    sections: dict[str, dict[str, Any]]
    constraints: dict[str, Any]
    locked_sections: set[str] = field(default_factory=set)


MessageScaffold = message_scaffold


@dataclass
class generated_message:
    """DEPRECATED v13.0: Generated message output (kept for backward compatibility)"""

    content: str
    word_count: int
    char_count: int
    route: str
    archetype: str
    generation_temperature: float
    generation_attempts: int
    checksum: str


GeneratedMessage = generated_message


@dataclass
class enforcement_validation_result:
    """Result from validation check (renamed to avoid conflict with existing ValidationResult)"""

    passed: bool
    severity: str
    rule_id: str
    message: str
    details: dict[str, Any] | None = None


EnforcementValidationResult = enforcement_validation_result


@dataclass
class qa_report:
    """DEPRECATED v13.0: QA report output (kept for backward compatibility)"""

    mission_id: str
    validation_results: list[EnforcementValidationResult]
    passed: bool
    timestamp: str


QAReport = qa_report

QaReport = qa_report

CORE_CONTRACTS_REGISTRY.update(
    {
        "OutreachMission": OutreachMission,
        "ProfileAnalysis": ProfileAnalysis,
        "MessageClaim": MessageClaim,
        "RAGCritique": RAGCritique,
        "EnforcementRAGResult": EnforcementRAGResult,
        "SenderGroundingWhitelists": SenderGroundingWhitelists,
        "ResearchContext": ResearchContext,
        "MessageScaffold": MessageScaffold,
        "GeneratedMessage": GeneratedMessage,
        "EnforcementValidationResult": EnforcementValidationResult,
        "QAReport": QAReport,
    },
)


@dataclass
class executive_profile:
    """Executive profile for leadership layer research."""

    name: str
    title: str
    ownership: str
    strategic_focus: str | None = None
    linkedin_url: str | None = None


ExecutiveProfile = executive_profile


@dataclass
class financial_metric:
    """Financial metric with validation."""

    metric_name: str
    value: str
    period: str
    source_citation: str
    yoy_change: str | None = None

    def validate(self) -> bool:
        return bool(self.metric_name and self.value and self.source_citation)


FinancialMetric = financial_metric


@dataclass
class technical_implementation:
    """Technical implementation details with validation."""

    technology_name: str
    implementation_details: str
    source_citation: str
    performance_gain: str | None = None

    def validate(self) -> bool:
        return bool(self.technology_name and self.implementation_details and self.source_citation)


TechnicalImplementation = technical_implementation


@dataclass
class strategic_layer:
    """Strategic research layer."""

    core_thesis: str
    financial_proof_points: list[FinancialMetric] = field(default_factory=list)
    strategic_initiatives: list[str] = field(default_factory=list)

    def validate(self) -> bool:
        if not self.core_thesis or len(self.core_thesis) < 20:
            return False
        if len(self.financial_proof_points) < 2:
            return False
        return all(metric.validate() for metric in self.financial_proof_points)


StrategicLayer = strategic_layer


@dataclass
class technical_layer:
    """Technical research layer."""

    key_technologies: list[TechnicalImplementation] = field(default_factory=list)
    infrastructure_stack: list[str] = field(default_factory=list)
    implementation_summary: str | None = None

    def validate(self) -> bool:
        if len(self.key_technologies) < 2:
            return False
        return all(tech.validate() for tech in self.key_technologies)


TechnicalLayer = technical_layer


@dataclass
class leadership_layer:
    """Leadership research layer."""

    key_executives: list[ExecutiveProfile] = field(default_factory=list)
    organizational_structure: str | None = None

    def validate(self) -> bool:
        if len(self.key_executives) < 2:
            return False
        return all(exec.name and exec.title and exec.ownership for exec in self.key_executives)


LeadershipLayer = leadership_layer


@dataclass
class citation_map:
    """Citation tracking for research sources."""

    citations: dict[str, str] = field(default_factory=dict)

    def add_citation(self, source_id: str, url: str) -> None:
        self.citations[source_id] = url

    def get_citation(self, source_id: str) -> str | None:
        return self.citations.get(source_id)

    def validate(self) -> bool:
        return len(self.citations) >= 3


CitationMap = citation_map


@dataclass
class deep_research_output:
    """Output data structure for K.2.5 deep research results."""

    company_name: str
    strategic_layer: StrategicLayer
    technical_layer: TechnicalLayer
    leadership_layer: LeadershipLayer
    citation_map: CitationMap
    research_timestamp: str | None = None

    def validate(self) -> bool:
        return (
            self.strategic_layer.validate()
            and self.technical_layer.validate()
            and self.leadership_layer.validate()
            and self.citation_map.validate()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_name": self.company_name,
            "strategic_layer": {
                "core_thesis": self.strategic_layer.core_thesis,
                "financial_proof_points": [
                    {
                        "metric_name": m.metric_name,
                        "value": m.value,
                        "period": m.period,
                        "yoy_change": m.yoy_change,
                        "source_citation": m.source_citation,
                    }
                    for m in self.strategic_layer.financial_proof_points
                ],
                "strategic_initiatives": self.strategic_layer.strategic_initiatives,
            },
            "technical_layer": {
                "key_technologies": [
                    {
                        "technology_name": t.technology_name,
                        "implementation_details": t.implementation_details,
                        "performance_gain": t.performance_gain,
                        "source_citation": t.source_citation,
                    }
                    for t in self.technical_layer.key_technologies
                ],
                "infrastructure_stack": self.technical_layer.infrastructure_stack,
                "implementation_summary": self.technical_layer.implementation_summary,
            },
            "leadership_layer": {
                "key_executives": [
                    {
                        "name": e.name,
                        "title": e.title,
                        "ownership": e.ownership,
                        "strategic_focus": e.strategic_focus,
                        "linkedin_url": e.linkedin_url,
                    }
                    for e in self.leadership_layer.key_executives
                ],
                "organizational_structure": self.leadership_layer.organizational_structure,
            },
            "citation_map": self.citation_map.citations,
            "research_timestamp": self.research_timestamp,
        }


DeepResearchOutput = deep_research_output


@dataclass
class research_hop_result:
    """Result from a research hop phase."""

    phase: str
    query: str
    results: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)
    success: bool = True
    error_message: str | None = None


ResearchHopResult = research_hop_result


@dataclass
class integrity_gate_result:
    """Result from integrity gate validation."""

    passed: bool
    rejection_reasons: list[str] = field(default_factory=list)
    detailed_violations: list[str] = field(default_factory=list)
    depth_score: float = 0.0

    def add_violation(self, reason: str, detail: str) -> None:
        self.rejection_reasons.append(reason)
        self.detailed_violations.append(detail)
        self.passed = False


IntegrityGateResult = integrity_gate_result

CORE_CONTRACTS_REGISTRY.update(
    {
        "ExecutiveProfile": ExecutiveProfile,
        "FinancialMetric": FinancialMetric,
        "TechnicalImplementation": TechnicalImplementation,
        "StrategicLayer": StrategicLayer,
        "TechnicalLayer": TechnicalLayer,
        "LeadershipLayer": LeadershipLayer,
        "CitationMap": CitationMap,
        "DeepResearchOutput": DeepResearchOutput,
        "ResearchHopResult": ResearchHopResult,
        "IntegrityGateResult": IntegrityGateResult,
    },
)


@dataclass
class subject_line_brief:
    """Brief for subject line generation."""

    word_count: tuple[int, int]
    tone: str
    forbidden_phrases: list[str] = field(default_factory=list)


SubjectLineBrief = subject_line_brief


@dataclass
class message_body_brief:
    """Brief for message body generation."""

    word_count: tuple[int, int]
    jargon_level: str
    focus: str


MessageBodyBrief = message_body_brief


@dataclass
class cta_brief:
    """Brief for call-to-action generation."""

    word_count: tuple[int, int]
    tone: str
    strategy: str | None = None


CTABrief = cta_brief

CtaBrief = cta_brief


@dataclass
class creative_brief:
    """Complete creative brief for message generation."""

    subject_line: SubjectLineBrief
    message_body: MessageBodyBrief
    cta: CTABrief


CreativeBrief = creative_brief


@dataclass
class archetype_template:
    """Complete template for an archetype."""

    archetype: str
    system_instructions: str
    tone: str
    approach: str
    avoid: str
    creative_brief: CreativeBrief


ArchetypeTemplate = archetype_template


@dataclass
class signature_template:
    """Template for message signature."""

    template: str
    use_for: list[str]
    line_count: int


SignatureTemplate = signature_template


@dataclass
class greeting_template:
    """Template for message greeting."""

    template: str
    note: str


GreetingTemplate = greeting_template

CORE_CONTRACTS_REGISTRY.update(
    {
        "SubjectLineBrief": SubjectLineBrief,
        "MessageBodyBrief": MessageBodyBrief,
        "CTABrief": CTABrief,
        "CreativeBrief": CreativeBrief,
        "ArchetypeTemplate": ArchetypeTemplate,
        "SignatureTemplate": SignatureTemplate,
        "GreetingTemplate": GreetingTemplate,
    },
)


@dataclass
class api_call_metrics:
    """Metrics for API call tracking"""

    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_tokens_used: int = 0
    total_latency_ms: float = 0
    safety_blocks: int = 0
    rate_limits: int = 0


APICallMetrics = api_call_metrics

ApiCallMetrics = api_call_metrics


@dataclass
class immutable_staging_buffer:
    """Immutable buffer for staging data transformations."""

    data: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    timestamp: str | None = None
    checksum: str | None = None

    def with_data(self, new_data: dict[str, Any]) -> ImmutableStagingBuffer:
        """Return a new buffer with updated data."""
        from datetime import datetime, timezone

        return ImmutableStagingBuffer(
            _data={**self.data, **new_data},
            _version=self.version + 1,
            _timestamp=datetime.now(timezone.utc).isoformat(),
            _checksum=None,
        )

    def clear(self) -> ImmutableStagingBuffer:
        """Return a new empty buffer."""
        from datetime import datetime, timezone

        return ImmutableStagingBuffer(
            _version=self.version + 1, _timestamp=datetime.now(timezone.utc).isoformat()
        )


ImmutableStagingBuffer = immutable_staging_buffer

CORE_CONTRACTS_REGISTRY.update(
    {"APICallMetrics": APICallMetrics, "ImmutableStagingBuffer": ImmutableStagingBuffer},
)


class voice_type(str, Enum):
    """Voice type for content generation."""

    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"
    THIRD_PERSON_IMPLIED = "third_person_implied"


VoiceType = voice_type


class provenance_strategy(str, Enum):
    """Strategy for bullet provenance."""

    JD_FIT_BASED = "jd_fit_based"
    INTERNAL_FIRST = "internal_first"
    TOP_SKILLS = "top_skills"
    BALANCED = "balanced"


ProvenanceStrategy = provenance_strategy


class message_route(str, Enum):
    """Message route types for LinkedIn outreach."""

    CONNECTION_REQUEST = "connection_request"
    INMAIL = "inmail"
    FOLLOW_UP = "follow_up"
    DIRECT_MESSAGE = "direct_message"


MessageRoute = message_route


class recipient_archetype(str, Enum):
    """Recipient archetype classifications."""

    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    RECRUITER = "recruiter"
    PEER = "peer"


RecipientArchetype = recipient_archetype


class signature_format(str, Enum):
    """Signature format types."""

    STANDARD = "standard"
    MINIMAL = "minimal"
    PROFESSIONAL = "professional"
    CASUAL = "casual"


SignatureFormat = signature_format


class cta_format(str, Enum):
    """Call-to-action format types."""

    STANDARD = "standard"
    QUESTION = "question"
    DIRECT_ASK = "direct_ask"
    SOFT_CLOSE = "soft_close"


CTAFormat = cta_format

CtaFormat = cta_format

CORE_CONTRACTS_REGISTRY.update(
    {
        "VoiceType": VoiceType,
        "ProvenanceStrategy": ProvenanceStrategy,
        "MessageRoute": MessageRoute,
        "RecipientArchetype": RecipientArchetype,
        "SignatureFormat": SignatureFormat,
        "CTAFormat": CTAFormat,
    },
)


@dataclass
class word_count_constraint:
    """Word count constraint for a section."""

    min_words: int
    max_words: int

    def validate(self, text: str) -> tuple[bool, str]:
        """Validate text against word count constraint."""
        word_count = len(text.split())
        if word_count < self.min_words:
            return (False, f"Word count {word_count} below minimum {self.min_words}")
        if word_count > self.max_words:
            return (False, f"Word count {word_count} above maximum {self.max_words}")
        return (True, "")


WordCountConstraint = word_count_constraint


@dataclass
class char_count_constraint:
    """Character count constraint for a section."""

    max_chars: int

    def validate(self, text: str) -> tuple[bool, str]:
        """Validate text against character count constraint."""
        char_count = len(text)
        if char_count > self.max_chars:
            return (False, f"Character count {char_count} above maximum {self.max_chars}")
        return (True, "")


CharCountConstraint = char_count_constraint


@dataclass
class structure_constraint:
    """Structure constraint for a section."""

    structure: str
    segment_word_limit: int | None = None
    exclusions: list[str] = field(default_factory=list)


StructureConstraint = structure_constraint


@dataclass
class headline_brief:
    """Creative brief for headline section."""

    word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(8, 12))
    char_count_max: int = 90
    STRUCTURE: str = "Domain | Leadership | Value Prop"
    segment_word_limit: int = 3
    exclusions: list[str] = field(
        default_factory=lambda: ["and", "a", "an", "the", "in", "on", "at", "for", "to", "of"],
    )
    GUIDANCE: str = "Must incorporate differentiator keywords from the Competitive Analysis."


HeadlineBrief = headline_brief


@dataclass
class hop_input:
    """Input specification for a hop."""

    source_artifact: str
    required: bool = True
    description: str = ""


HopInput = hop_input


@dataclass
class hop_output:
    """Output specification for a hop."""

    artifact_id: str
    DESCRIPTION: str = ""


HopOutput = hop_output


@dataclass
class hop_spec:
    """Specification for a workflow hop."""

    id: str
    script: str
    description: str
    inputs: list[HopInput] = field(default_factory=list)
    outputs: list[HopOutput] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    extra_args: list[str] = field(default_factory=list)


HopSpec = hop_spec


@dataclass
class workflow_spec:
    """Specification for a complete workflow."""

    name: str
    version: str
    hops: list[HopSpec]


WorkflowSpec = workflow_spec

CORE_CONTRACTS_REGISTRY.update(
    {
        "WordCountConstraint": WordCountConstraint,
        "CharCountConstraint": CharCountConstraint,
        "StructureConstraint": StructureConstraint,
        "HeadlineBrief": HeadlineBrief,
        "HopInput": HopInput,
        "HopOutput": HopOutput,
        "RetryPolicy": RetryPolicy,
        "HopSpec": HopSpec,
        "WorkflowSpec": WorkflowSpec,
    },
)


@dataclass
class experience_bullets_brief:
    """Creative brief for experience bullets section."""

    provenance_strategy: ProvenanceStrategy = ProvenanceStrategy.JD_FIT_BASED
    provenance_map: dict[str, str] = field(
        default_factory=lambda: {"Unify Consulting": "4V-3T-0S", "IBM": "4V-2T-0S"},
    )
    default_provenance_fallback: str = "10V-0A-0S"
    selection_logic: str = "Multi-factor scoring algorithm: (JD Keyword Overlap * 0.5) + (Metric Impact * 0.3) + (Uniqueness * 0.2)"
    overview_word_count: dict[str, WordCountConstraint] = field(
        default_factory=lambda: {"k6": WordCountConstraint(25, 33), "k7": WordCountConstraint(22, 28)},
    )
    k6_word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(28, 33))
    k7_word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(24, 30))
    GUIDANCE: str = "Must use standard technology terms (e.g., 'cloud data platform' instead of 'Snowflake')."


ExperienceBulletsBrief = experience_bullets_brief


@dataclass
class leadership_competencies_brief:
    """Creative brief for leadership competencies section."""

    TITLE: str = "Strategic & Technical Competencies"
    sourcing_strategy: ProvenanceStrategy = ProvenanceStrategy.INTERNAL_FIRST
    COUNT: int = 6
    word_count_per_desc: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(24, 30))


LeadershipCompetenciesBrief = leadership_competencies_brief


@dataclass
class cover_letter_brief:
    """Creative brief for cover letter section."""

    STRUCTURE: str = "1-intro-2-body"
    word_count_per_para: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(85, 100))
    min_specific_details: int = 4
    forbidden_patterns: list[str] = field(
        default_factory=lambda: ["At [COMPANY], I...", "During my time at..."],
    )
    signature_generation_policy: str = "DYNAMIC_FROM_OWNER_CONTACT"


CoverLetterBrief = cover_letter_brief


@dataclass
class optimized_skills_brief:
    """Creative brief for optimized skills list section."""

    sourcing_strategy: ProvenanceStrategy = ProvenanceStrategy.TOP_SKILLS
    LOGIC: str = "1. Extract and rank the top 12 skills from the JD. 2. Cross-reference this list against the master resume's competencies and bullet points. 3. Prioritize and render the final list based on the intersection."


OptimizedSkillsBrief = optimized_skills_brief


@dataclass
class rg_creative_brief:
    """Complete creative brief for resume generation."""

    headline: HeadlineBrief = field(default_factory=HeadlineBrief)
    executive_summary: ExecutiveSummaryBrief = None
    experience_bullets: ExperienceBulletsBrief = field(default_factory=ExperienceBulletsBrief)
    leadership_competencies: LeadershipCompetenciesBrief = field(default_factory=LeadershipCompetenciesBrief)
    cover_letter: CoverLetterBrief = field(default_factory=CoverLetterBrief)
    optimized_skills: OptimizedSkillsBrief = field(default_factory=OptimizedSkillsBrief)


RGCreativeBrief = rg_creative_brief

RgCreativeBrief = rg_creative_brief


@dataclass
class executive_summary_brief:
    """Creative brief for executive summary section."""

    word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(120, 140))
    voice: VoiceType = VoiceType.THIRD_PERSON_IMPLIED
    forbidden_patterns: list[str] = field(
        default_factory=lambda: ["I have", "My expertise", "At [COMPANY],", "I"],
    )
    GUIDANCE: str = "Subtly incorporate the 'primary_theme' from the K.0 analysis, while strictly maintaining the narrative voice of a professional executive biography. Do not use phrasing from the job posting."


ExecutiveSummaryBrief = executive_summary_brief

CORE_CONTRACTS_REGISTRY.update(
    {
        "ExperienceBulletsBrief": ExperienceBulletsBrief,
        "LeadershipCompetenciesBrief": LeadershipCompetenciesBrief,
        "CoverLetterBrief": CoverLetterBrief,
        "OptimizedSkillsBrief": OptimizedSkillsBrief,
        "RGCreativeBrief": RGCreativeBrief,
        "ExecutiveSummaryBrief": ExecutiveSummaryBrief,
    },
)


@dataclass
class route_conditions:
    """Conditions for route selection."""

    connection_status: str | None = None
    prior_message_count: int | None = None
    prior_message_count_gt: int | None = None
    prior_message_count_gte: int | None = None


RouteConditions = route_conditions


@dataclass
class route_constraints:
    """Constraints for a message route."""

    char_limit: int | None = None
    word_range: tuple[int, int] | None = None
    signature_format: SignatureFormat = SignatureFormat.STANDARD
    subject_line_enabled: bool = False
    attachments_enabled: bool = False
    cta_format: CTAFormat = CTAFormat.STANDARD
    cta_max_words: int | None = None
    greeting_format: str = "Hi {first_name},"


RouteConstraints = route_constraints


@dataclass
class route_config:
    """Complete configuration for a message route."""

    route: MessageRoute
    conditions: RouteConditions
    constraints: RouteConstraints


RouteConfig = route_config


@dataclass
class archetone_config:
    """Tone configuration for an archetype."""

    message_tone: str
    verb_preference: list[str]
    jargon_level: str
    formality: str
    focus: str


ArchetoneConfig = archetone_config


@dataclass
class temperature_config:
    """Temperature configuration for LLM generation."""

    base_temperature: float
    escalation_step: float = 0.15
    max_temperature: float = 0.95
    max_creative_retries: int = 3


TemperatureConfig = temperature_config

CORE_CONTRACTS_REGISTRY.update(
    {
        "RouteConditions": RouteConditions,
        "RouteConstraints": RouteConstraints,
        "RouteConfig": RouteConfig,
        "ArchetoneConfig": ArchetoneConfig,
        "TemperatureConfig": TemperatureConfig,
    },
)


logger = logging.getLogger(__name__)


class mission_priority(str, Enum):
    """Mission priority levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


MissionPriority = mission_priority


class mission_status(str, Enum):
    """Mission status values."""

    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


MissionStatus = mission_status


@dataclass(frozen=True)
class mission_phase(sovereign_base_model_types):
    """A single phase of a mission."""

    name: str
    agents: list[str]
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"
    result: dict[str, Any] | None = None


MissionPhase = mission_phase


@dataclass(frozen=True)
class mission_plan(sovereign_base_model_types):
    """
    Complete mission plan with Builder pattern support.

    Sovereign Builder Pattern (Phase 12):
    - Fluent API for mission construction
    - Immutable result with constitutional validation
    - observability stamping at build time
    """

    mission_id: str
    cycle_id: int
    priority: MissionPriority
    objective: str
    phases: list[MissionPhase] = field(default_factory=list)
    risk_assessment: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: MissionStatus = MissionStatus.PLANNED

    class Builder:
        """
        Sovereign Builder for MissionPlan – Phase 12 (Dec 26, 2025)
        Enforces:
        - Fluent, readable mission definitions
        - Early validation (uniqueness, required fields)
        - observability (construction logging)
        """

        def __init__(self):
            self._mission_id: str | None = None
            self._cycle_id: int | None = None
            self._priority: MissionPriority = MissionPriority.MEDIUM
            self._objective: str | None = None
            self._phases: list[MissionPhase] = []
            self._risk_assessment: dict = {}
            self._phase_names: set = set()

        def with_mission_id(self, mission_id: str) -> MissionPlan.Builder:
            self._mission_id = mission_id
            return self

        def with_cycle(self, cycle_id: int) -> MissionPlan.Builder:
            self._cycle_id = cycle_id
            return self

        def with_priority(self, priority: MissionPriority) -> MissionPlan.Builder:
            self._priority = priority
            return self

        def with_objective(self, objective: str) -> MissionPlan.Builder:
            self._objective = objective
            return self

        def add_phase(self, phase: MissionPhase) -> MissionPlan.Builder:
            if phase.name in self._phase_names:
                raise ValueError(f"Sovereignty Violation: Duplicate phase name detected: {phase.name}")
            self._phase_names.add(phase.name)
            self._phases.append(phase)
            return self

        def with_risk_assessment(self, assessment: dict) -> MissionPlan.Builder:
            self._risk_assessment = assessment
            return self

        def build(self) -> MissionPlan:
            """Construct immutable MissionPlan with sovereign validation"""
            if not self._mission_id:
                raise ValueError("mission_id is required")
            if self._cycle_id is None:
                raise ValueError("cycle_id is required")
            if not self._objective:
                raise ValueError("objective is required")
            if not self._phases:
                raise ValueError("At least one phase required")
            self._detect_dependency_cycles()
            logger.info(
                f"[BUILDER] Constructing MissionPlan {self._mission_id} | Phases: {len(self._phases)} | Priority: {self._priority}",
            )
            return MissionPlan(
                mission_id=self._mission_id,
                cycle_id=self._cycle_id,
                priority=self._priority,
                objective=self._objective,
                phases=self._phases.copy(),
                risk_assessment=self._risk_assessment.copy(),
            )

        def _detect_dependency_cycles(self) -> None:
            """
            Sovereign cycle detection using DFS (Depth-First Search)
            Prevents infinite loops in orchestration
            """
            if not self._phases:
                return
            graph: dict[str, list[str]] = {p.name: p.dependencies for p in self._phases}
            visited = set()
            rec_stack = set()

            def has_cycle(node: str) -> bool:
                visited.add(node)
                rec_stack.add(node)
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                rec_stack.remove(node)
                return False

            for phase_name in graph:
                if phase_name not in visited:
                    if has_cycle(phase_name):
                        raise ValueError(
                            f"Sovereignty Breach: Dependency cycle detected in MissionPlan {self._mission_id} involving phases: {list(rec_stack if rec_stack else graph.keys())}",
                        )


MissionPlan = mission_plan


@dataclass(frozen=True)
class thinking_step(sovereign_base_model_types):
    """A single step in a thought chain."""

    step_id: int
    thought: str
    action: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


ThinkingStep = thinking_step


@dataclass(frozen=True)
class revision_step(sovereign_base_model_types):
    """A revision made to the thought chain."""

    revision_number: int
    original_step: int
    revised_thought: str
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


RevisionStep = revision_step


@dataclass(frozen=True)
class thought_chain(sovereign_base_model_types):
    """
    Thought chain for reasoning trace with Builder pattern support.

    Sovereign Builder Pattern (Phase 12):
    - Ensures logical continuity in reasoning steps
    - Immutable chain with timestamp tracking
    - Constitutional validation of chain integrity
    """

    chain_id: str
    goal: str
    steps: list[ThinkingStep] = field(default_factory=list)
    active_hypotheses: list[Hypothesis] = field(default_factory=list)
    revisions: list[RevisionStep] = field(default_factory=list)
    final_conclusion: str | None = None
    success: bool = False
    duration_seconds: float = 0.0

    class Builder:
        """
        Sovereign Builder for ThoughtChain – Phase 12 (Dec 26, 2025)
        Enforces sequential integrity, constitutional validation, and observability.
        """

        def __init__(self):
            self._chain_id: str | None = None
            self._goal: str | None = None
            self._steps: list[ThinkingStep] = []
            self._hypotheses: list[Hypothesis] = []
            self._revisions: list[RevisionStep] = []
            self._final_conclusion: str | None = None
            self._success: bool = False
            self._duration_seconds: float = 0.0

        def with_chain_id(self, chain_id: str) -> ThoughtChain.Builder:
            self._chain_id = chain_id
            return self

        def with_goal(self, goal: str) -> ThoughtChain.Builder:
            self._goal = goal
            return self

        def add_step(self, step: ThinkingStep) -> ThoughtChain.Builder:
            """Adds a step while enforcing sequential ID integrity."""
            if self._steps and step.step_id <= self._steps[-1].step_id:
                raise ValueError(f"Step ID {step.step_id} is not sequential.")
            self._steps.append(step)
            return self

        def add_hypothesis(self, hypothesis: Hypothesis) -> ThoughtChain.Builder:
            self._hypotheses.append(hypothesis)
            return self

        def with_final_conclusion(self, conclusion: str) -> ThoughtChain.Builder:
            """Seals the chain with a conclusion and auto-marks success."""
            self._final_conclusion = conclusion
            self._success = True
            return self

        def mark_failed(self) -> ThoughtChain.Builder:
            self._success = False
            return self

        def build(self) -> ThoughtChain:
            """Construct immutable ThoughtChain with constitutional validation."""
            if not self._chain_id or not self._goal:
                raise ValueError("ThoughtChain construction failed: chain_id and goal are mandatory.")
            if self._success and (not self._final_conclusion):
                raise ValueError("Inconsistent State: Success requires a final_conclusion.")
            if self._steps and self._steps[0].step_id != 1:
                raise ValueError("Sovereignty Violation: Reasoning steps must begin with ID 1.")
            logger.info(f"[AUDIT] ThoughtChain Constructed: {self._chain_id} | Steps: {len(self._steps)}")
            return ThoughtChain(
                chain_id=self._chain_id,
                goal=self._goal,
                steps=self._steps.copy(),
                active_hypotheses=self._hypotheses.copy(),
                revisions=self._revisions.copy(),
                final_conclusion=self._final_conclusion,
                success=self._success,
                duration_seconds=self._duration_seconds,
            )


ThoughtChain = thought_chain


@dataclass(frozen=True)
class constitutional_violation(sovereign_base_model_types):
    """
    Constitutional violation record with Builder pattern support.

    Sovereign Builder Pattern (Phase 12):
    - Fluent judicial record construction
    - Severity validation
    - Auto-ID generation
    - observability warning trail on detection
    """

    violation_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    guardian: str
    dimension: str
    severity: str
    file_path: str
    line_number: int | None = None
    description: str
    evidence: str
    suggested_fix: str | None = None
    status: str = "detected"

    class Builder:
        """
        Sovereign Builder for ConstitutionalViolation – Phase 12 (Dec 26, 2025)
        Enforces:
        - Fluent, immutable judicial records
        - Severity and dimension validation
        - observability warning trail on creation
        """

        def __init__(self):
            self._violation_id: str | None = None
            self._guardian: str | None = None
            self._dimension: str | None = None
            self._severity: str | None = None
            self._file_path: str | None = None
            self._line_number: int | None = None
            self._description: str | None = None
            self._evidence: str | None = None
            self._suggested_fix: str | None = None

        def with_guardian(self, guardian: str) -> ConstitutionalViolation.Builder:
            self._guardian = guardian
            return self

        def in_dimension(self, dimension: str) -> ConstitutionalViolation.Builder:
            self._dimension = dimension
            return self

        def with_severity(self, severity: str) -> ConstitutionalViolation.Builder:
            if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                raise ValueError(f"Sovereignty Violation: Invalid severity: {severity}")
            self._severity = severity
            return self

        def at_location(
            self,
            file_path: str,
            line_number: int | None = None,
        ) -> ConstitutionalViolation.Builder:
            self._file_path = file_path
            self._line_number = line_number
            return self

        def with_description(self, description: str) -> ConstitutionalViolation.Builder:
            self._description = description
            return self

        def with_evidence(self, evidence: str) -> ConstitutionalViolation.Builder:
            self._evidence = evidence
            return self

        def with_suggested_fix(self, fix: str) -> ConstitutionalViolation.Builder:
            self._suggested_fix = fix
            return self

        def build(self) -> ConstitutionalViolation:
            """Construct immutable ConstitutionalViolation with final validation."""
            required = {
                "guardian": self._guardian,
                "dimension": self._dimension,
                "severity": self._severity,
                "file_path": self._file_path,
                "description": self._description,
            }
            for field, value in required.items():
                if not value:
                    raise ValueError(f"Constitutional Reporting Error: {field} is required.")
            if not self._violation_id:
                self._violation_id = f"violation-{uuid.uuid4().hex[:8]}"
            logger.warning(
                f"[AUDIT] Violation Detected: {self._violation_id} | Severity: {self._severity} | Dimension: {self._dimension} | Loc: {self._file_path}:{self._line_number or 'N/A'}",
            )
            return ConstitutionalViolation(
                violation_id=self._violation_id,
                guardian=self._guardian,
                dimension=self._dimension,
                severity=self._severity,
                file_path=self._file_path,
                line_number=self._line_number,
                description=self._description,
                evidence=self._evidence or "Not recorded",
                suggested_fix=self._suggested_fix,
            )


ConstitutionalViolation = constitutional_violation


@dataclass(frozen=True)
class healing_action(sovereign_base_model_types):
    """
    Healing action record with Builder pattern support.

    Sovereign Builder Pattern (Phase 12):
    - Fluent correction record construction
    - Explicit success/failure outcome paths
    - Transaction linkage for atomic operations
    - observability forensic audit trail
    """

    action_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    strategy: str
    action_type: str
    target_file: str
    target_line: int | None = None
    reason: str
    success: bool
    error_message: str | None = None
    backup_path: str | None = None
    transaction_id: str | None = None

    class Builder:
        """
        Sovereign Builder for HealingAction – Phase 12 (Dec 26, 2025)
        Enforces:
        - Fluent, immutable record of system corrections
        - Explicit success/failure outcome paths
        - observability integration for forensic audits
        - Atomic transaction linkage
        """

        def __init__(self):
            self._action_id: str | None = None
            self._strategy: str | None = None
            self._action_type: str | None = None
            self._target_file: str | None = None
            self._target_line: int | None = None
            self._reason: str | None = None
            self._success: bool | None = None
            self._error_message: str | None = None
            self._backup_path: str | None = None
            self._transaction_id: str | None = None

        def with_strategy(self, strategy: str) -> HealingAction.Builder:
            self._strategy = strategy
            return self

        def with_action_type(self, action_type: str) -> HealingAction.Builder:
            self._action_type = action_type
            return self

        def targeting(self, file: str, line: int | None = None) -> HealingAction.Builder:
            self._target_file = file
            self._target_line = line
            return self

        def for_reason(self, reason: str) -> HealingAction.Builder:
            self._reason = reason
            return self

        def succeeded(self) -> HealingAction.Builder:
            self._success = True
            self._error_message = None
            return self

        def failed(self, error: str) -> HealingAction.Builder:
            self._success = False
            self._error_message = error
            return self

        def with_backup(self, backup_path: str) -> HealingAction.Builder:
            self._backup_path = backup_path
            return self

        def in_transaction(self, transaction_id: str) -> HealingAction.Builder:
            self._transaction_id = transaction_id
            return self

        def build(self) -> HealingAction:
            """Construct immutable HealingAction with final constitutional validation."""
            required = {
                "strategy": self._strategy,
                "action_type": self._action_type,
                "target_file": self._target_file,
                "reason": self._reason,
            }
            for field, value in required.items():
                if not value:
                    raise ValueError(f"Sovereignty Reporting Error: {field} is required.")
            if self._success is None:
                raise ValueError("Incomplete Record: Must specify outcome via succeeded() or failed().")
            if not self._action_id:
                self._action_id = f"healact-{uuid.uuid4().hex[:8]}"
            status = "SUCCESS" if self._success else "FAILED"
            logger.info(
                f"[AUDIT] Healing Action Logged: {self._action_id} | Outcome: {status} | Strategy: {self._strategy} | Type: {self._action_type} | File: {self._target_file}",
            )
            return HealingAction(
                action_id=self._action_id,
                strategy=self._strategy,
                action_type=self._action_type,
                target_file=self._target_file,
                target_line=self._target_line,
                reason=self._reason,
                success=self._success,
                error_message=self._error_message,
                backup_path=self._backup_path,
                transaction_id=self._transaction_id,
            )


HealingAction = healing_action


@dataclass(frozen=True)
class healing_cycle(sovereign_base_model_types):
    """
    Healing cycle record with Builder pattern support.

    Sovereign Builder Pattern (Phase 12):
    - Fluent self-correction journey construction
    - Automatic success calculation from scores
    - Metric derivation from action list
    - observability for sovereignty restoration
    """

    cycle_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    trigger_score: float
    target_score: float
    actions: list[HealingAction] = field(default_factory=list)
    success: bool
    duration_seconds: float = 0.0
    healed_violations: int = 0
    persistent_violations: int = 0

    class Builder:
        """
        Sovereign Builder for HealingCycle – Phase 12 (Dec 26, 2025)
        Enforces:
        - Fluent construction of self-correction journeys
        - Automatic derivation of success metrics and counts
        - Score-based sovereignty validation
        - observability logging upon completion
        """

        def __init__(self):
            self._cycle_id: str | None = None
            self._trigger_score: float | None = None
            self._target_score: float | None = None
            self._actions: list[HealingAction] = []
            self._success: bool | None = None
            self._duration_seconds: float = 0.0

        def with_cycle_id(self, cycle_id: str) -> HealingCycle.Builder:
            self._cycle_id = cycle_id
            return self

        def triggered_by_score(self, score: float) -> HealingCycle.Builder:
            self._trigger_score = score
            return self

        def achieved_score(self, score: float) -> HealingCycle.Builder:
            """Sets final score and auto-calculates success status."""
            self._target_score = score
            if self._trigger_score is not None:
                self._success = score > self._trigger_score and score >= 95.0
            return self

        def add_action(self, action: HealingAction) -> HealingCycle.Builder:
            self._actions.append(action)
            return self

        def with_duration(self, seconds: float) -> HealingCycle.Builder:
            self._duration_seconds = seconds
            return self

        def build(self) -> HealingCycle:
            """Construct immutable HealingCycle with sovereign validation."""
            if self._trigger_score is None or self._target_score is None:
                raise ValueError("Healing Integrity Error: Both trigger and target scores are required.")
            if not self._cycle_id:
                self._cycle_id = f"healcycle-{uuid.uuid4().hex[:8]}"
            healed = sum(1 for a in self._actions if a.success)
            persistent = len(self._actions) - healed
            status = "SOVEREIGN" if self._success else "PARTIAL"
            logger.info(
                f"[AUDIT] Healing Cycle Concluded: {self._cycle_id} | Outcome: {status} | Delta: {self._trigger_score:.1f}% -> {self._target_score:.1f}% | Restored: {healed}/{len(self._actions)}",
            )
            return HealingCycle(
                cycle_id=self._cycle_id,
                trigger_score=self._trigger_score,
                target_score=self._target_score,
                actions=self._actions.copy(),
                success=self._success if self._success is not None else False,
                duration_seconds=self._duration_seconds,
                healed_violations=healed,
                persistent_violations=persistent,
            )


HealingCycle = healing_cycle


@dataclass(frozen=True)
class healing_report(sovereign_base_model_types):
    """
    Healing report for DDD compliance audits with Builder pattern support.

    Sovereign Builder Pattern (Phase 12):
    - Automatic ID generation if not provided
    - Strategy deduplication tracking
    - Constitutional invariants (fixed <= found)
    - Success threshold enforcement (>= 95%)
    """

    report_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    auditor_version: str
    target_scope: str
    violations_found: int
    violations_fixed: int
    healing_actions: list[dict[str, Any]] = field(default_factory=list)
    pre_healing_score: float
    post_healing_score: float
    success: bool
    healing_strategies_used: list[str] = field(default_factory=list)

    class Builder:
        """
        Sovereign Builder for HealingReport – Phase 12 (Dec 26, 2025)
        Enforces:
        - Fluent, immutable report construction
        - Automatic ID generation and strategy deduplication
        - Constitutional invariants (fixed <= found)
        - observability integration
        """

        def __init__(self):
            self._report_id: str | None = None
            self._auditor_version: str = "v3.0"
            self._target_scope: str = AGENTIC_CORE_DIR
            self._violations_found: int = 0
            self._violations_fixed: int = 0
            self._healing_actions: list[dict[str, Any]] = []
            self._pre_healing_score: float = 0.0
            self._post_healing_score: float = 0.0
            self._success: bool = False
            self._strategies_used: list[str] = []

        def with_report_id(self, report_id: str) -> HealingReport.Builder:
            self._report_id = report_id
            return self

        def with_violations(self, found: int, fixed: int) -> HealingReport.Builder:
            """Enforces the invariant that fixed violations cannot exceed found ones."""
            if fixed > found:
                raise ValueError("Sovereignty Violation: violations_fixed cannot exceed violations_found")
            self._violations_found = found
            self._violations_fixed = fixed
            return self

        def add_healing_action(self, action: dict[str, Any]) -> HealingReport.Builder:
            """Adds an action and automatically tracks the strategy used."""
            self._healing_actions.append(action)
            strategy = action.get("strategy", "unknown")
            if strategy not in self._strategies_used:
                self._strategies_used.append(strategy)
            return self

        def with_scores(self, pre: float, post: float) -> HealingReport.Builder:
            """Sets scores and determines mission success (threshold >= 95%)."""
            self._pre_healing_score = pre
            self._post_healing_score = post
            self._success = post >= 95.0
            return self

        def build(self) -> HealingReport:
            """Construct immutable HealingReport with final constitutional validation."""
            if not self._report_id:
                self._report_id = f"heal-{uuid.uuid4().hex[:8]}"
            logger.info(
                f"[AUDIT] HealingReport Sealed: {self._report_id} | Outcome: {('SUCCESS' if self._success else 'PARTIAL')} | Remediation: {self._violations_fixed}/{self._violations_found}",
            )
            return HealingReport(
                report_id=self._report_id,
                auditor_version=self._auditor_version,
                target_scope=self._target_scope,
                violations_found=self._violations_found,
                violations_fixed=self._violations_fixed,
                healing_actions=self._healing_actions.copy(),
                pre_healing_score=self._pre_healing_score,
                post_healing_score=self._post_healing_score,
                success=self._success,
                healing_strategies_used=self._strategies_used.copy(),
            )


HealingReport = healing_report


@dataclass(frozen=True)
class sovereign_event(sovereign_base_model_types):
    """
    Sovereign event telemetry with Builder pattern support.

    Sovereign Builder Pattern (Phase 12):
    - Fluent telemetry emission
    - Severity-to-log-level mapping
    - Correlation support for audit trails
    - observability integration
    """

    event_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: sovereign_event_type
    severity: sovereign_severity
    source: str
    dimension: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None

    @field_validator("event_type", mode="before")
    @classmethod
    def validate_event_type(cls, v):
        """Validate and convert event_type to SovereignEventType enum."""
        if isinstance(v, str):
            try:
                return SovereignEventType(v)
            except ValueError:
                raise ValueError(f"Sovereignty Violation: '{v}' is not a registered SovereignEventType")
        return v

    @field_validator("severity", mode="before")
    @classmethod
    def validate_severity(cls, v):
        """Validate and convert severity to SovereignSeverity enum."""
        if isinstance(v, str):
            try:
                return sovereign_severity(v)
            except ValueError:
                raise ValueError(f"Sovereignty Violation: '{v}' is not a valid SovereignSeverity")
        return v

    class Builder:
        """
        Sovereign Builder for SovereignEvent – Phase 12 (Dec 26, 2025)
        Enforces:
        - Fluent, immutable telemetry emission
        - Severity-to-observability mapping
        - Correlation support for multi-layer audit trails
        """

        def __init__(self):
            self._event_id: str | None = None
            self._event_type: SovereignEventType | None = None
            self._severity: SovereignSeverity | None = None
            self._source: str | None = None
            self._dimension: str | None = None
            self._payload: dict[str, Any] = {}
            self._correlation_id: str | None = None

        def with_type(self, event_type: Any) -> SovereignEvent.Builder:
            """Supports both Enum and String types with immediate validation."""
            try:
                self._event_type = sovereign_event_type(event_type)
            except ValueError:
                raise ValueError(f"Invalid Event Type: {event_type}. Use SovereignEventType.")
            return self

        def with_severity(self, severity: Any) -> SovereignEvent.Builder:
            """Hardens the event emission with canonical weight."""
            try:
                self._severity = sovereign_severity(severity)
            except ValueError:
                raise ValueError(f"Invalid Severity: {severity}. Choose from {list(SOVEREIGN_SEVERITIES)}")
            return self

        def from_source(self, source: str) -> SovereignEvent.Builder:
            self._source = source
            return self

        def in_dimension(self, dimension: str | None) -> SovereignEvent.Builder:
            self._dimension = dimension
            return self

        def with_payload(self, **kwargs) -> SovereignEvent.Builder:
            self._payload.update(kwargs)
            return self

        def correlated_with(self, correlation_id: str) -> SovereignEvent.Builder:
            self._correlation_id = correlation_id
            return self

        def build(self) -> SovereignEvent:
            """Construct immutable SovereignEvent with L6 log emission."""
            if self._event_type is None:
                raise ValueError("event_type is mandatory for SovereignEvent.")
            if self._severity is None:
                raise ValueError("Constitutional Error: severity is mandatory for all SovereignEvents.")
            if not self._source:
                raise ValueError("Sovereignty Telemetry Error: source is required.")
            if not self._event_id:
                self._event_id = f"event-{uuid.uuid4().hex[:8]}"
            log_level = SEVERITY_LOG_LEVELS[self._severity]
            logger.log(
                log_level,
                f"[SOVEREIGN EVENT] {self._event_id} | {self._severity.value} | {self._event_type.value} | {self._source}",
            )
            return SovereignEvent(
                event_id=self._event_id,
                event_type=self._event_type,
                severity=self._severity,
                source=self._source,
                dimension=self._dimension,
                payload=self._payload.copy(),
                correlation_id=self._correlation_id,
            )


SovereignEvent = sovereign_event


core_contracts_types_registry = {
    "Territory": Territory,
    "AgentMessage": AgentMessage,
    "ReadFileArgs": ReadFileArgs,
    "WriteFileArgs": WriteFileArgs,
    "MoveFileArgs": MoveFileArgs,
    "ListFilesArgs": ListFilesArgs,
    "ExecuteCommandArgs": ExecuteCommandArgs,
    "DeleteFileArgs": DeleteFileArgs,
    "CreateDirectoryArgs": CreateDirectoryArgs,
    "AgentThoughtProcess": AgentThoughtProcess,
    "CodeGenerationResult": CodeGenerationResult,
    "ResearchResult": ResearchResult,
    "ConsensusVerdict": ConsensusVerdict,
    "ModelOpinion": ModelOpinion,
    "AgentPlan": AgentPlan,
    "ToneType": ToneType,
    "StyleProfile": StyleProfile,
    "GenerationConfig": GenerationConfig,
    "micro_stage": micro_stage,
    "HopState": HopState,
    "RetryPolicy": RetryPolicy,
    "MicroCheckpoint": MicroCheckpoint,
    "StageTransition": StageTransition,
    "InjectionType": InjectionType,
    "InjectionScope": InjectionScope,
    "InjectionPattern": InjectionPattern,
}


CORE_CONTRACTS_REGISTRY.update(
    {
        "MissionPriority": MissionPriority,
        "MissionStatus": MissionStatus,
        "MissionPhase": MissionPhase,
        "MissionPlan": MissionPlan,
        "ThinkingStep": ThinkingStep,
        "RevisionStep": RevisionStep,
        "ThoughtChain": ThoughtChain,
        "ConstitutionalViolation": ConstitutionalViolation,
        "HealingAction": HealingAction,
        "HealingCycle": HealingCycle,
        "HealingReport": HealingReport,
        "SovereignSeverity": SovereignSeverity,
        "SovereignEventType": SovereignEventType,
        "SovereignEvent": SovereignEvent,
    },
)
if __name__ != "__main__":
    assert len(CORE_CONTRACTS_REGISTRY) == len(set(CORE_CONTRACTS_REGISTRY.values())), (
        "CRITICAL: Duplicate class definitions detected in CORE_CONTRACTS_REGISTRY"
    )
if __name__ != "__main__":
    assert len(CORE_CONTRACTS_REGISTRY) == len(set(CORE_CONTRACTS_REGISTRY.values())), (
        "CRITICAL: Duplicate class definitions detected in CORE_CONTRACTS_REGISTRY"
    )
if __name__ != "__main__":
    assert len(CORE_CONTRACTS_REGISTRY) == len(set(CORE_CONTRACTS_REGISTRY.values())), (
        "CRITICAL: Duplicate class definitions detected in CORE_CONTRACTS_REGISTRY"
    )
if __name__ != "__main__":
    assert len(CORE_CONTRACTS_REGISTRY) == len(set(CORE_CONTRACTS_REGISTRY.values())), (
        "CRITICAL: Duplicate class definitions detected in CORE_CONTRACTS_REGISTRY"
    )
