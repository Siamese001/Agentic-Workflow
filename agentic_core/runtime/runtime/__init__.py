#!/usr/bin/env python3
"""
Runtime Layer - Resume Generator v10_12 Integration
Thin facade providing stable public API for the L1-L5 engine
"""

from resume_engine.rg_planner import RGPlanner
from resume_engine.rg_orchestrator import RGOrchestrator
from resume_engine.state import RGStateManager
from resume_engine.l5.rg_safety_validator import RGSafetyValidator


class ResumeGeneratorRuntime:
    """Thin runtime facade for RG v10_12 engine"""
    
    def __init__(self):
        """Initialize all L1-L5 components"""
        self.planner = RGPlanner()
        self.orchestrator = RGOrchestrator()
        self.state_manager = RGStateManager()
        self.safety_validator = RGSafetyValidator()
    
    def generate_resume_v10_12(self, job_input: dict) -> dict:
        """
        Public API: Generate resume using full L1-L5 pipeline
        
        Args:
            job_input: Dictionary containing job and resume data
            
        Returns:
            Dictionary containing validated final resume
        """
        try:
            # Step 1: Extract and structure inputs for resume engine
            job_description = job_input.get("job_description")
            master_resume = job_input.get("master_resume")
            target_seniority = job_input.get("target_seniority", "mid")
            constraints = job_input.get("constraints", {})
            
            # Build job_input dict for resume engine
            resume_engine_job_input = {
                "title": "Senior Software Engineer",  # Extract from job_description if needed
                "description": job_description,
                "company": "Tech Corp",  # Extract from job_description if needed
                "industry": "technology",
                "seniority": target_seniority,
                "requirements": [],  # Extract from job_description if needed
                "skills": [],  # Extract from job_description if needed
                "experience_years": 5
            }
            
            # Build resume_input dict for resume engine
            resume_engine_resume_input = {
                "content": master_resume,
                "sections": {
                    "contact_info": "Extracted from resume content",
                    "summary": "Extracted from resume content",
                    "experience": "Extracted from resume content",
                    "education": "Extracted from resume content",
                    "skills": "Extracted from resume content"
                }
            }
            
            # Build processing options
            processing_options = {
                "analysis_depth": "comprehensive" if constraints else "basic",
                "validation_level": "comprehensive" if constraints else "basic",
                "formatting_standards": constraints.get("format", "ats_optimized")
            }
            
            # Step 2: Generate processing plan (for future extensibility)
            self.planner.plan_resume_processing(
                job_description=job_description,
                master_resume=master_resume,
                target_seniority=target_seniority,
                constraints=constraints
            )
            
            # Step 3: Execute resume generation workflow using actual RGOrchestrator API
            from resume_engine.rg_orchestrator import ResumeGenerationRequest
            generation_request = ResumeGenerationRequest(
                job_input=resume_engine_job_input,
                resume_input=resume_engine_resume_input,
                processing_options=processing_options
            )
            
            orchestrator_result = self.orchestrator.generate_resume(
                request=generation_request
            )
            
            # Step 4: Persist orchestrator output via RGStateManager
            workflow_state = self.state_manager.create_workflow_state(
                workflow_id="rg_runtime",
                input_parameters=job_input
            )
            self.state_manager.update_workflow_state(
                "rg_runtime", "execution", orchestrator_result
            )
            self.state_manager.complete_workflow("rg_runtime")
            
            # Step 5: Validate final output via RGSafetyValidator
            final_resume_content = orchestrator_result.final_resume_content if orchestrator_result.success else ""
            final_resume = {"content": final_resume_content}
            
            safety_report = self.safety_validator.validate_resume_safety(
                resume_content=final_resume,
                job_context={"job_description": job_description}
            )
            
            # Step 6: Return final validated resume (dict)
            return {
                "resume": final_resume,
                "safety_report": safety_report,
                "workflow_state": workflow_state,
                "orchestrator_result": orchestrator_result
            }
            
        except Exception as e:
            # Return error information if pipeline fails
            return {
                "error": str(e),
                "resume": {"content": ""},
                "safety_report": None,
                "workflow_state": None
            }


# Global runtime instance
_runtime = ResumeGeneratorRuntime()

# Public API function
def generate_resume_v10_12(job_input: dict) -> dict:
    """
    Stable public API for resume generation
    
    Args:
        job_input: Dictionary containing job and resume data
        
    Returns:
        Dictionary containing validated final resume
    """
    return _runtime.generate_resume_v10_12(job_input)


__all__ = ['generate_resume_v10_12', 'ResumeGeneratorRuntime']
