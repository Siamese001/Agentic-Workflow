"""
Sovereign Core Contracts – Absolute SSOT for all Pydantic models and data schemas
No inline BaseModel definitions allowed outside schemas/.
"""
from pathlib import Path
from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, validator, field_validator

class SovereignBaseModel(BaseModel):
    """Base model for all Sovereign entities with strict config."""
    model_config = ConfigDict(strict=True, frozen=True)

class Territory(SovereignBaseModel):
    name: str
    depth: int
    path: str
    canon_key: Optional[int] = None

class AgentMessage(SovereignBaseModel):
    source: str
    destination: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ReadFileArgs(BaseModel):
    """Arguments for reading a file."""
    path: str = Field(..., description="Relative path to the file to read")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

class WriteFileArgs(BaseModel):
    """Arguments for writing to a file."""
    path: str = Field(..., description="Relative path to the file to write")
    content: str = Field(..., description="Content to write to the file")
    create_dirs: bool = Field(default=True, description="Create parent directories if they don't exist")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

class MoveFileArgs(BaseModel):
    """Arguments for moving/renaming a file."""
    source: str = Field(..., description="Relative path to the source file")
    destination: str = Field(..., description="Relative path to the destination")
    overwrite: bool = Field(default=False, description="Overwrite destination if it exists")
    
    @validator('source', 'destination')
    def validate_paths(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Paths must be relative to project root")
        return v

class ListFilesArgs(BaseModel):
    """Arguments for listing files in a directory."""
    path: str = Field(default=".", description="Relative path to the directory to list")
    pattern: Optional[str] = Field(default=None, description="Glob pattern to filter files (e.g., '*.py')")
    recursive: bool = Field(default=False, description="Recursively list subdirectories")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

class ExecuteCommandArgs(BaseModel):
    """Arguments for executing a shell command."""
    command: str = Field(..., description="Command to execute")
    args: List[str] = Field(default_factory=list, description="Command arguments")
    cwd: Optional[str] = Field(default=None, description="Working directory (relative to project root)")
    timeout: int = Field(default=30, description="Timeout in seconds (max 300)")
    capture_output: bool = Field(default=True, description="Capture stdout and stderr")
    
    @validator('timeout')
    def validate_timeout(cls, v):
        if v > 300:
            raise ValueError("Timeout cannot exceed 300 seconds to prevent livelocks")
        if v < 1:
            raise ValueError("Timeout must be at least 1 second")
        return v
    
    @validator('cwd')
    def validate_cwd(cls, v):
        if v and Path(v).is_absolute():
            raise ValueError("Working directory must be relative to project root")
        return v

class DeleteFileArgs(BaseModel):
    """Arguments for deleting a file."""
    path: str = Field(..., description="Relative path to the file to delete")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

class CreateDirectoryArgs(BaseModel):
    """Arguments for creating a directory."""
    path: str = Field(..., description="Relative path to the directory to create")
    parents: bool = Field(default=True, description="Create parent directories if they don't exist")
    
    @validator('path')
    def validate_path(cls, v):
        if Path(v).is_absolute():
            raise ValueError("Path must be relative to project root")
        return v

class AgentThoughtProcess(BaseModel):
    """
    Forces the agent to show its work before acting.
    This is the "Physics" of your Agent - the schema it must follow.
    """
    reasoning_trace: List[str] = Field(
        ...,
        description="Step-by-step logic leading to the decision. Each step should be clear and atomic."
    )
    relevant_context_keys: List[str] = Field(...)
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ...,
        description="The action type to take"
    )
    tool_arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the chosen tool"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this decision (0.0 to 1.0)"
    )

    @field_validator('tool_arguments')
    @classmethod
    def validate_args(cls, v, info):
        """Self-validation inside the schema."""
        tool_choice = info.data.get('tool_choice')

        if tool_choice == 'CODE' and 'code' not in v:
            raise ValueError("Tool choice CODE requires a 'code' argument.")

        if tool_choice == 'SEARCH' and 'query' not in v:
            raise ValueError("Tool choice SEARCH requires a 'query' argument.")

        if tool_choice == 'DELEGATE' and 'subtask' not in v:
            raise ValueError("Tool choice DELEGATE requires a 'subtask' argument.")

        return v

class CodeGenerationResult(BaseModel):
    """Schema for code generation tasks."""
    reasoning: str = Field(..., description="Why this code solves the problem")
    code: str = Field(..., description="The generated Python code")
    dependencies: List[str] = Field(
        default_factory=list,
        description="Required pip packages"
    )
    test_cases: List[str] = Field(
        default_factory=list,
        description="Test cases to verify the code"
    )
    safety_notes: List[str] = Field(
        default_factory=list,
        description="Potential safety concerns or limitations"
    )

