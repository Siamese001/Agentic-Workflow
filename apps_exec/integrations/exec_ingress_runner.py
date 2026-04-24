"""Ingress-wired runner factory for ``apps_exec``.

Closes W8.2. See ``agentic_core/runtime/entry/app_ingress_runner.py``.
"""

from __future__ import annotations

from typing import Any, Callable

from agentic_core.L5_safety.enforcement.ingress_envelope_check import IngressEnvelopeCheck
from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner

EXEC_REQUIRED_FIELDS: tuple[str, ...] = ("task_id", "instruction")


def make_exec_ingress_runner(
    dispatch: Callable[[dict[str, Any]], Any],
    *,
    gate: IngressEnvelopeCheck | None = None,
) -> AppIngressRunner:
    return AppIngressRunner(
        dispatch=dispatch,
        parse=lambda payload: payload,
        required_fields=EXEC_REQUIRED_FIELDS,
        gate=gate,
    )


__all__ = ["EXEC_REQUIRED_FIELDS", "make_exec_ingress_runner"]
