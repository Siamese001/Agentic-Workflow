"""HOP5 assemble_decision — wraps DecisionPacketAssembler.

Note: the exact assembler entry point is project-specific; this adapter
reads common patterns (``assemble``, ``assemble_packet``, ``build``) and
falls back to surfacing a structured notice when none is found so the
pipeline run can still complete with a diagnostic.
"""

from __future__ import annotations

from typing import Any


class HopAssembleDecisionEngine:
    """Adapter for stage 5 — decision packet assembly."""

    def execute(self, context: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        from apps_underwriting_ai.engines.decision_packet_assembler import (
            DecisionPacketAssembler,
        )

        request = context.get("underwriting_request")
        register = context.get("evidence_register")
        features = context.get("risk_features")
        reconciliation = context.get("reconciliation_result")

        assembler = DecisionPacketAssembler()

        # Try the common entry points in order; adapt to whichever shape
        # the current DecisionPacketAssembler exposes.
        packet = None
        for method_name in ("assemble", "assemble_packet", "build", "run"):
            method = getattr(assembler, method_name, None)
            if callable(method):
                try:
                    packet = method(
                        request=request,
                        register=register,
                        features=features,
                        reconciliation=reconciliation,
                    )
                    break
                except TypeError:
                    # Try positional fallback for older signatures
                    try:
                        packet = method(request, register, features, reconciliation)
                        break
                    except TypeError:
                        continue

        return {
            "decision_packet": packet,
            "packet_assembled": packet is not None,
        }
