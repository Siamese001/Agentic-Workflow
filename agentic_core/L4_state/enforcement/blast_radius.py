"""Blast radius containment for Wave 16 - P2 Meta-Learning Prep.

This module provides deterministic blast radius computation
and containment for meta-learning proposals.
"""

import logging
import uuid
from tqdm import tqdm
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_appends_commit_receipt,
    _emit_records_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_verifies_blast_radius,
)

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BlastRadiusMetrics:
    """Metrics for blast radius calculation."""

    total_affected_objects: int
    state_surface_bytes: int
    mutation_depth: int
    cross_layer_impacts: int


class BlastRadiusCalculator:
    """Calculates deterministic blast radius for meta-learning proposals."""

    # guardian: allow-magic-config
    def __init__(self, max_radius: int = 1000, max_bytes: int = 10000000):
        self.max_radius = max_radius
        self.max_bytes = max_bytes

    def calculate_blast_radius(self, proposal: Any) -> BlastRadiusMetrics:
        """Calculate deterministic blast radius for a proposal.

        Args:
            proposal: Meta-learning proposal to analyze

        Returns:
            BlastRadiusMetrics with calculated values

        Raises:
            ValueError: If blast radius exceeds limits
        """
        _emit_snapshots_state(str(uuid.uuid4()), "BlastRadiusCalculator.calculate_blast_radius", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "BlastRadiusCalculator.calculate_blast_radius",
        )

        affected_objects = self._count_affected_objects(proposal)
        state_bytes = self._estimate_state_surface(proposal)
        mutation_depth = self._calculate_mutation_depth(proposal)
        cross_layer = self._count_cross_layer_impacts(proposal)
        metrics = BlastRadiusMetrics(
            total_affected_objects=affected_objects,
            state_surface_bytes=state_bytes,
            mutation_depth=mutation_depth,
            cross_layer_impacts=cross_layer,
        )
        if affected_objects > self.max_radius:
            raise ValueError(f"Blast radius {affected_objects} exceeds maximum {self.max_radius}")
        if state_bytes > self.max_bytes:
            raise ValueError(f"State surface {state_bytes} bytes exceeds maximum {self.max_bytes}")
        return metrics

    def _count_affected_objects(self, proposal: Any) -> int:
        """Count objects that would be affected by this proposal.

        Args:
            proposal: Proposal to analyze

        Returns:
            Number of affected objects
        """
        if hasattr(proposal, "__dict__"):
            return sum(1 for attr in proposal.__dict__ if not attr.startswith("_"))
        elif isinstance(proposal, (list, tuple)):
            return len(proposal)
        elif isinstance(proposal, dict):
            return len(proposal)
        else:
            return 1

    def _estimate_state_surface(self, proposal: Any) -> int:
        """Estimate the size of state surface this proposal affects.

        Args:
            proposal: Proposal to analyze

        Returns:
            Size in bytes
        """
        try:
            if hasattr(proposal, "__dict__"):
                proposal_str = str(proposal.__dict__)
            else:
                proposal_str = str(proposal)
            return len(proposal_str.encode("utf-8"))
        # guardian: allow-silent-swallow
        except (AttributeError, TypeError, ValueError, UnicodeError):
            if hasattr(proposal, "__dict__"):
                return len(proposal.__dict__) * 100
            return 1000

    def _calculate_mutation_depth(self, proposal: Any) -> int:
        """Calculate the depth of mutations this proposal would cause.

        Args:
            proposal: Proposal to analyze

        Returns:
            Mutation depth (1-5 scale)
        """
        depth = 1

        def _is_nested(val: Any) -> bool:
            if hasattr(val, "__dict__"):
                return True
            if isinstance(val, (dict, list, tuple)):
                return len(val) > 0
            return False

        if hasattr(proposal, "__dict__"):
            for value in tqdm(proposal.__dict__.values(), desc="depth scan", unit="field", leave=False):
                if _is_nested(value):
                    depth = max(depth, 2)
                    sub_iter = (
                        value.values()
                        if isinstance(value, dict)
                        else value
                        if isinstance(value, (list, tuple))
                        else value.__dict__.values()
                    )
                    for nested in sub_iter:
                        if _is_nested(nested):
                            depth = max(depth, 3)
        if isinstance(proposal, (list, tuple, dict)):
            items = proposal.values() if isinstance(proposal, dict) else proposal
            if any(_is_nested(item) for item in items):
                depth = max(depth, 2)
        return min(depth, 5)

    def _count_cross_layer_impacts(self, proposal: Any) -> int:
        """Count impacts that cross layer boundaries.

        Args:
            proposal: Proposal to analyze

        Returns:
            Number of cross-layer impacts
        """
        cross_layer_count = 0
        proposal_str = str(proposal).lower()
        layer_patterns = [
            "l0_routing",
            "l1_cognition",
            "l2_execution",
            "l3_orchestration",
            "l4_state",
            "l5_safety",
            "l6_observability",
            "l7_meta_learning",
        ]
        for pattern in layer_patterns:
            if pattern in proposal_str:
                cross_layer_count += 1
        return cross_layer_count


