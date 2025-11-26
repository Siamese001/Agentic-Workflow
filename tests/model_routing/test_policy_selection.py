from orchestration.model_routing import RoutingContext, choose_provider_and_model


def test_policy_selection_honors_requested_model():
    ctx = RoutingContext(agent_id="agent", task_type="llm_call", execution_profile=None)

    choice = choose_provider_and_model(ctx, requested_model="claude-haiku-4-5-20251001")

    assert choice.model_name == "claude-haiku-4-5-20251001"
    assert choice.provider == "anthropic"


def test_policy_selection_defaults_when_no_model():
    ctx = RoutingContext(agent_id="agent", task_type="llm_call", execution_profile=None)

    choice = choose_provider_and_model(ctx, requested_model=None)

    assert choice.model_name
    assert choice.provider in {"openai", "anthropic", "google"}







