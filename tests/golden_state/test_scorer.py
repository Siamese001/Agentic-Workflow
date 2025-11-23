from eval.golden_state.models import JudgeVerdict
from eval.golden_state.scorer import aggregate_scores


def test_aggregate_scores_basic():
    verdicts = [
        JudgeVerdict(score=1.0, rating="pass", explanation=""),
        JudgeVerdict(score=0.0, rating="fail", explanation=""),
    ]

    agg = aggregate_scores(verdicts)

    assert agg["avg_score"] == 0.5
    assert agg["pass_count"] == 1.0
    assert agg["fail_count"] == 1.0
    assert agg["total"] == 2.0
