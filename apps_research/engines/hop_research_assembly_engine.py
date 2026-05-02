"""HOP3 research_assembly — wraps ResearchAssemblyEngine.

See apps_research/config/hop_pipeline.py for stage I/O contract.
"""

from __future__ import annotations

from typing import Any


class HopResearchAssemblyEngine:
    """Adapter for stage 3 — final research artifact assembly."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_research.engines.research_assembly_engine import (
            ResearchAssemblyEngine,
        )

        request = context.get("research_request")
        retrieved = context.get("retrieved_research")
        brief = context.get("company_brief")

        engine = ResearchAssemblyEngine()

        artifact: Any = None
        for method_name in ("assemble", "build", "run", "execute"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    artifact = method(
                        request=request, retrieved=retrieved, brief=brief
                    )
                    break
                except TypeError:
                    try:
                        artifact = method(request, retrieved, brief)
                        break
                    except TypeError:
                        try:
                            artifact = method(request) if request is not None else method()
                            break
                        except TypeError:
                            continue

        return {
            "research_artifact": artifact,
            "research_assembly_completed": artifact is not None,
        }
