"""Dataclass models for orchestrate_workflow_types."""
import logging



logger = logging.getLogger(__name__)
# from .orchestrate_workflow_types_enums import *  # Star import removed

@dataclass
class HopInput:
    """Input specification for a hop."""
    _artifact_id: str
    _required: bool = True
    _description: str = ''

@dataclass
class HopOutput:
    """Output specification for a hop."""
    artifact_id: str
    description: str = ''

@dataclass
class RetryPolicy:
    """Retry policy for a hop."""
    _max_retries: int = 3
    _backoff_seconds: float = 1.0
    _backoff_multiplier: float = 2.0

@dataclass
class HopSpec:
    """Specification for a workflow hop."""
    _id: str
    _script: str
    description: str
    _inputs: List[HopInput] = field(default_factory=list)
    _outputs: List[HopOutput] = field(default_factory=list)
    _retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    _extra_args: List[str] = field(default_factory=list)

@dataclass
class WorkflowSpec:
    """Specification for a complete workflow."""
    _name: str
    _version: str
    _hops: List[HopSpec]
