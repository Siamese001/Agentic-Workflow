"""
Core models module.

Provides fundamental data models and enums used throughout the agentic system,
including complexity levels, task types, and execution contexts.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid

@dataclass
class ExecutionProfile:
    """Profile for execution configuration"""
    name: str
    description: str = ""
    model: str = "default"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retrieval: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalConfig:
    """Configuration for retrieval operations"""
    top_k: int = 10
    similarity_threshold: float = 0.5
    include_metadata: bool = True
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyPlan:
    """Strategy execution plan"""
    name: str = ""
    description: str = ""
    steps: List[str] = field(default_factory=list)
    schema_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyResult:
    """Result from strategy execution"""
    plan_name: str = ""
    success: bool = True
    branches: List[Any] = field(default_factory=list)
    schema_version: str = "v1"
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0

@dataclass
class DraftingPlan:
    """Drafting execution plan"""
    name: str = ""
    content: str = ""
    schema_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DraftingResult:
    """Result from drafting execution"""
    plan_name: str = ""
    success: bool = True
    sections: List[Any] = field(default_factory=list)
    schema_version: str = "v1"
    content: str = ""
    error: Optional[str] = None

@dataclass
class QAPlan:
    """QA execution plan"""
    name: str = ""
    checks: List[str] = field(default_factory=list)
    schema_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QAResult:
    """Result from QA execution"""
    plan_name: str = ""
    success: bool = True
    findings: List[Any] = field(default_factory=list)
    schema_version: str = "v1"
    issues: List[str] = field(default_factory=list)
    error: Optional[str] = None

@dataclass
class SafetyPlan:
    """Safety execution plan"""
    name: str = ""
    checks: List[str] = field(default_factory=list)
    schema_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SafetyResult:
    """Result from safety execution"""
    plan_name: str = ""
    success: bool = True
    findings: List[Any] = field(default_factory=list)
    schema_version: str = "v1"
    violations: List[str] = field(default_factory=list)
    error: Optional[str] = None

@dataclass
class WorkflowPlanBundle:
    """Bundle of workflow plans"""
    strategy: StrategyPlan = field(default_factory=StrategyPlan)
    rag: RAGPlan = field(default_factory=RAGPlan)
    drafting: DraftingPlan = field(default_factory=DraftingPlan)
    qa: QAPlan = field(default_factory=QAPlan)
    safety: SafetyPlan = field(default_factory=SafetyPlan)
    schema_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGPlan:
    """RAG execution plan"""
    name: str = ""
    query: str = ""
    retriever_config: RetrievalConfig = field(default_factory=RetrievalConfig)
    schema_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RAGResult:
    """Result from RAG execution"""
    plan_name: str = ""
    success: bool = True
    evidence: List[Any] = field(default_factory=list)
    used_hyde: bool = False
    schema_version: str = "v1"
    documents: List[Dict[str, Any]] = field(default_factory=list)
    answer: str = ""
    error: Optional[str] = None

@dataclass
class L2ResultBundle:
    """Bundle of L2 execution results"""
    strategy: StrategyResult = field(default_factory=lambda: StrategyResult(branches=[]))
    rag: RAGResult = field(default_factory=lambda: RAGResult(evidence=[], used_hyde=False))
    drafting: DraftingResult = field(default_factory=lambda: DraftingResult(sections=[]))
    qa: QAResult = field(default_factory=lambda: QAResult(findings=[]))
    safety: SafetyResult = field(default_factory=lambda: SafetyResult(findings=[]))
    schema_version: str = "v1"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplexityLevel(str, Enum):
    """Complexity levels for tasks and operations."""

    SIMPLE = "simple"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    COMPLEX = "complex"
    EXPERT = "expert"

    def __lt__(self, other: ComplexityLevel) -> bool:
        """Allow comparison of complexity levels."""
        order = [
            ComplexityLevel.SIMPLE,
            ComplexityLevel.BASIC,
            ComplexityLevel.INTERMEDIATE,
            ComplexityLevel.ADVANCED,
            ComplexityLevel.COMPLEX,
            ComplexityLevel.EXPERT
        ]
        return order.index(self) < order.index(other)

    def __le__(self, other: ComplexityLevel) -> bool:
        """Allow comparison of complexity levels."""
        return self == other or self < other

    def __gt__(self, other: ComplexityLevel) -> bool:
        """Allow comparison of complexity levels."""
        return not self <= other

    def __ge__(self, other: ComplexityLevel) -> bool:
        """Allow comparison of complexity levels."""
        return not self < other

    @classmethod
    def from_string(cls, value: str) -> ComplexityLevel:
        """Create ComplexityLevel from string, case-insensitive."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.BASIC  # Default fallback

    def get_numeric_value(self) -> int:
        """Get numeric representation for calculations."""
        mapping = {
            ComplexityLevel.SIMPLE: 1,
            ComplexityLevel.BASIC: 2,
            ComplexityLevel.INTERMEDIATE: 3,
            ComplexityLevel.ADVANCED: 4,
            ComplexityLevel.COMPLEX: 5,
            ComplexityLevel.EXPERT: 6
        }
        return mapping[self]


class TaskType(str, Enum):
    """Types of tasks in the agentic system."""

    PLANNING = "planning"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    VALIDATION = "validation"
    COORDINATION = "coordination"
    MONITORING = "monitoring"


