"""Prompt governance infrastructure.

Provides centralized prompt loading and caching for agentic components.
"""

from .contracts import CompiledPromptArtifact, PromptBOM, TemplateManifest
from .core.evaluation_loader import EvalLoadError, EvalSchemaError, EvaluationLoader
from .core.prompt_entry_types import (
    PromptConstitution,
    get_constitution,
    get_persona,
    get_prompt,
    get_template,
)
from .core.prompt_loader import PromptLoader, PromptLoadError, PromptSchemaError
from .managed_workflow_pa_resolver import ManagedWorkflowPAResolver
from . import mixins as _mixins
from .orchestrator import CompiledPromptEnvelope, assemble_prompt
from .pa_package_driven_binding import pa_assemble_prompt_package_driven
from .scripts.validate_assembly import validate_slot_order
from . import validation as _validation

BUNDLED_MIXIN_IDS = _mixins.BUNDLED_MIXIN_IDS
MixinNotFoundError = _mixins.MixinNotFoundError
bundled_mixin_content_hash = _mixins.bundled_mixin_content_hash
get_bundled_mixin = _mixins.get_bundled_mixin
is_bundled_mixin = _mixins.is_bundled_mixin

ApplyPatchReport = _validation.ApplyPatchReport
validate_apply_patch = _validation.validate_apply_patch

__all__ = [
    "EvalLoadError",
    "EvalSchemaError",
    "EvaluationLoader",
    "PromptLoader",
    "PromptLoadError",
    "PromptSchemaError",
    "PromptConstitution",
    "get_constitution",
    "get_prompt",
    "get_template",
    "get_persona",
    "CompiledPromptArtifact",
    "PromptBOM",
    "TemplateManifest",
    "assemble_prompt",
    "CompiledPromptEnvelope",
    "ManagedWorkflowPAResolver",
    "pa_assemble_prompt_package_driven",
    "validate_slot_order",
    "BUNDLED_MIXIN_IDS",
    "MixinNotFoundError",
    "bundled_mixin_content_hash",
    "get_bundled_mixin",
    "is_bundled_mixin",
    "ApplyPatchReport",
    "validate_apply_patch",
]
