"""
Feature Schemas for ML Decision Support

Defines deterministic feature extraction schemas with provenance tracking,
null handling policies, and versioning for all ML models.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FeatureType(Enum):
    """Supported feature types."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    BOOLEAN = "boolean"
    TEXT = "text"
    TIMESTAMP = "timestamp"
    LIST = "list"
    DICT = "dict"


class NullHandling(Enum):
    """How to handle null/missing values."""
    FAIL_CLOSED = "fail_closed"  # Return None/escalate
    DEFAULT_VALUE = "default_value"  # Use predefined default
    DROP_FEATURE = "drop_feature"  # Exclude from model input
    IMPUTE_MEAN = "impute_mean"  # Use mean (numeric only)
    IMPUTE_MODE = "impute_mode"  # Use mode (categorical only)


@dataclass
class FeatureDefinition:
    """Definition for a single feature."""
    name: str
    feature_type: FeatureType
    description: str
    required: bool = True
    null_handling: NullHandling = NullHandling.FAIL_CLOSED
    default_value: str | int | float | bool | None = None
    validation_rules: dict[str, Any] = field(default_factory=dict)
    provenance: str = ""  # Source of the feature
    extraction_function: str | None = None  # Function name for extraction
    version: str = "1.0"

    def __post_init__(self):
        """Validate feature definition."""
        if not self.name:
            raise ValueError("Feature name cannot be empty")

        if self.null_handling == NullHandling.DEFAULT_VALUE and self.default_value is None:
            raise ValueError(f"Feature {self.name} must have default_value when using DEFAULT_VALUE null handling")


