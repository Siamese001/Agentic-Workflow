"""
Guardian Anti-Pattern Detection Test Suite

Comprehensive tests for all Phase 2 landmine anti-pattern detectors.
These tests validate that anti-patterns are correctly detected and
that false positives are minimized through proper whitelisting.

Run with: pytest tests/guardian/test_anti_patterns.py -v
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.anti_patterns.base_detector import (
    CompositeDetector,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.anti_patterns.global_mutation_detector import (
    GlobalMutationDetector,
)
from agentic_core.L5_safety.validators.anti_patterns.magic_config_detector import (
    MagicConfigDetector,
)
from agentic_core.L5_safety.validators.anti_patterns.path_fragility_detector import (
    PathFragilityDetector,
)
from agentic_core.L5_safety.validators.anti_patterns.silent_swallower_detector import (
    SilentSwallowerDetector,
)
from agentic_core.L5_safety.validators.anti_patterns.type_erasure_detector import (
    TypeErasureDetector,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""

    def _create_file(content: str) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            return Path(f.name)

    return _create_file


@pytest.fixture
def silent_swallower_detector():
    """Create a SilentSwallowerDetector instance."""
    return SilentSwallowerDetector(enforcement_level=EnforcementLevel.WARNING)


@pytest.fixture
def type_erasure_detector():
    """Create a TypeErasureDetector instance."""
    return TypeErasureDetector(
        enforcement_level=EnforcementLevel.WARNING,
        check_agent_classes_only=False,  # Check all classes in tests
    )


@pytest.fixture
def path_fragility_detector():
    """Create a PathFragilityDetector instance."""
    return PathFragilityDetector(enforcement_level=EnforcementLevel.WARNING)


@pytest.fixture
def magic_config_detector():
    """Create a MagicConfigDetector instance."""
    return MagicConfigDetector(enforcement_level=EnforcementLevel.WARNING)


@pytest.fixture
def global_mutation_detector():
    """Create a GlobalMutationDetector instance."""
    return GlobalMutationDetector(enforcement_level=EnforcementLevel.WARNING)


# ============================================================================
# Silent Swallower Detection Tests
# ============================================================================


class TestSilentSwallowerDetector:
    """Tests for silent exception swallowing detection."""

    def test_detects_bare_except(self, silent_swallower_detector, temp_python_file):
        """Bare except clauses should be detected."""
        code = """
def risky_function():
    try:
        do_something()
    except:
        pass
"""
        file_path = temp_python_file(code)
        result = silent_swallower_detector.scan_file(file_path)

        assert result.has_violations
        assert result.violation_count >= 1
        assert any("bare except" in v.message.lower() for v in result.violations)

    def test_detects_exception_with_pass(self, silent_swallower_detector, temp_python_file):
        """except Exception with only pass should be detected."""
        code = """
def risky_function():
    try:
        do_something()
    except Exception:
        pass
"""
        file_path = temp_python_file(code)
        result = silent_swallower_detector.scan_file(file_path)

        assert result.has_violations
        assert result.violation_count >= 1

    def test_allows_exception_with_raise(self, silent_swallower_detector, temp_python_file):
        """except Exception with raise should NOT be detected."""
        code = """
def risky_function():
    try:
        do_something()
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
"""
        file_path = temp_python_file(code)
        result = silent_swallower_detector.scan_file(file_path)

        assert not result.has_violations

    def test_allows_exception_with_return_false(self, silent_swallower_detector, temp_python_file):
        """except Exception with return False should NOT be detected."""
        code = """
def risky_function():
    try:
        do_something()
        return True
    except Exception as e:
        logger.error(f"Error: {e}")
        return False
"""
        file_path = temp_python_file(code)
        result = silent_swallower_detector.scan_file(file_path)

        assert not result.has_violations

    def test_respects_whitelist_comment(self, silent_swallower_detector, temp_python_file):
        """Whitelist comment should suppress detection."""
        code = """
def risky_function():
    try:
        do_something()
    # guardian: allow-silent-swallow
    except Exception:
        pass
"""
        file_path = temp_python_file(code)
        result = silent_swallower_detector.scan_file(file_path)

        # Should not have violations due to whitelist
        assert not result.has_violations


# ============================================================================
# Type Erasure Detection Tests
# ============================================================================


class TestTypeErasureDetector:
    """Tests for type erasure detection."""

    def test_detects_dict_return_type(self, type_erasure_detector, temp_python_file):
        """Functions returning dict should be detected."""
        code = """
class TestAgent:
    def process(self, data: str) -> dict:
        return {"result": data}
"""
        file_path = temp_python_file(code)
        result = type_erasure_detector.scan_file(file_path)

        assert result.has_violations
        assert any("dict" in v.message for v in result.violations)

    def test_detects_any_return_type(self, type_erasure_detector, temp_python_file):
        """Functions returning Any should be detected."""
        code = """
