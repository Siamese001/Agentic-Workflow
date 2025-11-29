#!/usr/bin/env python3
"""
L1 Planning Layer - Resume Generator Planner
Pure cognition planner using ATOMIC_RG_SPEC
"""

from typing import Dict, Any, Optional

from resume_engine.l1.rg_plan_schema import CompleteRGPlan

class RGPlanner:
    """Resume Generator Planner - L1 pure cognition layer"""
    
    def __init__(self):
        self.plan_id_prefix = "rg_plan"
        self.default_execution_order = [
            "routing", "parameters", "job_workflow", "quant", "bullets",
            "rewrite", "skills", "sections", "ats", "templates",
            "formatting", "seniority", "tone", "constraints", "validation", "mission"
        ]
    
    def create_complete_plan(self, 
                           job_description: Optional[str] = None,
                           master_resume: Optional[Dict[str, Any]] = None,
                           target_seniority: Optional[str] = None,
                           constraints: Optional[Dict[str, Any]] = None) -> CompleteRGPlan:
        """
        Create a complete resume generation plan
        
        Args:
            job_description: Target job description
            master_resume: Source master resume
            target_seniority: Target seniority level
            constraints: Additional constraints
            
        Returns:
            CompleteRGPlan with all sub-plans populated
        """
        
        plan = CompleteRGPlan()
        
        # Enrich plans with contextual information
        self._enrich_routing_plan(plan, job_description, master_resume)
        self._enrich_parameter_plan(plan, target_seniority, constraints)
        self._enrich_job_workflow_plan(plan, job_description)
        self._enrich_quant_plan(plan, job_description)
        self._enrich_bullet_plan(plan, master_resume)
        self._enrich_formatting_plan(plan, target_seniority)
        self._enrich_seniority_plan(plan, target_seniority)
        self._enrich_constraints_plan(plan, constraints)
        self._enrich_validation_plan(plan, job_description, master_resume)
        
        return plan
    
    def _enrich_routing_plan(self, plan: CompleteRGPlan, 
                            job_description: Optional[str], 
                            master_resume: Optional[Dict[str, Any]]) -> None:
        """Enrich routing plan with job and resume context"""
        if job_description:
            plan.routing.workflow_sequence.append("job_analysis")
        if master_resume:
            plan.routing.workflow_sequence.append("resume_extraction")
        plan.routing.workflow_sequence.extend([
            "quant_scoring", "bullet_generation", "formatting", "validation"
        ])
        plan.routing.execution_parameters["has_job_description"] = bool(job_description)
        plan.routing.execution_parameters["has_master_resume"] = bool(master_resume)
    
    def _enrich_parameter_plan(self, plan: CompleteRGPlan,
                              target_seniority: Optional[str],
                              constraints: Optional[Dict[str, Any]]) -> None:
        """Enrich parameter plan with seniority and constraints"""
        if target_seniority:
            plan.parameter_values["target_seniority"] = target_seniority
        if constraints:
            plan.config_overrides.update(constraints)
        plan.runtime_settings["optimization_level"] = "balanced"
    
    def _enrich_job_workflow_plan(self, plan: CompleteRGPlan,
                                 job_description: Optional[str]) -> None:
        """Enrich job workflow plan with job analysis"""
        if job_description:
            plan.job_analysis_rules["job_description_length"] = len(job_description)
            plan.job_workflow_steps = ["extract_requirements", "analyze_keywords", "map_skills"]
    
    def _enrich_quant_plan(self, plan: CompleteRGPlan,
                          job_description: Optional[str]) -> None:
        """Enrich quant plan with scoring thresholds"""
        plan.metric_thresholds["min_keyword_match"] = 0.7
        plan.metric_thresholds["min_skill_alignment"] = 0.6
        if job_description:
            plan.quant_config["job_complexity"] = "medium"
    
    def _enrich_bullet_plan(self, plan: CompleteRGPlan,
                           master_resume: Optional[Dict[str, Any]]) -> None:
        """Enrich bullet plan with resume context"""
        if master_resume:
            plan.generation_parameters["source_experience_count"] = len(master_resume.get("experience", []))
        plan.formatting_constraints["max_bullet_length"] = 200
    
    def _enrich_formatting_plan(self, plan: CompleteRGPlan,
                               target_seniority: Optional[str]) -> None:
        """Enrich formatting plan with seniority context"""
        if target_seniority:
            plan.style_parameters["seniority_adjusted"] = True
        plan.presentation_settings["output_format"] = "markdown"
    
    def _enrich_seniority_plan(self, plan: CompleteRGPlan,
                              target_seniority: Optional[str]) -> None:
        """Enrich seniority plan with target level"""
        if target_seniority:
            plan.level_parameters["target_level"] = target_seniority
            plan.targeting_settings["level_specific_keywords"] = True
    
    def _enrich_constraints_plan(self, plan: CompleteRGPlan,
                                constraints: Optional[Dict[str, Any]]) -> None:
        """Enrich constraints plan with provided constraints"""
        if constraints:
            plan.constraint_rules.update(constraints)
        plan.limit_parameters["max_resume_length"] = 1000
        plan.enforcement_settings["strict_mode"] = False
    
    def _enrich_validation_plan(self, plan: CompleteRGPlan,
                               job_description: Optional[str],
                               master_resume: Optional[Dict[str, Any]]) -> None:
        """Enrich validation plan with context"""
        plan.validation_settings["validate_ats_compliance"] = True
        plan.validation_settings["validate_content_truthfulness"] = True
        if job_description:
            plan.quality_parameters["job_alignment_required"] = True
        if master_resume:
            plan.quality_parameters["source_validation"] = True
    
    def create_minimal_plan(self) -> CompleteRGPlan:
        """Create a minimal plan with default values"""
        return CompleteRGPlan()
    
    def validate_plan_completeness(self, plan: CompleteRGPlan) -> Dict[str, Any]:
        """Validate that plan covers all required capabilities"""
        summary = plan.get_plan_summary()
        validation_result = {
            "is_complete": True,
            "missing_capabilities": [],
            "plan_summary": summary
        }
        
        # Check for empty critical buckets
        critical_buckets = ["routing", "parameters", "quant", "validation"]
        for bucket in critical_buckets:
            if summary.get(f"{bucket}_rules", 0) == 0:
                validation_result["is_complete"] = False
                validation_result["missing_capabilities"].append(bucket)
        
        return validation_result
