#!/usr/bin/env python3
"""CI gate: verify every emit-contract dataclass carries l5_certification_ref.

Gate ID: L5CR1
Plan: l5-cert-ref-emit-chain-threading-c4e7f1 W4 / P4.2

Performs a static AST scan over the 11 canonical emit-contract dataclasses
specified in the plan §7.  For each class it checks that a field named
``l5_certification_ref`` exists with a default of ``""`` (singular, per the
AG-W0-1 decision).

Advisory by default; fail-closed via env var ``L5_CERT_REF_GATE_FAIL_CLOSED=1``.
Bypass: ``L5_CERT_REF_GATE_BYPASS=1`` (logs a warning, exits 0).
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Canonical emit-contract targets (file, class_name)
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]

EMIT_CONTRACTS: list[tuple[str, str]] = [
    # U0
    ("agentic_core/runtime/contracts/apps_rg_ingress_payload.py", "ValidatedRequest"),
    # L1
    ("agentic_core/prompt_governance/prompt_assembly/input_contracts.py", "L1PlanContract"),
    # L0
    ("agentic_core/runtime/contracts/route_contract.py", "RouteContract"),
    ("agentic_core/prompt_governance/prompt_assembly/input_contracts.py", "L0RouteContract"),
    # C0
    ("agentic_core/runtime/contracts/final_evidence_contract.py", "FinalEvidenceContract"),
    # PA
    ("agentic_core/runtime/contracts/compiled_prompt_artifact.py", "CompiledPromptArtifact"),
    # L3
    ("agentic_core/L3_orchestration/doctrine/contracts_l3_7.py", "L3StepContract"),
    # L2
    ("agentic_core/runtime/contracts/sealed_l2_artifact.py", "SealedL2Artifact"),
    # Exit X3 packets
    ("agentic_core/L3_orchestration/exit_eval/v6/types.py", "X3DenyPacket"),
    ("agentic_core/L3_orchestration/exit_eval/v6/types.py", "X3EscalatePacket"),
    ("agentic_core/L3_orchestration/exit_eval/v6/types.py", "X3CommitRequestPacket"),
    ("agentic_core/L3_orchestration/exit_eval/v6/types.py", "X3AllowPacket"),
    ("agentic_core/L3_orchestration/exit_eval/v6/types.py", "X3SafeAbstainPacket"),
    ("agentic_core/L3_orchestration/exit_eval/v6/types.py", "X3BreakGlassAllowPacket"),
    # UWG
    ("agentic_core/L4_state/contracts/records.py", "CommitRequest"),
    ("agentic_core/L4_state/contracts/records.py", "UWGCommitReceipt"),
    # L6
    ("agentic_core/L6_observability/runtime_trace/runtime_exhaust_bundle.py", "RuntimeExhaustBundle"),
    ("agentic_core/L6_observability/shadow_eval/contracts.py", "RuntimeExhaustBundle"),
]

FIELD_NAME = "l5_certification_ref"


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _extract_dataclass_field_names(tree: ast.AST, class_name: str) -> set[str] | None:
    """Return the set of field names for *class_name* in *tree*, or None if not found."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue
        fields: set[str] = set()
        for item in node.body:
            # @dataclass fields appear as annotated assignments at the class level
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                fields.add(item.target.id)
        return fields
    return None


def _check_file(rel_path: str, class_name: str) -> str | None:
    """Return an error string if *class_name* in *rel_path* is missing the field, else None."""
    full = REPO_ROOT / rel_path
    if not full.is_file():
        return f"MISSING_FILE  {rel_path} :: {class_name}"
    try:
        tree = ast.parse(full.read_text(encoding="utf-8"), filename=rel_path)
    except SyntaxError as exc:
        return f"SYNTAX_ERROR  {rel_path} :: {exc}"

    fields = _extract_dataclass_field_names(tree, class_name)
    if fields is None:
        return f"CLASS_NOT_FOUND  {rel_path} :: {class_name}"
    if FIELD_NAME not in fields:
        return f"FIELD_MISSING  {rel_path} :: {class_name}  (no '{FIELD_NAME}' annotated field)"
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    if os.getenv("L5_CERT_REF_GATE_BYPASS") == "1":
        print(f"WARNING: L5CR1 bypassed via L5_CERT_REF_GATE_BYPASS=1")
        return 0

    fail_closed = os.getenv("L5_CERT_REF_GATE_FAIL_CLOSED") == "1"

    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    for rel_path, class_name in EMIT_CONTRACTS:
        key = (rel_path, class_name)
        if key in seen:
            continue
        seen.add(key)
        err = _check_file(rel_path, class_name)
        if err:
            errors.append(err)

    total = len(seen)
    passed = total - len(errors)
    print(f"[L5CR1] emit-contract l5_certification_ref field scan: {passed}/{total} OK")

    if errors:
        print(f"[L5CR1] {len(errors)} VIOLATION(S):")
        for e in errors:
            print(f"  ERROR  {e}")
        if fail_closed:
            print("[L5CR1] fail-closed mode active — exiting 1")
            return 1
        print("[L5CR1] advisory mode — exiting 0 (set L5_CERT_REF_GATE_FAIL_CLOSED=1 to enforce)")
        return 0

    print("[L5CR1] all emit-contract fields present — gate GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