class ExecutionStatus(str, Enum):
    """Status of task execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TaskContext:
    """Context information for task execution."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    environment: str = "development"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "environment": self.environment,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ResourceRequirement:
    """Resource requirements for task execution."""

    cpu_cores: float = 1.0
    memory_mb: int = 512
    disk_mb: int = 100
    network_required: bool = False
    gpu_required: bool = False
    max_execution_time_seconds: int = 300

    def validate(self) -> List[str]:
        """Validate resource requirements."""
        errors = []
        if self.cpu_cores <= 0:
            errors.append("CPU cores must be positive")
        if self.memory_mb <= 0:
            errors.append("Memory must be positive")
        if self.disk_mb < 0:
            errors.append("Disk space cannot be negative")
        if self.max_execution_time_seconds <= 0:
            errors.append("Max execution time must be positive")
        return errors


@dataclass
class TaskSpecification:
    """Specification for a task to be executed."""

    name: str
    task_type: TaskType
    complexity_level: ComplexityLevel
    description: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    resource_requirements: ResourceRequirement = field(default_factory=ResourceRequirement)
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    estimated_duration_seconds: Optional[int] = None
    retry_count: int = 3
    timeout_seconds: int = 300

    def validate(self) -> List[str]:
        """Validate task specification."""
        errors = []

        if not self.name or not self.name.strip():
            errors.append("Task name is required")

        if not isinstance(self.task_type, TaskType):
            errors.append("Invalid task type")

        if not isinstance(self.complexity_level, ComplexityLevel):
            errors.append("Invalid complexity level")

        resource_errors = self.resource_requirements.validate()
        errors.extend(resource_errors)

        if self.estimated_duration_seconds is not None and self.estimated_duration_seconds <= 0:
            errors.append("Estimated duration must be positive")

        if self.retry_count < 0:
            errors.append("Retry count cannot be negative")

        if self.timeout_seconds <= 0:
            errors.append("Timeout must be positive")

        return errors

    def get_priority_score(self) -> float:
        """Calculate priority score based on complexity and requirements."""
        complexity_score = self.complexity_level.get_numeric_value()
        resource_score = (
            self.resource_requirements.cpu_cores +
            self.resource_requirements.memory_mb / 1024 +
            (10 if self.resource_requirements.gpu_required else 0)
        )
        return complexity_score + resource_score * 0.1


@dataclass
class ExecutionResult:
    """Result of task execution."""

    task_id: str
    status: ExecutionStatus
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_successful(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.COMPLETED and self.error_message is None

    def get_duration(self) -> Optional[float]:
        """Get actual execution duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return self.execution_time_seconds if self.execution_time_seconds > 0 else None


# Utility functions for model operations
def create_task_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    environment: str = "development"
) -> TaskContext:
    """Create a new task context."""
    return TaskContext(
        user_id=user_id,
        session_id=session_id,
        environment=environment
    )


def estimate_task_resources(
    complexity: ComplexityLevel,
    task_type: TaskType,
    estimated_duration: Optional[int] = None
) -> ResourceRequirement:
    """Estimate resource requirements based on task characteristics."""
    base_resources = {
        ComplexityLevel.SIMPLE: ResourceRequirement(cpu_cores=0.5, memory_mb=256, max_execution_time_seconds=60),
        ComplexityLevel.BASIC: ResourceRequirement(cpu_cores=1.0, memory_mb=512, max_execution_time_seconds=180),
        ComplexityLevel.INTERMEDIATE: ResourceRequirement(cpu_cores=2.0, memory_mb=1024, max_execution_time_seconds=300),
        ComplexityLevel.ADVANCED: ResourceRequirement(cpu_cores=4.0, memory_mb=2048, max_execution_time_seconds=600),
        ComplexityLevel.COMPLEX: ResourceRequirement(cpu_cores=8.0, memory_mb=4096, max_execution_time_seconds=1200),
        ComplexityLevel.EXPERT: ResourceRequirement(cpu_cores=16.0, memory_mb=8192, max_execution_time_seconds=2400)
    }

    resources = base_resources.get(complexity, base_resources[ComplexityLevel.BASIC])

    # Adjust based on task type
    if task_type in [TaskType.GENERATION, TaskType.ANALYSIS]:
        resources.memory_mb = int(resources.memory_mb * 1.5)
        resources.network_required = True

    if estimated_duration:
        resources.max_execution_time_seconds = max(estimated_duration * 2, resources.max_execution_time_seconds)

    return resources


def get_complexity_from_description(description: str) -> ComplexityLevel:
    """Estimate complexity level from task description."""
    description_lower = description.lower()

    if any(word in description_lower for word in ["simple", "basic", "quick", "easy"]):
        return ComplexityLevel.SIMPLE
    elif any(word in description_lower for word in ["complex", "advanced", "detailed", "comprehensive"]):
        return ComplexityLevel.COMPLEX
    elif any(word in description_lower for word in ["expert", "highly complex", "sophisticated"]):
        return ComplexityLevel.EXPERT
    elif any(word in description_lower for word in ["intermediate", "moderate"]):
        return ComplexityLevel.INTERMEDIATE
    elif any(word in description_lower for word in ["advanced", "challenging"]):
        return ComplexityLevel.ADVANCED
    else:
        return ComplexityLevel.BASIC


__all__ = [
    "ComplexityLevel",
    "TaskType",
    "ExecutionStatus",
    "TaskContext",
    "ResourceRequirement",
    "TaskSpecification",
    "ExecutionResult",
    "create_task_context",
    "estimate_task_resources",
    "get_complexity_from_description"
]





