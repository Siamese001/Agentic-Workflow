#!/usr/bin/env python3
"""
L3 Orchestration Layer - Resume Generator Orchestrator
Orchestrates K1-K8 execution workflow with retry and error handling
"""

from typing import Dict, Any, Optional, List
import time
import logging
from datetime import datetime

from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC

# Import L1 planning
from resume_engine.l1.rg_planner import RGPlanner

# Import L2 executors
from resume_engine.l2.rg_k1_extract import K1Extractor
from resume_engine.l2.rg_k2_clean import K2Cleaner
from resume_engine.l2.rg_k3_quant import K3Quantifier
from resume_engine.l2.rg_k4_rewrite import K4Rewriter
from resume_engine.l2.rg_k5_skillmap import K5SkillMapper
from resume_engine.l2.rg_k6_section_assembly import K6SectionAssembler
from resume_engine.l2.rg_k7_format import K7Formatter
from resume_engine.l2.rg_k8_validation import K8Validator

class RGOrchestrator:
    """Resume Generator Orchestrator - L3 orchestration layer"""
    
    def __init__(self):
        self.routing_rules = ATOMIC_RG_SPEC.get("routing", {})
        self.parameters = ATOMIC_RG_SPEC.get("parameters", {})
        
        # Initialize L1 planner
        self.planner = RGPlanner()
        
        # Initialize L2 executors
        self.k1_extractor = K1Extractor()
        self.k2_cleaner = K2Cleaner()
        self.k3_quantifier = K3Quantifier()
        self.k4_rewriter = K4Rewriter()
        self.k5_skill_mapper = K5SkillMapper()
        self.k6_section_assembler = K6SectionAssembler()
        self.k7_formatter = K7Formatter()
        self.k8_validator = K8Validator()
        
        # Orchestration configuration
        self.retry_config = {
            "max_retries": 3,
            "backoff_factor": 2.0,
            "timeout_seconds": 30
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def execute_complete_workflow(self, 
                                 master_resume: Optional[Dict[str, Any]] = None,
                                 job_description: Optional[str] = None,
                                 target_seniority: str = "mid",
                                 constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute complete K1-K8 workflow
        
        Args:
            master_resume: Source master resume
            job_description: Target job description
            target_seniority: Target seniority level
            constraints: Additional constraints
            
        Returns:
            Complete workflow execution results
        """
        workflow_id = f"rg_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        execution_context = {
            "workflow_id": workflow_id,
            "start_time": datetime.now(),
            "status": "running",
            "inputs": {
                "master_resume": bool(master_resume),
                "job_description": bool(job_description),
                "target_seniority": target_seniority,
                "constraints": bool(constraints)
            }
        }
        
        try:
            # Create execution plan
            plan = self.planner.create_complete_plan(
                job_description, master_resume, target_seniority, constraints
            )
            
            # Execute K1-K8 sequentially
            execution_results = self._execute_k_steps(
                master_resume, job_description, target_seniority, constraints, plan
            )
            
            # Compile final results
            final_result = {
                "workflow_id": workflow_id,
                "status": "completed",
                "execution_context": execution_context,
                "plan": plan.get_plan_summary(),
                "execution_results": execution_results,
                "final_resume": self._compile_final_resume(execution_results),
                "metadata": {
                    "total_execution_time": (datetime.now() - execution_context["start_time"]).total_seconds(),
                    "steps_completed": len([r for r in execution_results.values() if r.get("status") == "completed"]),
                    "routing_rules_applied": len(self.routing_rules),
                    "parameters_used": len(self.parameters)
                }
            }
            
            return final_result
            
        except Exception as e:
            execution_context["status"] = "failed"
            execution_context["error"] = str(e)
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "execution_context": execution_context,
                "error": str(e),
                "metadata": {
                    "failure_time": datetime.now().isoformat(),
                    "routing_rules_applied": len(self.routing_rules)
                }
            }
    
    def _execute_k_steps(self, 
                        master_resume: Optional[Dict[str, Any]],
                        job_description: Optional[str],
                        target_seniority: str,
                        constraints: Optional[Dict[str, Any]],
                        plan) -> Dict[str, Any]:
        """Execute all K1-K8 steps with retry logic"""
        
        results = {}
        
        # K1 - Extract
        results["k1"] = self._execute_with_retry(
            self.k1_extractor.execute_extraction,
            master_resume=master_resume,
            job_description=job_description
        )
        
        # K2 - Clean
        k1_data = results["k1"].get("extracted_data", {})
        results["k2"] = self._execute_with_retry(
            self.k2_cleaner.execute_cleaning,
            extracted_resume=k1_data.get("resume"),
            extracted_job=k1_data.get("job")
        )
        
        # K3 - Quant
        k2_data = results["k2"].get("cleaned_data", {})
        results["k3"] = self._execute_with_retry(
            self.k3_quantifier.execute_quantification,
            cleaned_resume=k2_data.get("resume"),
            cleaned_job=k2_data.get("job")
        )
        
        # K4 - Rewrite (NO-OP)
        k3_data = results["k3"].get("quantification_results", {})
        results["k4"] = self._execute_with_retry(
            self.k4_rewriter.execute_rewrite,
            cleaned_resume=k2_data.get("resume"),
            cleaned_job=k2_data.get("job"),
            quant_results=k3_data
        )
        
        # K5 - SkillMap (NO-OP)
        k4_data = results["k4"].get("rewritten_data", {})
        results["k5"] = self._execute_with_retry(
            self.k5_skill_mapper.execute_skill_mapping,
            resume_skills=k2_data.get("resume", {}).get("skills"),
            job_requirements=k2_data.get("job"),
            quant_results=k3_data
        )
        
        # K6 - Section Assembly (NO-OP)
        k5_data = results["k5"].get("skill_mapping_results", {})
        results["k6"] = self._execute_with_retry(
            self.k6_section_assembler.execute_section_assembly,
            resume_data=k2_data.get("resume"),
            job_requirements=k2_data.get("job"),
            skill_mapping=k5_data
        )
        
        # K7 - Format
        k6_data = results["k6"].get("assembly_results", {})
        results["k7"] = self._execute_with_retry(
            self.k7_formatter.execute_formatting,
            assembled_sections=k6_data.get("assembled_sections", {}).get("sections"),
            target_seniority=target_seniority,
            formatting_preferences=constraints or {}
        )
        
        # K8 - Validation
        k7_data = results["k7"].get("formatted_results", {})
        results["k8"] = self._execute_with_retry(
            self.k8_validator.execute_validation,
            formatted_resume=k7_data,
            job_requirements=k2_data.get("job"),
            quant_results=k3_data
        )
        
        return results
    
    def _execute_with_retry(self, func, **kwargs) -> Dict[str, Any]:
        """Execute function with retry logic"""
        
        for attempt in range(self.retry_config["max_retries"]):
            try:
                start_time = time.time()
                result = func(**kwargs)
                execution_time = time.time() - start_time
                
                result["execution_metadata"] = {
                    "attempt": attempt + 1,
                    "execution_time": execution_time,
                    "success": True
                }
                
                return result
                
            except Exception as e:
                if attempt == self.retry_config["max_retries"] - 1:
                    # Final attempt failed
                    return {
                        "status": "failed",
                        "error": str(e),
                        "execution_metadata": {
                            "attempt": attempt + 1,
                            "success": False,
                            "max_retries_exceeded": True
                        }
                    }
                
                # Wait before retry
                wait_time = self.retry_config["backoff_factor"] ** attempt
                time.sleep(wait_time)
        
        return {"status": "failed", "error": "Unknown error"}
    
    def _compile_final_resume(self, execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compile final resume from execution results"""
        
        # Get the formatted resume from K7
        k7_results = execution_results.get("k7", {})
        formatted_results = k7_results.get("formatted_results", {})
        
        # Get validation results from K8
        k8_results = execution_results.get("k8", {})
        validation_results = k8_results.get("validation_results", {})
        
        final_resume = {
            "content": formatted_results.get("document", {}),
            "validation": validation_results,
            "quality_score": validation_results.get("quality_score", 0.0),
            "status": "ready" if validation_results.get("quality_score", 0.0) > 0.7 else "needs_review"
        }
        
        return final_resume
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a running workflow (placeholder for async implementation)"""
        return {
            "workflow_id": workflow_id,
            "status": "not_implemented",
            "message": "Async workflow tracking not implemented in this version"
        }
    
    def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel a running workflow (placeholder for async implementation)"""
        return {
            "workflow_id": workflow_id,
            "status": "not_implemented",
            "message": "Workflow cancellation not implemented in this version"
        }
    
    def validate_workflow_inputs(self, 
                                master_resume: Optional[Dict[str, Any]],
                                job_description: Optional[str]) -> Dict[str, Any]:
        """Validate workflow inputs before execution"""
        
        validation_result = {
            "valid": True,
            "issues": [],
            "recommendations": []
        }
        
        if not master_resume:
            validation_result["valid"] = False
            validation_result["issues"].append("Master resume is required")
        
        if not job_description:
            validation_result["issues"].append("Job description is recommended for optimal results")
            validation_result["recommendations"].append("Provide job description for better alignment")
        
        if master_resume and not isinstance(master_resume, dict):
            validation_result["valid"] = False
            validation_result["issues"].append("Master resume must be a dictionary")
        
        return validation_result
