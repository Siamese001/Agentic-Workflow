"""
LIC Outreach Message Generation Executor Shim

Non-destructive shim that re-exports the original message generation executor.
This allows Phase 5 refinement without touching core L2.
"""

# Re-export the original executor exactly as-is
from l2.message_generation_executor import (
    MessageGenerationExecutor,
    MessageSection,
    MessageResult,
    GenerationContext
)

# Ensure all public interfaces are available
__all__ = [
    'MessageGenerationExecutor',
    'MessageSection',
    'MessageResult',
    'GenerationContext'
]
