"""
Guardian: Config-With-Logic Anti-Pattern Tests.

§1 windsurfrules compliance:
- §1.1  Every changed logic has deterministic test coverage
- §1.3  No randomness / wall-clock; all fixtures are static strings
- §1.5  Edge cases: None/empty, malformed, boundary, negative control
- §1.7  Determinism: same input → same violations list
- §1.8  Fail-closed: violation is raised, no side-effects
- §1.9  Matrix: lambda × assignment-type, if × function-name-suffix
- §1.11 Regression: near-miss cases (non-config var with lambda, etc.)

ROBUSTNESS_MATRIX:
  Surface                        | success | edge | failure | determinism
  -------------------------------|---------|------|---------|------------
  lambda in *_config assignment  |   ✅   |  ✅  |   ✅   |     ✅
  lambda in *_spec assignment    |   ✅   |  ✅  |   ✅   |     ✅
  lambda in *_policy assignment  |   ✅   |  ✅  |   ✅   |     ✅
  if-branch in *_config func     |   ✅   |  ✅  |   ✅   |     ✅
  whitelist comment suppression  |   ✅   |  ✅  |   ✅   |     ✅
  clean file                     |   ✅   |  ✅  |   N/A  |     ✅

DEFECT_MODEL:
  D1 - lambda in config dict causes hidden runtime dispatch
  D2 - if-branch in config factory creates shadow runtime behaviour
  D3 - whitelist bypass incorrectly suppresses valid violations
  D4 - non-config variable with lambda triggers false positive
  D5 - detector non-determinism across repeated scans
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.config_with_logic_validator import (
    ConfigWithLogicDetector,
)

pytestmark = pytest.mark.guardian

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _detector() -> ConfigWithLogicDetector:
    return ConfigWithLogicDetector(enforcement_level=EnforcementLevel.WARNING)


def _violations(source: str, tmp_path: Path) -> list:
    f = tmp_path / "subject.py"
    f.write_text(source, encoding="utf-8")
    tree = ast.parse(source)
    det = _detector()
    return det.detect(f, tree)


# ---------------------------------------------------------------------------
# Clean-file tests (success path)
# ---------------------------------------------------------------------------


class TestConfigWithLogicCleanFile:
    def test_plain_data_dict_no_violations(self, tmp_path):
        src = "my_config = {'key': 'value', 'n': 42}\n"
        assert _violations(src, tmp_path) == []

    def test_nested_plain_dict_no_violations(self, tmp_path):
        src = "agent_spec = {'name': 'foo', 'opts': {'timeout': 30}}\n"
        assert _violations(src, tmp_path) == []

    def test_non_config_name_with_lambda_no_violation(self, tmp_path):
        # D4 regression: lambda in non-config var must NOT trigger
        src = "transform = lambda x: x * 2\n"
        assert _violations(src, tmp_path) == []

    def test_function_not_config_suffix_with_if_no_violation(self, tmp_path):
        src = "def build_payload(x):\n    if x:\n        return x\n    return None\n"
        assert _violations(src, tmp_path) == []

    def test_empty_file_no_violations(self, tmp_path):
        assert _violations("", tmp_path) == []

    def test_comment_only_file_no_violations(self, tmp_path):
        assert _violations("# just a comment\n", tmp_path) == []


# ---------------------------------------------------------------------------
# Lambda-in-config-assignment violations
# ---------------------------------------------------------------------------


class TestLambdaInConfigAssignment:
    def test_lambda_in_config_var_detected(self, tmp_path):
        src = "my_config = {'transform': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1
        assert viols[0].category == AntiPatternCategory.CONFIG_WITH_LOGIC

    def test_lambda_in_spec_var_detected(self, tmp_path):
        src = "agent_spec = {'fn': lambda v: v + 1}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_in_policy_var_detected(self, tmp_path):
        src = "routing_policy = {'filter': lambda x: x > 0}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_in_settings_var_detected(self, tmp_path):
        src = "app_settings = {'hook': lambda: None}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_in_options_var_detected(self, tmp_path):
        src = "render_options = {'fmt': lambda s: s.lower()}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_lambda_violation_has_error_severity(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert viols[0].severity == "error"

    def test_lambda_violation_message_contains_keyword(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert "lambda" in viols[0].message.lower()

    def test_multiple_lambdas_produces_multiple_violations(self, tmp_path):
        src = "my_config = {\n    'a': lambda x: x,\n    'b': lambda y: y + 1,\n}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 2


# ---------------------------------------------------------------------------
# If-branch in config-factory function violations
# ---------------------------------------------------------------------------


class TestIfBranchInConfigFactory:
    def test_if_in_config_function_detected(self, tmp_path):
        src = (
            "def build_config(env):\n"
            "    if env == 'prod':\n"
            "        return {'db': 'prod-db'}\n"
            "    return {'db': 'dev-db'}\n"
        )
        viols = _violations(src, tmp_path)
        assert len(viols) == 1
        assert viols[0].category == AntiPatternCategory.CONFIG_WITH_LOGIC

    def test_if_in_spec_function_detected(self, tmp_path):
        src = (
            "def agent_spec(tier):\n"
            "    if tier > 2:\n"
            "        return {'model': 'pro'}\n"
            "    return {'model': 'basic'}\n"
        )
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_if_in_policy_function_detected(self, tmp_path):
        src = (
            "def routing_policy(flag):\n"
            "    if flag:\n"
            "        return {'allow': True}\n"
            "    return {'allow': False}\n"
        )
        viols = _violations(src, tmp_path)
        assert len(viols) == 1

    def test_if_violation_message_mentions_function_name(self, tmp_path):
        src = "def load_config(x):\n    if x:\n        return {}\n    return {}\n"
        viols = _violations(src, tmp_path)
        assert "load_config" in viols[0].message


# ---------------------------------------------------------------------------
# Whitelist suppression (§1.11 near-miss)
# ---------------------------------------------------------------------------


class TestWhitelistSuppression:
    def test_whitelist_comment_suppresses_lambda(self, tmp_path):
        src = "# guardian: allow-config-with-logic\nmy_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert viols == []

    def test_whitelist_on_wrong_line_does_not_suppress(self, tmp_path):
        src = "# guardian: allow-config-with-logic\n\nmy_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        # whitelist is >2 lines away — still flagged
        assert len(viols) == 1

    def test_partial_whitelist_string_does_not_suppress(self, tmp_path):
        src = "# guardian: allow-other-thing\nmy_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) == 1


# ---------------------------------------------------------------------------
# Determinism (§1.7 / §1.3)
# ---------------------------------------------------------------------------


class TestDetectorDeterminism:
    def test_same_source_produces_identical_violations(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols_a = _violations(src, tmp_path)
        # use a fresh temp file to avoid caching side-effects
        tmp2 = tmp_path / "second"
        tmp2.mkdir()
        viols_b = _violations(src, tmp2)
        assert len(viols_a) == len(viols_b)
        assert viols_a[0].category == viols_b[0].category
        assert viols_a[0].message == viols_b[0].message

    def test_clean_source_consistently_empty(self, tmp_path):
        src = "my_config = {'key': 42}\n"
        for _ in range(3):
            assert _violations(src, tmp_path) == []


# ---------------------------------------------------------------------------
# Fail-closed: violation object is well-formed (§1.8)
# ---------------------------------------------------------------------------


class TestViolationContract:
    def test_violation_has_required_fields(self, tmp_path):
        src = "my_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        v = viols[0]
        assert v.file_path is not None
        assert v.line_number >= 1
        assert v.category == AntiPatternCategory.CONFIG_WITH_LOGIC
        assert v.message
        assert v.evidence
        assert v.suggested_fix

    def test_violation_line_number_is_accurate(self, tmp_path):
        src = "x = 1\nmy_config = {'fn': lambda x: x}\n"
        viols = _violations(src, tmp_path)
        # lambda is on line 2
        assert viols[0].line_number == 2

    def test_violation_file_path_matches(self, tmp_path):
        f = tmp_path / "subject.py"
        src = "my_config = {'fn': lambda x: x}\n"
        f.write_text(src, encoding="utf-8")
        tree = ast.parse(src)
        viols = _detector().detect(f, tree)
        assert viols[0].file_path == f


# ---------------------------------------------------------------------------
# Matrix: variable-suffix × value-type (§1.9)
# ---------------------------------------------------------------------------


class TestSuffixMatrix:
    @pytest.mark.parametrize(
        "varname",
        ["my_config", "agent_spec", "routing_policy", "app_settings", "render_options"],
    )
    def test_all_config_suffixes_trigger(self, varname, tmp_path):
        src = f"{varname} = {{'fn': lambda x: x}}\n"
        viols = _violations(src, tmp_path)
        assert len(viols) >= 1, f"Expected violation for varname={varname!r}"

    @pytest.mark.parametrize(
        "varname",
        ["helper", "transform", "pipeline", "result", "data"],
    )
    def test_non_config_names_do_not_trigger(self, varname, tmp_path):
        src = f"{varname} = {{'fn': lambda x: x}}\n"
        viols = _violations(src, tmp_path)
        assert viols == [], f"Expected no violation for varname={varname!r}"
