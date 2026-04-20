"""Tests for SeverityLevel SSOT enum and conversion functions."""

import pytest

_severity = pytest.importorskip(
    "agentic_core.L5_safety.config.severity",
    reason="Requires agentic_core L5 severity module from the monorepo checkout.",
)

SeverityLevel = _severity.SeverityLevel
from_adg_category = _severity.from_adg_category
from_legacy_string = _severity.from_legacy_string
from_ruff_category = _severity.from_ruff_category


class TestSeverityLevelEnum:
    """Test SeverityLevel enum values and properties."""

    def test_enum_values_lowercase(self) -> None:
        """All severity levels use lowercase string values."""
        assert SeverityLevel.CRITICAL.value == "critical"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.INFO.value == "info"

    def test_str_representation(self) -> None:
        """__str__ returns the lowercase value."""
        assert str(SeverityLevel.CRITICAL) == "critical"
        assert str(SeverityLevel.HIGH) == "high"

    def test_p_level_property(self) -> None:
        """p_level returns the canonical P-band from the unified SSOT."""
        assert SeverityLevel.CRITICAL.p_level == "P0"
        assert SeverityLevel.HIGH.p_level == "P1"
        assert SeverityLevel.MEDIUM.p_level == "P2"
        assert SeverityLevel.LOW.p_level == "P3"
        assert SeverityLevel.INFO.p_level == "N/A"

    def test_ruff_category_property(self) -> None:
        """ruff_category returns canonical Ruff P0-P3 categories."""
        assert SeverityLevel.CRITICAL.ruff_category == "P0"
        assert SeverityLevel.HIGH.ruff_category == "P1"
        assert SeverityLevel.MEDIUM.ruff_category == "P2"
        assert SeverityLevel.LOW.ruff_category == "P3"

    def test_adg_category_property(self) -> None:
        """adg_category returns canonical ADG P0-P3 bands (unified with severity_bands SSOT)."""
        assert SeverityLevel.CRITICAL.adg_category == "P0"
        assert SeverityLevel.HIGH.adg_category == "P1"
        assert SeverityLevel.MEDIUM.adg_category == "P2"
        assert SeverityLevel.LOW.adg_category == "P3"


class TestFromRuffCategory:
    """Test from_ruff_category conversion function."""

    def test_ruff_p0_to_critical(self) -> None:
        """Convert Ruff P0 to SeverityLevel.CRITICAL."""
        assert from_ruff_category("P0") == SeverityLevel.CRITICAL

    def test_ruff_p1_to_high(self) -> None:
        """Convert Ruff P1 to SeverityLevel.HIGH."""
        assert from_ruff_category("P1") == SeverityLevel.HIGH

    def test_ruff_p2_to_medium(self) -> None:
        """Convert Ruff P2 to SeverityLevel.MEDIUM."""
        assert from_ruff_category("P2") == SeverityLevel.MEDIUM

    def test_ruff_p3_to_low(self) -> None:
        """Convert Ruff P3 to SeverityLevel.LOW."""
        assert from_ruff_category("P3") == SeverityLevel.LOW

    def test_ruff_invalid_fallback_to_info(self) -> None:
        """Invalid Ruff category gracefully falls back to INFO."""
        assert from_ruff_category("P99") == SeverityLevel.INFO


