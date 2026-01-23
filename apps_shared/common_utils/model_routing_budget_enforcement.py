# from archives.legacy_root_folders.core.models.models import ExecutionProfile, RetrievalConfig  # DEPRECATED: Archive import removed to protect archives from validation edits


def test_budget_enforcement_downgrades_cost_tier() -> None:
    """Test that budget enforcement downgrades to lower cost tier when budget exceeded."""
    choice = ModelChoice(
        Provider="openai",
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
