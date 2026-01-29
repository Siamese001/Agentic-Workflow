"""Logic Nodes Package for Resume Generation App.
Maintains structural parity with apps_lic.
"""

from .resume_section_node import (
    IndustryExtractionResult,
    ResumeSectionNode,
    ResumeSectionOutput,
    RoleExtractionResult,
    SectionAnalysisResult,
)
from .rg_flow_router import ResumeFlowResult, RGFlowOutput, RGFlowRouter
from .skill_extractor_node import (
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
