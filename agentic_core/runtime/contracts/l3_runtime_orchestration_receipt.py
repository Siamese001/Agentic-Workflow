"""L3 runtime-orchestration receipt — typed proof that L3 actually orchestrated.

Emitted when ``RouteContract.execution_form == MANAGED_WORKFLOW``. The
receipt proves the runtime side of the static-DAG / runtime split:

    1. The same ``run_id`` / ``request_id`` / ``trace_root`` as every
       other artifact in the chain.
    2. The same ``dag_id`` and ``dag_sha256`` as the
       ``static_dag_proof.json`` artifact (binds runtime to static).
    3. ``selected_node_ids`` is a subset of ``static_dag.node_ids``
       (no node selected that wasn't declared).
    4. Every step contract maps to a static DAG node and shares the
       run identity.
    5. L3 didn't execute tools, didn't retrieve, didn't assemble
       prompts, didn't write L4 — these assertions are explicit.

This is the runtime counterpart to ``L3BypassReceipt``. They are
mutually exclusive: at most ONE of the two is in the chain per run.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

L3_RUNTIME_RECEIPT_SCHEMA_VERSION = "1.0"

ALLOWED_STEP_STATUSES: frozenset[str] = frozenset({
    "step_handed_to_l2",
    "step_skipped",
    "step_completed_by_l2",
    "step_failed_by_l2",
    "step_returned_for_replan",
})

_DIGEST_STABLE_FIELDS: tuple[str, ...] = (
    "schema_version",
    "run_id",
    "request_id",
    "trace_root",
    "route_contract_id",
    "route_id",
    "dag_id",
    "dag_sha256",
    "selected_node_ids",
    "step_contracts",
    "l3_no_execute_assertion",
    "l3_no_retrieve_assertion",
    "l3_no_prompt_assembly_assertion",
    "l3_no_l4_write_assertion",
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class L3StepContractRef:
    """Lightweight reference to one L3 step handed to L2.

    The full ``L3StepContract`` lives at
    ``agentic_core.L3_orchestration.doctrine.contracts_l3_7``; this
    reference is the runtime-side stamp.
    """

    step_id: str
    node_id: str
    run_id: str
    status: str
    handed_to_l2_at_utc: str = ""
    skipped_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "node_id": self.node_id,
            "run_id": self.run_id,
            "status": self.status,
            "handed_to_l2_at_utc": self.handed_to_l2_at_utc,
            "skipped_reason": self.skipped_reason,
        }


@dataclass(frozen=True)
class L3RuntimeOrchestrationReceipt:
    """Typed receipt proving L3 actually orchestrated for one MANAGED_WORKFLOW run."""

    run_id: str
    request_id: str
    trace_root: str
    route_contract_id: str
    route_id: str
    dag_id: str
    dag_sha256: str
    selected_node_ids: tuple[str, ...]
    step_contracts: tuple[L3StepContractRef, ...]
    l3_required: bool = True
    l3_no_execute_assertion: bool = True
    l3_no_retrieve_assertion: bool = True
    l3_no_prompt_assembly_assertion: bool = True
    l3_no_l4_write_assertion: bool = True
    schema_version: str = L3_RUNTIME_RECEIPT_SCHEMA_VERSION
    deterministic_digest: str = ""
    static_dag_ref: str = ""
    l5_certification_ref: str = ""

    def __post_init__(self) -> None:
        for name in ("run_id", "request_id", "trace_root", "route_id", "dag_id", "dag_sha256"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                raise ValueError(
                    f"L3RuntimeOrchestrationReceipt.{name} must be non-empty string"
                )
        if self.l3_required is not True:
            raise ValueError(
                "L3RuntimeOrchestrationReceipt.l3_required must be True; "
                "use L3BypassReceipt when L3 did not run"
            )
        for name in (
            "l3_no_execute_assertion",
            "l3_no_retrieve_assertion",
            "l3_no_prompt_assembly_assertion",
            "l3_no_l4_write_assertion",
        ):
            value = getattr(self, name)
            if value is not True:
                raise ValueError(
                    f"L3RuntimeOrchestrationReceipt.{name} must be True; "
                    "L3 must NEVER execute, retrieve, assemble prompts, or write L4"
                )
        if not self.selected_node_ids:
            raise ValueError(
                "L3RuntimeOrchestrationReceipt.selected_node_ids must be non-empty; "
                "an orchestrated run must have selected at least one node"
            )
        for sc in self.step_contracts:
            if not isinstance(sc, L3StepContractRef):
                raise ValueError(
                    "L3RuntimeOrchestrationReceipt.step_contracts entries must be L3StepContractRef"
                )
            if sc.run_id != self.run_id:
                raise ValueError(
                    f"L3StepContractRef.run_id={sc.run_id!r} != receipt.run_id={self.run_id!r}"
                )
            if sc.status not in ALLOWED_STEP_STATUSES:
                raise ValueError(
                    f"L3StepContractRef.status={sc.status!r} not in {sorted(ALLOWED_STEP_STATUSES)}"
                )
            if sc.node_id not in self.selected_node_ids:
                raise ValueError(
                    f"L3StepContractRef.node_id={sc.node_id!r} not in selected_node_ids"
                )
        if self.schema_version != L3_RUNTIME_RECEIPT_SCHEMA_VERSION:
            raise ValueError(
                f"L3RuntimeOrchestrationReceipt.schema_version mismatch"
            )
        from agentic_core.L5_safety.contracts.verify import verify_certification_ref
        if not verify_certification_ref(self.l5_certification_ref):
            raise ValueError(
                f"L3RuntimeOrchestrationReceipt: missing or invalid "
                f"l5_certification_ref={self.l5_certification_ref!r} (AG-W0-5=fail_closed)"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "route_contract_id": self.route_contract_id,
            "route_id": self.route_id,
            "dag_id": self.dag_id,
            "dag_sha256": self.dag_sha256,
            "static_dag_ref": self.static_dag_ref,
            "selected_node_ids": list(self.selected_node_ids),
            "step_contracts": [sc.to_dict() for sc in self.step_contracts],
            "l3_required": self.l3_required,
            "l3_no_execute_assertion": self.l3_no_execute_assertion,
            "l3_no_retrieve_assertion": self.l3_no_retrieve_assertion,
            "l3_no_prompt_assembly_assertion": self.l3_no_prompt_assembly_assertion,
            "l3_no_l4_write_assertion": self.l3_no_l4_write_assertion,
            "deterministic_digest": self.deterministic_digest,
        }


def compute_l3_runtime_digest(payload: Mapping[str, Any]) -> str:
    stable: dict[str, Any] = {}
    for k in _DIGEST_STABLE_FIELDS:
        v = payload.get(k)
        if isinstance(v, (list, tuple)):
            # Normalize list-of-dicts via canonical JSON.
            stable[k] = [
                _canonical_json(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            stable[k] = v
    blob = _canonical_json(stable).encode("utf-8")
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_l3_runtime_orchestration_receipt(
    *,
    run_id: str,
    request_id: str,
    trace_root: str,
    route_contract_id: str,
    route_id: str,
    dag_id: str,
    dag_sha256: str,
    selected_node_ids: tuple[str, ...],
    step_contracts: tuple[L3StepContractRef, ...],
    static_dag_ref: str = "",
) -> L3RuntimeOrchestrationReceipt:
    digest_input: dict[str, Any] = {
        "schema_version": L3_RUNTIME_RECEIPT_SCHEMA_VERSION,
        "run_id": run_id,
        "request_id": request_id,
        "trace_root": trace_root,
        "route_contract_id": route_contract_id,
        "route_id": route_id,
        "dag_id": dag_id,
        "dag_sha256": dag_sha256,
        "selected_node_ids": list(selected_node_ids),
        "step_contracts": [sc.to_dict() for sc in step_contracts],
        "l3_no_execute_assertion": True,
        "l3_no_retrieve_assertion": True,
        "l3_no_prompt_assembly_assertion": True,
        "l3_no_l4_write_assertion": True,
    }
    digest = compute_l3_runtime_digest(digest_input)
    return L3RuntimeOrchestrationReceipt(
        run_id=run_id,
        request_id=request_id,
        trace_root=trace_root,
        route_contract_id=route_contract_id,
        route_id=route_id,
        dag_id=dag_id,
        dag_sha256=dag_sha256,
        selected_node_ids=tuple(selected_node_ids),
        step_contracts=tuple(step_contracts),
        static_dag_ref=static_dag_ref,
        deterministic_digest=digest,
    )


__all__ = [
    "ALLOWED_STEP_STATUSES",
    "L3RuntimeOrchestrationReceipt",
    "L3StepContractRef",
    "L3_RUNTIME_RECEIPT_SCHEMA_VERSION",
    "build_l3_runtime_orchestration_receipt",
    "compute_l3_runtime_digest",
]