class TestFromAdgCategory:
    """Test from_adg_category conversion function (canonical P0-P3 mapping)."""

    def test_adg_p0_to_critical(self) -> None:
        """Convert ADG P0 to SeverityLevel.CRITICAL."""
        assert from_adg_category("P0") == SeverityLevel.CRITICAL

    def test_adg_p1_to_high(self) -> None:
        """Convert ADG P1 to SeverityLevel.HIGH."""
        assert from_adg_category("P1") == SeverityLevel.HIGH

    def test_adg_p2_to_medium(self) -> None:
        """Convert ADG P2 to SeverityLevel.MEDIUM."""
        assert from_adg_category("P2") == SeverityLevel.MEDIUM

    def test_adg_p3_to_low(self) -> None:
        """Convert ADG P3 to SeverityLevel.LOW."""
        assert from_adg_category("P3") == SeverityLevel.LOW

    def test_adg_invalid_fallback_to_info(self) -> None:
        """Invalid ADG category gracefully falls back to INFO."""
        assert from_adg_category("P99") == SeverityLevel.INFO

    def test_adg_p4_legacy_fallback_to_info(self) -> None:
        """Legacy ADG P4 (from deprecated P1-P4 mapping) is not canonical -> INFO."""
        assert from_adg_category("P4") == SeverityLevel.INFO


class TestFromLegacyString:
    """Test from_legacy_string conversion function."""

    def test_uppercase_critical(self) -> None:
        """Convert uppercase CRITICAL to SeverityLevel.CRITICAL."""
        assert from_legacy_string("CRITICAL") == SeverityLevel.CRITICAL

    def test_lowercase_critical(self) -> None:
        """Convert lowercase critical to SeverityLevel.CRITICAL."""
        assert from_legacy_string("critical") == SeverityLevel.CRITICAL

    def test_mixed_case_critical(self) -> None:
        """Convert mixed-case Critical to SeverityLevel.CRITICAL."""
        assert from_legacy_string("Critical") == SeverityLevel.CRITICAL

    def test_uppercase_high(self) -> None:
        """Convert uppercase HIGH to SeverityLevel.HIGH."""
        assert from_legacy_string("HIGH") == SeverityLevel.HIGH

    def test_lowercase_high(self) -> None:
        """Convert lowercase high to SeverityLevel.HIGH."""
        assert from_legacy_string("high") == SeverityLevel.HIGH

    def test_uppercase_medium(self) -> None:
        """Convert uppercase MEDIUM to SeverityLevel.MEDIUM."""
        assert from_legacy_string("MEDIUM") == SeverityLevel.MEDIUM

    def test_lowercase_medium(self) -> None:
        """Convert lowercase medium to SeverityLevel.MEDIUM."""
        assert from_legacy_string("medium") == SeverityLevel.MEDIUM

    def test_uppercase_low(self) -> None:
        """Convert uppercase LOW to SeverityLevel.LOW."""
        assert from_legacy_string("LOW") == SeverityLevel.LOW

    def test_lowercase_low(self) -> None:
        """Convert lowercase low to SeverityLevel.LOW."""
        assert from_legacy_string("low") == SeverityLevel.LOW

    def test_uppercase_info(self) -> None:
        """Convert uppercase INFO to SeverityLevel.INFO."""
        assert from_legacy_string("INFO") == SeverityLevel.INFO

    def test_lowercase_info(self) -> None:
        """Convert lowercase info to SeverityLevel.INFO."""
        assert from_legacy_string("info") == SeverityLevel.INFO

    def test_legacy_warning_to_medium(self) -> None:
        """Convert legacy WARNING to SeverityLevel.MEDIUM."""
        assert from_legacy_string("WARNING") == SeverityLevel.MEDIUM

    def test_legacy_error_to_high(self) -> None:
        """Convert legacy ERROR to SeverityLevel.HIGH."""
        assert from_legacy_string("ERROR") == SeverityLevel.HIGH

    def test_invalid_fallback_to_info(self) -> None:
        """Invalid severity string gracefully falls back to INFO."""
        assert from_legacy_string("INVALID") == SeverityLevel.INFO


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_severity_levels_distinct(self) -> None:
        """All severity levels have distinct values."""
        values = {level.value for level in SeverityLevel}
        assert len(values) == 5

    def test_enum_membership(self) -> None:
        """SeverityLevel instances are enum members."""
        assert SeverityLevel.CRITICAL in SeverityLevel
        assert SeverityLevel.HIGH in SeverityLevel
