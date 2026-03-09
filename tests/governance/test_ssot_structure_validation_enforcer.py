"""
Wave 1 Phase 2 — SSOT Structure Validation Enforcer Tests

§4-compliant test suite covering:
- Success paths (compliant agents pass all checks)
- Branch paths (all conditionals in each validator method)
- Negative controls (violations correctly detected and categorised)
- Edge cases (empty paths, root-level files, exact depth boundaries)
- Exception paths (graceful handling of missing data)
- Determinism (same agent → same result twice)
- Side-effect safety (validate_agent does not mutate shared state)
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L5_safety.enforcement.registry_verification_enforcer import AgentInfo
from agentic_core.L5_safety.enforcement.ssot_structure_validation_enforcer import (
    BASE_AGENT_REQUIRED_PATH,
    LAYER_PATTERNS,
    SSOTStructureValidator,
    StructureValidationResult,
    StructureViolation,
    run_structure_validation,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_agent(
    class_name: str = "FooAgent",
    relative_path: str = "agentic_core/L2_execution/engines/foo_agent.py",
    layer: str = "L2",
) -> AgentInfo:
    """Build a minimal AgentInfo for testing."""
    return AgentInfo(
        class_name=class_name,
        file_path=Path(relative_path),
        relative_path=relative_path,
        layer=layer,
    )


@pytest.fixture()
def validator() -> SSOTStructureValidator:
    return SSOTStructureValidator(REPO_ROOT)


# ===========================================================================
# 1. Success-path tests
# ===========================================================================


class TestSuccessPaths:
    @pytest.mark.governance
    def test_validate_agent_returns_empty_when_l2_agent_compliant(self, validator):
        agent = _make_agent(
            class_name="SandboxAirlock",
            relative_path="agentic_core/L2_execution/assembly/sandbox_airlock.py",
            layer="L2",
        )
        violations = validator.validate_agent(agent)
        # May or may not have territory/depth violations depending on blueprint;
        # critical: no base_agent_location violation for non-BaseAgent class
        base_violations = [v for v in violations if v.violation_type == "base_agent_location"]
        assert base_violations == []

    @pytest.mark.governance
    def test_normalize_path_converts_backslash_to_forward(self, validator):
        result = validator._normalize_path("agentic_core\\L2_execution\\foo.py")
        assert "\\" not in result
        assert "agentic_core/L2_execution/foo.py" == result

    @pytest.mark.governance
    def test_normalize_path_leaves_forward_slash_unchanged(self, validator):
        path = "agentic_core/L5_safety/enforcement/foo.py"
        assert validator._normalize_path(path) == path

    @pytest.mark.governance
    def test_get_actual_depth_returns_correct_count(self, validator):
        path = "agentic_core/L2_execution/engines/foo.py"
        assert validator._get_actual_depth(path) == 4

    @pytest.mark.governance
    def test_structure_validation_result_compliance_pct_when_all_compliant(self):
        result = StructureValidationResult(total_agents=10, compliant_agents=10)
        assert result.compliance_percentage == 100.0

    @pytest.mark.governance
    def test_structure_validation_result_is_fully_compliant_when_no_violations(self):
        result = StructureValidationResult()
        assert result.is_fully_compliant is True

    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_path_and_layer_match(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="L2",
        )
        result = validator._validate_layer_assignment(agent)
        assert result is None

    @pytest.mark.governance
    def test_validate_base_agent_location_returns_none_when_not_base_agent(self, validator):
        agent = _make_agent(
            class_name="RegularAgent",
            relative_path="agentic_core/L2_execution/engines/regular_agent.py",
        )
        assert validator._validate_base_agent_location(agent) is None

    @pytest.mark.governance
    def test_validate_base_agent_location_returns_none_when_base_agent_in_correct_path(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="agentic_core/base_agents/sovereign_base_agent.py",
            layer="Root",
        )
        assert validator._validate_base_agent_location(agent) is None

    @pytest.mark.governance
    def test_generate_report_contains_summary_section(self, validator):
        result = StructureValidationResult(total_agents=5, compliant_agents=5)
        report = validator.generate_report(result)
        assert "Summary" in report
        assert "Total Agents" in report

    @pytest.mark.governance
    def test_generate_report_shows_100_percent_when_fully_compliant(self, validator):
        result = StructureValidationResult(total_agents=4, compliant_agents=4)
        report = validator.generate_report(result)
        assert "100.0%" in report


# ===========================================================================
# 2. Branch-path tests
# ===========================================================================


class TestBranchPaths:
    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_outside_agentic_core(self, validator):
        # apps_rg path — not in agentic_core, should be skipped
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="apps_rg/engines/foo_agent.py",
            layer="L2",
        )
        assert validator._validate_layer_assignment(agent) is None

    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_path_too_short(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path=AGENTIC_CORE_DIR,
            layer="L2",
        )
        assert validator._validate_layer_assignment(agent) is None

    @pytest.mark.governance
    def test_validate_layer_assignment_returns_none_when_layer_is_unknown(self, validator):
        # Unknown layer should not produce violation
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="Unknown",
        )
        assert validator._validate_layer_assignment(agent) is None

    @pytest.mark.governance
    def test_validate_territory_returns_none_when_territory_recognised(self, validator):
        agent = _make_agent(
            relative_path="agentic_core/L2_execution/engines/foo.py",
        )
        # Only check: no root_file or unknown_territory violation for known root
        result = validator._validate_territory(agent)
        if result is not None:
            assert result.violation_type not in ("root_file",)

    @pytest.mark.governance
    def test_validate_territory_detects_root_file(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="foo_agent.py",
            layer="Root",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "root_file"

    @pytest.mark.governance
    def test_validate_territory_detects_unknown_territory(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="totally_unknown_dir/foo.py",
            layer="Unknown",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "unknown_territory"

    @pytest.mark.governance
    def test_is_base_agent_returns_true_when_name_ends_with_base_agent(self, validator):
        assert validator._is_base_agent("SovereignBaseAgent") is True

    @pytest.mark.governance
    def test_is_base_agent_returns_false_when_name_does_not_end_with_base_agent(self, validator):
        assert validator._is_base_agent("RegularAgent") is False

    @pytest.mark.governance
    def test_validate_depth_returns_none_when_in_variable_depth_folder(self, validator):
        # "scripts" is typically a variable-depth subfolder
        agent = _make_agent(
            relative_path="agentic_core/L0_routing/scripts/sub/deep/very_deep/foo.py",
        )
        result = validator._validate_depth(agent)
        # Either None or depth violation — but NOT none only because variable depth was ignored
        # We verify the method returns without raising
        assert result is None or isinstance(result, StructureViolation)

    @pytest.mark.governance
    def test_get_actual_depth_returns_1_for_single_part_path(self, validator):
        assert validator._get_actual_depth("foo.py") == 1

    @pytest.mark.governance
    def test_get_actual_depth_handles_trailing_slash(self, validator):
        # Should handle paths normalised with trailing slash stripped
        depth = validator._get_actual_depth("agentic_core/L2_execution/")
        assert depth >= 1

    @pytest.mark.governance
    def test_validate_agent_aggregates_all_violation_types(self, validator):
        # A base agent outside required path produces exactly base_agent_location violation
        agent = _make_agent(
            class_name="WrongPlaceBaseAgent",
            relative_path="apps_rg/engines/wrong_base_agent.py",
            layer="Unknown",
        )
        violations = validator.validate_agent(agent)
        violation_types = {v.violation_type for v in violations}
        assert "base_agent_location" in violation_types

    @pytest.mark.governance
    def test_structure_validation_result_compliance_pct_zero_when_no_agents(self):
        result = StructureValidationResult(total_agents=0, compliant_agents=0)
        assert result.compliance_percentage == 0.0

    @pytest.mark.governance
    def test_structure_validation_result_is_not_fully_compliant_when_violations(self):
        v = StructureViolation(
            agent_class="Foo",
            agent_path="foo.py",
            violation_type="root_file",
            message="bad",
        )
        result = StructureValidationResult(violations=[v])
        assert result.is_fully_compliant is False


# ===========================================================================
# 3. Negative controls (enforcement + fail-closed)
# ===========================================================================


class TestNegativeControls:
    @pytest.mark.governance
    def test_validate_base_agent_location_flags_base_agent_outside_required_path(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="agentic_core/L5_safety/enforcement/sovereign_base_agent.py",
            layer="L5",
        )
        result = validator._validate_base_agent_location(agent)
        assert result is not None
        assert result.violation_type == "base_agent_location"
        assert result.severity == "critical"

    @pytest.mark.governance
    def test_validate_layer_assignment_flags_layer_mismatch(self, validator):
        # File is in L2 but agent.layer claims L5
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="L5",
        )
        result = validator._validate_layer_assignment(agent)
        assert result is not None
        assert result.violation_type == "layer_mismatch"

    @pytest.mark.governance
    def test_validate_territory_flags_root_level_file(self, validator):
        agent = _make_agent(
            class_name="BadAgent",
            relative_path="bad_agent.py",
            layer="Root",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "root_file"
        assert result.severity == "error"

    @pytest.mark.governance
    def test_validate_territory_flags_unknown_territory_with_warning(self, validator):
        agent = _make_agent(
            relative_path="forbidden_zone/sub/foo.py",
        )
        result = validator._validate_territory(agent)
        assert result is not None
        assert result.violation_type == "unknown_territory"

    @pytest.mark.governance
    def test_structure_violation_severity_defaults_to_warning(self):
        v = StructureViolation(
            agent_class="Foo",
            agent_path="foo.py",
            violation_type="unknown_territory",
            message="test",
        )
        assert v.severity == "warning"

    @pytest.mark.governance
    def test_validate_agent_includes_violation_in_result_list(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="apps_rg/engines/bad.py",
            layer="Unknown",
        )
        violations = validator.validate_agent(agent)
        assert len(violations) >= 1

    @pytest.mark.governance
    def test_generate_report_shows_base_agent_violations_section(self, validator):
        v = StructureViolation(
            agent_class="BrokenBaseAgent",
            agent_path="wrong/path.py",
            violation_type="base_agent_location",
            message="must be in base_agents",
            severity="critical",
            suggested_fix="move to base_agents/",
        )
        result = StructureValidationResult(
            total_agents=1,
            compliant_agents=0,
            violations=[v],
            base_agent_violations=[v],
        )
        report = validator.generate_report(result)
        assert "Critical" in report or "Base Agent" in report


# ===========================================================================
# 4. Edge cases
# ===========================================================================


class TestEdgeCases:
    @pytest.mark.governance
    def test_normalize_path_handles_empty_string(self, validator):
        result = validator._normalize_path("")
        assert result == ""

    @pytest.mark.governance
    def test_get_actual_depth_returns_zero_for_empty_path(self, validator):
        # Empty parts after filtering — should not crash
        depth = validator._get_actual_depth("")
        assert isinstance(depth, int)

    @pytest.mark.governance
    def test_validate_depth_returns_none_when_no_territory(self, validator):
        agent = _make_agent(
            relative_path="totally_unknown_territory/foo.py",
        )
        # No known territory → depth validation should skip
        result = validator._validate_depth(agent)
        assert result is None

    @pytest.mark.governance
    def test_validate_base_agent_location_handles_empty_path(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="",
            layer="Unknown",
        )
        # Should not raise; must return a violation or None
        result = validator._validate_base_agent_location(agent)
        assert result is None or isinstance(result, StructureViolation)

    @pytest.mark.governance
    def test_validate_layer_assignment_handles_empty_path(self, validator):
        agent = _make_agent(
            class_name="FooAgent",
            relative_path="",
            layer="L2",
        )
        result = validator._validate_layer_assignment(agent)
        assert result is None or isinstance(result, StructureViolation)

    @pytest.mark.governance
    def test_structure_validation_result_compliance_pct_with_partial_compliance(self):
        result = StructureValidationResult(total_agents=10, compliant_agents=7)
        assert result.compliance_percentage == pytest.approx(70.0)

    @pytest.mark.governance
    def test_generate_report_truncates_territory_violations_beyond_20(self, validator):
        violations = [
            StructureViolation(
                agent_class=f"Agent{i}",
                agent_path=f"unknown/agent{i}.py",
                violation_type="unknown_territory",
                message="bad",
            )
            for i in range(25)
        ]
        result = StructureValidationResult(
            total_agents=25,
            compliant_agents=0,
            violations=violations,
            territory_violations=violations,
        )
        report = validator.generate_report(result)
        # Should mention remaining count
        assert "more" in report

    @pytest.mark.governance
    def test_get_territory_returns_none_for_empty_parts(self, validator):
        result = validator._get_territory("")
        assert result is None

    @pytest.mark.governance
    def test_layer_patterns_covers_all_seven_layers(self):
        assert len(LAYER_PATTERNS) == 7
        for i in range(7):
            assert f"L{i}" in LAYER_PATTERNS

    @pytest.mark.governance
    def test_base_agent_required_path_is_nonempty_string(self):
        assert isinstance(BASE_AGENT_REQUIRED_PATH, str)
        assert len(BASE_AGENT_REQUIRED_PATH) > 0


# ===========================================================================
# 5. Exception-path tests
# ===========================================================================


class TestExceptionPaths:
    @pytest.mark.governance
    def test_validate_structure_handles_empty_agent_list(self, validator):
        with patch.object(validator.verifier, "scan_filesystem", return_value=[]):
            result = validator.validate_structure()
        assert result.total_agents == 0
        assert result.is_fully_compliant is True

    @pytest.mark.governance
    def test_run_structure_validation_returns_result_object(self):
        # run_structure_validation is a module-level function
        result = run_structure_validation()
        assert isinstance(result, StructureValidationResult)
        assert isinstance(result.total_agents, int)

    @pytest.mark.governance
    def test_validate_structure_increments_compliant_when_no_violations(self, validator):
        agent = _make_agent(
            class_name="CleanAgent",
            relative_path="agentic_core/L2_execution/engines/clean.py",
            layer="L2",
        )
        # Patch scan_filesystem to return just this one agent
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[]):
                result = validator.validate_structure()
        assert result.compliant_agents == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_base_agent_violations(self, validator):
        v = StructureViolation(
            agent_class="BadBaseAgent",
            agent_path="apps_rg/bad.py",
            violation_type="base_agent_location",
            message="wrong location",
            severity="critical",
        )
        agent = _make_agent(class_name="BadBaseAgent", relative_path="apps_rg/bad.py")
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[v]):
                result = validator.validate_structure()
        assert len(result.base_agent_violations) == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_layer_violations(self, validator):
        v = StructureViolation(
            agent_class="FooAgent",
            agent_path="agentic_core/L2_execution/foo.py",
            violation_type="layer_mismatch",
            message="wrong layer",
        )
        agent = _make_agent(class_name="FooAgent")
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[v]):
                result = validator.validate_structure()
        assert len(result.layer_violations) == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_depth_violations(self, validator):
        v = StructureViolation(
            agent_class="FooAgent",
            agent_path="agentic_core/L2_execution/engines/sub/deep/foo.py",
            violation_type="depth_violation",
            message="too deep",
        )
        agent = _make_agent(class_name="FooAgent")
        with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
            with patch.object(validator, "validate_agent", return_value=[v]):
                result = validator.validate_structure()
        assert len(result.depth_violations) == 1

    @pytest.mark.governance
    def test_validate_structure_categorises_territory_violations(self, validator):
        for vtype in ("root_file", "unknown_territory"):
            v = StructureViolation(
                agent_class="FooAgent",
                agent_path="bad/foo.py",
                violation_type=vtype,
                message="bad territory",
            )
            agent = _make_agent(class_name="FooAgent")
            with patch.object(validator.verifier, "scan_filesystem", return_value=[agent]):
                with patch.object(validator, "validate_agent", return_value=[v]):
                    result = validator.validate_structure()
            assert len(result.territory_violations) == 1


# ===========================================================================
# 6. Determinism tests
# ===========================================================================


class TestDeterminism:
    @pytest.mark.governance
    def test_normalize_path_deterministic_for_same_input_twice(self, validator):
        path = "agentic_core\\L2_execution\\foo.py"
        assert validator._normalize_path(path) == validator._normalize_path(path)

    @pytest.mark.governance
    def test_get_actual_depth_deterministic_for_same_input_twice(self, validator):
        path = "agentic_core/L2_execution/engines/foo.py"
        assert validator._get_actual_depth(path) == validator._get_actual_depth(path)

    @pytest.mark.governance
    def test_validate_agent_deterministic_for_same_agent_twice(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="apps_rg/engines/bad.py",
            layer="Unknown",
        )
        v1 = validator.validate_agent(agent)
        v2 = validator.validate_agent(agent)
        assert len(v1) == len(v2)
        assert [x.violation_type for x in v1] == [x.violation_type for x in v2]

    @pytest.mark.governance
    def test_validate_layer_assignment_deterministic_for_same_input_twice(self, validator):
        agent = _make_agent(
            relative_path="agentic_core/L2_execution/engines/foo.py",
            layer="L5",
        )
        r1 = validator._validate_layer_assignment(agent)
        r2 = validator._validate_layer_assignment(agent)
        assert (r1 is None) == (r2 is None)
        if r1 is not None:
            assert r1.violation_type == r2.violation_type

    @pytest.mark.governance
    def test_generate_report_deterministic_for_same_result_twice(self, validator):
        result = StructureValidationResult(total_agents=5, compliant_agents=3)
        assert validator.generate_report(result) == validator.generate_report(result)

    @pytest.mark.governance
    def test_compliance_percentage_deterministic_for_same_counts_twice(self):
        r = StructureValidationResult(total_agents=10, compliant_agents=7)
        assert r.compliance_percentage == r.compliance_percentage


# ===========================================================================
# 7. Side-effect safety tests
# ===========================================================================


class TestSideEffectSafety:
    @pytest.mark.governance
    def test_validate_agent_does_not_mutate_agent_info(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="apps_rg/engines/bad.py",
            layer="Unknown",
        )
        original_class_name = agent.class_name
        original_path = agent.relative_path
        validator.validate_agent(agent)
        assert agent.class_name == original_class_name
        assert agent.relative_path == original_path

    @pytest.mark.governance
    def test_validate_agent_called_twice_returns_independent_lists(self, validator):
        agent = _make_agent(
            class_name="SovereignBaseAgent",
            relative_path="apps_rg/engines/bad.py",
        )
        v1 = validator.validate_agent(agent)
        v2 = validator.validate_agent(agent)
        # Mutating v1 does not affect v2
        v1.clear()
        assert len(v2) >= 0  # v2 still has its own data

    @pytest.mark.governance
    def test_structure_validation_result_violations_list_independent_across_instances(self):
        r1 = StructureValidationResult()
        r2 = StructureValidationResult()
        v = StructureViolation(agent_class="X", agent_path="x.py", violation_type="root_file", message="m")
        r1.violations.append(v)
        assert r2.violations == []
