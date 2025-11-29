#!/usr/bin/env python3
"""
L1 Planning Layer - Resume Generator Plan Schemas
Pure cognition schemas derived from ATOMIC_RG_SPEC
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

# Import atomic spec as source of truth (read-only reference)
# import sys
# from rg_atomic_spec import ATOMIC_RG_SPEC

class RoutingPlan(BaseModel):
    """Plan for routing and workflow orchestration"""
    workflow_sequence: List[str] = Field(default_factory=list)
    routing_decisions: Dict[str, str] = Field(default_factory=dict)
    execution_parameters: Dict[str, Any] = Field(default_factory=dict)

class ParameterPlan(BaseModel):
    """Plan for parameter presets and configuration"""
    parameter_values: Dict[str, Any] = Field(default_factory=dict)
    config_overrides: Dict[str, Any] = Field(default_factory=dict)
    runtime_settings: Dict[str, Any] = Field(default_factory=dict)

class QuantPlan(BaseModel):
    """Plan for quantitative scoring and metrics"""
    scoring_rules: Dict[str, Any] = Field(default_factory=dict)
    metric_thresholds: Dict[str, float] = Field(default_factory=dict)
    quant_config: Dict[str, Any] = Field(default_factory=dict)

class BulletPlan(BaseModel):
    """Plan for bullet point processing and generation"""
    bullet_rules: Dict[str, Any] = Field(default_factory=dict)
    formatting_constraints: Dict[str, Any] = Field(default_factory=dict)
    generation_parameters: Dict[str, Any] = Field(default_factory=dict)

class RewritePlan(BaseModel):
    """Plan for content rewriting and enhancement"""
    rewrite_strategies: Dict[str, Any] = Field(default_factory=dict)
    enhancement_rules: Dict[str, Any] = Field(default_factory=dict)
    rewrite_parameters: Dict[str, Any] = Field(default_factory=dict)

class SkillsPlan(BaseModel):
    """Plan for skill mapping and competency analysis"""
    skill_taxonomy: Dict[str, List[str]] = Field(default_factory=dict)
    competency_rules: Dict[str, Any] = Field(default_factory=dict)
    mapping_parameters: Dict[str, Any] = Field(default_factory=dict)

class SectionPlan(BaseModel):
    """Plan for resume section assembly and organization"""
    section_templates: Dict[str, Any] = Field(default_factory=dict)
    assembly_rules: Dict[str, Any] = Field(default_factory=dict)
    section_parameters: Dict[str, Any] = Field(default_factory=dict)

class JobWorkflowPlan(BaseModel):
    """Plan for job-specific workflow and processing"""
    job_analysis_rules: Dict[str, Any] = Field(default_factory=dict)
    workflow_steps: List[str] = Field(default_factory=list)
    job_parameters: Dict[str, Any] = Field(default_factory=dict)

class ATSPlan(BaseModel):
    """Plan for ATS compliance and optimization"""
    ats_rules: Dict[str, Any] = Field(default_factory=dict)
    compliance_parameters: Dict[str, Any] = Field(default_factory=dict)
    optimization_settings: Dict[str, Any] = Field(default_factory=dict)

class TemplatePlan(BaseModel):
    """Plan for template selection and application"""
    template_rules: Dict[str, Any] = Field(default_factory=dict)
    layout_parameters: Dict[str, Any] = Field(default_factory=dict)
    formatting_constraints: Dict[str, Any] = Field(default_factory=dict)

class FormattingPlan(BaseModel):
    """Plan for document formatting and presentation"""
    formatting_rules: Dict[str, Any] = Field(default_factory=dict)
    style_parameters: Dict[str, Any] = Field(default_factory=dict)
    presentation_settings: Dict[str, Any] = Field(default_factory=dict)

class SeniorityPlan(BaseModel):
    """Plan for seniority level adjustments and targeting"""
    seniority_rules: Dict[str, Any] = Field(default_factory=dict)
    level_parameters: Dict[str, Any] = Field(default_factory=dict)
    targeting_settings: Dict[str, Any] = Field(default_factory=dict)

class TonePlan(BaseModel):
    """Plan for tone and voice adjustments"""
    tone_rules: Dict[str, Any] = Field(default_factory=dict)
    voice_parameters: Dict[str, Any] = Field(default_factory=dict)
    style_adjustments: Dict[str, Any] = Field(default_factory=dict)

class ConstraintsPlan(BaseModel):
    """Plan for constraint enforcement and limits"""
    constraint_rules: Dict[str, Any] = Field(default_factory=dict)
    limit_parameters: Dict[str, Any] = Field(default_factory=dict)
    enforcement_settings: Dict[str, Any] = Field(default_factory=dict)

class ValidationPlan(BaseModel):
    """Plan for validation and quality assurance"""
    validation_rules: Dict[str, Any] = Field(default_factory=dict)
    quality_parameters: Dict[str, Any] = Field(default_factory=dict)
    validation_settings: Dict[str, Any] = Field(default_factory=dict)

class MissionPlan(BaseModel):
    """Plan for mission-specific requirements and objectives"""
    mission_requirements: Dict[str, Any] = Field(default_factory=dict)
    objective_parameters: Dict[str, Any] = Field(default_factory=dict)
    mission_settings: Dict[str, Any] = Field(default_factory=dict)

class CompleteRGPlan(BaseModel):
    """Complete Resume Generator Plan containing all sub-plans"""
    plan_id: str = Field(default_factory=lambda: f"rg_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # All sub-plans for each capability bucket
    routing: RoutingPlan = Field(default_factory=RoutingPlan)
    parameters: ParameterPlan = Field(default_factory=ParameterPlan)
    quant: QuantPlan = Field(default_factory=QuantPlan)
    bullets: BulletPlan = Field(default_factory=BulletPlan)
    rewrite: RewritePlan = Field(default_factory=RewritePlan)
    skills: SkillsPlan = Field(default_factory=SkillsPlan)
    sections: SectionPlan = Field(default_factory=SectionPlan)
    job_workflow: JobWorkflowPlan = Field(default_factory=JobWorkflowPlan)
    ats: ATSPlan = Field(default_factory=ATSPlan)
    templates: TemplatePlan = Field(default_factory=TemplatePlan)
    formatting: FormattingPlan = Field(default_factory=FormattingPlan)
    seniority: SeniorityPlan = Field(default_factory=SeniorityPlan)
    tone: TonePlan = Field(default_factory=TonePlan)
    constraints: ConstraintsPlan = Field(default_factory=ConstraintsPlan)
    validation: ValidationPlan = Field(default_factory=ValidationPlan)
    mission: MissionPlan = Field(default_factory=MissionPlan)
    
    # Execution metadata
    execution_order: List[str] = Field(default_factory=lambda: [
        "routing", "parameters", "job_workflow", "quant", "bullets", 
        "rewrite", "skills", "sections", "ats", "templates", 
        "formatting", "seniority", "tone", "constraints", "validation", "mission"
    ])
    
    def get_plan_summary(self) -> Dict[str, int]:
        """Get summary of plan complexity"""
        return {
            "routing_rules": len(self.routing.routing_decisions),
            "parameter_presets": len(self.parameters.parameter_values),
            "quant_rules": len(self.quant.scoring_rules),
            "bullet_rules": len(self.bullets.bullet_rules),
            "rewrite_strategies": len(self.rewrite.rewrite_strategies),
            "skill_taxonomies": len(self.skills.skill_taxonomy),
            "section_templates": len(self.sections.section_templates),
            "job_workflow_rules": len(self.job_workflow.job_analysis_rules),
            "ats_rules": len(self.ats.ats_rules),
            "template_rules": len(self.templates.template_rules),
            "formatting_rules": len(self.formatting.formatting_rules),
            "seniority_rules": len(self.seniority.seniority_rules),
            "tone_rules": len(self.tone.tone_rules),
            "constraint_rules": len(self.constraints.constraint_rules),
            "validation_rules": len(self.validation.validation_rules),
            "mission_requirements": len(self.mission.mission_requirements)
        }
