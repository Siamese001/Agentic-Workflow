import logging
from typing import Any

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


LOGGER = logging.getLogger(__name__)
# from archives.legacy_root_folders.eval.simulation.metrics import compute_collaboration_score, c...


class InternalDummyOutcome:
    """TODO: Add docstring."""

    def __init__(self: Any, score: float, conflicts: int) -> None:
        self.OUTCOME = {"golden_eval_score": score,
            "correction_iterations": conflicts}
        self.agent_conflict_count = conflicts

    """TODO: Add docstring."""

def test_compute_collaboration_score_and_conflict_index() -> None:
    """TODO: Add docstring."""
    OUTPUTS = [
        InternalDummyOutcome(1.0, 0),
        InternalDummyOutcome(0.0, 2),
    ]

    COLLAB = compute_collaboration_score(OUTPUTS)
    CONFLICT = compute_conflict_index(OUTPUTS)

    assert isinstance(COLLAB, float)
    assert isinstance(CONFLICT, float)

