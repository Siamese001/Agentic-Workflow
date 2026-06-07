"""HOP stage 2 adapter — company brief generation.

Thin adapter mapping the shared ``HopPipelineExecutor`` stage contract
(``execute(context: dict) -> dict``) onto the existing
:class:`apps_research.engines.company_brief_engine.CompanyBriefEngine`.

Stage contract (apps_research/config/hop_pipeline.py, stage 2):
    inputs:  ("research_request", "retrieved_research")
    outputs: ("company_brief",)

The returned ``company_brief`` dict is the CompanyBriefEngine output. When
the apps_rg targeting route is active (``output_format``/``synthesis_template``
in jd_context, or the env flag), the dict carries either:
  - ``company_brief_text`` (a sealed, contract-valid plain-markdown brief), or
  - ``targeting_brief_disposition`` in {BLOCKED, DEGRADED, REJECTED} with NO
    ``company_brief_text`` — the fail-closed path.

Either way the dict surfaces ``_c0_bundle``/``_gate_verdict`` so downstream
FEC assembly can seal a rejection/degraded artifact when grounding is
insufficient.
"""

from __future__ import annotations

from typing import Any


class HopCompanyBriefEngine:
    """No-arg-constructable hop adapter for company-brief synthesis."""

    AGENT_ID = "apps_research.hop_company_brief_engine"

    def execute(self, context: dict[str, Any], **_kwargs: Any) -> dict[str, Any]:
        request = context.get("research_request")
        if request is None:
            return {
                "company_brief": {
                    "company": "",
                    "targeting_brief_disposition": "BLOCKED",
                    "targeting_brief_block_reason": "missing_research_request",
                }
            }

        from apps_research.engines.company_brief_engine import (  # noqa: PLC0415
            CompanyBriefEngine,
        )

        jd_context = dict(getattr(request, "jd_context", {}) or {})
        # Identify the company strictly from company_name; never from the JD.
        company_name = str(jd_context.get("company_name") or "").strip()
        topic = company_name or str(getattr(request, "topic", "") or "").strip()

        engine_input = {
            "topic": topic,
            "depth": str(getattr(request, "depth_profile", "") or "standard"),
            "jd_context": jd_context,
        }
        engine = CompanyBriefEngine()
        brief = engine.execute(engine_input)
        if isinstance(brief, dict):
            return {"company_brief": brief}
        return {
            "company_brief": {
                "company": topic,
                "targeting_brief_disposition": "BLOCKED",
                "targeting_brief_block_reason": "engine_returned_non_dict",
            }
        }


__all__ = ["HopCompanyBriefEngine"]
