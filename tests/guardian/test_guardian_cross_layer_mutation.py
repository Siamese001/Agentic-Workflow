"""
Guardian Cross-Layer Mutation Tests.

1. Clean repo → PASS on all layer mutation checks
2. L6 file importing from L4 → FAIL on L6_mutates_L4
3. L4 file importing from L2 → FAIL on L4_invokes_L2
4. File with embedding assigned to control_plane → FAIL on C0_mutates_control_plane
5. Output conforms to guardian_contract schema
6. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation import (
    run_cross_layer_mutation_guardian,
    scan_cross_layer_mutations,
)
from agentic_core.L0_routing.types.guardian_contract import (
    CheckStatus,
    GuardianStatus,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core" / "L0_routing").mkdir(parents=True)
    (tmp_path / "agentic_core" / "L0_routing" / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def l6_l4_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core" / "L6_observability").mkdir(parents=True)
    (tmp_path / "agentic_core" / "L6_observability" / "bad.py").write_text(
        "from agentic_core.L4_state import Something\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def l4_l2_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core" / "L4_state").mkdir(parents=True)
    (tmp_path / "agentic_core" / "L4_state" / "bad.py").write_text(
        "from agentic_core.L2_execution import Something\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def c0_control_plane_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core" / "L1_cognition").mkdir(parents=True)
    (tmp_path / "agentic_core" / "L1_cognition" / "bad.py").write_text(
        "control_plane = embedding_score\n", encoding="utf-8"
    )
    return tmp_path


class TestCrossLayerMutationGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_cross_layer_mutation_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["upward_layer_mutation"] == CheckStatus.PASS.value
        assert check_map["L6_mutates_L4"] == CheckStatus.PASS.value
        assert check_map["L4_invokes_L2"] == CheckStatus.PASS.value
        assert check_map["C0_mutates_control_plane"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_cross_layer_mutation_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value

    def test_no_absolute_paths_in_result(self, clean_repo):
        result = run_cross_layer_mutation_guardian(repo_root=clean_repo)
        errs = validate_no_absolute_paths(result.to_dict())
        assert not errs


class TestCrossLayerMutationGuardianViolations:
    def test_l6_l4_detected(self, l6_l4_repo):
        viols = scan_cross_layer_mutations(l6_l4_repo)
        assert viols["L6_mutates_L4"]
        assert len(viols["L6_mutates_L4"]) == 1

    def test_l6_l4_fails_result(self, l6_l4_repo):
        result = run_cross_layer_mutation_guardian(repo_root=l6_l4_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["L6_mutates_L4"] == CheckStatus.FAIL.value

    def test_l4_l2_detected(self, l4_l2_repo):
        viols = scan_cross_layer_mutations(l4_l2_repo)
        assert viols["L4_invokes_L2"]
        assert len(viols["L4_invokes_L2"]) == 1

    def test_l4_l2_fails_result(self, l4_l2_repo):
        result = run_cross_layer_mutation_guardian(repo_root=l4_l2_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["L4_invokes_L2"] == CheckStatus.FAIL.value

    def test_c0_control_plane_detected(self, c0_control_plane_repo):
        viols = scan_cross_layer_mutations(c0_control_plane_repo)
        assert viols["C0_mutates_control_plane"]
        assert len(viols["C0_mutates_control_plane"]) == 1

    def test_c0_control_plane_fails_result(self, c0_control_plane_repo):
        result = run_cross_layer_mutation_guardian(repo_root=c0_control_plane_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["C0_mutates_control_plane"] == CheckStatus.FAIL.value


class TestCrossLayerMutationDeterminism:
    def test_scan_is_deterministic(self, l6_l4_repo):
        a = scan_cross_layer_mutations(l6_l4_repo)
        b = scan_cross_layer_mutations(l6_l4_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_cross_layer_mutation_guardian(repo_root=clean_repo)
        assert result.guardian_id == "cross_layer_mutation_guard"
