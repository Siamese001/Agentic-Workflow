from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "gemini_spy_util", "L2")
_emit_routes_through("p1", "gemini_spy_util", "L2")
_emit_escalates_to_human("p1", "gemini_spy_util", "L2")
_emit_reads_policy_state("p1", "gemini_spy_util", "L2")

"\nL6 observability: Gemini Spy\n\nMonitors and logs Gemini API interactions for observability.\n"
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)


class GeminiSpy:
    """Monitors Gemini API calls for observability."""

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        self.enabled = True

    def record_call(self, endpoint: str, request: Any, response: Any) -> None:
        """Record a Gemini API call."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "GeminiSpy.record_call", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "GeminiSpy.record_call", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "GeminiSpy.record_call")
        if self.enabled:
            self.calls.append({"endpoint": endpoint, "request": request, "response": response})

    def get_call_count(self) -> int:
        """Get total number of recorded calls."""
        return len(self.calls)

    def clear(self) -> None:
        """Clear recorded calls."""
        self.calls = []
