"""apps_research airlock layer — PA boundary gates for research routes.

Routes covered:
- R3_SIMPLE_GROUNDED_READ: research_query airlock validates topic before C0 + synthesis
- R5_PRE_ROUTE_FALLBACK: no LLM dispatch; no airlock needed

Plan: apps-research-pa-spine-hardening-a28ea8 W3
"""

from __future__ import annotations

from apps_research.airlocks._otel_spans import airlock_span, OTEL_AVAILABLE

__all__ = ["airlock_span", "OTEL_AVAILABLE"]
