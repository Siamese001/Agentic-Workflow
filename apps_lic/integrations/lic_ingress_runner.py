"""Ingress-wired runner factory for ``apps_lic`` (Life-Insurance / Campaign).

Closes W8.3. See ``agentic_core/runtime/entry/app_ingress_runner.py``.
"""

from __future__ import annotations

from typing import Any, Callable

from agentic_core.L5_safety.enforcement.ingress_envelope_check import IngressEnvelopeCheck
from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner

LIC_REQUIRED_FIELDS: tuple[str, ...] = ("campaign_id", "audience", "objective")


def make_lic_ingress_runner(
    dispatch: Callable[[dict[str, Any]], Any],
    *,
    gate: IngressEnvelopeCheck | None = None,
) -> AppIngressRunner:
    return AppIngressRunner(
        dispatch=dispatch,
        parse=lambda payload: payload,
        required_fields=LIC_REQUIRED_FIELDS,
        gate=gate,
    )


__all__ = ["LIC_REQUIRED_FIELDS", "make_lic_ingress_runner"]
