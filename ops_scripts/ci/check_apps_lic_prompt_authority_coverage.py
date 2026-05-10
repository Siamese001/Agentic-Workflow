"""
AG-9 apps_lic Prompt Authority Coverage CI Gate

Checks that apps_lic has complete prompt authority coverage per AG-9 plan.
Exit 0 only when all invariants pass.

Usage:
    python ops_scripts/ci/check_apps_lic_prompt_authority_coverage.py

Environment:
    PA_LIC_COV_BYPASS=1 — bypass gate (logged as WARNING)
    PA_LIC_COV_FAIL_CLOSED=1 — fail closed on any warning (default: advisory)
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Constants
ARTIFACTS_DIR = Path("artifacts/apps_lic")
INVENTORY_FILE = ARTIFACTS_DIR / "ag9_prompt_authority_inventory.json"
CLASSIFICATION_FILE = ARTIFACTS_DIR / "ag9_prompt_authority_classification.json"
MATRIX_FILE = ARTIFACTS_DIR / "ag9_prompt_stage_consumption_matrix.json"
NO_BYPASS_FILE = ARTIFACTS_DIR / "ag9_prompt_no_bypass_map.json"
REPORT_FILE = Path("artifacts/ci/apps_lic_prompt_authority_coverage.json")


class GateError:
    """Represents a gate error or warning"""
    def __init__(self, code: str, message: str, is_warning: bool = False):
        self.code = code
        self.message = message
        self.is_warning = is_warning

    def __str__(self):
        level = "WARN" if self.is_warning else "ERROR"
        return f"{level}: {self.code} — {self.message}"


class PromptAuthorityGate:
    """CI gate for apps_lic prompt authority coverage"""

    def __init__(self):
        self.errors: List[GateError] = []
        self.warnings: List[GateError] = []

    def add_error(self, code: str, message: str):
        self.errors.append(GateError(code, message, is_warning=False))

    def add_warning(self, code: str, message: str):
        self.warnings.append(GateError(code, message, is_warning=True))

    def load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file with error handling"""
        if not path.exists():
            self.add_error("MISSING_FILE", f"Required artifact not found: {path}")
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.add_error("INVALID_JSON", f"Invalid JSON in {path}: {e}")
            return {}
        except Exception as e:
            self.add_error("READ_ERROR", f"Error reading {path}: {e}")
            return {}

    def check_inventory(self, data: Dict[str, Any]):
        """Check prompt authority inventory"""
        if not data:
            return

        total = data.get("inventory_metadata", {}).get("total_surfaces", 0)
        if total != 116:
            self.add_error("INVENTORY_COUNT", f"Expected 116 surfaces, found {total}")

        surfaces = data.get("surfaces", [])
        if len(surfaces) != 116:
            self.add_error("INVENTORY_LIST_COUNT", f"Expected 116 surfaces in list, found {len(surfaces)}")

        # Check required fields
        for surface in surfaces:
            required_fields = ["prompt_id", "source_file", "surface_type", "content_ref_or_digest"]
            for field in required_fields:
                if field not in surface:
                    self.add_warning("MISSING_FIELD", f"Surface {surface.get('prompt_id', '?')} missing {field}")

    def check_classification(self, data: Dict[str, Any]):
        """Check prompt authority classification"""
        if not data:
            return

        total = data.get("classification_metadata", {}).get("total_classified", 0)
        if total != 116:
            self.add_error("CLASSIFICATION_COUNT", f"Expected 116 classified, found {total}")

        classifications = data.get("classifications", [])
        if len(classifications) != 116:
            self.add_error("CLASSIFICATION_LIST_COUNT", f"Expected 116 classifications, found {len(classifications)}")

        # Check for UNKNOWN_NEEDS_REVIEW
        unknowns = [c for c in classifications if c.get("authority_class") == "UNKNOWN_NEEDS_REVIEW"]
        if unknowns:
            self.add_error("UNKNOWN_REVIEW", f"{len(unknowns)} surfaces have UNKNOWN_NEEDS_REVIEW classification")

        # Check runtime prompts have required fields
        runtime = [c for c in classifications if c.get("runtime_reachable", False)]
        for c in runtime:
            if not c.get("authority_class"):
                self.add_warning("MISSING_AUTHORITY", f"Runtime prompt {c.get('prompt_id', '?')} missing authority_class")
            if not c.get("contract_field_target"):
                self.add_warning("MISSING_CONTRACT", f"Runtime prompt {c.get('prompt_id', '?')} missing contract_field_target")
            if not c.get("prompt_slot_target"):
                self.add_warning("MISSING_SLOT", f"Runtime prompt {c.get('prompt_id', '?')} missing prompt_slot_target")

    def check_matrix(self, data: Dict[str, Any]):
        """Check stage consumption matrix"""
        if not data:
            return

        total = data.get("matrix_metadata", {}).get("total_matrix_rows", 0)
        if total != 116:
            self.add_error("MATRIX_COUNT", f"Expected 116 matrix rows, found {total}")

        matrix = data.get("matrix", [])
        if len(matrix) != 116:
            self.add_error("MATRIX_LIST_COUNT", f"Expected 116 matrix entries, found {len(matrix)}")

        # Check PA is only generation assembly authority
        pa_slots = [m for m in matrix if m.get("PA") == "PROMPT_ASSEMBLY_SLOT"]

        # Verify no other stage has PROMPT_ASSEMBLY_SLOT
        for row in pa_slots:
            for stage in ["U0", "L1", "L0", "C0", "L2", "Exit"]:
                if row.get(stage) == "PROMPT_ASSEMBLY_SLOT":
                    self.add_error("MULTI_STAGE_PA", f"Row {row['prompt_id']} has PROMPT_ASSEMBLY_SLOT at {stage}")

        # Verify eval rubrics are EXIT_EVAL_ONLY
        eval_rubrics = [m for m in matrix if m["prompt_id"].startswith("EVAL-")]
        for row in eval_rubrics:
            if row.get("Exit") != "EXIT_EVAL_ONLY":
                self.add_error("EVAL_NOT_EXIT", f"Eval rubric {row['prompt_id']} should be EXIT_EVAL_ONLY")
            if row.get("PA") == "PROMPT_ASSEMBLY_SLOT":
                self.add_error("EVAL_IN_PA", f"Eval rubric {row['prompt_id']} should not be PROMPT_ASSEMBLY_SLOT")

    def check_no_bypass(self, data: Dict[str, Any]):
        """Check no-bypass map"""
        if not data:
            return

        laws = data.get("hard_laws", [])
        if len(laws) != 18:
            self.add_warning("LAW_COUNT", f"Expected 18 hard laws, found {len(laws)}")

        # Check for violations
        violations = [l for l in laws if l.get("violation_detected", False)]
        if violations:
            for v in violations:
                self.add_error("LAW_VIOLATION", f"Law {v['law_id']} violation: {v['description']}")

    def run(self) -> Tuple[int, List[GateError], List[GateError]]:
        """Run all checks and return (exit_code, errors, warnings)"""
        # Check bypass
        if os.environ.get("PA_LIC_COV_BYPASS") == "1":
            print("WARNING: PA_LIC_COV_BYPASS=1 — gate bypassed")
            return 0, [], []

        # Load artifacts
        inventory = self.load_json(INVENTORY_FILE)
        classification = self.load_json(CLASSIFICATION_FILE)
        matrix = self.load_json(MATRIX_FILE)
        no_bypass = self.load_json(NO_BYPASS_FILE)

        # Run checks
        self.check_inventory(inventory)
        self.check_classification(classification)
        self.check_matrix(matrix)
        self.check_no_bypass(no_bypass)

        # Determine exit code
        if self.errors:
            exit_code = 1
        elif self.warnings and os.environ.get("PA_LIC_COV_FAIL_CLOSED") == "1":
            exit_code = 1
        else:
            exit_code = 0

        return exit_code, self.errors, self.warnings

    def write_report(self, exit_code: int):
        """Write JSON report"""
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "gate_name": "PA-LIC-COV",
            "timestamp": "2026-05-10",
            "exit_code": exit_code,
            "status": "PASS" if exit_code == 0 else "FAIL",
            "errors": [{"code": e.code, "message": e.message} for e in self.errors],
            "warnings": [{"code": w.code, "message": w.message} for w in self.warnings],
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }

        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return report


def main():
    """Main entry point"""
    print("=" * 60)
    print("AG-9 apps_lic Prompt Authority Coverage CI Gate")
    print("=" * 60)

    gate = PromptAuthorityGate()
    exit_code, errors, warnings = gate.run()
    report = gate.write_report(exit_code)

    # Print results
    print()
    if errors:
        print(f"ERRORS: {len(errors)}")
        for e in errors:
            print(f"  {e}")

    if warnings:
        print(f"WARNINGS: {len(warnings)}")
        for w in warnings:
            print(f"  {w}")

    if not errors and not warnings:
        print("✅ All checks passed")

    print()
    print(f"Report: {REPORT_FILE}")
    print(f"Status: {report['status']} (exit_code={exit_code})")
    print("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
