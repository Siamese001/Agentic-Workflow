"""
Guardian Change Package Activation Tests.

1. Clean repo → PASS on all activation checks
2. File with direct VersionStore.commit() → FAIL on direct_version_store_commit
3. File with activate() missing approval_gate → FAIL on activation_without_approval_gate
4. Output conforms to guardian_contract schema
5. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_change_package_activation import (
    run_change_package_activation_guardian,
    scan_activation_patterns,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
)

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def direct_commit_repo(tmp_path: Path) -> Path:
    (tmp_path / SYSTEM_LEARNING_DIR).mkdir()
    (tmp_path / SYSTEM_LEARNING_DIR / "bad.py").write_text("version_store.commit(data)\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def missing_gate_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text("change_package.activate()\n", encoding="utf-8")
    return tmp_path


class TestChangePackageActivationGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_change_package_activation_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["proposal_only_bypass"] == CheckStatus.PASS.value
        assert check_map["direct_version_store_commit"] == CheckStatus.PASS.value
        assert check_map["activation_without_approval_gate"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_change_package_activation_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value


class TestChangePackageActivationGuardianViolations:
    def test_direct_commit_detected(self, direct_commit_repo):
        viols = scan_activation_patterns(direct_commit_repo)
        assert viols["direct_version_store_commit"]
        assert len(viols["direct_version_store_commit"]) == 1

    def test_direct_commit_fails_result(self, direct_commit_repo):
        result = run_change_package_activation_guardian(repo_root=direct_commit_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["direct_version_store_commit"] == CheckStatus.FAIL.value

    def test_missing_gate_detected(self, missing_gate_repo):
        viols = scan_activation_patterns(missing_gate_repo)
        assert viols["activation_without_approval_gate"]
        assert len(viols["activation_without_approval_gate"]) == 1

    def test_missing_gate_fails_result(self, missing_gate_repo):
        result = run_change_package_activation_guardian(repo_root=missing_gate_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["activation_without_approval_gate"] == CheckStatus.FAIL.value


class TestChangePackageActivationDeterminism:
    def test_scan_is_deterministic(self, direct_commit_repo):
        a = scan_activation_patterns(direct_commit_repo)
        b = scan_activation_patterns(direct_commit_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_change_package_activation_guardian(repo_root=clean_repo)
        assert result.guardian_id == "change_package_activation_guard"
