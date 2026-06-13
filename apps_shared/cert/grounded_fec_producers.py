"""Per-app FEC producers for the 5 grounded apps.

Plan: `.windsurf/plans/apps-eval-harness-final-8f3e21.md` W1.P1.

Context
-------
`apps_shared/cert/fec_producer.py` holds the registry + no-op default.
This module registers a concrete default producer for each of the 5
grounded apps so that `resolve_fec(app_id, ctx)` returns a minimally
populated FEC-shaped dict when the app's run_context carries an
``evidence_bundle`` — even before the per-app retrieval path is
rewired through C0.

Producer contract
-----------------
Each producer reads ``run_context["evidence_bundle"]`` if present and
projects to the FEC shape:

    {
      "c0_status": "PASS" | "WEAK_WITH_CAVEATS" | "FAIL" | "UNKNOWN",
      "support_score": float ∈ [0, 1],
      "cited_spans": list[str],
      "contradiction_flags": list[str],
      "contract_refs": list[str],
    }

When the evidence bundle is missing or empty, the producer returns an
empty dict — same as the no-op default. This keeps fail-open behavior
intact while enabling Exit-pipeline X1D to observe real evidence on
apps whose retrieval surfaces `evidence_bundle` today.

Registration
------------
`register_all()` is idempotent and is called by the module-import side
effect at the bottom of this file. Tests call `clear_registry()` first
and then `register_all()` to restore defaults.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping

from apps_shared.cert.fec_producer import register_producer

Logger = logging.getLogger(__name__)

GROUNDED_APP_IDS: tuple[str, ...] = (
    "apps_qna",
    "apps_research",
    "apps_exec",
    "apps_underwriting_ai",
)


def _coerce_str_list(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [str(x) for x in value]
    return [str(value)]


def _project_bundle_to_fec(bundle: Mapping[str, Any]) -> Dict[str, Any]:
    """Project an evidence_bundle into FEC-shaped dict.

    Tolerant of missing keys; absent fields default to safe values.
    """
    if not bundle:
        return {}
    support = bundle.get("support_score", None)
    try:
        support_score = float(support) if support is not None else 0.0
    except (TypeError, ValueError):
        support_score = 0.0
    support_score = max(0.0, min(1.0, support_score))

    # Derive c0_status from support_score + contradiction flags.
    contradiction_flags = _coerce_str_list(bundle.get("contradiction_flags"))
    cited_spans = _coerce_str_list(bundle.get("cited_spans") or bundle.get("spans"))
    contract_refs = _coerce_str_list(bundle.get("contract_refs") or bundle.get("refs"))

    explicit_status = bundle.get("c0_status")
    if isinstance(explicit_status, str) and explicit_status:
        c0_status = explicit_status.upper()
    elif contradiction_flags:
        c0_status = "FAIL"
    elif support_score >= 0.85:
        c0_status = "PASS"
    elif support_score >= 0.60:
        c0_status = "WEAK_WITH_CAVEATS"
    elif support_score > 0.0 or cited_spans:
        c0_status = "WEAK_WITH_CAVEATS"
    else:
        c0_status = "UNKNOWN"

    return {
        "c0_status": c0_status,
        "support_score": support_score,
        "cited_spans": cited_spans,
        "contradiction_flags": contradiction_flags,
        "contract_refs": contract_refs,
    }


def _make_default_producer(app_id: str):
    """Build a producer bound to app_id (for log context)."""

    def _producer(run_context: Mapping[str, Any]) -> Dict[str, Any]:
        if not run_context:
            return {}
        bundle = run_context.get("evidence_bundle") or run_context.get("final_evidence_contract")
        if not isinstance(bundle, Mapping) or not bundle:
            return {}
        fec = _project_bundle_to_fec(bundle)
        if fec:
            Logger.debug("[grounded_fec_producers] %s -> c0_status=%s", app_id, fec.get("c0_status"))
        return fec

    _producer.__name__ = f"default_fec_producer_{app_id}"
    return _producer


def register_all() -> tuple[str, ...]:
    """Register default producers for all grounded apps. Idempotent."""
    for app_id in GROUNDED_APP_IDS:
        register_producer(app_id, _make_default_producer(app_id))
    return GROUNDED_APP_IDS


# Module-import side effect — ensures producers are registered on import.
register_all()


__all__ = [
    "GROUNDED_APP_IDS",
    "register_all",
]
