"""apps_rg prompt_assembly — INERT (W0 cleanup).

This package is neutralized per W0 cleanup of quarantine rot.
Prompt assembly functionality has been relocated to agentic_core.
"""

# W0 cleanup: Package made inert. No runtime functionality remains here.
__all__: list[str] = []
# """apps_rg prompt assembly — PA-compatible prompt compilation.
# 
# Re-exports the core PA compiler, contracts, slot mapper, and provider adapter.
# """
# 
# from apps_rg.prompt_assembly.compiler import compile_prompt
# from apps_rg.prompt_assembly.contracts import (
#     AppsRgCompiledPromptArtifact,
#     AppsRgPromptRequest,
#     PACompileStatus,
#     PromptCompileReceipt,
#     PromptSlotReceipt,
# )
# from apps_rg.prompt_assembly.provider_request import artifact_to_provider_request
# from apps_rg.prompt_assembly.slot_mapper import map_slots, render_template
# 
# __all__ = [
#     "AppsRgCompiledPromptArtifact",
#     "AppsRgPromptRequest",
#     "PACompileStatus",
#     "PromptCompileReceipt",
#     "PromptSlotReceipt",
#     "artifact_to_provider_request",
#     "compile_prompt",
#     "map_slots",
#     "render_template",
# ]
# 