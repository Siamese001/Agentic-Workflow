"""apps_rg airlock layer — boundary protection for prompt injection defense.

Per PROMPT_BOUNDARY_CONTRACT.md §3:
- U0 user-text airlock (apps_rg.airlocks.u0_user_text)
- C0 evidence airlock (apps_rg.airlocks.c0_evidence)
- Tool/model output airlock (apps_rg.airlocks.tool_output)
- HITL re-entry airlock (apps_lic.airlocks.hitl_reentry)

Each airlock emits a typed PA boundary receipt and an optional OTEL span.
"""

from __future__ import annotations

from apps_rg.airlocks._otel_spans import airlock_span, OTEL_AVAILABLE

__all__ = ["airlock_span", "OTEL_AVAILABLE"]
