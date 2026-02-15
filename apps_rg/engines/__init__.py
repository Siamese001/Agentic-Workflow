"""apps_rg/engines/__init__.py — Sovereign Engine Registry.

Only canonical executors are eagerly imported. All other agents remain
importable directly from their modules, e.g.:
    from apps_rg.engines.RGValidationExecutor import RGValidationExecutor
    from apps_rg.reasoning.ATSCompatibilityAgent import ATSCompatibilityAgent
"""

from .ResumeAssemblyAgent import (
    ResumeAssemblyAgent,
    get_resume_executive_summary,
    get_resume_skills_section,
)
from .RGStrategyExecutor import RGStrategyExecutor
from .RGValidationExecutor import RGValidationExecutor

__all__ = [
    "RGStrategyExecutor",
    "RGValidationExecutor",
    "ResumeAssemblyAgent",
    "get_resume_skills_section",
    "get_resume_executive_summary",
]
