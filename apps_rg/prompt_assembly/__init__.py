"""apps_rg prompt assembly — PA-compatible prompt compilation.

Re-exports the core PA compiler, contracts, slot mapper, and provider adapter.
"""

from apps_rg.prompt_assembly.compiler import compile_prompt
from apps_rg.prompt_assembly.contracts import (
    AppsRgCompiledPromptArtifact,
    AppsRgPromptRequest,
    PACompileStatus,
    PromptCompileReceipt,
    PromptSlotReceipt,
)
from apps_rg.prompt_assembly.provider_request import artifact_to_provider_request
from apps_rg.prompt_assembly.slot_mapper import map_slots, render_template

__all__ = [
    "AppsRgCompiledPromptArtifact",
    "AppsRgPromptRequest",
    "PACompileStatus",
    "PromptCompileReceipt",
    "PromptSlotReceipt",
    "artifact_to_provider_request",
    "compile_prompt",
    "map_slots",
    "render_template",
]
