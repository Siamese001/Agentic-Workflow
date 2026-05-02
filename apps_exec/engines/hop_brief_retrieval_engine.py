"""HOP2 brief_retrieval — wraps BriefRetrievalEngine."""

from __future__ import annotations

from typing import Any


class HopBriefRetrievalEngine:
    """Adapter for stage 2 — retrieval of similar prior exec briefs."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_exec.engines.brief_retrieval_engine import BriefRetrievalEngine

        request = context.get("exec_request")
        ingested = context.get("ingested_documents")

        engine = BriefRetrievalEngine()

        retrieved: Any = None
        for method_name in ("retrieve", "run", "execute", "search"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    retrieved = method(request=request, ingested=ingested)
                    break
                except TypeError:
                    try:
                        retrieved = method(request, ingested)
                        break
                    except TypeError:
                        try:
                            retrieved = (
                                method(request) if request is not None else method()
                            )
                            break
                        except TypeError:
                            continue

        return {
            "retrieved_briefs": retrieved,
            "brief_retrieval_completed": retrieved is not None,
        }
