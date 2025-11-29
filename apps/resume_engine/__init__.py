#!/usr/bin/env python3
"""
Resume Engine - Complete Resume Generation Pipeline

Incorporated from historical agentic_workflow to provide the full 8-node
resume generation pipeline with L1 planning and L3 orchestration.

Architecture Overview:
L1 Planning Layer: RGPlanner (rg_planner.py)
L2 Execution Layer: K1 Extract → K2 Clean → K3 Quantify → K4 Rewrite → K5 Skillmap → K6 Assemble → K7 Format → K8 Validate
L3 Orchestration Layer: RGOrchestrator (rg_orchestrator.py)

Usage:
    from resume_engine import RGOrchestrator, ResumeGenerationRequest
    
    orchestrator = RGOrchestrator()
    request = orchestrator.create_sample_request()
    result = orchestrator.generate_resume(request=request)
"""

__version__ = "1.0.0"
__author__ = "Resume Generation Engine"
__description__ = "Complete 8-node resume generation pipeline with L1-L3 architecture"

# L1 Planning Layer
from .legacy.rg_planner import RGPlanner, ResumeProcessingPlan, ResumeAnalysisPlan, ResumeSectionConfig

# L2 Execution Layer - Now from agentic_core
from agentic_core.l2_execution.draft_execution.rg_k1_extract import RGK1Extract, ExtractionOutput, ExtractedSection, ExtractionMetrics
from agentic_core.l2_execution.draft_execution.rg_k2_clean import RGK2Clean, CleaningOutput, CleaningOperation, CleaningMetrics
from agentic_core.l2_execution.draft_execution.rg_k3_quantify import RGK3Quantify, QuantificationOutput, QuantifiedMetric, QuantifiedAchievement, QuantificationMetrics
from agentic_core.l2_execution.draft_execution.rg_k4_rewrite import RGK4Rewrite, RewritingOutput, RewritingOperation, RewrittenSection, RewritingMetrics
from agentic_core.l2_execution.draft_execution.rg_k5_skillmap import RGK5Skillmap, SkillMappingOutput, SkillMapping, SkillGap, SkillMappingMetrics
from agentic_core.l2_execution.draft_execution.rg_k6_assemble import RGK6Assemble, AssemblyOutput, SectionAssembly, AssemblyMetrics
from agentic_core.l2_execution.draft_execution.rg_k7_format import RGK7Format, FormattingOutput, FormattingRule, FormattedSection, FormattingMetrics
from agentic_core.l2_execution.draft_execution.rg_k8_validate import RGK8Validate, ValidationOutput, ValidationResult, ValidationRule, ValidationMetrics

# L3 Orchestration Layer
from .legacy.rg_orchestrator import RGOrchestrator, ResumeGenerationRequest, ResumeGenerationResult, OrchestratorMetrics

# Public API exports
__all__ = [
    # L1 Planning Layer
    "RGPlanner",
    "ResumeProcessingPlan", 
    "ResumeAnalysisPlan",
    "ResumeSectionConfig",
    
    # L2 Execution Layer - K1 Extract
    "RGK1Extract",
    "ExtractionOutput",
    "ExtractedSection", 
    "ExtractionMetrics",
    
    # L2 Execution Layer - K2 Clean
    "RGK2Clean",
    "CleaningOutput",
    "CleaningOperation",
    "CleaningMetrics",
    
    # L2 Execution Layer - K3 Quantify
    "RGK3Quantify",
    "QuantificationOutput",
    "QuantifiedMetric",
    "QuantifiedAchievement", 
    "QuantificationMetrics",
    
    # L2 Execution Layer - K4 Rewrite
    "RGK4Rewrite",
    "RewritingOutput",
    "RewritingOperation",
    "RewrittenSection",
    "RewritingMetrics",
    
    # L2 Execution Layer - K5 Skillmap
    "RGK5Skillmap",
    "SkillMappingOutput",
    "SkillMapping",
    "SkillGap",
    "SkillMappingMetrics",
    
    # L2 Execution Layer - K6 Assemble
    "RGK6Assemble",
    "AssemblyOutput",
    "SectionAssembly",
    "AssemblyMetrics",
    
    # L2 Execution Layer - K7 Format
    "RGK7Format",
    "FormattingOutput",
    "FormattingRule",
    "FormattedSection",
    "FormattingMetrics",
    
    # L2 Execution Layer - K8 Validate
    "RGK8Validate",
    "ValidationOutput",
    "ValidationResult",
    "ValidationRule",
    "ValidationMetrics",
    
    # L3 Orchestration Layer
    "RGOrchestrator",
    "ResumeGenerationRequest",
    "ResumeGenerationResult",
    "OrchestratorMetrics",
    
    # Convenience functions
    "generate_resume",
    "create_sample_request"
]

def generate_resume(
    job_input: dict,
    resume_input: dict,
    processing_options: dict | None = None,
    config: dict | None = None
) -> ResumeGenerationResult:
    """Convenience function to generate a resume with default orchestrator.
    
    Args:
        job_input: Target job requirements and specifications
        resume_input: Current resume content and structure
        processing_options: Optional processing preferences
        config: Optional orchestrator configuration
        
    Returns:
        Complete resume generation result
    """
    orchestrator = RGOrchestrator(config=config)
    request = ResumeGenerationRequest(
        job_input=job_input,
        resume_input=resume_input,
        processing_options=processing_options
    )
    return orchestrator.generate_resume(request=request)

def create_sample_request() -> ResumeGenerationRequest:
    """Create a sample resume generation request for testing.
    
    Returns:
        Sample request with realistic job and resume data
    """
    orchestrator = RGOrchestrator()
    return orchestrator.create_sample_request()

def get_resume_engine_version():
    """Get the current resume engine version"""
    return __version__

def get_resume_engine_description():
    """Get the resume engine description"""
    return __description__
