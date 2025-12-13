"""Dataclass models for orchestrate_workflow_types."""

from dataclasses import dataclass, field
# from .orchestrate_workflow_types_enums import *  # Star import removed

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
