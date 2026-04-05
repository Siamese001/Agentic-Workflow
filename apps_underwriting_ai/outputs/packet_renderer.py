"""
Packet Renderer - Renders decision packet as formatted output.
"""
import json
from typing import Dict, Any

from ..types import DecisionPacket


class PacketRenderer:
    """Renders DecisionPacket as formatted JSON."""
    
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
