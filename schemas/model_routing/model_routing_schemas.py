#!/usr/bin/env python3
"""
Model Routing Schemas
Section 10: Schema Layer - Schemas for model routing operations
"""

from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..core.base_schemas import BaseRequest, BaseResponse

class ProviderType(str, Enum):
    """Available model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    AZURE = "azure"
    AWS = "aws"
    LOCAL = "local"

class CostTier(str, Enum):
    """Model cost tiers."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PREMIUM = "premium"

class TaskType(str, Enum):
    """Task types for routing decisions."""
    GENERATION = "generation"
    ANALYSIS = "analysis"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    REASONING = "reasoning"
    CODE = "code"

class ModelChoice(BaseModel):
    """Choice of model for execution."""
    provider: ProviderType = Field(..., description="Model provider")
    model_name: str = Field(..., description="Model name")
    cost_tier: CostTier = Field(CostTier.MEDIUM, description="Cost tier")
    estimated_cost: float = Field(0.001, description="Estimated cost per request")
    latency_ms: int = Field(500, description="Expected latency in milliseconds")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens supported")
    temperature_range: Tuple[float, float] = Field((0.0, 1.0), description="Temperature range")
    capabilities: List[str] = Field(default_factory=list, description="Model capabilities")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class RoutingContext(BaseModel):
    """Context for model routing decisions."""
    agent_id: str = Field(..., description="Agent identifier")
    task_type: TaskType = Field(..., description="Type of task")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    execution_profile: Optional[Dict[str, Any]] = Field(None, description="Execution profile")
    budget_constraints: Optional[Dict[str, Any]] = Field(None, description="Budget constraints")
    performance_requirements: Optional[Dict[str, Any]] = Field(None, description="Performance requirements")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")

class RoutingRequest(BaseRequest):
    """Request schema for model routing operations."""
    task_type: TaskType = Field(..., description="Type of task")
    agent_id: str = Field(..., description="Agent identifier")
    requested_model: Optional[str] = Field(None, description="Specific model requested")
    execution_profile: Optional[Dict[str, Any]] = Field(None, description="Execution profile")
    budget_constraints: Optional[Dict[str, Any]] = Field(None, description="Budget constraints")
    performance_requirements: Optional[Dict[str, Any]] = Field(None, description="Performance requirements")
    routing_context: Optional[RoutingContext] = Field(None, description="Routing context")

class RoutingResponse(BaseResponse):
    """Response schema for model routing operations."""
    routing_id: str = Field(..., description="Routing identifier")
    model_choice: ModelChoice = Field(..., description="Selected model")
    routing_reason: str = Field(..., description="Reason for model selection")
    estimated_cost: float = Field(..., description="Estimated cost for request")
    estimated_latency: int = Field(..., description="Estimated latency in milliseconds")
    confidence_score: float = Field(..., description="Routing confidence score")

class BudgetProfile(BaseModel):
    """Budget profile for routing constraints."""
    profile_id: str = Field(..., description="Profile identifier")
    max_cost_per_request: float = Field(..., description="Maximum cost per request")
    max_cost_per_session: float = Field(..., description="Maximum cost per session")
    max_cost_tier: CostTier = Field(CostTier.MEDIUM, description="Maximum cost tier allowed")
    daily_budget_limit: float = Field(..., description="Daily budget limit")
    monthly_budget_limit: float = Field(..., description="Monthly budget limit")
    enabled_providers: List[ProviderType] = Field(default_factory=list, description="Enabled providers")
    blocked_models: List[str] = Field(default_factory=list, description="Blocked models")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional profile metadata")

class PerformanceProfile(BaseModel):
    """Performance profile for routing requirements."""
    profile_id: str = Field(..., description="Profile identifier")
    max_latency_ms: int = Field(..., description="Maximum acceptable latency")
    min_accuracy: Optional[float] = Field(None, description="Minimum accuracy requirement")
    throughput_requirement: Optional[float] = Field(None, description="Required throughput")
    priority_level: int = Field(1, description="Priority level (1-10)")
    real_time_required: bool = Field(False, description="Real-time processing required")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="Retry policy")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional profile metadata")

class RoutingPolicy(BaseModel):
    """Routing policy configuration."""
    policy_id: str = Field(..., description="Policy identifier")
    policy_name: str = Field(..., description="Policy name")
    task_types: List[TaskType] = Field(..., description="Applicable task types")
    routing_rules: List[Dict[str, Any]] = Field(..., description="Routing rules")
    fallback_models: List[ModelChoice] = Field(default_factory=list, description="Fallback models")
    budget_profile: Optional[BudgetProfile] = Field(None, description="Budget constraints")
    performance_profile: Optional[PerformanceProfile] = Field(None, description="Performance requirements")
    enabled: bool = Field(True, description="Policy enabled status")
    priority: int = Field(1, description="Policy priority")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional policy metadata")

class RoutingMetrics(BaseModel):
    """Routing performance metrics."""
    routing_id: str = Field(..., description="Routing identifier")
    timestamp: datetime = Field(..., description="Metrics timestamp")
    total_requests: int = Field(..., description="Total requests routed")
    successful_requests: int = Field(..., description="Successful requests")
    failed_requests: int = Field(..., description="Failed requests")
    average_latency_ms: float = Field(..., description="Average latency")
    total_cost: float = Field(..., description="Total cost incurred")
    model_usage: Dict[str, int] = Field(default_factory=dict, description="Model usage counts")
    provider_usage: Dict[str, int] = Field(default_factory=dict, description="Provider usage counts")
    error_types: Dict[str, int] = Field(default_factory=dict, description="Error type counts")

class RoutingMetricsRequest(BaseRequest):
    """Request schema for routing metrics operations."""
    routing_id: Optional[str] = Field(None, description="Specific routing identifier")
    time_range: Optional[Dict[str, datetime]] = Field(None, description="Time range for metrics")
    aggregation_level: str = Field("summary", description="Aggregation level")
    include_costs: bool = Field(True, description="Include cost metrics")
    include_performance: bool = Field(True, description="Include performance metrics")

class RoutingMetricsResponse(BaseResponse):
    """Response schema for routing metrics operations."""
    metrics: List[RoutingMetrics] = Field(..., description="Routing metrics data")
    summary: Dict[str, Any] = Field(..., description="Metrics summary")
    time_range: Dict[str, datetime] = Field(..., description="Time range covered")
    total_requests: int = Field(..., description="Total requests in time range")
    total_cost: float = Field(..., description="Total cost in time range")
