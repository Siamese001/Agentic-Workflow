"""System Learning type definitions."""

# Re-exports are done via direct imports from submodules to avoid circular imports.
# Import directly from system_learning.types.meta_learning_types, etc.

# Wave 1: Case Compilation types
from system_learning.types.case_compilation_types import (
    CaseCompilationResult,
    CompilationInput,
    CompilationPayload,
    CompilationStage,
    ContextLogAttachment,
    SealedOutputRef,
)

__all__ = [
    # Case Compilation types
    "CaseCompilationResult",
    "CompilationInput",
    "CompilationPayload",
    "CompilationStage",
    "ContextLogAttachment",
    "SealedOutputRef",
]
