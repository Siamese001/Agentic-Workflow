"""
Phase F: Guardian Self-Integrity Tests.

Tests the Guardian-of-Guardians (run_guardian_contract_integrity.py).
Verifies:
1. Real guardian scripts pass integrity check
2. Synthetic non-compliant script is caught
3. AST-based checks are accurate
4. Schema compliance of integrity result
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import ast

from agentic_core.L0_routing.scripts.run_guardian_contract_integrity import (
    _check_imports_contract,
    _check_imports_normalize,
    _check_no_raw_json_dumps,
    _check_returns_guardian_result,
    run_contract_integrity_guardian,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
    check_schema_compatibility,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Fixtures: synthetic scripts
# ---------------------------------------------------------------------------

COMPLIANT_SCRIPT = '''
"""Compliant guardian."""
from agentic_core.L0_routing.types.guardian_contract_types import (
    GuardianResult,
    normalize_repo_path,
)

def run_guardian_example(repo_root=None) -> GuardianResult:
    return GuardianResult(guardian_id="example")
'''

NON_COMPLIANT_SCRIPT = '''
"""Non-compliant guardian — raw dict emission."""
import json

def run_guardian_bad(repo_root=None) -> dict:
    return {"status": "PASS"}
'''


# ---------------------------------------------------------------------------
# 1. AST check unit tests
# ---------------------------------------------------------------------------


class TestASTChecks:
    def test_compliant_imports_contract(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        assert _check_imports_contract(tree) is True

    def test_non_compliant_missing_contract(self):
        tree = ast.parse(NON_COMPLIANT_SCRIPT)
        assert _check_imports_contract(tree) is False

    def test_compliant_imports_normalize(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        assert _check_imports_normalize(tree) is True

    def test_non_compliant_missing_normalize(self):
        tree = ast.parse(NON_COMPLIANT_SCRIPT)
        assert _check_imports_normalize(tree) is False

    def test_compliant_returns_guardian_result(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        assert _check_returns_guardian_result(tree) is True

    def test_non_compliant_returns_dict(self):
        tree = ast.parse(NON_COMPLIANT_SCRIPT)
        assert _check_returns_guardian_result(tree) is False

    def test_raw_json_dumps_detected(self):
        script_with_dumps = """
import json
def bad():
    return json.dumps({"key": "val"})
"""
        tree = ast.parse(script_with_dumps)
        lines = _check_no_raw_json_dumps(tree)
        assert len(lines) > 0

    def test_no_raw_json_dumps_in_compliant(self):
        tree = ast.parse(COMPLIANT_SCRIPT)
        lines = _check_no_raw_json_dumps(tree)
        assert lines == []


# ---------------------------------------------------------------------------
# 2. Real repo integrity check
# ---------------------------------------------------------------------------


class TestRealRepoIntegrity:
    def test_real_guardians_pass(self):
        """All real guardian scripts must pass the integrity checker."""
        result = run_contract_integrity_guardian()
        failed_checks = [c for c in result.checks if c.status == CheckStatus.FAIL.value]
        assert not failed_checks, (
            f"Real guardian scripts have integrity violations: "
            f"{[c.check_id + ': ' + c.details for c in failed_checks]}"
        )

    def test_real_result_is_pass(self):
        result = run_contract_integrity_guardian()
        assert result.status == GuardianStatus.PASS.value, (
            f"Integrity guardian status: {result.status}, summary: {result.summary}"
        )

    def test_scripts_found(self):
        result = run_contract_integrity_guardian()
        assert result.metrics["scripts_checked"] >= 2, (
            "Should find at least 2 guardian scripts (hygiene + manifest)"
        )


# ---------------------------------------------------------------------------
# 3. Synthetic non-compliant script detected
# ---------------------------------------------------------------------------


class TestSyntheticViolation:
    def test_non_compliant_detected(self, tmp_path: Path):
        """A synthetic non-compliant script should be caught."""
        # Create a fake repo with a non-compliant guardian script
        scripts_dir = tmp_path / "agentic_core" / "L0_routing" / "scripts"
        scripts_dir.mkdir(parents=True)
        bad_script = scripts_dir / "run_guardian_fake.py"
        bad_script.write_text(NON_COMPLIANT_SCRIPT, encoding="utf-8")

        result = run_contract_integrity_guardian(repo_root=tmp_path)
        assert result.status == GuardianStatus.FAIL.value
        assert result.metrics["violations_found"] > 0


# ---------------------------------------------------------------------------
# 4. Schema compliance of integrity result
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths(self):
        result = run_contract_integrity_guardian()
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths: {violations}"

    def test_schema_compatible(self):
        result = run_contract_integrity_guardian()
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"Schema drift: {errors}"

    def test_guardian_id_stable(self):
        result = run_contract_integrity_guardian()
        assert result.guardian_id == "contract_integrity"
