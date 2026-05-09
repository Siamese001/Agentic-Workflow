"""compiler - QUARANTINED PLACEHOLDER

This module has been moved to apps_rg/_quarantine/ as part of W4 governance enforcement.

Reason: Runtime authority violation (emits CompiledPromptArtifact - core contract authority).
All prompt assembly and contract emission now lives in agentic_core L1.

See: .windsurf/plans/author-gate-enforcement-deferred-scope-complete-d7f5e3.md
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.prompt_assembly.compiler is QUARANTINED. "
    "apps_rg may NOT emit CompiledPromptArtifact or other core contracts. "
    "Core L1 Prompt Assembly owns compilation."
)
