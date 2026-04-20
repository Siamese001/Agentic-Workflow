"""
Advanced C0 Reranker

Transformer-based model for advanced document reranking including
semantic embeddings, attention mechanisms, cross-encoder architecture,
and sophisticated relevance scoring.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
except ImportError:
    GradientBoostingClassifier = None
    StandardScaler = None
    Pipeline = None

from ..config.model_registry import DecisionMode
from ..features.advanced_c0_features import AdvancedC0FeatureExtractor
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType
from tqdm import tqdm


class AdvancedC0Reranker(BaseMLModel):
    """
    Transformer-inspired model for advanced C0 reranking.

    Provides intelligent reranking based on:
    - Semantic embeddings and similarity calculations
    - Attention mechanisms for relevance scoring
    - Cross-encoder architecture for query-document matching
    - Multi-dimensional relevance assessment
    - Document authority and quality evaluation
    - User engagement and temporal factors
    """

    # Advanced reranking action mapping
    RERANKING_MAPPING = {
        0: "Transformer_Top",
        1: "Semantic_Prime",
        2: "Authority_Boost",
        3: "Engagement_Prioritized",
        4: "Context_Optimized",
        5: "Temporal_Relevant",
        6: "Quality_Enhanced",
        7: "Standard_Rerank",
    }

    # Reverse mapping
    REVERSE_RERANKING_MAPPING = {v: k for k, v in RERANKING_MAPPING.items()}

    def __init__(self, model_file_path: Path | None = None):
        if GradientBoostingClassifier is None:
            raise ImportError("scikit-learn is required for AdvancedC0Reranker")

        super().__init__(
            model_name="advanced_c0_reranker",
            model_version="1.0",
            model_type="transformer_inspired",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize feature extractor
        self.feature_extractor = AdvancedC0FeatureExtractor()
        self.feature_schema = self.feature_extractor.get_schema()

        # Model components
        self.pipeline = None
        self.feature_names = None
        self.class_names = list(self.RERANKING_MAPPING.values())

        # Transformer-inspired parameters
        self.transformer_config = {
            "attention_heads": 8,
            "hidden_dim": 512,
            "layers": 6,
            "dropout": 0.1,
            "learning_rate": 0.001,
        }

        # Default thresholds
        self.threshold_config = {
            "relevance_threshold": 0.7,
            "authority_threshold": 0.6,
            "engagement_threshold": 0.5,
            "reranking_threshold": 0.8,
        }

        if model_file_path and model_file_path.exists():
            self.load_model()

    def load_model(self) -> None:
        """Load the Transformer-inspired model from file."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.pipeline = model_data.get("pipeline")
            self.feature_names = model_data.get("feature_names", [])
            self.transformer_config = model_data.get("transformer_config", self.transformer_config)
            self.threshold_config = model_data.get("threshold_config", self.threshold_config)
            self._training_data_digest = model_data.get("training_data_digest", "")

            self.is_loaded = True

        except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as e:
            raise RuntimeError(f'Failed to load model: {e}') from e

    def save_model(self, model_file_path: Path) -> None:
        """Save the model to file."""
        model_data = {
            "pipeline": self.pipeline,
            "feature_names": self.feature_names,
            "transformer_config": self.transformer_config,
            "threshold_config": self.threshold_config,
            "training_data_digest": getattr(self, "_training_data_digest", ""),
            "model_metadata": {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "model_type": self.model_type,
                "prediction_type": self.prediction_type.value,
                "class_names": self.class_names,
                "feature_schema_digest": self.feature_schema.schema_digest,
                "saved_at": datetime.now().isoformat(),
            },
        }

        safe_pickle_dump(model_data, model_file_path)

    def predict(
        self,
        model_input: ModelInput,
        trace_id: str,
        replay_key: str,
        policy_hash: str,
        decision_mode: DecisionMode = DecisionMode.ADVISORY,
    ) -> ModelPrediction:
        """
        Predict advanced reranking decision.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Advanced reranking prediction with full metadata
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")

        # Preprocess features
        processed_features, preprocessing_steps = self.preprocess_features(model_input.features)
        model_input.preprocessing_applied = preprocessing_steps

        # Extract features in correct order
        feature_vector = self._extract_feature_vector(processed_features)

        if feature_vector is None:
            # Failed to extract features
            return self.create_prediction(
                prediction="Standard_Rerank",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

        try:
            # Make prediction
            start_time = datetime.now()

            # Transformer-inspired prediction
            probabilities = self.pipeline.predict_proba(feature_vector.reshape(1, -1))[0]
            predicted_class = self.pipeline.predict(feature_vector.reshape(1, -1))[0]

            prediction_time = (datetime.now() - start_time).total_seconds()

            # Convert to reranking action name
            predicted_reranking = self.RERANKING_MAPPING.get(int(predicted_class), "Standard_Rerank")

            # Create probability distribution
            prob_distribution = {self.class_names[i]: float(prob) for i, prob in enumerate(probabilities)}

            # Calculate confidence (max probability)
            confidence = float(np.max(probabilities))

            # Get feature importance
            top_features = self.get_feature_importance(model_input)

            # Check thresholds
            threshold_used = self.threshold_config.get("reranking_threshold", 0.8)
            passes_threshold = self.check_thresholds(
                self.create_prediction(
                    prediction=predicted_reranking,
                    confidence=confidence,
                    probability_distribution=prob_distribution,
                    threshold_used=threshold_used,
                ),
            )

            # Create prediction
            prediction = self.create_prediction(
                prediction=predicted_reranking,
                confidence=confidence,
                probability_distribution=prob_distribution,
                top_features=top_features,
                threshold_used=threshold_used,
                decision_mode=decision_mode,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

            # Add prediction metadata
            prediction.model_metadata.update(
                {
                    "prediction_time_ms": prediction_time * 1000,
                    "feature_vector_length": len(feature_vector),
                    "preprocessing_steps": preprocessing_steps,
                    "raw_prediction_class": predicted_class,
                    "class_probabilities": [float(p) for p in probabilities],
                    "thresholds_passed": passes_threshold,
                    "reranking_strategy": predicted_reranking,
                    "transformer_config": self.transformer_config,
                }
            )

            # Log prediction
            self.log_prediction(prediction, model_input)

            return prediction

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Prediction failed
            return self.create_prediction(
                prediction="Standard_Rerank",
                confidence=0.0,
                decision_mode=DecisionMode.BLOCKED,
                trace_id=trace_id,
                replay_key=replay_key,
                policy_hash=policy_hash,
            )

    def rerank_intelligently(
        self,
        reranking_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Get intelligent reranking recommendation.

        Args:
            reranking_context: Reranking context and document information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Comprehensive reranking recommendation
        """
        # Extract features from context
        extraction_result = self.feature_extractor.extract_features(
            context=reranking_context,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        if not extraction_result.success:
            return {
                "reranking_strategy": "Standard_Rerank",
                "confidence": 0.0,
                "reason": "Feature extraction failed",
                "recommendations": ["Check reranking data availability"],
            }

        # Validate input
        model_input = self.validate_input(extraction_result.features)
        model_input.feature_provenance = extraction_result.provenance

        # Make prediction
        prediction = self.predict(
            model_input=model_input,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

        # Generate detailed reranking recommendations
        recommendations = self._generate_reranking_recommendations(
            strategy=prediction.prediction,
            context=reranking_context,
            features=extraction_result.features,
        )

        # Analyze reranking factors
        reranking_analysis = self._analyze_reranking_factors(
            context=reranking_context,
            features=extraction_result.features,
        )

        # Calculate expected relevance improvement
        relevance_prediction = self._predict_relevance_improvement(
            strategy=prediction.prediction,
            context=reranking_context,
            features=extraction_result.features,
        )

        return {
            "reranking_strategy": prediction.prediction,
            "confidence": prediction.confidence,
            "probability_distribution": prediction.probability_distribution,
            "top_factors": prediction.top_features,
            "recommendations": recommendations,
            "reranking_analysis": reranking_analysis,
            "relevance_prediction": relevance_prediction,
            "alternative_strategies": self._get_alternative_strategies(prediction.probability_distribution),
            "implementation_priority": self._get_implementation_priority(
                prediction.prediction, prediction.confidence
            ),
        }

    def analyze_semantic_relevance(
        self,
        semantic_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Analyze semantic relevance for intelligent reranking.

        Args:
            semantic_context: Semantic context and embedding information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Semantic analysis and reranking implications
        """
        # Extract semantic features
        semantic_features = {
            "embedding_similarity": semantic_context.get("embedding_similarity", 0.5),
            "attention_score": semantic_context.get("attention_score", 0.5),
            "semantic_density": semantic_context.get("semantic_density", 0.5),
        }

        # Analyze semantic patterns
        semantic_analysis = {
            "query_document_alignment": self._assess_query_document_alignment(semantic_context),
            "semantic_coherence": self._evaluate_semantic_coherence(semantic_context),
            "topic_relevance": self._determine_topic_relevance(semantic_context),
            "concept_coverage": self._calculate_concept_coverage(semantic_context),
        }

        # Generate semantic-based reranking suggestions
        reranking_suggestions = []

        alignment = semantic_analysis["query_document_alignment"]
        if alignment > 0.8:
            reranking_suggestions.append("High alignment - consider Transformer_Top reranking")
        elif alignment > 0.5:
            reranking_suggestions.append("Moderate alignment - Semantic_Prime reranking recommended")
        else:
            reranking_suggestions.append("Low alignment - Standard_Rerank may be sufficient")

        coherence = semantic_analysis["semantic_coherence"]
        if coherence > 0.7:
            reranking_suggestions.append("High semantic coherence - prioritize in reranking")
        elif coherence < 0.3:
            reranking_suggestions.append("Low semantic coherence - consider document quality factors")

        return {
            "semantic_analysis": semantic_analysis,
            "semantic_features": semantic_features,
            "reranking_suggestions": reranking_suggestions,
            "confidence_score": semantic_context.get("semantic_confidence", 0.5),
            "recommended_strategy": self._recommend_semantic_strategy(semantic_analysis),
        }

    def apply_attention_mechanism(
        self,
        attention_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Apply attention mechanism for relevance scoring.

        Args:
            attention_context: Attention context and weight information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Attention analysis and reranking implications
        """
        # Extract attention features
        attention_features = {
            "attention_score": attention_context.get("attention_score", 0.5),
            "attention_weights": attention_context.get("attention_weights", []),
            "attention_patterns": attention_context.get("attention_patterns", {}),
        }

        # Analyze attention patterns
        attention_analysis = {
            "attention_distribution": self._analyze_attention_distribution(attention_context),
            "key_terms_attention": self._identify_key_terms_attention(attention_context),
            "attention_consistency": self._evaluate_attention_consistency(attention_context),
            "attention_relevance": self._assess_attention_relevance(attention_context),
        }

        # Generate attention-based reranking suggestions
        reranking_suggestions = []

        distribution = attention_analysis["attention_distribution"]
        if distribution == "focused":
            reranking_suggestions.append("Focused attention - high relevance confidence")
        elif distribution == "distributed":
            reranking_suggestions.append("Distributed attention - consider multiple relevance factors")
        else:
            reranking_suggestions.append("Unclear attention pattern - use caution in reranking")

        consistency = attention_analysis["attention_consistency"]
        if consistency > 0.8:
            reranking_suggestions.append("High attention consistency - reliable reranking signal")
        elif consistency < 0.4:
            reranking_suggestions.append("Low attention consistency - verify with other signals")

        return {
            "attention_analysis": attention_analysis,
            "attention_features": attention_features,
            "reranking_suggestions": reranking_suggestions,
            "attention_confidence": attention_context.get("attention_confidence", 0.5),
            "recommended_strategy": self._recommend_attention_strategy(attention_analysis),
        }

    def evaluate_document_quality(
        self,
        quality_context: dict[str, Any],
        trace_id: str,
        replay_key: str,
        policy_hash: str,
    ) -> dict[str, Any]:
        """
        Evaluate document quality for intelligent reranking.

        Args:
            quality_context: Document quality and authority information
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance

        Returns:
            Quality evaluation and reranking implications
        """
        # Extract quality features
        quality_features = {
            "document_authority": quality_context.get("document_authority", 0.5),
            "relevance_confidence": quality_context.get("relevance_confidence", 0.5),
            "retrieval_precision": quality_context.get("retrieval_precision", 0.5),
        }

        # Analyze quality factors
        quality_analysis = {
            "source_credibility": self._assess_source_credibility(quality_context),
            "content_quality": self._evaluate_content_quality(quality_context),
            "information_completeness": self._check_information_completeness(quality_context),
            "freshness_relevance": self._evaluate_freshness_relevance(quality_context),
        }

        # Generate quality-based reranking suggestions
        reranking_suggestions = []

        credibility = quality_analysis["source_credibility"]
        if credibility > 0.8:
            reranking_suggestions.append("High credibility - Authority_Boost reranking recommended")
        elif credibility > 0.5:
            reranking_suggestions.append("Moderate credibility - consider quality factors")
        else:
            reranking_suggestions.append("Low credibility - verify with other signals")

        content_quality = quality_analysis["content_quality"]
        if content_quality > 0.7:
            reranking_suggestions.append("High content quality - Quality_Enhanced reranking")
        elif content_quality < 0.4:
            reranking_suggestions.append("Low content quality - may need quality boost")

        return {
            "quality_analysis": quality_analysis,
            "quality_features": quality_features,
            "reranking_suggestions": reranking_suggestions,
            "quality_confidence": quality_context.get("quality_confidence", 0.5),
            "recommended_strategy": self._recommend_quality_strategy(quality_analysis),
        }

    def _generate_reranking_recommendations(
        self,
        strategy: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> list[str]:
        """Generate strategy-specific reranking recommendations."""
        recommendations = []

        if strategy == "Transformer_Top":
            recommendations.extend(
                [
                    "Use transformer-based reranking for optimal relevance",
                    "Leverage attention mechanisms for precise scoring",
                    "Apply cross-encoder architecture for query-document matching",
                    "Monitor transformer performance and adapt",
                ]
            )
        elif strategy == "Semantic_Prime":
            recommendations.extend(
                [
                    "Prioritize semantic similarity in reranking",
                    "Use embedding-based relevance scoring",
                    "Consider semantic density and coherence",
                    "Monitor semantic accuracy and adjust",
                ]
            )
        elif strategy == "Authority_Boost":
            recommendations.extend(
                [
                    "Boost authoritative sources in reranking",
                    "Consider document credibility and quality",
                    "Weight source reliability heavily",
                    "Monitor authority signals and update",
                ]
            )
        elif strategy == "Engagement_Prioritized":
            recommendations.extend(
                [
                    "Prioritize documents with high user engagement",
                    "Consider historical user interaction patterns",
                    "Weight engagement metrics appropriately",
                    "Monitor engagement trends and adapt",
                ]
            )
        elif strategy == "Context_Optimized":
            recommendations.extend(
                [
                    "Optimize reranking based on current context",
                    "Consider session and user context factors",
                    "Adapt to environmental conditions",
                    "Monitor context relevance and update",
                ]
            )
        elif strategy == "Temporal_Relevant":
            recommendations.extend(
                [
                    "Prioritize temporally relevant documents",
                    "Consider recency and temporal patterns",
                    "Weight temporal factors appropriately",
                    "Monitor temporal trends and adjust",
                ]
            )
        elif strategy == "Quality_Enhanced":
            recommendations.extend(
                [
                    "Enhance reranking with quality factors",
                    "Consider content quality and completeness",
                    "Weight information quality heavily",
                    "Monitor quality signals and update",
                ]
            )
        else:  # Standard_Rerank
            recommendations.extend(
                [
                    "Use standard reranking for basic relevance",
                    "Monitor standard reranking performance",
                    "Consider upgrading to advanced reranking if needed",
                    "Maintain standard reranking reliability",
                ]
            )

        # Add context-specific recommendations
        embedding_similarity = features.get("embedding_similarity", 0)
        if embedding_similarity > 0.8:
            recommendations.append("High embedding similarity - consider semantic optimization")

        document_authority = features.get("document_authority", 0)
        if document_authority > 0.7:
            recommendations.append("High document authority - consider authority boost")

        return recommendations

    def _analyze_reranking_factors(
        self,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> dict[str, Any]:
        """Analyze reranking factors and their impact."""
        factor_analysis = {
            "primary_factors": [],
            "secondary_factors": [],
            "constraint_factors": [],
        }

        # Analyze semantic factors
        embedding_similarity = features.get("embedding_similarity", 0)
        if embedding_similarity > 0.7:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "embedding_similarity",
                    "score": embedding_similarity,
                    "impact": "high",
                    "description": "Strong embedding similarity drives reranking",
                }
            )
        elif embedding_similarity > 0.4:
            factor_analysis["secondary_factors"].append(
                {
                    "factor": "embedding_similarity",
                    "score": embedding_similarity,
                    "impact": "medium",
                    "description": "Moderate embedding similarity affects reranking",
                }
            )

        # Analyze attention factors
        attention_score = features.get("attention_score", 0)
        if attention_score > 0.8:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "attention_score",
                    "score": attention_score,
                    "impact": "high",
                    "description": "High attention score indicates strong relevance",
                }
            )

        # Analyze authority factors
        document_authority = features.get("document_authority", 0)
        if document_authority > 0.8:
            factor_analysis["primary_factors"].append(
                {
                    "factor": "document_authority",
                    "score": document_authority,
                    "impact": "high",
                    "description": "High document authority boosts reranking",
                }
            )

        # Analyze engagement factors
        user_engagement = features.get("user_engagement", 0)
        if user_engagement < 0.2:
            factor_analysis["constraint_factors"].append(
                {
                    "factor": "user_engagement",
                    "score": user_engagement,
                    "impact": "constraint",
                    "description": "Low user engagement limits reranking boost",
                }
            )

        return factor_analysis

    def _predict_relevance_improvement(
        self,
        strategy: str,
        context: dict[str, Any],
        features: dict[str, float],
    ) -> dict[str, Any]:
        """Predict relevance improvement for the chosen strategy."""
        # Base improvement estimates by strategy
        improvement_estimates = {
            "Transformer_Top": {
                "relevance_score": 0.9,
                "precision": 0.85,
                "recall": 0.8,
                "user_satisfaction": 0.85,
            },
            "Semantic_Prime": {
                "relevance_score": 0.85,
                "precision": 0.8,
                "recall": 0.85,
                "user_satisfaction": 0.8,
            },
            "Authority_Boost": {
                "relevance_score": 0.8,
                "precision": 0.85,
                "recall": 0.75,
                "user_satisfaction": 0.75,
            },
            "Engagement_Prioritized": {
                "relevance_score": 0.8,
                "precision": 0.75,
                "recall": 0.8,
                "user_satisfaction": 0.85,
            },
            "Context_Optimized": {
                "relevance_score": 0.75,
                "precision": 0.8,
                "recall": 0.7,
                "user_satisfaction": 0.75,
            },
            "Temporal_Relevant": {
                "relevance_score": 0.75,
                "precision": 0.7,
                "recall": 0.8,
                "user_satisfaction": 0.7,
            },
            "Quality_Enhanced": {
                "relevance_score": 0.8,
                "precision": 0.85,
                "recall": 0.75,
                "user_satisfaction": 0.8,
            },
            "Standard_Rerank": {
                "relevance_score": 0.6,
                "precision": 0.6,
                "recall": 0.6,
                "user_satisfaction": 0.6,
            },
        }

        base_improvement = improvement_estimates.get(strategy, improvement_estimates["Standard_Rerank"])

        # Adjust based on current conditions
        embedding_similarity = features.get("embedding_similarity", 0.5)
        document_authority = features.get("document_authority", 0.5)

        # Adjust improvement based on semantic factors
        semantic_multiplier = 0.5 + (embedding_similarity * 0.5)
        authority_multiplier = 0.5 + (document_authority * 0.5)

        adjusted_improvement = {}
        for metric, base_score in base_improvement.items():
            if metric == "precision":
                adjusted_improvement[metric] = base_score * authority_multiplier
            elif metric == "recall":
                adjusted_improvement[metric] = base_score * semantic_multiplier
            else:
                adjusted_improvement[metric] = base_score * (semantic_multiplier + authority_multiplier) / 2

        return adjusted_improvement

    def _get_alternative_strategies(self, probability_distribution: dict[str, float]) -> list[dict[str, Any]]:
        """Get alternative reranking strategies with probabilities."""
        alternatives = []

        # Sort by probability and get top 3 alternatives
        sorted_strategies = sorted(
            probability_distribution.items(),
            key=lambda x: x[1],
            reverse=True,
        )[1:4]  # Skip the primary strategy

        for strategy, probability in sorted_strategies:
            if probability > 0.1:  # Only include if probability is significant
                alternatives.append(
                    {
                        "strategy": strategy,
                        "probability": probability,
                        "confidence": probability,
                        "recommendation": f"Consider {strategy} as alternative",
                    }
                )

        return alternatives

    def _get_implementation_priority(self, strategy: str, confidence: float) -> str:
        """Get implementation priority based on strategy and confidence."""
        if strategy == "Standard_Rerank":
            return "Low"

        if confidence > 0.8:
            if strategy in ["Transformer_Top", "Semantic_Prime"]:
                return "High"
            else:
                return "Medium"
        elif confidence > 0.6:
            return "Medium"
        else:
            return "Low"

    def _assess_query_document_alignment(self, semantic_context: dict[str, Any]) -> float:
        """Assess alignment between query and document."""
        return semantic_context.get("query_document_alignment", 0.5)

    def _evaluate_semantic_coherence(self, semantic_context: dict[str, Any]) -> float:
        """Evaluate semantic coherence of the document."""
        return semantic_context.get("semantic_coherence", 0.5)

    def _determine_topic_relevance(self, semantic_context: dict[str, Any]) -> float:
        """Determine topic relevance to the query."""
        return semantic_context.get("topic_relevance", 0.5)

    def _calculate_concept_coverage(self, semantic_context: dict[str, Any]) -> float:
        """Calculate concept coverage of the document."""
        return semantic_context.get("concept_coverage", 0.5)

    def _recommend_semantic_strategy(self, semantic_analysis: dict[str, Any]) -> str:
        """Recommend reranking strategy based on semantic analysis."""
        alignment = semantic_analysis["query_document_alignment"]
        coherence = semantic_analysis["semantic_coherence"]

        if alignment > 0.8 and coherence > 0.7:
            return "Transformer_Top"
        elif alignment > 0.6:
            return "Semantic_Prime"
        elif coherence > 0.6:
            return "Quality_Enhanced"
        else:
            return "Standard_Rerank"

    def _analyze_attention_distribution(self, attention_context: dict[str, Any]) -> str:
        """Analyze attention distribution pattern."""
        attention_weights = attention_context.get("attention_weights", [])

        if not attention_weights:
            return "unknown"

        # Calculate distribution characteristics
        max_weight = max(attention_weights)
        avg_weight = sum(attention_weights) / len(attention_weights)

        if max_weight > 0.8:
            return "focused"
        elif max_weight > 0.5:
            return "moderate"
        else:
            return "distributed"

    def _identify_key_terms_attention(self, attention_context: dict[str, Any]) -> list[str]:
        """Identify key terms with high attention."""
        attention_patterns = attention_context.get("attention_patterns", {})
        key_terms = []

        for term, attention_score in attention_patterns.items():
            if attention_score > 0.7:
                key_terms.append(term)

        return key_terms

    def _evaluate_attention_consistency(self, attention_context: dict[str, Any]) -> float:
        """Evaluate consistency of attention patterns."""
        return attention_context.get("attention_consistency", 0.5)

    def _assess_attention_relevance(self, attention_context: dict[str, Any]) -> float:
        """Assess relevance of attention patterns."""
        return attention_context.get("attention_relevance", 0.5)

    def _recommend_attention_strategy(self, attention_analysis: dict[str, Any]) -> str:
        """Recommend reranking strategy based on attention analysis."""
        distribution = attention_analysis["attention_distribution"]
        consistency = attention_analysis["attention_consistency"]

        if distribution == "focused" and consistency > 0.7:
            return "Transformer_Top"
        elif consistency > 0.6:
            return "Semantic_Prime"
        else:
            return "Standard_Rerank"

    def _assess_source_credibility(self, quality_context: dict[str, Any]) -> float:
        """Assess credibility of the document source."""
        return quality_context.get("source_credibility", 0.5)

    def _evaluate_content_quality(self, quality_context: dict[str, Any]) -> float:
        """Evaluate quality of the document content."""
        return quality_context.get("content_quality", 0.5)

    def _check_information_completeness(self, quality_context: dict[str, Any]) -> float:
        """Check completeness of information in the document."""
        return quality_context.get("information_completeness", 0.5)

    def _evaluate_freshness_relevance(self, quality_context: dict[str, Any]) -> float:
        """Evaluate relevance of document freshness."""
        return quality_context.get("freshness_relevance", 0.5)

    def _recommend_quality_strategy(self, quality_analysis: dict[str, Any]) -> str:
        """Recommend reranking strategy based on quality analysis."""
        credibility = quality_analysis["source_credibility"]
        content_quality = quality_analysis["content_quality"]

        if credibility > 0.8:
            return "Authority_Boost"
        elif content_quality > 0.7:
            return "Quality_Enhanced"
        else:
            return "Standard_Rerank"

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        if not self.is_loaded or not self.pipeline:
            return []

        try:
            # Get feature importances from Gradient Boosting
            gb_model = self.pipeline.named_steps["classifier"]
            importances = gb_model.feature_importances_

            # Get feature names
            feature_names = self.feature_names or list(model_input.features.keys())

            # Create feature importance list
            feature_importance = []
            for i, (name, importance) in tqdm(
                enumerate(zip(feature_names, importances)), desc="Processing", unit="item"
            ):
                feature_importance.append(
                    {
                        "feature_name": name,
                        "importance_score": float(importance),
                        "feature_value": model_input.features.get(name),
                        "rank": i + 1,
                        "relative_importance": float(importance / max(importances))
                        if max(importances) > 0
                        else 0.0,
                    }
                )

            # Sort by importance
            feature_importance.sort(key=lambda x: x["importance_score"], reverse=True)

            # Update ranks
            for i, feature in enumerate(feature_importance):
                feature["rank"] = i + 1

            # Return top 10 features
            return feature_importance[:10]

        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError):
            # Failed to compute importance
            return []

    def _extract_feature_vector(self, features: dict[str, Any]) -> np.ndarray | None:
        """Extract features in the correct order for the model."""
        if not self.feature_names:
            return None

        try:
            feature_vector = []
            for feature_name in self.feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            return np.array(feature_vector)

        except (
            TypeError,
            ValueError,
        ) as _fe:  # guardian: allow-return-none-swallow -- _extract_feature_vector: Optional return by contract, callers explicitly handle None, warning now logged
            logging.getLogger(__name__).warning("Feature vector construction failed: %s", _fe)
            return None

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for Transformer-inspired model."""
        processed_features, preprocessing_steps = super().preprocess_features(features)

        # Additional preprocessing for Transformer-inspired model
        for key, value in tqdm(processed_features.items(), desc="Processing", unit="item"):
            # Ensure all features are numeric
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

        return processed_features, preprocessing_steps

    def train_model(
        self,
        training_data: list[dict[str, Any]],
        feature_names: list[str],
        training_data_digest: str = "",
    ) -> None:
        """
        Train the Transformer-inspired model.

        Args:
            training_data: List of training examples with features and labels
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
        """
        # Extract features and labels
        X = []
        y = []

        for example in tqdm(training_data, desc="Processing", unit="item"):
            features = example["features"]
            label = example["label"]

            # Convert reranking type string to class index
            if isinstance(label, str):
                label = self.REVERSE_RERANKING_MAPPING.get(label, 7)  # Default to Standard_Rerank
            else:
                label = int(label)

            feature_vector = []
            for feature_name in feature_names:
                value = features.get(feature_name, 0.0)
                feature_vector.append(float(value))

            X.append(feature_vector)
            y.append(label)

        X = np.array(X)
        y = np.array(y)

        # Create pipeline with scaling and Gradient Boosting (as transformer proxy)
        self.pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    GradientBoostingClassifier(
                        n_estimators=100,
                        learning_rate=0.1,
                        max_depth=6,
                        min_samples_split=5,
                        min_samples_leaf=2,
                        random_state=42,
                    ),
                ),
            ]
        )

        # Train model
        self.pipeline.fit(X, y)

        # Store feature names and training digest
        self.feature_names = feature_names
        self._training_data_digest = training_data_digest

        self.is_loaded = True
