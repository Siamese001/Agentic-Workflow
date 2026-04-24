"""Ingress-wired runner factory for ``apps_underwriting_ai``.

Closes W8.6. See ``agentic_core/runtime/entry/app_ingress_runner.py``.
"""

from __future__ import annotations

from typing import Any, Callable

from agentic_core.L5_safety.enforcement.ingress_envelope_check import IngressEnvelopeCheck
from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner

UW_REQUIRED_FIELDS: tuple[str, ...] = ("applicant_id", "policy_type", "amount")


def make_uw_ingress_runner(
    dispatch: Callable[[dict[str, Any]], Any],
    *,
    gate: IngressEnvelopeCheck | None = None,
) -> AppIngressRunner:
    return AppIngressRunner(
        dispatch=dispatch,
        parse=lambda payload: payload,
        required_fields=UW_REQUIRED_FIELDS,
        gate=gate,
    )


__all__ = ["UW_REQUIRED_FIELDS", "make_uw_ingress_runner"]
