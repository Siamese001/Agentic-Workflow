"""System Learning Policy Integration

Integrates system learning with agentic_core policy infrastructure for
policy-aware caching, validation, and compliance checking.

Provides unified policy integration across all system learning operations
with policy hash integration, validation frameworks, and compliance monitoring.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.cache.redis_cache_client import DeterministicRedisCache, get_hot_cache
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    # P1 Execution
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    # P4 Observability
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

# Module-level telemetry initialization
_emit_applies_guardrail("p0", "system_learning_policy", "p0_governance")
_emit_reads_policy_state("p0", "system_learning_policy", "policy_binding")
_emit_snapshots_state("p0", "system_learning_policy", "state_snapshot")

_emit_emits_metric_event("system_learning_policy", "p4obs", "metric_1")
_emit_emits_metric_event("system_learning_policy", "p4obs", "metric_2")
_emit_emits_metric_event("system_learning_policy", "p4obs", "metric_3")
_emit_emits_metric_event("system_learning_policy", "p4obs", "metric_4")
_emit_emits_metric_event("system_learning_policy", "p4obs", "metric_5")
_emit_emits_metric_event("system_learning_policy", "p4obs", "metric_6")
_emit_records_incident_event("system_learning_policy", "p4obs", "incident")
_emit_captures_runtime_anomaly("system_learning_policy", "p4obs", "anomaly")
_emit_writes_observability_log("system_learning_policy", "p4obs", "obs_log")
_emit_records_telemetry_event("system_learning_policy", "p4obs", "mon_state")
_emit_triggers_alert("system_learning_policy", "p4obs", "alert")
_emit_links_incident_trace("system_learning_policy", "p4obs", "trace_link")
_emit_captures_pattern("system_learning_policy", "p3lm", "pattern")
_emit_records_learning_event("system_learning_policy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("system_learning_policy", "p3lm", "snapshot")
_emit_feeds_meta_learning("system_learning_policy", "p3lm", "meta_feed")
_emit_feeds_meta_learning("system_learning_policy", "p3lm", "routing")
_emit_improves_agent_policy("system_learning_policy", "p3lm", "policy")
_emit_stores_learning_state("system_learning_policy", "p3lm", "state")

logger = logging.getLogger(__name__)


class PolicyComplianceStatus(Enum):
    """Policy compliance status for system learning operations."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    UNKNOWN = "unknown"
    ERROR = "error"


class PolicyValidationType(Enum):
    """Types of policy validation for system learning."""

    CACHE_POLICY = "cache_policy"
    RETRIEVAL_POLICY = "retrieval_policy"
    EMBEDDING_POLICY = "embedding_policy"
    LEARNING_POLICY = "learning_policy"
    SAFETY_POLICY = "safety_policy"
    PRIVACY_POLICY = "privacy_policy"
    RESOURCE_POLICY = "resource_policy"


@dataclass
class PolicyContext:
    """Policy context for system learning operations."""

    # Basic policy context
    policy_hash: str
    policy_version: str
    policy_type: PolicyValidationType

    # Policy parameters
    max_cache_size: int | None = None
    max_embedding_dimension: int | None = None
    allowed_models: list[str] | None = None
    retention_period_days: int | None = None

    # Compliance thresholds
    min_similarity_threshold: float = 0.7
    max_drift_tolerance: float = 0.2
    max_error_rate: float = 0.05

    # Resource limits
    max_memory_mb: int | None = None
    max_cpu_percent: float | None = None
    max_concurrent_operations: int | None = None


@dataclass
class PolicyValidationResult:
    """Result of policy validation for system learning operations."""

    # Validation outcome
    status: PolicyComplianceStatus
    is_compliant: bool
    validation_type: PolicyValidationType

    # Validation details
    score: float  # 0.0 to 1.0
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Context
    policy_context: PolicyContext | None = None
    validation_timestamp: float = field(default_factory=time.time)

    # Additional data
    metrics: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


