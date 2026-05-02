"""L3 bypass receipt — typed proof that L3 lawfully did NOT run.

Emitted when ``RouteContract.execution_form != MANAGED_WORKFLOW``. The
receipt proves three things at once:

    1. L3 was not invoked (``l3_required=False``).
    2. The bypass had a permitted reason (``l3_bypass_reason`` from the
       allowed set).
    3. The fact that a static DAG was/was not available is captured
       (``static_dag_available`` plus optional ``static_dag_ref`` and
       ``why_static_dag_not_used``).

The receipt does NOT imply L3 ran. It does NOT carry node selection,
step contracts, or DAG traversal. Any of those would belong to a
``RuntimeL3OrchestrationReceipt`` (not in this pass).

Doctrine alignment:
    - Allowed bypass reasons are kept in lockstep with the spec
      (TERMINAL_SHORTCIRCUIT, SINGLE_STEP_ROUTE, FALLBACK_RET,
      NO_MANAGED_WORKFLOW_REQUIRED).
    - Today's ``TerminalExecutionForm`` enum only declares
      ``TERMINAL_SHORTCIRCUIT``; this receipt's ``execution_form`` field
      is intentionally a ``str`` so future MANAGED_WORKFLOW / SINGLE_STEP
      variants can flow through without a contract migration.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

L3_BYPASS_RECEIPT_SCHEMA_VERSION = "1.0"

ALLOWED_L3_BYPASS_REASONS: frozenset[str] = frozenset({
    "TERMINAL_SHORTCIRCUIT",
    "SINGLE_STEP_ROUTE",
    "FALLBACK_RET",
    "NO_MANAGED_WORKFLOW_REQUIRED",
})

_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "run_id",
    "request_id",
    "trace_root",
    "route_contract_id",
    "route_id",
    "execution_form",
    "l3_required",
    "l3_bypass_reason",
    "static_dag_available",
    "why_static_dag_not_used",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class L3BypassReceipt:
    """Typed receipt proving L3 lawfully did not execute."""

    run_id: str
    request_id: str
    trace_root: str
    route_contract_id: str
    route_id: str
    execution_form: str
    l3_bypass_reason: str
    why_static_dag_not_used: str
    static_dag_available: bool = False
    static_dag_ref: str = ""
    l3_required: bool = False
    schema_version: str = L3_BYPASS_RECEIPT_SCHEMA_VERSION
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        for name in ("run_id", "request_id", "trace_root", "route_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"L3BypassReceipt.{name} must be a non-empty string; got {value!r}"
                )
        if self.l3_required is not False:
            raise ValueError(
                "L3BypassReceipt.l3_required must be False; "
                "use RuntimeL3OrchestrationReceipt when L3 actually ran"
            )
        if self.l3_bypass_reason not in ALLOWED_L3_BYPASS_REASONS:
            raise ValueError(
                f"L3BypassReceipt.l3_bypass_reason must be one of "
                f"{sorted(ALLOWED_L3_BYPASS_REASONS)}; got {self.l3_bypass_reason!r}"
            )
        if not isinstance(self.static_dag_available, bool):
            raise ValueError(
                "L3BypassReceipt.static_dag_available must be bool"
            )
        if self.schema_version != L3_BYPASS_RECEIPT_SCHEMA_VERSION:
            raise ValueError(
                f"L3BypassReceipt.schema_version must be "
                f"{L3_BYPASS_RECEIPT_SCHEMA_VERSION!r}; got {self.schema_version!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "route_contract_id": self.route_contract_id,
            "route_id": self.route_id,
            "execution_form": self.execution_form,
            "l3_required": self.l3_required,
            "l3_bypass_reason": self.l3_bypass_reason,
            "static_dag_available": self.static_dag_available,
            "static_dag_ref": self.static_dag_ref,
            "why_static_dag_not_used": self.why_static_dag_not_used,
            "deterministic_digest": self.deterministic_digest,
        }


def compute_l3_bypass_digest(payload: Mapping[str, Any]) -> str:
    stable: dict[str, Any] = {k: payload.get(k) for k in _DIGEST_STABLE_FIELDS}
    blob = _canonical_json(stable).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_l3_bypass_receipt(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    route_contract_id: str,
    route_id: str,
    execution_form: str,
    l3_bypass_reason: str,
    why_static_dag_not_used: str,
    static_dag_available: bool = False,
    static_dag_ref: str = "",
) -> L3BypassReceipt:
    digest_input: dict[str, Any] = {
        "schema_version": L3_BYPASS_RECEIPT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_contract_id": route_contract_id,
        "route_id": route_id,
        "execution_form": execution_form,
        "l3_required": False,
        "l3_bypass_reason": l3_bypass_reason,
        "static_dag_available": bool(static_dag_available),
        "why_static_dag_not_used": why_static_dag_not_used,
    }
    digest = compute_l3_bypass_digest(digest_input)
    return L3BypassReceipt(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_contract_id=route_contract_id,
        route_id=route_id,
        execution_form=execution_form,
        l3_bypass_reason=l3_bypass_reason,
        why_static_dag_not_used=why_static_dag_not_used,
        static_dag_available=bool(static_dag_available),
        static_dag_ref=static_dag_ref,
        l3_required=False,
        deterministic_digest=digest,
    )


__all__ = [
    "ALLOWED_L3_BYPASS_REASONS",
    "L3BypassReceipt",
    "L3_BYPASS_RECEIPT_SCHEMA_VERSION",
    "build_l3_bypass_receipt",
    "compute_l3_bypass_digest",
]
