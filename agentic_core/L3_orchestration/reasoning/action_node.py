from __future__ import annotations

from copy import deepcopy
from typing import Any

from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import evaluate_and_emit


def _invoke_evidence_sidecar(bundle: Any, ctx: Any, source: str) -> tuple[Any, Any]:
    return evaluate_and_emit(bundle, ctx, tool_name=source)


class ActionNode:
    def act(self, reasoning: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = dict(reasoning or {})
        result: dict[str, Any] = {
            "status": "ok",
            "executed": False,
            "source": "action_node",
        }

        bundle = normalized.get("evidence_bundle")
        ctx = normalized.get("execution_context")
        if bundle is not None and ctx is not None:
            contract, packet = _invoke_evidence_sidecar(bundle, ctx, "actionnode")
            result["evidence_contract_present"] = contract is not None
            result["eval_packet_present"] = packet is not None

        action = normalized.get("action")
        if callable(action):
            payload = normalized.get("payload")
            result["action_result"] = action(payload)
            result["executed"] = True
        elif "payload" in normalized:
            result["payload"] = deepcopy(normalized.get("payload"))

        return result


__all__ = ["ActionNode", "_invoke_evidence_sidecar"]
