"""
Guardian Gateway Bypass Tests.

1. Clean repo → PASS on provider_sdk_import and direct_model_call
2. File with forbidden import → FAIL with correct check_id
3. Allowlisted file containing SDK import → PASS (not flagged)
4. File with direct OpenAI() call → FAIL on direct_model_call
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

from agentic_core.L0_routing.scripts.run_guardian_gateway_bypass import (
    run_gateway_bypass_guardian,
    scan_direct_model_calls,
    scan_provider_sdk_imports,
)
from agentic_core.L0_routing.types.guardian_contract import (
    CheckStatus,
    GuardianStatus,
    validate_no_absolute_paths,
)

pytestmark = pytest.mark.guardian


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "agentic_core" / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def sdk_import_repo(tmp_path: Path) -> Path:
    (tmp_path / "agentic_core").mkdir()
    (tmp_path / "agentic_core" / "bad.py").write_text("import openai\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def direct_call_repo(tmp_path: Path) -> Path:
    (tmp_path / "apps_lic").mkdir()
    (tmp_path / "apps_lic" / "caller.py").write_text(
        "from openai import OpenAI\nclient = OpenAI()\n", encoding="utf-8"
    )
    return tmp_path


class TestGatewayBypassGuardianClean:
    def test_clean_repo_passes(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["provider_sdk_import"] == CheckStatus.PASS.value
        assert check_map["direct_model_call"] == CheckStatus.PASS.value

    def test_clean_repo_top_status_pass(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        assert result.status == GuardianStatus.PASS.value

    def test_no_absolute_paths_in_result(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        errs = validate_no_absolute_paths(result.to_dict())
        assert not errs


class TestGatewayBypassGuardianViolations:
    def test_sdk_import_detected(self, sdk_import_repo):
        viols = scan_provider_sdk_imports(sdk_import_repo)
        assert any(v["check_id"] == "provider_sdk_import" for v in viols)
        assert any("openai" in v["detail"] for v in viols)

    def test_sdk_import_fails_result(self, sdk_import_repo):
        result = run_gateway_bypass_guardian(repo_root=sdk_import_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["provider_sdk_import"] == CheckStatus.FAIL.value

    def test_direct_call_detected(self, direct_call_repo):
        viols = scan_direct_model_calls(direct_call_repo)
        assert any(v["check_id"] == "direct_model_call" for v in viols)

    def test_direct_call_fails_result(self, direct_call_repo):
        result = run_gateway_bypass_guardian(repo_root=direct_call_repo)
        check_map = {c.check_id: c.status for c in result.checks}
        assert check_map["direct_model_call"] == CheckStatus.FAIL.value


class TestGatewayBypassDeterminism:
    def test_scan_is_deterministic(self, sdk_import_repo):
        a = scan_provider_sdk_imports(sdk_import_repo)
        b = scan_provider_sdk_imports(sdk_import_repo)
        assert a == b

    def test_result_guardian_id_correct(self, clean_repo):
        result = run_gateway_bypass_guardian(repo_root=clean_repo)
        assert result.guardian_id == "gateway_bypass"
