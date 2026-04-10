"""L5 Board Integration - CompletenessRAGProposer Bridge

Implements spec-compliant L5 Board integration from Agentic Retrieval Models v9:
- Receives proposals from CompletenessRAGProposer
- Proposal-only mode (C0 RULE: proposals never authorize)
- CompletenessChangePackage routing
- L5 Board approval workflow
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


@dataclass
class CompletenessChangePackage:
    """Change package for L5 Board review.

    Spec-compliant C0 RULE: proposal_only=True, never authorizes.
    """

    package_id: str
    proposal_type: str  # Depth++, Enrichment+, HybridMode, LexicalBoost, None
    confidence: float
    rationale: str
    affected_layers: list[str]

    # Source
    source_evaluator: str
    source_trace_id: str

    # Signals that triggered proposal
    trigger_signals: list[str]

    # C0 RULE enforcement
    proposal_only: bool = True

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "pending"  # pending, approved, rejected, escalated

    # L5 Board response
    board_decision: str | None = None
    decision_rationale: str | None = None
    decided_at: str | None = None


class L5BoardBridge:
    """Bridge between CompletenessRAGProposer and L5 Board.

    Routes proposals to L5 Board for decision per C0 RULE.
    """

    def __init__(self, board_endpoint: str | None = None):
        """Initialize L5 Board bridge.

        Args:
            board_endpoint: L5 Board API endpoint
        """
        self.board_endpoint = board_endpoint
        self._pending_packages: list[CompletenessChangePackage] = []
        self._decided_packages: list[CompletenessChangePackage] = []
        self._package_count = 0

    def submit_proposal(
        self,
        proposal_type: str,
        confidence: float,
        rationale: str,
        affected_layers: list[str],
        source_evaluator: str,
        source_trace_id: str,
        trigger_signals: list[str],
    ) -> CompletenessChangePackage:
        """Submit proposal to L5 Board.

        Args:
            proposal_type: Type of proposal
            confidence: Confidence score
            rationale: Proposal rationale
            affected_layers: Layers affected
            source_evaluator: Evaluator that generated proposal
            source_trace_id: Trace ID of source evaluation
            trigger_signals: Signals that triggered proposal

        Returns:
            CompletenessChangePackage
        """
        _trace_id = f"l5_submit_{self._package_count}"
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_SAFETY,
            "L5BoardBridge.submit_proposal",
        )

        package = CompletenessChangePackage(
            package_id=f"l5pkg_{source_trace_id[:16]}_{self._package_count:04d}",
            proposal_type=proposal_type,
            confidence=confidence,
            rationale=rationale,
            affected_layers=affected_layers,
            source_evaluator=source_evaluator,
            source_trace_id=source_trace_id,
            trigger_signals=trigger_signals,
            proposal_only=True,  # C0 RULE
            status="pending",
        )

        # _emit_records_proposal_submitted(
        #     _trace_id, package.package_id, proposal_type, confidence
        # )

        # Store pending
        self._pending_packages.append(package)
        self._package_count += 1

        Logger.info(
            f"Submitted proposal to L5 Board: {package.package_id} "
            f"({proposal_type}, confidence={confidence:.2f})",
        )

        return package

    def route_to_l5(self, package: CompletenessChangePackage) -> bool:
        """Route package to L5 Board for decision.

        Args:
            package: Change package to route

        Returns:
            True if routed successfully
        """
        _trace_id = f"l5_route_{package.package_id}"

        # In production, this would call L5 Board API
        # For now, we log and simulate
        Logger.info(f"Routing to L5 Board: {package.package_id}")

        # Simulate L5 Board decision process
        # In production, this would be async
        self._simulate_l5_decision(package)

        return True

    def _simulate_l5_decision(self, package: CompletenessChangePackage) -> None:
        """Simulate L5 Board decision (placeholder)."""
        # L5 Board decision logic would go here
        # For now, auto-approve high confidence, escalate low confidence

        if package.confidence > 0.8:
            package.status = "approved"
            package.board_decision = "approved"
            package.decision_rationale = "High confidence proposal - auto-approved"
        elif package.confidence > 0.5:
            package.status = "escalated"
            package.board_decision = "escalated"
            package.decision_rationale = "Medium confidence - requires human review"
        else:
            package.status = "rejected"
            package.board_decision = "rejected"
            package.decision_rationale = "Low confidence proposal - rejected"

        package.decided_at = datetime.utcnow().isoformat()

        # _emit_records_decision_logged(
        #     package.source_trace_id,
        #     package.package_id,
        #     package.board_decision,
        # )

        # Move to decided
        self._pending_packages = [p for p in self._pending_packages if p.package_id != package.package_id]
        self._decided_packages.append(package)

        Logger.info(
            f"L5 Board decision: {package.package_id} = {package.status}",
        )

    def get_pending_packages(self) -> list[CompletenessChangePackage]:
        """Get all pending packages."""
        return self._pending_packages.copy()

    def get_decided_packages(
        self,
        since: str | None = None,
    ) -> list[CompletenessChangePackage]:
        """Get decided packages."""
        packages = self._decided_packages

        if since:
            packages = [p for p in packages if p.decided_at and p.decided_at >= since]

        return packages

    def get_approval_stats(self) -> dict[str, Any]:
        """Get approval statistics."""
        decided = self._decided_packages

        if not decided:
            return {"total": 0}

        approved = sum(1 for p in decided if p.status == "approved")
        rejected = sum(1 for p in decided if p.status == "rejected")
        escalated = sum(1 for p in decided if p.status == "escalated")

        return {
            "total": len(decided),
            "approved": approved,
            "rejected": rejected,
            "escalated": escalated,
            "approval_rate": approved / len(decided) if decided else 0.0,
            "pending": len(self._pending_packages),
        }

    def export_packages(self, path: str) -> bool:
        """Export packages to file."""
        try:
            all_packages = self._pending_packages + self._decided_packages

            data = [
                {
                    "package_id": p.package_id,
                    "proposal_type": p.proposal_type,
                    "confidence": p.confidence,
                    "rationale": p.rationale,
                    "affected_layers": p.affected_layers,
                    "status": p.status,
                    "board_decision": p.board_decision,
                    "created_at": p.created_at,
                    "decided_at": p.decided_at,
                }
                for p in all_packages
            ]

            with open(path, "w") as f:
                json.dump(data, f, indent=2)

            Logger.info(f"Exported {len(data)} packages to {path}")
            return True

        except (ValueError, TypeError) as e:
            Logger.error(f"Failed to export packages: {e}")
            return False


class CompletenessRAGProposerBridge:
    """Bridge from CompletenessRAGProposer to L5 Board.

    Integrates Pipeline D proposals with L5 Board governance.
    """

    def __init__(self, l5_bridge: L5BoardBridge | None = None):
        """Initialize proposer bridge."""
        self.l5_bridge = l5_bridge or L5BoardBridge()

    def submit_proposal_from_pipeline_d(
        self,
        proposal_type: str,
        confidence: float,
        rationale: str,
        affected_layers: list[str],
        source_trace_id: str,
        trigger_signals: list[str],
    ) -> CompletenessChangePackage:
        """Submit Pipeline D proposal to L5 Board.

        Args:
            proposal_type: Proposal type
            confidence: Confidence score
            rationale: Proposal rationale
            affected_layers: Affected layers
            source_trace_id: Source trace ID
            trigger_signals: Trigger signals

        Returns:
            CompletenessChangePackage
        """
        return self.l5_bridge.submit_proposal(
            proposal_type=proposal_type,
            confidence=confidence,
            rationale=rationale,
            affected_layers=affected_layers,
            source_evaluator="CompletenessRAGProposer",
            source_trace_id=source_trace_id,
            trigger_signals=trigger_signals,
        )


# Global instance
_global_l5_bridge: L5BoardBridge | None = None
_global_proposer_bridge: CompletenessRAGProposerBridge | None = None


def get_global_l5_bridge() -> L5BoardBridge:
    """Get or create global L5 bridge."""
    global _global_l5_bridge
    if _global_l5_bridge is None:
        _global_l5_bridge = L5BoardBridge()
    return _global_l5_bridge


def get_global_proposer_bridge() -> CompletenessRAGProposerBridge:
    """Get or create global proposer bridge."""
    global _global_proposer_bridge
    if _global_proposer_bridge is None:
        _global_proposer_bridge = CompletenessRAGProposerBridge()
    return _global_proposer_bridge


def submit_proposal(
    proposal_type: str,
    confidence: float,
    rationale: str,
    affected_layers: list[str],
    source_trace_id: str,
    trigger_signals: list[str],
) -> CompletenessChangePackage:
    """Convenience function to submit proposal to L5."""
    return get_global_proposer_bridge().submit_proposal_from_pipeline_d(
        proposal_type=proposal_type,
        confidence=confidence,
        rationale=rationale,
        affected_layers=affected_layers,
        source_trace_id=source_trace_id,
        trigger_signals=trigger_signals,
    )
