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

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    CompositeDetector,
    DetectionResult,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.global_mutation_validator import (
    GlobalMutationDetector,
)
from agentic_core.L5_safety.validators.magic_validator import (
    MagicConfigDetector,
)
from agentic_core.L5_safety.validators.path_fragility_validator import (
    PathFragilityDetector,
)
from agentic_core.L5_safety.validators.silent_swallower_validator import (
    SilentSwallowerDetector,
)
from agentic_core.L5_safety.validators.type_erasure_validator import (
    TypeErasureDetector,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


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
def silent_swallower_validator():
    """Create a SilentSwallowerDetector instance."""
    return SilentSwallowerDetector(enforcement_level=EnforcementLevel.WARNING)


@pytest.fixture
def type_erasure_validator():
    """Create a TypeErasureDetector instance."""
    return TypeErasureDetector(
        enforcement_level=EnforcementLevel.WARNING,
        check_agent_classes_only=False,  # Check all classes in tests
    )


@pytest.fixture
def path_fragility_validator():
    """Create a PathFragilityDetector instance."""
    return PathFragilityDetector(enforcement_level=EnforcementLevel.WARNING)


@pytest.fixture
def magic_validator():
    """Create a MagicConfigDetector instance."""
    return MagicConfigDetector(enforcement_level=EnforcementLevel.WARNING)


@pytest.fixture
def global_mutation_validator():
    """Create a GlobalMutationDetector instance."""
    return GlobalMutationDetector(enforcement_level=EnforcementLevel.WARNING)


# ============================================================================
# Silent Swallower Detection Tests
# ============================================================================


class TestSilentSwallowerDetector:
    """Tests for silent exception swallowing detection."""

    def test_detects_bare_except(self, silent_swallower_validator, temp_python_file):
        """Bare except clauses should be detected."""
        code = """
def risky_function():
    try:
        do_something()
    except:
        pass
"""
        file_path = temp_python_file(code)
        result = silent_swallower_validator.scan_file(file_path)

        assert result.has_violations
        assert result.violation_count >= 1
        assert any("bare except" in v.message.lower() for v in result.violations)

    def test_detects_exception_with_pass(self, silent_swallower_validator, temp_python_file):
        """except Exception with only pass should be detected."""
        code = """
def risky_function():
    try:
        do_something()
    except (ValueError, TypeError):
        pass
"""
        file_path = temp_python_file(code)
        result = silent_swallower_validator.scan_file(file_path)

        assert result.has_violations
        assert result.violation_count >= 1

    def test_allows_exception_with_raise(self, silent_swallower_validator, temp_python_file):
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
        result = silent_swallower_validator.scan_file(file_path)

        assert not result.has_violations

    def test_allows_exception_with_return_false(self, silent_swallower_validator, temp_python_file):
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
        result = silent_swallower_validator.scan_file(file_path)

        assert not result.has_violations

    def test_respects_whitelist_comment(self, silent_swallower_validator, temp_python_file):
        """Whitelist comment should suppress detection."""
        code = """
def risky_function():
    try:
        do_something()
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        pass
"""
        file_path = temp_python_file(code)
        result = silent_swallower_validator.scan_file(file_path)

        # Should not have violations due to whitelist
        assert not result.has_violations


# ============================================================================
# Type Erasure Detection Tests
# ============================================================================


class TestTypeErasureDetector:
    """Tests for type erasure detection."""

    def test_detects_dict_return_type(self, type_erasure_validator, temp_python_file):
        """Functions returning dict should be detected."""
        code = """
class TestAgent:
    def process(self, data: str) -> dict:
        return {"result": data}
"""
        file_path = temp_python_file(code)
        result = type_erasure_validator.scan_file(file_path)

        assert result.has_violations
        assert any("dict" in v.message for v in result.violations)

    def test_detects_any_return_type(self, type_erasure_validator, temp_python_file):
        """Functions returning Any should be detected."""
        code = """
from typing import Any

class TestAgent:
    def process(self, data: str) -> Any:
        return data
"""
        file_path = temp_python_file(code)
        result = type_erasure_validator.scan_file(file_path)

        assert result.has_violations
        assert any("Any" in v.message for v in result.violations)

    def test_allows_specific_dict_types(self, type_erasure_validator, temp_python_file):
        """Specific dict types like dict[str, str] should be allowed."""
        code = """
class TestAgent:
    def process(self, data: str) -> dict[str, str]:
        return {"result": data}
"""
        file_path = temp_python_file(code)
        result = type_erasure_validator.scan_file(file_path)

        # dict[str, str] is in allowed types
        assert not result.has_violations

    def test_ignores_private_methods(self, type_erasure_validator, temp_python_file):
        """Private methods should be ignored."""
        code = """
class TestAgent:
    def _internal_process(self, data: str) -> dict:
        return {"result": data}
"""
        file_path = temp_python_file(code)
        result = type_erasure_validator.scan_file(file_path)

        assert not result.has_violations

    def test_ignores_to_dict_methods(self, type_erasure_validator, temp_python_file):
        """to_dict methods should be ignored."""
        code = """
class TestAgent:
    def to_dict(self) -> dict:
        return {"name": self.name}
"""
        file_path = temp_python_file(code)
        result = type_erasure_validator.scan_file(file_path)

        assert not result.has_violations


# ============================================================================
# Path Fragility Detection Tests
# ============================================================================


class TestPathFragilityDetector:
    """Tests for path fragility detection."""

    def test_detects_os_path_join(self, path_fragility_validator, temp_python_file):
        """os.path.join should be detected."""
        code = """
import os

def get_path():
    return os.path.join("base", "subdir", "file.txt")
"""
        file_path = temp_python_file(code)
        result = path_fragility_validator.scan_file(file_path)

        assert result.has_violations
        assert any("os.path.join" in v.message for v in result.violations)

    def test_detects_os_getcwd(self, path_fragility_validator, temp_python_file):
        """os.getcwd should be detected."""
        code = """
import os

def get_current_dir():
    return os.getcwd()
"""
        file_path = temp_python_file(code)
        result = path_fragility_validator.scan_file(file_path)

        assert result.has_violations
        assert any("os.getcwd" in v.message for v in result.violations)

    def test_detects_os_path_exists(self, path_fragility_validator, temp_python_file):
        """os.path.exists should be detected."""
        code = """
import os

def check_file(path):
    return os.path.exists(path)
"""
        file_path = temp_python_file(code)
        result = path_fragility_validator.scan_file(file_path)

        assert result.has_violations
        assert any("os.path.exists" in v.message for v in result.violations)

    def test_allows_pathlib_usage(self, path_fragility_validator, temp_python_file):
        """pathlib.Path usage should NOT be detected."""
        code = """
from pathlib import Path

def get_path():
    return Path("base") / "subdir" / "file.txt"

def check_file(path):
    return Path(path).exists()
"""
        file_path = temp_python_file(code)
        result = path_fragility_validator.scan_file(file_path)

        assert not result.has_violations


# ============================================================================
# Magic Configuration Detection Tests
# ============================================================================


class TestMagicConfigDetector:
    """Tests for magic configuration detection."""

    def test_detects_hardcoded_model_name(self, magic_validator, temp_python_file):
        """Hardcoded model names should be detected."""
        code = """
def get_model():
    model = "gpt-4"
    return model
"""
        file_path = temp_python_file(code)
        result = magic_validator.scan_file(file_path)

        assert result.has_violations
        assert any("model" in v.message.lower() for v in result.violations)

    def test_detects_hardcoded_timeout(self, magic_validator, temp_python_file):
        """Hardcoded timeout values should be detected."""
        code = """
def call_api(timeout=DEFAULT_TIMEOUT):
    pass
"""
        file_path = temp_python_file(code)
        result = magic_validator.scan_file(file_path)

        assert result.has_violations
        assert any("timeout" in v.message.lower() for v in result.violations)

    def test_detects_hardcoded_threshold(self, magic_validator, temp_python_file):
        """Hardcoded threshold values should be detected."""
        code = """
class Validator:
    relevance_threshold = 0.75
"""
        file_path = temp_python_file(code)
        result = magic_validator.scan_file(file_path)

        assert result.has_violations
        assert any("threshold" in v.message.lower() for v in result.violations)

    def test_allows_zero_and_one(self, magic_validator, temp_python_file):
        """0 and 1 should not be flagged as magic numbers."""
        code = """
def initialize():
    count = 0
    enabled = 1
"""
        file_path = temp_python_file(code)
        result = magic_validator.scan_file(file_path)

        # 0 and 1 are allowed
        assert not result.has_violations


# ============================================================================
# Global Mutation Detection Tests
# ============================================================================


class TestGlobalMutationDetector:
    """Tests for global mutation detection."""

    def test_detects_sys_path_insert(self, global_mutation_validator, temp_python_file):
        """sys.path.insert should be detected."""
        code = """
import sys

sys.path.insert(0, "/some/path")
"""
        file_path = temp_python_file(code)
        result = global_mutation_validator.scan_file(file_path)

        assert result.has_violations
        assert any("sys.path.insert" in v.message for v in result.violations)

    def test_detects_sys_path_append(self, global_mutation_validator, temp_python_file):
        """sys.path.append should be detected."""
        code = """
import sys

sys.path.append("/some/path")
"""
        file_path = temp_python_file(code)
        result = global_mutation_validator.scan_file(file_path)

        assert result.has_violations
        assert any("sys.path.append" in v.message for v in result.violations)

    def test_detects_environ_assignment(self, global_mutation_validator, temp_python_file):
        """os.environ['KEY'] = value should be detected."""
        code = """
import os

os.environ["MY_VAR"] = "value"
"""
        file_path = temp_python_file(code)
        result = global_mutation_validator.scan_file(file_path)

        assert result.has_violations
        assert any("os.environ" in v.message for v in result.violations)

    def test_allows_environ_get(self, global_mutation_validator, temp_python_file):
        """os.environ.get should NOT be detected (read-only)."""
        code = """
import os

value = os.environ.get("MY_VAR", "default")
"""
        file_path = temp_python_file(code)
        result = global_mutation_validator.scan_file(file_path)

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
        except (OSError, ValueError):
            pass
"""
        file_path = temp_python_file(code)

        composite = CompositeDetector(
            [
                SilentSwallowerDetector(),
                TypeErasureDetector(check_agent_classes_only=False),
                PathFragilityDetector(),
                GlobalMutationDetector(),
            ],
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
            ],
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
            ],
        )

        # Scan the anti_patterns directory itself (should be clean)
        target_dir = PROJECT_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "validators" / "anti_patterns"

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
    except (ValueError, TypeError):
        pass
"""
        # Create a test file (should be whitelisted by default)
        with tempfile.NamedTemporaryFile(
            mode="w",
            prefix="test_",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(code)
            file_path = Path(f.name)

        detector = SilentSwallowerDetector()
        result = detector.scan_file(file_path)

        # Test files are whitelisted by default
        assert not result.has_violations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================================
# Tier 1 Guardian: base_detector_validator ABC Contract Tests
# AST-graph justification: fan_in=11, ABC base for all concrete detectors;
# if the abstract interface regresses, all 11 consumers silently break.
# ============================================================================


class TestAntiPatternDetectorABCContract:
    """AntiPatternDetector is an ABC — direct instantiation must raise."""

    def test_direct_instantiation_raises_type_error(self):
        with pytest.raises(TypeError):
            AntiPatternDetector()  # type: ignore[abstract]

    def test_concrete_subclass_without_category_raises(self):
        """Subclass missing category property must raise on instantiation."""

        class MissingCategory(AntiPatternDetector):
            def detect(self, file_path, tree):
                return []

        with pytest.raises(TypeError):
            MissingCategory()

    def test_concrete_subclass_without_detect_raises(self):
        """Subclass missing detect() must raise on instantiation."""

        class MissingDetect(AntiPatternDetector):
            @property
            def category(self):
                return AntiPatternCategory.SILENT_SWALLOWER

        with pytest.raises(TypeError):
            MissingDetect()

    def test_concrete_subclass_with_both_abstracts_instantiates(self):
        """Valid concrete subclass must instantiate without error."""

        class MinimalDetector(AntiPatternDetector):
            @property
            def category(self):
                return AntiPatternCategory.SILENT_SWALLOWER

            def detect(self, file_path, tree):
                return []

        detector = MinimalDetector()
        assert detector.category == AntiPatternCategory.SILENT_SWALLOWER


class TestEnforcementLevelOrdering:
    """EnforcementLevel values and ordering contract."""

    def test_all_levels_defined(self):
        levels = {e.value for e in EnforcementLevel}
        assert "disabled" in levels
        assert "warning" in levels
        assert "soft_block" in levels
        assert "hard_block" in levels

    def test_enforcement_level_is_str_enum(self):
        assert isinstance(EnforcementLevel.WARNING, str)
        assert EnforcementLevel.WARNING == "warning"

    def test_hard_block_is_most_restrictive(self):
        levels = list(EnforcementLevel)
        assert levels.index(EnforcementLevel.HARD_BLOCK) > levels.index(EnforcementLevel.DISABLED)

    def test_detector_stores_enforcement_level(self):
        detector = SilentSwallowerDetector(enforcement_level=EnforcementLevel.HARD_BLOCK)
        assert detector.enforcement_level == EnforcementLevel.HARD_BLOCK


class TestDetectionResultContract:
    """DetectionResult field contract and computed properties."""

    def test_empty_result_has_no_violations(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        result = DetectionResult(file_path=p)
        assert result.has_violations is False
        assert result.violation_count == 0

    def test_whitelisted_violations_not_counted(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        v = AntiPatternViolation(
            file_path=p,
            line_number=1,
            category=AntiPatternCategory.SILENT_SWALLOWER,
            message="test",
            evidence="",
            whitelisted=True,
        )
        result = DetectionResult(file_path=p, violations=[v])
        assert result.has_violations is False
        assert result.violation_count == 0

    def test_non_whitelisted_violation_counted(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        v = AntiPatternViolation(
            file_path=p,
            line_number=1,
            category=AntiPatternCategory.TYPE_ERASURE,
            message="type erasure",
            evidence="def foo() -> dict:",
            whitelisted=False,
        )
        result = DetectionResult(file_path=p, violations=[v])
        assert result.has_violations is True
        assert result.violation_count == 1

    def test_error_field_none_by_default(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        result = DetectionResult(file_path=p)
        assert result.error is None

    def test_cached_field_false_by_default(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        result = DetectionResult(file_path=p)
        assert result.cached is False


class TestAntiPatternViolationContract:
    """AntiPatternViolation.to_dict() serialization contract."""

    def test_to_dict_contains_all_required_keys(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        v = AntiPatternViolation(
            file_path=p,
            line_number=5,
            category=AntiPatternCategory.PATH_FRAGILITY,
            message="fragile path",
            evidence="os.path.join(...)",
        )
        d = v.to_dict()
        for key in (
            "file_path",
            "line_number",
            "category",
            "message",
            "evidence",
            "severity",
            "suggested_fix",
            "whitelisted",
            "metadata",
        ):
            assert key in d, f"Missing key in to_dict(): {key}"

    def test_to_dict_category_is_string_value(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        v = AntiPatternViolation(
            file_path=p,
            line_number=1,
            category=AntiPatternCategory.TYPE_ERASURE,
            message="msg",
            evidence="ev",
        )
        d = v.to_dict()
        assert d["category"] == "type_erasure"

    def test_to_dict_file_path_is_string(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        v = AntiPatternViolation(
            file_path=p,
            line_number=1,
            category=AntiPatternCategory.GLOBAL_MUTATION,
            message="msg",
            evidence="ev",
        )
        d = v.to_dict()
        assert isinstance(d["file_path"], str)

    def test_whitelisted_defaults_to_false(self, tmp_path):
        p = tmp_path / "x.py"
        p.write_text("", encoding="utf-8")
        v = AntiPatternViolation(
            file_path=p,
            line_number=1,
            category=AntiPatternCategory.MAGIC_CONFIGURATION,
            message="msg",
            evidence="ev",
        )
        assert v.whitelisted is False


class TestScanFileErrorHandling:
    """scan_file() must be fail-safe — never raises, always returns DetectionResult."""

    def test_nonexistent_file_returns_result_with_error(self, tmp_path):
        detector = SilentSwallowerDetector()
        result = detector.scan_file(tmp_path / "ghost.py")
        assert isinstance(result, DetectionResult)
        # No violations — error path returns empty
        assert result.violation_count == 0

    def test_syntax_error_file_returns_result_not_raise(self, tmp_path):
        p = tmp_path / "broken.py"
        p.write_text("def bad(:\n    pass\n", encoding="utf-8")
        detector = SilentSwallowerDetector()
        result = detector.scan_file(p)
        assert isinstance(result, DetectionResult)
    def test_whitelisted_file_returns_empty_result(self, tmp_path):
        p = tmp_path / "my_module.py"
        p.write_text("try:\n    x()\nexcept Exception:\n    pass\n", encoding="utf-8")
        detector = SilentSwallowerDetector(whitelisted_files=["my_module.py"])
        result = detector.scan_file(p)
        assert result.violation_count == 0
class TestTypeErasureDetectorABCInheritance:
    """TypeErasureDetector correctly inherits and extends AntiPatternDetector."""
    def test_is_subclass_of_anti_pattern_detector(self):
        from agentic_core.L5_safety.validators.type_erasure_validator import TypeErasureDetector
        assert issubclass(TypeErasureDetector, AntiPatternDetector)
    def test_category_returns_type_erasure(self):
        from agentic_core.L5_safety.validators.type_erasure_validator import TypeErasureDetector
        detector = TypeErasureDetector(check_agent_classes_only=False)
        assert detector.category == AntiPatternCategory.TYPE_ERASURE
    def test_category_value_is_string(self):
        from agentic_core.L5_safety.validators.type_erasure_validator import TypeErasureDetector
        detector = TypeErasureDetector()
        assert isinstance(detector.category.value, str)
    def test_allowed_dict_types_are_not_flagged(self, tmp_path):
        from agentic_core.L5_safety.validators.type_erasure_validator import TypeErasureDetector
        p = tmp_path / "my_agent.py"
        p.write_text(
            "class MyAgent:\n    def run(self) -> dict[str, str]:\n        return {}\n",
            encoding="utf-8",
        )
        detector = TypeErasureDetector(check_agent_classes_only=False)
        result = detector.scan_file(p)
        assert result.violation_count == 0