"""L7 Runtime Audit Contracts — AG-RGGOV-W7 Audit Evidence

Canonical dataclasses for L7 runtime auditability.
L7 is audit evidence only — no planning, routing, execution, or state mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional
from enum import Enum


class AuditStatus(str, Enum):
    """L7 audit record status."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    PENDING = "pending"


@dataclass(frozen=True, slots=True)
class StageOwnerEntry:
    """Single stage ownership entry in the stage owner map."""

    stage_id: str  # e.g., "l1", "l0", "c0", "pa", "l2", "exit"
    stage_name: str  # e.g., "L1 Cognition", "C0 Evidence"
    owner_component: str  # e.g., "agentic_core", "apps_rg"
    owner_module: str  # e.g., "agentic_core.L1_cognition.l1_plan_contract"
    contract_emitted: str  # e.g., "L1PlanContract"
    ownership_verdict: AuditStatus


@dataclass(frozen=True, slots=True)
class ContractDigestEntry:
    """Single contract digest in the chain."""

    stage_id: str
    contract_name: str
    contract_digest: str  # sha256 hash
    parent_digest: str  # Previous contract in chain
    timestamp: str
    status: AuditStatus


@dataclass(frozen=True, slots=True)
class NoShadowPipelineReceipt:
    """Receipt proving no shadow pipeline exists."""

    apps_rg_runtime_authority: bool  # Must be False
    apps_rg_contract_emission_detected: bool  # Must be False
    apps_rg_provider_calls_detected: bool  # Must be False
    shadow_pipeline_verdict: AuditStatus  # Must be PASS
    verification_timestamp: str
    verification_method: str  # e.g., "static_analysis", "runtime_instrumentation"


@dataclass(frozen=True, slots=True)
class ProviderEgressOwnershipProof:
    """Proof that provider egress is owned by SovereignLLMGateway."""

    egress_owner_component: str  # Must be "agentic_core"
    egress_owner_module: str  # e.g., "agentic_core.L2_execution.SovereignLLMGateway"
    apps_rg_egress_detected: bool  # Must be False
    egress_ownership_verdict: AuditStatus  # Must be PASS
    verification_timestamp: str


@dataclass(frozen=True, slots=True)
class StageOwnerMapProof:
    """Proof that all runtime stages are owned by agentic_core."""

    stage_entries: tuple[StageOwnerEntry, ...]
    apps_rg_stages_count: int  # Must be 0
    agentic_core_stages_count: int  # Should be > 0
    stage_ownership_verdict: AuditStatus  # Must be PASS
    verification_timestamp: str


@dataclass(frozen=True, slots=True)
class ContractDigestChainReceipt:
    """Receipt proving contract digest chain is sealed."""

    digest_entries: tuple[ContractDigestEntry, ...]
    chain_head_digest: str
    chain_tail_digest: str
    chain_complete: bool  # Must be True
    chain_sealed: bool  # Must be True
    chain_verdict: AuditStatus  # Must be PASS
    verification_timestamp: str


@dataclass(frozen=True, slots=True)
class L7SuccessRecord:
    """Single L7 success record."""

    record_id: str  # e.g., "l7.apps_rg.ingress_payload.validated"
    record_type: str  # e.g., "ingress_validation", "contract_emission", "ownership_confirmation"
    component: str  # e.g., "apps_rg", "agentic_core", "provider_egress"
    stage: Optional[str]  # e.g., "l1", "l0", "exit"
    status: AuditStatus
    timestamp: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class L7RuntimeAuditTrace:
    """L7 Runtime Audit Trace — complete audit record for a request.

    Contains all evidence required to prove:
    - No shadow pipeline exists
    - All runtime stages owned by agentic_core
    - Provider egress owned by SovereignLLMGateway
    - Contract digest chain is sealed
    """

    # Identity
    trace_id: str
    request_id: str
    run_id: str
    app_id: str

    # Core audit evidence
    success_records: tuple[L7SuccessRecord, ...]
    no_shadow_pipeline_receipt: NoShadowPipelineReceipt
    stage_owner_map_proof: StageOwnerMapProof
    provider_egress_ownership_proof: ProviderEgressOwnershipProof
    contract_digest_chain_receipt: ContractDigestChainReceipt

    # Summary
    overall_audit_verdict: AuditStatus
    audit_timestamp: str
    audit_version: str = "W7.0"
