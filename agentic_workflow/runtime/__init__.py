#!/usr/bin/env python3
"""
Runtime Integration Layer - Resume Generator v10_12
Provides the main public API for resume generation using L1-L5 engine components
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Import L1-L5 components using clean absolute imports
from agentic_workflow.l1.rg_planner import RGPlanner
from agentic_workflow.l3.rg_orchestrator import RGOrchestrator
from agentic_workflow.l4.rg_state import RGStateManager
from agentic_workflow.l5.rg_safety_validator import RGSafetyValidator

logger = logging.getLogger(__name__)


class ResumeGeneratorRuntime:
    """
    Runtime wrapper for Resume Generator v10_12
    Orchestrates L1-L5 components to provide a single stable public API
    """
    
    def __init__(self):
        """Initialize runtime with all L1-L5 components"""
        self.planner = RGPlanner()
        self.orchestrator = RGOrchestrator()
        self.state_manager = RGStateManager()
        self.safety_validator = RGSafetyValidator()
        
        logger.info("ResumeGeneratorRuntime initialized with L1-L5 components")
    
    def generate_resume(self, job_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main resume generation pipeline following required execution flow
        
        Step 1 → Receive job_input (dict)
        Step 2 → Call RGPlanner.create_complete_plan(job_input)
        Step 3 → Call RGOrchestrator.execute_complete_workflow(plan)
        Step 4 → Persist final orchestrator output via RGStateManager
        Step 5 → Validate output using RGSafetyValidator
        Step 6 → Return final validated resume (dict)
        
        Args:
            job_input: Dictionary containing job description, master resume, 
                      target seniority, and constraints
                      
        Returns:
            Dictionary containing generated resume and metadata
        """
        workflow_id = f"rg_runtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: Extract inputs from job_input
            job_description = job_input.get("job_description")
            master_resume = job_input.get("master_resume")
            target_seniority = job_input.get("target_seniority", "mid")
            constraints = job_input.get("constraints")
            
            logger.info(f"Starting resume generation workflow {workflow_id}")
            
            # Step 2: Create plan using RGPlanner
            logger.info("Step 2: Creating execution plan")
            plan = self.planner.create_complete_plan(
                job_description=job_description,
                master_resume=master_resume,
                target_seniority=target_seniority,
                constraints=constraints
            )
            
            # Step 3: Execute workflow using RGOrchestrator
            logger.info("Step 3: Executing complete workflow")
            execution_result = self.orchestrator.execute_complete_workflow(
                master_resume=master_resume,
                job_description=job_description,
                target_seniority=target_seniority,
                constraints=constraints
            )
            
            # Step 4: Persist state using RGStateManager
            logger.info("Step 4: Persisting workflow state")
            workflow_state = self.state_manager.create_workflow_state(
                workflow_id=workflow_id,
                input_parameters=job_input
            )
            
            # Store execution results in state
            self.state_manager.update_workflow_state(
                workflow_id, "planning", {"plan": plan.get_plan_summary() if hasattr(plan, 'get_plan_summary') else str(plan)}
            )
            self.state_manager.update_workflow_state(
                workflow_id, "execution", execution_result
            )
            
            # Step 5: Validate output using RGSafetyValidator
            logger.info("Step 5: Validating resume safety")
            final_resume = execution_result.get("final_resume", {})
            safety_report = self.safety_validator.validate_resume_safety(
                resume_content=final_resume,
                job_context={"job_description": job_description}
            )
            
            # Step 6: Complete workflow and return final result
            self.state_manager.complete_workflow(workflow_id)
            
            final_result = {
                "workflow_id": workflow_id,
                "status": "completed" if safety_report.is_safe else "completed_with_warnings",
                "resume": final_resume,
                "safety_report": {
                    "is_safe": safety_report.is_safe,
                    "safety_score": safety_report.overall_safety_score,
                    "violations_count": len(safety_report.violations),
                    "warnings": safety_report.warnings
                },
                "execution_metadata": execution_result.get("metadata", {}),
                "plan_summary": plan.get_plan_summary() if hasattr(plan, 'get_plan_summary') else str(plan),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Resume generation completed successfully for workflow {workflow_id}")
            return final_result
            
        except Exception as e:
            logger.error(f"Resume generation failed for workflow {workflow_id}: {str(e)}")
            
            # Record error in state manager
            if 'workflow_id' in locals():
                self.state_manager.record_workflow_error(workflow_id, "runtime", str(e))
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }


# Public API function as required
def generate_resume_v10_12(job_input: dict) -> dict:
    """
    Public API function for resume generation v10_12
    
    Args:
        job_input: Dictionary containing job description, master resume, 
                  target seniority, and constraints
                  
    Returns:
        Dictionary containing generated resume and metadata
    """
    runtime = ResumeGeneratorRuntime()
    return runtime.generate_resume(job_input)


# Export the main API
__all__ = ["ResumeGeneratorRuntime", "generate_resume_v10_12"]
