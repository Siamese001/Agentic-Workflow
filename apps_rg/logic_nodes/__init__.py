"""Logic Nodes Package for Resume Generation App.
Maintains structural parity with apps_lic.
"""

from .ResumeSectionNode import (
    IndustryExtractionResult,
    ResumeSectionNode,
    ResumeSectionOutput,
    RoleExtractionResult,
    SectionAnalysisResult,
)
from .RGFlowRouter import ResumeFlowResult, RGFlowOutput, RGFlowRouter
from .SkillExtractorNode import (
    SkillAnalysisOutput,
    SkillExtractionResult,
    SkillExtractorNode,
    SkillGapResult,
    SkillMatchResult,
)

__all__ = [
    # Flow Routing Logic
    "RGFlowRouter",
    "RGFlowOutput",
    "ResumeFlowResult",
    # Resume Section Logic
    "ResumeSectionNode",
    "ResumeSectionOutput",
    "RoleExtractionResult",
    "IndustryExtractionResult",
    "SectionAnalysisResult",
    # Skill Extraction Logic
    "SkillExtractorNode",
    "SkillAnalysisOutput",
    "SkillExtractionResult",
    "SkillGapResult",
    "SkillMatchResult",
]
