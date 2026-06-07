"""apps_qna FEC producer — builds a FinalEvidenceContract-shaped dict.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-c0-fec-producer-wiring-d4f1e8.md W1.P1.

Parent residual plan (apps-eval-harness-residual-a2d9c7) landed the
`apps_shared.cert.fec_producer` registry but left per-app producers
unimplemented. This module is the first real producer, landing
BLOCKER #4 for apps_qna as a demonstrated pattern other grounded apps
can copy.

Shape
-----
The returned dict follows `ExitReviewPacket.final_evidence_contract`
contract — a minimal but self-describing evidence record:

    {
        "schema_version": "1.0",
        "producer": "apps_qna.cert.fec_producer",
        "grounded": <bool>,
        "retrieval_sources": [<str>, ...],
        "template_ids": [<str>, ...],
        "route_id": <str>,
        "evidence_sufficiency": "grounded" | "template_only" | "empty",
    }

apps_qna is **template-deterministic** (no C0 retrieval today), so
`grounded=False` and `evidence_sufficiency="template_only"` are the
normal path. When C0 grounding wires in later, run_context will carry
`c0_retrieval_sources` and this producer will upgrade the packet
without a code change at the cert entrypoint.

Authority
---------
READ-ONLY. Never mutates run_context. Returns a fresh dict each call.
"""

from __future__ import annotations

import logging
from typing import Any, Mapping

_LOGGER = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"
_PRODUCER_ID = "apps_qna.cert.fec_producer"


def _safe_list(value: Any) -> list[str]:
    """Coerce value to list[str], dropping non-str items. Never raises."""
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if isinstance(item, (str, int, float))]


def _safe_str(value: Any, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def produce_fec(run_context: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a FEC-shaped dict from apps_qna's run_context.

    Keys consumed from ``run_context`` (all optional, all defensive):

    - ``route_id`` / ``route_contract.route_id``: cert route id
    - ``template_ids``: list of deterministic template ids used
    - ``c0_retrieval_sources``: list of retrieved source ids (empty today)
    - ``grounded``: explicit bool override (defaults to inferred)

    Returns a new dict on every call. Empty/malformed context yields a
    well-shaped "empty" packet rather than raising — keeps Exit's X1D
    gate at NOT_APPLICABLE.
    """
    ctx = run_context if isinstance(run_context, Mapping) else {}

    # route_id resolution: prefer explicit, fall back to route_contract
    route_id = _safe_str(ctx.get("route_id"))
    if not route_id:
        rc = ctx.get("route_contract")
        if isinstance(rc, Mapping):
            route_id = _safe_str(rc.get("route_id"))

    template_ids = _safe_list(ctx.get("template_ids"))
    retrieval_sources = _safe_list(ctx.get("c0_retrieval_sources"))

    explicit_grounded = ctx.get("grounded")
    if isinstance(explicit_grounded, bool):
        grounded = explicit_grounded
    else:
        grounded = bool(retrieval_sources)

    if grounded:
        sufficiency = "grounded"
    elif template_ids:
        sufficiency = "template_only"
    else:
        sufficiency = "empty"

    return {
        "schema_version": _SCHEMA_VERSION,
        "producer": _PRODUCER_ID,
        "grounded": grounded,
        "retrieval_sources": retrieval_sources,
        "template_ids": template_ids,
        "route_id": route_id,
        "evidence_sufficiency": sufficiency,
    }


__all__ = ["produce_fec"]
