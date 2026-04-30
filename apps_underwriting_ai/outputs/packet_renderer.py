"""
Packet Renderer - Renders decision packet as formatted output.
"""

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)
import json
from typing import Any, Dict

from ..types import DecisionPacket


class PacketRenderer:
    """Renders DecisionPacket as formatted JSON."""

    @traces_execute(layer="L1_COGNITION")
    def render(self, packet: DecisionPacket) -> str:
        """Render packet as formatted JSON string."""
        return json.dumps(packet.dict(), indent=2, default=str)

    def render_compact(self, packet: DecisionPacket) -> Dict[str, Any]:
        """Render packet as compact dictionary."""
        return {
            "request_id": packet.request_id,
            "decision": packet.decision_state,
            "confidence": round(packet.confidence_score, 2),
            "review_required": packet.review_required,
            "conditions_count": len(packet.conditions),
            "covenants_count": len(packet.covenants),
        }


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_underwriting_ai.outputs.packet_renderer', "module_loaded")