@dataclass
class FeatureSchema:
    """Complete feature schema for a model."""
    schema_name: str
    schema_version: str
    description: str
    features: list[FeatureDefinition]
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    schema_digest: str = ""

    def __post_init__(self):
        """Compute schema digest after creation."""
        self.schema_digest = self._compute_digest()

    def _compute_digest(self) -> str:
        """Compute SHA-256 digest of schema."""
        schema_dict = {
            'schema_name': self.schema_name,
            'schema_version': self.schema_version,
            'features': [
                {
                    'name': f.name,
                    'type': f.feature_type.value,
                    'required': f.required,
                    'null_handling': f.null_handling.value,
                    'default_value': f.default_value,
                    'validation_rules': f.validation_rules,
                    'provenance': f.provenance,
                    'extraction_function': f.extraction_function,
                    'version': f.version
                }
                for f in self.features
            ]
        }

        schema_str = json.dumps(schema_dict, sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()

    def get_feature(self, name: str) -> FeatureDefinition | None:
        """Get feature definition by name."""
        for feature in self.features:
            if feature.name == name:
                return feature
        return None

    def validate_features(self, features: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate a feature dictionary against this schema.

        Args:
            features: Feature dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required features
        for feature_def in self.features:
            if feature_def.required and feature_def.name not in features:
                errors.append(f"Required feature '{feature_def.name}' is missing")

        # Validate feature types and values
        for name, value in features.items():
            feature_def = self.get_feature(name)
            if not feature_def:
                errors.append(f"Unknown feature '{name}'")
                continue

            # Type validation
            if not self._validate_feature_type(value, feature_def):
                errors.append(f"Feature '{name}' has invalid type")
                continue

            # Value validation
            if not self._validate_feature_value(value, feature_def):
                errors.append(f"Feature '{name}' failed validation rules")

        return len(errors) == 0, errors

    def _validate_feature_type(self, value: Any, feature_def: FeatureDefinition) -> bool:
        """Validate feature type."""
        if value is None:
            return True  # Null handling handled separately

        type_map = {
            FeatureType.NUMERIC: (int, float),
            FeatureType.CATEGORICAL: str,
            FeatureType.BOOLEAN: bool,
            FeatureType.TEXT: str,
            FeatureType.TIMESTAMP: (str, datetime),
            FeatureType.LIST: list,
            FeatureType.DICT: dict
        }

        expected_types = type_map.get(feature_def.feature_type)
        if expected_types is None:
            return False

        return isinstance(value, expected_types)

    def _validate_feature_value(self, value: Any, feature_def: FeatureDefinition) -> bool:
        """Validate feature value against rules."""
        if value is None or not feature_def.validation_rules:
            return True

        # Numeric validations
        if feature_def.feature_type == FeatureType.NUMERIC:
            if 'min_value' in feature_def.validation_rules:
                if value < feature_def.validation_rules['min_value']:
                    return False
            if 'max_value' in feature_def.validation_rules:
                if value > feature_def.validation_rules['max_value']:
                    return False
            if 'allowed_values' in feature_def.validation_rules:
                if value not in feature_def.validation_rules['allowed_values']:
                    return False

        # Categorical validations
        elif feature_def.feature_type == FeatureType.CATEGORICAL:
            if 'allowed_values' in feature_def.validation_rules:
                if value not in feature_def.validation_rules['allowed_values']:
                    return False

        # Text validations
        elif feature_def.feature_type == FeatureType.TEXT:
            if 'min_length' in feature_def.validation_rules:
                if len(value) < feature_def.validation_rules['min_length']:
                    return False
            if 'max_length' in feature_def.validation_rules:
                if len(value) > feature_def.validation_rules['max_length']:
                    return False

        return True


class FeatureSchemas:
    """
    Registry of feature schemas for all ML models.

    Provides centralized schema management with versioning,
    validation, and provenance tracking.
    """

    def __init__(self):
        self._schemas: dict[str, FeatureSchema] = {}
        self._initialize_builtin_schemas()

    def _initialize_builtin_schemas(self) -> None:
        """Initialize built-in feature schemas."""

        # L0 Route Recommender Schema
        l0_route_schema = FeatureSchema(
            schema_name="l0_route_recommender",
            schema_version="1.0",
            description="Features for L0 routing recommendation model",
            features=[
                FeatureDefinition(
                    name="token_count",
                    feature_type=FeatureType.NUMERIC,
                    description="Number of tokens in request",
                    provenance="request.input.token_count",
                    validation_rules={"min_value": 0, "max_value": 100000}
                ),
                FeatureDefinition(
                    name="tool_complexity_score",
                    feature_type=FeatureType.NUMERIC,
                    description="Complexity score of required tools",
                    provenance="request.tools.complexity_score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="latency_budget_ms",
                    feature_type=FeatureType.NUMERIC,
                    description="Latency budget in milliseconds",
                    provenance="request.constraints.latency_budget_ms",
                    validation_rules={"min_value": 0, "max_value": 300000}
                ),
                FeatureDefinition(
                    name="user_confidence_score",
                    feature_type=FeatureType.NUMERIC,
                    description="User confidence in request",
                    provenance="request.user.confidence_score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="path_success_history",
                    feature_type=FeatureType.NUMERIC,
                    description="Historical success rate for paths",
                    provenance="history.path.success_rate",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="current_load_ratio",
                    feature_type=FeatureType.NUMERIC,
                    description="Current system load ratio",
                    provenance="system.load.current_ratio",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="semantic_similarity_score",
                    feature_type=FeatureType.NUMERIC,
                    description="Semantic similarity to historical requests",
                    provenance="request.semantic.similarity_score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="policy_hash_version",
                    feature_type=FeatureType.CATEGORICAL,
                    description="Version of policy hash",
                    provenance="policy.hash.version",
                    validation_rules={"allowed_values": ["v1.0", "v1.1", "v2.0"]}
                ),
                FeatureDefinition(
                    name="trace_id_hash",
                    feature_type=FeatureType.TEXT,
                    description="Hash of trace ID for determinism",
                    provenance="trace.id.hash",
                    validation_rules={"min_length": 32, "max_length": 64}
                )
            ]
        )

        # C0 Retrieval Reranker Schema
        c0_rerank_schema = FeatureSchema(
            schema_name="c0_retrieval_reranker",
            schema_version="1.0",
            description="Features for C0 retrieval reranking model",
            features=[
                FeatureDefinition(
                    name="query_doc_similarity",
                    feature_type=FeatureType.NUMERIC,
                    description="Query-document similarity score",
                    provenance="retrieval.similarity.query_doc",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="doc_authority_score",
                    feature_type=FeatureType.NUMERIC,
                    description="Document authority score",
                    provenance="document.authority.score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="recency_score",
                    feature_type=FeatureType.NUMERIC,
                    description="Document recency score",
                    provenance="document.recency.score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="usage_frequency",
                    feature_type=FeatureType.NUMERIC,
                    description="Historical usage frequency",
                    provenance="document.usage.frequency",
                    validation_rules={"min_value": 0.0, "max_value": 1000.0}
                ),
                FeatureDefinition(
                    name="semantic_density",
                    feature_type=FeatureType.NUMERIC,
                    description="Semantic density of document",
                    provenance="document.semantic.density",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="source_reliability",
                    feature_type=FeatureType.NUMERIC,
                    description="Source reliability score",
                    provenance="source.reliability.score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="completeness_score",
                    feature_type=FeatureType.NUMERIC,
                    description="Document completeness score",
                    provenance="document.completeness.score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="query_complexity",
                    feature_type=FeatureType.NUMERIC,
                    description="Query complexity score",
                    provenance="query.complexity.score",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                ),
                FeatureDefinition(
                    name="cache_hit_probability",
                    feature_type=FeatureType.NUMERIC,
                    description="Probability of cache hit",
                    provenance="cache.hit.probability",
                    validation_rules={"min_value": 0.0, "max_value": 1.0}
                )
            ]
        )

        # L6 Anomaly Detector Schema
        l6_anomaly_schema = FeatureSchema(
            schema_name="l6_anomaly_detector",
            schema_version="1.0",
            description="Features for L6 anomaly detection model",
            features=[
                FeatureDefinition(
                    name="latency_z_score",
                    feature_type=FeatureType.NUMERIC,
                    description="Latency z-score",
                    provenance="metrics.latency.z_score",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=0.0
                ),
                FeatureDefinition(
                    name="error_rate_spike",
                    feature_type=FeatureType.NUMERIC,
                    description="Error rate spike factor",
                    provenance="metrics.error_rate.spike",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=1.0
                ),
                FeatureDefinition(
                    name="token_deviation",
                    feature_type=FeatureType.NUMERIC,
                    description="Token count deviation from baseline",
                    provenance="metrics.tokens.deviation",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=0.0
                ),
                FeatureDefinition(
                    name="path_divergence",
                    feature_type=FeatureType.NUMERIC,
                    description="Path selection divergence",
                    provenance="routing.path.divergence",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=0.0
                ),
                FeatureDefinition(
                    name="policy_hash_changes",
                    feature_type=FeatureType.NUMERIC,
                    description="Number of policy hash changes",
                    provenance="policy.hash.changes.count",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=0
                ),
                FeatureDefinition(
                    name="replay_mismatch_count",
                    feature_type=FeatureType.NUMERIC,
                    description="Replay mismatch count",
                    provenance="replay.mismatch.count",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=0
                ),
                FeatureDefinition(
                    name="escalation_frequency",
                    feature_type=FeatureType.NUMERIC,
                    description="Escalation frequency",
                    provenance="escalation.frequency",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=0.0
                ),
                FeatureDefinition(
                    name="healing_success_rate",
                    feature_type=FeatureType.NUMERIC,
                    description="Healing success rate",
                    provenance="healing.success.rate",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=1.0
                ),
                FeatureDefinition(
                    name="semantic_drift_score",
                    feature_type=FeatureType.NUMERIC,
                    description="Semantic drift score",
                    provenance="semantic.drift.score",
                    null_handling=NullHandling.DEFAULT_VALUE,
                    default_value=0.0
                )
            ]
        )

        # Register schemas
        self.register_schema(l0_route_schema)
        self.register_schema(c0_rerank_schema)
        self.register_schema(l6_anomaly_schema)

    def register_schema(self, schema: FeatureSchema) -> None:
        """Register a feature schema."""
        schema_key = f"{schema.schema_name}:{schema.schema_version}"
        self._schemas[schema_key] = schema

    def get_schema(self, schema_name: str, version: str = "1.0") -> FeatureSchema | None:
        """Get feature schema by name and version."""
        schema_key = f"{schema_name}:{version}"
        return self._schemas.get(schema_key)

    def get_latest_schema(self, schema_name: str) -> FeatureSchema | None:
        """Get latest version of a schema."""
        matching_schemas = [
            schema for key, schema in self._schemas.items()
            if schema.schema_name == schema_name
        ]

        if not matching_schemas:
            return None

        # Return schema with highest version
        return max(matching_schemas, key=lambda s: s.schema_version)

    def list_schemas(self) -> list[str]:
        """List all available schema names."""
        return list(set(schema.schema_name for schema in self._schemas.values()))

    def validate_features(
        self,
        schema_name: str,
        features: dict[str, Any],
        version: str = "1.0"
    ) -> tuple[bool, list[str], dict[str, Any] | None]:
        """
        Validate features against a schema.

        Args:
            schema_name: Name of schema
            features: Feature dictionary to validate
            version: Schema version

        Returns:
            Tuple of (is_valid, error_messages, processed_features)
        """
        schema = self.get_schema(schema_name, version)
        if not schema:
            return False, [f"Schema {schema_name}:{version} not found"], None

        is_valid, errors = schema.validate_features(features)

        # Process null handling
        processed_features = self._process_null_handling(features, schema)

        return is_valid, errors, processed_features

    def _process_null_handling(
        self,
        features: dict[str, Any],
        schema: FeatureSchema
    ) -> dict[str, Any]:
        """Process null values according to schema rules."""
        processed = {}

        for feature_def in schema.features:
            value = features.get(feature_def.name)

            if value is None:
                # Apply null handling strategy
                if feature_def.null_handling == NullHandling.DEFAULT_VALUE:
                    processed[feature_def.name] = feature_def.default_value
                elif feature_def.null_handling == NullHandling.DROP_FEATURE:
                    continue  # Skip this feature
                elif feature_def.null_handling == NullHandling.FAIL_CLOSED:
                    processed[feature_def.name] = None  # Keep None, will fail later
                else:
                    # IMPUTE_* handled during training, not inference
                    processed[feature_def.name] = feature_def.default_value
            else:
                processed[feature_def.name] = value

        return processed

    def get_schema_digest(self, schema_name: str, version: str = "1.0") -> str | None:
        """Get schema digest for version tracking."""
        schema = self.get_schema(schema_name, version)
        return schema.schema_digest if schema else None
