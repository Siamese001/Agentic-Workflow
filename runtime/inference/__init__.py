"""Runtime inference layer - execution, context management, and budget control."""

from .executor import (
    TaskExecutionContext,
    TaskExecutionResult,
    TaskExecutor,
    execute_task,
    get_task_executor,
    configure_task_executor
)
from .context_manager import (
    ContextEntry,
    ConversationContext,
    ContextQuery,
    ContextManager,
    get_context_manager,
    create_context,
    add_context_entry,
    get_context_entries
)
from .runtime_utils import (
    SandboxConfig,
    ModelInvocationResult,
    ModelExecutor,
    invoke_model,
    invoke_model_with_result,
    get_model_executor,
    configure_model_executor,
    list_available_models,
    validate_model_id
)

__all__ = [
    # Executor classes and functions
    "TaskExecutionContext",
    "TaskExecutionResult", 
    "TaskExecutor",
    "execute_task",
    "get_task_executor",
    "configure_task_executor",
    
    # Context manager classes and functions
    "ContextEntry",
    "ConversationContext",
    "ContextQuery",
    "ContextManager",
    "get_context_manager",
    "create_context",
    "add_context_entry",
    "get_context_entries",
    
    # Runtime utilities
    "SandboxConfig",
    "ModelInvocationResult",
    "ModelExecutor",
    "invoke_model",
    "invoke_model_with_result",
    "get_model_executor",
    "configure_model_executor",
    "list_available_models",
    "validate_model_id"
]
