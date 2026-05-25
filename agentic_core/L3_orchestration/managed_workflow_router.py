"""
DS-2: L3 MANAGED_WORKFLOW for apps_rg
Multi-step workflow orchestration via core L3 (not apps_rg).
"""
import logging
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

_logger = logging.getLogger(__name__)
_L5_CERT_REF_FAIL_CLOSED = os.getenv("L5_CERT_REF_FAIL_CLOSED", "0") == "1"


def _check_l5_cert_ref_l3(ref: str) -> None:
    """Fail-soft L5 cert ref verify at L3 entry per AG-W0-3=A_consume_entry."""
    try:
        from agentic_core.L5_safety.contracts.registry import verify_certification_ref
        valid = verify_certification_ref(ref)
    except Exception as exc:  # guardian: allow-log-and-swallow -- L5 registry must not crash L3 workflow; treat as unverified  # guardian: allow-broad-exception -- P1 ADG burndown
        _logger.warning("L5CertRefViolation stage=L3_entry registry_error=%s", exc)
        return
    if not valid:
        msg = "L5CertRefViolation stage=L3_entry ref=%r — missing or invalid l5_certification_ref"
        if _L5_CERT_REF_FAIL_CLOSED:
            raise ValueError(msg % (ref,))
        _logger.warning(msg, ref)


class WorkflowStage(Enum):
    """Stages in a managed workflow."""
    RESEARCH = "research"  # C0 grounding/retrieval
    BRIEF_SYNTHESIS = "brief_synthesis"  # L1 planning
    JD_ANALYSIS = "jd_analysis"  # L0 routing/c0 evidence
    CONTENT_GENERATION = "content_generation"  # L2 execution
    QUALITY_REVIEW = "quality_review"  # Exit evaluation
    HITL_REVIEW = "hitl_review"  # L5 checkpoint


class StageOutcome(Enum):
    """Outcome of a workflow stage."""
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    SKIP = "skip"
    HITL_REQUIRED = "hitl_required"


@dataclass(frozen=True)
class WorkflowStageConfig:
    """Configuration for a single workflow stage."""
    stage: WorkflowStage
    l3_required: bool = True
    c0_required: bool = False
    pa_required: bool = False
    max_retries: int = 2
    timeout_seconds: int = 120
    hitl_on_failure: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage.value,
            "l3_required": self.l3_required,
            "c0_required": self.c0_required,
            "pa_required": self.pa_required,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "hitl_on_failure": self.hitl_on_failure,
        }


@dataclass(frozen=True)
class StageExecution:
    """Execution record for a workflow stage."""
    stage: WorkflowStage
    outcome: StageOutcome
    started_at: str
    completed_at: str
    input_digest: str  # Hash of input for traceability
    output_digest: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage.value,
            "outcome": self.outcome.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }


@dataclass(frozen=True)
class ManagedWorkflow:
    """
    DS-2: Managed Workflow definition.
    
    This is the L3-orchestrated multi-step workflow for apps_rg.
    apps_rg remains ingress-only: it SUBMITS to this workflow,
    it does not orchestrate it.
    """
    workflow_id: str
    workflow_type: str = "resume_generation"  # or other domain workflows
    
    # Stage pipeline (ordered)
    stages: List[WorkflowStageConfig] = field(default_factory=list)
    
    # UWG state integration
    uwg_state_key_prefix: str = "workflow"
    persist_intermediate_results: bool = True
    
    # Governance
    requires_approval: bool = False  # Pre-execution approval
    requires_exit_eval: bool = True  # Post-execution Exit evaluation
    
    def __post_init__(self):
        # Default stage pipeline if not specified
        if not self.stages:
            default_stages = [
                WorkflowStageConfig(WorkflowStage.RESEARCH, c0_required=True),
                WorkflowStageConfig(WorkflowStage.BRIEF_SYNTHESIS, l3_required=True),
                WorkflowStageConfig(WorkflowStage.JD_ANALYSIS, c0_required=True),
                WorkflowStageConfig(WorkflowStage.CONTENT_GENERATION, l3_required=True),
                WorkflowStageConfig(WorkflowStage.QUALITY_REVIEW),
            ]
            # Use object.__setattr__ because frozen
            object.__setattr__(self, 'stages', default_stages)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type,
            "stages": [s.to_dict() for s in self.stages],
            "uwg_state_key_prefix": self.uwg_state_key_prefix,
            "persist_intermediate_results": self.persist_intermediate_results,
            "requires_approval": self.requires_approval,
            "requires_exit_eval": self.requires_exit_eval,
        }


@dataclass(frozen=True)
class WorkflowExecution:
    """Execution instance of a managed workflow."""
    execution_id: str
    workflow: ManagedWorkflow
    ingress_payload_digest: str  # Reference to AppsRgIngressPayload
    
    # Execution state
    status: str = "pending"  # pending, running, completed, failed
    current_stage_index: int = 0
    stage_executions: List[StageExecution] = field(default_factory=list)
    
    # Timing
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Final output
    final_output_digest: Optional[str] = None
    exit_evaluation_passed: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow.workflow_id,
            "ingress_payload_digest": self.ingress_payload_digest,
            "status": self.status,
            "current_stage_index": self.current_stage_index,
            "stage_executions": [se.to_dict() for se in self.stage_executions],
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "final_output_digest": self.final_output_digest,
            "exit_evaluation_passed": self.exit_evaluation_passed,
        }


