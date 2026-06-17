"""apps_shared.cert.exit_eval_hook — W2.P3 opt-in Exit invocation hook.

Plan: ``.claude/plans/apps-eval-harness-parity-f8d4a2.md`` W2.P3.

Problem (audit BLOCKER #5): ``apps_qna`` and ``apps_underwriting_ai``
cert routes declare ``execution_form: SINGLE_STEP`` + ``l3_required: false``.
Legitimate for those pipelines (statically-ordered, no retries/branches).
BUT: L3 bypass is currently interpreted as "skip the v6 Exit pipeline
too" — so the app-specific rubric (W1 wiring) never runs on cert routes.

Fix (W2.P3 Option D — opt-in, no hot-path disruption): cert_route_registry
gains an optional ``invoke_exit_eval: true`` flag. Per-app cert entrypoints
call :func:`maybe_invoke_exit_eval` after L2 seals the artifact; when the
flag is true AND the route is cert-reachable, the hook runs
``run_exit_eval`` against the sealed L2 receipts. When the flag is false /
absent, the hook is a no-op (preserves existing non-cert SINGLE_STEP
hot path).

Design invariants:

- FAIL-SOFT: any exception in the Exit invocation is swallowed and logged;
  the cert harness's existing bundle-building continues unaffected. The
  Exit disposition is an ADDITIONAL evidence surface, not a gate on the
  bundle itself.
- NO ROUTE-FORM CHANGE: the route remains SINGLE_STEP. No L3 orchestration,
  no retries, no state machine. Just a post-seal Exit pass.
- OPT-IN: only routes with ``invoke_exit_eval: true`` in their
  ``cert_route_registry.yaml`` participate.
- OBSERVABILITY: the Exit result is handed back to the caller so it can
  be serialized into the proof bundle if desired.

Adoption status (as of landing commit):

- ``apps_qna/config/cert_route_registry.yaml``: flag set true.
  ``apps_qna/__main__.py`` adoption of the hook is DEFERRED_SCOPE.
- ``apps_underwriting_ai/config/cert_route_registry.yaml``: flag set true.
  ``apps_underwriting_ai``'s cert entrypoint adoption is DEFERRED_SCOPE.

The harness-parity gate
(:mod:`ops_scripts.ci.check_app_domain_harness_parity`) surfaces the
adoption gap via the ``NO_CERT_EXIT_INVOCATION`` check (added in the
same PR as this hook).
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)


def should_invoke_exit_eval(route_entry: Mapping[str, Any] | None) -> bool:
    """Return True if the cert route declares ``invoke_exit_eval: true``.

    Accepts the per-route dict as it appears in
    ``cert_route_registry.yaml`` under ``routes[*]``. Missing / None / non-dict
    inputs are treated as "do not invoke" (fail-safe default — callers that
    don't have a route entry available also skip the hook).
    """
    if not isinstance(route_entry, Mapping):
        return False
    flag = route_entry.get("invoke_exit_eval", False)
    return bool(flag) is True


def maybe_invoke_exit_eval(
    receipts: dict[str, Any],
    route_entry: Mapping[str, Any] | None,
) -> Any | None:
    """Conditionally invoke the v6 Exit pipeline against sealed receipts.

    Args:
        receipts: The receipts dict normally passed to ``run_exit_eval``.
            At minimum must contain the keys that
            :func:`agentic_core.L3_orchestration.exit_eval.v6.preflight.normalize_to_packet`
            consumes (output, evidence_bundle, final_evidence_contract, etc.).
        route_entry: The route dict from ``cert_route_registry.yaml``. Used
            only to read the ``invoke_exit_eval`` flag.

    Returns:
        The ``ExitEvalResult`` if the hook fired and succeeded; ``None``
        when the flag is false / absent, when the hook raised (logged),
        or when receipts are malformed.

    Never raises.
    """
    if not should_invoke_exit_eval(route_entry):
        return None
    try:
        # Lazy import — avoids pulling the Exit pipeline into cert paths
        # that don't opt in.
        from agentic_core.L3_orchestration.exit_eval.v6.pipeline import (
            run_exit_eval,
        )
    except ImportError as exc:  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        _LOGGER.warning(
            "[apps_shared.cert] Exit pipeline unavailable for hook: %s", exc,
        )
        return None
    try:
        return run_exit_eval(receipts)
    except Exception as exc:  # noqa: BLE001  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        # guardian: allow-broad-except -- cert hook MUST NOT break the
        # bundle-building path; Exit failures are additional evidence only
        # (NOT a gate on the cert bundle). BLOCKER #5 closure tolerates
        # fail-soft behavior.
        _LOGGER.warning(
            "[apps_shared.cert] run_exit_eval raised %s: %s — cert bundle unaffected",
            type(exc).__name__, exc,
        )
        return None


__all__ = ["maybe_invoke_exit_eval", "should_invoke_exit_eval"]
