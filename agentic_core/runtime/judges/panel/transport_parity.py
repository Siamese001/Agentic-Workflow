"""Transport parity audit — declared policy vs observed receipt."""

from __future__ import annotations

from agentic_core.runtime.judges.panel.adapter_protocol import DeclaredTransportPolicy
from agentic_core.runtime.judges.panel.panel_types import TransportParityViolation, TransportReceipt


def audit_transport_parity(
    provider_key: str,
    declared: DeclaredTransportPolicy,
    observed: TransportReceipt,
) -> list[TransportParityViolation]:
    violations: list[TransportParityViolation] = []
    if observed.provider_key != provider_key:
        violations.append(
            TransportParityViolation(
                code="provider_key_mismatch",
                detail=f"observed={observed.provider_key!r}",
                provider_key=provider_key,
            )
        )
    if observed.max_output_tokens < declared.max_output_tokens:
        violations.append(
            TransportParityViolation(
                code="max_output_tokens_below_declared",
                detail=f"observed={observed.max_output_tokens} declared={declared.max_output_tokens}",
                provider_key=provider_key,
            )
        )
    if declared.json_output_lock and observed.json_output_lock != declared.json_output_lock:
        violations.append(
            TransportParityViolation(
                code="json_output_lock_mismatch",
                detail=f"observed={observed.json_output_lock!r} declared={declared.json_output_lock!r}",
                provider_key=provider_key,
            )
        )
    if declared.system_includes_score_schema and observed.parse_status == "missing_schema_anchor":
        violations.append(
            TransportParityViolation(
                code="system_missing_score_schema",
                detail="parse_status indicates missing schema anchor",
                provider_key=provider_key,
            )
        )
    trunc_reasons = frozenset({"max_tokens", "length", "model_length"})
    if observed.finish_or_stop_reason in trunc_reasons:
        violations.append(
            TransportParityViolation(
                code="truncation_stop_reason",
                detail=f"finish/stop reason={observed.finish_or_stop_reason!r}",
                provider_key=provider_key,
            )
        )
    return violations


__all__ = ["audit_transport_parity"]
