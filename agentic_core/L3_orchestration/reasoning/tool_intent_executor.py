from __future__ import annotations

from copy import deepcopy
from typing import Any

from agentic_core.L3_orchestration.reasoning.engines.evidence_eval_bridge import evaluate_and_emit


def _invoke_evidence_sidecar(bundle: Any, ctx: Any, source: str) -> tuple[Any, Any]:
    return evaluate_and_emit(bundle, ctx, tool_name=source)


class ToolIntentExecutor:
    def act(self, reasoning: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = dict(reasoning or {})
        result: dict[str, Any] = {
            "status": "ok",
            "executed": False,
            "source": "tool_intent_executor",
        }

        bundle = normalized.get("evidence_bundle")
        ctx = normalized.get("execution_context")
        if bundle is not None and ctx is not None:
            contract, packet = _invoke_evidence_sidecar(bundle, ctx, "toolintentexecutor")
            result["evidence_contract_present"] = contract is not None
            result["eval_packet_present"] = packet is not None

        tool = normalized.get("tool")
        tool_args = normalized.get("tool_args") or {}
        if callable(tool):
            if not isinstance(tool_args, dict):
                tool_args = {"value": tool_args}
            result["tool_result"] = tool(**tool_args)
            result["executed"] = True
        elif "tool_args" in normalized:
            result["tool_args"] = deepcopy(tool_args)

        return result


__all__ = ["ToolIntentExecutor", "_invoke_evidence_sidecar"]
