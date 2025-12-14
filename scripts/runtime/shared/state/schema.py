"""State schema definitions for atomic workflow persistence.


logger = logging.getLogger(__name__)
Defines the structure of workflow state and checkpoint metadata using Pydantic
for validation and serialization.

Phase 3 - Atomic State Persistence
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

class BackendType(str, Enum):
    """Storage backend types for state persistence."""
    FILE = "file"
    REDIS = "redis"
    SQLITE = "sqlite"

class CheckpointMetadata(BaseModel):
    """Metadata about a checkpoint operation."""
    checkpoint_id: str
    workflow_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    k_node_index: int
    k_node_name: str
    success: bool
    error_message: Optional[str] = None
    duration_ms: float = 0.0

class KNodeExecution(BaseModel):
    """Execution record for a single K-Node."""

    k_node_index: int
    k_node_name: str
    input_prompt: str
    output: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowState(BaseModel):
    """Complete workflow state for atomic persistence.

    This represents the entire state of a workflow execution that can be
    checkpointed and resumed. All fields are designed to be JSON-serializable.

    Attributes:
        workflow_id: Unique identifier for this workflow instance
        workflow_type: Type of workflow (e.g., "resume_generation", "outreach")
        current_k_node: Index of the currently executing K-Node
        total_k_nodes: Total number of K-Nodes in the workflow
        execution_log: History of all K-Node executions
        last_successful_output: Output from the most recent successful K-Node
        accumulated_context: Context accumulated across K-Nodes
        started_at: Workflow start timestamp
        last_checkpoint_at: Most recent checkpoint timestamp
        status: Current workflow status
        metadata: Additional workflow-specific metadata
    """

    workflow_id: str
    workflow_type: str
    current_k_node: int = 0
    total_k_nodes: int
    execution_log: List[KNodeExecution] = Field(default_factory=list)
    last_successful_output: Optional[str] = None
    accumulated_context: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_checkpoint_at: Optional[datetime] = None
    status: str = "running"  # running, completed, failed, paused
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
            """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

        """Docstring."""
    def add_execution(
        self,
        k_node_index: int,
        k_node_name: str,
        input_prompt: str,
        output: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
            """Add a K-Node execution to the log.

        Args:
            k_node_index: Index of the K-Node
            k_node_name: Name of the K-Node
            input_prompt: Input prompt for the K-Node
            output: Output from the K-Node
            duration_ms: Execution duration in milliseconds
            success: Whether execution succeeded
            error: Error message if failed
            metadata: Additional execution metadata
        """
        execution = KNodeExecution(
            k_node_index=k_node_index,
            k_node_name=k_node_name,
            input_prompt=input_prompt,
            output=output,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata=metadata or {},
        )
        self.execution_log.append(execution)

        if success:
            self.last_successful_output = output
            self.current_k_node = k_node_index + 1

    def get_last_execution(self) -> Optional[KNodeExecution]:
            """Get the most recent K-Node execution."""
        if self.execution_log:
            return self.execution_log[-1]
        return None

    def get_successful_executions(self) -> List[KNodeExecution]:
            """Get all successful K-Node executions."""
        return [exec for exec in self.execution_log if exec.success]

    def is_complete(self) -> bool:
            """Check if workflow has completed all K-Nodes."""
        return self.current_k_node >= self.total_k_nodes

    def get_progress_percentage(self) -> float:
            """Get workflow completion percentage."""
        if self.total_k_nodes == 0:
            return 0.0
        return (self.current_k_node / self.total_k_nodes) * 100.0

    def to_dict(self) -> Dict[str, Any]:
            """Convert to dictionary for serialization."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
            """Create WorkflowState from dictionary."""
        return cls(**data)

    def to_json(self) -> str:
            """Convert to JSON string."""
        return self.json()

    @classmethod
    def from_json(cls, json_str: str) -> "WorkflowState":
            """Create WorkflowState from JSON string."""
        return cls.parse_raw(json_str)
