"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit core runtime contracts or perform prompt assembly.

Original: apps_rg/prompt_assembly/compiler.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Emits CompiledPromptArtifact (core contract authority)

Importing this module raises RuntimeError.
Core L1 Prompt Assembly owns all compilation and contract emission.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/prompt_assembly/compiler.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.prompt_assembly.compiler is QUARANTINED. "
    "apps_rg may NOT emit CompiledPromptArtifact or other core contracts. "
    "Core L1 Prompt Assembly owns compilation. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
