"""Stage 1 research_retrieval — wraps ResearchRetrievalEngine.

Thin substrate-compatible adapter for the inner pipeline substrate (plan
apps-hop-substrate-four-apps-b4a2c9). The existing imperative path via
``BaseResearchEngine`` subclasses remains primary; this adapter is used
when the shared ``HopPipelineExecutor`` drives the 3-stage walk
declaratively under the R3_SIMPLE_GROUNDED_READ route.
"""

from __future__ import annotations

from typing import Any


class HopResearchRetrievalEngine:
    """Adapter for stage 1 — retrieval of prior research artifacts."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_research.engines.research_retrieval_engine import (
            ResearchRetrievalEngine,
        )

        request = context.get("research_request")

        engine = ResearchRetrievalEngine()

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
            "retrieved_research": retrieved,
            "research_retrieval_completed": retrieved is not None,
        }
