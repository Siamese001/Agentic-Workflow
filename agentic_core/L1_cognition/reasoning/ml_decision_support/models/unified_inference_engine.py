"""
Unified Inference Engine

Coordinates all Phase 4 advanced ML models for comprehensive decision making,
including intelligent routing, semantic reranking, anomaly detection, and
unified inference orchestration with governance compliance.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config.model_registry import DecisionMode
from .advanced_c0_reranker import AdvancedC0Reranker

# Import Phase 4 models
from .advanced_l0_router import AdvancedL0Router
from .advanced_l6_detector import AdvancedL6Detector
from ._pickle_io import safe_pickle_dump, safe_pickle_load
from .base_model import BaseMLModel, DecisionMode, ModelInput, ModelPrediction, PredictionType


@dataclass
class UnifiedInferenceRequest:
    """Request for unified inference across all Phase 4 models."""

    trace_id: str
    replay_key: str
    policy_hash: str
    decision_mode: DecisionMode = DecisionMode.ADVISORY

    # Context data for different models
    routing_context: dict[str, Any] | None = None
    reranking_context: dict[str, Any] | None = None
    anomaly_context: dict[str, Any] | None = None

    # Unified context
    unified_context: dict[str, Any] | None = None

    # Inference options
    enable_routing: bool = True
    enable_reranking: bool = True
    enable_anomaly_detection: bool = True
    enable_coordination: bool = True


@dataclass
class UnifiedInferenceResult:
    """Result from unified inference across all Phase 4 models."""

    trace_id: str
    replay_key: str
    policy_hash: str
    timestamp: datetime

    # Individual model results
    routing_result: ModelPrediction | None = None
    reranking_result: ModelPrediction | None = None
    anomaly_result: ModelPrediction | None = None

    # Coordination results
    coordinated_decision: str | None = None
    coordination_confidence: float = 0.0
    coordination_rationale: list[str] = None

    # Unified recommendations
    unified_recommendations: list[str] = None
    implementation_priority: str = "Medium"

    # Metadata
    inference_time_ms: float = 0.0
    models_executed: list[str] = None
    governance_compliance: bool = True


class UnifiedInferenceEngine(BaseMLModel):
    """
    Unified inference engine for coordinating all Phase 4 advanced ML models.

    Provides comprehensive decision making through:
    - Intelligent routing with neural networks
    - Semantic reranking with transformer-inspired models
    - Advanced anomaly detection with autoencoder-inspired models
    - Unified coordination and decision synthesis
    - Cross-model consistency and validation
    - Governance compliance and audit logging
    """

    def __init__(self, model_file_path: Path | None = None):
        super().__init__(
            model_name="unified_inference_engine",
            model_version="1.0",
            model_type="unified_orchestrator",
            prediction_type=PredictionType.MULTICLASS,
            model_file_path=model_file_path,
        )

        # Initialize Phase 4 models
        self.routing_model = None
        self.reranking_model = None
        self.anomaly_model = None

        # Unified configuration
        self.unified_config = {
            "coordination_strategy": "weighted_consensus",
            "confidence_threshold": 0.6,
            "consensus_threshold": 0.7,
            "governance_enforcement": True,
            "deterministic_order": True,
        }

        # Model weights for coordination
        self.model_weights = {
            "routing": 0.4,
            "reranking": 0.3,
            "anomaly": 0.3,
        }

        # Initialize models if available
        self._initialize_models()

        if model_file_path and model_file_path.exists():
            self.load_model()

    def _initialize_models(self) -> None:
        """Initialize Phase 4 models."""
        try:
            self.routing_model = AdvancedL0Router()
        except (
            AttributeError,
            ImportError,
            TypeError,
        ) as e:  # guardian: allow-log-and-swallow -- routing model init: non-fatal, engine degrades to fallback
            import logging

            logging.getLogger(__name__).debug(
                "unified_inference_engine: routing model init failed at L128: %s", e
            )

        try:
            self.reranking_model = AdvancedC0Reranker()
        except (
            AttributeError,
            ImportError,
            TypeError,
        ) as e:  # guardian: allow-log-and-swallow -- reranking model init: non-fatal, engine degrades to fallback
            import logging

            logging.getLogger(__name__).debug(
                "unified_inference_engine: reranking model init failed at L133: %s", e
            )

        try:
            self.anomaly_model = AdvancedL6Detector()
        except (
            AttributeError,
            ImportError,
            TypeError,
        ) as e:  # guardian: allow-log-and-swallow -- anomaly model init: optional component, engine degrades gracefully
            import logging

            logging.getLogger(__name__).debug(
                "unified_inference_engine: anomaly model init failed at L138: %s", e
            )

    def load_model(self) -> None:
        """Load the unified inference engine configuration."""
        if not self.model_file_path or not self.model_file_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_file_path}")

        try:
            model_data = safe_pickle_load(self.model_file_path)

            self.unified_config = model_data.get("unified_config", self.unified_config)
            self.model_weights = model_data.get("model_weights", self.model_weights)
            self._training_data_digest = model_data.get("training_data_digest", "")

            self.is_loaded = True

        except (OSError, IOError, KeyError, TypeError) as e:
            raise RuntimeError(f"Failed to load model: {e}")

    def save_model(self, model_file_path: Path) -> None:
        """Save the unified inference engine configuration."""
        model_data = {
            "unified_config": self.unified_config,
            "model_weights": self.model_weights,
            "training_data_digest": getattr(self, "_training_data_digest", ""),
            "model_metadata": {
                "model_name": self.model_name,
                "model_version": self.model_version,
                "model_type": self.model_type,
                "prediction_type": self.prediction_type.value,
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
        Predict using unified inference engine.

        Args:
            model_input: Validated model input
            trace_id: Trace ID for reproducibility
            replay_key: Replay key for determinism
            policy_hash: Policy hash for governance
            decision_mode: Decision authority level

        Returns:
            Unified prediction with full metadata
        """
        # This is a placeholder - the main inference happens through execute_unified_inference
        return self.create_prediction(
            prediction="Unified_Inference",
            confidence=0.8,
            decision_mode=decision_mode,
            trace_id=trace_id,
            replay_key=replay_key,
            policy_hash=policy_hash,
        )

    def execute_unified_inference(
        self,
        request: UnifiedInferenceRequest,
    ) -> UnifiedInferenceResult:
        """
        Execute unified inference across all Phase 4 models.

        Args:
            request: Unified inference request

        Returns:
            Comprehensive unified inference result
        """
        start_time = datetime.now()

        # Initialize result
        result = UnifiedInferenceResult(
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
            timestamp=start_time,
            models_executed=[],
            unified_recommendations=[],
            coordination_rationale=[],
        )

        # Execute individual models based on request
        if request.enable_routing and self.routing_model:
            try:
                routing_result = self._execute_routing_inference(request)
                result.routing_result = routing_result
                result.models_executed.append("routing")
            except (
                AttributeError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:  # guardian: allow-log-and-swallow -- routing inference: sub-model failure non-fatal, analysis continues
                import logging

                logging.getLogger(__name__).debug("unified_inference_engine: routing inference failed: %s", e)

        if request.enable_reranking and self.reranking_model:
            try:
                reranking_result = self._execute_reranking_inference(request)
                result.reranking_result = reranking_result
                result.models_executed.append("reranking")
            except (
                AttributeError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:  # guardian: allow-log-and-swallow -- reranking inference: sub-model failure non-fatal, analysis continues
                import logging

                logging.getLogger(__name__).debug(
                    "unified_inference_engine: reranking inference failed: %s", e
                )

        if request.enable_anomaly_detection and self.anomaly_model:
            try:
                anomaly_result = self._execute_anomaly_inference(request)
                result.anomaly_result = anomaly_result
                result.models_executed.append("anomaly")
            except (
                AttributeError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:  # guardian: allow-log-and-swallow -- anomaly inference: sub-model failure non-fatal, analysis continues
                import logging

                logging.getLogger(__name__).debug("unified_inference_engine: anomaly inference failed: %s", e)

        # Coordinate results if enabled
        if request.enable_coordination and len(result.models_executed) > 1:
            coordination_result = self._coordinate_inference_results(result)
            result.coordinated_decision = coordination_result["decision"]
            result.coordination_confidence = coordination_result["confidence"]
            result.coordination_rationale = coordination_result["rationale"]

        # Generate unified recommendations
        result.unified_recommendations = self._generate_unified_recommendations(result)

        # Determine implementation priority
        result.implementation_priority = self._determine_implementation_priority(result)

        # Calculate inference time
        result.inference_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Check governance compliance
        result.governance_compliance = self._check_governance_compliance(result)

        return result

    def _execute_routing_inference(self, request: UnifiedInferenceRequest) -> ModelPrediction:
        """Execute routing inference."""
        if not request.routing_context:
            raise ValueError("Routing context required for routing inference")

        # Extract routing features
        routing_features = self.routing_model.feature_extractor.extract_features(
            context=request.routing_context,
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
        )

        if not routing_features.success:
            raise RuntimeError("Failed to extract routing features")

        # Create model input
        model_input = self.routing_model.validate_input(routing_features.features)
        model_input.feature_provenance = routing_features.provenance

        # Make prediction
        return self.routing_model.predict(
            model_input=model_input,
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
            decision_mode=request.decision_mode,
        )

    def _execute_reranking_inference(self, request: UnifiedInferenceRequest) -> ModelPrediction:
        """Execute reranking inference."""
        if not request.reranking_context:
            raise ValueError("Reranking context required for reranking inference")

        # Extract reranking features
        reranking_features = self.reranking_model.feature_extractor.extract_features(
            context=request.reranking_context,
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
        )

        if not reranking_features.success:
            raise RuntimeError("Failed to extract reranking features")

        # Create model input
        model_input = self.reranking_model.validate_input(reranking_features.features)
        model_input.feature_provenance = reranking_features.provenance

        # Make prediction
        return self.reranking_model.predict(
            model_input=model_input,
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
            decision_mode=request.decision_mode,
        )

    def _execute_anomaly_inference(self, request: UnifiedInferenceRequest) -> ModelPrediction:
        """Execute anomaly detection inference."""
        if not request.anomaly_context:
            raise ValueError("Anomaly context required for anomaly detection inference")

        # Extract anomaly features
        anomaly_features = self.anomaly_model.feature_extractor.extract_features(
            context=request.anomaly_context,
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
        )

        if not anomaly_features.success:
            raise RuntimeError("Failed to extract anomaly features")

        # Create model input
        model_input = self.anomaly_model.validate_input(anomaly_features.features)
        model_input.feature_provenance = anomaly_features.provenance

        # Make prediction
        return self.anomaly_model.predict(
            model_input=model_input,
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
            decision_mode=request.decision_mode,
        )

    def _coordinate_inference_results(self, result: UnifiedInferenceResult) -> dict[str, Any]:
        """Coordinate inference results from multiple models."""
        coordination = {
            "decision": "Standard_Operation",
            "confidence": 0.0,
            "rationale": [],
        }

        # Collect model predictions
        predictions = []
        confidences = []

        if result.routing_result:
            predictions.append(result.routing_result.prediction)
            confidences.append(result.routing_result.confidence)
            coordination["rationale"].append(
                f"Routing: {result.routing_result.prediction} (confidence: {result.routing_result.confidence:.2f})"
            )

        if result.reranking_result:
            predictions.append(result.reranking_result.prediction)
            confidences.append(result.reranking_result.confidence)
            coordination["rationale"].append(
                f"Reranking: {result.reranking_result.prediction} (confidence: {result.reranking_result.confidence:.2f})"
            )

        if result.anomaly_result:
            predictions.append(result.anomaly_result.prediction)
            confidences.append(result.anomaly_result.confidence)
            coordination["rationale"].append(
                f"Anomaly: {result.anomaly_result.prediction} (confidence: {result.anomaly_result.confidence:.2f})"
            )

        if not predictions:
            return coordination

        # Weighted consensus
        if self.unified_config["coordination_strategy"] == "weighted_consensus":
            weights = []

            if result.routing_result:
                weights.append(self.model_weights["routing"])
            if result.reranking_result:
                weights.append(self.model_weights["reranking"])
            if result.anomaly_result:
                weights.append(self.model_weights["anomaly"])

            # Calculate weighted confidence
            total_weight = sum(weights)
            if total_weight > 0:
                coordination["confidence"] = sum(w * c for w, c in zip(weights, confidences)) / total_weight
            else:
                coordination["confidence"] = sum(confidences) / len(confidences)

            # Determine coordinated decision
            if coordination["confidence"] > self.unified_config["consensus_threshold"]:
                # High confidence - use highest confidence prediction
                max_confidence_idx = confidences.index(max(confidences))
                coordination["decision"] = predictions[max_confidence_idx]
                coordination["rationale"].append(f"High confidence consensus: {coordination['decision']}")
            else:
                # Low confidence - conservative decision
                coordination["decision"] = "Standard_Operation"
                coordination["rationale"].append("Low confidence - conservative decision")

        return coordination

    def _generate_unified_recommendations(self, result: UnifiedInferenceResult) -> list[str]:
        """Generate unified recommendations from all model results."""
        recommendations = []

        # Routing recommendations
        if result.routing_result:
            if result.routing_result.prediction == "Neural_Advanced":
                recommendations.append("Implement neural network-based routing for optimal performance")
            elif result.routing_result.prediction == "Semantic_Optimized":
                recommendations.append("Use semantic optimization for routing decisions")
            elif result.routing_result.prediction == "User_Personalized":
                recommendations.append("Apply personalized routing based on user preferences")

        # Reranking recommendations
        if result.reranking_result:
            if result.reranking_result.prediction == "Transformer_Top":
                recommendations.append("Use transformer-based reranking for maximum relevance")
            elif result.reranking_result.prediction == "Authority_Boost":
                recommendations.append("Boost authoritative sources in reranking")
            elif result.reranking_result.prediction == "Engagement_Prioritized":
                recommendations.append("Prioritize documents with high user engagement")

        # Anomaly recommendations
        if result.anomaly_result:
            if result.anomaly_result.prediction == "Critical_Alert":
                recommendations.append("Immediate investigation required for critical anomalies")
            elif result.anomaly_result.prediction == "High_Priority":
                recommendations.append("High priority monitoring of detected anomalies")
            elif result.anomaly_result.prediction == "Adaptive_Monitoring":
                recommendations.append("Implement adaptive monitoring for anomaly patterns")

        # Coordination recommendations
        if result.coordinated_decision:
            if result.coordination_confidence > 0.8:
                recommendations.append(f"High confidence coordinated decision: {result.coordinated_decision}")
            elif result.coordination_confidence > 0.6:
                recommendations.append(
                    f"Moderate confidence coordinated decision: {result.coordinated_decision}"
                )
            else:
                recommendations.append("Low confidence - consider additional validation")

        # General recommendations
        if len(result.models_executed) == 3:
            recommendations.append(
                "All Phase 4 models executed successfully - comprehensive analysis available"
            )
        elif len(result.models_executed) == 2:
            recommendations.append("Partial Phase 4 analysis - consider enabling remaining models")
        else:
            recommendations.append("Limited analysis - enable more models for comprehensive insights")

        return recommendations

    def _determine_implementation_priority(self, result: UnifiedInferenceResult) -> str:
        """Determine implementation priority based on results."""
        # Check for critical anomalies
        if result.anomaly_result and result.anomaly_result.prediction == "Critical_Alert":
            return "Critical"

        # Check for high confidence coordinated decisions
        if result.coordination_confidence > 0.8:
            if result.coordinated_decision in ["Neural_Advanced", "Transformer_Top"]:
                return "High"
            else:
                return "Medium"

        # Check for individual model priorities
        if result.routing_result and result.routing_result.prediction in [
            "Neural_Advanced",
            "Semantic_Optimized",
        ]:
            if result.routing_result.confidence > 0.7:
                return "High"

        if result.reranking_result and result.reranking_result.prediction in [
            "Transformer_Top",
            "Semantic_Prime",
        ]:
            if result.reranking_result.confidence > 0.7:
                return "High"

        # Default priority
        return "Medium"

    def _check_governance_compliance(self, result: UnifiedInferenceResult) -> bool:
        """Check governance compliance of the unified result."""
        # Check if all models operated in appropriate modes
        if result.routing_result and result.routing_result.decision_mode == DecisionMode.BLOCKED:
            return False

        if result.reranking_result and result.reranking_result.decision_mode == DecisionMode.BLOCKED:
            return False

        if result.anomaly_result and result.anomaly_result.decision_mode == DecisionMode.BLOCKED:
            return False

        # Check coordination confidence
        if result.coordination_confidence < self.unified_config["confidence_threshold"]:
            return False

        return True

    def get_comprehensive_analysis(
        self,
        request: UnifiedInferenceRequest,
    ) -> dict[str, Any]:
        """
        Get comprehensive analysis across all Phase 4 models.

        Args:
            request: Unified inference request

        Returns:
            Comprehensive analysis report
        """
        # Execute unified inference
        result = self.execute_unified_inference(request)

        # Build comprehensive analysis
        analysis = {
            "summary": {
                "trace_id": result.trace_id,
                "timestamp": result.timestamp.isoformat(),
                "models_executed": result.models_executed,
                "inference_time_ms": result.inference_time_ms,
                "governance_compliance": result.governance_compliance,
            },
            "routing_analysis": None,
            "reranking_analysis": None,
            "anomaly_analysis": None,
            "coordination_analysis": {
                "decision": result.coordinated_decision,
                "confidence": result.coordination_confidence,
                "rationale": result.coordination_rationale,
            },
            "unified_recommendations": result.unified_recommendations,
            "implementation_priority": result.implementation_priority,
        }

        # Detailed routing analysis
        if result.routing_result and request.routing_context:
            try:
                routing_analysis = self.routing_model.route_intelligently(
                    routing_context=request.routing_context,
                    trace_id=request.trace_id,
                    replay_key=request.replay_key,
                    policy_hash=request.policy_hash,
                )
                analysis["routing_analysis"] = routing_analysis
            except (
                AttributeError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:  # guardian: allow-log-and-swallow -- routing analysis: sub-model failure non-fatal, analysis continues
                import logging

                logging.getLogger(__name__).debug("unified_inference_engine: routing analysis failed: %s", e)

        # Detailed reranking analysis
        if result.reranking_result and request.reranking_context:
            try:
                reranking_analysis = self.reranking_model.rerank_intelligently(
                    reranking_context=request.reranking_context,
                    trace_id=request.trace_id,
                    replay_key=request.replay_key,
                    policy_hash=request.policy_hash,
                )
                analysis["reranking_analysis"] = reranking_analysis
            except (
                AttributeError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:  # guardian: allow-log-and-swallow -- reranking analysis: sub-model failure non-fatal, analysis continues
                import logging

                logging.getLogger(__name__).debug(
                    "unified_inference_engine: reranking analysis failed: %s", e
                )

        # Detailed anomaly analysis
        if result.anomaly_result and request.anomaly_context:
            try:
                anomaly_analysis = self.anomaly_model.detect_anomalies_intelligently(
                    anomaly_context=request.anomaly_context,
                    trace_id=request.trace_id,
                    replay_key=request.replay_key,
                    policy_hash=request.policy_hash,
                )
                analysis["anomaly_analysis"] = anomaly_analysis
            except (
                AttributeError,
                TypeError,
                ValueError,
                KeyError,
            ) as e:  # guardian: allow-log-and-swallow -- anomaly analysis: sub-model failure non-fatal, analysis continues
                import logging

                logging.getLogger(__name__).debug("unified_inference_engine: anomaly analysis failed: %s", e)

        return analysis

    def validate_unified_configuration(self) -> dict[str, Any]:
        """Validate unified inference engine configuration."""
        validation_result = {
            "is_valid": True,
            "issues": [],
            "recommendations": [],
            "model_status": {},
        }

        # Check model availability
        if self.routing_model:
            validation_result["model_status"]["routing"] = "available"
        else:
            validation_result["model_status"]["routing"] = "unavailable"
            validation_result["issues"].append("Advanced L0 Router not available")

        if self.reranking_model:
            validation_result["model_status"]["reranking"] = "available"
        else:
            validation_result["model_status"]["reranking"] = "unavailable"
            validation_result["issues"].append("Advanced C0 Reranker not available")

        if self.anomaly_model:
            validation_result["model_status"]["anomaly"] = "available"
        else:
            validation_result["model_status"]["anomaly"] = "unavailable"
            validation_result["issues"].append("Advanced L6 Detector not available")

        # Check configuration validity
        if not self.unified_config.get("coordination_strategy"):
            validation_result["issues"].append("No coordination strategy specified")
            validation_result["is_valid"] = False

        if not self.model_weights:
            validation_result["issues"].append("No model weights specified")
            validation_result["is_valid"] = False

        # Check weight sum
        total_weight = sum(self.model_weights.values())
        if abs(total_weight - 1.0) > 0.1:
            validation_result["issues"].append(f"Model weights sum to {total_weight:.2f}, should be 1.0")

        # Generate recommendations
        if len(validation_result["issues"]) > 0:
            validation_result["recommendations"].append("Address configuration issues before deployment")

        available_models = sum(
            1 for status in validation_result["model_status"].values() if status == "available"
        )
        if available_models < 2:
            validation_result["recommendations"].append("Enable more models for comprehensive analysis")

        return validation_result

    def get_feature_importance(self, model_input: ModelInput) -> list[dict[str, Any]]:
        """Get feature importance for explainability."""
        # Unified inference engine doesn't have direct feature importance
        # This would aggregate importance from individual models
        return []

    def preprocess_features(self, features: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Preprocess features for unified inference."""
        # Unified inference engine doesn't directly process features
        # This would coordinate preprocessing across individual models
        return features, []

    def train_model(
        self,
        training_data: list[dict[str, Any]],
        feature_names: list[str],
        training_data_digest: str = "",
    ) -> None:
        """
        Train the unified inference engine configuration.

        Args:
            training_data: List of training examples
            feature_names: Names of features to use
            training_data_digest: Digest of training data for provenance
        """
        # Unified inference engine doesn't require training in the traditional sense
        # This would coordinate training across individual models
        self._training_data_digest = training_data_digest
        self.is_loaded = True
