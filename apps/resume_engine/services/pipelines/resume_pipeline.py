"""
Resume Pipeline Service
LEVEL 5 - Orchestrates the complete resume generation workflow
"""

from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
import time
from datetime import datetime

from ..builders.resume_builder import ResumeBuilder
from ..builders.ats_optimizer import ATSOptimizer
from ..enrichers.skill_expander import SkillExpander
from ..enrichers.job_alignment import JobAligner
from ..generators.section_generator import SectionGenerator
from ..generators.summary_generator import SummaryGenerator

@dataclass
class PipelineResult:
    """Results of the resume generation pipeline"""
    resume_content: Dict[str, Any]
    metadata: Dict[str, Any]
    processing_time: float
    stages_completed: List[str]
    quality_score: float

class ResumePipeline:
    """Orchestrates the complete resume generation and optimization workflow"""
    
    def __init__(self):
        self.resume_builder = ResumeBuilder()
        self.ats_optimizer = ATSOptimizer()
        self.skill_expander = SkillExpander()
        self.job_aligner = JobAligner()
        self.section_generator = SectionGenerator()
        self.summary_generator = SummaryGenerator()
        
        self.pipeline_stages = [
            "skill_analysis",
            "job_alignment", 
            "content_generation",
            "ats_optimization",
            "quality_validation"
        ]
    
    async def execute(
        self,
        request: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> PipelineResult:
        """
        Execute the complete resume generation pipeline
        
        Args:
            request: Resume generation request with user profile and job description
            preferences: Generation preferences and options
            
        Returns:
            Complete pipeline results with optimized resume
        """
        start_time = time.time()
        preferences = preferences or {}
        
        user_profile = request.get("user_profile", {})
        job_description = request.get("job_description", {})
        
        completed_stages = []
        pipeline_data = {}
        
        try:
            # Stage 1: Skill Analysis and Expansion
            skill_analysis = await self._stage_skill_analysis(user_profile, job_description)
            pipeline_data["skill_analysis"] = skill_analysis
            completed_stages.append("skill_analysis")
            
            # Stage 2: Job Alignment Analysis
            alignment_analysis = await self._stage_job_alignment(
                user_profile, job_description, skill_analysis
            )
            pipeline_data["job_alignment"] = alignment_analysis
            completed_stages.append("job_alignment")
            
            # Stage 3: Content Generation
            content_generation = await self._stage_content_generation(
                user_profile, job_description, preferences, pipeline_data
            )
            pipeline_data["content_generation"] = content_generation
            completed_stages.append("content_generation")
            
            # Stage 4: ATS Optimization
            ats_optimization = await self._stage_ats_optimization(
                content_generation, job_description
            )
            pipeline_data["ats_optimization"] = ats_optimization
            completed_stages.append("ats_optimization")
            
            # Stage 5: Quality Validation
            quality_validation = await self._stage_quality_validation(
                content_generation, ats_optimization, alignment_analysis
            )
            pipeline_data["quality_validation"] = quality_validation
            completed_stages.append("quality_validation")
            
            # Compile final results
            processing_time = time.time() - start_time
            
            return PipelineResult(
                resume_content=content_generation,
                metadata={
                    "skill_analysis": skill_analysis,
                    "job_alignment": alignment_analysis,
                    "ats_optimization": ats_optimization,
                    "quality_validation": quality_validation,
                    "processing_time": processing_time,
                    "timestamp": datetime.utcnow().isoformat()
                },
                processing_time=processing_time,
                stages_completed=completed_stages,
                quality_score=quality_validation.get("overall_score", 0.8)
            )
            
        except Exception as e:
            # Return partial results with error information
            processing_time = time.time() - start_time
            return PipelineResult(
                resume_content=pipeline_data.get("content_generation", {}),
                metadata={
                    "error": str(e),
                    "partial_results": pipeline_data,
                    "processing_time": processing_time,
                    "stages_completed": completed_stages
                },
                processing_time=processing_time,
                stages_completed=completed_stages,
                quality_score=0.0
            )
    
    async def _stage_skill_analysis(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 1: Analyze and expand user skills"""
        user_skills = user_profile.get("skills", [])
        
        skill_analysis = await self.skill_expander.expand_skills(user_skills, job_description)
        
        return {
            "expanded_skills": skill_analysis.expanded_skills,
            "skill_categories": skill_analysis.skill_categories,
            "proficiency_levels": skill_analysis.proficiency_levels,
            "recommended_additions": skill_analysis.recommended_additions
        }
    
    async def _stage_job_alignment(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        skill_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 2: Analyze job-resume alignment"""
        # Create enhanced profile with expanded skills
        enhanced_profile = user_profile.copy()
        enhanced_profile["skills"] = skill_analysis["expanded_skills"]
        
        # Build basic resume content for alignment analysis
        basic_resume = await self.resume_builder.build_resume(enhanced_profile, job_description)
        
        alignment_analysis = await self.job_aligner.analyze_alignment(
            basic_resume["content"], job_description
        )
        
        return {
            "alignment_score": alignment_analysis.alignment_score,
            "matched_requirements": alignment_analysis.matched_requirements,
            "missing_requirements": alignment_analysis.missing_requirements,
            "strength_areas": alignment_analysis.strength_areas,
            "improvement_areas": alignment_analysis.improvement_areas,
            "optimization_suggestions": alignment_analysis.optimization_suggestions
        }
    
    async def _stage_content_generation(
        self,
        user_profile: Dict[str, Any],
        job_description: Dict[str, Any],
        preferences: Dict[str, Any],
        pipeline_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 3: Generate resume content"""
        # Enhance user profile with skill analysis
        enhanced_profile = user_profile.copy()
        enhanced_profile["skills"] = pipeline_data["skill_analysis"]["expanded_skills"]
        
        # Generate complete resume
        resume_result = await self.resume_builder.build_resume(
            enhanced_profile, job_description, preferences
        )
        
        return resume_result["content"]
    
    async def _stage_ats_optimization(
        self,
        resume_content: Dict[str, Any],
        job_description: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 4: Optimize for ATS systems"""
        ats_result = await self.ats_optimizer.optimize_resume(resume_content, job_description)
        
        return {
            "ats_score": ats_result.score,
            "recommendations": ats_result.recommendations,
            "keyword_density": ats_result.keyword_density,
            "format_issues": ats_result.format_issues,
            "compliance_score": ats_result.compliance_score
        }
    
    async def _stage_quality_validation(
        self,
        resume_content: Dict[str, Any],
        ats_optimization: Dict[str, Any],
        alignment_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 5: Validate overall quality"""
        # Calculate quality metrics
        word_count = sum(
            len(section.get("content", [])) if isinstance(section.get("content"), list)
            else len(str(section.get("content", "")).split())
            for section in resume_content.values()
        )
        
        # Calculate overall quality score
        ats_score = ats_optimization.get("ats_score", 0.8)
        alignment_score = alignment_analysis.get("alignment_score", 0.8)
        
        # Weight the scores
        overall_score = (ats_score * 0.6) + (alignment_score * 0.4)
        
        # Quality checks
        quality_issues = []
        
        if word_count < 200:
            quality_issues.append("Resume may be too brief")
        elif word_count > 600:
            quality_issues.append("Resume may be too long for one page")
        
        if ats_score < 70:
            quality_issues.append("ATS optimization needs improvement")
        
        if alignment_score < 70:
            quality_issues.append("Job alignment could be stronger")
        
        return {
            "overall_score": overall_score,
            "word_count": word_count,
            "quality_issues": quality_issues,
            "readability_score": 0.85,  # Placeholder
            "completeness_score": 0.90,  # Placeholder
            "validation_passed": overall_score >= 0.7 and len(quality_issues) == 0
        }
    
    async def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and configuration"""
        return {
            "stages": self.pipeline_stages,
            "total_stages": len(self.pipeline_stages),
            "components": {
                "resume_builder": "initialized",
                "ats_optimizer": "initialized", 
                "skill_expander": "initialized",
                "job_aligner": "initialized",
                "section_generator": "initialized",
                "summary_generator": "initialized"
            }
        }

__all__ = ["ResumePipeline", "PipelineResult"]
