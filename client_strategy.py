from typing import Dict, Any

from model_invocation import invoke_model


class ModelClient:
    """Abstract client for model execution. Deterministic stub only."""

    def __init__(self, route_metadata: Dict[str, Any] | None = None) -> None:
        self.route_metadata = route_metadata or {}

    def complete(self, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke the deterministic stub with a fully rendered prompt."""

        merged_metadata = {**self.route_metadata, **(config or {})}
        return invoke_model(prompt, merged_metadata)


def build_client_for_route(route: Dict[str, Any]) -> ModelClient:
    # Return a new client bound to route metadata; side-effect free
    return ModelClient(route)


def configure_for_routing(route: Dict[str, Any]) -> Dict[str, Any]:
    selected_model = route.get("selected_model") or route.get("model")
    model_name = selected_model or "stub-model-for-" + route.get("complexity", "default")
    endpoint = route.get("endpoint") or "/v1/" + route.get("complexity", "default")
    return {
        "model": model_name,
        "model_name": model_name,
        "endpoint": endpoint,
        "route": route,
    }


def run_model_for_plan(plan: Dict[str, Any], state: Dict[str, Any]):
    from prompt_builder import build_prompt_from_plan_and_state
    from routing_policy import RoutingCriteria, decide_route
    from routing_views import get_routing_plan
    from client_strategy import build_client_for_route, configure_for_routing

    rendered = build_prompt_from_plan_and_state(plan, state)
    routing_plan = get_routing_plan(plan)

    safety_metadata = plan.get("safety_metadata", {}) if isinstance(plan, dict) else {}
    latency_seconds = routing_plan.get("latency_target", 0)
    try:
        latency_ms = int(latency_seconds * 1000)
    except Exception:
        latency_ms = 0

    criteria = RoutingCriteria(
        task_type=str(plan.get("mode", "unknown")),
        complexity=str(routing_plan.get("complexity", "low")),
        latency_target_ms=latency_ms,
        cost_ceiling_usd=float(routing_plan.get("cost_ceiling", 0.0)),
        risk_level=str(
            routing_plan.get(
                "risk_level", "strict" if safety_metadata.get("sensitivity") == "high" else "normal"
            )
        ),
    )
    decision = decide_route(criteria)
    routing_dict = {
        "selected_model": decision.model,
        "endpoint": decision.endpoint,
        "rationale": decision.rationale,
    }

    routing_plan.update(routing_dict)
    plan["routing"] = routing_plan

    client = build_client_for_route(routing_dict)
    config = configure_for_routing(routing_dict)
    result = client.complete(rendered["prompt"], config)

    return {
        "prompt": rendered["prompt"],
        "model_output": result,
        "routing": routing_dict,
    }
