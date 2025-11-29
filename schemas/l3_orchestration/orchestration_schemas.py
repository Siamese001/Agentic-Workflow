#!/usr/bin/env python3
"""
Orchestration Schemas
Section 10: Schema Layer - Schemas for L3 orchestration operations
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from .base_schemas import BaseRequest, BaseResponse, ProcessingStatus

class OrchestrationType(str, Enum):
    """Orchestration type enumeration"""
    WORKFLOW = "workflow"
    PIPELINE = "pipeline"
    COORDINATION = "coordination"
    ROUTING = "routing"
    MONITORING = "monitoring"

class WorkflowStatus(str, Enum):
    """Workflow status enumeration"""
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecutionMode(str, Enum):
    """Execution mode enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    EVENT_DRIVEN = "event_driven"

class OrchestrationRequest(BaseRequest):
    """Request schema for orchestration operations"""
    orchestration_type: OrchestrationType = Field(..., description="Type of orchestration to perform")
    workflow_config: Dict[str, Any] = Field(..., description="Workflow configuration")
    execution_mode: ExecutionMode = Field(ExecutionMode.SEQUENTIAL, description="Execution mode")
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial input data")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Orchestration context")

class OrchestrationResponse(BaseResponse):
    """Response schema for orchestration operations"""
    orchestration_id: str = Field(..., description="Orchestration identifier")
    orchestration_type: OrchestrationType = Field(..., description="Type of orchestration performed")
    workflow_id: str = Field(..., description="Workflow identifier")
    status: WorkflowStatus = Field(..., description="Orchestration status")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Orchestration result data")
    execution_summary: Optional[Dict[str, Any]] = Field(None, description="Execution summary")

class WorkflowConfig(BaseModel):
    """Workflow configuration schema"""
    workflow_id: str = Field(..., description="Workflow identifier")
    workflow_name: str = Field(..., description="Workflow name")
    workflow_type: str = Field(..., description="Workflow type")
    steps: List[Dict[str, Any]] = Field(..., description="Workflow steps")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Step dependencies")
    execution_mode: ExecutionMode = Field(ExecutionMode.SEQUENTIAL, description="Execution mode")
    error_handling: str = Field("fail_fast", description="Error handling strategy")
    timeout_seconds: int = Field(3600, description="Workflow timeout in seconds")

class WorkflowStep(BaseModel):
    """Workflow step schema"""
    step_id: str = Field(..., description="Step identifier")
    step_name: str = Field(..., description="Step name")
    step_type: str = Field(..., description="Step type")
    executor: str = Field(..., description="Executor to use")
    input_mapping: Dict[str, str] = Field(default_factory=dict, description="Input data mapping")
    output_mapping: Dict[str, str] = Field(default_factory=dict, description="Output data mapping")
    retry_policy: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Retry policy")
    timeout_seconds: int = Field(300, description="Step timeout in seconds")

class PipelineConfig(BaseModel):
    """Pipeline configuration schema"""
    pipeline_id: str = Field(..., description="Pipeline identifier")
    pipeline_name: str = Field(..., description="Pipeline name")
    stages: List[Dict[str, Any]] = Field(..., description="Pipeline stages")
    data_flow: Dict[str, List[str]] = Field(default_factory=dict, description="Data flow configuration")
    stage_dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Stage dependencies")
    parallel_stages: Optional[List[str]] = Field(default_factory=list, description="Parallel executable stages")

class RoutingConfig(BaseModel):
    """Routing configuration schema"""
    routing_id: str = Field(..., description="Routing identifier")
    routing_rules: List[Dict[str, Any]] = Field(..., description="Routing rules")
    default_route: str = Field(..., description="Default route")
    fallback_routes: Optional[List[str]] = Field(default_factory=list, description="Fallback routes")
    load_balancing: str = Field("round_robin", description="Load balancing strategy")

class MonitoringConfig(BaseModel):
    """Monitoring configuration schema"""
    monitoring_id: str = Field(..., description="Monitoring identifier")
    metrics_to_track: List[str] = Field(default_factory=list, description="Metrics to track")
    alert_thresholds: Dict[str, Any] = Field(default_factory=dict, description="Alert thresholds")
    sampling_rate: float = Field(1.0, description="Metrics sampling rate")
    retention_policy: Dict[str, Any] = Field(default_factory=dict, description="Data retention policy")

# Re-export orchestration schemas
__all__ = [
    'OrchestrationRequest', 'OrchestrationResponse', 'WorkflowConfig', 'WorkflowStep',
    'PipelineConfig', 'RoutingConfig', 'MonitoringConfig',
    'OrchestrationType', 'WorkflowStatus', 'ExecutionMode'
]
