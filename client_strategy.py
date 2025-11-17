from typing import Dict, Any


class ModelClient:
    """Abstract client for model execution. Deterministic stub only."""

    def complete(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        # Deterministic fake output:
        return {
            "completion": f"stubbed: {prompt[:20]}",
            "model": config.get("model_name", "unknown"),
            "endpoint": config.get("endpoint", "none"),
        }


def build_client_for_route(route: Dict[str, Any]) -> ModelClient:
    # Return a new client; side-effect free
    return ModelClient()
