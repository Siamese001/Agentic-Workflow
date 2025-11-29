#!/usr/bin/env python3
"""
Planning Schemas
Section 10: Schema Layer - Schemas for L1 planning operations
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from .base_schemas import BaseRequest, BaseResponse, ProcessingStatus

class PlanType(str, Enum):
    """Plan type enumeration"""
    STRATEGY = "strategy"
    RESEARCH = "research"
    WORKFLOW = "workflow"
    OUTREACH = "outreach"
    RESUME = "resume"

class ComplexityLevel(str, Enum):
    """Complexity level enumeration"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    EXPERT = "expert"

class SeniorityLevel(str, Enum):
    """Seniority level enumeration"""
    ENTRY = "entry_level"
    JUNIOR = "junior"
    MID = "mid_level"
    SENIOR = "senior"
    EXECUTIVE = "executive"

class DomainType(str, Enum):
    """Domain type enumeration"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    GENERAL = "general"

class PlanRequest(BaseRequest):
    """Request schema for planning operations"""
    plan_type: PlanType = Field(..., description="Type of plan to generate")
    input_data: Dict[str, Any] = Field(..., description="Input data for planning")
    target_profile: Optional[str] = Field(None, description="Target profile description")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Planning constraints")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Planning preferences")

class PlanResponse(BaseResponse):
    """Response schema for planning operations"""
    plan_id: str = Field(..., description="Generated plan identifier")
    plan_type: PlanType = Field(..., description="Type of plan generated")
    plan_data: Dict[str, Any] = Field(..., description="Generated plan data")
    complexity: ComplexityLevel = Field(..., description="Plan complexity level")
    estimated_duration: Optional[str] = Field(None, description="Estimated execution duration")
    dependencies: Optional[List[str]] = Field(default_factory=list, description="Plan dependencies")

class StrategyPlan(BaseModel):
    """Strategy plan schema"""
    plan_id: str = Field(..., description="Strategy plan identifier")
    objective: str = Field(..., description="Strategic objective")
    approach: str = Field(..., description="Strategic approach")
    milestones: List[str] = Field(default_factory=list, description="Strategic milestones")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    timeline: Optional[str] = Field(None, description="Implementation timeline")
    resources: Optional[List[str]] = Field(default_factory=list, description="Required resources")

class ResearchPlan(BaseModel):
    """Research plan schema"""
    plan_id: str = Field(..., description="Research plan identifier")
    research_question: str = Field(..., description="Primary research question")
    methodology: str = Field(..., description="Research methodology")
    data_sources: List[str] = Field(default_factory=list, description="Data sources to query")
    search_strategy: str = Field(..., description="Search strategy")
    validation_criteria: List[str] = Field(default_factory=list, description="Validation criteria")
    expected_outcomes: List[str] = Field(default_factory=list, description="Expected research outcomes")

class WorkflowPlan(BaseModel):
    """Workflow plan schema"""
    plan_id: str = Field(..., description="Workflow plan identifier")
    workflow_type: str = Field(..., description="Type of workflow")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Step dependencies")
    parallel_execution: bool = Field(False, description="Allow parallel execution")
    error_handling: str = Field("fail_fast", description="Error handling strategy")

class ProfileAnalysis(BaseModel):
    """Profile analysis schema"""
    profile_id: str = Field(..., description="Profile identifier")
    complexity: ComplexityLevel = Field(..., description="Profile complexity")
    seniority: SeniorityLevel = Field(..., description="Profile seniority level")
    domain: DomainType = Field(..., description="Primary domain")
    skills: List[str] = Field(default_factory=list, description="Key skills")
    experience: Optional[Dict[str, Any]] = Field(None, description="Experience details")
    recommendations: List[str] = Field(default_factory=list, description="Profile recommendations")

# Re-export planning schemas
__all__ = [
    'PlanRequest', 'PlanResponse', 'StrategyPlan', 'ResearchPlan', 'WorkflowPlan',
    'ProfileAnalysis', 'PlanType', 'ComplexityLevel', 'SeniorityLevel', 'DomainType'
]
