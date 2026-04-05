"""
Audit Trace Renderer - Renders audit trace as formatted output.
"""
import json
from typing import Dict, Any

from ..types import AuditTrace


class AuditTraceRenderer:
    """Renders AuditTrace as formatted JSON."""
    
    def render(self, trace: AuditTrace) -> str:
        """Render audit trace as formatted JSON string."""
        data = {
            "request_id": trace.request_id,
            "trace_id": trace.trace_id,
            "policy_hash": trace.policy_hash,
            "derived_features": trace.derived_features.dict() if trace.derived_features else {},
            "evidence_count": len(trace.evidence_refs),
            "validators_executed": trace.validators_run,
            "routing_outcome": trace.routing_outcome,
            "decision_proposal": trace.decision_proposal,
            "human_review_triggered": trace.human_review_triggered,
            "determinism_digest": trace.determinism_digest,
        }
        
        return json.dumps(data, indent=2, default=str)
    
    def render_minimal(self, trace: AuditTrace) -> Dict[str, Any]:
        """Render minimal audit trace for embedding."""
        return {
            "request_id": trace.request_id,
            "trace_id": trace.trace_id,
            "decision": trace.decision_proposal,
            "human_review": trace.human_review_triggered,
        }
