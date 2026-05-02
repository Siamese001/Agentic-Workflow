"""HOP2 company_brief — wraps CompanyBriefEngine.

See apps_research/config/hop_pipeline.py for stage I/O contract.
"""

from __future__ import annotations

from typing import Any


class HopCompanyBriefEngine:
    """Adapter for stage 2 — company brief generation."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_research.engines.company_brief_engine import CompanyBriefEngine

        request = context.get("research_request")

        engine = CompanyBriefEngine()

        brief: Any = None
        for method_name in ("execute", "generate", "run", "build"):
            method = getattr(engine, method_name, None)
            if callable(method):
                try:
                    brief = method(request) if request is not None else method()
                    break
                except TypeError:
                    continue

        return {
            "company_brief": brief,
            "company_brief_completed": brief is not None,
        }
