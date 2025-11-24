from __future__ import annotations

from typing import Any, Dict

from runtime.observability.spans import start_span, end_span


def start_agent_span(name: str, meta: Dict[str, Any]) -> str:
    """Start an agent-level span and return its span identifier.

    This is a thin convenience wrapper over the core spans module so that
    higher layers have a semantic home for agent-centric tracing.
    """

    ctx = meta if isinstance(meta, dict) else {"meta": str(meta)}
    span_id = start_span(name, ctx=ctx)
    return span_id


def end_agent_span(span_id: str) -> None:
    """End a previously-started agent span.

    The span identifier is passed straight through to the spans module.
    """

    end_span(span_id)



