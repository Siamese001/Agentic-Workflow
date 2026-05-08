"""C0 bypass receipt — typed proof that C0 retrieval lawfully did NOT run.

Emitted when ``RouteContract.grounding_required == False``. The receipt
proves three things:

    1. Grounding was not required for the route.
    2. C0 was not invoked (``c0_required=False``).
    3. The bypass had a permitted reason.

The receipt does NOT imply C0 ran. It does NOT carry candidates,
evidence, or graph traversal. Any of those would belong to a
``FinalEvidenceContract`` (see
``agentic_core.L0_routing.c0_retrieval.final_contract``).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

C0_BYPASS_RECEIPT_SCHEMA_VERSION = "1.0"

# W4 c0-policy-rectification-f7b2a9: Extended with typed bypass reasons from C0Policy.
# LEGACY reasons kept for backward compatibility during transition.
ALLOWED_C0_BYPASS_REASONS: frozenset[str] = frozenset({
    # Legacy reasons (deprecated)
    "GROUNDING_NOT_REQUIRED",
    "TERMINAL_SHORTCIRCUIT_NO_RETRIEVAL",
    "CACHE_REUSE_PRIOR_EVIDENCE",
    "FALLBACK_NO_RETRIEVAL",
    # W4: Typed bypass reasons (preferred)
    "BYPASS_PRELOADED_CONTEXT",
    "BYPASS_CACHE_RETURN",
    "BYPASS_FALLBACK",
    "NOT_REQUIRED",
})

_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "run_id",
    "request_id",
    "trace_root",
    "route_contract_id",
    "route_id",
    "grounding_required",
    "c0_required",
    "c0_bypass_reason",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class C0BypassReceipt:
    """Typed receipt proving C0 lawfully did not execute."""

    run_id: str
    request_id: str
    trace_root: str
    route_contract_id: str
    route_id: str
    c0_bypass_reason: str
    grounding_required: bool = False
    c0_required: bool = False
    schema_version: str = C0_BYPASS_RECEIPT_SCHEMA_VERSION
    deterministic_digest: str = ""

    def __post_init__(self) -> None:
        for name in ("run_id", "request_id", "trace_root", "route_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"C0BypassReceipt.{name} must be a non-empty string; got {value!r}"
                )
        if self.grounding_required is not False:
            raise ValueError(
                "C0BypassReceipt.grounding_required must be False; "
                "use FinalEvidenceContract when grounding actually happened"
            )
        if self.c0_required is not False:
            raise ValueError(
                "C0BypassReceipt.c0_required must be False"
            )
        if self.c0_bypass_reason not in ALLOWED_C0_BYPASS_REASONS:
            raise ValueError(
                f"C0BypassReceipt.c0_bypass_reason must be one of "
                f"{sorted(ALLOWED_C0_BYPASS_REASONS)}; got {self.c0_bypass_reason!r}"
            )
        if self.schema_version != C0_BYPASS_RECEIPT_SCHEMA_VERSION:
            raise ValueError(
                f"C0BypassReceipt.schema_version must be "
                f"{C0_BYPASS_RECEIPT_SCHEMA_VERSION!r}; got {self.schema_version!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "route_contract_id": self.route_contract_id,
            "route_id": self.route_id,
            "grounding_required": self.grounding_required,
            "c0_required": self.c0_required,
            "c0_bypass_reason": self.c0_bypass_reason,
            "deterministic_digest": self.deterministic_digest,
        }


def compute_c0_bypass_digest(payload: Mapping[str, Any]) -> str:
    stable: dict[str, Any] = {k: payload.get(k) for k in _DIGEST_STABLE_FIELDS}
    blob = _canonical_json(stable).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_c0_bypass_receipt(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    route_contract_id: str,
    route_id: str,
    c0_bypass_reason: str,
) -> C0BypassReceipt:
    digest_input: dict[str, Any] = {
        "schema_version": C0_BYPASS_RECEIPT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_contract_id": route_contract_id,
        "route_id": route_id,
        "grounding_required": False,
        "c0_required": False,
        "c0_bypass_reason": c0_bypass_reason,
    }
    digest = compute_c0_bypass_digest(digest_input)
    return C0BypassReceipt(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_contract_id=route_contract_id,
        route_id=route_id,
        c0_bypass_reason=c0_bypass_reason,
        grounding_required=False,
        c0_required=False,
        deterministic_digest=digest,
    )


__all__ = [
    "ALLOWED_C0_BYPASS_REASONS",
    "C0BypassReceipt",
    "C0_BYPASS_RECEIPT_SCHEMA_VERSION",
    "build_c0_bypass_receipt",
    "compute_c0_bypass_digest",
]
