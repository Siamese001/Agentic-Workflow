#!/usr/bin/env python3
"""
L4 State Layer - Resume Generator State Management
Maintains execution state and atomic lineage for all steps
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

import sys
sys.path.append(r'C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\RG_capabilities')
from RG_capabilities.rg_atomic_spec import ATOMIC_RG_SPEC

class K1State(BaseModel):
    """State for K1 Extract step"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending"
    extracted_resume: Optional[Dict[str, Any]] = None
    extracted_job: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class K2State(BaseModel):
    """State for K2 Clean step"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending"
    cleaned_resume: Optional[Dict[str, Any]] = None
    cleaned_job: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class K3State(BaseModel):
    """State for K3 Quant step"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending"
    job_alignment_scores: Optional[Dict[str, Any]] = None
    resume_quality_metrics: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class K4State(BaseModel):
    """State for K4 Rewrite step (NO-OP)"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending_no_op"
    rewritten_content: Optional[Dict[str, Any]] = None
    enhancements_applied: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class K5State(BaseModel):
    """State for K5 SkillMap step (NO-OP)"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending_no_op"
    skill_mapping: Optional[Dict[str, Any]] = None
    competency_scores: Dict[str, float] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class K6State(BaseModel):
    """State for K6 Section Assembly step (NO-OP)"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending_no_op"
    assembled_sections: Optional[Dict[str, Any]] = None
    section_order: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class K7State(BaseModel):
    """State for K7 Format step"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending"
    formatted_resume: Optional[Dict[str, Any]] = None
    formatting_metadata: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class K8State(BaseModel):
    """State for K8 Validation step"""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    status: str = "pending"
    validation_results: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0
    issues_found: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RGWorkflowState(BaseModel):
    """Complete workflow state tracking all K1-K8 steps"""
    
    # Workflow metadata
    workflow_id: str = Field(default_factory=lambda: f"rg_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = "initialized"
    
    # Input tracking
    input_resume_hash: Optional[str] = None
    input_job_hash: Optional[str] = None
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # Step states (all 16 buckets tracked)
    k1_state: K1State = Field(default_factory=K1State)
    k2_state: K2State = Field(default_factory=K2State)
    k3_state: K3State = Field(default_factory=K3State)
    k4_state: K4State = Field(default_factory=K4State)
    k5_state: K5State = Field(default_factory=K5State)
    k6_state: K6State = Field(default_factory=K6State)
    k7_state: K7State = Field(default_factory=K7State)
    k8_state: K8State = Field(default_factory=K8State)
    
    # Atomic lineage tracking
    step_lineage: List[str] = Field(default_factory=list)
    data_provenance: Dict[str, str] = Field(default_factory=dict)
    
    # Execution metrics
    total_execution_time: float = 0.0
    step_completion_times: Dict[str, float] = Field(default_factory=dict)
    
    # Error tracking
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    retry_attempts: Dict[str, int] = Field(default_factory=dict)
    
    def update_step_state(self, step_name: str, step_data: Dict[str, Any]) -> None:
        """Update state for a specific step"""
        
        self.updated_at = datetime.now()
        self.step_lineage.append(step_name)
        
        if step_name == "k1":
            self.k1_state.status = step_data.get("status", "completed")
            self.k1_state.extracted_resume = step_data.get("extracted_data", {}).get("resume")
            self.k1_state.extracted_job = step_data.get("extracted_data", {}).get("job")
            self.k1_state.metadata = step_data.get("metadata", {})
            
        elif step_name == "k2":
            self.k2_state.status = step_data.get("status", "completed")
            self.k2_state.cleaned_resume = step_data.get("cleaned_data", {}).get("resume")
            self.k2_state.cleaned_job = step_data.get("cleaned_data", {}).get("job")
            self.k2_state.metadata = step_data.get("metadata", {})
            
        elif step_name == "k3":
            self.k3_state.status = step_data.get("status", "completed")
            quant_results = step_data.get("quantification_results", {})
            self.k3_state.job_alignment_scores = quant_results.get("job_alignment")
            self.k3_state.resume_quality_metrics = quant_results.get("resume_quality")
            self.k3_state.metadata = step_data.get("metadata", {})
            
        elif step_name == "k4":
            self.k4_state.status = step_data.get("status", "completed_no_op")
            self.k4_state.rewritten_content = step_data.get("rewritten_data", {})
            self.k4_state.enhancements_applied = step_data.get("rewritten_data", {}).get("enhancements_applied", [])
            self.k4_state.metadata = step_data.get("metadata", {})
            
        elif step_name == "k5":
            self.k5_state.status = step_data.get("status", "completed_no_op")
            skill_results = step_data.get("skill_mapping_results", {})
            self.k5_state.skill_mapping = skill_results.get("skill_mapping", {})
            self.k5_state.metadata = step_data.get("metadata", {})
            
        elif step_name == "k6":
            self.k6_state.status = step_data.get("status", "completed_no_op")
            assembly_results = step_data.get("assembly_results", {})
            self.k6_state.assembled_sections = assembly_results.get("assembled_sections", {}).get("sections")
            self.k6_state.metadata = step_data.get("metadata", {})
            
        elif step_name == "k7":
            self.k7_state.status = step_data.get("status", "completed")
            self.k7_state.formatted_resume = step_data.get("formatted_results", {})
            self.k7_state.formatting_metadata = step_data.get("formatted_results", {}).get("formatting_metadata")
            self.k7_state.metadata = step_data.get("metadata", {})
            
        elif step_name == "k8":
            self.k8_state.status = step_data.get("status", "completed")
            validation_results = step_data.get("validation_results", {})
            self.k8_state.validation_results = validation_results
            self.k8_state.quality_score = validation_results.get("quality_score", 0.0)
            self.k8_state.issues_found = validation_results.get("issues_found", [])
            self.k8_state.metadata = step_data.get("metadata", {})
        
        # Track execution time
        execution_meta = step_data.get("execution_metadata", {})
        if execution_meta.get("execution_time"):
            self.step_completion_times[step_name] = execution_meta["execution_time"]
        
        # Track retry attempts
        if execution_meta.get("attempt", 1) > 1:
            self.retry_attempts[step_name] = execution_meta["attempt"]
    
    def record_error(self, step_name: str, error: str) -> None:
        """Record an error for a specific step"""
        error_record = {
            "step": step_name,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.errors.append(error_record)
        self.status = "error"
    
    def get_step_status(self, step_name: str) -> str:
        """Get status of a specific step"""
        step_states = {
            "k1": self.k1_state.status,
            "k2": self.k2_state.status,
            "k3": self.k3_state.status,
            "k4": self.k4_state.status,
            "k5": self.k5_state.status,
            "k6": self.k6_state.status,
            "k7": self.k7_state.status,
            "k8": self.k8_state.status
        }
        return step_states.get(step_name, "unknown")
    
    def is_workflow_complete(self) -> bool:
        """Check if all steps are completed"""
        required_steps = ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8"]
        
        for step in required_steps:
            status = self.get_step_status(step)
            if status not in ["completed", "completed_no_op"]:
                return False
        
        return True
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total_execution_time": self.total_execution_time,
            "steps_completed": len([s for s in [self.get_step_status(step) for step in ["k1", "k2", "k3", "k4", "k5", "k6", "k7", "k8"]] if s in ["completed", "completed_no_op"]]),
            "total_errors": len(self.errors),
            "retry_attempts": dict(self.retry_attempts),
            "final_quality_score": self.k8_state.quality_score,
            "step_lineage": self.step_lineage
        }
    
    def get_atomic_lineage(self) -> Dict[str, Any]:
        """Get atomic lineage information for all steps"""
        lineage = {
            "workflow_id": self.workflow_id,
            "step_execution_order": self.step_lineage,
            "data_provenance": self.data_provenance,
            "step_timestamps": {
                "k1": self.k1_state.timestamp.isoformat(),
                "k2": self.k2_state.timestamp.isoformat(),
                "k3": self.k3_state.timestamp.isoformat(),
                "k4": self.k4_state.timestamp.isoformat(),
                "k5": self.k5_state.timestamp.isoformat(),
                "k6": self.k6_state.timestamp.isoformat(),
                "k7": self.k7_state.timestamp.isoformat(),
                "k8": self.k8_state.timestamp.isoformat()
            },
            "atomic_bucket_tracking": {
                "routing": len(ATOMIC_RG_SPEC.get("routing", {})),
                "parameters": len(ATOMIC_RG_SPEC.get("parameters", {})),
                "quant": len(ATOMIC_RG_SPEC.get("quant", {})),
                "bullets": len(ATOMIC_RG_SPEC.get("bullets", {})),
                "rewrite": len(ATOMIC_RG_SPEC.get("rewrite", {})),
                "skills": len(ATOMIC_RG_SPEC.get("skills", {})),
                "sections": len(ATOMIC_RG_SPEC.get("sections", {})),
                "job_workflow": len(ATOMIC_RG_SPEC.get("job_workflow", {})),
                "ats": len(ATOMIC_RG_SPEC.get("ats", {})),
                "templates": len(ATOMIC_RG_SPEC.get("templates", {})),
                "formatting": len(ATOMIC_RG_SPEC.get("formatting", {})),
                "seniority": len(ATOMIC_RG_SPEC.get("seniority", {})),
                "tone": len(ATOMIC_RG_SPEC.get("tone", {})),
                "constraints": len(ATOMIC_RG_SPEC.get("constraints", {})),
                "validators": len(ATOMIC_RG_SPEC.get("validators", {})),
                "mission": len(ATOMIC_RG_SPEC.get("mission", {}))
            }
        }
        
        return lineage

class RGStateManager:
    """State manager for Resume Generator workflows"""
    
    def __init__(self):
        self.active_states: Dict[str, RGWorkflowState] = {}
        self.atomic_spec = ATOMIC_RG_SPEC
    
    def create_workflow_state(self, 
                             workflow_id: Optional[str] = None,
                             input_resume_hash: Optional[str] = None,
                             input_job_hash: Optional[str] = None,
                             input_parameters: Optional[Dict[str, Any]] = None) -> RGWorkflowState:
        """Create a new workflow state"""
        
        if workflow_id:
            state = RGWorkflowState(workflow_id=workflow_id)
        else:
            state = RGWorkflowState()
        
        state.input_resume_hash = input_resume_hash
        state.input_job_hash = input_job_hash
        if input_parameters:
            state.input_parameters = input_parameters
        
        self.active_states[state.workflow_id] = state
        return state
    
    def get_workflow_state(self, workflow_id: str) -> Optional[RGWorkflowState]:
        """Get existing workflow state"""
        return self.active_states.get(workflow_id)
    
    def update_workflow_state(self, workflow_id: str, step_name: str, step_data: Dict[str, Any]) -> None:
        """Update workflow state with step results"""
        state = self.get_workflow_state(workflow_id)
        if state:
            state.update_step_state(step_name, step_data)
    
    def record_workflow_error(self, workflow_id: str, step_name: str, error: str) -> None:
        """Record error in workflow state"""
        state = self.get_workflow_state(workflow_id)
        if state:
            state.record_error(step_name, error)
    
    def complete_workflow(self, workflow_id: str) -> Optional[RGWorkflowState]:
        """Mark workflow as completed"""
        state = self.get_workflow_state(workflow_id)
        if state:
            state.status = "completed"
            state.updated_at = datetime.now()
        return state
    
    def cleanup_workflow(self, workflow_id: str) -> None:
        """Remove workflow state from active states"""
        if workflow_id in self.active_states:
            del self.active_states[workflow_id]
    
    def get_all_active_workflows(self) -> List[str]:
        """Get list of all active workflow IDs"""
        return list(self.active_states.keys())
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """Get statistics about all workflow states"""
        total_workflows = len(self.active_states)
        completed_workflows = len([s for s in self.active_states.values() if s.is_workflow_complete()])
        error_workflows = len([s for s in self.active_states.values() if s.status == "error"])
        
        return {
            "total_active_workflows": total_workflows,
            "completed_workflows": completed_workflows,
            "error_workflows": error_workflows,
            "success_rate": completed_workflows / total_workflows if total_workflows > 0 else 0.0,
            "atomic_spec_buckets": len(self.atomic_spec)
        }
