from core.models.models import ExecutionProfile, RetrievalConfig
from orchestration.model_routing import ModelChoice, enforce_budget


def test_budget_enforcement_downgrades_cost_tier():
    choice = ModelChoice(
        provider="openai",
        model_name="gpt-5.1-codex",
        cost_tier="high",
        estimated_cost=0.004,
        latency_ms=1200,
    )

    profile = ExecutionProfile(
        name="test_profile",
        description="test",
        retrieval=RetrievalConfig(),
        metadata={"max_cost_tier": "medium"},
    )

    adjusted = enforce_budget(choice, profile)

    assert adjusted.cost_tier in {"low", "medium"}
    assert adjusted.estimated_cost <= choice.estimated_cost






