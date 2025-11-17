# exceptions.py
"""
Shared Exceptions — v10_9
"""

class RuntimeConfigurationError(Exception): pass
class PlanningError(Exception): pass
class ReasoningError(Exception): pass

class ModelClientError(Exception): pass
class ToolExecutionError(Exception): pass
class ToolTimeoutError(Exception): pass

class OrchestrationError(Exception): pass
class IllegalTransitionError(Exception): pass
class ControlFlowHalt(Exception): pass
class ControlFlowAbort(Exception): pass

class ValidationError(Exception): pass
class BudgetExceededError(Exception): pass
class CacheMiss(Exception): pass
class StateIntegrityError(Exception): pass

class SafetyViolationError(Exception): pass
class RedactionFailureError(Exception): pass
class ArbitrationError(Exception): pass

class WorkflowFailed(Exception): pass
class WorkflowCompleted(Exception): pass
