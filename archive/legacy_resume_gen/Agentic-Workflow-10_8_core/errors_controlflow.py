"""
Error definitions for control-flow orchestration structures.
"""


class ControlFlowError(Exception):
    """Base error for control-flow orchestration."""


class DAGValidationError(ControlFlowError):
    """Raised when a DAG definition is invalid or cyclic."""


class NodeExecutionError(ControlFlowError):
    """Raised when a DAG node encounters an execution failure."""
