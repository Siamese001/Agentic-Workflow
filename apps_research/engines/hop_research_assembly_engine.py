"""HOP stage 3 adapter — research artifact assembly.

Thin adapter mapping the shared ``HopPipelineExecutor`` stage contract
(``execute(context: dict) -> dict``) onto the existing
:class:`apps_research.engines.research_assembly_engine.ResearchAssemblyEngine`.

Stage contract (apps_research/config/hop_pipeline.py, stage 3):
    inputs:  ("research_request", "retrieved_research", "company_brief")
    outputs: ("research_artifact",)

The assembled artifact summary is returned under ``research_artifact``. The
already-produced ``company_brief`` remains in context untouched so FEC
extraction in GovernedResearchRun reads ``company_brief.company_brief_text``.
"""

from __future__ import annotations

from typing import Any


class HopResearchAssemblyEngine:
    """No-arg-constructable hop adapter for research artifact assembly."""

    AGENT_ID = "apps_research.hop_research_assembly_engine"

    def execute(self, context: dict[str, Any], **_kwargs: Any) -> dict[str, Any]:
        request = context.get("research_request")
        company_brief = context.get("company_brief") or {}
        if request is None:
            return {"research_artifact": {"sections": [], "source_count": 0}}

        from apps_research.engines.research_assembly_engine import (  # noqa: PLC0415
            ResearchAssemblyEngine,
        )

        engine = ResearchAssemblyEngine()
        result = engine.execute(
            request,
            company_brief_result=company_brief if isinstance(company_brief, dict) else None,
        )
        artifact = {
            "section_count": len(getattr(result, "sections", []) or []),
            "source_count": len(getattr(result, "source_register", []) or []),
            "mode": str(getattr(request, "mode", "") or ""),
            "pa_slot_bindings": getattr(result, "pa_slot_bindings", None),
        }
        return {"research_artifact": artifact}


__all__ = ["HopResearchAssemblyEngine"]
