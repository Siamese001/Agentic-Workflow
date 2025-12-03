from typing import Dict, Any


def invoke_model(prompt: str, route_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic model invocation stub that echoes prompt metadata."""

    completion = prompt[:30]
    model_name = route_metadata.get("model")
    return {
        "completion": completion,
        "model": model_name,
    }
