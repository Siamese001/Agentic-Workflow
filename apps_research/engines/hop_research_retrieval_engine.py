"""HOP stage 1 adapter — research retrieval.

Thin adapter mapping the shared ``HopPipelineExecutor`` stage contract
(``execute(context: dict) -> dict``) onto the existing imperative
:class:`apps_research.engines.research_retrieval_engine.ResearchRetrievalEngine`.

Stage contract (apps_research/config/hop_pipeline.py, stage 1):
    inputs:  ("research_request",)
    outputs: ("retrieved_research",)

Retrieval is best-effort prior-art lookup; an empty store yields an empty
``retrieved_research`` list, which is the normal degraded path and never
fails the stage.
"""

from __future__ import annotations

from typing import Any


class HopResearchRetrievalEngine:
    """No-arg-constructable hop adapter for past-research retrieval."""

    AGENT_ID = "apps_research.hop_research_retrieval_engine"

    def execute(self, context: dict[str, Any], **_kwargs: Any) -> dict[str, Any]:
        request = context.get("research_request")
        topic = self._topic(request)
        retrieved: list[dict[str, Any]] = []
        if topic:
            try:
                from apps_research.engines.research_retrieval_engine import (  # noqa: PLC0415
                    create_retrieval_engine,
                )

                engine = create_retrieval_engine(chromadb_path=None)
                results = engine.find_similar_research(
                    current_topic=topic,
                    artifact_mode="brief",
                    n_results=5,
                )
                retrieved = [
                    {
                        "research_id": r.research_id,
                        "topic": r.topic,
                        "quality_score": r.quality_score,
                        "similarity_score": r.similarity_score,
                    }
                    for r in results
                ]
            except (ImportError, RuntimeError, ValueError, AttributeError):
                # guardian: allow-log-and-swallow -- prior-art retrieval is a
                # best-effort optional boundary; an empty store is the normal
                # degraded path and must not fail the hop stage.
                retrieved = []
        return {"retrieved_research": retrieved}

    @staticmethod
    def _topic(request: Any) -> str:
        if request is None:
            return ""
        return str(getattr(request, "topic", "") or "").strip()


__all__ = ["HopResearchRetrievalEngine"]
