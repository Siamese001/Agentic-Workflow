# from archives.legacy_root_folders.eval.golden_state.models import JudgeVerdict  # DEPRECATED: Archive import removed to protect archives from validation edits
# from archives.legacy_root_folders.eval.golden_state.scorer import aggregate_scores  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_aggregate_scores_basic() -> None:
    verdicts = [
        JudgeVerdict(score=1.0, rating="pass", explanation=""),
        JudgeVerdict(score=0.0, rating="fail", explanation=""),
    ]

    agg = aggregate_scores(verdicts)

    assert agg["avg_score"] == 0.5
    assert agg["pass_count"] == 1.0
    assert agg["fail_count"] == 1.0
    assert agg["total"] == 2.0
