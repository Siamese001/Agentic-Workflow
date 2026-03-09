"""
Guardian Escalation Determinism Tests.

1. Clean repo → PASS on all escalation checks
2. File with f-string in FailureSignal() → FAIL on failure_signal_built_from_raw_notes
3. File with mutation on escalation context → FAIL on escalation_context_mutation
4. Output conforms to guardian_contract schema
5. scan functions are deterministic (same input → same output)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.scripts.run_guardian_escalation_determinism import (
    run_escalation_determinism_guardian,
    scan_escalation_patterns,
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
def fstring_signal_repo(tmp_path: Path) -> Path:
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / AGENTIC_CORE_DIR / "bad.py").write_text("FailureSignal(f'error: {msg}')\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def mutation_context_repo(tmp_path: Path) -> Path:
    (tmp_path / APPS_LIC_DIR).mkdir()
    (tmp_path / APPS_LIC_DIR / "bad.py").write_text(
        "escalation_context.update({'key': 'value'})\n", encoding="utf-8"
    )
    return tmp_path


class TestEscalationDeterminismGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["failure_signal_built_from_raw_notes"] == CheckStatus.PASS.value
        assert check_map["alternate_escalation_context_construction"] == CheckStatus.PASS.value
        assert check_map["escalation_context_mutation"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value

    def test_no_absolute_paths_in_result(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        errs = validate_no_absolute_paths(result.to_dict())
        assert not errs


class TestEscalationDeterminismGuardianViolations:
    def test_fstring_signal_detected(self, fstring_signal_repo):
        viols = scan_escalation_patterns(fstring_signal_repo)
        assert viols["failure_signal_built_from_raw_notes"]
        assert len(viols["failure_signal_built_from_raw_notes"]) == 1

    def test_fstring_signal_fails_result(self, fstring_signal_repo):
        result = run_escalation_determinism_guardian(repo_root=fstring_signal_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["failure_signal_built_from_raw_notes"] == CheckStatus.FAIL.value

    def test_mutation_context_detected(self, mutation_context_repo):
        viols = scan_escalation_patterns(mutation_context_repo)
        assert viols["escalation_context_mutation"]
        assert len(viols["escalation_context_mutation"]) == 1

    def test_mutation_context_fails_result(self, mutation_context_repo):
        result = run_escalation_determinism_guardian(repo_root=mutation_context_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["escalation_context_mutation"] == CheckStatus.FAIL.value


class TestEscalationDeterminismDeterminism:
    def test_scan_is_deterministic(self, fstring_signal_repo):
        a = scan_escalation_patterns(fstring_signal_repo)
        b = scan_escalation_patterns(fstring_signal_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_escalation_determinism_guardian(repo_root=clean_repo)
        assert result.guardian_id == "escalation_determinism"