class BlastRadiusEnforcer:
    """Enforces blast radius containment policies."""

    def __init__(self, calculator: BlastRadiusCalculator | None = None):
        self.calculator = calculator or BlastRadiusCalculator()
        self._active_proposals: dict[str, BlastRadiusMetrics] = {}

    def enforce_blast_radius(self, proposal_id: str, proposal: Any) -> BlastRadiusMetrics:
        """Enforce blast radius containment for a proposal.

        Args:
            proposal_id: Unique identifier for the proposal
            proposal: The proposal to enforce

        Returns:
            BlastRadiusMetrics for the approved proposal

        Raises:
            ValueError: If blast radius exceeds limits
            RuntimeError: If proposal already exists
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "BlastRadiusEnforcer.enforce_blast_radius",
        )

        _emit_verifies_blast_radius(_trace_id, "BlastRadiusEnforcer", "enforce_blast_radius")
        if proposal_id in self._active_proposals:
            raise RuntimeError(f"Proposal {proposal_id} already exists")
        metrics = self.calculator.calculate_blast_radius(proposal)
        _emit_appends_commit_receipt(_trace_id, "BlastRadiusEnforcer", proposal_id)
        self._active_proposals[proposal_id] = metrics
        Logger.info(
            f"Proposal {proposal_id} approved: radius={metrics.total_affected_objects}, bytes={metrics.state_surface_bytes}",
        )
        return metrics

    def get_proposal_metrics(self, proposal_id: str) -> BlastRadiusMetrics | None:
        """Get metrics for an active proposal.

        Args:
            proposal_id: Proposal identifier

        Returns:
            BlastRadiusMetrics or None if not found
        """
        return self._active_proposals.get(proposal_id)

    def clear_proposal(self, proposal_id: str) -> None:
        """Clear a proposal from active tracking.

        Args:
            proposal_id: Proposal identifier to clear
        """
        if proposal_id in self._active_proposals:
            del self._active_proposals[proposal_id]
            Logger.info(f"Proposal {proposal_id} cleared")

    def get_total_blast_radius(self) -> int:
        """Get total blast radius across all active proposals.

        Returns:
            Total blast radius
        """
        return sum(metrics.total_affected_objects for metrics in self._active_proposals.values())

    def validate_total_impact(self) -> bool:
        """Validate that total impact across all proposals is acceptable.

        Returns:
            True if total impact is acceptable

        Raises:
            ValueError: If total impact exceeds limits
        """
        total_radius = self.get_total_blast_radius()
        total_bytes = sum(metrics.state_surface_bytes for metrics in self._active_proposals.values())
        if total_radius > self.calculator.max_radius:
            raise ValueError(
                f"Total blast radius {total_radius} exceeds maximum {self.calculator.max_radius}",
            )
        if total_bytes > self.calculator.max_bytes:
            raise ValueError(
                f"Total state surface {total_bytes} bytes exceeds maximum {self.calculator.max_bytes}",
            )
        return True


_blast_enforcer = BlastRadiusEnforcer()


def enforce_blast_radius(proposal_id: str, proposal: Any) -> BlastRadiusMetrics:
    """Exported function for blast radius enforcement."""
    return _blast_enforcer.enforce_blast_radius(proposal_id, proposal)


def get_proposal_metrics(proposal_id: str) -> BlastRadiusMetrics | None:
    """Exported function to get proposal metrics."""
    return _blast_enforcer.get_proposal_metrics(proposal_id)


def clear_proposal(proposal_id: str) -> None:
    """Exported function to clear a proposal."""
    _blast_enforcer.clear_proposal(proposal_id)


def validate_total_impact() -> bool:
    """Exported function to validate total impact."""
    return _blast_enforcer.validate_total_impact()
