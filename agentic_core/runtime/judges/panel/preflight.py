"""Panel transport preflight — declared vs observed policy audit (app-agnostic)."""

from __future__ import annotations

from agentic_core.runtime.judges.panel.adapter_protocol import DeclaredTransportPolicy
from agentic_core.runtime.judges.panel.panel_types import TransportParityViolation, TransportReceipt
from agentic_core.runtime.judges.panel.transport_parity import audit_transport_parity


def audit_provider_transport_profile(
    provider_key: str,
    declared: DeclaredTransportPolicy,
    observed: TransportReceipt,
) -> list[TransportParityViolation]:
    """Run core transport parity checks for one provider."""
    return audit_transport_parity(provider_key, declared, observed)


__all__ = ["audit_provider_transport_profile"]
