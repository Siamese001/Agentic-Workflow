"""
Guardian C0 Sovereignty Tests.

1. Clean repo → PASS on all embedding boundary checks
2. File with embedding in conditional → FAIL on embedding_drives_routing
3. File with embedding assigned to threshold → FAIL on embedding_mutates_threshold
4. Output conforms to guardian_contract schema
5. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty import (
    run_c0_sovereignty_guardian,
    scan_embedding_control_flow,
)
from agentic_core.L0_routing.types.guardian_contract_types import (
    CheckStatus,
    GuardianStatus,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def embedding_routing_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text(
        "if embedding_score > 0.5:\n    route = 'high'\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture()
def embedding_threshold_repo(tmp_path: Path) -> Path:
    (tmp_path / SYSTEM_LEARNING_DIR).mkdir()
    (tmp_path / SYSTEM_LEARNING_DIR / "bad.py").write_text("threshold = embedding_result\n", encoding="utf-8")
    return tmp_path


class TestC0SovereigntyGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_c0_sovereignty_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["embedding_drives_routing"] == CheckStatus.PASS.value
        assert check_map["embedding_drives_tier_selection"] == CheckStatus.PASS.value
        assert check_map["embedding_mutates_threshold"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_c0_sovereignty_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value

    def test_no_absolute_paths_in_result(self, clean_repo):
        result = run_c0_sovereignty_guardian(repo_root=clean_repo)
        errs = validate_no_absolute_paths(result.to_dict())
        assert not errs


class TestC0SovereigntyGuardianViolations:
    def test_embedding_routing_detected(self, embedding_routing_repo):
        viols = scan_embedding_control_flow(embedding_routing_repo)
        assert viols["embedding_drives_routing"]
        assert len(viols["embedding_drives_routing"]) == 1

    def test_embedding_routing_fails_result(self, embedding_routing_repo):
        result = run_c0_sovereignty_guardian(repo_root=embedding_routing_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["embedding_drives_routing"] == CheckStatus.FAIL.value

    def test_embedding_threshold_detected(self, embedding_threshold_repo):
        viols = scan_embedding_control_flow(embedding_threshold_repo)
        assert viols["embedding_mutates_threshold"]
        assert len(viols["embedding_mutates_threshold"]) == 1

    def test_embedding_threshold_fails_result(self, embedding_threshold_repo):
        result = run_c0_sovereignty_guardian(repo_root=embedding_threshold_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["embedding_mutates_threshold"] == CheckStatus.FAIL.value


class TestC0SovereigntyDeterminism:
    def test_scan_is_deterministic(self, embedding_routing_repo):
        a = scan_embedding_control_flow(embedding_routing_repo)
        b = scan_embedding_control_flow(embedding_routing_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_c0_sovereignty_guardian(repo_root=clean_repo)
        assert result.guardian_id == "c0_sovereignty_enforcement"