class ManagedWorkflowEngine:
    """
    DS-2: L3 Managed Workflow Engine.
    
    This is the core orchestration engine. It lives in L3 (orchestration),
    NOT in apps_rg. apps_rg submits requests to this engine via the
    AppIngressRunner.
    """
    
    def __init__(self):
        self._workflows: Dict[str, ManagedWorkflow] = {}
        self._executions: Dict[str, WorkflowExecution] = {}
        self._stage_handlers: Dict[WorkflowStage, Callable] = {}
        
        # Register default stage handlers
        from .workflow_stage_handlers import STAGE_HANDLERS
        self._stage_handlers.update(STAGE_HANDLERS)
    
    def register_workflow(self, workflow: ManagedWorkflow):
        """Register a workflow definition."""
        self._workflows[workflow.workflow_id] = workflow
    
    def register_stage_handler(self, stage: WorkflowStage, handler: Callable):
        """Register a handler for a workflow stage."""
        self._stage_handlers[stage] = handler
    
    def create_execution(
        self,
        workflow_id: str,
        ingress_payload: Any,
    ) -> Optional[WorkflowExecution]:
        """
        Create a new workflow execution.
        
        This is called by AppIngressRunner when a multi-step workflow is needed.
        """
        import hashlib
        import json
        
        # L3 entry: verify upstream l5_certification_ref (AG-W0-3)
        _check_l5_cert_ref_l3(
            getattr(ingress_payload, "l5_certification_ref", "")
            if not isinstance(ingress_payload, dict)
            else ingress_payload.get("l5_certification_ref", "")
        )

        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return None
        
        # Compute payload digest
        payload_str = json.dumps(ingress_payload, default=str)
        payload_digest = hashlib.sha256(payload_str.encode()).hexdigest()[:16]
        
        execution_id = f"{workflow_id}_{payload_digest}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow=workflow,
            ingress_payload_digest=payload_digest,
        )
        
        self._executions[execution_id] = execution
        return execution
    
    def execute_stage(self, execution_id: str) -> bool:
        """
        Execute the current stage of a workflow.
        
        Returns True if more stages remain, False if complete.
        """
        execution = self._executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status in ["completed", "failed"]:
            return False
        
        # Get current stage
        if execution.current_stage_index >= len(execution.workflow.stages):
            # All stages complete
            object.__setattr__(execution, 'status', 'completed')
            object.__setattr__(execution, 'completed_at', datetime.utcnow().isoformat())
            return False
        
        stage_config = execution.workflow.stages[execution.current_stage_index]
        stage_handler = self._stage_handlers.get(stage_config.stage)
        
        if not stage_handler:
            # Skip stage with no handler
            object.__setattr__(execution, 'current_stage_index', execution.current_stage_index + 1)
            return execution.current_stage_index < len(execution.workflow.stages)
        
        # Execute stage (simplified - real implementation would be async)
        try:
            result = stage_handler(execution)
            
            # Record execution
            stage_exec = StageExecution(
                stage=stage_config.stage,
                outcome=StageOutcome.SUCCESS,
                started_at=datetime.utcnow().isoformat(),
                completed_at=datetime.utcnow().isoformat(),
                input_digest=execution.ingress_payload_digest,
            )
            
            new_executions = list(execution.stage_executions) + [stage_exec]
            object.__setattr__(execution, 'stage_executions', new_executions)
            object.__setattr__(execution, 'current_stage_index', execution.current_stage_index + 1)
            
        except Exception as e:  # guardian: allow-broad-exception -- P1 ADG burndown
            # Stage failed
            stage_exec = StageExecution(
                stage=stage_config.stage,
                outcome=StageOutcome.FAILURE,
                started_at=datetime.utcnow().isoformat(),
                completed_at=datetime.utcnow().isoformat(),
                input_digest=execution.ingress_payload_digest,
                error_message=str(e),
            )
            
            new_executions = list(execution.stage_executions) + [stage_exec]
            object.__setattr__(execution, 'stage_executions', new_executions)
            object.__setattr__(execution, 'status', 'failed')
            
            if stage_config.hitl_on_failure:
                object.__setattr__(execution, 'status', 'hitl_required')
            
            return False
        
        # Check if complete
        if execution.current_stage_index >= len(execution.workflow.stages):
            object.__setattr__(execution, 'status', 'completed')
            object.__setattr__(execution, 'completed_at', datetime.utcnow().isoformat())
            return False
        
        return True
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution status."""
        return self._executions.get(execution_id)


# Pre-defined workflow: Resume Generation
RESUME_GENERATION_WORKFLOW = ManagedWorkflow(
    workflow_id="resume_generation_managed",
    workflow_type="resume_generation",
    stages=[
        WorkflowStageConfig(WorkflowStage.RESEARCH, c0_required=True, max_retries=1),
        WorkflowStageConfig(WorkflowStage.BRIEF_SYNTHESIS, l3_required=True),
        WorkflowStageConfig(WorkflowStage.JD_ANALYSIS, c0_required=True),
        WorkflowStageConfig(WorkflowStage.CONTENT_GENERATION, l3_required=True, max_retries=2),
        WorkflowStageConfig(WorkflowStage.QUALITY_REVIEW),
    ],
    requires_exit_eval=True,
)
