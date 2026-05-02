"""HOP3 proposal_assembly — wraps ProposalAssemblyEngine."""

from __future__ import annotations

from typing import Any


class HopProposalAssemblyEngine:
    """Adapter for stage 3 — proposal assembly."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_rfp.engines.proposal_assembly_engine import (
            ProposalAssemblyEngine,
        )

        request = context.get("rfp_request")
        ingested = context.get("ingested_rfp")
        retrieved = context.get("retrieved_proposals")

        engine = ProposalAssemblyEngine()

        proposal: Any = None
        for method_name in ("assemble", "build", "run", "execute"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    proposal = method(
                        request=request, ingested=ingested, retrieved=retrieved
                    )
                    break
                except TypeError:
                    try:
                        proposal = method(request, ingested, retrieved)
                        break
                    except TypeError:
                        try:
                            proposal = (
                                method(request) if request is not None else method()
                            )
                            break
                        except TypeError:
                            continue

        return {
            "proposal": proposal,
            "proposal_assembly_completed": proposal is not None,
        }
