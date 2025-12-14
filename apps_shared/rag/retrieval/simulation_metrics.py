import logging

# from archives.legacy_root_folders.eval.simulation.metrics import compute_collaboration_score, c...

class InternalDummyOutcome:
    """TODO: Add docstring."""

    def __init__(self, score: float, conflicts: int) -> None:
        self.outcome = {"golden_eval_score": score, "correction_iterations": conflicts}
        self.agent_conflict_count = conflicts

    """TODO: Add docstring."""

def test_compute_collaboration_score_and_conflict_index() -> None:
    """TODO: Add docstring."""
    outputs = [
        _DummyOutcome(1.0, 0),
        _DummyOutcome(0.0, 2),
    ]

    collab = compute_collaboration_score(outputs)
    conflict = compute_conflict_index(outputs)

    assert isinstance(collab, float)
    assert isinstance(conflict, float)
