"""Logic Nodes Package for Resume Generation App.
Maintains structural parity with apps_lic.
"""

from .rg_flow_router import RGFlowRouter, RGFlowOutput, ResumeFlowResult
from .resume_section_node import ResumeSectionNode, ResumeSectionOutput, RoleExtractionResult, IndustryExtractionResult, SectionAnalysisResult
from .skill_extractor_node import SkillExtractorNode, SkillAnalysisOutput, SkillExtractionResult, SkillGapResult, SkillMatchResult

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
