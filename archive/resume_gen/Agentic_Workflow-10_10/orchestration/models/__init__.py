"""
Orchestration layer data models.

This module provides data models specific to orchestration operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Import DAG models from core.models for backward compatibility
from core.models.dag_models import *


class OrchestrationStatus(str, Enum):
    """Status of orchestration operations."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OrchestrationContext:
    """Context for orchestration operations."""
    workflow_id: str
    execution_id: str
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NodeExecution:
    """Represents execution of a single node in the orchestration graph."""
    node_id: str
    workflow_id: str
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class WorkflowExecution:
    """Represents execution of an entire workflow."""
    workflow_id: str
    execution_id: str
    nodes: List[NodeExecution] = field(default_factory=list)
    status: OrchestrationStatus = OrchestrationStatus.PENDING
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    context: OrchestrationContext = field(default_factory=OrchestrationContext)
