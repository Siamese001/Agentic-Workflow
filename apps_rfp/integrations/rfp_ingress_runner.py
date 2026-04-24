"""Ingress-wired runner factory for ``apps_rfp``.

Closes W8.5. See ``agentic_core/runtime/entry/app_ingress_runner.py``.
"""

from __future__ import annotations

from typing import Any, Callable

from agentic_core.L5_safety.enforcement.ingress_envelope_check import IngressEnvelopeCheck
from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner

RFP_REQUIRED_FIELDS: tuple[str, ...] = ("rfp_id", "proposal_type", "deadline")


def make_rfp_ingress_runner(
    dispatch: Callable[[dict[str, Any]], Any],
    *,
    gate: IngressEnvelopeCheck | None = None,
) -> AppIngressRunner:
    return AppIngressRunner(
        dispatch=dispatch,
        parse=lambda payload: payload,
        required_fields=RFP_REQUIRED_FIELDS,
        gate=gate,
    )


__all__ = ["RFP_REQUIRED_FIELDS", "make_rfp_ingress_runner"]
