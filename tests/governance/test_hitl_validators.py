"""
Tests for HITL validator scripts:
  - ops_scripts/ci/validate_hitl_rules.py
  - ops_scripts/ci/validate_hitl_format.py

Coverage: happy path, failure path, edge case for each validator function.
"""
import logging
import sys
import textwrap
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path bootstrap — make ops_scripts importable from the repo root
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ops_scripts.ci.validate_hitl_format import validate_file
from ops_scripts.ci.validate_hitl_rules import (
    validate_no_hardcoded_2to4,
    validate_option_shape_section,
    validate_yaml_config_section,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_md(tmp_path):
    """Return a factory that writes content to a .md file and returns its Path."""

    def _make(content: str, name: str = "test.md") -> Path:
        p = tmp_path / name
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        logging.info("C3 write receipt: tests/governance/test_hitl_validators.py write side effect recorded")
        return p

    return _make


# ---------------------------------------------------------------------------
# validate_yaml_config_section
# ---------------------------------------------------------------------------


class TestValidateYamlConfigSection:
    def test_happy_valid_hitl9_block(self, tmp_md):
        """Happy: §HITL-9 present with all required keys → no errors."""
        content = """\
            ## §HITL-9: Confidence Policy Configuration

            ```yaml
            hitl_option_policy:
              surface_threshold: 0.72
              dominance_score_threshold: 0.85
              dominance_delta: 0.12
              allow_single_option_hitl: true
            ```
        """
        errors = validate_yaml_config_section(tmp_md(content))
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_failure_missing_hitl9_section(self, tmp_md):
        """Failure: file has no §HITL-9 section → error reported."""
        content = "## §HITL-0: Core Principle\n\nSome content.\n"
        errors = validate_yaml_config_section(tmp_md(content))
        assert any("§HITL-9 section not found" in e for e in errors)

    def test_failure_missing_required_key(self, tmp_md):
        """Failure: §HITL-9 present but dominance_delta omitted → specific error."""
        content = """\
            ## §HITL-9: Confidence Policy Configuration

            ```yaml
            hitl_option_policy:
              surface_threshold: 0.72
              dominance_score_threshold: 0.85
              allow_single_option_hitl: true
            ```
        """
        errors = validate_yaml_config_section(tmp_md(content))
        assert any("dominance_delta: 0.12" in e for e in errors)

    def test_edge_missing_yaml_fence(self, tmp_md):
        """Edge: §HITL-9 section exists with keys but no ```yaml``` fence → error."""
        content = """\
            ## §HITL-9: Confidence Policy Configuration

            surface_threshold: 0.72
            dominance_score_threshold: 0.85
            dominance_delta: 0.12
            allow_single_option_hitl: true
        """
        errors = validate_yaml_config_section(tmp_md(content))
        assert any("YAML config block not found" in e for e in errors)


# ---------------------------------------------------------------------------
# validate_option_shape_section
# ---------------------------------------------------------------------------


class TestValidateOptionShapeSection:
    def test_happy_all_fields_present(self, tmp_md):
        """Happy: §HITL-10 with all required fields → no errors."""
        content = """\
            ## §HITL-10: Option Shape Contract

            ```
            decision_thesis:
            value_to_goal:
            key_tradeoffs:
            execution_impact:
            risk_profile:
            time_to_value:
            ```
        """
        errors = validate_option_shape_section(tmp_md(content))
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_failure_no_hitl10_section(self, tmp_md):
        """Failure: file lacks §HITL-10 entirely → error."""
        content = "## §HITL-9: Config\n\nsome content\n"
        errors = validate_option_shape_section(tmp_md(content))
        assert any("§HITL-10 section not found" in e for e in errors)

    def test_failure_missing_field(self, tmp_md):
        """Failure: §HITL-10 present but risk_profile omitted → specific error."""
        content = """\
            ## §HITL-10: Option Shape Contract

            decision_thesis:
            value_to_goal:
            key_tradeoffs:
            execution_impact:
            time_to_value:
        """
        errors = validate_option_shape_section(tmp_md(content))
        assert any("risk_profile" in e for e in errors)

    def test_edge_hitl10_immediately_followed_by_hitl11(self, tmp_md):
        """Edge: §HITL-10 section ends exactly at §HITL-11 — section boundary parsed correctly."""
        content = """\
            ## §HITL-10: Option Shape Contract

            decision_thesis:
            value_to_goal:
            key_tradeoffs:
            execution_impact:
            risk_profile:
            time_to_value:

            ## §HITL-11: Telemetry

            Some telemetry content.
        """
        errors = validate_option_shape_section(tmp_md(content))
        assert errors == [], f"Expected no errors, got: {errors}"


# ---------------------------------------------------------------------------
# validate_no_hardcoded_2to4
# ---------------------------------------------------------------------------


class TestValidateNoHardcoded2to4:
    def test_happy_clean_new_format(self, tmp_md):
        """Happy: new-format content with all required patterns, no forbidden ones → no errors."""
        content = """\
            surface_threshold = 0.72
            The dominance rule fires when gap >= 0.12.
            Surface 1\u2013N options to the user.
            LOW_CONFIDENCE_AMBIGUITY packet emitted when nothing clears threshold.
        """
        errors = validate_no_hardcoded_2to4(tmp_md(content))
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_failure_forbidden_pattern_present(self, tmp_md):
        """Failure: old 'Present 2-4 concrete options' text present → error."""
        content = """\
            Present 2-4 concrete options with trade-offs.
            surface_threshold = 0.72
            dominance rule
            Surface 1\u2013N options
            LOW_CONFIDENCE_AMBIGUITY
        """
        errors = validate_no_hardcoded_2to4(tmp_md(content))
        assert any("Present 2-4 concrete options" in e for e in errors)

    def test_failure_forbidden_options_24(self, tmp_md):
        """Failure: old 'Options (2-4)' text present → error."""
        content = """\
            Options (2-4): each with label and description.
            surface_threshold = 0.72
            dominance rule
            Surface 1\u2013N options
            LOW_CONFIDENCE_AMBIGUITY
        """
        errors = validate_no_hardcoded_2to4(tmp_md(content))
        assert any("Options \\(2-4\\)" in e for e in errors)

    def test_failure_missing_required_pattern(self, tmp_md):
        """Failure: LOW_CONFIDENCE_AMBIGUITY missing → error."""
        content = """\
            surface_threshold = 0.72
            dominance rule
            Surface 1\u2013N options
        """
        errors = validate_no_hardcoded_2to4(tmp_md(content))
        assert any("LOW_CONFIDENCE_AMBIGUITY" in e for e in errors)

    def test_failure_missing_en_dash_pattern(self, tmp_md):
        """Failure: 'Surface 1-N options' with hyphen instead of en-dash → missing required pattern."""
        content = """\
            surface_threshold = 0.72
            dominance rule
            Surface 1-N options
            LOW_CONFIDENCE_AMBIGUITY
        """
        errors = validate_no_hardcoded_2to4(tmp_md(content))
        # en-dash variant must be present; hyphen variant does NOT satisfy the check
        assert any("Surface 1\u2013N options" in e for e in errors)

    def test_edge_forbidden_and_missing_simultaneously(self, tmp_md):
        """Edge: both a forbidden pattern present AND a required pattern absent → both errors reported."""
        content = "Present 2-4 concrete options\ndominance rule\nLOW_CONFIDENCE_AMBIGUITY\n"
        errors = validate_no_hardcoded_2to4(tmp_md(content))
        forbidden_hit = any("Present 2-4 concrete options" in e for e in errors)
        missing_hit = any("surface_threshold = 0.72" in e for e in errors)
        assert forbidden_hit and missing_hit


# ---------------------------------------------------------------------------
# validate_file (validate_hitl_format.py)
# ---------------------------------------------------------------------------


class TestValidateFile:
    def test_happy_compliant_new_format(self, tmp_md):
        """Happy: file with well-formed §HITL-10 ask_user_question block → no violations."""
        content = """\
            ask_user_question(
              question=\"\"\"Recommended: Root-cause fix
            Why it wins: Only path that addresses root cause.
            What you are optimizing for: Accurate analysis.
            What is being traded off: 45 min investigation.
            Candidates evaluated: 3 | Surfaced: 1 | Suppressed (low confidence): 2 | Suppressed (non-distinct): 0\"\"\",
              options=[
                {
                  label: "⭐ Option A [0.91 HIGH]",
                  description: "decision_thesis: Fixes the root cause at source."
                }
              ],
              allowMultiple=false
            )
        """
        violations = validate_file(tmp_md(content))
        assert violations == [], f"Expected no violations, got: {violations}"

    def test_failure_banned_pros_pattern(self, tmp_md):
        """Failure: file contains **Pros**: → BANNED_OLD_FORMAT violation."""
        content = """\
            **Pros**: Fast implementation, easy rollback.
            **Cons**: Increases debt.
        """
        violations = validate_file(tmp_md(content))
        issue_types = [v[1] for v in violations]
        assert "BANNED_OLD_FORMAT" in issue_types

    def test_failure_missing_confidence_score_in_label(self, tmp_md):
        """Failure: ask_user_question block with label but no [0.NN HIGH|MEDIUM] → MISSING_CONFIDENCE_SCORE."""
        content = """\
            ask_user_question(
              question=\"\"\"Recommended: Fix
            Why it wins: best path.
            What you are optimizing for: speed.
            What is being traded off: scope.
            Candidates evaluated: 2 | Surfaced: 1 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0\"\"\",
              options=[
                {
                  label: "Option A",
                  description: "decision_thesis: Does X."
                }
              ]
            )
        """
        violations = validate_file(tmp_md(content))
        issue_types = [v[1] for v in violations]
        assert "MISSING_CONFIDENCE_SCORE" in issue_types

    def test_failure_missing_decision_thesis(self, tmp_md):
        """Failure: ask_user_question block with description but no decision_thesis: → MISSING_DECISION_THESIS."""
        content = """\
            ask_user_question(
              question=\"\"\"Recommended: Fix
            Why it wins: best path.
            What you are optimizing for: speed.
            What is being traded off: scope.
            Candidates evaluated: 2 | Surfaced: 1 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0\"\"\",
              options=[
                {
                  label: "Option A [0.88 HIGH]",
                  description: "Fixes the problem quickly."
                }
              ]
            )
        """
        violations = validate_file(tmp_md(content))
        issue_types = [v[1] for v in violations]
        assert "MISSING_DECISION_THESIS" in issue_types

    def test_edge_no_ask_user_question_block(self, tmp_md):
        """Edge: file with no ask_user_question block → no violations (clean doc)."""
        content = "# Some plan\n\nNo HITL blocks here.\n"
        violations = validate_file(tmp_md(content))
        assert violations == [], f"Expected no violations, got: {violations}"

    def test_edge_inline_pros_in_prose_flagged(self, tmp_md):
        """Edge: 'Pros: ' appearing inline in prose (not in a block) is still flagged as banned."""
        content = "The option has Pros: fast and Cons: risky.\n"
        violations = validate_file(tmp_md(content))
        issue_types = [v[1] for v in violations]
        assert "BANNED_OLD_FORMAT" in issue_types
