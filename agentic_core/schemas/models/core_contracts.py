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
    _reasoning_trace: List[str] = Field(
        ...,
        description="Step-by-step logic leading to the decision. Each step should be clear and atomic."
    )
    _relevant_context_keys: List[str] = Field(...)
    tool_choice: Literal["SEARCH", "CODE", "ANSWER", "DELEGATE", "TERMINATE"] = Field(
        ...,
        description="The action type to take"
    )
    _tool_arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the chosen tool"
    )
    _confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in this decision (0.0 to 1.0)"
    )

    @field_validator('_tool_arguments')
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
    _reasoning: str = Field(..., description="Why this code solves the problem")
    _code: str = Field(..., description="The generated Python code")
    _dependencies: List[str] = Field(
        default_factory=list,
        description="Required pip packages"
    )
    _test_cases: List[str] = Field(
        default_factory=list,
        description="Test cases to verify the code"
    )
    _safety_notes: List[str] = Field(
        default_factory=list,
        description="Potential safety concerns or limitations"
    )

class ResearchResult(BaseModel):
    """Schema for research tasks."""
    _query_understanding: str = Field(..., description="How you interpreted the research question")
    _sources: List[Dict[str, str]] = Field(
        ...,
        description="List of sources with 'url' and 'relevance' keys"
    )
    _key_findings: List[str] = Field(..., description="Main findings from the research")
    _confidence_level: Literal["high", "medium", "low"] = Field(
        ...,
        description="Confidence in the research results"
    )
    _follow_up_questions: List[str] = Field(
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
    _max_retries: int = Field(default=3, ge=0, le=10)
    _retry_delay: float = Field(default=1.0, ge=0.0)
    _exponential_backoff: bool = Field(default=True)
    _retryable_stages: List[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )

class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage."""
    _hop_id: str
    _stage: MicroStage
    _timestamp: float
    _state: HopState
    _data: Dict[str, Any] = Field(default_factory=dict)
    _error: Optional[str] = None

class StageTransition(BaseModel):
    """Record of a stage transition."""
    _from_stage: Optional[MicroStage] = None
    _to_stage: MicroStage
    timestamp: float
    _reason: Optional[str] = None

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
    _hop_types: List[str] = Field(default_factory=list)
    _stages: List[str] = Field(default_factory=list)
    _contexts: Dict[str, Any] = Field(default_factory=dict)

class InjectionPattern(BaseModel):
    """A single prompt injection pattern."""
    _id: str
    _name: str
    _type: InjectionType
    _description: str
    _template: str
    _variables: List[str] = Field(default_factory=list)
    _scope: InjectionScope = Field(default_factory=InjectionScope)
    _priority: int = Field(default=0, ge=0, le=10)
    _enabled: bool = True

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
