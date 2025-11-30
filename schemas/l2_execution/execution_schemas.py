#!/usr/bin/env python3
"""
Execution Schemas
Section 10: Schema Layer - Schemas for L2 execution operations
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from .base_schemas import BaseRequest, BaseResponse, ProcessingStatus

class ExecutionType(str, Enum):
    """Execution type enumeration"""
    RESEARCH = "research"
    DRAFT = "draft"
    REGENERATE = "regenerate"
    VALIDATE = "validate"
    CTA = "cta"
    ASSEMBLY = "assembly"
    OUTREACH = "outreach"
    RESUME = "resume"

class ToolStatus(str, Enum):
    """Tool execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ExecutionRequest(BaseRequest):
    """Request schema for execution operations"""
    execution_type: ExecutionType = Field(..., description="Type of execution to perform")
    plan_data: Dict[str, Any] = Field(..., description="Plan data to execute")
    tool_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tool configuration")
    execution_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution context")
    timeout_seconds: int = Field(300, description="Execution timeout in seconds")

class ExecutionResponse(BaseResponse):
    """Response schema for execution operations"""
    execution_id: str = Field(..., description="Execution identifier")
    execution_type: ExecutionType = Field(..., description="Type of execution performed")
    status: ProcessingStatus = Field(..., description="Execution status")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Execution result data")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    tools_used: Optional[List[str]] = Field(default_factory=list, description="Tools used in execution")

class ToolContract(BaseModel):
    """Tool contract schema for execution layer"""
    tool_name: str = Field(..., description="Tool name")
    tool_version: str = Field(..., description="Tool version")
    input_schema: Dict[str, Any] = Field(..., description="Input schema definition")
    output_schema: Dict[str, Any] = Field(..., description="Output schema definition")
    timeout_seconds: int = Field(300, description="Tool timeout in seconds")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="Retry policy configuration")
    requirements: Optional[List[str]] = Field(default_factory=list, description="Tool requirements")

class ToolExecution(BaseModel):
    """Tool execution schema"""
    execution_id: str = Field(..., description="Execution identifier")
    tool_name: str = Field(..., description="Tool being executed")
    input_data: Dict[str, Any] = Field(..., description="Input data for tool")
    status: ToolStatus = Field(..., description="Tool execution status")
    start_time: datetime = Field(default_factory=datetime.now, description="Execution start time")
    end_time: Optional[datetime] = Field(None, description="Execution end time")
    result: Optional[Dict[str, Any]] = Field(None, description="Tool execution result")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class ResearchExecution(BaseModel):
    """Research execution schema"""
    execution_id: str = Field(..., description="Research execution identifier")
    research_query: str = Field(..., description="Research query to execute")
    data_sources: List[str] = Field(default_factory=list, description="Data sources to query")
    search_strategy: str = Field(..., description="Search strategy")
    max_results: int = Field(10, description="Maximum results to return")
    validation_required: bool = Field(True, description="Whether validation is required")

class DraftExecution(BaseModel):
    """Draft execution schema"""
    execution_id: str = Field(..., description="Draft execution identifier")
    draft_type: str = Field(..., description="Type of draft to generate")
    input_data: Dict[str, Any] = Field(..., description="Input data for draft generation")
    template: Optional[str] = Field(None, description="Draft template to use")
    style_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Style preferences")

class ValidationExecution(BaseModel):
    """Validation execution schema"""
    execution_id: str = Field(..., description="Validation execution identifier")
    content_to_validate: Dict[str, Any] = Field(..., description="Content to validate")
    validation_rules: List[str] = Field(default_factory=list, description="Validation rules to apply")
    strict_mode: bool = Field(False, description="Enable strict validation mode")
    error_threshold: float = Field(0.1, description="Error threshold for validation")

# Re-export execution schemas
__all__ = [
    'ExecutionRequest', 'ExecutionResponse', 'ToolContract', 'ToolExecution',
    'ResearchExecution', 'DraftExecution', 'ValidationExecution',
    'ExecutionType', 'ToolStatus'
]