class ResearchResult(BaseModel):
    """Schema for research tasks."""
    query_understanding: str = Field(..., description="How you interpreted the research question")
    sources: List[Dict[str, str]] = Field(
        ...,
        description="List of sources with 'url' and 'relevance' keys"
    )
    key_findings: List[str] = Field(..., description="Main findings from the research")
    confidence_level: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence in the research results"
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="Suggested follow-up research questions"
    )

class ConsensusVerdict(BaseModel):
    """Result of a consensus deliberation."""
    chosen_plan: str
    consensus_score: float  # 0.0 to 1.0
    dissenting_opinions: List[str] = Field(default_factory=list)
    reasoning: str
    safe_to_proceed: bool

class ModelOpinion(BaseModel):
    """Individual model's opinion on a plan."""
    model_name: str
    plan: str
    reasoning: str
    risk_assessment: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float  # 0.0 to 1.0

class AgentPlan(BaseModel):
    """Agent execution plan with reasoning and tool calls."""
    reasoning: str
    tool_calls: list[dict]

class ToneType(str, Enum):
    """Primary tone types for communication style analysis."""
    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    ENTHUSIASTIC = "enthusiastic"
    DIRECT = "direct"

class StyleProfile(BaseModel):
    """Profile defining a communication style."""
    primary_tone: ToneType = Field(..., description="Primary tone type")
    formality_level: float = Field(default=0.7, ge=0.0, le=1.0, description="Formality level (0=Casual, 1=Academic)")
    emoji_frequency: float = Field(default=0.2, ge=0.0, le=1.0, description="Emoji usage frequency")
    sentence_length_avg: int = Field(default=15, ge=5, le=50, description="Target words per sentence")
    vocabulary_complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Vocabulary complexity")
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in analysis")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True

class GenerationConfig(BaseModel):
    """Configuration for LLM generation based on tone profile."""
    system_prompt_fragment: str = Field(..., description="Instruction to inject into prompts")
    temperature_setting: float = Field(..., ge=0.1, le=1.0, description="LLM temperature")
    banned_phrases: List[str] = Field(default_factory=list, description="Phrases to avoid")
    preferred_transitions: List[str] = Field(default_factory=list, description="Preferred transition words")
    max_sentence_length: int = Field(default=25, ge=5, le=100, description="Max words per sentence")

    @validator('temperature_setting')
    def clamp_temperature(cls, v):
        """Ensure temperature is within valid range."""
        return max(0.1, min(1.0, v))

class MicroStage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""
    INIT = "init"
    THINK = "think"
    ACT = "act"
    CRITIQUE = "critique"
    COMMIT = "commit"

