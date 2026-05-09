"""apps_qna airlock layer — boundary protection for prompt injection defense.

Two airlock surfaces per apps_qna route types:

- build_time_compiler airlock: validates template input variables (no LLM at
  build time; inputs are static interview YAML fields).
- R4_SINGLE_ACTION airlock (live interview): validates user question text
  before LLM dispatch.

Each airlock emits a PA boundary receipt and an optional OTEL span.

Plan: .windsurf/plans/apps-qna-pa-spine-hardening-498d20.md W3
"""

from __future__ import annotations

from apps_qna.airlocks._otel_spans import airlock_span, OTEL_AVAILABLE

__all__ = ["airlock_span", "OTEL_AVAILABLE"]
