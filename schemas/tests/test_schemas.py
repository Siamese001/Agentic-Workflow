#!/usr/bin/env python3
"""
Test Framework Schemas
Section 10: Schema Layer - Schemas for test framework operations
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..core.base_schemas import BaseRequest, BaseResponse

class TestType(str, Enum):
    """Types of tests."""
    UNIT = "unit"
    INTEGRATION = "integration"
    END_TO_END = "end_to_end"
    PERFORMANCE = "performance"
    STRESS = "stress"
    REGRESSION = "regression"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    VALIDATION = "validation"

class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    ERROR = "error"

class TestLevel(str, Enum):
    """Test levels for L5 architecture."""
    L1_PLANNING = "l1_planning"
    L2_EXECUTION = "l2_execution"
    L3_ORCHESTRATION = "l3_orchestration"
    L4_MEMORY_STATE = "l4_memory_state"
    L5_SAFETY = "l5_safety"
    CROSS_LAYER = "cross_layer"
    SYSTEM = "system"

class TestPriority(str, Enum):
    """Test priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TestCase(BaseModel):
    """Test case definition."""
    test_id: str = Field(..., description="Test case identifier")
    test_name: str = Field(..., description="Test case name")
    test_type: TestType = Field(..., description="Test type")
    test_level: TestLevel = Field(..., description="Test level")
    description: str = Field(..., description="Test description")
    priority: TestPriority = Field(TestPriority.MEDIUM, description="Test priority")
    tags: List[str] = Field(default_factory=list, description="Test tags")
    dependencies: List[str] = Field(default_factory=list, description="Test dependencies")
    timeout_seconds: int = Field(300, description="Test timeout in seconds")
    retry_count: int = Field(0, description="Number of retries on failure")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional test metadata")

class TestExecution(BaseModel):
    """Test execution record."""
    execution_id: str = Field(..., description="Execution identifier")
    test_id: str = Field(..., description="Test case identifier")
    test_name: str = Field(..., description="Test case name")
    status: TestStatus = Field(TestStatus.PENDING, description="Execution status")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    environment: str = Field(..., description="Test environment")
    executor: str = Field(..., description="Test executor")
    test_data: Dict[str, Any] = Field(default_factory=dict, description="Test data used")
    results: Dict[str, Any] = Field(default_factory=dict, description="Test results")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    stack_trace: Optional[str] = Field(None, description="Stack trace if error")
    logs: List[str] = Field(default_factory=list, description="Execution logs")
    artifacts: List[str] = Field(default_factory=list, description="Generated artifacts")

class TestSuite(BaseModel):
    """Test suite definition."""
    suite_id: str = Field(..., description="Suite identifier")
    suite_name: str = Field(..., description="Suite name")
    description: str = Field(..., description="Suite description")
    test_cases: List[str] = Field(..., description="Test case IDs")
    test_level: TestLevel = Field(..., description="Suite test level")
    setup_commands: List[str] = Field(default_factory=list, description="Setup commands")
    teardown_commands: List[str] = Field(default_factory=list, description="Teardown commands")
    parallel_execution: bool = Field(False, description="Enable parallel execution")
    max_parallel_tests: int = Field(1, description="Maximum parallel tests")
    timeout_minutes: int = Field(60, description="Suite timeout in minutes")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional suite metadata")

class TestEnvironment(BaseModel):
    """Test environment configuration."""
    environment_id: str = Field(..., description="Environment identifier")
    environment_name: str = Field(..., description="Environment name")
    environment_type: str = Field(..., description="Environment type")
    configuration: Dict[str, Any] = Field(..., description="Environment configuration")
    services: List[Dict[str, Any]] = Field(default_factory=list, description="Available services")
    databases: List[Dict[str, Any]] = Field(default_factory=list, description="Database connections")
    api_endpoints: Dict[str, str] = Field(default_factory=dict, description="API endpoints")
    credentials: Dict[str, str] = Field(default_factory=dict, description="Environment credentials")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")

