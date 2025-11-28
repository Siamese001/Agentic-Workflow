#!/usr/bin/env python3
"""
Unified Router - Resume Generation + LinkedIn Outreach
Provides single API for both independent engines
"""

from typing import Dict, Any, Optional
from enum import Enum

class TaskType(str, Enum):
    """Supported task types for unified routing"""
    RESUME_GENERATION = "resume"
    LINKEDIN_OUTREACH = "linkedin_outreach"


class UnifiedRouter:
    """
    Unified router that delegates to appropriate specialized engine
    Resume generation runs first, followed by LinkedIn outreach if requested
    """
    
    def __init__(self):
        """Initialize both specialized engines"""
        # Import resume engine
        from resume_engine.l1.rg_planner import RGPlanner
        from resume_engine.l3.rg_orchestrator import RGOrchestrator
        from resume_engine.l4.rg_state import RGStateManager
        from resume_engine.l5.rg_safety_validator import RGSafetyValidator
        
        # Initialize resume engine components
        self.resume_planner = RGPlanner()
        self.resume_orchestrator = RGOrchestrator()
        self.resume_state_manager = RGStateManager()
        self.resume_safety_validator = RGSafetyValidator()
        
        # TODO: Initialize outreach engine components when needed
        # from outreach_engine.l1.lic_planner import LICPlanner
        # self.outreach_planner = LICPlanner()
        # ... other outreach components
    
    def generate_content(self, task_type: str, input_data: dict) -> dict:
        """
        Unified entry point for both resume generation and LinkedIn outreach
        
        Args:
            task_type: "resume" or "linkedin_outreach"
            input_data: Task-specific input data
            
        Returns:
            Unified response format with task results
        """
        if task_type == TaskType.RESUME_GENERATION:
            return self._generate_resume(input_data)
        elif task_type == TaskType.LINKEDIN_OUTREACH:
            return self._generate_outreach(input_data)
        else:
            raise ValueError(f"Unsupported task type: {task_type}")
    
    def _generate_resume(self, job_input: dict) -> dict:
        """
        Generate resume using RG v10_12 engine
        """
        # Step 1: Extract inputs
        job_description = job_input.get("job_description")
        master_resume = job_input.get("master_resume")
        target_seniority = job_input.get("target_seniority", "mid")
        constraints = job_input.get("constraints")
        
        # Step 2: Create plan
        self.resume_planner.create_complete_plan(
            job_description=job_description,
            master_resume=master_resume,
            target_seniority=target_seniority,
            constraints=constraints
        )
        
        # Step 3: Execute workflow
        orchestrator_output = self.resume_orchestrator.execute_complete_workflow(
            master_resume=master_resume,
            job_description=job_description,
            target_seniority=target_seniority,
            constraints=constraints
        )
        
        # Step 4: Persist state
        workflow_state = self.resume_state_manager.create_workflow_state(
            workflow_id="unified_resume",
            input_parameters=job_input
        )
        self.resume_state_manager.update_workflow_state(
            "unified_resume", "execution", orchestrator_output
        )
        self.resume_state_manager.complete_workflow("unified_resume")
        
        # Step 5: Validate output
        final_resume = orchestrator_output.get("final_resume", {})
        safety_report = self.resume_safety_validator.validate_resume_safety(
            resume_content=final_resume,
            job_context={"job_description": job_description}
        )
        
        return {
            "task_type": TaskType.RESUME_GENERATION,
            "status": "completed",
            "resume": final_resume,
            "safety_report": safety_report,
            "workflow_state": workflow_state
        }
    
    def _generate_outreach(self, outreach_input: dict) -> dict:
        """
        Generate LinkedIn outreach using LIC engine
        TODO: Implement when outreach engine is fully integrated
        """
        # Placeholder for outreach generation
        return {
            "task_type": TaskType.LINKEDIN_OUTREACH,
            "status": "not_implemented",
            "message": "LinkedIn outreach engine integration pending"
        }
    
    def generate_sequential(self, resume_input: dict, outreach_input: Optional[dict] = None) -> dict:
        """
        Generate resume first, then LinkedIn outreach if provided
        Resume generation runs first, followed by LinkedIn outreach
        
        Args:
            resume_input: Resume generation input data
            outreach_input: Optional LinkedIn outreach input data
            
        Returns:
            Combined results from both engines
        """
        results = {
            "workflow_type": "sequential",
            "resume_result": None,
            "outreach_result": None
        }
        
        # Step 1: Generate resume (always runs first)
        results["resume_result"] = self._generate_resume(resume_input)
        
        # Step 2: Generate outreach if provided (runs after resume)
        if outreach_input:
            results["outreach_result"] = self._generate_outreach(outreach_input)
        
        return results


# Global router instance
_unified_router = UnifiedRouter()

# Public API functions
def generate_resume_v10_12(job_input: dict) -> dict:
    """
    Resume generation API (backward compatible)
    """
    return _unified_router.generate_content(TaskType.RESUME_GENERATION, job_input)

def generate_linkedin_outreach(outreach_input: dict) -> dict:
    """
    LinkedIn outreach API
    """
    return _unified_router.generate_content(TaskType.LINKEDIN_OUTREACH, outreach_input)

def generate_sequential_workflow(resume_input: dict, outreach_input: Optional[dict] = None) -> dict:
    """
    Sequential workflow: Resume generation first, then LinkedIn outreach
    """
    return _unified_router.generate_sequential(resume_input, outreach_input)


__all__ = [
    'UnifiedRouter',
    'TaskType',
    'generate_resume_v10_12',
    'generate_linkedin_outreach', 
    'generate_sequential_workflow'
]
