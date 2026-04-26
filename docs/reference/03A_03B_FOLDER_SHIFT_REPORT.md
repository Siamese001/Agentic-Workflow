# 03A / 03B Folder Shift Report

## Bottom line
C0 and Prompt Assembly were moved to route-adjacent sibling folders without dropping any content files.

## Folder changes
- `C0_Context_Engine/` -> `03A_C0_Context_Engine/`
- `PA_Prompt_Assembly/` -> `03B_PA_Prompt_Assembly/`

## Rationale
L0 owns RouteContract authority. C0 owns evidence retrieval and FinalEvidenceContract. Prompt Assembly owns provider-ready PromptEnvelope / CompiledPromptArtifact construction.

The `03A` and `03B` prefixes show sequence adjacency after L0 without implying that L0 owns retrieval or prompt assembly.

## Zero-loss statement
All existing files from the previous Windows Explorer-safe pack were preserved. Only folder paths and path references were updated for C0 and PA.
