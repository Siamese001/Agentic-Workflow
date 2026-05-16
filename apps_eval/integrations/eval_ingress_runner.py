"""Ingress-wired runner factory for ``apps_eval``.

Closes W8.1. Wires :class:`AppIngressRunner` with apps_eval's required
payload fields. Callers supply the ``dispatch`` callable to decouple
ingress wiring from concrete domain runners.
"""

from __future__ import annotations

from typing import Any, Callable

from agentic_core.L5_safety.enforcement.ingress import IngressEnvelopeCheck
from agentic_core.runtime.entry.app_ingress_runner import AppIngressRunner

EVAL_REQUIRED_FIELDS: tuple[str, ...] = ("eval_id", "prompt", "expected")


def make_eval_ingress_runner(
    dispatch: Callable[[dict[str, Any]], Any],
    *,
    gate: IngressEnvelopeCheck | None = None,
) -> AppIngressRunner:
    """Return an :class:`AppIngressRunner` configured for ``apps_eval``.

    ``dispatch`` receives the normalized payload dict (already stamped and
    field-validated by the gate) and is expected to drive the domain runner.
    """

    return AppIngressRunner(
        dispatch=dispatch,
        parse=lambda payload: payload,
        required_fields=EVAL_REQUIRED_FIELDS,
        gate=gate,
    )


__all__ = ["EVAL_REQUIRED_FIELDS", "make_eval_ingress_runner"]


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_eval.integrations.eval_ingress_runner', "module_loaded")
