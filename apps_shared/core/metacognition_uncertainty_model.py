# from archives.legacy_root_folders.meta.metacognition.models import Hypothesis  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.meta.metacognition.uncertainty import compute_uncertainty  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_uncertainty_increases_with_signals() -> None:
    hs = [
        Hypothesis(id="h1", agent_id="a1", content="c1", confidence=0.8),
        Hypothesis(id="h2", agent_id="a1", content="c2", confidence=0.6),
    ]

    low = compute_uncertainty(hs, qa_signals=0, safety_signals=0)
    high = compute_uncertainty(hs, qa_signals=3, safety_signals=2)

    assert 0.0 <= low <= 1.0
    assert 0.0 <= high <= 1.0
    assert high > low






