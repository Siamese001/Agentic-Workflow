"""
Base Deterministic Feature Extractor

Provides deterministic feature extraction with provenance tracking,
replayability, and null handling according to governance rules.
"""

import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_records_execution_trace

from ..config.feature_schemas import FeatureDefinition, FeatureSchema, NullHandling


@dataclass
class FeatureProvenance:
    """Provenance information for a feature."""
    feature_name: str
    source: str  # Where the feature came from
    extraction_function: str  # Function that extracted it
    extraction_timestamp: datetime
    input_hash: str  # Hash of inputs for reproducibility
    confidence: float  # Confidence in feature value
    processing_steps: list[str]  # Processing steps applied
    version: str = "1.0"


@dataclass
class FeatureExtractionResult:
    """Result of feature extraction with full provenance."""
    features: dict[str, Any]
    provenance: dict[str, FeatureProvenance]
    extraction_metadata: dict[str, Any]
    success: bool
    error_messages: list[str]
    extraction_id: str
    deterministic_hash: str


class DeterministicFeatureExtractor(ABC):
    """
    Base class for deterministic feature extractors.

    Ensures all feature extraction is:
    - Deterministic (same inputs → same outputs)
    - Replayable (can reproduce extraction)
    - Provenance-tracked (source of each feature)
    - Governed (follows null handling policies)
    """

    def __init__(self, schema: FeatureSchema):
        self.schema = schema
        self.extraction_functions: dict[str, Callable] = {}
        self._register_extraction_functions()

    @abstractmethod
    def _register_extraction_functions(self) -> None:
        """Register feature extraction functions."""
        pass

    def extract_features(
        self,
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        semantic_clock: int | None = None
    ) -> FeatureExtractionResult:
        """
        Extract features deterministically with full provenance.

        Args:
            context: Input context for extraction
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            semantic_clock: Semantic clock for temporal consistency

        Returns:
            Feature extraction result with provenance
        """
        extraction_id = self._generate_extraction_id(trace_id, replay_key)
        start_time = time.time()

        # Create deterministic context hash
        context_hash = self._compute_context_hash(context, trace_id, replay_key, policy_hash, semantic_clock)

        features = {}
        provenance = {}
        errors = []

        try:
            # Extract each feature
            for feature_def in self.schema.features:
                try:
                    feature_value, feature_provenance = self._extract_single_feature(
                        feature_def, context, context_hash, extraction_id
                    )

                    if feature_value is not None:
                        features[feature_def.name] = feature_value
                        provenance[feature_def.name] = feature_provenance
                    elif feature_def.required:
                        errors.append(f"Required feature '{feature_def.name}' could not be extracted")

                except Exception as e:
                    error_msg = f"Error extracting feature '{feature_def.name}': {str(e)}"
                    errors.append(error_msg)

                    # Handle null according to schema
                    if feature_def.null_handling == NullHandling.DEFAULT_VALUE:
                        features[feature_def.name] = feature_def.default_value
                    elif feature_def.required and feature_def.null_handling == NullHandling.FAIL_CLOSED:
                        # Critical error for required feature
                        errors.append(f"CRITICAL: Required feature '{feature_def.name}' failed extraction")

            # Validate features against schema
            is_valid, validation_errors = self.schema.validate_features(features)
            errors.extend(validation_errors)

            # Compute deterministic hash of extraction
            deterministic_hash = self._compute_extraction_hash(features, context_hash)

            # Create extraction metadata
            extraction_metadata = {
                'extraction_id': extraction_id,
                'trace_id': trace_id,
                'replay_key': replay_key,
                'policy_hash': policy_hash,
                'semantic_clock': semantic_clock,
                'context_hash': context_hash,
                'extraction_timestamp': datetime.now().isoformat(),
                'extraction_duration_ms': (time.time() - start_time) * 1000,
                'schema_version': self.schema.schema_version,
                'schema_digest': self.schema.schema_digest,
                'feature_count': len(features),
                'extraction_success': is_valid and len(errors) == 0
            }

            # Log extraction trace
            _emit_records_execution_trace(
                root_trace_id=trace_id,
                layer="L1_ML_DECISION_SUPPORT",
                operation="features_extracted"
            )

            return FeatureExtractionResult(
                features=features,
                provenance=provenance,
                extraction_metadata=extraction_metadata,
                success=is_valid and len(errors) == 0,
                error_messages=errors,
                extraction_id=extraction_id,
                deterministic_hash=deterministic_hash
            )

        except Exception as e:
            # Catastrophic failure
            error_msg = f"Catastrophic extraction failure: {str(e)}"
            errors.append(error_msg)

            extraction_metadata = {
                'extraction_id': extraction_id,
                'trace_id': trace_id,
                'replay_key': replay_key,
                'policy_hash': policy_hash,
                'extraction_timestamp': datetime.now().isoformat(),
                'extraction_duration_ms': (time.time() - start_time) * 1000,
                'extraction_success': False,
                'catastrophic_error': error_msg
            }

            return FeatureExtractionResult(
                features={},
                provenance={},
                extraction_metadata=extraction_metadata,
                success=False,
                error_messages=errors,
                extraction_id=extraction_id,
                deterministic_hash=""
            )

    def _extract_single_feature(
        self,
        feature_def: FeatureDefinition,
        context: dict[str, Any],
        context_hash: str,
        extraction_id: str
    ) -> tuple[Any | None, FeatureProvenance]:
        """
        Extract a single feature with provenance tracking.

        Args:
            feature_def: Feature definition
            context: Input context
            context_hash: Hash of context for reproducibility
            extraction_id: Extraction ID

        Returns:
            Tuple of (feature_value, provenance)
        """
        # Get extraction function
        extraction_function = self.extraction_functions.get(feature_def.name)
        if not extraction_function:
            raise ValueError(f"No extraction function for feature '{feature_def.name}'")

        # Extract feature
        start_time = time.time()
        feature_value = extraction_function(context)
        extraction_time = (time.time() - start_time) * 1000

        # Validate feature value
        if not self._validate_feature_value(feature_value, feature_def):
            raise ValueError(f"Feature value validation failed for '{feature_def.name}'")

        # Create provenance
        provenance = FeatureProvenance(
            feature_name=feature_def.name,
            source=feature_def.provenance,
            extraction_function=feature_def.extraction_function or feature_def.name,
            extraction_timestamp=datetime.now(),
            input_hash=context_hash,
            confidence=self._compute_feature_confidence(feature_value, feature_def),
            processing_steps=[f"extract_{feature_def.name}", f"validate_{feature_def.name}"],
            version=feature_def.version
        )

        return feature_value, provenance

    def _validate_feature_value(self, value: Any, feature_def: FeatureDefinition) -> bool:
        """Validate feature value against definition."""
        if value is None:
            return not feature_def.required

        # Type validation
        type_map = {
            "numeric": (int, float),
            "categorical": str,
            "boolean": bool,
            "text": str,
            "timestamp": (str, datetime),
            "list": list,
            "dict": dict
        }

        expected_types = type_map.get(feature_def.feature_type.value)
        if expected_types and not isinstance(value, expected_types):
            return False

        # Value validation rules
        if feature_def.validation_rules:
            if feature_def.feature_type.value == "numeric":
                if "min_value" in feature_def.validation_rules:
                    if value < feature_def.validation_rules["min_value"]:
                        return False
                if "max_value" in feature_def.validation_rules:
                    if value > feature_def.validation_rules["max_value"]:
                        return False
            elif feature_def.feature_type.value == "categorical":
                if "allowed_values" in feature_def.validation_rules:
                    if value not in feature_def.validation_rules["allowed_values"]:
                        return False

        return True

    def _compute_feature_confidence(self, value: Any, feature_def: FeatureDefinition) -> float:
        """Compute confidence in feature value."""
        if value is None:
            return 0.0

        # Base confidence depends on feature type and source
        base_confidence = 0.8

        # Adjust based on source reliability
        if "system" in feature_def.provenance.lower():
            base_confidence += 0.1
        elif "user" in feature_def.provenance.lower():
            base_confidence -= 0.1

        # Adjust based on feature completeness
        if feature_def.required:
            base_confidence += 0.1

        return min(1.0, max(0.0, base_confidence))

    def _generate_extraction_id(self, trace_id: str, replay_key: str) -> str:
        """Generate unique extraction ID."""
        timestamp = int(time.time() * 1000)
        base_string = f"{trace_id}:{replay_key}:{timestamp}"
        return hashlib.md5(base_string.encode()).hexdigest()[:16]

    def _compute_context_hash(
        self,
        context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        semantic_clock: int | None
    ) -> str:
        """Compute deterministic hash of extraction context."""
        # Create deterministic context representation
        context_dict = {
            'trace_id': trace_id,
            'replay_key': replay_key,
            'policy_hash': policy_hash,
            'semantic_clock': semantic_clock,
            'context': self._normalize_context(context)
        }

        context_str = json.dumps(context_dict, sort_keys=True, default=str)
        return hashlib.sha256(context_str.encode()).hexdigest()

    def _normalize_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Normalize context for deterministic hashing."""
        normalized = {}

        for key, value in context.items():
            if isinstance(value, dict):
                normalized[key] = self._normalize_context(value)
            elif isinstance(value, list):
                normalized[key] = [str(item) for item in value]
            elif isinstance(value, (int, float, str, bool)):
                normalized[key] = value
            else:
                # Convert complex objects to string representation
                normalized[key] = str(value)

        return normalized

    def _compute_extraction_hash(self, features: dict[str, Any], context_hash: str) -> str:
        """Compute deterministic hash of extraction result."""
        extraction_data = {
            'context_hash': context_hash,
            'schema_digest': self.schema.schema_digest,
            'features': {k: str(v) for k, v in sorted(features.items())}
        }

        extraction_str = json.dumps(extraction_data, sort_keys=True)
        return hashlib.sha256(extraction_str.encode()).hexdigest()

    def replay_extraction(
        self,
        extraction_id: str,
        original_context: dict[str, Any],
        original_trace_id: str,
        original_replay_key: str,
        original_policy_hash: str,
        original_semantic_clock: int | None = None
    ) -> FeatureExtractionResult:
        """
        Replay feature extraction for determinism validation.

        Args:
            extraction_id: Original extraction ID
            original_context: Original context
            original_trace_id: Original trace ID
            original_replay_key: Original replay key
            original_policy_hash: Original policy hash
            original_semantic_clock: Original semantic clock

        Returns:
            Replayed extraction result
        """
        # Extract features with same inputs
        result = self.extract_features(
            context=original_context,
            trace_id=original_trace_id,
            replay_key=original_replay_key,
            policy_hash=original_policy_hash,
            semantic_clock=original_semantic_clock
        )

        # Add replay metadata
        result.extraction_metadata.update({
            'is_replay': True,
            'original_extraction_id': extraction_id,
            'replay_timestamp': datetime.now().isoformat()
        })

        return result

    def register_extraction_function(self, feature_name: str, function: Callable) -> None:
        """Register a feature extraction function."""
        self.extraction_functions[feature_name] = function

    def get_schema(self) -> FeatureSchema:
        """Get the feature schema."""
        return self.schema
