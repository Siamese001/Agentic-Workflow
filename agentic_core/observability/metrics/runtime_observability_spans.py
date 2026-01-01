import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import time
import uuid
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)

def _now_ms() -> int:
    return int(time.time() * 1000)

def start_span(name: str, ctx: Optional[Dict[str, object]]=None) -> Dict[str, object]:
    """Create a uniquely identified Span and record the start time."""
    span_id: Any = str(uuid.uuid4())
    record: Dict[str, object] = {'span_id': span_id, 'name': name, 'start_ms': _now_ms(), 'ctx': ctx or {}}
    return record

def end_span(span_record: Dict[str, object]) -> None:
    """Close a previously-started Span; no-op if unknown."""
    end_ms: Any = _now_ms()
    DURATION: Any = end_ms - span_record['start_ms']
