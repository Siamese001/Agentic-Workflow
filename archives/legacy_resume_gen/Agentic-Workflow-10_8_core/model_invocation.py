from typing import Dict, object


def invoke_model(prompt: str, route_metadata: Dict[str, object]) -> Dict[str, object]:
    """Deterministic model invocation stub that echoes prompt metadata."""

    completion = prompt[:30]
    model_name = route_metadata.get("model")
    return {
        "completion": completion,
        "model": model_name,
    }
