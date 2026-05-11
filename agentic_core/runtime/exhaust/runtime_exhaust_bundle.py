"""RuntimeExhaustBundle — post-runtime exhaust contract for L6 writeback.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

This is the ONLY input to L6WritebackProposer.  It is created AFTER Exit
emits its X3 disposition and NEVER before.  L6 receives this bundle as a
completed, sealed view of the run.  L6 cannot mutate the current run through
this contract — the ``current_run_closed`` and ``created_after_exit`` fields
enforce this invariant at construction time.

Scope invariants (non-negotiable):
  - created_after_exit MUST be True; construction raises if False.
  - current_run_closed MUST be True; construction raises if False.
  - L6 consumes this bundle as read-only evidence.
  - No durable writes are triggered by creating this bundle.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return "sha256::" + hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeExhaustBundle:
    """Sealed post-runtime evidence bundle consumed exclusively by L6.

    Created only after Exit emits its X3 disposition.
    All fields are immutable — L6 cannot mutate the current run.
    """

    # Identity
    bundle_id: str = ""
    request_id: str = ""
    run_id: str = ""
    trace_root: str = ""

    # Cross-run provenance
    route_contract_ref: str = ""
    sealed_result_ref: str = ""         # SealedWorkflowPackage.package_id
    gate_mesh_result_ref: str = ""      # GateMeshResult.deterministic_digest
    exit_disposition_ref: str = ""      # ExitDispositionReceipt.deterministic_digest

    # Runtime receipt bundle
    runtime_receipt_refs: tuple[str, ...] = field(default_factory=tuple)

    # Learning / meta-feedback profile refs (declarative, not authoritative)
    learning_profile_ref: str = ""
    meta_feedback_profile_ref: str = ""

    # Post-run learning signals (inert summary data)
    learning_signals: tuple[str, ...] = field(default_factory=tuple)

    # Lifecycle guards — enforced at construction
    created_after_exit: bool = False    # MUST be True
    current_run_closed: bool = False    # MUST be True

    # Timestamps
    created_at: str = ""

    # Integrity
    deterministic_digest: str = ""

    schema_version: str = "w10.1"

    def __post_init__(self) -> None:
        if not self.created_after_exit:
            raise ValueError(
                "RuntimeExhaustBundle: created_after_exit must be True. "
                "Bundle must be created only after Exit emits its X3 disposition."
            )
        if not self.current_run_closed:
            raise ValueError(
                "RuntimeExhaustBundle: current_run_closed must be True. "
                "Bundle must not be created while current run is still open."
            )

    def as_dict(self) -> dict:
        return {
            "bundle_id": self.bundle_id,
            "request_id": self.request_id,
            "run_id": self.run_id,
            "trace_root": self.trace_root,
            "route_contract_ref": self.route_contract_ref,
            "sealed_result_ref": self.sealed_result_ref,
            "gate_mesh_result_ref": self.gate_mesh_result_ref,
            "exit_disposition_ref": self.exit_disposition_ref,
            "runtime_receipt_refs": list(self.runtime_receipt_refs),
            "learning_profile_ref": self.learning_profile_ref,
            "meta_feedback_profile_ref": self.meta_feedback_profile_ref,
            "learning_signals": list(self.learning_signals),
            "created_after_exit": self.created_after_exit,
            "current_run_closed": self.current_run_closed,
            "created_at": self.created_at,
            "deterministic_digest": self.deterministic_digest,
            "schema_version": self.schema_version,
        }


def build_runtime_exhaust_bundle(
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
    route_contract_ref: str = "",
    sealed_result_ref: str = "",
    gate_mesh_result_ref: str = "",
    exit_disposition_ref: str,
    runtime_receipt_refs: tuple[str, ...] = (),
    learning_profile_ref: str = "",
    meta_feedback_profile_ref: str = "",
    learning_signals: tuple[str, ...] = (),
) -> RuntimeExhaustBundle:
    """Factory — creates a RuntimeExhaustBundle after Exit has completed.

    Caller is responsible for ensuring Exit has emitted before calling this.
    The ``exit_disposition_ref`` is required and must be non-empty, proving
    Exit ran.
    """
    if not exit_disposition_ref:
        raise ValueError(
            "build_runtime_exhaust_bundle: exit_disposition_ref is required. "
            "Must be the deterministic_digest of the ExitDispositionReceipt."
        )

    import uuid
    bundle_id = f"reb::{run_id}::{uuid.uuid4().hex[:8]}"
    created_at = _utcnow()

    core: dict = {
        "bundle_id": bundle_id,
        "request_id": request_id,
        "run_id": run_id,
        "trace_root": trace_root,
        "route_contract_ref": route_contract_ref,
        "sealed_result_ref": sealed_result_ref,
        "gate_mesh_result_ref": gate_mesh_result_ref,
        "exit_disposition_ref": exit_disposition_ref,
        "created_after_exit": True,
        "current_run_closed": True,
        "created_at": created_at,
    }
    digest = _digest(core)

    return RuntimeExhaustBundle(
        bundle_id=bundle_id,
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        route_contract_ref=route_contract_ref,
        sealed_result_ref=sealed_result_ref,
        gate_mesh_result_ref=gate_mesh_result_ref,
        exit_disposition_ref=exit_disposition_ref,
        runtime_receipt_refs=runtime_receipt_refs,
        learning_profile_ref=learning_profile_ref,
        meta_feedback_profile_ref=meta_feedback_profile_ref,
        learning_signals=learning_signals,
        created_after_exit=True,
        current_run_closed=True,
        created_at=created_at,
        deterministic_digest=digest,
    )


__all__ = [
    "RuntimeExhaustBundle",
    "build_runtime_exhaust_bundle",
]
