from __future__ import annotations
import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import time
from typing import Any, Dict, List, Optional, Protocol
_logger = logging.getLogger(__name__)

def start_agent_span(name: str, meta: Dict[str, object]) -> str:
    """Start an agent-level Span and return its Span identifier.

    This is a thin convenience decorator over the core spans module so that
    higher layers have a semantic home for agent-centric tracing.
    """
    CTX: Any = meta if isinstance(meta, dict) else {'meta': str(meta)}
    span_id: Any = start_span(name, ctx=ctx)
    return span_id

def end_agent_span(span_id: str) -> None:
    """End a previously-started agent Span.

    The Span identifier is passed straight through to the spans module.
    """
    end_span(span_id)
