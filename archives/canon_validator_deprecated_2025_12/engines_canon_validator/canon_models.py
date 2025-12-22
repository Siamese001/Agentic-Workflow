"""
Hybrid Semantic Cache Models - Canon Entry Schema

This module defines the Pydantic models for storing and retrieving
canon patterns in Redis with vector search capabilities.

The CanonEntry model enforces the L5 Safety Protocol by tracking
risk metrics and failure history for each pattern.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class CanonEntry(BaseModel):
    """
    A Meta-Learning Record for the Hybrid Semantic Cache.

    This model stores rich metadata for the L5 Agentic Meta-Learning system,
    enabling trend analysis, knowledge transfer, and performance optimization.
    """

    # Primary identifier
    id: UUID = Field(default_factory=uuid4,
                     description="Unique identifier for the canon entry")

    # Vector representation (768 dimensions for sentence-transformers)
    vector: List[float] = Field(..., min_items=768, max_items=768,
                                description="768-dimensional vector embedding")

    # Content tracking
    ast_json: Dict = Field(...,
                           description="Abstract Syntax Tree as JSON for structural validation")
    ast_hash: str = Field(..., min_length=32, max_length=64,
                          description="SHA-256 hash of AST structure")

    # Meta-Learning metadata
    policy_key: str = Field(
        ..., description="The specific Canon rule key triggered (e.g., 'canon:rule:12')")
    failure_count: int = Field(
        default=0, ge=0, description="Number of times this pattern caused validation failure")
    success_count: int = Field(
        default=0, ge=0, description="Number of successful validations")
    latency_ms: int = Field(
        default=0, ge=0, description="Time taken for L5 Agent to resolve the issue")
    last_validated: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of last validation")
    project_tag: str = Field(
        default="default", description="Project identifier for cross-project knowledge transfer")

    # Additional metadata
    metadata: Dict = Field(
        default_factory=lambda: {
            "risk_score": 0,
            "max_files_touched": 0,
            "created_at": datetime.utcnow().isoformat(),
            "pattern_type": "unknown",
            "agent_name": "unknown",
            "validation_status": "pending",
            "is_canon_key": False,  # Whether this is one of the 50 Canon Keys
            "meta_prompt": None  # Refined instruction set from failed runs
        },
        description="Additional tracking metadata"
    )

    @validator('metadata')
    def validate_safety_metadata(cls, v):
        """Ensure required safety fields are present and valid."""
        required_fields = {
            'risk_score': (int, (0, 100)),
            'failure_count': (int, (0, None)),
            'max_files_touched': (int, (0, None)),
            'created_at': (str, None),
            'last_seen': (str, None),
            'pattern_type': (str, None),
            'agent_name': (str, None),
            'validation_status': (str, ['pending', 'validated', 'failed', 'blocked'])
        }

        for field, (field_type, constraints) in required_fields.items():
            if field not in v:
                raise ValueError(f"Missing required metadata field: {field}")

            if constraints and isinstance(constraints, tuple):
                min_val, max_val = constraints
                if min_val is not None and v[field] < min_val:
                    raise ValueError(f"{field} must be >= {min_val}")
                if max_val is not None and v[field] > max_val:
                    raise ValueError(f"{field} must be <= {max_val}")
            elif isinstance(constraints, list):
                if v[field] not in constraints:
                    raise ValueError(f"{field} must be one of {constraints}")

        return v

    @validator('risk_score', always=True)
    def calculate_risk_score(cls, v, values):
        """Calculate risk score based on failure count, success rate, and performance."""
        # Direct fields
        failure_count = values.get('failure_count', 0)
        success_count = values.get('success_count', 0)
        latency_ms = values.get('latency_ms', 0)

        # Metadata fields
        metadata = values.get('metadata', {})
        max_files = metadata.get('max_files_touched', 0)

        # Base risk from failures
        risk = min(50, failure_count * 10)  # Max 50 from failures

        # Reduce risk based on success rate
        total_runs = failure_count + success_count
        if total_runs > 0:
            success_rate = success_count / total_runs
            # Reduce risk based on success rate
            risk = int(risk * (1 - success_rate))

        # Additional risk if pattern touched many files
        if max_files > 5:
            risk += min(30, (max_files - 5) * 5)

        # Performance risk (high latency)
        if latency_ms > 1000:
            risk += min(20, (latency_ms - 1000) // 100)

        return min(100, risk)

    class Config:
        json_encoders = {
            UUID: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }

    def is_safe_to_execute(self) -> bool:
        """
        Check if this pattern is safe to execute based on L5 Safety Protocol.

        Returns:
            bool: True if safe, False if blocked
        """
        # Block if high risk score
        if self.risk_score > 80:
            return False

        # Block if any failures recorded (unless overridden by high success rate)
        if self.failure_count > 0:
            total_runs = self.failure_count + self.success_count
            if total_runs < 10 or (self.failure_count / total_runs) > 0.1:
                return False

        # Block if historically touched too many files
        if self.metadata.get('max_files_touched', 0) > 5:
            return False

        # Block if validation status is not 'validated'
        if self.metadata.get('validation_status') != 'validated':
            return False

        return True

    def update_failure(self, meta_prompt: Optional[str] = None):
        """Record a failure and update risk metrics."""
        self.failure_count += 1
        self.last_validated = datetime.utcnow()
        self.metadata['validation_status'] = 'failed'

        # Store meta-prompt from failed run for learning
        if meta_prompt:
            self.metadata['meta_prompt'] = meta_prompt

        # Update risk score
        self.metadata['risk_score'] = self.risk_score

    def update_success(self, files_touched: int = 0, latency_ms: int = 0):
        """Record a successful execution."""
        self.success_count += 1
        self.last_validated = datetime.utcnow()
        self.metadata['validation_status'] = 'validated'

        # Update performance metrics
        if files_touched > self.metadata.get('max_files_touched', 0):
            self.metadata['max_files_touched'] = files_touched

        # Update rolling average latency
        if self.latency_ms == 0:
            self.latency_ms = latency_ms
        else:
            self.latency_ms = int((self.latency_ms + latency_ms) // 2)

        # Update risk score
        self.metadata['risk_score'] = self.risk_score

    def is_within_time_window(self, hours: int = 24) -> bool:
        """Check if this entry is within the specified time window."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.last_validated >= cutoff

    def get_success_rate(self) -> float:
        """Calculate the success rate for this pattern."""
        total = self.failure_count + self.success_count
        return self.success_count / total if total > 0 else 0.0


class CanonQuery(BaseModel):
    """Query model for searching canon entries."""

    query_vector: List[float] = Field(..., min_items=768, max_items=768)
    threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    max_results: int = Field(default=10, ge=1, le=100)
    filter_safe_only: bool = Field(
        default=True, description="Only return safe patterns")

    class Config:
        schema_extra = {
            "example": {
                "query_vector": [0.1] * 768,
                "threshold": 0.8,
                "max_results": 10,
                "filter_safe_only": True
            }
        }


class CanonSearchResult(BaseModel):
    """Result model for canon search operations."""

    entries: List[CanonEntry]
    total_found: int
    query_time_ms: float
    safe_count: int
    blocked_count: int

    @property
    def has_safe_patterns(self) -> bool:
        """Check if any safe patterns were found."""
        return self.safe_count > 0

    @property
    def safety_ratio(self) -> float:
        """Ratio of safe to total patterns."""
        return self.safe_count / self.total_found if self.total_found > 0 else 0.0