class TestReport(BaseModel):
    """Test execution report."""
    report_id: str = Field(..., description="Report identifier")
    suite_id: Optional[str] = Field(None, description="Suite identifier")
    test_level: TestLevel = Field(..., description="Test level")
    execution_summary: Dict[str, Any] = Field(..., description="Execution summary")
    test_results: List[TestExecution] = Field(..., description="Test execution results")
    passed_tests: int = Field(..., description="Number of passed tests")
    failed_tests: int = Field(..., description="Number of failed tests")
    skipped_tests: int = Field(..., description="Number of skipped tests")
    total_tests: int = Field(..., description="Total number of tests")
    success_rate: float = Field(..., description="Success rate percentage")
    total_duration_ms: int = Field(..., description="Total execution duration")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")
    environment: str = Field(..., description="Test environment")

class TestMetrics(BaseModel):
    """Test performance metrics."""
    metric_id: str = Field(..., description="Metric identifier")
    test_id: str = Field(..., description="Test identifier")
    test_name: str = Field(..., description="Test name")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")
    memory_usage_mb: float = Field(..., description="Memory usage in MB")
    cpu_usage_percent: float = Field(..., description="CPU usage percentage")
    network_io_mb: float = Field(..., description="Network I/O in MB")
    disk_io_mb: float = Field(..., description="Disk I/O in MB")
    timestamp: datetime = Field(..., description="Metric collection timestamp")
    environment: str = Field(..., description="Test environment")
    additional_metrics: Dict[str, float] = Field(default_factory=dict, description="Additional metrics")

class TestRequest(BaseRequest):
    """Request schema for test operations."""
    test_type: TestType = Field(..., description="Test type to execute")
    test_level: TestLevel = Field(..., description="Test level")
    test_ids: Optional[List[str]] = Field(None, description="Specific test IDs to run")
    suite_id: Optional[str] = Field(None, description="Test suite to execute")
    environment: str = Field(..., description="Test environment")
    parallel_execution: bool = Field(False, description="Enable parallel execution")
    timeout_minutes: int = Field(60, description="Test timeout in minutes")
    test_data: Optional[Dict[str, Any]] = Field(None, description="Test data to use")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Test configuration")

class TestResponse(BaseResponse):
    """Response schema for test operations."""
    execution_id: str = Field(..., description="Test execution identifier")
    test_count: int = Field(..., description="Number of tests executed")
    status: TestStatus = Field(..., description="Overall execution status")
    started_at: datetime = Field(..., description="Execution start timestamp")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    environment: str = Field(..., description="Test environment")
    execution_url: Optional[str] = Field(None, description="Execution tracking URL")

class TestValidationRequest(BaseRequest):
    """Request schema for test validation operations."""
    test_id: str = Field(..., description="Test identifier to validate")
    validation_type: str = Field(..., description="Validation type")
    criteria: Dict[str, Any] = Field(..., description="Validation criteria")
    strict_mode: bool = Field(False, description="Enable strict validation")
    auto_fix: bool = Field(False, description="Auto-fix validation issues")

class TestValidationResponse(BaseResponse):
    """Response schema for test validation operations."""
    test_id: str = Field(..., description="Validated test identifier")
    validation_status: str = Field(..., description="Validation status")
    issues_found: List[Dict[str, Any]] = Field(default_factory=list, description="Validation issues found")
    issues_fixed: List[Dict[str, Any]] = Field(default_factory=list, description="Issues auto-fixed")
    validation_score: float = Field(..., description="Validation score")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")

