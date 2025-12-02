"""
Schema definitions for schema operation performance and execution.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class OperationType(Enum):
    """Schema operation types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    TRANSFORM = "transform"


class ExecutionStrategy(Enum):
    """Operation execution strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINED = "pipelined"
    OPTIMIZED = "optimized"


@dataclass
class SchemaOperation:
    """Schema for individual schema operation."""
    operation_id: str
    operation_type: OperationType
    target_schema_id: str
    operation_data: Dict[str, Any]
    execution_strategy: ExecutionStrategy


@dataclass
class OperationExecutionContext:
    """Schema for operation execution context."""
    context_id: str
    operations: List[SchemaOperation]
    execution_environment: Dict[str, Any]
    resource_requirements: Dict[str, int]


@dataclass
class OperationExecutionResult:
    """Schema for operation execution results."""
    result_id: str
    context: OperationExecutionContext
    successful_operations: List[str]
    failed_operations: List[str]
    execution_statistics: Dict[str, Any]