"""ADG-driven tests for agentic_core/mixins/safety_mixin.py — fan_in=4.

Covers SafetyAnalysisMixin, HealingMixin, StateAnalysisMixin.
All methods are static — no instance state needed.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.mixins.safety_mixin import HealingMixin, SafetyAnalysisMixin, StateAnalysisMixin


class TestSafetyAnalysisMixinImport:
    def test_all_classes_importable(self):
        assert callable(SafetyAnalysisMixin)
        assert callable(HealingMixin)
        assert callable(StateAnalysisMixin)


class TestCompareThreatLevels:
    def test_low_lt_medium(self):
        assert SafetyAnalysisMixin._compare_threat_levels("LOW", "MEDIUM") == -1

    def test_medium_lt_high(self):
        assert SafetyAnalysisMixin._compare_threat_levels("MEDIUM", "HIGH") == -1

    def test_high_lt_critical(self):
        assert SafetyAnalysisMixin._compare_threat_levels("HIGH", "CRITICAL") == -1

    def test_equal_levels(self):
        assert SafetyAnalysisMixin._compare_threat_levels("HIGH", "HIGH") == 0

    def test_critical_gt_low(self):
        assert SafetyAnalysisMixin._compare_threat_levels("CRITICAL", "LOW") == 1

    def test_case_insensitive(self):
        assert SafetyAnalysisMixin._compare_threat_levels("low", "HIGH") == -1


class TestGenerateRecommendations:
    def test_critical_has_immediate_action(self):
        recs = SafetyAnalysisMixin._generate_recommendations("CRITICAL", {})
        assert any("Immediate" in r for r in recs)

    def test_high_has_24_hour_guidance(self):
        recs = SafetyAnalysisMixin._generate_recommendations("HIGH", {})
        assert any("24" in r for r in recs)

    def test_medium_has_week_guidance(self):
        recs = SafetyAnalysisMixin._generate_recommendations("MEDIUM", {})
        assert any("week" in r.lower() for r in recs)

    def test_low_has_maintenance_guidance(self):
        recs = SafetyAnalysisMixin._generate_recommendations("LOW", {})
        assert any("maintenance" in r.lower() for r in recs)

    def test_large_file_count_adds_recommendation(self):
        recs = SafetyAnalysisMixin._generate_recommendations("LOW", {"file_count": 200})
        assert any("bulk" in r.lower() for r in recs)

    def test_system_critical_adds_recommendation(self):
        recs = SafetyAnalysisMixin._generate_recommendations("HIGH", {"system_critical": True})
        assert any("availability" in r.lower() for r in recs)

    def test_returns_list(self):
        assert isinstance(SafetyAnalysisMixin._generate_recommendations("LOW", {}), list)


class TestMatches:
    def test_exact_match(self):
        assert SafetyAnalysisMixin.matches("foo.py", "foo.py") is True

    def test_no_match(self):
        assert SafetyAnalysisMixin.matches("foo.py", "bar.py") is False

    def test_wildcard_match(self):
        assert SafetyAnalysisMixin.matches("*.py", "foo.py") is True

    def test_wildcard_no_match(self):
        assert SafetyAnalysisMixin.matches("*.py", "foo.txt") is False

    def test_empty_pattern_returns_false(self):
        assert SafetyAnalysisMixin.matches("", "foo.py") is False

    def test_empty_target_returns_false(self):
        assert SafetyAnalysisMixin.matches("*.py", "") is False


class TestHealingMixin:
    def test_import_error_heals(self):
        result = HealingMixin.standard_heal("foo.py", "import_error", {})
        assert result["healed"] is True
        assert result["file_path"] == "foo.py"

    def test_syntax_error_not_healed(self):
        result = HealingMixin.standard_heal("foo.py", "syntax_error", {})
        assert result["healed"] is False
        assert len(result["warnings"]) > 0

    def test_missing_dependency_warning(self):
        result = HealingMixin.standard_heal("foo.py", "missing_dependency", {})
        assert "warnings" in result
        assert len(result["warnings"]) > 0

    def test_unknown_issue_heals(self):
        result = HealingMixin.standard_heal("foo.py", "unknown_issue", {})
        assert result["healed"] is True

    def test_backup_context_adds_action(self):
        result = HealingMixin.standard_heal("foo.py", "import_error", {"backup_available": True})
        assert any("backup" in a.lower() for a in result["actions_taken"])

    def test_result_has_required_keys(self):
        result = HealingMixin.standard_heal("foo.py", "import_error", {})
        for key in ("file_path", "issue_type", "healed", "actions_taken", "warnings"):
            assert key in result


class TestStateAnalysisMixin:
    def test_empty_history_no_failures(self):
        result = StateAnalysisMixin._check_past_failures([])
        assert result["failures_detected"] is False
        assert result["failure_count"] == 0

    def test_counts_failed_states(self):
        history = [{"status": "failed"}, {"status": "failed"}, {"status": "ok"}]
        result = StateAnalysisMixin._check_past_failures(history)
        assert result["failure_count"] == 2

    def test_threshold_exceeded_changes_recommendation(self):
        history = [{"status": "failed"}] * 3
        result = StateAnalysisMixin._check_past_failures(history, failure_threshold=3)
        assert "Change approach" in result["recommendation"] or "escalate" in result["recommendation"].lower()

    def test_below_threshold_retry_with_caution(self):
        history = [{"status": "failed"}]
        result = StateAnalysisMixin._check_past_failures(history, failure_threshold=3)
        assert "caution" in result["recommendation"].lower()

    def test_retry_delay_non_negative(self):
        history = [{"status": "failed"}] * 5
        result = StateAnalysisMixin._check_past_failures(history)
        assert result["retry_delay"] >= 0
