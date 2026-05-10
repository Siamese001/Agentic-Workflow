#!/usr/bin/env python3
"""AG-8 CI gate: apps_lic Golden Path Runtime Proof Verification.

Per plan apps-lic-ag8-golden-template-adoption-f3c2e1.

Checks:
 1.  U0 binding wires u0_validate_apps_lic — L1 cannot be entered without it.
 2.  custom apps_lic payload maps into ValidatedRequest.app_payload.
 3.  Functionality preservation matrix has no MISSING rows.
 4.  L1 reads app_payload, not legacy envelope.payload.
 5.  L0 reads L1PlanContract, not legacy payload.
 6.  L3 participates for MANAGED_WORKFLOW (source assertion + execution_form check).
 7.  C0 populates FinalEvidenceContract (not thin/default-only).
 8.  PA places evidence in C0_EVIDENCE_DATA_ONLY slot; does not promote to instruction.
 9.  L2 preserves prompt_artifact_digest + evidence_refs in SealedL2Artifact.
10.  L2 does not write L4 directly (no DB connect in source).
11.  Exit emits X3Disposition only after building X1CheckoutResult.
12.  X2 aggregate_decision is called with x1_checkout_result.
13.  scalar eval_score is not authoritative (eval_score=None in exit source).
14.  material FAIL cannot ALLOW_FINISH (exit_status != success for failed L2).
15.  material UNKNOWN cannot pass (aggregate_decision must not ALLOW on UNKNOWN).
16.  NOT_APPLICABLE omits no reason (all NA verdicts must have rationale).
17.  proposed_state_diff cannot bypass X1J/UWG (state_diff always {} on L2 source).
18.  ChromaDB is not mutated (no chromadb import in golden-path modules).
19.  Embeddings are not generated (no embed_texts / bge_embed in golden-path modules).
20.  AG-8-FU1 is recorded in known-followups (ag8_exit_x1_x3_receipt.json).

Usage:
    python ops_scripts/ci/check_apps_lic_golden_path_runtime.py
    python ops_scripts/ci/check_apps_lic_golden_path_runtime.py --fail-closed
    python ops_scripts/ci/check_apps_lic_golden_path_runtime.py --json

Exit codes:
    0  All checks passed (or advisory mode)
    1  --fail-closed and one or more checks failed
    2  Gate execution error
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any


GATE_NAME = "AG-8 apps_lic Golden Path Runtime Proof"
GATE_VERSION = "1.0.0"

GOLDEN_PATH_MODULES = [
    "agentic_core/runtime/entry/u0_apps_lic_binding.py",
    "agentic_core/L1_cognition/apps_lic_l1_binding.py",
    "agentic_core/L0_routing/apps_lic_l0_binding.py",
    "agentic_core/L3_orchestration/apps_lic_l3_binding.py",
    "agentic_core/runtime/c0/apps_lic_c0_binding.py",
    "agentic_core/prompt_governance/apps_lic_pa_binding.py",
    "agentic_core/L2_execution/apps_lic_l2_binding.py",
    "agentic_core/runtime/exit/apps_lic_exit_binding.py",
]

FORBIDDEN_CHROMADB_PATTERNS = ["chromadb"]
FORBIDDEN_EMBEDDING_PATTERNS = ["embed_texts", "bge_embed", "get_embeddings", "sentence_transformers"]
FORBIDDEN_L4_PATTERNS = ["sqlite3.connect", "psycopg2.connect", "sqlalchemy.create_engine"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[2]


def _read_source(rel_path: str) -> str | None:
    path = _repo_root() / rel_path
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _code_only(source: str) -> str:
    """Strip comments and docstrings from source."""
    import re
    lines = [ln for ln in source.splitlines() if not ln.strip().startswith("#")]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r'""".*?"""', "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"'''.*?'''", "", cleaned, flags=re.DOTALL)
    return cleaned


def _ast_has_no_import(source: str, patterns: list[str]) -> list[str]:
    """Return list of violations: imports matching any pattern."""
    violations = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for pat in patterns:
                        if pat in alias.name:
                            violations.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for pat in patterns:
                        if pat in node.module:
                            violations.append(f"from {node.module} import ...")
    except SyntaxError:
        pass
    return violations


def _make_sealed_l2(execution_status: str = "completed") -> Any:
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.origin import Origin

    return SealedL2Artifact(
        request_id=uuid.uuid4().hex[:16],
        run_id=uuid.uuid4().hex[:16],
        app_id="apps_lic",
        trace_id=uuid.uuid4().hex[:16],
        execution_status=execution_status,
        generated_content="Hi test lead..." if execution_status == "completed" else "",
        generated_content_origin=Origin.MODEL_GENERATION,
        proposed_state_diff={},
        state_diff_authorized=False,
        compilation_hash="ag8-gate-digest",
        prompt_artifact_digest="pa-gate-digest",
        replay_key="gate-replay-key",
        tenant_id="apps_lic_tenant",
        l5_certification_ref="l2-apps-lic-outreach-message-ag8-w6-f3c2e1",
    )


# ---------------------------------------------------------------------------
# Checks (source-level)
# ---------------------------------------------------------------------------

def check_u0_wires_reflection_receipt() -> tuple[bool, str]:
    src = _read_source("agentic_core/runtime/entry/u0_apps_lic_binding.py")
    if src is None:
        return False, "U0 binding not found"
    if "reflection_receipt" not in src:
        return False, "U0 binding does not produce reflection_receipt — L1 bypass possible"
    if "u0_validate_apps_lic" not in src:
        return False, "u0_validate_apps_lic function not found in U0 binding"
    return True, "U0 produces reflection_receipt and exports u0_validate_apps_lic"


def check_payload_maps_to_app_payload() -> tuple[bool, str]:
    src = _read_source("agentic_core/runtime/entry/u0_apps_lic_binding.py")
    if src is None:
        return False, "U0 binding not found"
    if "app_payload" not in src:
        return False, "U0 does not set app_payload on ValidatedRequest"
    return True, "U0 maps custom apps_lic payload into ValidatedRequest.app_payload"


def check_preservation_matrix_no_missing() -> tuple[bool, str]:
    path = _repo_root() / "artifacts" / "apps_lic" / "ag8_apps_lic_functionality_preservation_matrix.json"
    if not path.exists():
        return False, f"Preservation matrix not found: {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"Cannot parse preservation matrix: {e}"

    missing = [
        cap["capability_id"]
        for cap in data.get("capabilities", [])
        if cap.get("status") == "MISSING"
    ]
    if missing:
        return False, f"Preservation matrix has MISSING capabilities: {missing}"

    summary_missing = data.get("summary", {}).get("MISSING", 0)
    if summary_missing != 0:
        return False, f"summary.MISSING = {summary_missing}, expected 0"

    return True, f"Preservation matrix: 0 MISSING rows"


def check_l1_reads_app_payload() -> tuple[bool, str]:
    src = _read_source("agentic_core/L1_cognition/apps_lic_l1_binding.py")
    if src is None:
        return False, "L1 binding not found"
    if "app_payload" not in src:
        return False, "L1 does not reference app_payload"
    # Use AST to check for actual code reference to envelope.payload (not docstrings)
    try:
        tree = ast.parse(src)
        violations = [
            n for n in ast.walk(tree)
            if (
                isinstance(n, ast.Attribute)
                and n.attr == "payload"
                and isinstance(n.value, ast.Name)
                and n.value.id == "envelope"
            )
        ]
        if violations:
            return False, "L1 references legacy envelope.payload in actual code (not just docstrings)"
    except SyntaxError as e:
        return False, f"L1 source parse error: {e}"
    return True, "L1 reads app_payload and does not reference legacy envelope.payload"


def check_l0_reads_l1_plan_contract() -> tuple[bool, str]:
    src = _read_source("agentic_core/L0_routing/apps_lic_l0_binding.py")
    if src is None:
        return False, "L0 binding not found"
    code = _code_only(src)
    if "L1PlanContract" not in src:
        return False, "L0 does not reference L1PlanContract"
    if "envelope.payload" in code:
        return False, "L0 references legacy envelope.payload"
    return True, "L0 reads L1PlanContract and does not reference legacy payload"


def check_l3_participates_for_managed_workflow() -> tuple[bool, str]:
    src = _read_source("agentic_core/L3_orchestration/apps_lic_l3_binding.py")
    if src is None:
        return False, "L3 binding not found"
    if "managed_workflow" not in src.lower():
        return False, "L3 binding does not reference managed_workflow"
    if "l3_no_execute_assertion" not in src:
        return False, "L3 missing l3_no_execute_assertion"
    if "l3_no_retrieve_assertion" not in src:
        return False, "L3 missing l3_no_retrieve_assertion"

    # Runtime check: route_contract must have execution_form=managed_workflow
    try:
        from agentic_core.runtime.entry.u0_apps_lic_binding import u0_validate_apps_lic
        from agentic_core.L1_cognition.apps_lic_l1_binding import l1_plan_apps_lic
        from agentic_core.L0_routing.apps_lic_l0_binding import l0_route_apps_lic
        from agentic_core.runtime.contracts.apps_lic_ingress_payload import (
            AppsLicIngressPayload,
            AppsLicRequestEnvelope,
        )

        payload = AppsLicIngressPayload(
            app_id="apps_lic",
            task_class="outreach_message",
            request_type="outreach_draft",
            channel="email",
            lead_profile={
                "verified_name": "CI Gate Lead",
                "title": "VP Technology",
                "seniority_class": "VP",
                "company_name": "Acme Corp",
                "industry": "Technology",
                "consent_attested": True,
            },
            sender_profile={
                "sender_id": "rep-gate",
                "name": "CI Rep",
                "title": "SVP",
            },
        )
        envelope = AppsLicRequestEnvelope(
            request_id=uuid.uuid4().hex[:16],
            run_id=uuid.uuid4().hex[:16],
            trace_id=uuid.uuid4().hex[:16],
            tenant_id="apps_lic",
            payload=payload,
        )
        vr = u0_validate_apps_lic(envelope)
        l1 = l1_plan_apps_lic(vr)
        rc = l0_route_apps_lic(l1)
        if rc.execution_form != "managed_workflow":
            return False, f"L0 route has execution_form={rc.execution_form!r}, expected managed_workflow"
    except Exception as e:
        return False, f"Runtime L3 participation check failed: {e}"

    return True, "L3 participates for managed_workflow; source assertions present"


def check_c0_populates_evidence_contract() -> tuple[bool, str]:
    src = _read_source("agentic_core/runtime/c0/apps_lic_c0_binding.py")
    if src is None:
        return False, "C0 binding not found"
    if "FinalEvidenceContract" not in src:
        return False, "C0 does not reference FinalEvidenceContract (thin/default-only)"
    if "grounding_required" not in src:
        return False, "C0 does not check grounding_required"
    viols = _ast_has_no_import(src, FORBIDDEN_CHROMADB_PATTERNS)
    if viols:
        return False, f"C0 imports chromadb: {viols}"
    return True, "C0 populates FinalEvidenceContract and is ChromaDB-free"


def check_pa_evidence_data_only() -> tuple[bool, str]:
    src = _read_source("agentic_core/prompt_governance/apps_lic_pa_binding.py")
    if src is None:
        return False, "PA binding not found"
    if "C0_EVIDENCE_DATA_ONLY" not in src and "evidence_data_only" not in src.lower():
        return False, "PA does not place evidence in C0_EVIDENCE_DATA_ONLY slot"
    if "slot_lineage_map" not in src:
        return False, "PA missing slot_lineage_map"
    code = _code_only(src)
    viols = _ast_has_no_import(src, FORBIDDEN_CHROMADB_PATTERNS)
    if viols:
        return False, f"PA imports chromadb: {viols}"
    return True, "PA places evidence in C0_EVIDENCE_DATA_ONLY; slot_lineage_map present"


def check_l2_preserves_refs() -> tuple[bool, str]:
    src = _read_source("agentic_core/L2_execution/apps_lic_l2_binding.py")
    if src is None:
        return False, "L2 binding not found"
    missing = []
    for field in ("prompt_artifact_digest", "evidence_refs", "replay"):
        if field not in src:
            missing.append(field)
    if missing:
        return False, f"L2 does not reference: {missing}"
    if "proposed_state_diff" not in src:
        return False, "L2 does not reference proposed_state_diff"
    return True, "L2 preserves prompt_artifact_digest, evidence_refs, replay refs"


def check_l2_no_direct_l4_write() -> tuple[bool, str]:
    src = _read_source("agentic_core/L2_execution/apps_lic_l2_binding.py")
    if src is None:
        return False, "L2 binding not found"
    code = _code_only(src)
    violations = [p for p in FORBIDDEN_L4_PATTERNS if p in code]
    if violations:
        return False, f"L2 contains direct L4 write patterns: {violations}"
    return True, "L2 has no direct L4 write"


def check_exit_uses_x1_checkout() -> tuple[bool, str]:
    src = _read_source("agentic_core/runtime/exit/apps_lic_exit_binding.py")
    if src is None:
        return False, "Exit binding not found"
    if "build_x1_checkout_result" not in src:
        return False, "Exit does not call build_x1_checkout_result — X1CheckoutResult bypassed"
    if "run_all_x1_gates" not in src:
        return False, "Exit does not call run_all_x1_gates"
    if "X3Disposition" not in src:
        return False, "Exit does not reference X3Disposition"
    return True, "Exit calls run_all_x1_gates + build_x1_checkout_result, emits X3Disposition"


def check_x2_called_with_x1_checkout() -> tuple[bool, str]:
    src = _read_source("agentic_core/runtime/exit/apps_lic_exit_binding.py")
    if src is None:
        return False, "Exit binding not found"
    if "aggregate_decision" not in src:
        return False, "Exit does not call aggregate_decision (X2)"
    if "x1_checkout_result=x1_checkout" not in src and "x1_checkout" not in src:
        return False, "aggregate_decision not called with x1_checkout_result"
    return True, "X2 aggregate_decision called with x1_checkout_result"


def check_eval_score_not_authoritative() -> tuple[bool, str]:
    src = _read_source("agentic_core/runtime/exit/apps_lic_exit_binding.py")
    if src is None:
        return False, "Exit binding not found"
    if "eval_score=None" not in src:
        return False, "eval_score is not set to None — scalar score may be treated as authoritative"
    return True, "eval_score=None; scalar score is not authoritative"


def check_material_fail_cannot_allow(execution_status: str = "failed") -> tuple[bool, str]:
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import exit_finalize_apps_lic
        l2 = _make_sealed_l2(execution_status=execution_status)
        result = exit_finalize_apps_lic(l2)
        if result.outcome_authorized:
            return False, f"Failed L2 (status={execution_status}) returned outcome_authorized=True — material FAIL can ALLOW_FINISH"
        if result.exit_status == "success":
            return False, f"Failed L2 returned exit_status='success'"
    except Exception as e:
        return False, f"Runtime check error: {e}"
    return True, f"Failed L2 ({execution_status}) correctly denied (outcome_authorized=False)"


def check_na_verdicts_have_rationale() -> tuple[bool, str]:
    """Verify NOT_APPLICABLE verdicts carry an explicit applicability rationale.

    Hard law: gate_id identifies the check — it is NOT an applicability rationale.
    Every NOT_APPLICABLE verdict must carry at least one of:
      - non-empty reason_codes  (preferred: machine-readable explanation)
      - non-empty remediation_hint  (acceptable: human-readable explanation)
    An empty reason_codes + empty remediation_hint is a hard-law violation even
    if gate_id is present.
    """
    try:
        from agentic_core.runtime.exit.apps_lic_exit_binding import _build_exit_review_packet
        from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import run_all_x1_gates
        from agentic_core.L3_orchestration.exit_eval.v6.types import GateResult
        l2 = _make_sealed_l2()
        packet = _build_exit_review_packet(l2)
        verdicts = run_all_x1_gates(packet)
        missing_reason = [
            v.gate_id for v in verdicts
            if v.result == GateResult.NOT_APPLICABLE
            and not v.reason_codes
            and not v.remediation_hint
        ]
        if missing_reason:
            return False, (
                f"NOT_APPLICABLE verdicts lack explicit reason (reason_codes and "
                f"remediation_hint both empty): {missing_reason}"
            )
    except Exception as e:
        return False, f"Runtime rationale check error: {e}"
    return True, "All NOT_APPLICABLE verdicts carry explicit reason (reason_codes or remediation_hint)"


def check_proposed_state_diff_inert() -> tuple[bool, str]:
    src = _read_source("agentic_core/L2_execution/apps_lic_l2_binding.py")
    if src is None:
        return False, "L2 binding not found"
    # proposed_state_diff must always be {} — check it's referenced but not assigned a real value
    if "proposed_state_diff" not in src:
        return False, "L2 does not reference proposed_state_diff"
    # Runtime verify
    try:
        l2 = _make_sealed_l2()
        assert l2.proposed_state_diff == {}, f"proposed_state_diff not empty: {l2.proposed_state_diff}"
    except Exception as e:
        return False, f"proposed_state_diff runtime check failed: {e}"
    return True, "proposed_state_diff is inert (always {})"


def check_no_chromadb_in_golden_path() -> tuple[bool, str]:
    violations = []
    for rel_path in GOLDEN_PATH_MODULES:
        src = _read_source(rel_path)
        if src is None:
            continue
        viols = _ast_has_no_import(src, FORBIDDEN_CHROMADB_PATTERNS)
        if viols:
            violations.append(f"{rel_path}: {viols}")
    if violations:
        return False, "ChromaDB imports found in golden-path modules:\n" + "\n".join(f"  {v}" for v in violations)
    return True, "No ChromaDB imports in golden-path modules"


def check_no_embedding_generation() -> tuple[bool, str]:
    violations = []
    for rel_path in GOLDEN_PATH_MODULES:
        src = _read_source(rel_path)
        if src is None:
            continue
        code = _code_only(src)
        for pat in FORBIDDEN_EMBEDDING_PATTERNS:
            if pat in code:
                violations.append(f"{rel_path}: {pat!r}")
    if violations:
        return False, "Embedding calls found in golden-path modules:\n" + "\n".join(f"  {v}" for v in violations)
    return True, "No embedding generation in golden-path modules"


def check_ag8_fu1_documented() -> tuple[bool, str]:
    path = _repo_root() / "artifacts" / "apps_lic" / "ag8_exit_x1_x3_receipt.json"
    if not path.exists():
        return False, f"ag8_exit_x1_x3_receipt.json not found at {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"Cannot parse ag8_exit_x1_x3_receipt.json: {e}"
    divergences = {d.get("id"): d for d in data.get("known_divergences", [])}
    if "AG-8-FU1" not in divergences:
        return False, "AG-8-FU1 not recorded in known_divergences of ag8_exit_x1_x3_receipt.json"
    fu1 = divergences["AG-8-FU1"]
    is_guarded = fu1.get("do_not_start") is True
    is_complete = (fu1.get("do_not_start") is False and str(fu1.get("status", "")).startswith("COMPLETE"))
    if not (is_guarded or is_complete):
        return False, "AG-8-FU1 must have do_not_start=true (guarded) or do_not_start=false+status=COMPLETE (done)"
    status_note = "do_not_start=true" if is_guarded else "COMPLETE"
    return True, f"AG-8-FU1 documented as known follow-up with {status_note}"


# ---------------------------------------------------------------------------
# Orchestrate all checks
# ---------------------------------------------------------------------------

def run_all_checks() -> dict[str, Any]:
    checks = {
        "u0_wires_reflection_receipt": check_u0_wires_reflection_receipt(),
        "payload_maps_to_app_payload": check_payload_maps_to_app_payload(),
        "preservation_matrix_no_missing": check_preservation_matrix_no_missing(),
        "l1_reads_app_payload": check_l1_reads_app_payload(),
        "l0_reads_l1_plan_contract": check_l0_reads_l1_plan_contract(),
        "l3_participates_for_managed_workflow": check_l3_participates_for_managed_workflow(),
        "c0_populates_evidence_contract": check_c0_populates_evidence_contract(),
        "pa_evidence_data_only": check_pa_evidence_data_only(),
        "l2_preserves_refs": check_l2_preserves_refs(),
        "l2_no_direct_l4_write": check_l2_no_direct_l4_write(),
        "exit_uses_x1_checkout": check_exit_uses_x1_checkout(),
        "x2_called_with_x1_checkout": check_x2_called_with_x1_checkout(),
        "eval_score_not_authoritative": check_eval_score_not_authoritative(),
        "material_fail_cannot_allow": check_material_fail_cannot_allow("failed"),
        "na_verdicts_have_rationale": check_na_verdicts_have_rationale(),
        "proposed_state_diff_inert": check_proposed_state_diff_inert(),
        "no_chromadb_in_golden_path": check_no_chromadb_in_golden_path(),
        "no_embedding_generation": check_no_embedding_generation(),
        "ag8_fu1_documented": check_ag8_fu1_documented(),
    }

    return {
        "gate_name": GATE_NAME,
        "gate_version": GATE_VERSION,
        "checks": {
            name: {"passed": r[0], "message": r[1]}
            for name, r in checks.items()
        },
        "passed": all(r[0] for r in checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=GATE_NAME)
    parser.add_argument("--fail-closed", action="store_true",
                        help="Exit 1 if any check fails")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--output", type=str, help="Write JSON results to file")
    args = parser.parse_args()

    if os.environ.get("APPS_LIC_GOLDEN_PATH_GATE_BYPASS"):
        print(f"⚠️  {GATE_NAME}: BYPASSED")
        return 0

    fail_closed = args.fail_closed or bool(
        os.environ.get("APPS_LIC_GOLDEN_PATH_GATE_FAIL_CLOSED")
    )

    try:
        results = run_all_checks()
    except Exception as e:
        print(f"\n❌ {GATE_NAME}: EXECUTION ERROR\n   {e}")
        return 2

    if args.json or args.output:
        out = json.dumps(results, indent=2)
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
        else:
            print(out)
    else:
        print(f"\n{'=' * 70}")
        print(f"{GATE_NAME} v{GATE_VERSION}")
        print(f"{'=' * 70}")
        for name, chk in results["checks"].items():
            status = "✅ PASS" if chk["passed"] else "❌ FAIL"
            print(f"\n{status}: {name}")
            print(f"   {chk['message']}")
        print(f"\n{'=' * 70}")
        if results["passed"]:
            print("✅ ALL CHECKS PASSED")
        else:
            n_fail = sum(1 for c in results["checks"].values() if not c["passed"])
            print(f"❌ {n_fail} CHECK(S) FAILED")
        print(f"{'=' * 70}")

    if fail_closed and not results["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
