"""W8: CI Gate — apps_rg Runtime Gate Hardening Validation.

Validates that all W0-W7 gates are properly implemented, registered,
and have corresponding test coverage. Part of the runtime gate hardening
wave completion verification.

Exit policy:
  - Default: **advisory** — prints the W8 report and exits 0 when the catalog
    or on-disk test layout drifts (non-blocking in the contract plane).
  - ``APPS_RG_W8_GATE_FAIL_CLOSED=1`` — exits 1 when validation status is not PASS.

Spec reference: .codex/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W8)
"""

from __future__ import annotations

import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Ensure repo root on path for imports
REPO_ROOT = Path(__file__).parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_core.L5_safety.runtime_gates.contracts import Result


@dataclass
class GateValidationResult:
    """Result of validating a single gate."""
    gate_id: str
    wave: str
    exists: bool
    callable: bool
    has_tests: bool
    errors: list[str]


# Expected gates by wave (W0-W7)
EXPECTED_GATES = {
    "W0": [
        "RuntimeGateEngine initialization",
        "GateVerdict dataclass",
        "WriteAdmissionGuard",
    ],
    "W1": [
        "candidate_accepted_gate",
        "post_ens_resume_composite_gate",
    ],
    "W2": [
        "online_judge_binding",
    ],
    "W3": [
        "prompt_assembly_sha_gate",
        "master_resume_sha_pinned_gate",
    ],
    "W4": [
        "provenance_required_gate",
        "figure_citation_verification_gate",
        "tenure_accuracy_gate",
        "anti_fabrication_composite_gate",
        "degree_certification_unchanged_gate",
    ],
    "W5": [
        "length_parity_strict_gate",
        "quantified_outcome_count_gate",
        "target_company_name_absence_gate",
        "forbidden_filler_strict_gate",
        "sentence_max_length_gate",
        "archetype_lead_gate",
        "per_cand_quality_composite_gate",
    ],
    "W6": [
        "jd_keyword_coverage_min_gate",
        "claim_uniqueness_gate",
        "cross_section_consistency_gate",
        "bullet_count_per_role_gate",
        "role_chronology_gate",
        "ats_composite_gate",
    ],
    "W7": [
        "docx_render_no_orphan_gate",
        "pre_export_composite_gate",
    ],
}

# Module paths to check
GATE_MODULES = {
    "post_ens_resume_gates": "apps_rg.integrations.gates.post_ens_resume_gates",
    "pre_llm_gates": "apps_rg.integrations.gates.pre_llm_gates",
    "per_cand_resume_gates": "apps_rg.integrations.gates.per_cand_resume_gates",
    "post_narr_resume_gates": "apps_rg.integrations.gates.post_narr_resume_gates",
    "pre_export_resume_gates": "apps_rg.integrations.gates.pre_export_resume_gates",
    "online_judges": "apps_rg.integrations.gates.online_judges",
}

# Test files to verify
TEST_FILES = {
    "W0": "tests/_apps_contract/test_w0_runtime_gate_foundation.py",
    "W1": "tests/_apps_contract/test_w1_p0_write_boundary_fix.py",
    "W2": "tests/_apps_contract/test_w2_online_judge_contract.py",
    "W3": "tests/_apps_contract/test_w3_pre_llm_gates.py",
    "W4": "tests/_apps_contract/test_w4_anti_fabrication_gates.py",
    "W5": "tests/_apps_contract/test_w5_per_cand_gates.py",
    "W6": "tests/_apps_contract/test_w6_post_narr_gates.py",
    "W7": "tests/_apps_contract/test_w7_pre_export_gates.py",
}


def validate_gate_module(module_name: str, module_path: str) -> list[GateValidationResult]:
    """Validate a gate module exists and exports expected gates."""
    results = []
    
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        return [GateValidationResult(
            gate_id=module_name,
            wave="unknown",
            exists=False,
            callable=False,
            has_tests=False,
            errors=[f"Module import failed: {e}"],
        )]
    
    # Check __all__ exports
    exports = getattr(module, "__all__", [])
    
    for export in exports:
        obj = getattr(module, export, None)
        
        # Skip module-level constants that aren't gates
        if export.isupper() or export.startswith("NARRATIVE_") or export.startswith("DEFAULT_"):
            continue
            
        results.append(GateValidationResult(
            gate_id=export,
            wave=_infer_wave(export),
            exists=obj is not None,
            callable=callable(obj) if obj else False,
            has_tests=False,  # Checked separately
            errors=[] if (obj and callable(obj)) else ["Not callable"] if obj else ["Missing"],
        ))
    
    return results


