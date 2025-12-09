from typing import Any, Dict


def compute_optimization_hint(spans: list) -> Dict[str, Any]:
    """
    Deterministic optimization hint based on span durations.
    """
    planning = next((s for s in spans if s.get("name") == "planning"), {"duration_ms": 0})
    execution = next((s for s in spans if s.get("name") == "execution"), {"duration_ms": 0})

    if float(planning.get("duration_ms", 0)) > float(execution.get("duration_ms", 0)):
        return {"suggestion": "reroute_fast"}
    return {"suggestion": "normal"}
