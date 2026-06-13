"""HOP1 evaluation_retrieval — wraps EvaluationRetrievalEngine."""

from __future__ import annotations

from typing import Any


class HopEvaluationRetrievalEngine:
    """Adapter for stage 1 — retrieval of prior evaluation results."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_eval.engines.evaluation_retrieval_engine import (
            EvaluationRetrievalEngine,
        )

        request = context.get("eval_request")

        engine = EvaluationRetrievalEngine()

        retrieved: Any = None
        for method_name in ("retrieve", "run", "execute", "search"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    retrieved = method(request) if request is not None else method()
                    break
                except TypeError:
                    continue

        return {
            "retrieved_evaluations": retrieved,
            "evaluation_retrieval_completed": retrieved is not None,
        }
