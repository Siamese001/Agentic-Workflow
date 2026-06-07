"""Apps_rg ingress-wired runner ΓÇö proof of pattern for W7.1.

Closes deferred gap W7.1 (proof of pattern) from plan
``request-intake-w7-deferred-4c8e1f``.

This module is the *additive* layer that routes U1/U2/U3/U4 envelopes through
:class:`IngressEnvelopeCheck` before invoking the existing
:class:`GovernedRgRun`. The existing governed runner is NOT modified ΓÇö this
wrapper is a new, optional adoption path that other apps_* runners can copy.

Responsibility split::

    raw envelope ΓåÆ IngressEnvelopeCheck ΓåÆ StampedRequest / Clarification / Rejection
                                        Γöé
                                        ΓööΓåÆ ResumeRequest parser
                                           Γöé
                                           ΓööΓåÆ GovernedRgRun.run_governed_e2e()
"""

from __future__ import annotations

from typing import Any

from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    ClarificationRequired,
    IngressEnvelopeCheck,
    StampedRequest,
)
from agentic_core.runtime.entry.chat_adapter import ChatIngressAdapter
from agentic_core.runtime.entry.http_adapter import HttpIngressAdapter
from apps_rg.integrations.governed_rg_run import (
    GovernedRgE2ERunRecord,
    GovernedRgRun,
)


class RgIngressRunner:
    """Thin ingress-wired wrapper over :class:`GovernedRgRun`.

    Usage::

        runner = RgIngressRunner()
        result = runner.handle_chat({"user_id": "alice", "message": "..."})
        if isinstance(result, GovernedRgE2ERunRecord):
            ...  # happy path ΓÇö run completed
        elif isinstance(result, ClarificationRequired):
            ...  # surface back to caller
        else:
            ...  # rendered rejection (string for chat, tuple for HTTP)
    """

    def __init__(
        self,
        *,
        gate: IngressEnvelopeCheck | None = None,
        runner: GovernedRgRun | None = None,
    ) -> None:
        self._gate = gate or IngressEnvelopeCheck()
        self._runner = runner or GovernedRgRun()
        self._chat = ChatIngressAdapter(self._gate)
        self._http = HttpIngressAdapter(self._gate)

    # ------------------------------------------------------------------ U1 chat
    def handle_chat(
        self, turn: dict[str, Any]
    ) -> GovernedRgE2ERunRecord | ClarificationRequired | str:
        stamped = self._chat.handle(turn)
        if isinstance(stamped, str):
            return stamped  # rendered rejection string
        if isinstance(stamped, ClarificationRequired):
            return stamped
        return self._dispatch_or_clarify(stamped)

    # ------------------------------------------------------------------ U2 HTTP
    def handle_http(
        self, *, headers: dict[str, str], body: Any
    ) -> GovernedRgE2ERunRecord | ClarificationRequired | tuple[int, dict[str, str], str]:
        result = self._http.handle(headers=headers, body=body)
        if isinstance(result, tuple):
            return result
        if isinstance(result, ClarificationRequired):
            return result
        return self._dispatch_or_clarify(result)

    # ------------------------------------------------------------------ shared
    def _dispatch_or_clarify(
        self, stamped: StampedRequest
    ) -> GovernedRgE2ERunRecord | ClarificationRequired:
        resume = _parse_resume_request(stamped.normalized_payload)
        if resume is None:
            return ClarificationRequired(
                request_id=stamped.request_id,
                trace_root=stamped.trace_root,
                reason="request_payload missing required ResumeRequest fields.",
                suggested_followups=(
                    "Provide candidate_name, target_role, target_industry, experience_level.",
                ),
            )
        return self._runner.run_governed_e2e(resume)


# ---------------------------------------------------------------------------
# Payload ΓåÆ ResumeRequest parser
# ---------------------------------------------------------------------------


_RESUME_FIELDS = ("candidate_name", "target_role", "target_industry", "experience_level")


def _parse_resume_request(payload: Any):
    """Return a :class:`ResumeRequest` or None when parsing fails.

    Imported lazily so that importing this module does not force the full
    apps_rg domain graph to be imported at module load. Tests that depend
    solely on the ingress wiring (not the underlying runner) can substitute
    a stub payload-parser via monkeypatch.
    """

    if not isinstance(payload, dict):
        return None
    if not all(isinstance(payload.get(f), str) and payload.get(f) for f in _RESUME_FIELDS):
        return None

    from apps_rg.types.rg_types import ResumeRequest

    try:
        return ResumeRequest(
            candidate_name=str(payload["candidate_name"]),
            target_role=str(payload["target_role"]),
            target_industry=str(payload["target_industry"]),
            experience_level=str(payload["experience_level"]),
            trace_id=str(payload.get("trace_id") or ""),
        )
    except (TypeError, ValueError):
        return None


__all__ = ["RgIngressRunner"]


# ----------------------------------------------------------------------
# OTEL coverage ΓÇö module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_rg.integrations.rg_ingress_runner', "module_loaded")
