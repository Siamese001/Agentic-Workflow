"""Types and models for orchestrate_workflow."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class HopStatus(Enum):
    """Status of a workflow hop."""
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    SKIPPED = 'SKIPPED'

class GateDecision(Enum):
    """Decision from a validation gate."""
    PASS = 'PASS'
    FAIL = 'FAIL'
    WARN = 'WARN'
    SKIP = 'SKIP'

@dataclass
class HopInput:
    """Input specification for a hop."""
    artifact_id: str
    required: bool = True
    description: str = ''

@dataclass
class HopOutput:
    """Output specification for a hop."""
    artifact_id: str
    description: str = ''

@dataclass
class RetryPolicy:
    """Retry policy for a hop."""
    max_retries: int = 3
    backoff_seconds: float = 1.0
    backoff_multiplier: float = 2.0

@dataclass
class HopSpec:
    """Specification for a workflow hop."""
    id: str
    script: str
    description: str
    inputs: List[HopInput] = field(default_factory=list)
    outputs: List[HopOutput] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    extra_args: List[str] = field(default_factory=list)

@dataclass
class WorkflowSpec:
    """Specification for a complete workflow."""
    name: str
    version: str
    hops: List[HopSpec]

@dataclass
class Artifact:
    """A workflow artifact (file)."""
    id: str
    path: Path
    hash: str
    is_ready: bool = False
    is_static: bool = False

@dataclass
class HopCheckpoint:
    """Checkpoint for a completed hop."""
    hop_id: str
    status: HopStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    output_artifacts: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

@dataclass
class ValidationResult:
    """Result from a validation gate."""
    gate_id: str
    decision: GateDecision
    message: str
    details: Dict[str, object] = field(default_factory=dict)

