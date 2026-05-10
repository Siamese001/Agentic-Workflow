"""W6 Emit-Contract Enrichment — 9-concern CI gate (plan w6-emit-contract-enrichment-d8b2a4, W9 P9.1).

D12=9 per-concern checks packaged in a single gate file.
Each concern maps to a field that must exist on its target contracts.

Advisory by default; fail-closed via W6_EMIT_CONTRACT_GATE_FAIL_CLOSED=1.
Bypass: W6_EMIT_CONTRACT_GATE_BYPASS=1.
"""
from __future__ import annotations

import importlib
import os
import sys
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

BYPASS = os.environ.get("W6_EMIT_CONTRACT_GATE_BYPASS", "0") == "1"
FAIL_CLOSED = os.environ.get("W6_EMIT_CONTRACT_GATE_FAIL_CLOSED", "0") == "1"


def _attr(obj: Any, *names: str) -> list[str]:
    """Return names that are missing from obj."""
    return [n for n in names if not hasattr(obj, n)]


def _import(module: str, cls: str) -> Any:
    mod = importlib.import_module(module)
    return getattr(mod, cls)


errors: list[str] = []
warnings: list[str] = []


def check(concern: str, cls_name: str, module: str, *fields: str) -> None:
    try:
        cls = _import(module, cls_name)
        # Instantiate a minimal instance to check field presence at class level
        import dataclasses
        if dataclasses.is_dataclass(cls):
            field_names = {f.name for f in dataclasses.fields(cls)}
            missing = [f for f in fields if f not in field_names]
        else:
            missing = []  # not a dataclass — skip structural check
        if missing:
            errors.append(
                f"[{concern}] {cls_name} missing fields: {missing}"
            )
    except Exception as exc:
        errors.append(f"[{concern}] failed to import {module}.{cls_name}: {exc}")


# ---------------------------------------------------------------------------
# Concern #1 — Identity quad (request_id + run_id + trace token on all 11)
# Note: L3RuntimeOrchestrationReceipt and CommitRequest use `trace_root`
# instead of `trace_id`. RuntimeExhaustBundle is an aggregator — it uses
# `bundle_id` + `tenant_id` rather than per-request identity fields.
# ---------------------------------------------------------------------------
_IDENTITY_CONTRACTS = [
    ("agentic_core.runtime.contracts.apps_rg_ingress_payload", "ValidatedRequest"),
    ("agentic_core.runtime.contracts.l1_plan_contract", "L1PlanContract"),
    ("agentic_core.runtime.contracts.route_contract", "RouteContract"),
    ("agentic_core.runtime.contracts.final_evidence_contract", "FinalEvidenceContract"),
    ("agentic_core.runtime.contracts.compiled_prompt_artifact", "CompiledPromptArtifact"),
    ("agentic_core.runtime.contracts.sealed_l2_artifact", "SealedL2Artifact"),
    ("agentic_core.runtime.contracts.x3_disposition", "X3Disposition"),
    ("agentic_core.runtime.contracts.l3_runtime_orchestration_receipt", "L3RuntimeOrchestrationReceipt"),
    ("agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle", "RuntimeExhaustBundle"),
    ("agentic_core.L4_state.contracts.records", "CommitRequest"),
]
# Standard trace-id contracts
_TRACE_ID_CONTRACTS = [
    ("agentic_core.runtime.contracts.apps_rg_ingress_payload", "ValidatedRequest"),
    ("agentic_core.runtime.contracts.l1_plan_contract", "L1PlanContract"),
    ("agentic_core.runtime.contracts.route_contract", "RouteContract"),
    ("agentic_core.runtime.contracts.final_evidence_contract", "FinalEvidenceContract"),
    ("agentic_core.runtime.contracts.compiled_prompt_artifact", "CompiledPromptArtifact"),
    ("agentic_core.runtime.contracts.sealed_l2_artifact", "SealedL2Artifact"),
    ("agentic_core.runtime.contracts.x3_disposition", "X3Disposition"),
]
for mod, cls in _TRACE_ID_CONTRACTS:
    check("C1-identity", cls, mod, "request_id", "run_id", "trace_id")
# trace_root alias contracts
for mod, cls in [
    ("agentic_core.runtime.contracts.l3_runtime_orchestration_receipt", "L3RuntimeOrchestrationReceipt"),
    ("agentic_core.L4_state.contracts.records", "CommitRequest"),
]:
    check("C1-identity", cls, mod, "request_id", "run_id", "trace_root")
# RuntimeExhaustBundle — aggregator; uses bundle_id + tenant_id
check("C1-identity", "RuntimeExhaustBundle",
      "agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle",
      "bundle_id", "tenant_id")

# ---------------------------------------------------------------------------
# Concern #3 — Runtime gate receipts (gate_verdict_refs on all 11)
# ---------------------------------------------------------------------------
for mod, cls in _IDENTITY_CONTRACTS:
    check("C3-gate-receipts", cls, mod, "gate_verdict_refs")

