"""apps_rg L2 recipe — registered app-specific step implementations.

This package provides step adapters for the apps_rg deterministic L2 recipe.
Steps are imported and chained by ``agentic_core.runtime.l2_recipe_resolver``
at L2 execution time — **never** directly by ``apps_rg.__main__``.

Canonical dependency law:
    agentic_core → imports apps_rg.l2_recipe.steps (to resolve recipe)
    apps_rg.__main__ → MUST NOT import this package
"""

from apps_rg.l2_recipe.steps import (
    DocxExportStep,
    GenerateResumeStep,
    NarrativePassStep,
)

__all__ = [
    "GenerateResumeStep",
    "NarrativePassStep",
    "DocxExportStep",
]
