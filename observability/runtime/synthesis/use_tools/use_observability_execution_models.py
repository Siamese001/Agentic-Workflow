"""Dataclass models for use_observability_execution."""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)
# from .use_observability_execution_enums import *  # Star import removed

@dataclass
class ExecutionRequest:
    """Request for observability execution."""
    request_id: str
    operation_type: str
    parameters: Dict[str, Any]
    strategy: ExecutionStrategy = ExecutionStrategy.IMMEDIATE
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    timeout: float = 30.0
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionEnvironment:
    """Environment for execution."""
    env_id: str
    resources: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, str] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)

@dataclass
class ExecutionConfig:
    """Configuration for execution."""
    default_timeout: float = 30.0
    max_concurrent_executions: int = 10
    enable_queueing: bool = True
    queue_size: int = 100
    enable_retry: bool = True
    max_retries: int = 3
    enable_metrics: bool = True

@dataclass
class ExecutionResult:
    """Result of execution."""
    request_id: str
    operation_type: str
    success: bool
    output: Optional[Any] = None
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    resource_usage: Dict[str, float] = field(default_factory=dict)
