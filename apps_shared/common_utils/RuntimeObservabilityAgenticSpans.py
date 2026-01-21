from __future__ import annotations

from typing import Dict

# from archives.legacy_root_folders.runtime.observability.spans import start_span, end_span  # DEPRECATED: Archive import removed to protect archives from validation edits


def start_agent_span(name: str, meta: Dict[str, object]) -> str:
    """Start an agent-level span and return its span identifier.

    This is a thin convenience decorator over the core spans module so that
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
