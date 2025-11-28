#!/usr/bin/env python3
"""
Runtime Layer - Resume Generator v10_12 Integration
Thin facade providing stable public API for the L1-L5 engine
"""

from agentic_workflow.resume_engine.l1.rg_planner import RGPlanner
from agentic_workflow.resume_engine.l3.rg_orchestrator import RGOrchestrator
from agentic_workflow.resume_engine.l4.rg_state import RGStateManager
from agentic_workflow.resume_engine.l5.rg_safety_validator import RGSafetyValidator


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
        # Step 1: Accept job_input (already done as parameter)
        
        # Step 2: Create plan via RGPlanner.create_complete_plan()
        job_description = job_input.get("job_description")
        master_resume = job_input.get("master_resume")
        target_seniority = job_input.get("target_seniority", "mid")
        constraints = job_input.get("constraints")
        
        # Plan created for documentation purposes (not directly used in current flow)
        self.planner.create_complete_plan(
            job_description=job_description,
            master_resume=master_resume,
            target_seniority=target_seniority,
            constraints=constraints
        )
        
        # Step 3: Execute full workflow via RGOrchestrator.execute_complete_workflow()
        orchestrator_output = self.orchestrator.execute_complete_workflow(
            master_resume=master_resume,
            job_description=job_description,
            target_seniority=target_seniority,
            constraints=constraints
        )
        
        # Step 4: Persist orchestrator output via RGStateManager
        workflow_state = self.state_manager.create_workflow_state(
            workflow_id="rg_runtime",
            input_parameters=job_input
        )
        self.state_manager.update_workflow_state(
            "rg_runtime", "execution", orchestrator_output
        )
        self.state_manager.complete_workflow("rg_runtime")
        
        # Step 5: Validate final output via RGSafetyValidator
        final_resume = orchestrator_output.get("final_resume", {})
        safety_report = self.safety_validator.validate_resume_safety(
            resume_content=final_resume,
            job_context={"job_description": job_description}
        )
        
        # Step 6: Return final validated resume (dict)
        return {
            "resume": final_resume,
            "safety_report": safety_report,
            "workflow_state": workflow_state
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
