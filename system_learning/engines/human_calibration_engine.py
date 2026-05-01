"""Human Calibration Engine — Evaluation Spine Component F.

Captures explicit operator judgments and model confidences to prevent
silent drift. Produces calibration records for feedback loops.

Deterministic, with full ADG traceability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_escalates_to_human,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json

# ADG wiring for human calibration engine
_emit_records_execution_trace("human_calibration_engine", "p0", "calibration_trace")
_emit_applies_guardrail("p0", "human_calibration_engine", "p0_governance")
emit_replay_key("p0", "human_calibration_engine")
emit_determinism_digest("p0", "human_calibration_engine")
_emit_writes_via_uwg("p2", "human_calibration_engine", "uwg_write")
_emit_blocks_direct_write("p2", "human_calibration_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "human_calibration_engine", "tool_invocation")
_emit_captures_execution_output("p2", "human_calibration_engine", "exec_output")
_emit_escalates_to_human("p3", "human_calibration_engine", "human_escalation")
_emit_dispatches_agent("p3", "human_calibration_engine", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "human_calibration_engine", "exec_plan")
_emit_routes_to_agent("p3", "human_calibration_engine", "target_agent")
_emit_checks_agent_registry("p3", "human_calibration_engine", "agent_registry")
_emit_validates_agent_capability("p3", "human_calibration_engine", "capability")
_emit_verifies_policy("p3", "human_calibration_engine", "policy_check")
_emit_verifies_boundary("p3", "human_calibration_engine", "boundary_check")
_emit_agent_executes_agent("p3", "human_calibration_engine", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# Human Calibration Types
# =============================================================================


@dataclass(frozen=True)
class HumanJudgment:
    """Explicit human judgment record.

    Attributes
    ----------
    judgment_id:
        Deterministic SHA-256 ID for this judgment.
    trace_id:
        Source execution trace identifier.
    model_prediction:
        What the model predicted.
    human_label:
        What the human labeled (AGREE, DISAGREE, FLAG).
    confidence_delta:
        Difference between model and human confidence.
    reason_tags:
        Tags explaining the judgment.
    reviewer_id:
        Identifier of the human reviewer.
    timestamp_utc:
        Unix timestamp provided by caller.
    """

    judgment_id: str
    trace_id: str
    model_prediction: str
    human_label: Literal["AGREE", "DISAGREE", "FLAG"]
    confidence_delta: float
    reason_tags: tuple[str, ...]
    reviewer_id: str
    timestamp_utc: int

    def __post_init__(self) -> None:
        if not self.judgment_id:
            raise ValueError("judgment_id must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "confidence_delta": self.confidence_delta,
            "human_label": self.human_label,
            "judgment_id": self.judgment_id,
            "model_prediction": self.model_prediction,
            "reason_tags": list(self.reason_tags),
            "reviewer_id": self.reviewer_id,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


@dataclass(frozen=True)
class CalibrationRecord:
    """Calibration record for drift prevention.

    Attributes
    ----------
    artifact_type:
        Always ``CALIBRATION_RECORD``.
    record_id:
        Deterministic SHA-256 ID for this record.
    trace_id:
        Source execution trace identifier.
    model_confidence:
        Model's reported confidence.
    calibrated_confidence:
        Calibrated confidence after human judgment.
    judgment:
        Human judgment record.
    drift_flag:
        True if this indicates potential drift.
    feedback_action:
        Action to take based on calibration (RETRAIN, ADJUST, IGNORE).
    timestamp_utc:
        Unix timestamp provided by caller.
    """

    artifact_type: Literal["CALIBRATION_RECORD"]
    record_id: str
    trace_id: str
    model_confidence: float
    calibrated_confidence: float
    judgment: HumanJudgment
    drift_flag: bool
    feedback_action: Literal["RETRAIN", "ADJUST", "IGNORE"]
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "CALIBRATION_RECORD":
            raise ValueError(f"artifact_type must be 'CALIBRATION_RECORD', got {self.artifact_type!r}")
        if not self.record_id:
            raise ValueError("record_id must not be empty")
        if not 0.0 <= self.model_confidence <= 1.0:
            raise ValueError(f"model_confidence must be in [0.0, 1.0], got {self.model_confidence}")
        if not 0.0 <= self.calibrated_confidence <= 1.0:
            raise ValueError(f"calibrated_confidence must be in [0.0, 1.0], got {self.calibrated_confidence}")

    def to_dict(self) -> dict[str, object]:
        return {
            "artifact_type": self.artifact_type,
            "calibrated_confidence": self.calibrated_confidence,
            "drift_flag": self.drift_flag,
            "feedback_action": self.feedback_action,
            "judgment": self.judgment.to_dict(),
            "model_confidence": self.model_confidence,
            "record_id": self.record_id,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# HumanCalibrationEngine
# =============================================================================


class HumanCalibrationEngine:
    """Engine for human-in-the-loop calibration (Component F).

    Captures explicit operator judgments and model confidences to:
        1. Detect silent drift
        2. Calibrate confidence scores
        3. Generate feedback for retraining
        4. Flag examples for review

    Deterministic: Same inputs always produce same calibration.

    Attributes
    ----------
    drift_threshold:
        Confidence delta threshold to flag as drift.
    calibration_window:
        Number of records to keep for calibration.
    """

    DEFAULT_DRIFT_THRESHOLD: float = 0.3
    DEFAULT_CALIBRATION_WINDOW: int = 1000

    def __init__(
        self,
        drift_threshold: float | None = None,
        calibration_window: int | None = None,
    ) -> None:
        self.drift_threshold = drift_threshold or self.DEFAULT_DRIFT_THRESHOLD
        self.calibration_window = calibration_window or self.DEFAULT_CALIBRATION_WINDOW
        self._calibration_history: list[CalibrationRecord] = []
        # v6 KPI state.
        # JUDGE_HUMAN_KAPPA_FRESHNESS: epoch of latest calibration per
        # rubric_id; we report the OLDEST among rubrics (worst-case age).
        # JUDGE_UNKNOWN_BUDGET_COMPLIANCE: counters for judges that
        # respected their unknown_budget vs total judges scored.
        self._last_calibration_epoch_by_rubric: dict[str, float] = {}
        self._compliant_judges: int = 0
        self._total_judges: int = 0

    # --- v6 KPI surface -------------------------------------------------

    def mark_calibration(self, *, rubric_id: str, epoch: float) -> None:
        """Record that ``rubric_id`` was just calibrated at ``epoch``."""
        prev = self._last_calibration_epoch_by_rubric.get(rubric_id)
        if prev is None or epoch > prev:
            self._last_calibration_epoch_by_rubric[rubric_id] = float(epoch)

    def mark_judge_scored(self, *, compliant: bool) -> None:
        """Record one judge scored against unknown_budget."""
        self._total_judges += 1
        if compliant:
            self._compliant_judges += 1

    @property
    def calibration_state(self) -> tuple[dict[str, float], int, int]:
        """Return ``(per_rubric_epochs, compliant_judges, total_judges)``."""
        return (
            dict(self._last_calibration_epoch_by_rubric),
            self._compliant_judges,
            self._total_judges,
        )

    def reset_calibration_state(self) -> None:
        """Reset all v6 KPI calibration state."""
        self._last_calibration_epoch_by_rubric.clear()
        self._compliant_judges = 0
        self._total_judges = 0

    def publish_kpi_sample(self, board: Any, *, now: float | None = None) -> None:
        """Publish JUDGE_HUMAN_KAPPA_FRESHNESS and
        JUDGE_UNKNOWN_BUDGET_COMPLIANCE to ``board``.

        Freshness is reported using the OLDEST calibration epoch across
        rubrics (worst-case age). If no rubrics have been calibrated, the
        sample is skipped (no spurious zero).

        Compliance ratio uses the standard zero-total convention: 0.0 when
        no judges have been scored.
        """
        try:
            from system_learning.engines.v6_kpi_producers import (  # noqa: PLC0415
                record_judge_human_kappa_freshness,
                record_judge_unknown_budget_compliance,
            )

            if self._last_calibration_epoch_by_rubric:
                oldest_rubric_id, oldest_epoch = min(
                    self._last_calibration_epoch_by_rubric.items(),
                    key=lambda kv: kv[1],
                )
                record_judge_human_kappa_freshness(
                    board,
                    last_calibration_epoch=oldest_epoch,
                    rubric_id=oldest_rubric_id,
                    now=now,
                )
            record_judge_unknown_budget_compliance(
                board,
                compliant_judges=self._compliant_judges,
                total_judges=self._total_judges,
                now=now,
            )
        except (ImportError, AttributeError, RuntimeError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break calibration
            logger.warning("v6_kpi_human_calibration_publish_failed: %s", exc)

    def record_judgment(
        self,
        trace_id: str,
        model_prediction: str,
        model_confidence: float,
        human_label: Literal["AGREE", "DISAGREE", "FLAG"],
        reviewer_id: str,
        reason_tags: list[str],
        timestamp_utc: int,
    ) -> CalibrationRecord:
        """Record human judgment and generate calibration record.

        Parameters
        ----------
        trace_id:
            Source execution trace identifier.
        model_prediction:
            Model's prediction/response.
        model_confidence:
            Model's reported confidence (0.0 to 1.0).
        human_label:
            Human judgment label.
        reviewer_id:
            Identifier of the human reviewer.
        reason_tags:
            Tags explaining the judgment.
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        CalibrationRecord
            Deterministic calibration record.
        """
        _emit_records_execution_trace("human_calibration_engine", "judgment_record_start", trace_id)

        # Calculate confidence delta
        human_confidence = self._human_label_to_confidence(human_label)
        confidence_delta = abs(model_confidence - human_confidence)

        # Create judgment record
        judgment = HumanJudgment(
            judgment_id=stable_sha256_json(
                {
                    "trace_id": trace_id,
                    "reviewer": reviewer_id,
                    "timestamp_utc": timestamp_utc,
                }
            ),
            trace_id=trace_id,
            model_prediction=model_prediction,
            human_label=human_label,
            confidence_delta=confidence_delta,
            reason_tags=tuple(sorted(reason_tags)),
            reviewer_id=reviewer_id,
            timestamp_utc=timestamp_utc,
        )

        # Calculate calibrated confidence
        calibrated_confidence = self._calibrate_confidence(
            model_confidence,
            human_label,
            confidence_delta,
        )

        # Determine drift flag
        drift_flag = self._detect_drift(confidence_delta, human_label)

        # Determine feedback action
        feedback_action = self._determine_feedback_action(
            drift_flag,
            confidence_delta,
            human_label,
        )

        _emit_records_execution_trace("human_calibration_engine", "judgment_record_complete", trace_id)

        record = CalibrationRecord(
            artifact_type="CALIBRATION_RECORD",
            record_id=stable_sha256_json(
                {
                    "trace_id": trace_id,
                    "judgment": judgment.judgment_id,
                    "timestamp_utc": timestamp_utc,
                }
            ),
            trace_id=trace_id,
            model_confidence=model_confidence,
            calibrated_confidence=calibrated_confidence,
            judgment=judgment,
            drift_flag=drift_flag,
            feedback_action=feedback_action,
            timestamp_utc=timestamp_utc,
        )

        # Add to history
        self._calibration_history.append(record)
        if len(self._calibration_history) > self.calibration_window:
            self._calibration_history.pop(0)

        logger.info(
            "Calibration recorded: trace=%s, drift=%s, action=%s, delta=%.2f",
            trace_id,
            drift_flag,
            feedback_action,
            confidence_delta,
        )

        return record

    def get_calibration_summary(self) -> dict[str, object]:
        """Get summary of calibration history."""
        if not self._calibration_history:
            return {
                "total_records": 0,
                "drift_count": 0,
                "average_confidence_delta": 0.0,
                "retrain_recommended": False,
            }

        drift_count = sum(1 for r in self._calibration_history if r.drift_flag)
        avg_delta = sum(r.judgment.confidence_delta for r in self._calibration_history) / len(
            self._calibration_history
        )

        # Recommend retrain if drift rate is high
        drift_rate = drift_count / len(self._calibration_history)
        retrain_recommended = drift_rate > 0.1  # More than 10% drift

        return {
            "total_records": len(self._calibration_history),
            "drift_count": drift_count,
            "average_confidence_delta": round(avg_delta, 6),
            "drift_rate": round(drift_rate, 6),
            "retrain_recommended": retrain_recommended,
        }

    def _human_label_to_confidence(self, label: Literal["AGREE", "DISAGREE", "FLAG"]) -> float:
        """Convert human label to confidence score."""
        confidence_map = {
            "AGREE": 1.0,
            "DISAGREE": 0.0,
            "FLAG": 0.2,  # Flagged items have low confidence
        }
        return confidence_map.get(label, 0.5)

    def _calibrate_confidence(
        self,
        model_confidence: float,
        human_label: Literal["AGREE", "DISAGREE", "FLAG"],
        confidence_delta: float,
    ) -> float:
        """Calibrate confidence based on human judgment."""
        human_confidence = self._human_label_to_confidence(human_label)

        # Simple calibration: weighted average
        # More weight to human judgment when there's large disagreement
        if confidence_delta > self.drift_threshold:
            # High disagreement - trust human more
            weight_human = 0.7
        else:
            # Low disagreement - blend evenly
            weight_human = 0.3

        calibrated = weight_human * human_confidence + (1 - weight_human) * model_confidence

        return round(calibrated, 6)

    def _detect_drift(
        self,
        confidence_delta: float,
        human_label: Literal["AGREE", "DISAGREE", "FLAG"],
    ) -> bool:
        """Detect if this judgment indicates potential drift."""
        # Large confidence delta indicates drift
        if confidence_delta > self.drift_threshold:
            return True

        # Disagreement or flagging indicates potential drift
        if human_label in ("DISAGREE", "FLAG"):
            return True

        return False

    def _determine_feedback_action(
        self,
        drift_flag: bool,
        confidence_delta: float,
        human_label: Literal["AGREE", "DISAGREE", "FLAG"],
    ) -> Literal["RETRAIN", "ADJUST", "IGNORE"]:
        """Determine feedback action based on calibration."""
        if not drift_flag:
            return "IGNORE"

        if human_label == "FLAG":
            return "RETRAIN"

        if confidence_delta > 0.5:
            return "RETRAIN"

        return "ADJUST"


__all__ = ["HumanCalibrationEngine", "HumanJudgment", "CalibrationRecord"]