class TestCoverage(BaseModel):
    """Test coverage data."""
    coverage_id: str = Field(..., description="Coverage identifier")
    test_level: TestLevel = Field(..., description="Test level")
    module_name: str = Field(..., description="Module name")
    total_lines: int = Field(..., description="Total lines of code")
    covered_lines: int = Field(..., description="Covered lines of code")
    coverage_percentage: float = Field(..., description="Coverage percentage")
    uncovered_functions: List[str] = Field(default_factory=list, description="Uncovered functions")
    last_calculated: datetime = Field(..., description="Coverage calculation timestamp")
    test_ids: List[str] = Field(default_factory=list, description="Covering test IDs")

class TestCoverageRequest(BaseRequest):
    """Request schema for test coverage operations."""
    test_level: Optional[TestLevel] = Field(None, description="Test level filter")
    module_names: Optional[List[str]] = Field(None, description="Module names filter")
    include_uncovered: bool = Field(True, description="Include uncovered items")
    format: str = Field("json", description="Output format")

class TestCoverageResponse(BaseResponse):
    """Response schema for test coverage operations."""
    coverage_data: List[TestCoverage] = Field(..., description="Coverage data")
    overall_coverage: float = Field(..., description="Overall coverage percentage")
    total_modules: int = Field(..., description="Total modules analyzed")
    covered_modules: int = Field(..., description="Modules with coverage")
    generated_at: datetime = Field(default_factory=datetime.now, description="Coverage generation timestamp")

class TestBenchmark(BaseModel):
    """Test benchmark data."""
    benchmark_id: str = Field(..., description="Benchmark identifier")
    test_name: str = Field(..., description="Test name")
    baseline_time_ms: int = Field(..., description="Baseline execution time")
    current_time_ms: int = Field(..., description="Current execution time")
    performance_change_percent: float = Field(..., description="Performance change percentage")
    status: str = Field(..., description="Benchmark status")
    threshold_percent: float = Field(..., description="Performance threshold")
    last_updated: datetime = Field(..., description="Last update timestamp")
    environment: str = Field(..., description="Test environment")

class TestBenchmarkRequest(BaseRequest):
    """Request schema for test benchmark operations."""
    test_ids: Optional[List[str]] = Field(None, description="Test IDs to benchmark")
    threshold_percent: float = Field(10.0, description="Performance threshold percentage")
    environment: str = Field(..., description="Test environment")
    create_baseline: bool = Field(False, description="Create new baseline")

class TestBenchmarkResponse(BaseResponse):
    """Response schema for test benchmark operations."""
    benchmark_results: List[TestBenchmark] = Field(..., description="Benchmark results")
    summary: Dict[str, Any] = Field(..., description="Benchmark summary")
    performance_regression: bool = Field(False, description="Performance regression detected")
    generated_at: datetime = Field(default_factory=datetime.now, description="Benchmark generation timestamp")

class TestArtifact(BaseModel):
    """Test artifact data."""
    artifact_id: str = Field(..., description="Artifact identifier")
    test_id: str = Field(..., description="Test identifier")
    artifact_type: str = Field(..., description="Artifact type")
    file_path: str = Field(..., description="Artifact file path")
    file_size: int = Field(..., description="Artifact file size")
    created_at: datetime = Field(..., description="Artifact creation timestamp")
    description: str = Field(..., description="Artifact description")
    retention_days: int = Field(30, description="Retention period in days")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional artifact metadata")

class TestArtifactRequest(BaseRequest):
    """Request schema for test artifact operations."""
    test_id: str = Field(..., description="Test identifier")
    artifact_type: str = Field(..., description="Artifact type")
    description: str = Field(..., description="Artifact description")
    file_path: str = Field(..., description="Artifact file path")
    retention_days: int = Field(30, description="Retention period in days")

class TestArtifactResponse(BaseResponse):
    """Response schema for test artifact operations."""
    artifact_id: str = Field(..., description="Artifact identifier")
    test_id: str = Field(..., description="Test identifier")
    artifact_type: str = Field(..., description="Artifact type")
    file_size: int = Field(..., description="Artifact file size")
    download_url: str = Field(..., description="Artifact download URL")
    expires_at: datetime = Field(..., description="Download URL expiration")