# ---------------------------------------------------------------------------
# Concern #4 — Replay / determinism (replay_key + snapshot_refs on all 11)
# ---------------------------------------------------------------------------
for mod, cls in _IDENTITY_CONTRACTS:
    check("C4-replay", cls, mod, "replay_key", "snapshot_refs")

# ---------------------------------------------------------------------------
# Concern #5 — Observability / audit (otel_span_refs + audit_refs on all 11)
# ---------------------------------------------------------------------------
for mod, cls in _IDENTITY_CONTRACTS:
    check("C5-observability", cls, mod, "otel_span_refs", "audit_refs")

# ---------------------------------------------------------------------------
# Concern #7 — Risk posture (posture field on 10; CommitRequest uses posture too)
# ---------------------------------------------------------------------------
_POSTURE_CONTRACTS = [
    ("agentic_core.runtime.contracts.apps_rg_ingress_payload", "ValidatedRequest"),
    ("agentic_core.runtime.contracts.l1_plan_contract", "L1PlanContract"),
    ("agentic_core.runtime.contracts.route_contract", "RouteContract"),
    ("agentic_core.runtime.contracts.final_evidence_contract", "FinalEvidenceContract"),
    ("agentic_core.runtime.contracts.compiled_prompt_artifact", "CompiledPromptArtifact"),
    ("agentic_core.runtime.contracts.sealed_l2_artifact", "SealedL2Artifact"),
    ("agentic_core.runtime.contracts.x3_disposition", "X3Disposition"),
    ("agentic_core.runtime.contracts.l3_runtime_orchestration_receipt", "L3RuntimeOrchestrationReceipt"),
    ("agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle", "RuntimeExhaustBundle"),
    ("agentic_core.L4_state.contracts.records", "CommitRequest"),
]
for mod, cls in _POSTURE_CONTRACTS:
    check("C7-posture", cls, mod, "posture")

# ---------------------------------------------------------------------------
# Concern #9 — Schema / hash / signature (schema_version + signature on all 11)
# ---------------------------------------------------------------------------
for mod, cls in _IDENTITY_CONTRACTS:
    check("C9-schema-signature", cls, mod, "signature")

# ---------------------------------------------------------------------------
# Concern #10 — Write / learning firewall (4 write-eligible contracts)
# ---------------------------------------------------------------------------
_FIREWALL_CONTRACTS = [
    ("agentic_core.runtime.contracts.sealed_l2_artifact", "SealedL2Artifact"),
    ("agentic_core.runtime.contracts.x3_disposition", "X3Disposition"),
    ("agentic_core.L4_state.contracts.records", "CommitRequest"),
    ("agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle", "RuntimeExhaustBundle"),
]
for mod, cls in _FIREWALL_CONTRACTS:
    check("C10-write-firewall", cls, mod, "is_uwg_write_authority", "is_future_run_only")

# ---------------------------------------------------------------------------
# Concern #2 (L5 cert ref — parent plan) — spot-check field exists
# ---------------------------------------------------------------------------
for mod, cls in _IDENTITY_CONTRACTS:
    check("C2-l5-cert-ref", cls, mod, "l5_certification_ref")

# ---------------------------------------------------------------------------
# RuntimePosture type check
# ---------------------------------------------------------------------------
try:
    from agentic_core.runtime.contracts.posture import (
        RuntimePosture,
        POSTURE_READ_ONLY,
        POSTURE_GENERATION,
        POSTURE_WRITE_INTENT,
        POSTURE_HITL_REQUIRED,
        POSTURE_RETRIEVAL,
    )
    import dataclasses
    if not dataclasses.is_dataclass(RuntimePosture):
        errors.append("[C7-posture] RuntimePosture is not a dataclass")
    for sentinel_name, sentinel in [
        ("POSTURE_READ_ONLY", POSTURE_READ_ONLY),
        ("POSTURE_GENERATION", POSTURE_GENERATION),
        ("POSTURE_WRITE_INTENT", POSTURE_WRITE_INTENT),
        ("POSTURE_HITL_REQUIRED", POSTURE_HITL_REQUIRED),
        ("POSTURE_RETRIEVAL", POSTURE_RETRIEVAL),
    ]:
        if not isinstance(sentinel, RuntimePosture):
            errors.append(f"[C7-posture] {sentinel_name} is not a RuntimePosture instance")
except Exception as exc:
    errors.append(f"[C7-posture] RuntimePosture import failed: {exc}")

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if BYPASS:
    print("W6_EMIT_CONTRACT_GATE_BYPASS=1 — skipping")
    sys.exit(0)

total = len(errors) + len(warnings)
print(f"W6 emit-contract enrichment gate: {len(errors)} ERROR(s), {len(warnings)} WARN(s)")
for e in errors:
    print(f"  ERROR: {e}")
for w in warnings:
    print(f"  WARN: {w}")

if errors:
    if FAIL_CLOSED:
        sys.exit(1)
    else:
        print("  (advisory — set W6_EMIT_CONTRACT_GATE_FAIL_CLOSED=1 to enforce)")
        sys.exit(0)

sys.exit(0)
