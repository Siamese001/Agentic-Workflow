"""
Shadow Logger for ML Decision Support

Logs all ML decisions in shadow mode for comparison with actual decisions,
training data collection, and model improvement without affecting live traffic.
"""

import hashlib
import json
import os
from tempfile import NamedTemporaryFile
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_records_execution_trace

from ..models.base_model import ModelInput, ModelPrediction
from tqdm import tqdm


class ShadowMode(Enum):
    """Shadow logging modes."""

    LOG_ONLY = "log_only"  # Just log predictions
    COMPARE = "compare"  # Compare with actual decisions
    TRAINING_DATA = "training_data"  # Collect for training


@dataclass
class ShadowLogEntry:
    """Single shadow log entry."""

    timestamp: datetime
    trace_id: str
    replay_key: str
    policy_hash: str
    model_name: str
    model_version: str
    model_input: dict[str, Any]
    model_prediction: dict[str, Any]
    actual_decision: dict[str, Any] | None = None
    comparison_result: dict[str, Any] | None = None
    logging_mode: ShadowMode = ShadowMode.LOG_ONLY
    session_id: str = ""


@dataclass
class ComparisonResult:
    """Result of comparing ML prediction with actual decision."""

    predictions_match: bool
    confidence_difference: float | None = None
    path_difference: str | None = None
    ml_better: bool | None = None
    actual_outcome: dict[str, Any] | None = None
    improvement_opportunity: bool = False


