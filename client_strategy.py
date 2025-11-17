from typing import Dict, Any

from model_invocation import invoke_model


class ModelClient:
    """Abstract client for model execution. Deterministic stub only."""

    def __init__(self, route_metadata: Dict[str, Any] | None = None) -> None:
        self.route_metadata = route_metadata or {}

    def complete(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        merged_metadata = {**self.route_metadata, **(config or {})}
        return invoke_model(prompt, merged_metadata)


def build_client_for_route(route: Dict[str, Any]) -> ModelClient:
    # Return a new client bound to route metadata; side-effect free
    return ModelClient(route)


def configure_for_routing(route: Dict[str, Any]) -> Dict[str, Any]:
    model_name = route.get("model") or "stub-model-for-" + route.get(
        "complexity", "default"
    )
    endpoint = route.get("endpoint") or "/v1/" + route.get("complexity", "default")
    return {
        "model": model_name,
        "model_name": model_name,
        "endpoint": endpoint,
        "route": route,
    }
