import pytest

from client_strategy import ModelClient, build_client_for_route


def test_build_client_for_route_returns_model_client():
    route = {"route_name": "test"}
    client = build_client_for_route(route)
    assert isinstance(client, ModelClient)


def test_complete_returns_expected_keys():
    client = ModelClient()
    prompt = "Hello world"
    config = {"model_name": "test-model", "endpoint": "local"}

    result = client.complete(prompt, config)

    assert set(result.keys()) == {"completion", "model", "endpoint"}


def test_complete_is_deterministic():
    client = ModelClient()
    prompt = "Consistent prompt"
    config = {"model_name": "deterministic", "endpoint": "offline"}

    first_result = client.complete(prompt, config)
    second_result = client.complete(prompt, config)

    assert first_result == second_result
