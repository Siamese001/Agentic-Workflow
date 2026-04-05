"""
Semantic Cache Classifier

Exponentially Weighted Moving Average (EWMA) model for classifying
semantic cache entries based on usage patterns, access frequency,
and content relevance.
"""

import pickle
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from ..config.feature_schemas import FeatureSchema
from ..config.model_registry import DecisionMode
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType


class EWMACacheClassifier(BaseMLModel):
    """
    EWMA-based semantic cache classifier.

    Classifies cache entries based on:
    - Access frequency and recency patterns
    - Content relevance and semantic similarity
    - Cache hit/miss ratios
    - Temporal access patterns
    - Resource utilization metrics
    - User query patterns

    Always operates in advisory mode - provides recommendations for cache management.
    """

    # Cache classification mapping
    CACHE_MAPPING = {
        0: "Hot",
        1: "Warm",
        2: "Cold",
        3: "Stale"
    }

    # Reverse mapping
    REVERSE_CACHE_MAPPING = {v: k for k, v in CACHE_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        super().__init__(
            model_name="semantic_cache_classifier",
            model_version="1.0",
            model_type="ewma",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path
        )

        # Create feature schema for cache classifier
        self.feature_schema = self._create_cache_schema()

        # EWMA parameters
        self.alpha = 0.3  # Smoothing factor (0 < alpha < 1)
        self.decay_factor = 0.95  # Daily decay factor

        # Cache state tracking
        self.cache_entries = {}  # cache_id -> entry_data
        self.access_history = {}  # cache_id -> deque of access timestamps
        self.ewma_scores = {}  # cache_id -> ewma_score

        # Feature names for model
        self.feature_names = [
            'access_frequency',
            'recency_score',
            'hit_ratio',
            'access_pattern_regularity',
            'content_relevance',
            'semantic_similarity',
            'resource_utilization',
            'temporal_decay',
            'user_preference',
            'cache_efficiency'
        ]

        # Default thresholds
        self.threshold_config = {
            "hot_threshold": 0.7,
            "warm_threshold": 0.4,
            "cold_threshold": 0.2,
            "stale_threshold": 0.1
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def _create_cache_schema(self) -> FeatureSchema:
        """Create feature schema for cache classifier."""
        from ..config.feature_schemas import FeatureDefinition, FeatureSchema, FeatureType

        features = [
            FeatureDefinition(
                name="access_frequency",
                feature_type=FeatureType.NUMERIC,
                description="Frequency of cache access",
                provenance="cache.access.frequency",
                validation_rules={"min_value": 0.0, "max_value": 1000.0}
            ),
            FeatureDefinition(
                name="recency_score",
                feature_type=FeatureType.NUMERIC,
                description="Recency of last access",
                provenance="cache.access.recency",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="hit_ratio",
                feature_type=FeatureType.NUMERIC,
                description="Cache hit ratio",
                provenance="cache.performance.hit_ratio",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="access_pattern_regularity",
                feature_type=FeatureType.NUMERIC,
                description="Regularity of access patterns",
                provenance="cache.pattern.regularity",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="content_relevance",
                feature_type=FeatureType.NUMERIC,
                description="Content relevance score",
                provenance="cache.content.relevance",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="semantic_similarity",
                feature_type=FeatureType.NUMERIC,
                description="Semantic similarity to queries",
                provenance="cache.semantic.similarity",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="resource_utilization",
                feature_type=FeatureType.NUMERIC,
                description="Resource utilization efficiency",
                provenance="cache.resource.utilization",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="temporal_decay",
                feature_type=FeatureType.NUMERIC,
                description="Temporal decay factor",
                provenance="cache.temporal.decay",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="user_preference",
                feature_type=FeatureType.NUMERIC,
                description="User preference score",
                provenance="cache.user.preference",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            ),
            FeatureDefinition(
                name="cache_efficiency",
                feature_type=FeatureType.NUMERIC,
                description="Overall cache efficiency",
                provenance="cache.performance.efficiency",
                validation_rules={"min_value": 0.0, "max_value": 1.0}
            )
        ]

        return FeatureSchema(
            schema_name="semantic_cache_classifier",
            schema_version="1.0",
            description="Features for semantic cache classification model",
            features=features
        )

    def load_model(self) -> None:
        """Load the EWMA model state from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            with open(self.model_file_path, 'rb') as f:
                model_data = pickle.load(f)

            self.cache_entries = model_data.get('cache_entries', {})
            self.access_history = model_data.get('access_history', {})
            self.ewma_scores = model_data.get('ewma_scores', {})
            self.alpha = model_data.get('alpha', 0.3)
            self.decay_factor = model_data.get('decay_factor', 0.95)
            self.threshold_config = model_data.get('threshold_config', self.threshold_config)
            self._training_data_digest = model_data.get('training_data_digest', '')

            self.is_loaded = True

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the model state to file."""
        model_data = {
            'cache_entries': self.cache_entries,
            'access_history': self.access_history,
            'ewma_scores': self.ewma_scores,
            'alpha': self.alpha,
            'decay_factor': self.decay_factor,
            'threshold_config': self.threshold_config,
            'training_data_digest': getattr(self, '_training_data_digest', ''),
            'model_metadata': {
                'model_name': self.model_name,
                'model_version': self.model_version,
                'model_type': self.model_type,
                'prediction_type': self.prediction_type.value,
                'class_names': list(self.CACHE_MAPPING.values()),
                'feature_schema_digest': self.feature_schema.schema_digest,
                'saved_at': datetime.now().isoformat(),
                'total_cache_entries': len(self.cache_entries)
            }
        }

        with open(model_file_path, 'wb') as f:
            pickle.dump(model_data, f)

    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY
    ) -> ModelPrediction:
        """
        Predict cache classification for a cache entry.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Cache classification prediction with full metadata
        """
        # Preprocess features
        processed_features, preprocessing_steps = self.preprocess_features(model_input.features)
        model_input.preprocessing_applied = preprocessing_steps

        # Extract features in correct order
        feature_vector = self._extract_feature_vector(processed_features)

        if feature_vector is None:
            # Failed to extract features
            return self.create_prediction(
                prediction="Cold",  # Default classification
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

        try:
            # Make EWMA prediction
            start_time = datetime.now()

            # Calculate EWMA score
            ewma_score = self._calculate_ewma_score(feature_vector)

            # Classify based on EWMA score and thresholds
            predicted_class = self._classify_by_ewma_score(ewma_score)
            predicted_classification = self.CACHE_MAPPING.get(predicted_class, "Cold")

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Calculate confidence based on EWMA characteristics
            confidence = self._calculate_ewma_confidence(ewma_score, feature_vector)

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("warm_threshold", 0.4)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_classification,
                    confidence=confidence,
                    threshold_used=threshold_used
                )
            )

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_classification,
                confidence=confidence,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=decision_mode,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

            # Add prediction metadata
            prediction.model_metadata.update({
                'prediction_time_ms': prediction_time * 1000,
                'feature_vector_length': len(feature_vector),
                'preprocessing_steps': preprocessing_steps,
                'ewma_score': ewma_score,
                'raw_prediction_class': predicted_class,
                'thresholds_passed': passes_threshold,
                'cache_classification': predicted_classification,
                'cache_action': self._get_recommended_action(predicted_classification)
            })

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except Exception as e:
            # Prediction failed
            return self.create_prediction(
                prediction="Cold",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

    def update_cache_entry(
        self,
        cache_id: str,
        access_event: dict[str, Any],
        current_time: datetime | None = None
    ) -> None:
        """
        Update cache entry with new access event.

        Args:
            cache_id: Unique cache entry identifier
            access_event: Access event data
            current_time: Current timestamp (defaults to now)
        """
        if current_time is None:
            current_time = datetime.now()

        # Initialize cache entry if not exists
        if cache_id not in self.cache_entries:
            self.cache_entries[cache_id] = {
                'created_at': current_time,
                'last_access': current_time,
                'access_count': 0,
                'hit_count': 0,
                'miss_count': 0,
                'content_relevance': 0.5,
                'semantic_similarity': 0.5,
                'resource_utilization': 0.5
            }
            self.access_history[cache_id] = deque(maxlen=100)  # Keep last 100 accesses
            self.ewma_scores[cache_id] = 0.5  # Initial EWMA score

        # Update entry
        entry = self.cache_entries[cache_id]
        entry['last_access'] = current_time
        entry['access_count'] += 1

        # Update access history
        self.access_history[cache_id].append(current_time)

        # Update hit/miss counts
        event_type = access_event.get('type', 'hit')
        if event_type == 'hit':
            entry['hit_count'] += 1
        elif event_type == 'miss':
            entry['miss_count'] += 1

        # Update content metrics if provided
        if 'content_relevance' in access_event:
            entry['content_relevance'] = access_event['content_relevance']
        if 'semantic_similarity' in access_event:
            entry['semantic_similarity'] = access_event['semantic_similarity']
        if 'resource_utilization' in access_event:
            entry['resource_utilization'] = access_event['resource_utilization']

        # Calculate new EWMA score
        features = self._extract_features_from_entry(cache_id)
        new_ewma_score = self._calculate_ewma_score(features)

        # Apply EWMA smoothing
        old_ewma_score = self.ewma_scores[cache_id]
        self.ewma_scores[cache_id] = (self.alpha * new_ewma_score) + ((1 - self.alpha) * old_ewma_score)

    def classify_cache_entry(
        self,
        cache_id: str,
        trace_id: str,
        replay_key: str,
        policy_hash: str
    ) -> ModelPrediction:
        """
        Classify a specific cache entry.

        Args:
            cache_id: Cache entry identifier
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Cache classification prediction
        """
        if cache_id not in self.cache_entries:
            # Cache entry not found
            return self.create_prediction(
                prediction="Cold",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash
            )

        # Extract features from cache entry
        features = self._extract_features_from_entry(cache_id)

        # Validate input
        model_input = self.validate_input(features)

        # Make prediction
        return self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash
        )

    def get_cache_recommendations(
        self,
        cache_id: str,
        trace_id: str,
        replay_key: str,
        policy_hash: str
    ) -> dict[str, Any]:
        """
        Get comprehensive cache management recommendations.

        Args:
            cache_id: Cache entry identifier
            trace_id: Trace ID
            replay_key: Replay key
            policy_hash: Policy hash

        Returns:
            Cache management recommendations
        """
        # Get classification
        prediction = self.classify_cache_entry(
            cache_id=cache_id,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash
        )

        # Get cache entry details
        entry = self.cache_entries.get(cache_id, {})
        ewma_score = self.ewma_scores.get(cache_id, 0.0)

        # Generate recommendations
        recommendations = self._generate_cache_recommendations(
            classification=prediction.prediction,
            entry=entry,
            ewma_score=ewma_score
        )

        # Calculate cache statistics
        stats = self._calculate_cache_statistics(cache_id)

        return {
            'cache_id': cache_id,
            'classification': prediction.prediction,
            'confidence': prediction.confidence,
            'ewma_score': ewma_score,
            'top_factors': prediction.top_features,
            'recommendations': recommendations,
            'statistics': stats,
            'recommended_action': self._get_recommended_action(prediction.prediction),
            'priority': self._get_cache_priority(prediction.prediction, ewma_score)
        }

    def _extract_features_from_entry(self, cache_id: str) -> dict[str, float]:
        """Extract features from cache entry data."""
        entry = self.cache_entries.get(cache_id, {})
        access_history = self.access_history.get(cache_id, deque())

        now = datetime.now()

        # Access frequency (accesses per day)
        if entry.get('created_at'):
            age_days = max(1, (now - entry['created_at']).days)
            access_frequency = entry.get('access_count', 0) / age_days
        else:
            access_frequency = 0.0

        # Recency score (how recent was last access)
        if entry.get('last_access'):
            hours_since_access = (now - entry['last_access']).total_seconds() / 3600
            recency_score = max(0.0, 1.0 - (hours_since_access / 168.0))  # 1 week decay
        else:
            recency_score = 0.0

        # Hit ratio
        total_accesses = entry.get('hit_count', 0) + entry.get('miss_count', 0)
        hit_ratio = entry.get('hit_count', 0) / max(1, total_accesses)

        # Access pattern regularity (variance in access intervals)
        if len(access_history) > 1:
            access_times = list(access_history)
            intervals = [(access_times[i+1] - access_times[i]).total_seconds()
                        for i in range(len(access_times)-1)]

            if intervals:
                mean_interval = sum(intervals) / len(intervals)
                variance = sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)
                # Lower variance = higher regularity
                regularity = max(0.0, 1.0 - (variance / (86400 * 7)))  # Normalize by week variance
            else:
                regularity = 0.5
        else:
            regularity = 0.5

        # Content relevance and semantic similarity (from entry)
        content_relevance = entry.get('content_relevance', 0.5)
        semantic_similarity = entry.get('semantic_similarity', 0.5)

        # Resource utilization (from entry)
        resource_utilization = entry.get('resource_utilization', 0.5)

        # Temporal decay (based on age)
        if entry.get('created_at'):
            age_days = (now - entry['created_at']).days
            temporal_decay = self.decay_factor ** age_days
        else:
            temporal_decay = 1.0

        # User preference (based on hit ratio and recency)
        user_preference = (hit_ratio * 0.6) + (recency_score * 0.4)

        # Cache efficiency (combination of hit ratio and resource utilization)
        cache_efficiency = (hit_ratio * 0.7) + (resource_utilization * 0.3)

        return {
            'access_frequency': min(1000.0, access_frequency),
            'recency_score': recency_score,
            'hit_ratio': hit_ratio,
            'access_pattern_regularity': regularity,
            'content_relevance': content_relevance,
            'semantic_similarity': semantic_similarity,
            'resource_utilization': resource_utilization,
            'temporal_decay': temporal_decay,
            'user_preference': user_preference,
            'cache_efficiency': cache_efficiency
        }

    def _calculate_ewma_score(self, feature_vector: np.ndarray) -> float:
        """Calculate EWMA score from feature vector."""
        # Feature weights (can be tuned)
        weights = np.array([
            0.15,  # access_frequency
            0.20,  # recency_score
            0.20,  # hit_ratio
            0.10,  # access_pattern_regularity
            0.10,  # content_relevance
            0.10,  # semantic_similarity
            0.05,  # resource_utilization
            0.05,  # temporal_decay
            0.03,  # user_preference
            0.02   # cache_efficiency
        ])

        # Weighted sum
        weighted_score = np.dot(feature_vector, weights)

        return float(np.clip(weighted_score, 0.0, 1.0))

    def _classify_by_ewma_score(self, ewma_score: float) -> int:
        """Classify cache entry based on EWMA score."""
        if ewma_score >= self.threshold_config.get("hot_threshold", 0.7):
            return 0  # Hot
        elif ewma_score >= self.threshold_config.get("warm_threshold", 0.4):
            return 1  # Warm
        elif ewma_score >= self.threshold_config.get("cold_threshold", 0.2):
            return 2  # Cold
        else:
            return 3  # Stale

    def _calculate_ewma_confidence(self, ewma_score: float, feature_vector: np.ndarray) -> float:
        """Calculate confidence based on EWMA characteristics."""
        # Base confidence from score magnitude
        if ewma_score > 0.8:
            base_confidence = 0.9
        elif ewma_score > 0.6:
            base_confidence = 0.8
        elif ewma_score > 0.4:
            base_confidence = 0.7
        elif ewma_score > 0.2:
            base_confidence = 0.6
        else:
            base_confidence = 0.5

        # Adjust based on feature variance (higher variance = lower confidence)
        feature_variance = np.var(feature_vector)
        variance_factor = max(0.8, 1.0 - (feature_variance / 4.0))  # Normalize variance

        # Adjust based on access history length (more history = higher confidence)
        # This would require access to cache_id, which we don't have in this context
        history_factor = 1.0  # Placeholder

        confidence = base_confidence * variance_factor * history_factor
        return round(min(1.0, max(0.0, confidence)), 3)

    def _extract_feature_vector(self, features: dict[str, Any]) -> np.ndarray | None:
        """Extract features in the correct order for the model."""
        try:
            feature_vector = []
            for feature_name in self.feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            return np.array(feature_vector)

        except Exception as e:
            return None

    def _get_recommended_action(self, classification: str) -> str:
        """Get recommended action for cache classification."""
        actions = {
            "Hot": "Keep in cache, prioritize for retention",
            "Warm": "Keep in cache, monitor for changes",
            "Cold": "Consider eviction if space needed",
            "Stale": "Evict from cache immediately"
        }
        return actions.get(classification, "Monitor cache entry")

    def _generate_cache_recommendations(
        self,
        classification: str,
        entry: dict[str, Any],
        ewma_score: float
    ) -> list[str]:
        """Generate cache management recommendations."""
        recommendations = []

        # Base recommendations by classification
        if classification == "Hot":
            recommendations.extend([
                "Keep entry in primary cache tier",
                "Consider preloading related content",
                "Monitor for performance impact"
            ])
        elif classification == "Warm":
            recommendations.extend([
                "Maintain in cache with regular monitoring",
                "Consider content refresh if available",
                "Track access patterns for optimization"
            ])
        elif classification == "Cold":
            recommendations.extend([
                "Consider eviction during cache cleanup",
                "Move to secondary storage if valuable",
                "Review content relevance"
            ])
        else:  # Stale
            recommendations.extend([
                "Evict immediately",
                "Remove from all cache tiers",
                "Consider content refresh if still relevant"
            ])

        # Score-based recommendations
        if ewma_score > 0.8:
            recommendations.append("High-value entry - preserve aggressively")
        elif ewma_score < 0.2:
            recommendations.append("Low-value entry - prioritize for eviction")

        # Entry-specific recommendations
        hit_ratio = entry.get('hit_count', 0) / max(1, entry.get('hit_count', 0) + entry.get('miss_count', 0))
        if hit_ratio < 0.3:
            recommendations.append("Low hit ratio - consider eviction")
        elif hit_ratio > 0.8:
            recommendations.append("High hit ratio - preserve in cache")

        return recommendations

    def _calculate_cache_statistics(self, cache_id: str) -> dict[str, Any]:
        """Calculate statistics for cache entry."""
        entry = self.cache_entries.get(cache_id, {})
        access_history = self.access_history.get(cache_id, deque())

        now = datetime.now()

        stats = {
            'access_count': entry.get('access_count', 0),
            'hit_count': entry.get('hit_count', 0),
            'miss_count': entry.get('miss_count', 0),
            'hit_ratio': entry.get('hit_count', 0) / max(1, entry.get('hit_count', 0) + entry.get('miss_count', 0)),
            'created_at': entry.get('created_at'),
            'last_access': entry.get('last_access'),
            'age_days': (now - entry.get('created_at', now)).days if entry.get('created_at') else 0,
            'hours_since_last_access': (now - entry.get('last_access', now)).total_seconds() / 3600 if entry.get('last_access') else float('inf'),
            'access_history_length': len(access_history),
            'ewma_score': self.ewma_scores.get(cache_id, 0.0)
        }

        return stats

    def _get_cache_priority(self, classification: str, ewma_score: float) -> str:
        """Get cache priority level."""
        if classification == "Hot":
            return "Critical"
        elif classification == "Warm":
            return "High"
        elif classification == "Cold":
            return "Medium"
        else:
            return "Low"

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        # For EWMA, importance is based on feature weights
        weights = {
            'recency_score': 0.20,
            'hit_ratio': 0.20,
            'access_frequency': 0.15,
            'access_pattern_regularity': 0.10,
            'content_relevance': 0.10,
            'semantic_similarity': 0.10,
            'resource_utilization': 0.05,
            'temporal_decay': 0.05,
            'user_preference': 0.03,
            'cache_efficiency': 0.02
        }

        feature_importance = []
        for i, feature_name in enumerate(self.feature_names):
            feature_importance.append({
                'feature_name': feature_name,
                'importance_score': weights.get(feature_name, 0.0),
                'feature_value': model_input.features.get(feature_name),
                'rank': i + 1,
                'weight': weights.get(feature_name, 0.0)
            })

        # Sort by importance
        feature_importance.sort(key=lambda x: x['importance_score'], reverse=True)

        # Update ranks
        for i, feature in enumerate(feature_importance):
            feature['rank'] = i + 1

        return feature_importance

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for EWMA."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for EWMA
        for key, value in processed_features.items():
            # Ensure all features are numeric and in valid range
            if isinstance(value, str):
                try:
                    processed_features[key] = float(value)
                    preprocessing_steps.append(f"string_to_numeric_{key}")
                except ValueError:
                    processed_features[key] = 0.0
                    preprocessing_steps.append(f"string_to_default_{key}")
            elif not isinstance(value, (int, float)):
                processed_features[key] = 0.0
                preprocessing_steps.append(f"non_numeric_to_default_{key}")

            # Clip to valid ranges
            if key in ['recency_score', 'hit_ratio', 'access_pattern_regularity', 'content_relevance',
                      'semantic_similarity', 'resource_utilization', 'temporal_decay', 'user_preference', 'cache_efficiency']:
                processed_features[key] = max(0.0, min(1.0, float(processed_features[key])))
            elif key == 'access_frequency':
                processed_features[key] = max(0.0, min(1000.0, float(processed_features[key])))

        return processed_features, preprocessing_steps

    def train_model(
        self,
        training_data: list[dict[str, Any]],
        training_data_digest: str = ""
    ) -> None:
        """
        Train the EWMA model (update parameters based on training data).

        Args:
            training_data: List of training examples with features and labels
            training_data_digest: Digest of training data for provenance
        """
        # For EWMA, "training" means updating the alpha parameter based on data characteristics

        # Calculate optimal alpha based on data volatility
        all_features = []
        for example in training_data:
            features = example['features']
            feature_vector = []
            for feature_name in self.feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))
            all_features.append(feature_vector)

        if all_features:
            # Calculate variance across all features to determine optimal smoothing
            all_features_array = np.array(all_features)
            feature_variances = np.var(all_features_array, axis=0)
            avg_variance = np.mean(feature_variances)

            # Higher variance -> lower alpha (more smoothing)
            # Lower variance -> higher alpha (more responsive)
            if avg_variance > 0.25:
                self.alpha = 0.2
            elif avg_variance > 0.1:
                self.alpha = 0.3
            else:
                self.alpha = 0.4

        # Store training digest
        self._training_data_digest = training_data_digest
        self.is_loaded = True
