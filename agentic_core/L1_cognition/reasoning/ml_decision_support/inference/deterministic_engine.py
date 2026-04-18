"""
Deterministic Inference Engine

Coordinates ML model inference with deterministic execution,
governance compliance, and audit logging.
"""

import time
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_records_execution_trace

from ..config.model_registry import DecisionMode
from ..inference.replay_harness import ReplayHarness
from ..inference.shadow_logger import ShadowLogger, ShadowMode
from ..models.base_model import BaseMLModel, ModelPrediction
from tqdm import tqdm


@dataclass
class InferenceRequest:
    """Request for ML inference."""

    model_name: str
    model_version: str
    context: dict[str, Any]
    trace_id: str
    replay_key: str
    policy_hash: str
    semantic_clock: int | None = None
    decision_mode: DecisionMode = DecisionMode.ADVISORY
    shadow_mode: bool = False
    validation_required: bool = True


@dataclass
class InferenceResult:
    """Result of ML inference."""

    prediction: ModelPrediction
    inference_metadata: dict[str, Any]
    success: bool
    error_message: str | None = None
    inference_time_ms: float = 0.0


class DeterministicInferenceEngine:
    """
    Coordinates deterministic ML inference with full governance compliance.

    Provides:
    - Deterministic model execution
    - Governance mode enforcement
    - Shadow mode operation
    - Audit logging
    - Performance monitoring
    - Error handling and fallback
    """

    def __init__(
        self,
        models: dict[str, BaseMLModel],
        shadow_logger: ShadowLogger,
        replay_harness: ReplayHarness,
    ):
        self.models = models
        self.shadow_logger = shadow_logger
        self.replay_harness = replay_harness

        # Inference statistics
        self.stats = {
            "total_inferences": 0,
            "successful_inferences": 0,
            "failed_inferences": 0,
            "shadow_inferences": 0,
            "production_inferences": 0,
            "average_inference_time_ms": 0.0,
        }

    def infer(
        self,
        request: InferenceRequest,
    ) -> InferenceResult:
        """
        Execute ML inference with deterministic behavior.

        Args:
            request: Inference request with all required parameters

        Returns:
            Inference result with prediction and metadata
        """
        start_time = time.time()
        self.stats["total_inferences"] += 1

        try:
            # Get the requested model
            model_key = f"{request.model_name}:{request.model_version}"
            model = self.models.get(model_key)

            if not model:
                raise ValueError(f"Model {model_key} not found")

            # Validate request
            self._validate_request(request)

            # Execute inference
            prediction = self._execute_inference(model, request)

            # Log shadow prediction if in shadow mode
            if request.shadow_mode:
                self._log_shadow_prediction(model, request, prediction)

            # Update statistics
            inference_time = (time.time() - start_time) * 1000
            self._update_stats(inference_time, request.shadow_mode, True)

            # Create inference result
            result = InferenceResult(
                prediction=prediction,
                inference_metadata=self._create_inference_metadata(request, prediction),
                success=True,
                inference_time_ms=inference_time,
            )

            # Log inference completion
            self._log_inference_completion(request, result)

            return result

        except (RuntimeError, ValueError, TypeError) as e:
            # Inference failed
            inference_time = (time.time() - start_time) * 1000
            self._update_stats(inference_time, request.shadow_mode, False)

            error_message = f"Inference failed: {str(e)}"

            result = InferenceResult(
                prediction=None,
                inference_metadata={"error": error_message},
                success=False,
                error_message=error_message,
                inference_time_ms=inference_time,
            )

            # Log inference failure
            self._log_inference_failure(request, result)

            return result

    def infer_batch(
        self,
        requests: list[InferenceRequest],
    ) -> list[InferenceResult]:
        """
        Execute multiple inferences efficiently.

        Args:
            requests: List of inference requests

        Returns:
            List of inference results
        """
        results = []

        for request in requests:
            result = self.infer(request)
            results.append(result)

        return results

    def validate_determinism(
        self,
        model_name: str,
        model_version: str,
        test_cases: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Validate model determinism using replay harness.

        Args:
            model_name: Name of model to validate
            model_version: Version of model to validate
            test_cases: Test cases for validation

        Returns:
            Determinism validation results
        """
        model_key = f"{model_name}:{model_version}"
        model = self.models.get(model_key)

        if not model:
            raise ValueError(f"Model {model_key} not found")

        # Convert test cases to replay format
        replay_cases = []
        for i, case in tqdm(enumerate(test_cases), desc="Processing", unit="item"):
            # Create inference request for this case
            request = InferenceRequest(
                model_name=model_name,
                model_version=model_version,
                context=case.get("context", {}),
                trace_id=case.get("trace_id", f"det_test_{i}"),
                replay_key=case.get("replay_key", f"det_replay_{i}"),
                policy_hash=case.get("policy_hash", "det_policy"),
                semantic_clock=case.get("semantic_clock"),
                decision_mode=DecisionMode.SHADOW_ONLY,
            )

            # Execute original prediction
            original_result = self.infer(request)

            replay_case = {
                "context": case.get("context", {}),
                "trace_id": request.trace_id,
                "replay_key": request.replay_key,
                "policy_hash": request.policy_hash,
                "semantic_clock": request.semantic_clock,
                "original_prediction": original_result.prediction,
            }

            replay_cases.append(replay_case)

        # Validate determinism using replay harness
        validation_result = self.replay_harness.validate_determinism(model, replay_cases)

        return validation_result

    def get_model_statistics(self, model_name: str | None = None) -> dict[str, Any]:
        """Get inference statistics for models."""
        if model_name:
            # Return statistics for specific model
            model_stats = {
                "model_name": model_name,
                "total_inferences": self.stats["total_inferences"],
                "successful_inferences": self.stats["successful_inferences"],
                "failed_inferences": self.stats["failed_inferences"],
                "success_rate": self.stats["successful_inferences"] / max(1, self.stats["total_inferences"]),
                "average_inference_time_ms": self.stats["average_inference_time_ms"],
            }

            # Add model-specific statistics if available
            model = self.models.get(f"{model_name}:latest")
            if model:
                model_info = model.get_model_info()
                model_stats.update(model_info)

            return model_stats
        else:
            # Return overall statistics
            return {
                **self.stats,
                "available_models": list(self.models.keys()),
                "shadow_statistics": self.shadow_logger.get_shadow_statistics(),
                "replay_statistics": self.replay_harness.get_replay_statistics(),
            }

    def _validate_request(self, request: InferenceRequest) -> None:
        """Validate inference request."""
        if not request.model_name:
            raise ValueError("Model name is required")

        if not request.model_version:
            raise ValueError("Model version is required")

        if not request.context:
            raise ValueError("Context is required")

        if not request.trace_id:
            raise ValueError("Trace ID is required")

        if not request.replay_key:
            raise ValueError("Replay key is required")

        if not request.policy_hash:
            raise ValueError("Policy hash is required")

        # Validate decision mode
        if request.decision_mode == DecisionMode.PRODUCTION:
            # Production mode should only be allowed for specific models
            allowed_production_models = ["l0_route_recommender", "c0_retrieval_reranker"]
            if request.model_name not in allowed_production_models:
                raise ValueError(f"Production mode not allowed for model {request.model_name}")

    def _execute_inference(self, model: BaseMLModel, request: InferenceRequest) -> ModelPrediction:
        """Execute model inference."""
        # Extract features if model has feature extractor
        if hasattr(model, "feature_extractor"):
            extraction_result = model.feature_extractor.extract_features(
                context=request.context,
                trace_id=request.trace_id,
                replay_key=request.replay_key,
                policy_hash=request.policy_hash,
                semantic_clock=request.semantic_clock,
            )

            if not extraction_result.success and request.validation_required:
                raise ValueError(f"Feature extraction failed: {extraction_result.error_messages}")

            # Validate features
            model_input = model.validate_input(extraction_result.features)
            model_input.feature_provenance = extraction_result.provenance

            if model_input.validation_status == "invalid" and request.validation_required:
                raise ValueError(f"Feature validation failed: {model_input.validation_errors}")
        else:
            # Create model input from context directly
            model_input = model.validate_input(request.context)

        # Make prediction
        prediction = model.predict(
            model_input=model_input,
            trace_id=request.trace_id,
            replay_key=request.replay_key,
            policy_hash=request.policy_hash,
            decision_mode=request.decision_mode,
        )

        return prediction

    def _log_shadow_prediction(
        self, model: BaseMLModel, request: InferenceRequest, prediction: ModelPrediction
    ) -> None:
        """Log prediction in shadow mode."""
        try:
            # Create model input for logging
            if hasattr(model, "feature_extractor"):
                extraction_result = model.feature_extractor.extract_features(
                    context=request.context,
                    trace_id=request.trace_id,
                    replay_key=request.replay_key,
                    policy_hash=request.policy_hash,
                )

                if extraction_result.success:
                    model_input = model.validate_input(extraction_result.features)
                    model_input.feature_provenance = extraction_result.provenance
                else:
                    return  # Skip logging if extraction failed
            else:
                model_input = model.validate_input(request.context)

            # Log to shadow logger
            self.shadow_logger.log_prediction(
                model_input=model_input,
                model_prediction=prediction,
                logging_mode=ShadowMode.LOG_ONLY,
            )

        except (RuntimeError, ValueError, TypeError) as e:
            # Log failure but don't fail the inference
            print(f"Failed to log shadow prediction: {e}")

    def _create_inference_metadata(
        self, request: InferenceRequest, prediction: ModelPrediction
    ) -> dict[str, Any]:
        """Create inference metadata."""
        return {
            "model_name": request.model_name,
            "model_version": request.model_version,
            "decision_mode": request.decision_mode.value,
            "shadow_mode": request.shadow_mode,
            "validation_required": request.validation_required,
            "prediction_confidence": prediction.confidence,
            "prediction_timestamp": prediction.prediction_timestamp.isoformat(),
            "feature_digest": prediction.feature_digest,
            "training_data_digest": prediction.training_data_digest,
            "threshold_used": prediction.threshold_used,
        }

    def _update_stats(self, inference_time: float, is_shadow: bool, success: bool) -> None:
        """Update inference statistics."""
        if success:
            self.stats["successful_inferences"] += 1
        else:
            self.stats["failed_inferences"] += 1

        if is_shadow:
            self.stats["shadow_inferences"] += 1
        else:
            self.stats["production_inferences"] += 1

        # Update average inference time
        total_successful = self.stats["successful_inferences"]
        if total_successful > 0:
            current_avg = self.stats["average_inference_time_ms"]
            self.stats["average_inference_time_ms"] = (
                current_avg * (total_successful - 1) + inference_time
            ) / total_successful

    def _log_inference_completion(self, request: InferenceRequest, result: InferenceResult) -> None:
        """Log successful inference completion."""
        try:
            event_data = {
                "model_name": request.model_name,
                "model_version": request.model_version,
                "trace_id": request.trace_id,
                "decision_mode": request.decision_mode.value,
                "shadow_mode": request.shadow_mode,
                "prediction": result.prediction.prediction if result.prediction else None,
                "confidence": result.prediction.confidence if result.prediction else None,
                "inference_time_ms": result.inference_time_ms,
                "success": result.success,
            }

            _emit_records_execution_trace(
                root_trace_id=request.trace_id,
                layer="L1_ML_DECISION_SUPPORT",
                operation="inference_completed",
            )

        except (RuntimeError, ValueError, TypeError) as e:
            print(f"Failed to log inference completion: {e}")

    def _log_inference_failure(self, request: InferenceRequest, result: InferenceResult) -> None:
        """Log inference failure."""
        try:
            event_data = {
                "model_name": request.model_name,
                "model_version": request.model_version,
                "trace_id": request.trace_id,
                "decision_mode": request.decision_mode.value,
                "shadow_mode": request.shadow_mode,
                "error_message": result.error_message,
                "inference_time_ms": result.inference_time_ms,
                "success": result.success,
            }

            _emit_records_execution_trace(
                root_trace_id=request.trace_id,
                layer="L1_ML_DECISION_SUPPORT",
                operation="inference_failed",
            )

        except (RuntimeError, ValueError, TypeError) as e:
            print(f"Failed to log inference failure: {e}")

    def register_model(self, model: BaseMLModel) -> None:
        """Register a model with the inference engine."""
        model_key = f"{model.model_name}:{model.model_version}"
        self.models[model_key] = model

    def unregister_model(self, model_name: str, model_version: str) -> None:
        """Unregister a model from the inference engine."""
        model_key = f"{model_name}:{model_version}"
        if model_key in self.models:
            del self.models[model_key]

    def get_available_models(self) -> list[str]:
        """Get list of available models."""
        return list(self.models.keys())
