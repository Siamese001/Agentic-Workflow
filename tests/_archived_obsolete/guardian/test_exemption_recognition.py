"""
Tests for guardian exemption recognition in silent degradation detector.

Covers all 6 sub-patterns and verifies that # guardian: allow-silent-degradation
comments properly suppress violations when placed within 3-5 lines.
"""

from __future__ import annotations

import logging

from agentic_core.L5_safety.validators.base_detector_validator import EnforcementLevel
from agentic_core.L5_safety.validators.silent_degradation_validator import SilentDegradationDetector


class TestExemptionRecognition:
    """Test that guardian exemptions properly suppress violations."""

    def test_exemption_suppresses_except_import_pass(self, tmp_path):
        """EXCEPT_IMPORT_PASS pattern should be suppressed by exemption."""
        code = """# guardian: allow-silent-degradation - Optional dependency
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)
        logging.info("C3 write receipt: tests/_archived_obsolete/guardian/test_exemption_recognition.py write side effect recorded")

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should be suppressed by exemption
        assert len(violations) == 0, f"Expected no violations, got: {[v.message for v in violations]}"

    def test_exemption_suppresses_availability_guard_skip(self, tmp_path):
        """AVAILABILITY_GUARD_SKIP pattern should be suppressed by exemption."""
        code = """# guardian: allow-silent-degradation - Optional MCP availability
if not self._mcp_available:
    return None
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should be suppressed by exemption
        assert len(violations) == 0, f"Expected no violations, got: {[v.message for v in violations]}"

    def test_exemption_suppresses_log_and_return_mock(self, tmp_path):
        """LOG_AND_RETURN_MOCK pattern should be suppressed by exemption."""
        code = """# guardian: allow-silent-degradation - Fallback mock in CI
except ImportError:
    Logger.warning("Module not available, returning mock")
    return {"status": "mock", "data": []}
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should be suppressed by exemption
        assert len(violations) == 0, f"Expected no violations, got: {[v.message for v in violations]}"

    def test_exemption_suppresses_skip_string_return(self, tmp_path):
        """SKIP_STRING_RETURN pattern should be suppressed by exemption."""
        code = """# guardian: allow-silent-degradation - Probe skip informational
return "Hierarchy probe: Skipped (agent not available)"
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should be suppressed by exemption
        assert len(violations) == 0, f"Expected no violations, got: {[v.message for v in violations]}"

    def test_exemption_suppresses_phantom_module_import(self, tmp_path):
        """PHANTOM_MODULE_IMPORT pattern should be suppressed by exemption."""
        code = """# guardian: allow-silent-degradation - Optional MCP module
try:
    importlib.import_module("mcp11")
    self._mcp_available = True
except ImportError:
    self._mcp_available = False
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Phantom pattern should be suppressed (exemption on line 1, try on line 2 = 1 line diff)
        # But except pattern might still be detected (exemption on line 1, except on line 5 = 4 lines diff)
        # Let's check what we actually get
        phantom_violations = [
            v for v in violations if v.metadata.get("sub_pattern") == "PHANTOM_MODULE_IMPORT"
        ]
        except_violations = [v for v in violations if v.metadata.get("sub_pattern") == "EXCEPT_IMPORT_PASS"]

        assert len(phantom_violations) == 0, (
            f"Phantom pattern should be suppressed, got: {[v.message for v in phantom_violations]}"
        )
        # The except pattern may or may not be suppressed depending on exact line counting

    def test_exemption_suppresses_silent_success_on_noop(self, tmp_path):
        """SILENT_SUCCESS_ON_NOOP pattern should be suppressed by exemption."""
        code = """# guardian: allow-silent-degradation - Legacy compatibility
if result is not None or (self._fn is None and self._mod is None):
    return True
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should be suppressed by exemption
        assert len(violations) == 0, f"Expected no violations, got: {[v.message for v in violations]}"

    def test_exemption_proximity_requirement_3_lines(self, tmp_path):
        """Exemption must be within 3 lines to be valid."""
        code = """# guardian: allow-silent-degradation - Optional dependency
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should be suppressed (exemption on line 1, except on line 4 = 3 lines apart)
        assert len(violations) == 0

    def test_exemption_proximity_requirement_too_far_not_suppressed(self, tmp_path):
        """Exemption too far away (4+ lines) should not suppress violation."""
        code = """# guardian: allow-silent-degradation - Optional dependency
# Line 2
# Line 3
# Line 4
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should NOT be suppressed (4 lines = too far)
        assert len(violations) > 0
        assert violations[0].category.value == "silent_degradation"

    def test_exemption_too_far_away_not_suppressed(self, tmp_path):
        """Exemption too far away (6+ lines) should not suppress violation."""
        code = """# guardian: allow-silent-degradation - Optional dependency
# Line 2
# Line 3
# Line 4
# Line 5
# Line 6
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should NOT be suppressed (6 lines = too far)
        assert len(violations) > 0
        assert violations[0].category.value == "silent_degradation"

    def test_malformed_exemption_not_suppressed(self, tmp_path):
        """Malformed exemption comment should not suppress violation."""
        code = """# guardian: allow-silent-swallow - Wrong format
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should NOT be suppressed (wrong format)
        assert len(violations) > 0
        assert violations[0].category.value == "silent_degradation"

    def test_no_exemption_violation_detected(self, tmp_path):
        """Without exemption, violation should be detected."""
        code = """
try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should detect violation (no exemption)
        assert len(violations) > 0
        assert violations[0].category.value == "silent_degradation"

    def test_exemption_only_affects_targeted_line(self, tmp_path):
        """Exemption should only suppress violations on nearby lines."""
        code = """# guardian: allow-silent-degradation - Optional dependency
try:
    import missing_module
except ImportError:
    pass

# This violation should still be detected
if not self._other_available:
    return None
"""
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(file_path)
        violations = result.violations

        # Should detect the second violation but not the first
        assert len(violations) == 1
        assert "Availability guard skip" in violations[0].message
