import types

from core_v10_7.services import CollaborationEngine


def _make_config(enabled: bool):
    cfg = types.SimpleNamespace(
        enabled=enabled,
        max_team_size=4,
        allow_agent_feedback=True,
    )
    return types.SimpleNamespace(collaboration_config=cfg)


def test_team_formation():
    config = _make_config(enabled=True)
    engine = CollaborationEngine(config)

    team = engine.form_team("StrategyStack")

    assert team == ["StrategyStack", "StrategyStack_aux"]


def test_feedback_merge():
    config = _make_config(enabled=True)
    engine = CollaborationEngine(config)

    messages = [{"content": "alpha"}, {"content": "beta"}]

    merged = engine.merge_feedback(messages)

    assert merged == {"merged_feedback_count": 2}