class HopState(Enum):
    """Overall state of a Subatomic Hop."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

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

class InjectionType(Enum):
    """Types of prompt injections."""
    SYSTEM = "system"
    USER = "user"
    CONTEXT = "context"
    REASONING = "reasoning"
    TOOLING = "tooling"
    SAFETY = "safety"
    OUTPUT = "output"

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

CORE_CONTRACTS_REGISTRY = {
    # Base Models
    "Territory": Territory,
    "AgentMessage": AgentMessage,
    # Tool Registry
    "ReadFileArgs": ReadFileArgs,
    "WriteFileArgs": WriteFileArgs,
    "MoveFileArgs": MoveFileArgs,
    "ListFilesArgs": ListFilesArgs,
    "ExecuteCommandArgs": ExecuteCommandArgs,
    "DeleteFileArgs": DeleteFileArgs,
    "CreateDirectoryArgs": CreateDirectoryArgs,
    # Structured Engine
    "AgentThoughtProcess": AgentThoughtProcess,
    "CodeGenerationResult": CodeGenerationResult,
    "ResearchResult": ResearchResult,
    # Consensus
    "ConsensusVerdict": ConsensusVerdict,
    "ModelOpinion": ModelOpinion,
    # Agent Execution
    "AgentPlan": AgentPlan,
    # Tone Model
    "ToneType": ToneType,
    "StyleProfile": StyleProfile,
    "GenerationConfig": GenerationConfig,
    # Runtime Shared
    "MicroStage": MicroStage,
    "HopState": HopState,
    "RetryPolicy": RetryPolicy,
    "MicroCheckpoint": MicroCheckpoint,
    "StageTransition": StageTransition,
    "InjectionType": InjectionType,
    "InjectionScope": InjectionScope,
    "InjectionPattern": InjectionPattern,
}

# === Legacy P1 Core Profiles – Phase 2B Migration (Dec 2025) ===

from dataclasses import dataclass, field
from datetime import datetime
import uuid

# Context Passport Models

class ThermalProfile(str, Enum):
    """Predefined thermal configurations for different node types."""
    CREATIVITY_MAX = "creativity_max"
    CREATIVITY_HIGH = "creativity_high"
    BALANCED = "balanced"
    STRUCTURED = "structured"
    PRECISION = "precision"

@dataclass(frozen=True)
class HardState:
    """
    Immutable, DAG-owned state that the LLM cannot edit directly.
    
    This contains critical execution metadata, security_scopes, and structural
    information that must remain stable throughout the workflow.
    """
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    node_id: Optional[str] = None
    security_scopes: set = field(default_factory=set)
    file_paths: Dict[str, str] = field(default_factory=dict)
    schemas: Dict[str, str] = field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_trace(self, event: str, data: Dict[str, Any]) -> 'HardState':
        """Add an event to the execution trace (returns new instance)."""
        new_trace = self.execution_trace + [{
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }]
        return HardState(
            execution_id=self.execution_id,
            workflow_id=self.workflow_id,
            node_id=self.node_id,
            security_scopes=self.security_scopes,
            file_paths=self.file_paths,
            schemas=self.schemas,
            execution_trace=new_trace,
            created_at=self.created_at
        )

@dataclass
class SoftState:
    """
    Mutable, LLM-owned scratchpad for high-temperature creativity.
    
    This is where the LLM can draft, speculate, and iterate without risking
    system stability. Content here must be validated before promotion to HardState.
    """
    drafts: Dict[str, Any] = field(default_factory=dict)
    scratchpad: List[str] = field(default_factory=list)
    creative_variants: List[Dict[str, Any]] = field(default_factory=list)
    speculative_content: Dict[str, Any] = field(default_factory=dict)
    revision_history: List[Dict[str, Any]] = field(default_factory=list)

    def add_draft(self, key: str, content: Any) -> None:
        """Add content to the drafts."""
        self.drafts[key] = content

    def add_scratch_note(self, note: str) -> None:
        """Add a note to the scratchpad."""
        self.scratchpad.append(note)

    def record_revision(self, key: str, old_value: Any, new_value: Any) -> None:
        """Record a revision in the history."""
        self.revision_history.append({
            "key": key,
            "old_value": old_value,
            "new_value": new_value,
            "timestamp": datetime.utcnow().isoformat()
        })

@dataclass
class ThermalConfig:
    """Dynamic thermal configuration for LLM parameters."""
    profile: ThermalProfile = ThermalProfile.BALANCED
    temperature: float = 0.7
    top_p: float = 0.85
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_tokens: Optional[int] = None
    node_overrides: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def get_params_for_node(self, node_id: str) -> Dict[str, float]:
        """Get thermal parameters for a specific node."""
        if node_id in self.node_overrides:
            return {
                "temperature": self.node_overrides[node_id].get("temperature", self.temperature),
                "top_p": self.node_overrides[node_id].get("top_p", self.top_p),
                "frequency_penalty": self.node_overrides[node_id].get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": self.node_overrides[node_id].get("presence_penalty", self.presence_penalty)
            }
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }

    def set_node_profile(self, node_id: str, profile: ThermalProfile) -> None:
        """Set a thermal profile for a specific node."""
        profile_configs = {
            ThermalProfile.CREATIVITY_MAX: {"temperature": 0.9, "top_p": 0.95},
            ThermalProfile.CREATIVITY_HIGH: {"temperature": 0.8, "top_p": 0.90},
            ThermalProfile.BALANCED: {"temperature": 0.7, "top_p": 0.85},
            ThermalProfile.STRUCTURED: {"temperature": 0.3, "top_p": 0.70},
            ThermalProfile.PRECISION: {"temperature": 0.1, "top_p": 0.50}
        }
        self.node_overrides[node_id] = profile_configs[profile]

@dataclass
class SignedClaim:
    """A factual claim with source attribution and confidence score."""
    claim: str
    source: str
    confidence: float
    evidence: Optional[str] = None
    verified_at: Optional[datetime] = None

    def __post_init__(self):
        if self.verified_at is None:
            self.verified_at = datetime.utcnow()

class SignalContext(BaseModel):
    """
    The Thermostatic Context Passport that enables high-temperature creativity
    while maintaining structural integrity through dual-state isolation.
    """
    hard_state: HardState = Field(default_factory=HardState)
    soft_state: SoftState = Field(default_factory=SoftState)
    thermal_config: ThermalConfig = Field(default_factory=ThermalConfig)
    signed_claims: List[SignedClaim] = Field(default_factory=list)
    context_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.last_modified = datetime.utcnow()

    def add_signed_claim(self, claim: str, source: str, confidence: float, evidence: Optional[str] = None) -> None:
        """Add a signed claim to the context."""
        signed_claim = SignedClaim(claim=claim, source=source, confidence=confidence, evidence=evidence)
        self.signed_claims.append(signed_claim)

# Safety Profile

class SafetyProfile(BaseModel):
    """Safety configuration profile used by execution profiles."""
    safety_tier: str = Field(default="standard", description="Safety tier: standard | strict | relaxed | debug")
    pii_detection_enabled: bool = True
    policy_engine_enabled: bool = True

# Simulation Models

class SimScenario(BaseModel):
    """Simulation scenario definition."""
    id: str
    description: str
    initial_context: Dict[str, Any]
    execution_profile_name: str
    run_count: int

class SimOutcome(BaseModel):
    """Simulation outcome results."""
    scenario_id: str
    average_scores: Dict[str, float]
    safety_incidents: int
    agent_conflict_count: int

# Metacognition Models

class Hypothesis(BaseModel):
    """Lightweight hypothesis used by the metacognition layer."""
    id: str
    agent_id: str
    content: str
    confidence: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)
    rationale: Optional[str] = None

class MetacognitionReport(BaseModel):
    """Aggregate view over a set of hypotheses and signals."""
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    global_confidence: float = 0.0
    uncertainty_score: float = 0.0
    issues_detected: List[str] = Field(default_factory=list)

# Golden State Models

@dataclass
class GoldenStateTestCase:
    """Single golden-state test case."""
    id: str
    input_text: str
    expected_behavior: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JudgeVerdict:
    """LM-as-a-judge style verdict."""
    score: float
    rating: str
    explanation: str

@dataclass
class EvalResult:
    """Result of running a golden test case through the system."""
    test_id: str
    verdict: JudgeVerdict
    raw_output: str
    reasoning_trace: List[Dict[str, Any]] = field(default_factory=list)

class GoldenCase(BaseModel):
    """Golden test case for evaluation."""
    id: str
    input_text: str
    agent_sequence: List[str]
    expected_keypoints: List[str]
    correctness_criteria: Dict[str, Any]

class GoldenOutput(BaseModel):
    """Golden test output results."""
    case_id: str
    produced_keypoints: List[str]
    correctness_map: Dict[str, bool]
    safety_decisions: Dict[str, Any]
    metacognition_summary: Dict[str, Any]
    final_verdict: Literal["pass", "fail", "borderline"]

# Budget Profile

class BudgetProfile(BaseModel):
    """High-level budget profile for cost/latency envelopes."""
    max_cost_usd: float = Field(default=0.10, ge=0.0)
    max_latency_ms: int = Field(default=3000, ge=0)

# Update Registry
CORE_CONTRACTS_REGISTRY.update({
    # Context Passport
    "ThermalProfile": ThermalProfile,
    "HardState": HardState,
    "SoftState": SoftState,
    "ThermalConfig": ThermalConfig,
    "SignedClaim": SignedClaim,
    "SignalContext": SignalContext,
    # Profiles
    "SafetyProfile": SafetyProfile,
    "BudgetProfile": BudgetProfile,
    # Simulation
    "SimScenario": SimScenario,
    "SimOutcome": SimOutcome,
    # Metacognition
    "Hypothesis": Hypothesis,
    "MetacognitionReport": MetacognitionReport,
    # Golden State
    "GoldenStateTestCase": GoldenStateTestCase,
    "JudgeVerdict": JudgeVerdict,
    "EvalResult": EvalResult,
    "GoldenCase": GoldenCase,
    "GoldenOutput": GoldenOutput,
})

# === Phase 2C Residual Sweep – Dec 26, 2025 ===
# Models discovered in non-schema directories during final sweep

# Runtime Shared Models

@dataclass
class LLMResponse:
    """Standard LLM response format."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageType(str, Enum):
    """Message types for agent communication."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class ResidualAgentMessage:  # CONFLICT: Renamed to avoid collision with existing AgentMessage
    """Message in agent conversation (from runtime_shared_models.py)."""
    role: MessageType
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentResponse:
    """Response from agent execution."""
    message: 'ResidualAgentMessage'
    success: bool
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Optional[Dict[str, Any]] = None

class ResidualValidationResult(BaseModel):  # CONFLICT: Renamed to avoid collision
    """Validation result for data or operations (from runtime_shared_models.py)."""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}

class ReasoningConfig(BaseModel):
    """Configuration for reasoning operations."""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[List[str]] = None

class HopStatus(str, Enum):
    """Status of hop execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GateDecision(str, Enum):
    """Decision from validation gate."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"

class ValidationSeverity(str, Enum):
    """Severity of validation issue."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class WorkflowCheckpoint:
    """Checkpoint in workflow execution."""
    hop_id: str
    status: HopStatus
    data: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ThematicAnalysis:
    """Analysis of thematic content."""
    theme: str
    confidence: float
    keywords: List[str]
    sentiment: Optional[str] = None

@dataclass
class RAGState:
    """State of RAG operations."""
    query: str
    retrieved_docs: List[Dict[str, Any]]
    context: str
    response: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CircuitState(str, Enum):
    """Circuit breaker state."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# Update Registry
CORE_CONTRACTS_REGISTRY.update({
    # Runtime Shared Models
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
})