class ShadowLogger:
    """
    Logs ML predictions in shadow mode for analysis and improvement.

    Provides:
    - Shadow prediction logging without affecting traffic
    - Comparison with actual decisions
    - Training data collection
    - Performance analysis
    - Model improvement insights
    """

    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.shadow_log_file = self.log_path / "shadow_predictions.jsonl"
        self.comparison_log_file = self.log_path / "comparisons.jsonl"
        self.training_data_file = self.log_path / "training_data.jsonl"
        self.session_id = self._generate_session_id(log_path)

        # Statistics
        self.stats = {
            "total_predictions": 0,
            "comparisons_made": 0,
            "ml_correct": 0,
            "ml_better": 0,
            "ml_worse": 0,
            "confidence_disagreements": 0,
            "path_disagreements": 0,
        }

    def log_prediction(
        self,
        model_input: ModelInput,
        model_prediction: ModelPrediction,
        logging_mode: ShadowMode = ShadowMode.LOG_ONLY,
        actual_decision: dict[str, Any] | None = None,
    ) -> str:
        """
        Log a model prediction in shadow mode.

        Args:
            model_input: Model input features
            model_prediction: Model prediction result
            logging_mode: Shadow logging mode
            actual_decision: Actual decision made (for comparison)

        Returns:
            Log entry ID
        """
        # Create log entry
        log_entry = ShadowLogEntry(
            timestamp=datetime.utcnow(),
            trace_id=model_prediction.trace_id,
            replay_key=model_prediction.replay_key,
            policy_hash=model_prediction.policy_hash,
            model_name=model_prediction.model_metadata.get("model_name", ""),
            model_version=model_prediction.model_version,
            model_input=model_input.features,
            model_prediction=asdict(model_prediction),
            actual_decision=actual_decision,
            logging_mode=logging_mode,
            session_id=self.session_id,
        )

        # Add comparison if actual decision provided
        if actual_decision and logging_mode in [ShadowMode.COMPARE, ShadowMode.TRAINING_DATA]:
            log_entry.comparison_result = self._compare_predictions(
                model_prediction,
                actual_decision,
            )
            self._update_stats(log_entry.comparison_result)

        # Write to appropriate log file
        self._write_log_entry(log_entry, logging_mode)

        # Update statistics
        self.stats["total_predictions"] += 1

        # Log to execution trace
        self._log_shadow_event(log_entry)

        return f"{log_entry.trace_id}:{int(log_entry.timestamp.timestamp())}"

    def log_batch_predictions(
        self,
        predictions: list[tuple[ModelInput, ModelPrediction]],
        logging_mode: ShadowMode = ShadowMode.LOG_ONLY,
        actual_decisions: list[dict[str, Any]] | None = None,
    ) -> list[str]:
        """
        Log multiple predictions efficiently.

        Args:
            predictions: List of (input, prediction) tuples
            logging_mode: Shadow logging mode
            actual_decisions: List of actual decisions for comparison

        Returns:
            List of log entry IDs
        """
        log_ids = []

        for i, (model_input, model_prediction) in enumerate(predictions):
            actual_decision = actual_decisions[i] if actual_decisions and i < len(actual_decisions) else None

            log_id = self.log_prediction(
                model_input=model_input,
                model_prediction=model_prediction,
                logging_mode=logging_mode,
                actual_decision=actual_decision,
            )
            log_ids.append(log_id)

        return log_ids

    def compare_with_actual(
        self,
        trace_id: str,
        actual_decision: dict[str, Any],
        actual_outcome: dict[str, Any] | None = None,
    ) -> ComparisonResult | None:
        """
        Compare a shadow prediction with actual decision.

        Args:
            trace_id: Trace ID of original prediction
            actual_decision: Actual decision that was made
            actual_outcome: Outcome of actual decision

        Returns:
            Comparison result if prediction found
        """
        # Find the shadow prediction
        shadow_prediction = self._find_prediction_by_trace_id(trace_id)
        if not shadow_prediction:
            return None

        # Reconstruct model prediction object
        model_prediction_dict = shadow_prediction["model_prediction"]
        model_prediction = self._reconstruct_prediction(model_prediction_dict)

        # Compare predictions
        comparison = self._compare_predictions(model_prediction, actual_decision)

        if actual_outcome:
            comparison.actual_outcome = actual_outcome

        # Update the log entry with comparison
        self._update_log_entry_with_comparison(trace_id, comparison)

        return comparison

    def get_shadow_statistics(self) -> dict[str, Any]:
        """Get shadow logging statistics."""
        return {
            **self.stats,
            "session_id": self.session_id,
            "session_start_time": self._get_session_start_time(),
            "log_files": {
                "shadow_predictions": str(self.shadow_log_file),
                "comparisons": str(self.comparison_log_file),
                "training_data": str(self.training_data_file),
            },
        }

    def get_improvement_opportunities(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get cases where ML predictions could improve decisions.

        Args:
            limit: Maximum number of opportunities to return

        Returns:
            List of improvement opportunities
        """
        opportunities = []

        try:
            with open(self.comparison_log_file, encoding="utf-8") as f:
                for line in f:
                    if len(opportunities) >= limit:
                        break

                    entry = json.loads(line.strip())
                    if entry.get("improvement_opportunity", False):
                        opportunities.append(entry)

        except FileNotFoundError:  # guardian: allow-silent-swallow -- log file absent on first run: opportunities list remains empty, caller handles
            pass

        return opportunities

    def export_training_data(
        self,
        output_file: Path | None = None,
        min_confidence: float = 0.7,
        include_comparisons: bool = True,
    ) -> Path:
        """
        Export shadow logs as training data.

        Args:
            output_file: Output file path
            min_confidence: Minimum confidence for training examples
            include_comparisons: Whether to include comparison data

        Returns:
            Path to exported training data file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.log_path / f"training_data_{timestamp}.jsonl"

        training_examples = []

        try:
            with open(self.shadow_log_file, encoding="utf-8") as f:
                for line in tqdm(f, desc="Processing", unit="item"):
                    entry = json.loads(line.strip())

                    # Filter by confidence
                    prediction = entry.get("model_prediction", {})
                    confidence = prediction.get("confidence", 0.0)

                    if confidence >= min_confidence:
                        training_example = {
                            "features": entry.get("model_input", {}),
                            "prediction": prediction.get("prediction"),
                            "confidence": confidence,
                            "trace_id": entry.get("trace_id"),
                            "timestamp": entry.get("timestamp"),
                        }

                        if include_comparisons and entry.get("comparison_result"):
                            training_example["actual_decision"] = entry.get("actual_decision")
                            training_example["comparison"] = entry.get("comparison_result")

                        training_examples.append(training_example)

        except FileNotFoundError:  # guardian: allow-silent-swallow -- log file absent: training export proceeds with no prior data
            pass

        # Write training data
        with open(output_file, "w", encoding="utf-8") as f:
            for example in training_examples:
                f.write(json.dumps(example) + "\n")

        return output_file

    def _compare_predictions(
        self,
        model_prediction: ModelPrediction,
        actual_decision: dict[str, Any],
    ) -> ComparisonResult:
        """Compare ML prediction with actual decision."""
        # Extract decision values
        predicted_path = model_prediction.prediction
        actual_path = actual_decision.get("path", actual_decision.get("decision"))

        # Check if predictions match
        predictions_match = str(predicted_path) == str(actual_path)

        # Calculate confidence difference if both have confidence
        confidence_difference = None
        if model_prediction.confidence is not None:
            actual_confidence = actual_decision.get("confidence")
            if actual_confidence is not None:
                confidence_difference = abs(model_prediction.confidence - actual_confidence)

        # Determine path difference
        path_difference = None
        if not predictions_match:
            path_difference = f"ML:{predicted_path} vs Actual:{actual_path}"

        # Determine if ML was better (requires outcome data)
        ml_better = None
        improvement_opportunity = False

        # This would be enhanced with actual outcome data
        # For now, flag high-confidence disagreements as opportunities
        if not predictions_match and model_prediction.confidence and model_prediction.confidence > 0.8:
            improvement_opportunity = True

        return ComparisonResult(
            predictions_match=predictions_match,
            confidence_difference=confidence_difference,
            path_difference=path_difference,
            ml_better=ml_better,
            improvement_opportunity=improvement_opportunity,
        )

    def _write_log_entry(self, log_entry: ShadowLogEntry, logging_mode: ShadowMode) -> None:
        """Write log entry to appropriate file."""
        log_data = asdict(log_entry)

        # Convert datetime to string for JSON serialization
        log_data["timestamp"] = log_entry.timestamp.isoformat()

        # Convert enums and datetime to strings for JSON serialization
        for key, value in tqdm(log_data.items(), desc="Processing", unit="item"):
            if isinstance(value, Enum):
                log_data[key] = value.value
            elif isinstance(value, datetime):
                log_data[key] = value.isoformat()
            elif isinstance(value, dict):
                # Handle nested dicts that may contain enums or datetime
                for k, v in value.items():
                    if isinstance(v, Enum):
                        value[k] = v.value
                    elif isinstance(v, datetime):
                        value[k] = v.isoformat()

        if logging_mode == ShadowMode.LOG_ONLY:
            self._append_json_line(self.shadow_log_file, log_data)

        elif logging_mode == ShadowMode.COMPARE:
            # Write to both shadow and comparison logs
            self._append_json_line(self.shadow_log_file, log_data)

            if log_entry.comparison_result:
                comparison_data = {
                    **log_data,
                    "comparison_result": asdict(log_entry.comparison_result),
                }
                self._append_json_line(self.comparison_log_file, comparison_data)

        elif logging_mode == ShadowMode.TRAINING_DATA:
            # Write to all three logs
            self._append_json_line(self.shadow_log_file, log_data)

            if log_entry.comparison_result:
                comparison_data = {
                    **log_data,
                    "comparison_result": asdict(log_entry.comparison_result),
                }
                self._append_json_line(self.comparison_log_file, comparison_data)

            # Training data format
            training_data = {
                "features": log_entry.model_input,
                "prediction": log_entry.model_prediction["prediction"],
                "confidence": log_entry.model_prediction.get("confidence"),
                "metadata": {
                    "trace_id": log_entry.trace_id,
                    "timestamp": log_entry.timestamp.isoformat(),
                    "model_version": log_entry.model_version,
                },
            }

            if log_entry.actual_decision:
                training_data["actual_decision"] = log_entry.actual_decision

            self._append_json_line(self.training_data_file, training_data)

    def _update_stats(self, comparison_result: ComparisonResult) -> None:
        """Update comparison statistics."""
        self.stats["comparisons_made"] += 1

        if comparison_result.predictions_match:
            self.stats["ml_correct"] += 1
        else:
            self.stats["path_disagreements"] += 1

        if comparison_result.confidence_difference and comparison_result.confidence_difference > 0.2:
            self.stats["confidence_disagreements"] += 1

        if comparison_result.ml_better is True:
            self.stats["ml_better"] += 1
        elif comparison_result.ml_better is False:
            self.stats["ml_worse"] += 1

    def _log_shadow_event(self, log_entry: ShadowLogEntry) -> None:
        """Log shadow event to execution trace."""
        try:
            event_data = {
                "session_id": self.session_id,
                "trace_id": log_entry.trace_id,
                "model_name": log_entry.model_name,
                "model_version": log_entry.model_version,
                "logging_mode": log_entry.logging_mode.value,
                "prediction": log_entry.model_prediction.get("prediction"),
                "confidence": log_entry.model_prediction.get("confidence"),
                "has_comparison": log_entry.comparison_result is not None,
            }

            _emit_records_execution_trace(
                root_trace_id=log_entry.trace_id,
                layer="L1_ML_DECISION_SUPPORT",
                operation="shadow_prediction_logged",
            )

        except (OSError, TypeError, ValueError) as e:
            # Log failure but don't fail the operation
            print(f"Failed to log shadow event: {e}")

    def _append_json_line(self, path: Path, data: dict) -> None:
        """Atomically append a JSON line to a JSONL file."""
        line = json.dumps(data) + "\n"
        with NamedTemporaryFile("w", dir=path.parent, delete=False, encoding="utf-8") as tmp:
            tmp_path = Path(tmp.name)
            if path.exists():
                tmp.write(path.read_text(encoding="utf-8"))
            tmp.write(line)
        try:
            os.replace(tmp_path, path)
        except Exception:  # guardian: allow-broad-exception -- temp file cleanup before re-raise; all exception types must trigger unlink
            tmp_path.unlink(missing_ok=True)
            raise

    def _generate_session_id(self, seed: Path) -> str:
        """Generate stable session ID for the configured log root."""
        digest = hashlib.sha256(str(Path(seed).resolve()).encode()).hexdigest()[:16]
        return f"shadow_session_{digest}"

    def _find_prediction_by_trace_id(self, trace_id: str) -> dict[str, Any] | None:
        """Find shadow prediction by trace ID."""
        try:
            with open(self.shadow_log_file, encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    if entry.get("trace_id") == trace_id:
                        return entry

        except FileNotFoundError:  # guardian: allow-silent-swallow -- log file absent: returns None, caller handles missing record
            pass

        return None

    def _reconstruct_prediction(self, prediction_dict: dict[str, Any]) -> ModelPrediction:
        """Reconstruct ModelPrediction object from dictionary."""
        # This is a simplified reconstruction
        # In practice, you'd want to fully reconstruct the object
        return ModelPrediction(**prediction_dict)

    def _update_log_entry_with_comparison(self, trace_id: str, comparison: ComparisonResult) -> None:
        """Update existing log entry with comparison result."""
        # This would involve finding and updating the specific log entry
        # For simplicity, we just append to comparison log
        comparison_data = {
            "trace_id": trace_id,
            "comparison_result": asdict(comparison),
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._append_json_line(self.comparison_log_file, comparison_data)

    def _get_session_start_time(self) -> str | None:
        """Get session start time from first log entry."""
        try:
            with open(self.shadow_log_file, encoding="utf-8") as f:
                first_line = f.readline()
                if first_line:
                    entry = json.loads(first_line.strip())
                    return entry.get("timestamp")

        except (FileNotFoundError, json.JSONDecodeError):  # guardian: allow-silent-swallow -- log missing or corrupt: returns None, caller handles
            pass

        return None
