#!/usr/bin/env python3
"""
DAG Types
Section 4: DAG Orchestration - Shared types and enums for DAG components
"""

from enum import Enum

class NodeStatus(str, Enum):
    """DAG node execution status"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class ExecutionState(str, Enum):
    """DAG execution state"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DependencyType(str, Enum):
    """Dependency type enumeration"""
    DATA = "data"
    CONTROL = "control"
    TEMPORAL = "temporal"
    RESOURCE = "resource"

class NodeType(str, Enum):
    """Node type enumeration"""
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    SUB_DAG = "sub_dag"
    CONDITION = "condition"

# Re-export types
__all__ = [
    'NodeStatus', 'ExecutionState', 'DependencyType', 'NodeType'
]





