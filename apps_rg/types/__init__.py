"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/types\__init__.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.types\__init__ is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/types\__init__.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """Types package for apps_rg."""
# 
# from apps_rg.types.rg_types import (
#     ExperienceEntry,
#     ExperienceLevel,
#     ResumeConfig,
#     ResumeFormat,
#     ResumeRequest,
#     ResumeResult,
#     ResumeRunSummary,
#     ResumeSection,
#     ResumeStatus,
#     SkillMatch,
#     TargetIndustry,
# )
# 
# __all__ = [
#     "ExperienceEntry",
#     "ExperienceLevel",
#     "ResumeConfig",
#     "ResumeFormat",
#     "ResumeRequest",
#     "ResumeResult",
#     "ResumeRunSummary",
#     "ResumeSection",
#     "ResumeStatus",
#     "SkillMatch",
#     "TargetIndustry",
# ]
# 