class SystemLearningPolicyValidator:
    """Policy validator for system learning operations.

    Integrates with agentic_core policy infrastructure to provide:
    - Policy-aware cache key generation
    - Comprehensive validation frameworks
    - Compliance monitoring and reporting
    - Policy violation detection and handling
    """

    def __init__(
        self,
        component_name: str,
        cache: DeterministicRedisCache | None = None,
        enable_policy_caching: bool = True,
        policy_cache_ttl: int = 3600,  # 1 hour
    ) -> None:
        """Initialize system learning policy validator."""
        self.component_name = component_name
        self._cache = cache or get_hot_cache()
        self.enable_policy_caching = enable_policy_caching
        self.policy_cache_ttl = policy_cache_ttl

        # Policy registry
        self._policy_contexts: dict[str, PolicyContext] = {}
        self._validation_cache: dict[str, PolicyValidationResult] = {}

        # Metrics
        self._metrics = {
            "validations_performed": 0,
            "compliant_operations": 0,
            "non_compliant_operations": 0,
            "policy_cache_hits": 0,
            "policy_cache_misses": 0,
            "violations_by_type": {},
        }

        logger.info(f"SystemLearningPolicyValidator initialized for {component_name}")

    def register_policy_context(self, policy_context: PolicyContext) -> None:
        """Register a policy context for validation."""
        policy_key = self._build_policy_key(policy_context)
        self._policy_contexts[policy_key] = policy_context

        # Cache policy context if enabled
        if self.enable_policy_caching:
            policy_data = {
                "policy_hash": policy_context.policy_hash,
                "policy_version": policy_context.policy_version,
                "policy_type": policy_context.policy_type.value,
                "max_cache_size": policy_context.max_cache_size,
                "max_embedding_dimension": policy_context.max_embedding_dimension,
                "allowed_models": policy_context.allowed_models,
                "retention_period_days": policy_context.retention_period_days,
                "min_similarity_threshold": policy_context.min_similarity_threshold,
                "max_drift_tolerance": policy_context.max_drift_tolerance,
                "max_error_rate": policy_context.max_error_rate,
                "max_memory_mb": policy_context.max_memory_mb,
                "max_cpu_percent": policy_context.max_cpu_percent,
                "max_concurrent_operations": policy_context.max_concurrent_operations,
                "registered_at": time.time(),
            }

            cache_key = f"policy_context:{policy_context.policy_hash}"
            self._cache.set_json(cache_key, policy_data, ttl_seconds=self.policy_cache_ttl)

        logger.info(f"Registered policy context: {policy_context.policy_type.value}")

    async def validate_cache_operation(
        self,
        operation: str,
        cache_key: str,
        data_size: int | None = None,
        policy_hash: str | None = None,
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate a cache operation against policy constraints."""
        return await self._validate_operation(
            PolicyValidationType.CACHE_POLICY,
            operation=operation,
            cache_key=cache_key,
            data_size=data_size,
            policy_hash=policy_hash,
            **context,
        )

    async def validate_retrieval_operation(
        self,
        query_text: str,
        result_count: int,
        similarity_scores: list[float],
        policy_hash: str | None = None,
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate a retrieval operation against policy constraints."""
        return await self._validate_operation(
            PolicyValidationType.RETRIEVAL_POLICY,
            query_text=query_text,
            result_count=result_count,
            similarity_scores=similarity_scores,
            policy_hash=policy_hash,
            **context,
        )

    async def validate_embedding_operation(
        self,
        text_length: int,
        embedding_dimension: int,
        model_name: str,
        policy_hash: str | None = None,
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate an embedding operation against policy constraints."""
        return await self._validate_operation(
            PolicyValidationType.EMBEDDING_POLICY,
            text_length=text_length,
            embedding_dimension=embedding_dimension,
            model_name=model_name,
            policy_hash=policy_hash,
            **context,
        )

    async def validate_learning_operation(
        self,
        learning_rate: float,
        batch_size: int,
        model_version: str,
        policy_hash: str | None = None,
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate a learning operation against policy constraints."""
        return await self._validate_operation(
            PolicyValidationType.LEARNING_POLICY,
            learning_rate=learning_rate,
            batch_size=batch_size,
            model_version=model_version,
            policy_hash=policy_hash,
            **context,
        )

    async def _validate_operation(
        self,
        validation_type: PolicyValidationType,
        policy_hash: str | None = None,
        **operation_context: Any,
    ) -> PolicyValidationResult:
        """Internal method to validate an operation against policy."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "SystemLearningPolicyValidator._validate_operation",
        )

        self._metrics["validations_performed"] += 1

        try:
            # Get policy context
            policy_context = await self._get_policy_context(validation_type, policy_hash)

            # Check cache first
            cache_key = self._build_validation_cache_key(validation_type, operation_context)
            if self.enable_policy_caching and cache_key in self._validation_cache:
                self._metrics["policy_cache_hits"] += 1
                cached_result = self._validation_cache[cache_key]
                logger.debug(f"Policy validation cache hit for {validation_type.value}")
                return cached_result
            else:
                self._metrics["policy_cache_misses"] += 1

            # Perform validation based on type
            if validation_type == PolicyValidationType.CACHE_POLICY:
                result = await self._validate_cache_policy(policy_context, **operation_context)
            elif validation_type == PolicyValidationType.RETRIEVAL_POLICY:
                result = await self._validate_retrieval_policy(policy_context, **operation_context)
            elif validation_type == PolicyValidationType.EMBEDDING_POLICY:
                result = await self._validate_embedding_policy(policy_context, **operation_context)
            elif validation_type == PolicyValidationType.LEARNING_POLICY:
                result = await self._validate_learning_policy(policy_context, **operation_context)
            else:
                result = PolicyValidationResult(
                    status=PolicyComplianceStatus.UNKNOWN,
                    is_compliant=False,
                    validation_type=validation_type,
                    score=0.0,
                    violations=[f"Unknown validation type: {validation_type.value}"],
                )

            # Cache result if enabled
            if self.enable_policy_caching:
                self._validation_cache[cache_key] = result

            # Update metrics
            if result.is_compliant:
                self._metrics["compliant_operations"] += 1
                _emit_records_learning_event(
                    "p3lm",
                    self.component_name,
                    f"policy_compliant:{validation_type.value}",
                )
            else:
                self._metrics["non_compliant_operations"] += 1
                violation_type = validation_type.value
                self._metrics["violations_by_type"][violation_type] = (
                    self._metrics["violations_by_type"].get(violation_type, 0) + 1
                )

                _emit_captures_pattern(
                    "p3lm",
                    self.component_name,
                    f"policy_violation:{validation_type.value}",
                )
                _emit_triggers_alert(
                    "p4obs",
                    self.component_name,
                    f"policy_violation:{validation_type.value}",
                )

            # Emit policy telemetry
            await self._emit_policy_telemetry(result, operation_context)

            return result

        except Exception as e:
            logger.error(f"Policy validation failed: {e}")
            _emit_captures_runtime_anomaly(
                "p4obs",
                self.component_name,
                f"policy_validation_error:{validation_type.value}",
            )

            return PolicyValidationResult(
                status=PolicyComplianceStatus.ERROR,
                is_compliant=False,
                validation_type=validation_type,
                score=0.0,
                violations=[f"Validation error: {str(e)}"],
            )

    async def _validate_cache_policy(
        self,
        policy_context: PolicyContext,
        operation: str,
        cache_key: str,
        data_size: int | None = None,
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate cache operation against policy."""
        violations = []
        warnings = []
        score = 1.0

        # Check cache size limits
        if policy_context.max_cache_size and data_size:
            if data_size > policy_context.max_cache_size:
                violations.append(f"Cache size {data_size} exceeds limit {policy_context.max_cache_size}")
                score -= 0.5

        # Check cache key compliance
        if not cache_key or len(cache_key) < 10:
            violations.append("Invalid cache key format")
            score -= 0.3

        # Check operation compliance
        allowed_operations = ["get", "set", "delete", "invalidate"]
        if operation not in allowed_operations:
            violations.append(f"Operation {operation} not in allowed operations: {allowed_operations}")
            score -= 0.2

        # Emit policy verification
        _emit_verifies_policy("p1", self.component_name, f"cache_policy:{operation}")

        return PolicyValidationResult(
            status=PolicyComplianceStatus.COMPLIANT
            if not violations
            else PolicyComplianceStatus.NON_COMPLIANT,
            is_compliant=len(violations) == 0,
            validation_type=PolicyValidationType.CACHE_POLICY,
            score=max(0.0, score),
            violations=violations,
            warnings=warnings,
            policy_context=policy_context,
            metrics={
                "operation": operation,
                "cache_key_length": len(cache_key),
                "data_size": data_size,
            },
        )

    async def _validate_retrieval_policy(
        self,
        policy_context: PolicyContext,
        query_text: str,
        result_count: int,
        similarity_scores: list[float],
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate retrieval operation against policy."""
        violations = []
        warnings = []
        score = 1.0

        # Check similarity thresholds
        if similarity_scores:
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            if avg_similarity < policy_context.min_similarity_threshold:
                violations.append(
                    f"Average similarity {avg_similarity:.3f} below threshold "
                    f"{policy_context.min_similarity_threshold}",
                )
                score -= 0.4

        # Check result count limits
        if result_count > 100:  # Reasonable default limit
            warnings.append(f"Large result set: {result_count} items")
            score -= 0.1

        # Check query text compliance
        if len(query_text) > 10000:  # Reasonable limit
            violations.append(f"Query text too long: {len(query_text)} characters")
            score -= 0.3

        # Check for low-quality results
        low_quality_count = sum(1 for score in similarity_scores if score < 0.5)
        if low_quality_count > len(similarity_scores) * 0.5:
            warnings.append(
                f"High number of low-quality results: {low_quality_count}/{len(similarity_scores)}",
            )
            score -= 0.2

        # Emit policy verification
        _emit_verifies_policy("p1", self.component_name, "retrieval_policy")

        return PolicyValidationResult(
            status=PolicyComplianceStatus.COMPLIANT
            if not violations
            else PolicyComplianceStatus.NON_COMPLIANT,
            is_compliant=len(violations) == 0,
            validation_type=PolicyValidationType.RETRIEVAL_POLICY,
            score=max(0.0, score),
            violations=violations,
            warnings=warnings,
            policy_context=policy_context,
            metrics={
                "query_length": len(query_text),
                "result_count": result_count,
                "avg_similarity": sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0,
                "low_quality_count": low_quality_count,
            },
        )

    async def _validate_embedding_policy(
        self,
        policy_context: PolicyContext,
        text_length: int,
        embedding_dimension: int,
        model_name: str,
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate embedding operation against policy."""
        violations = []
        warnings = []
        score = 1.0

        # Check embedding dimension limits
        if policy_context.max_embedding_dimension:
            if embedding_dimension > policy_context.max_embedding_dimension:
                violations.append(
                    f"Embedding dimension {embedding_dimension} exceeds limit "
                    f"{policy_context.max_embedding_dimension}",
                )
                score -= 0.5

        # Check model compliance
        if policy_context.allowed_models and model_name not in policy_context.allowed_models:
            violations.append(f"Model {model_name} not in allowed models: {policy_context.allowed_models}")
            score -= 0.4

        # Check text length limits
        if text_length > 50000:  # Reasonable limit
            warnings.append(f"Large text for embedding: {text_length} characters")
            score -= 0.1

        # Check embedding dimension reasonableness
        if embedding_dimension < 128 or embedding_dimension > 4096:
            warnings.append(f"Unusual embedding dimension: {embedding_dimension}")
            score -= 0.1

        # Emit policy verification and store embedding
        _emit_verifies_policy("p1", self.component_name, "embedding_policy")
        _emit_stores_embedding("p4obs", self.component_name, f"embedding_validation:{model_name}")

        return PolicyValidationResult(
            status=PolicyComplianceStatus.COMPLIANT
            if not violations
            else PolicyComplianceStatus.NON_COMPLIANT,
            is_compliant=len(violations) == 0,
            validation_type=PolicyValidationType.EMBEDDING_POLICY,
            score=max(0.0, score),
            violations=violations,
            warnings=warnings,
            policy_context=policy_context,
            metrics={
                "text_length": text_length,
                "embedding_dimension": embedding_dimension,
                "model_name": model_name,
            },
        )

    async def _validate_learning_policy(
        self,
        policy_context: PolicyContext,
        learning_rate: float,
        batch_size: int,
        model_version: str,
        **context: Any,
    ) -> PolicyValidationResult:
        """Validate learning operation against policy."""
        violations = []
        warnings = []
        score = 1.0

        # Check learning rate bounds
        if learning_rate < 0.0001 or learning_rate > 1.0:
            violations.append(f"Learning rate {learning_rate} outside reasonable bounds [0.0001, 1.0]")
            score -= 0.4

        # Check batch size limits
        if batch_size > 1024:  # Reasonable limit
            warnings.append(f"Large batch size: {batch_size}")
            score -= 0.1

        # Check model version format
        if not model_version or len(model_version) < 3:
            violations.append("Invalid model version format")
            score -= 0.2

        # Emit policy verification and learning events
        _emit_verifies_policy("p1", self.component_name, "learning_policy")
        _emit_records_learning_event("p3lm", self.component_name, "learning_policy_validated")
        _emit_writes_learning_snapshot("p3lm", self.component_name, "learning_policy_validation")

        return PolicyValidationResult(
            status=PolicyComplianceStatus.COMPLIANT
            if not violations
            else PolicyComplianceStatus.NON_COMPLIANT,
            is_compliant=len(violations) == 0,
            validation_type=PolicyValidationType.LEARNING_POLICY,
            score=max(0.0, score),
            violations=violations,
            warnings=warnings,
            policy_context=policy_context,
            metrics={
                "learning_rate": learning_rate,
                "batch_size": batch_size,
                "model_version": model_version,
            },
        )

    async def _get_policy_context(
        self,
        validation_type: PolicyValidationType,
        policy_hash: str | None = None,
    ) -> PolicyContext:
        """Get policy context for validation."""
        if policy_hash:
            # Try to get from cache first
            cache_key = f"policy_context:{policy_hash}"
            if self.enable_policy_caching:
                cached_data = self._cache.get_json(cache_key)
                if cached_data:
                    return PolicyContext(
                        policy_hash=cached_data["policy_hash"],
                        policy_version=cached_data["policy_version"],
                        policy_type=PolicyValidationType(cached_data["policy_type"]),
                        max_cache_size=cached_data.get("max_cache_size"),
                        max_embedding_dimension=cached_data.get("max_embedding_dimension"),
                        allowed_models=cached_data.get("allowed_models"),
                        retention_period_days=cached_data.get("retention_period_days"),
                        min_similarity_threshold=cached_data.get("min_similarity_threshold", 0.7),
                        max_drift_tolerance=cached_data.get("max_drift_tolerance", 0.2),
                        max_error_rate=cached_data.get("max_error_rate", 0.05),
                        max_memory_mb=cached_data.get("max_memory_mb"),
                        max_cpu_percent=cached_data.get("max_cpu_percent"),
                        max_concurrent_operations=cached_data.get("max_concurrent_operations"),
                    )

        # Create default policy context
        return PolicyContext(
            policy_hash=policy_hash or "default",
            policy_version="1.0",
            policy_type=validation_type,
            min_similarity_threshold=0.7,
            max_drift_tolerance=0.2,
            max_error_rate=0.05,
        )

    def _build_policy_key(self, policy_context: PolicyContext) -> str:
        """Build policy key for context storage."""
        return f"{policy_context.policy_type.value}:{policy_context.policy_hash}"

    def _build_validation_cache_key(
        self,
        validation_type: PolicyValidationType,
        operation_context: dict[str, Any],
    ) -> str:
        """Build cache key for validation results."""
        # Create deterministic key from operation context
        context_str = json.dumps(operation_context, sort_keys=True, default=str)
        context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:16]
        return f"validation:{validation_type.value}:{context_hash}"

    async def _emit_policy_telemetry(
        self,
        result: PolicyValidationResult,
        operation_context: dict[str, Any],
    ) -> None:
        """Emit policy validation telemetry."""
        # Emit telemetry event
        _emit_records_telemetry_event(
            "p4",
            self.component_name,
            f"policy_validation:{result.validation_type.value}",
        )

        # Update monitoring state
        _emit_updates_monitoring_state("p4obs", self.component_name, f"policy_status:{result.status.value}")

        # Write observability log
        log_data = {
            "validation_type": result.validation_type.value,
            "status": result.status.value,
            "is_compliant": result.is_compliant,
            "score": result.score,
            "violations_count": len(result.violations),
            "warnings_count": len(result.warnings),
            "component": self.component_name,
        }

        _emit_writes_observability_log("p4obs", self.component_name, json.dumps(log_data))

    def build_policy_aware_cache_key(
        self,
        base_key: str,
        policy_hash: str | None = None,
        **additional_params: Any,
    ) -> str:
        """Build policy-aware cache key."""
        if policy_hash:
            # Add policy hash to cache key
            policy_suffix = f":policy:{policy_hash[:8]}"
            return base_key + policy_suffix
        return base_key

    def get_metrics(self) -> dict[str, Any]:
        """Get policy validator metrics."""
        total_validations = self._metrics["validations_performed"]
        compliance_rate = (
            self._metrics["compliant_operations"] / total_validations if total_validations > 0 else 0.0
        )

        return {
            **self._metrics,
            "compliance_rate": compliance_rate,
            "non_compliance_rate": 1 - compliance_rate,
            "cache_hit_rate": (
                self._metrics["policy_cache_hits"]
                / (self._metrics["policy_cache_hits"] + self._metrics["policy_cache_misses"])
                if (self._metrics["policy_cache_hits"] + self._metrics["policy_cache_misses"]) > 0
                else 0.0
            ),
        }

    def reset_metrics(self) -> None:
        """Reset policy validator metrics."""
        for key in self._metrics:
            if isinstance(self._metrics[key], dict):
                self._metrics[key].clear()
            else:
                self._metrics[key] = 0
        _emit_records_telemetry_event("system_learning_policy", "p4obs", "metrics_reset")


# Component policy validators registry
_policy_validators: dict[str, SystemLearningPolicyValidator] = {}


def get_policy_validator(component_name: str) -> SystemLearningPolicyValidator:
    """Get or create a policy validator for a component."""
    if component_name not in _policy_validators:
        _policy_validators[component_name] = SystemLearningPolicyValidator(component_name)
    return _policy_validators[component_name]


__all__ = [
    "PolicyComplianceStatus",
    "PolicyValidationType",
    "PolicyContext",
    "PolicyValidationResult",
    "SystemLearningPolicyValidator",
    "get_policy_validator",
]
