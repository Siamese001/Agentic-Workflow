"""Meta-learning module for execute_ssot - extracted from monolith.

This module contains meta-learning types and functions that were previously
in the monolithic execute_ssot.py file.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MetaLearningResult:
    """Result from meta-learning intake processing.

    Attributes:
        records_persisted: Number of records successfully persisted
        proposals: Tuple of generated proposals
        errors: List of any errors encountered
    """
    records_persisted: int = 0
    proposals: tuple = ()
    errors: list[str] | None = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        # GAP FIX: Validate records_persisted is non-negative
        if self.records_persisted < 0:
            raise ValueError(f"records_persisted must be non-negative, got {self.records_persisted}")


class MetaLearningError(Exception):
    """Exception raised for meta-learning related errors."""
    pass


def _fire_meta_learning_intake_required(
    state: Any,
    timestamp: int,
    _output_dir: Path,
    healing_actions: list[dict] | None = None,
) -> MetaLearningResult:
    """Process healing actions for meta-learning intake.

    Args:
        state: Runtime state object with healing context
        timestamp: Unix timestamp of the intake
        _output_dir: Reserved for future file output (currently unused)
        healing_actions: Optional list of healing actions to process

    Returns:
        MetaLearningResult with processing results
    """
    # Get healing actions from state if not provided
    if healing_actions is None:
        if hasattr(state, 'state') and isinstance(state.state, dict):
            healing_actions = state.state.get('healing_actions', [])
        else:
            healing_actions = []

    # GAP FIX: Validate timestamp is positive
    if timestamp <= 0:
        raise ValueError(f"Timestamp must be positive, got {timestamp}")

    # If no healing actions, return empty result
    if not healing_actions:
        return MetaLearningResult(records_persisted=0, proposals=())

    records_persisted = 0
    proposals = []
    errors = []

    for action in healing_actions:
        try:
            # Process each healing action
            if isinstance(action, dict):
                # Generate proposal from action
                proposal = {
                    'action_type': action.get('type', 'unknown'),
                    'target': action.get('target'),
                    'outcome': action.get('outcome', 'pending'),
                    'timestamp': timestamp,
                }
                proposals.append(proposal)
                records_persisted += 1
        except (AttributeError, TypeError, KeyError, ValueError, IndexError) as e:
            errors.append(f"Failed to process action: {e}")

    return MetaLearningResult(
        records_persisted=records_persisted,
        proposals=tuple(proposals),
        errors=errors,
    )
