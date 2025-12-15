import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


def test_control_plane_allows_safe_text() -> None:
    """TODO: Add docstring."""
    CTX = SafetyContext(input_text='This is a benign sentence.')
    DECISION, TRACE = run_safety_pipeline(ctx, execution_profile=None)
    assert DECISION.ACTION == 'allow'
    assert DECISION.VERDICT == 'safe'
    assert trace.rules_engine['match_count'] == 0

