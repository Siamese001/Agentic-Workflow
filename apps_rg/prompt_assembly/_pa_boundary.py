"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT emit lifecycle trace contracts or make provider calls.

Original: apps_rg/prompt_assembly\_pa_boundary.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — Runtime authority violation

Importing this module raises RuntimeError immediately.
Core L6 Observability owns all trace emission. apps_rg is ingress-only.
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.prompt_assembly\_pa_boundary is QUARANTINED. "
    "apps_rg may NOT contain runtime authority. "
    "Core L2/L5/L6 owns execution. apps_rg is ingress-only. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)

# Original code archived to: archives/apps_rg/quarantine_w4_20260509/prompt_assembly\_pa_boundary.py.ORIGINAL

# QUARANTINED — Original content below for reference only — NOT EXECUTABLE:
# """PA boundary helper — receipt generation and mixin guard for apps_rg.
# 
# Small, typed, deterministic utilities for:
#   1. PA boundary receipts (all emit/bridge sites)
#   2. Worker-side mixin guard (ensures mixins consumed only post-PA)
# 
# See PROMPT_BOUNDARY_CONTRACT.md for the authoritative slot/airlock/receipt contract.
# """
# 
# from __future__ import annotations
# 
# import hashlib
# import json
# import uuid
# from dataclasses import asdict, dataclass, field
# from enum import Enum, auto
# from typing import Any, Optional
# 
# 
# class PABoundaryStatus(str, Enum):
#     """Decision status for PA boundary crossing."""
# 
#     PA_BOM_RESOLVED = "PA_BOM_RESOLVED"
#     PA_SLOTS_COMPOSED = "PA_SLOTS_COMPOSED"
#     PA_SECURITY_PASS = "PA_SECURITY_PASS"
#     PA_SECURITY_GAP = "PA_SECURITY_GAP"
#     PA_RENDERED = "PA_RENDERED"
#     PA_L2_HANDOFF_READY = "PA_L2_HANDOFF_READY"
#     PA_COMPILE_FAILED = "PA_COMPILE_FAILED"
#     PA_BOUNDARY_ERROR = "PA_BOUNDARY_ERROR"
#     NOT_BOUND = "NOT_BOUND"  # legacy path: field unavailable
# 
# 
# @dataclass(frozen=True)
# class PABoundaryReceipt:
#     """Receipt emitted at every PA boundary crossing.
# 
#     Common header fields per PROMPT_BOUNDARY_CONTRACT.md §5.
#     If a field is unavailable in the legacy path, it is recorded as
#     NOT_BOUND with explicit reason code.
#     """
# 
#     # Identity
#     receipt_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
#     receipt_type: str = "prompt_boundary_receipt"
# 
#     # Header (required where available)
#     request_id: str = ""
#     run_id: str = ""
#     trace_id: str = ""
#     route_id: str = ""
# 
#     # Content hashes (prompt_hash or compiled_artifact_hash must be present)
#     policy_hash: str = ""
#     blueprint_hash: str = ""
#     prompt_hash: str = ""  # NOT_BOUND if legacy path lacks it
#     compiled_artifact_hash: str = ""  # NOT_BOUND if legacy path lacks it
#     bom_hash: str = ""
#     registry_hash: str = ""
#     template_hash: str = ""
# 
#     # Source / lineage refs
#     source_refs: dict[str, str] = field(default_factory=dict)
#     lineage_refs: dict[str, str] = field(default_factory=dict)
# 
#     # Decision status (UNKNOWN is never PASS)
#     status: str = field(default=PABoundaryStatus.PA_BOM_RESOLVED.value)
#     reason_codes: list[str] = field(default_factory=list)
# 
#     # Deterministic digest of this receipt itself
#     deterministic_digest: str = ""
# 
#     # Legacy path metadata (when NOT_BOUND fields exist)
#     unavailable_fields: list[str] = field(default_factory=list)
# 
#     def __post_init__(self) -> None:
#         # Compute deterministic digest over frozen fields.
#         # Note: receipt_id and receipt_type are excluded from digest computation
#         # because they are metadata about the receipt itself, not attested content.
#         canonical = json.dumps(
#             {
#                 "request_id": self.request_id,
#                 "run_id": self.run_id,
#                 "trace_id": self.trace_id,
#                 "route_id": self.route_id,
#                 "policy_hash": self.policy_hash,
#                 "blueprint_hash": self.blueprint_hash,
#                 "prompt_hash": self.prompt_hash,
#                 "compiled_artifact_hash": self.compiled_artifact_hash,
#                 "bom_hash": self.bom_hash,
#                 "registry_hash": self.registry_hash,
#                 "template_hash": self.template_hash,
#                 "source_refs": self.source_refs,
#                 "lineage_refs": self.lineage_refs,
#                 "status": self.status,
#                 "reason_codes": self.reason_codes,
#                 "unavailable_fields": self.unavailable_fields,
#             },
#             sort_keys=True,
#             ensure_ascii=True,
#         )
#         object.__setattr__(
#             self,
#             "deterministic_digest",
#             hashlib.sha256(canonical.encode()).hexdigest()[:16],
#         )
# 
#     def to_dict(self) -> dict[str, Any]:
#         """Serialize to JSON-safe dict."""
#         return asdict(self)
# 
# 
# class MixinGuardError(RuntimeError):
#     """Raised when worker-side mixin guard fails."""
# 
# 
# @dataclass(frozen=True)
# class MixinGuardEvidence:
#     """Evidence required for mixin consumption."""
# 
#     # PA must have compiled before mixin can fire
#     compiled_artifact_hash: str = ""
#     pa_boundary_receipt_digest: str = ""
# 
#     # Route must be established (cannot create new authority)
#     route_id: str = ""
#     route_contract_hash: str = ""
# 
#     # If these are missing, mixin cannot fire
#     def is_valid(self) -> bool:
#         return bool(
#             self.compiled_artifact_hash
#             and self.pa_boundary_receipt_digest
#             and self.route_id
#         )
# 
# 
# @dataclass(frozen=True)
# class MixinGuardResult:
#     """Result of mixin guard check."""
# 
#     allowed: bool
#     reason: str = ""
#     reason_code: str = ""
# 
# 
# def make_pa_boundary_receipt(
#     *,
#     request_id: str = "",
#     run_id: str = "",
#     trace_id: str = "",
#     route_id: str = "",
#     policy_hash: str = "",
#     blueprint_hash: str = "",
#     prompt_hash: str = "",
#     compiled_artifact_hash: str = "",
#     bom_hash: str = "",
#     registry_hash: str = "",
#     template_hash: str = "",
#     source_refs: Optional[dict[str, str]] = None,
#     lineage_refs: Optional[dict[str, str]] = None,
#     status: PABoundaryStatus = PABoundaryStatus.PA_BOM_RESOLVED,
#     reason_codes: Optional[list[str]] = None,
#     unavailable_fields: Optional[list[str]] = None,
# ) -> PABoundaryReceipt:
#     """Factory for PA boundary receipts.
# 
#     Every PA emit/bridge site calls this to produce a receipt.
#     Legacy paths explicitly mark unavailable fields as NOT_BOUND.
#     """
#     return PABoundaryReceipt(
#         request_id=request_id or "NOT_BOUND",
#         run_id=run_id or "NOT_BOUND",
#         trace_id=trace_id or "NOT_BOUND",
#         route_id=route_id or "NOT_BOUND",
#         policy_hash=policy_hash or "NOT_BOUND",
#         blueprint_hash=blueprint_hash or "NOT_BOUND",
#         prompt_hash=prompt_hash or "NOT_BOUND",
#         compiled_artifact_hash=compiled_artifact_hash or "NOT_BOUND",
#         bom_hash=bom_hash or "NOT_BOUND",
#         registry_hash=registry_hash or "NOT_BOUND",
#         template_hash=template_hash or "NOT_BOUND",
#         source_refs=source_refs or {},
#         lineage_refs=lineage_refs or {},
#         status=status.value,
#         reason_codes=reason_codes or [],
#         unavailable_fields=unavailable_fields or [],
#     )
# 
# 
# def check_mixin_guard(
#     evidence: MixinGuardEvidence,
#     *,
#     mixin_id: str = "",
#     require_pa_boundary: bool = True,
#     allow_create_authority: bool = False,  # always False for governed paths
# ) -> MixinGuardResult:
#     """Worker-side mixin guard.
# 
#     Invariants (PROMPT_BOUNDARY_CONTRACT.md §4):
#       1. Mixins cannot fire pre-PA (evidence must show PA compiled).
#       2. Mixins cannot create new authority (allow_create_authority=False).
#       3. Mixins cannot bypass PA (evidence must contain PA receipt digest).
#       4. Mixins cannot override route, policy, schema, provider, model, tool,
#          capability, sandbox, or evidence scope (route_contract_hash must match).
# 
#     Args:
#         evidence: MixinGuardEvidence with PA boundary proof.
#         mixin_id: Identifier for logging/diagnostics.
#         require_pa_boundary: If True (default), mixin fails when evidence invalid.
#         allow_create_authority: Must be False for governed paths.
# 
#     Returns:
#         MixinGuardResult with allowed=True only when all invariants satisfied.
# 
#     Raises:
#         MixinGuardError: When guard fails and require_pa_boundary is strict.
#     """
#     failures: list[str] = []
# 
#     # Invariant 1: PA boundary must exist (mixin cannot fire pre-PA)
#     if not evidence.compiled_artifact_hash:
#         failures.append("MISSING_COMPILED_ARTIFACT_HASH: mixin cannot fire pre-PA")
#     if not evidence.pa_boundary_receipt_digest:
#         failures.append("MISSING_PA_BOUNDARY_RECEIPT: mixin bypass detected")
# 
#     # Invariant 2: Mixins cannot create authority
#     if allow_create_authority:
#         failures.append("AUTHORITY_CREATION_BLOCKED: mixins cannot create authority")
# 
#     # Invariant 3: Route must be established (cannot widen scope)
#     if not evidence.route_id:
#         failures.append("MISSING_ROUTE_ID: mixin cannot fire without established route")
# 
#     if failures:
#         reason = "; ".join(failures)
#         return MixinGuardResult(
#             allowed=False,
#             reason=reason,
#             reason_code="MIXIN_GUARD_VIOLATION",
#         )
# 
#     return MixinGuardResult(
#         allowed=True,
#         reason=f"Mixin {mixin_id} passes guard with route_id={evidence.route_id}",
#         reason_code="MIXIN_GUARD_PASS",
#     )
# 
# 
# def strict_mixin_guard(
#     evidence: MixinGuardEvidence,
#     *,
#     mixin_id: str = "",
# ) -> None:
#     """Strict variant that raises MixinGuardError on failure.
# 
#     Use in production code paths where silent failure is unsafe.
#     """
#     result = check_mixin_guard(evidence, mixin_id=mixin_id, require_pa_boundary=True)
#     if not result.allowed:
#         raise MixinGuardError(
#             f"MixinGuardError [{result.reason_code}]: {result.reason}"
#         )
# 
# 
# __all__ = [
#     "PABoundaryStatus",
#     "PABoundaryReceipt",
#     "MixinGuardError",
#     "MixinGuardEvidence",
#     "MixinGuardResult",
#     "make_pa_boundary_receipt",
#     "check_mixin_guard",
#     "strict_mixin_guard",
# ]
# 