from typing import Any

class TestAgent:
    def process(self, data: str) -> Any:
        return data
"""
        file_path = temp_python_file(code)
        result = type_erasure_detector.scan_file(file_path)

        assert result.has_violations
        assert any("Any" in v.message for v in result.violations)

    def test_allows_specific_dict_types(self, type_erasure_detector, temp_python_file):
        """Specific dict types like dict[str, str] should be allowed."""
        code = """
class TestAgent:
    def process(self, data: str) -> dict[str, str]:
        return {"result": data}
"""
        file_path = temp_python_file(code)
        result = type_erasure_detector.scan_file(file_path)

        # dict[str, str] is in allowed types
        assert not result.has_violations

    def test_ignores_private_methods(self, type_erasure_detector, temp_python_file):
        """Private methods should be ignored."""
        code = """
class TestAgent:
    def _internal_process(self, data: str) -> dict:
        return {"result": data}
"""
        file_path = temp_python_file(code)
        result = type_erasure_detector.scan_file(file_path)

        assert not result.has_violations

    def test_ignores_to_dict_methods(self, type_erasure_detector, temp_python_file):
        """to_dict methods should be ignored."""
        code = """
class TestAgent:
    def to_dict(self) -> dict:
        return {"name": self.name}
"""
        file_path = temp_python_file(code)
        result = type_erasure_detector.scan_file(file_path)

        assert not result.has_violations


# ============================================================================
# Path Fragility Detection Tests
# ============================================================================


class TestPathFragilityDetector:
    """Tests for path fragility detection."""

    def test_detects_os_path_join(self, path_fragility_detector, temp_python_file):
        """os.path.join should be detected."""
        code = """
import os

def get_path():
    return os.path.join("base", "subdir", "file.txt")
"""
        file_path = temp_python_file(code)
        result = path_fragility_detector.scan_file(file_path)

        assert result.has_violations
        assert any("os.path.join" in v.message for v in result.violations)

    def test_detects_os_getcwd(self, path_fragility_detector, temp_python_file):
        """os.getcwd should be detected."""
        code = """
import os

def get_current_dir():
    return os.getcwd()
"""
        file_path = temp_python_file(code)
        result = path_fragility_detector.scan_file(file_path)

        assert result.has_violations
        assert any("os.getcwd" in v.message for v in result.violations)

    def test_detects_os_path_exists(self, path_fragility_detector, temp_python_file):
        """os.path.exists should be detected."""
        code = """
import os

def check_file(path):
    return os.path.exists(path)
"""
        file_path = temp_python_file(code)
        result = path_fragility_detector.scan_file(file_path)

        assert result.has_violations
        assert any("os.path.exists" in v.message for v in result.violations)

    def test_allows_pathlib_usage(self, path_fragility_detector, temp_python_file):
        """pathlib.Path usage should NOT be detected."""
        code = """
from pathlib import Path

def get_path():
    return Path("base") / "subdir" / "file.txt"

def check_file(path):
    return Path(path).exists()
"""
        file_path = temp_python_file(code)
        result = path_fragility_detector.scan_file(file_path)

        assert not result.has_violations


# ============================================================================
# Magic Configuration Detection Tests
# ============================================================================


class TestMagicConfigDetector:
    """Tests for magic configuration detection."""

    def test_detects_hardcoded_model_name(self, magic_config_detector, temp_python_file):
        """Hardcoded model names should be detected."""
        code = """
def get_model():
    model = "gpt-4"
    return model
"""
        file_path = temp_python_file(code)
        result = magic_config_detector.scan_file(file_path)

        assert result.has_violations
        assert any("model" in v.message.lower() for v in result.violations)

    def test_detects_hardcoded_timeout(self, magic_config_detector, temp_python_file):
        """Hardcoded timeout values should be detected."""
        code = """
def call_api(timeout=30):
    pass
"""
        file_path = temp_python_file(code)
        result = magic_config_detector.scan_file(file_path)

        assert result.has_violations
        assert any("timeout" in v.message.lower() for v in result.violations)

    def test_detects_hardcoded_threshold(self, magic_config_detector, temp_python_file):
        """Hardcoded threshold values should be detected."""
        code = """
class Validator:
    relevance_threshold = 0.75
"""
        file_path = temp_python_file(code)
        result = magic_config_detector.scan_file(file_path)

        assert result.has_violations
        assert any("threshold" in v.message.lower() for v in result.violations)

    def test_allows_zero_and_one(self, magic_config_detector, temp_python_file):
        """0 and 1 should not be flagged as magic numbers."""
        code = """
def initialize():
    count = 0
    enabled = 1
