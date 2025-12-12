from orchestration.model_routing import RoutingContext, select_model


def test_selector_integration_uses_cache_for_generic_calls():
    ctx = RoutingContext(agent_id="agent1", task_type="llm_call", execution_profile=None)

    first = select_model(ctx, requested_model=None, execution_profile=None)
    second = select_model(ctx, requested_model=None, execution_profile=None)

    assert first.provider == second.provider
    assert first.model_name == second.model_name







