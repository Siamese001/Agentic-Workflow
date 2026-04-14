"""
Replay Harness for ML Decision Support

Provides deterministic replay capability for validating model consistency
and detecting drift over time.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_records_execution_trace

from ..models.base_model import ModelPrediction
from tqdm import tqdm


@dataclass
class ReplayResult:
    """Result of a replay operation."""

    original_prediction: ModelPrediction
    replayed_prediction: ModelPrediction
    predictions_match: bool
    confidence_difference: float
    prediction_difference: Any
    replay_timestamp: datetime
    replay_success: bool
    error_message: str | None = None


@dataclass
class ReplaySession:
    """Session for batch replay operations."""

    session_id: str
    start_time: datetime
    end_time: datetime | None = None
    total_replays: int = 0
    successful_replays: int = 0
    failed_replays: int = 0
    matches: int = 0
    mismatches: int = 0
    average_confidence_diff: float = 0.0


class ReplayHarness:
    """
    Provides deterministic replay capability for ML models.

    Ensures:
    - Same inputs produce same outputs over time
    - Model predictions are reproducible
    - Drift detection capabilities
    - Determinism validation
    """

    def __init__(self, replay_log_path: Path):
        self.replay_log_path = Path(replay_log_path)
        self.replay_log_path.mkdir(parents=True, exist_ok=True)
        self.replay_log_file = self.replay_log_path / "replay_results.jsonl"
        self.active_sessions: dict[str, ReplaySession] = {}

    def replay_prediction(
        self,
        model,
        original_context: dict[str, Any],
        original_trace_id: str,
        original_replay_key: str,
        original_policy_hash: str,
        original_semantic_clock: int | None = None,
        original_prediction: ModelPrediction | None = None,
    ) -> ReplayResult:
        """
        Replay a single prediction to verify determinism.

        Args:
            model: ML model to replay
            original_context: Original input context
            original_trace_id: Original trace ID
            original_replay_key: Original replay key
            original_policy_hash: Original policy hash
            original_semantic_clock: Original semantic clock
            original_prediction: Original prediction (if available)

        Returns:
            Replay result with comparison
        """
        start_time = datetime.utcnow()

        try:
            # Replay the prediction
            if hasattr(model, "predict_from_context"):
                replayed_prediction = model.predict_from_context(
                    context=original_context,
                    trace_id=original_trace_id,
                    replay_key=original_replay_key,
                    policy_hash=original_policy_hash,
                )
            else:
                # Fallback to manual feature extraction
                if hasattr(model, "feature_extractor"):
                    extraction_result = model.feature_extractor.extract_features(
                        context=original_context,
                        trace_id=original_trace_id,
                        replay_key=original_replay_key,
                        policy_hash=original_policy_hash,
                        semantic_clock=original_semantic_clock,
                    )

                    if extraction_result.success:
                        model_input = model.validate_input(extraction_result.features)
                        model_input.feature_provenance = extraction_result.provenance

                        replayed_prediction = model.predict(
                            model_input=model_input,
                            trace_id=original_trace_id,
                            replay_key=original_replay_key,
                            policy_hash=original_policy_hash,
                        )
                    else:
                        raise RuntimeError("Feature extraction failed during replay")
                else:
                    raise RuntimeError("Model does not support replay")

            # Compare predictions
            if original_prediction:
                predictions_match = self._compare_predictions(original_prediction, replayed_prediction)
                confidence_diff = abs(
                    original_prediction.confidence or 0.0 - (replayed_prediction.confidence or 0.0)
                )
                prediction_diff = self._calculate_prediction_difference(
                    original_prediction, replayed_prediction
                )
            else:
                predictions_match = True  # Can't compare without original
                confidence_diff = 0.0
                prediction_diff = None

            replay_result = ReplayResult(
                original_prediction=original_prediction,
                replayed_prediction=replayed_prediction,
                predictions_match=predictions_match,
                confidence_difference=confidence_diff,
                prediction_difference=prediction_diff,
                replay_timestamp=start_time,
                replay_success=True,
            )

            # Log replay result
            self._log_replay_result(replay_result)

            return replay_result

        except (OSError, ValueError, RuntimeError) as e:
            # Replay failed
            error_message = f"Replay failed: {str(e)}"

            replay_result = ReplayResult(
                original_prediction=original_prediction,
                replayed_prediction=None,
                predictions_match=False,
                confidence_difference=0.0,
                prediction_difference=None,
                replay_timestamp=start_time,
                replay_success=False,
                error_message=error_message,
            )

            self._log_replay_result(replay_result)

            return replay_result

    def replay_batch(
        self,
        model,
        replay_cases: list[dict[str, Any]],
        session_id: str | None = None,
    ) -> ReplaySession:
        """
        Replay multiple predictions in a batch.

        Args:
            model: ML model to replay
            replay_cases: List of replay case dictionaries
            session_id: Optional session ID

        Returns:
            Replay session summary
        """
        if session_id is None:
            session_id = self._stable_session_id(replay_cases)

        session = ReplaySession(
            session_id=session_id,
            start_time=datetime.utcnow(),
        )

        self.active_sessions[session_id] = session

        confidence_diffs = []

        for case in tqdm(replay_cases, desc="Processing", unit="item"):
            session.total_replays += 1

            result = self.replay_prediction(
                model=model,
                original_context=case.get("context", {}),
                original_trace_id=case.get("trace_id", ""),
                original_replay_key=case.get("replay_key", ""),
                original_policy_hash=case.get("policy_hash", ""),
                original_semantic_clock=case.get("semantic_clock"),
                original_prediction=case.get("original_prediction"),
            )

            if result.replay_success:
                session.successful_replays += 1

                if result.predictions_match:
                    session.matches += 1
                else:
                    session.mismatches += 1

                confidence_diffs.append(result.confidence_difference)
            else:
                session.failed_replays += 1

        # Calculate session statistics
        if confidence_diffs:
            session.average_confidence_diff = sum(confidence_diffs) / len(confidence_diffs)

        session.end_time = datetime.utcnow()

        # Log session summary
        self._log_session_summary(session)

        return session

    def validate_determinism(
        self,
        model,
        test_cases: list[dict[str, Any]],
        tolerance: float = 0.001,
    ) -> dict[str, Any]:
        """
        Validate model determinism across multiple test cases.

        Args:
            model: ML model to validate
            test_cases: List of test cases
            tolerance: Tolerance for floating point comparison

        Returns:
            Determinism validation results
        """
        session = self.replay_batch(model, test_cases)

        # Calculate determinism metrics
        determinism_rate = session.matches / max(1, session.successful_replays)
        success_rate = session.successful_replays / max(1, session.total_replays)

        # Determine if model is deterministic
        is_deterministic = (
            success_rate >= 0.95  # 95% success rate
            and determinism_rate >= 0.95  # 95% match rate
            and session.average_confidence_diff <= tolerance
        )

        validation_result = {
            "is_deterministic": is_deterministic,
            "success_rate": success_rate,
            "determinism_rate": determinism_rate,
            "average_confidence_diff": session.average_confidence_diff,
            "total_cases": session.total_replays,
            "successful_replays": session.successful_replays,
            "matches": session.matches,
            "mismatches": session.mismatches,
            "failed_replays": session.failed_replays,
            "session_id": session.session_id,
            "validation_timestamp": datetime.utcnow().isoformat(),
        }

        # Log validation result
        self._log_validation_result(validation_result)

        return validation_result

    def detect_drift(
        self,
        model,
        historical_cases: list[dict[str, Any]],
        current_cases: list[dict[str, Any]],
        drift_threshold: float = 0.1,
    ) -> dict[str, Any]:
        """
        Detect model drift by comparing historical and current predictions.

        Args:
            model: ML model to test
            historical_cases: Historical test cases
            current_cases: Current test cases
            drift_threshold: Threshold for drift detection

        Returns:
            Drift detection results
        """
        # Replay historical cases
        historical_session = self.replay_batch(
            model,
            historical_cases,
            self._stable_session_id(historical_cases, prefix="historical"),
        )

        # Replay current cases
        current_session = self.replay_batch(
            model,
            current_cases,
            self._stable_session_id(current_cases, prefix="current"),
        )

        # Calculate drift metrics
        historical_confidence = self._calculate_average_confidence(historical_cases)
        current_confidence = self._calculate_average_confidence(current_cases)

        confidence_drift = abs(current_confidence - historical_confidence)

        # Compare prediction distributions
        prediction_drift = self._calculate_prediction_distribution_drift(
            historical_cases,
            current_cases,
        )

        # Determine if drift is detected
        drift_detected = confidence_drift > drift_threshold or prediction_drift > drift_threshold

        drift_result = {
            "drift_detected": drift_detected,
            "confidence_drift": confidence_drift,
            "prediction_drift": prediction_drift,
            "historical_session": {
                "total_cases": historical_session.total_replays,
                "success_rate": historical_session.successful_replays
                / max(1, historical_session.total_replays),
                "average_confidence": historical_confidence,
            },
            "current_session": {
                "total_cases": current_session.total_replays,
                "success_rate": current_session.successful_replays / max(1, current_session.total_replays),
                "average_confidence": current_confidence,
            },
            "drift_threshold": drift_threshold,
            "detection_timestamp": datetime.utcnow().isoformat(),
        }

        # Log drift detection result
        self._log_drift_result(drift_result)

        return drift_result

    def _compare_predictions(self, pred1: ModelPrediction, pred2: ModelPrediction) -> bool:
        """Compare two predictions for equality."""
        if pred1.prediction != pred2.prediction:
            return False

        # Compare confidence within tolerance
        conf1 = pred1.confidence or 0.0
        conf2 = pred2.confidence or 0.0

        if abs(conf1 - conf2) > 0.001:  # 0.1% tolerance
            return False

        return True

    def _calculate_prediction_difference(self, pred1: ModelPrediction, pred2: ModelPrediction) -> Any:
        """Calculate the difference between two predictions."""
        if pred1.prediction != pred2.prediction:
            return f"{pred1.prediction} -> {pred2.prediction}"

        conf1 = pred1.confidence or 0.0
        conf2 = pred2.confidence or 0.0

        return conf2 - conf1

    def _calculate_average_confidence(self, cases: list[dict[str, Any]]) -> float:
        """Calculate average confidence from cases."""
        confidences = []

        for case in cases:
            prediction = case.get("original_prediction")
            if prediction and prediction.confidence is not None:
                confidences.append(prediction.confidence)

        return sum(confidences) / len(confidences) if confidences else 0.0

    def _calculate_prediction_distribution_drift(
        self,
        historical_cases: list[dict[str, Any]],
        current_cases: list[dict[str, Any]],
    ) -> float:
        """Calculate drift in prediction distributions."""
        # Get prediction distributions
        historical_dist = self._get_prediction_distribution(historical_cases)
        current_dist = self._get_prediction_distribution(current_cases)

        # Calculate simple drift metric (difference in distributions)
        all_predictions = set(historical_dist.keys()) | set(current_dist.keys())

        drift_sum = 0.0
        for pred in all_predictions:
            hist_prob = historical_dist.get(pred, 0.0)
            curr_prob = current_dist.get(pred, 0.0)
            drift_sum += abs(hist_prob - curr_prob)

        return drift_sum / len(all_predictions) if all_predictions else 0.0

    def _get_prediction_distribution(self, cases: list[dict[str, Any]]) -> dict[str, float]:
        """Get prediction distribution from cases."""
        distribution = {}

        for case in cases:
            prediction = case.get("original_prediction")
            if prediction:
                pred_str = str(prediction.prediction)
                distribution[pred_str] = distribution.get(pred_str, 0) + 1

        # Convert to probabilities
        total = sum(distribution.values())
        if total > 0:
            for pred in distribution:
                distribution[pred] = distribution[pred] / total

        return distribution

    def _log_replay_result(self, result: ReplayResult) -> None:
        """Log replay result to file."""
        log_data = {
            "timestamp": result.replay_timestamp.isoformat(),
            "predictions_match": result.predictions_match,
            "confidence_difference": result.confidence_difference,
            "prediction_difference": result.prediction_difference,
            "replay_success": result.replay_success,
            "error_message": result.error_message,
            "original_prediction": asdict(result.original_prediction) if result.original_prediction else None,
            "replayed_prediction": asdict(result.replayed_prediction) if result.replayed_prediction else None,
        }

        with open(self.replay_log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, default=str) + "\n")

    def _log_session_summary(self, session: ReplaySession) -> None:
        """Log session summary."""
        try:
            event_data = {
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "total_replays": session.total_replays,
                "successful_replays": session.successful_replays,
                "failed_replays": session.failed_replays,
                "matches": session.matches,
                "mismatches": session.mismatches,
                "average_confidence_diff": session.average_confidence_diff,
            }

            _emit_records_execution_trace(
                root_trace_id=f"replay_session_{session.session_id}",
                layer="L1_ML_DECISION_SUPPORT",
                operation="session_completed",
            )

        except (OSError, TypeError, ValueError) as e:
            print(f"Failed to log session summary: {e}")

    def _log_validation_result(self, validation_result: dict[str, Any]) -> None:
        """Log determinism validation result."""
        try:
            _emit_records_execution_trace(
                root_trace_id=f"determinism_validation_{validation_result.get('session_id', '')}",
                layer="L1_ML_DECISION_SUPPORT",
                operation="determinism_validated",
            )

        except (OSError, TypeError, ValueError) as e:
            print(f"Failed to log validation result: {e}")

    def _log_drift_result(self, drift_result: dict[str, Any]) -> None:
        """Log drift detection result."""
        try:
            _emit_records_execution_trace(
                root_trace_id=f"drift_detection_{drift_result.get('drift_threshold', '')}",
                layer="L1_ML_DECISION_SUPPORT",
                operation="drift_detected",
            )

        except (OSError, TypeError, ValueError) as e:
            print(f"Failed to log drift result: {e}")

    def _stable_session_id(self, cases: list[dict[str, Any]], prefix: str = "replay") -> str:
        """Generate deterministic session ID from case content hash."""
        digest = hashlib.sha256(json.dumps(cases, sort_keys=True, default=str).encode()).hexdigest()[:16]
        return f"{prefix}_session_{digest}"

    def get_replay_statistics(self) -> dict[str, Any]:
        """Get overall replay statistics."""
        try:
            total_replays = 0
            successful_replays = 0
            matches = 0
            mismatches = 0

            with open(self.replay_log_file, encoding="utf-8") as f:
                for line in tqdm(f, desc="Processing", unit="item"):
                    try:
                        log_entry = json.loads(line.strip())
                        total_replays += 1

                        if log_entry.get("replay_success", False):
                            successful_replays += 1

                        if log_entry.get("predictions_match", False):
                            matches += 1
                        else:
                            mismatches += 1

                    except json.JSONDecodeError:
                        continue

            return {
                "total_replays": total_replays,
                "successful_replays": successful_replays,
                "failed_replays": total_replays - successful_replays,
                "matches": matches,
                "mismatches": mismatches,
                "success_rate": successful_replays / max(1, total_replays),
                "determinism_rate": matches / max(1, successful_replays),
                "active_sessions": len(self.active_sessions),
            }

        except FileNotFoundError:
            return {
                "total_replays": 0,
                "successful_replays": 0,
                "failed_replays": 0,
                "matches": 0,
                "mismatches": 0,
                "success_rate": 0.0,
                "determinism_rate": 0.0,
                "active_sessions": 0,
            }