"""
        file_path = temp_python_file(code)
        result = magic_config_detector.scan_file(file_path)

        # 0 and 1 are allowed
        assert not result.has_violations


# ============================================================================
# Global Mutation Detection Tests
# ============================================================================


class TestGlobalMutationDetector:
    """Tests for global mutation detection."""

    def test_detects_sys_path_insert(self, global_mutation_detector, temp_python_file):
        """sys.path.insert should be detected."""
        code = """
import sys

sys.path.insert(0, "/some/path")
"""
        file_path = temp_python_file(code)
        result = global_mutation_detector.scan_file(file_path)

        assert result.has_violations
        assert any("sys.path.insert" in v.message for v in result.violations)

    def test_detects_sys_path_append(self, global_mutation_detector, temp_python_file):
        """sys.path.append should be detected."""
        code = """
import sys

sys.path.append("/some/path")
"""
        file_path = temp_python_file(code)
        result = global_mutation_detector.scan_file(file_path)

        assert result.has_violations
        assert any("sys.path.append" in v.message for v in result.violations)

    def test_detects_environ_assignment(self, global_mutation_detector, temp_python_file):
        """os.environ['KEY'] = value should be detected."""
        code = """
import os

os.environ["MY_VAR"] = "value"
"""
        file_path = temp_python_file(code)
        result = global_mutation_detector.scan_file(file_path)

        assert result.has_violations
        assert any("os.environ" in v.message for v in result.violations)

    def test_allows_environ_get(self, global_mutation_detector, temp_python_file):
        """os.environ.get should NOT be detected (read-only)."""
        code = """
import os

value = os.environ.get("MY_VAR", "default")
"""
        file_path = temp_python_file(code)
        result = global_mutation_detector.scan_file(file_path)

        assert not result.has_violations


# ============================================================================
# Composite Detector Tests
# ============================================================================


class TestCompositeDetector:
    """Tests for the composite detector that combines all detectors."""

    def test_composite_detects_multiple_patterns(self, temp_python_file):
        """Composite detector should detect violations from all categories."""
        code = """
import os
import sys

class BadAgent:
    def process(self, data: str) -> dict:
        try:
            sys.path.insert(0, os.getcwd())
            return {"result": data}
        except Exception:
            pass
"""
        file_path = temp_python_file(code)

        composite = CompositeDetector(
            [
                SilentSwallowerDetector(),
                TypeErasureDetector(check_agent_classes_only=False),
                PathFragilityDetector(),
                GlobalMutationDetector(),
            ]
        )

        results = composite.scan_file(file_path)

        # Should have results from multiple detectors
        assert len(results) > 0

        # Check that we have violations from different categories
        categories = set()
        for result in results:
            for violation in result.violations:
                if not violation.whitelisted:
                    categories.add(violation.category)

        # Should detect at least 2 different categories
        assert len(categories) >= 2

    def test_composite_generates_summary(self, temp_python_file):
        """Composite detector should generate accurate summary statistics."""
        code = """
import os

def bad_function():
    return os.path.join("a", "b")
"""
        file_path = temp_python_file(code)

        composite = CompositeDetector(
            [
                PathFragilityDetector(),
            ]
        )

        results = composite.scan_directory(
            file_path.parent,
            include_patterns=[file_path.name],
        )

        summary = composite.get_summary(results)

        assert "total_files_scanned" in summary
        assert "total_violations" in summary
        assert "violations_by_category" in summary


# ============================================================================
# Integration Tests
# ============================================================================


class TestAntiPatternIntegration:
    """Integration tests for anti-pattern detection."""

    def test_scan_real_codebase_directory(self):
        """Test scanning a real directory in the codebase."""
        composite = CompositeDetector(
            [
                SilentSwallowerDetector(),
                TypeErasureDetector(),
                PathFragilityDetector(),
                MagicConfigDetector(),
                GlobalMutationDetector(),
            ]
        )

        # Scan the anti_patterns directory itself (should be clean)
        target_dir = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "anti_patterns"

        if target_dir.exists():
            results = composite.scan_directory(target_dir)
            summary = composite.get_summary(results)

            # Just verify it runs without error
            assert "total_files_scanned" in summary
            assert summary["total_files_scanned"] > 0

    def test_enforcement_levels(self):
        """Test that enforcement levels are properly set."""
        detector = SilentSwallowerDetector(enforcement_level=EnforcementLevel.HARD_BLOCK)

        assert detector.enforcement_level == EnforcementLevel.HARD_BLOCK

    def test_whitelisted_files(self, temp_python_file):
        """Test that whitelisted file patterns work."""
        code = """
def bad_function():
    try:
        do_something()
    except Exception:
        pass
"""
        # Create a test file (should be whitelisted by default)
        with tempfile.NamedTemporaryFile(
            mode="w", prefix="test_", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            file_path = Path(f.name)

        detector = SilentSwallowerDetector()
        result = detector.scan_file(file_path)

        # Test files are whitelisted by default
        assert not result.has_violations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
