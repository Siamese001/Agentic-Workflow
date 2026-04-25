"""Desk D — Governed Board for Path D HITL Meta-Learning Feedback.

Desk D (L6 Observability / Cataloging Board) is the final stage in Path D flow:
- Extracts DPO pairs from human decisions
- Validates human decisions for meta-learning records
- Feeds RLHF optimizer for system adaptation
- Emits structured telemetry for governance visibility

Reference: docs/reference/HITL/Path D HITL.md, docs/reference/HITL/HITL Implementations v2.md
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from agentic_core.L3_orchestration.types.human_decision_artifact_types import (
    HumanAction,
    HumanDecisionArtifact,
)
from agentic_core.L5_safety.types.human_decision_artifact_types import (
    HumanDecisionArtifact as L5HumanDecisionArtifact,
)
from agentic_core.L6_observability.types.dpo_types import DPOExampleId
from agentic_core.L6_observability.utils.engines.hitl_dpo_pair_generator import (
    DefaultDeterministicDPOPairGenerator,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
)
from tqdm import tqdm


# Lazy import to avoid L6->L_SL gravity violation
def _get_rlhf_optimizer():
    from system_learning.engines.rlhf_optimizer_impl import (
        DefaultRLHFOptimizer,
        RLHFChangePackage,
    )

    return DefaultRLHFOptimizer, RLHFChangePackage


# Lifecycle trace emissions for P0-P4 governance
_emit_reads_policy_state("p0", "desk_d_governed_board", "policy_binding")
# P1 orchestration emissions
# P3 learning emissions
# P3 Learning Maturity emissions
_emit_captures_pattern("p3", "desk_d_governed_board", "pattern_learning")
_emit_writes_learning_snapshot("p3", "desk_d_governed_board", "learning_snapshot")
_emit_feeds_meta_learning("p3", "desk_d_governed_board", "meta_learning_feed")
_emit_updates_routing_strategy("p3", "desk_d_governed_board", "routing_strategy_update")
_emit_improves_agent_policy("p3", "desk_d_governed_board", "policy_improvement")
_emit_stores_learning_state("p3", "desk_d_governed_board", "learning_state")

# P4 telemetry emissions
_emit_updates_meta_learning_state("p4", "desk_d_governed_board", "meta_learning_state")
_emit_links_execution_to_snapshot("p4", "desk_d_governed_board", "snapshot_link")

# P4 observability emissions
_emit_records_incident_event("p4obs", "desk_d_governed_board", "incident_event")
_emit_captures_runtime_anomaly("p4obs", "desk_d_governed_board", "anomaly_capture")
_emit_updates_monitoring_state("p4obs", "desk_d_governed_board", "monitoring_state")
_emit_triggers_alert("p4obs", "desk_d_governed_board", "alert_trigger")
_emit_links_incident_trace("p4obs", "desk_d_governed_board", "incident_trace")

logger = logging.getLogger(__name__)


class BoardDecisionType(str, Enum):
    """Decision types emitted by the Governed Board."""

    ACCEPT_FOR_LEARNING = "accept_for_learning"
    REJECT_ANOMALOUS = "reject_anomalous"
    FLAG_FOR_REVIEW = "flag_for_review"
    DEFER_TO_SAFETY = "defer_to_safety"


@dataclass(frozen=True)
class DPOFeedbackRecord:
    """A single DPO feedback record processed by Desk D.

    Attributes:
        trace_id: Unique trace identifier
        example_id: DPO example with control/candidate hashes
        human_decision: APPROVE or REJECT from human reviewer
        reason_codes: Structured reason codes for learning
        control_output: Original control output bytes
        candidate_output: Candidate output bytes
        timestamp: Deterministic sequence number (not wall clock)
    """

    trace_id: str
    example_id: DPOExampleId
    human_decision: str
    reason_codes: tuple[str, ...]
    control_output: bytes
    candidate_output: bytes
    timestamp: int  # Sequence number for determinism

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "trace_id": self.trace_id,
            "example_id": {
                "control_hash": self.example_id.control_hash,
                "candidate_hash": self.example_id.candidate_hash,
            },
            "human_decision": self.human_decision,
            "reason_codes": list(self.reason_codes),
            "control_output_hash": hashlib.sha256(self.control_output).hexdigest()[:16],
            "candidate_output_hash": hashlib.sha256(self.candidate_output).hexdigest()[:16],
            "timestamp": self.timestamp,
        }


@dataclass
class BoardProcessingResult:
    """Result of Desk D processing a DPO record.

    Attributes:
        decision: Board's decision on this record
        rlhf_proposal: Optional RLHF change package
        confidence: Confidence in the decision (0-1)
        metadata: Additional processing metadata
    """

    decision: BoardDecisionType
    rlhf_proposal: RLHFChangePackage | None
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BoardMetrics:
    """Metrics for Desk D processing."""

    records_processed: int = 0
    records_accepted: int = 0
    records_rejected: int = 0
    records_flagged: int = 0
    records_deferred: int = 0
    rlhf_proposals_generated: int = 0
    learning_cycles_completed: int = 0


class DeskDGovernedBoard:
    """Desk D — Governed Board for Path D HITL Meta-Learning Feedback.

    The Governed Board sits at L6 Observability and processes human decisions
    into structured DPO pairs for the RLHF optimizer. It enforces governance
    invariants and emits telemetry for system visibility.

    Usage:
        board = DeskDGovernedBoard()

        # Process a human decision
        result = board.process_human_decision(
            trace_id="trace-123",
            human_artifact=artifact,
            control_output=b"original",
            candidate_output=b"proposed",
        )

        # Batch process for RLHF optimization
        batch_result = board.process_batch_for_rlhf(records, min_pairs=4)
    """

    def __init__(
        self,
        dpo_generator: DefaultDeterministicDPOPairGenerator | None = None,
        rlhf_optimizer: DefaultRLHFOptimizer | None = None,
    ) -> None:
        """Initialize the Governed Board.

        Args:
            dpo_generator: DPO pair generator (creates default if None)
            rlhf_optimizer: RLHF optimizer (creates default if None)
        """
        self._dpo_generator = dpo_generator or DefaultDeterministicDPOPairGenerator()
        self._rlhf_optimizer = rlhf_optimizer or DefaultRLHFOptimizer()
        self._metrics = BoardMetrics()
        self._feedback_history: list[DPOFeedbackRecord] = []
        self._processing_callbacks: list[Callable[[DPOFeedbackRecord, BoardProcessingResult], None]] = []

        logger.info("Desk D Governed Board initialized")

    def register_processing_callback(
        self,
        callback: Callable[[DPOFeedbackRecord, BoardProcessingResult], None],
    ) -> None:
        """Register a callback for DPO processing events.

        Args:
            callback: Function called with (record, result) after processing
        """
        self._processing_callbacks.append(callback)
        logger.debug("Registered Desk D processing callback")

    def process_human_decision(
        self,
        trace_id: str,
        human_artifact: HumanDecisionArtifact | L5HumanDecisionArtifact,
        control_output: bytes,
        candidate_output: bytes,
        reason_codes: tuple[str, ...] = ("HUMAN_REVIEW",),
    ) -> BoardProcessingResult:
        """Process a human decision artifact into DPO feedback.

        Args:
            trace_id: Unique trace identifier
            human_artifact: The human decision artifact (L3 or L5 type)
            control_output: Original control output bytes
            candidate_output: Candidate output bytes
            reason_codes: Structured reason codes

        Returns:
            BoardProcessingResult with decision and optional RLHF proposal
        """
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "DeskDGovernedBoard.process_human_decision",
        )

        # Map action to human decision string
        if hasattr(human_artifact, "action"):
            if isinstance(human_artifact.action, HumanAction):
                human_decision = "APPROVE" if human_artifact.action == HumanAction.APPROVE else "REJECT"
            else:
                human_decision = human_artifact.action
        else:
            human_decision = "APPROVE"

        # Generate DPO pair
        try:
            dpo_pair = self._dpo_generator.generate(
                control_output_bytes=control_output,
                candidate_output_bytes=candidate_output,
                human_decision=human_decision,
                reason_codes=reason_codes,
            )
        except ValueError as e:
            logger.error(f"Failed to generate DPO pair: {e}")
            return BoardProcessingResult(
                decision=BoardDecisionType.REJECT_ANOMALOUS,
                rlhf_proposal=None,
                confidence=0.0,
                metadata={"error": str(e)},
            )

        # Create feedback record
        record = DPOFeedbackRecord(
            trace_id=trace_id,
            example_id=dpo_pair.example_id,
            human_decision=dpo_pair.human_decision,
            reason_codes=dpo_pair.reasons,
            control_output=control_output,
            candidate_output=candidate_output,
            timestamp=len(self._feedback_history),
        )

        self._feedback_history.append(record)
        self._metrics.records_processed += 1

        # Validate and decide
        result = self._validate_and_decide(record)

        # Emit callbacks
        for callback in tqdm(self._processing_callbacks, desc="Processing", unit="item"):
            try:
                callback(record, result)
            except (
                AttributeError,
                RuntimeError,
                TypeError,
                ValueError,
            ) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                logger.error("[GovernoredBoard] Callback error: %s", exc)

        logger.info(
            "Desk D processed decision: trace=%s decision=%s confidence=%.2f",
            trace_id,
            result.decision.value,
            result.confidence,
        )

        return result

    def _validate_and_decide(self, record: DPOFeedbackRecord) -> BoardProcessingResult:
        """Validate a DPO record and make a board decision.

        Args:
            record: The DPO feedback record to validate

        Returns:
            BoardProcessingResult with decision and optional RLHF proposal
        """
        # Basic validation
        if not record.reason_codes:
            self._metrics.records_flagged += 1
            return BoardProcessingResult(
                decision=BoardDecisionType.FLAG_FOR_REVIEW,
                rlhf_proposal=None,
                confidence=0.5,
                metadata={"reason": "Missing reason codes"},
            )

        # Check for anomalous patterns
        if len(record.control_output) == 0 or len(record.candidate_output) == 0:
            self._metrics.records_rejected += 1
            return BoardProcessingResult(
                decision=BoardDecisionType.REJECT_ANOMALOUS,
                rlhf_proposal=None,
                confidence=0.0,
                metadata={"reason": "Empty output detected"},
            )

        # Accept for learning
        self._metrics.records_accepted += 1
        return BoardProcessingResult(
            decision=BoardDecisionType.ACCEPT_FOR_LEARNING,
            rlhf_proposal=None,  # Generated in batch processing
            confidence=0.95,
            metadata={"reason_codes": record.reason_codes},
        )

    def process_batch_for_rlhf(
        self,
        records: list[DPOFeedbackRecord],
        min_pairs: int = 3,
        surface_name: str = "desk_d_learning",
    ) -> RLHFChangePackage | None:
        """Process a batch of DPO records for RLHF optimization.

        Args:
            records: List of DPO feedback records
            min_pairs: Minimum pairs required for RLHF proposal
            surface_name: Surface name for RLHF optimization

        Returns:
            RLHFChangePackage if optimization generated, None otherwise
        """
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L6_OBSERVABILITY,
            "DeskDGovernedBoard.process_batch_for_rlhf",
        )

        if len(records) < min_pairs:
            logger.debug(f"Insufficient records for RLHF: {len(records)} < {min_pairs}")
            return None

        # Build DPO batch
        pairs = []
        for record in tqdm(records, desc="Processing", unit="item"):
            chosen_threshold = 0.8 if record.human_decision == "APPROVE" else 0.4
            rejected_threshold = 0.4 if record.human_decision == "APPROVE" else 0.8

            pairs.append(
                {
                    "chosen": {"threshold": chosen_threshold},
                    "rejected": {"threshold": rejected_threshold},
                    "surface": surface_name,
                }
            )

        dpo_batch = {"pairs": pairs}
        batch_bytes = json.dumps(dpo_batch).encode("utf-8")

        # Generate RLHF proposal
        snapshot_id = f"desk_d_batch_{len(self._metrics.learning_cycles_completed)}"
        proposal = self._rlhf_optimizer.propose_from_dpo(
            dpo_batch_bytes=batch_bytes,
            snapshot_id=snapshot_id,
        )

        if proposal:
            self._metrics.rlhf_proposals_generated += 1
            logger.info(
                "Desk D generated RLHF proposal: surface=%s direction=%s strength=%.2f",
                proposal.surface_name,
                proposal.direction,
                proposal.preference_strength,
            )

        return proposal

    def complete_learning_cycle(
        self,
        cycle_name: str = "desk_d_cycle",
    ) -> dict[str, Any]:
        """Complete a learning cycle and return summary.

        Args:
            cycle_name: Name for this learning cycle

        Returns:
            Dictionary with cycle summary and RLHF proposal if generated
        """
        # Get accepted records for this cycle
        accepted_records = [
            r for r in self._feedback_history if r.timestamp >= self._metrics.learning_cycles_completed * 100
        ]

        # Generate RLHF proposal from batch
        proposal = self.process_batch_for_rlhf(accepted_records)

        if proposal:
            self._metrics.learning_cycles_completed += 1

        return {
            "cycle_name": cycle_name,
            "cycle_number": self._metrics.learning_cycles_completed,
            "records_processed": self._metrics.records_processed,
            "records_accepted": self._metrics.records_accepted,
            "rlhf_proposal": proposal,
            "has_proposal": proposal is not None,
        }

    def get_metrics(self) -> BoardMetrics:
        """Get current board metrics."""
        return BoardMetrics(
            records_processed=self._metrics.records_processed,
            records_accepted=self._metrics.records_accepted,
            records_rejected=self._metrics.records_rejected,
            records_flagged=self._metrics.records_flagged,
            records_deferred=self._metrics.records_deferred,
            rlhf_proposals_generated=self._metrics.rlhf_proposals_generated,
            learning_cycles_completed=self._metrics.learning_cycles_completed,
        )

    def get_feedback_history(
        self,
        limit: int | None = None,
        decision_type: str | None = None,
    ) -> list[DPOFeedbackRecord]:
        """Get feedback history with optional filtering.

        Args:
            limit: Maximum records to return (newest first)
            decision_type: Filter by human decision type

        Returns:
            List of DPO feedback records
        """
        records = self._feedback_history

        if decision_type:
            records = [r for r in records if r.human_decision == decision_type]

        if limit:
            records = records[-limit:]

        return records

    def export_learning_report(self, output_path: Path | None = None) -> Path:
        """Export a learning report to disk.

        Args:
            output_path: Path for report (default: artifacts/hitl/desk_d_report.json)

        Returns:
            Path to the written report
        """
        if output_path is None:
            output_path = Path("artifacts/hitl/desk_d_report.json")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        metrics = self.get_metrics()
        report = {
            "board_type": "DeskD_GovernedBoard",
            "metrics": {
                "records_processed": metrics.records_processed,
                "records_accepted": metrics.records_accepted,
                "records_rejected": metrics.records_rejected,
                "records_flagged": metrics.records_flagged,
                "rlhf_proposals_generated": metrics.rlhf_proposals_generated,
                "learning_cycles_completed": metrics.learning_cycles_completed,
            },
            "feedback_summary": [r.to_dict() for r in self._feedback_history[-10:]],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)

        logger.info(f"Desk D learning report exported: {output_path}")
        return output_path


# Global board instance for singleton access
_global_desk_d_board: DeskDGovernedBoard | None = None


def get_desk_d_board() -> DeskDGovernedBoard:
    """Get the global Desk D Governed Board instance."""
    global _global_desk_d_board
    if _global_desk_d_board is None:
        _global_desk_d_board = DeskDGovernedBoard()
    return _global_desk_d_board


def reset_desk_d_board() -> None:
    """Reset the global Desk D board (for testing)."""
    global _global_desk_d_board
    _global_desk_d_board = None


__all__ = [
    "BoardDecisionType",
    "BoardMetrics",
    "BoardProcessingResult",
    "DeskDGovernedBoard",
    "DPOFeedbackRecord",
    "get_desk_d_board",
    "reset_desk_d_board",
]