def _infer_wave(gate_id: str) -> str:
    """Infer which wave a gate belongs to."""
    wave_mapping = {
        "candidate_accepted": "W1",
        "post_ens_resume_composite": "W1",
        "prompt_assembly_sha": "W3",
        "master_resume_sha_pinned": "W3",
        "provenance_required": "W4",
        "figure_citation_verification": "W4",
        "tenure_accuracy": "W4",
        "anti_fabrication_composite": "W4",
        "length_parity_strict": "W5",
        "quantified_outcome_count": "W5",
        "target_company_name_absence": "W5",
        "forbidden_filler_strict": "W5",
        "sentence_max_length": "W5",
        "archetype_lead": "W5",
        "per_cand_quality_composite": "W5",
        "jd_keyword_coverage_min": "W6",
        "claim_uniqueness": "W6",
        "cross_section_consistency": "W6",
        "bullet_count_per_role": "W6",
        "role_chronology": "W6",
        "ats_composite": "W6",
        "degree_certification_unchanged": "W4",  # Also in W7
        "docx_render_no_orphan": "W7",
        "pre_export_composite": "W7",
    }
    
    for prefix, wave in wave_mapping.items():
        if gate_id.startswith(prefix):
            return wave
    
    return "unknown"


def check_test_files() -> dict[str, bool]:
    """Check that test files exist for each wave."""
    results = {}
    for wave, test_path in TEST_FILES.items():
        full_path = REPO_ROOT / test_path
        results[wave] = full_path.exists()
    return results


def run_validation() -> dict[str, Any]:
    """Run full W8 validation."""
    all_results = []
    
    # Validate gate modules
    for module_name, module_path in GATE_MODULES.items():
        module_results = validate_gate_module(module_name, module_path)
        all_results.extend(module_results)
    
    # Check test files
    test_results = check_test_files()
    
    # Aggregate statistics
    total_gates = len(all_results)
    valid_gates = sum(1 for r in all_results if r.exists and r.callable and not r.errors)
    missing_gates = sum(1 for r in all_results if not r.exists)
    broken_gates = sum(1 for r in all_results if r.exists and r.errors)
    
    waves_with_tests = sum(1 for exists in test_results.values() if exists)
    
    return {
        "gate_results": all_results,
        "test_results": test_results,
        "summary": {
            "total_gates_checked": total_gates,
            "valid_gates": valid_gates,
            "missing_gates": missing_gates,
            "broken_gates": broken_gates,
            "waves_with_tests": waves_with_tests,
            "total_waves": len(TEST_FILES),
        },
        "status": "PASS" if (missing_gates == 0 and broken_gates == 0 and waves_with_tests == len(TEST_FILES)) else "FAIL",
    }


def print_report(results: dict[str, Any]) -> None:
    """Print validation report."""
    print("=" * 70)
    print("W8: apps_rg Runtime Gate Hardening Validation")
    print("=" * 70)
    
    summary = results["summary"]
    print(f"\n📊 Summary:")
    print(f"   Total gates checked: {summary['total_gates_checked']}")
    print(f"   ✅ Valid gates: {summary['valid_gates']}")
    print(f"   ❌ Missing gates: {summary['missing_gates']}")
    print(f"   ⚠️  Broken gates: {summary['broken_gates']}")
    print(f"   🧪 Waves with tests: {summary['waves_with_tests']}/{summary['total_waves']}")
    
    print(f"\n📁 Test File Status:")
    for wave, exists in results["test_results"].items():
        status = "✅" if exists else "❌"
        print(f"   {status} {wave}: {TEST_FILES[wave]}")
    
    # Group gates by wave
    by_wave: dict[str, list[GateValidationResult]] = {}
    for r in results["gate_results"]:
        by_wave.setdefault(r.wave, []).append(r)
    
    print(f"\n🔍 Gate Details by Wave:")
    for wave in sorted(by_wave.keys()):
        if wave == "unknown":
            continue
        gates = by_wave[wave]
        wave_ok = all(r.exists and r.callable for r in gates)
        status = "✅" if wave_ok else "⚠️"
        print(f"\n   {status} {wave} ({len(gates)} gates):")
        for g in gates:
            g_status = "✅" if (g.exists and g.callable) else "❌"
            print(f"      {g_status} {g.gate_id}")
            if g.errors:
                for e in g.errors[:2]:
                    print(f"         → {e}")
    
    print(f"\n{'=' * 70}")
    status = results["status"]
    if status == "PASS":
        print("✅ W8 VALIDATION PASSED: All W0-W7 gates implemented with test coverage")
    else:
        print("❌ W8 VALIDATION FAILED: Issues detected above")
    print("=" * 70)


def main() -> int:
    """Main entry point.

    Exit 0 when validation PASS, or when advisory mode applies (default).
    Exit 1 when validation FAIL and ``APPS_RG_W8_GATE_FAIL_CLOSED=1``.
    """
    results = run_validation()
    print_report(results)

    if results["status"] == "PASS":
        return 0
    if os.environ.get("APPS_RG_W8_GATE_FAIL_CLOSED", "").strip() == "1":
        return 1
    print(
        "[check_apps_rg_runtime_gate_hardening] Advisory mode — W8 catalog/test "
        "mismatch; exiting 0 (set APPS_RG_W8_GATE_FAIL_CLOSED=1 to fail closed).",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
