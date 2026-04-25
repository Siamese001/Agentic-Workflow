"""Generic ingress-wired runner — the pattern used by all apps_* adapters.

Closes W8 residual from plan ``request-intake-w7-deferred-4c8e1f``.

Every ``apps_*`` runner needs the same five-step choreography:

    raw envelope → IngressEnvelopeCheck
                 → Stamped | Clarify | Rejected
                 → payload parser → domain request
                 → dispatch(domain_request) → domain result

``AppIngressRunner`` factors that choreography into a single class. Per-app
wrappers supply only:

* ``required_fields`` — the set of payload keys that MUST be present and
  non-empty strings for the request to be dispatchable; missing fields
  surface as :class:`ClarificationRequired` rather than a hard rejection.
* ``parse`` — a callable ``(normalized_payload: dict) -> domain_request | None``
  that builds the typed domain request.
* ``dispatch`` — a callable ``(domain_request) -> domain_result``.

The result of :meth:`handle_http` / :meth:`handle_chat` is therefore one of:

* ``domain_result`` (whatever the runner returns) on the happy path,
* :class:`ClarificationRequired` when the envelope is clean but intent is
  missing / cannot be parsed,
* an HTTP ``(status, headers, body)`` triple or chat rejection string when the
  envelope fails an E-stage.

This module does NOT know the concrete types. Tests should patch
``parse``/``dispatch`` rather than driving real domain code.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    ClarificationRequired,
    IngressEnvelopeCheck,
    StampedRequest,
)
from agentic_core.runtime.entry.chat_adapter import ChatIngressAdapter
from agentic_core.runtime.entry.http_adapter import HttpIngressAdapter


class AppIngressRunner:
    """Generic ingress-wired wrapper over an arbitrary app runner.

    Parameters
    ----------
    dispatch:
        Callable invoked with the parsed domain request on the happy path.
        Returns whatever the downstream runner produces.
    parse:
        Callable that turns a normalized payload dict into a typed domain
        request. Returns None when parsing fails (triggers clarification).
    required_fields:
        Iterable of payload keys that must be present and non-empty strings
        for the request to be considered complete. Used to emit a helpful
        ``ClarificationRequired`` when fields are missing.
    gate:
        Optional :class:`IngressEnvelopeCheck` instance. When omitted a fresh
        one is constructed with defaults.
    """

    def __init__(
        self,
        *,
        dispatch: Callable[[Any], Any],
        parse: Callable[[dict[str, Any]], Any | None],
        required_fields: Iterable[str],
        gate: IngressEnvelopeCheck | None = None,
    ) -> None:
        self._dispatch = dispatch
        self._parse = parse
        self._required = tuple(required_fields)
        self._gate = gate or IngressEnvelopeCheck()
        self._chat = ChatIngressAdapter(self._gate)
        self._http = HttpIngressAdapter(self._gate)

    # ------------------------------------------------------------------ U1
    def handle_chat(self, turn: dict[str, Any]) -> Any | ClarificationRequired | str:
        result = self._chat.handle(turn)
        if isinstance(result, str):
            return result  # rendered rejection
        if isinstance(result, ClarificationRequired):
            return result
        return self._dispatch_or_clarify(result)

    # ------------------------------------------------------------------ U2
    def handle_http(
        self, *, headers: dict[str, str], body: Any
    ) -> Any | ClarificationRequired | tuple[int, dict[str, str], str]:
        result = self._http.handle(headers=headers, body=body)
        if isinstance(result, tuple):
            return result
        if isinstance(result, ClarificationRequired):
            return result
        return self._dispatch_or_clarify(result)

    # ------------------------------------------------------------------ shared
    def _dispatch_or_clarify(self, stamped: StampedRequest) -> Any | ClarificationRequired:
        payload = stamped.normalized_payload
        if not isinstance(payload, dict):
            return ClarificationRequired(
                request_id=stamped.request_id,
                trace_root=stamped.trace_root,
                reason="request_payload must be an object with domain fields.",
                suggested_followups=(f"Provide a JSON object containing: {', '.join(self._required)}.",),
            )

        missing = [
            f for f in self._required if not (isinstance(payload.get(f), str) and payload.get(f, "").strip())
        ]
        if missing:
            return ClarificationRequired(
                request_id=stamped.request_id,
                trace_root=stamped.trace_root,
                reason=f"request_payload missing required fields: {missing}",
                suggested_followups=(f"Provide non-empty string values for: {', '.join(missing)}.",),
            )

        domain_request = self._parse(payload)
        if domain_request is None:
            return ClarificationRequired(
                request_id=stamped.request_id,
                trace_root=stamped.trace_root,
                reason="domain request could not be parsed from payload.",
                suggested_followups=(f"Verify types for required fields: {', '.join(self._required)}.",),
            )

        return self._dispatch(domain_request)


__all__ = ["AppIngressRunner"]
