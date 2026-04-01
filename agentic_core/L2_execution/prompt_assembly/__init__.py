"""
Prompt Assembly Runtime

Core runtime for assembling authority slots (S0→I0→D0→C0→U0) into
compiled prompts with HMAC-SHA256 signatures for verification.
"""

from .authority_validator import (
    AuthorityValidationError,
    AuthorityValidator,
)
from .compiled_artifact import (
    AuthorityLevel,
    AuthoritySlot,
    CompiledPromptArtifact,
    InjectionScanResult,
    PromptBOM,
    RoutingDecision,
    TemplateManifest,
)
from .slot_assembly_engine import (
    AssemblyError,
    SlotAssemblyEngine,
)

__all__ = [
    # Authority levels and slots
    "AuthorityLevel",
    "AuthoritySlot",
    # Compiled artifact
    "CompiledPromptArtifact",
    "PromptBOM",
    "TemplateManifest",
    "RoutingDecision",
    "InjectionScanResult",
    # Validator
    "AuthorityValidator",
    "AuthorityValidationError",
    # Engine
    "SlotAssemblyEngine",
    "AssemblyError",
]
