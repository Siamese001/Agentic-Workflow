"""HOP2 proposal_retrieval — wraps ProposalRetrievalEngine."""

from __future__ import annotations

from typing import Any


class HopProposalRetrievalEngine:
    """Adapter for stage 2 — retrieval of similar prior proposals."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_rfp.engines.proposal_retrieval_engine import (
            ProposalRetrievalEngine,
        )

        request = context.get("rfp_request")
        ingested = context.get("ingested_rfp")

        engine = ProposalRetrievalEngine()

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
            "retrieved_proposals": retrieved,
            "proposal_retrieval_completed": retrieved is not None,
        }
