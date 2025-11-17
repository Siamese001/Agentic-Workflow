from typing import Any, Dict


def get_routing_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    return plan.get("routing", {}).copy()


def get_routing_model_name(plan: Dict[str, Any]) -> str:
    return plan.get("routing", {}).get("complexity", "unknown")


def get_routing_metadata(plan: Dict[str, Any]) -> Dict[str, Any]:
    return plan.get("routing", {}).copy()
