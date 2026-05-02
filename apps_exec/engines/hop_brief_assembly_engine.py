"""HOP4 brief_assembly — wraps BriefAssemblyEngine."""

from __future__ import annotations

from typing import Any


class HopBriefAssemblyEngine:
    """Adapter for stage 4 — executive brief assembly."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_exec.engines.brief_assembly_engine import BriefAssemblyEngine

        request = context.get("exec_request")
        ingested = context.get("ingested_documents")
        retrieved = context.get("retrieved_briefs")
        capabilities = context.get("extracted_capabilities")

        engine = BriefAssemblyEngine()

        brief: Any = None
        for method_name in ("execute", "assemble", "build", "run"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    brief = method(
                        request=request,
                        ingested=ingested,
                        retrieved=retrieved,
                        capabilities=capabilities,
                    )
                    break
                except TypeError:
                    try:
                        brief = method(request, ingested, retrieved, capabilities)
                        break
                    except TypeError:
                        try:
                            brief = (
                                method(request) if request is not None else method()
                            )
                            break
                        except TypeError:
                            continue

        return {
            "exec_brief": brief,
            "brief_assembly_completed": brief is not None,
        }
