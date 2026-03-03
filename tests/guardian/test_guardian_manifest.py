"""
Guardian Manifest Integrity Tests — ReAct-Style (Observe → Verify → Report).

Tests the run_guardian_manifest script against sandboxed tmp_repo fixtures.
Verifies:
1. Missing manifest.json → SKIP (not applicable)
2. Missing .manifest.lock → FAIL
3. Matching checksums → PASS
4. Mismatched checksums → FAIL with evidence
5. JSON output conforms to guardian_contract schema
6. Deterministic: same input → same JSON output
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_manifest import (
    run_manifest_guardian,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repo_no_manifest(tmp_path: Path) -> Path:
    """Repo with no manifest.json at all."""
    return tmp_path


@pytest.fixture
def repo_no_lock(tmp_path: Path) -> Path:
    """Repo with manifest.json but no .manifest.lock."""
    (tmp_path / "manifest.json").write_text('{"agents": []}', encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo_valid(tmp_path: Path) -> Path:
    """Repo with manifest.json and matching .manifest.lock."""
    content = b'{"agents": []}'
    (tmp_path / "manifest.json").write_bytes(content)
    (tmp_path / ".manifest.lock").write_text(_sha256(content), encoding="utf-8")
    return tmp_path


@pytest.fixture
def repo_tampered(tmp_path: Path) -> Path:
    """Repo with manifest.json modified after seal."""
    original = b'{"agents": []}'
    (tmp_path / ".manifest.lock").write_text(_sha256(original), encoding="utf-8")
    (tmp_path / "manifest.json").write_bytes(b'{"agents": ["rogue"]}')
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Missing manifest → SKIP
# ---------------------------------------------------------------------------


class TestMissingManifest:
    def test_no_manifest_returns_pass(self, repo_no_manifest: Path):
        result = run_manifest_guardian(repo_root=repo_no_manifest)
        assert result.status == GuardianStatus.PASS.value

    def test_no_manifest_has_skip_check(self, repo_no_manifest: Path):
        result = run_manifest_guardian(repo_root=repo_no_manifest)
        skip_checks = [c for c in result.checks if c.status == CheckStatus.SKIP.value]
        assert len(skip_checks) >= 1

    def test_manifest_exists_check_id(self, repo_no_manifest: Path):
        result = run_manifest_guardian(repo_root=repo_no_manifest)
        check_ids = {c.check_id for c in result.checks}
        assert "manifest_exists" in check_ids


# ---------------------------------------------------------------------------
# 2. Missing lock → FAIL
# ---------------------------------------------------------------------------


class TestMissingLock:
    def test_no_lock_fails(self, repo_no_lock: Path):
        result = run_manifest_guardian(repo_root=repo_no_lock)
        assert result.status == GuardianStatus.FAIL.value

    def test_no_lock_check_id(self, repo_no_lock: Path):
        result = run_manifest_guardian(repo_root=repo_no_lock)
        lock_check = next(c for c in result.checks if c.check_id == "lock_exists")
        assert lock_check.status == CheckStatus.FAIL.value

    def test_no_lock_has_remediation(self, repo_no_lock: Path):
        result = run_manifest_guardian(repo_root=repo_no_lock)
        assert len(result.remediation_hints) > 0


# ---------------------------------------------------------------------------
# 3. Valid manifest + lock → PASS
# ---------------------------------------------------------------------------


class TestValidManifest:
    def test_valid_passes(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        assert result.status == GuardianStatus.PASS.value

    def test_all_checks_pass(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        for check in result.checks:
            assert check.status == CheckStatus.PASS.value, f"Check {check.check_id} should PASS"

    def test_checksum_evidence(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        cs_check = next(c for c in result.checks if c.check_id == "checksum_match")
        assert "sha256" in cs_check.evidence


# ---------------------------------------------------------------------------
# 4. Tampered manifest → FAIL
# ---------------------------------------------------------------------------


class TestTamperedManifest:
    def test_tampered_fails(self, repo_tampered: Path):
        result = run_manifest_guardian(repo_root=repo_tampered)
        assert result.status == GuardianStatus.FAIL.value

    def test_checksum_mismatch_details(self, repo_tampered: Path):
        result = run_manifest_guardian(repo_root=repo_tampered)
        cs_check = next(c for c in result.checks if c.check_id == "checksum_match")
        assert cs_check.status == CheckStatus.FAIL.value
        assert "expected" in cs_check.evidence
        assert "actual" in cs_check.evidence

    def test_tampered_has_remediation(self, repo_tampered: Path):
        result = run_manifest_guardian(repo_root=repo_tampered)
        assert len(result.remediation_hints) > 0


# ---------------------------------------------------------------------------
# 5. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"Absolute paths: {violations}"

    def test_validation_passes(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        errors = result.validate()
        assert errors == [], f"Contract violations: {errors}"

    def test_guardian_id_is_stable(self, repo_valid: Path):
        result = run_manifest_guardian(repo_root=repo_valid)
        assert result.guardian_id == "manifest_integrity"


# ---------------------------------------------------------------------------
# 6. Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_input_same_output(self, repo_valid: Path):
        r1 = run_manifest_guardian(repo_root=repo_valid)
        r2 = run_manifest_guardian(repo_root=repo_valid)
        assert r1.to_json() == r2.to_json()

    def test_timestamp_injectable(self, repo_valid: Path):
        ts = "2026-02-08T00:00:00Z"
        result = run_manifest_guardian(repo_root=repo_valid, timestamp=ts)
        assert result.timestamp == ts
