"""
Unified CST Healer Integration Tests

Tests the unified healing orchestration that combines all CST-based
transformations into a single entry point.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.core.unified_cst_healer import (
    HealingConfig,
    HealingResult,
    UnifiedCSTHealer,
)


class TestUnifiedCSTHealer:
    """Test the unified CST healer."""

    def test_healer_initialization(self):
        """Test that the healer initializes correctly."""
        healer = UnifiedCSTHealer()
        assert healer.config is not None
        assert healer.config.enable_import_healing is True

    def test_healer_with_custom_config(self):
        """Test healer with custom configuration."""
        config = HealingConfig(
            enable_import_healing=False,
            enable_docstring_healing=False,
            dry_run=True,
        )
        healer = UnifiedCSTHealer(config)
        assert healer.config.enable_import_healing is False
        assert healer.config.dry_run is True

    def test_heal_file_with_auto_detection(self):
        """Test healing a file with automatic violation detection."""
        source_code = """import os

def test():
    try:
        x = 1 / 0
    except:
        pass
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            healer = UnifiedCSTHealer()
            result = healer.heal_file(temp_path)

            assert result.status == "success"
            assert result.violations_found >= 1  # At least bare except

            healed_content = temp_path.read_text(encoding="utf-8")

            # Check bare except was fixed
            assert "except Exception:" in healed_content
            assert "except:" not in healed_content.replace("except Exception:", "")

            # Check future import was added
            assert "from __future__ import annotations" in healed_content

        finally:
            temp_path.unlink()

    def test_heal_file_dry_run(self):
        """Test dry run mode doesn't modify files."""
        source_code = """def test():
    try:
        x = 1
    except:
        pass
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            config = HealingConfig(dry_run=True)
            healer = UnifiedCSTHealer(config)
            healer.heal_file(temp_path)

            # File should be unchanged
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

        finally:
            temp_path.unlink()

    def test_heal_multiple_files(self):
        """Test healing multiple files at once."""
        source1 = """def func1():
    try:
        pass
    except:
        pass
"""
        source2 = """def func2():
    try:
        pass
    except:
        pass
"""

        temp_files = []
        try:
            for source in [source1, source2]:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, encoding="utf-8"
                ) as f:
                    f.write(source)
                    temp_files.append(Path(f.name))

            healer = UnifiedCSTHealer()
            result = healer.heal_files(temp_files)

            assert result.status == "success"
            assert result.violations_fixed >= 2  # At least 2 bare excepts
            assert len(result.modified_files) == 2

        finally:
            for temp_path in temp_files:
                temp_path.unlink()

    def test_preserves_all_code_elements(self):
        """Test that healing preserves all code elements."""
        source_code = '''#!/usr/bin/env python3
"""Module docstring."""

# Important comment
import os  # OS operations

class MyClass:
    """Class docstring."""

    def method(self):
        # Method comment
        try:
            return os.getcwd()
        except:
            pass
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            healer = UnifiedCSTHealer()
            healer.heal_file(temp_path)

            healed_content = temp_path.read_text(encoding="utf-8")

            # All comments should be preserved
            assert "# Important comment" in healed_content
            assert "# OS operations" in healed_content
            assert "# Method comment" in healed_content

            # Docstrings should be preserved
            assert '"""Module docstring."""' in healed_content
            assert '"""Class docstring."""' in healed_content

            # Code structure should be preserved
            assert "class MyClass:" in healed_content
            assert "def method(self):" in healed_content
            assert "return os.getcwd()" in healed_content

            # Bare except should be fixed
            assert "except Exception:" in healed_content

        finally:
            temp_path.unlink()


class TestHealingConfig:
    """Test healing configuration options."""

    def test_default_config(self):
        """Test default configuration values."""
        config = HealingConfig()
        assert config.enable_import_healing is True
        assert config.enable_docstring_healing is True
        assert config.enable_bare_except_healing is True
        assert config.enable_future_import_healing is True
        assert config.dry_run is False
        assert config.max_blank_lines == 2

    def test_selective_healing(self):
        """Test that only enabled healing types are applied."""
        source_code = """def test():
    try:
        pass
    except:
        pass
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Disable bare except healing
            config = HealingConfig(
                enable_bare_except_healing=False,
                enable_future_import_healing=False,
            )
            healer = UnifiedCSTHealer(config)
            healer.heal_file(temp_path)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Bare except should NOT be fixed
            assert "except:" in healed_content
            assert "except Exception:" not in healed_content

        finally:
            temp_path.unlink()


class TestHealingResult:
    """Test healing result aggregation."""

    def test_result_aggregation(self):
        """Test that results are properly aggregated."""
        result = HealingResult(status="success")
        assert result.violations_found == 0
        assert result.violations_fixed == 0
        assert result.errors == 0
        assert len(result.modified_files) == 0

    def test_partial_status(self):
        """Test partial status when some files fail."""
        source1 = "def test(): pass\n"
        source2 = "invalid python syntax {{{"

        temp_files = []
        try:
            # Create valid file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(source1)
                temp_files.append(Path(f.name))

            # Create invalid file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(source2)
                temp_files.append(Path(f.name))

            healer = UnifiedCSTHealer()
            result = healer.heal_files(temp_files)

            # Should have at least one error
            assert result.errors >= 1

        finally:
            for temp_path in temp_files:
                temp_path.unlink()


class TestTransformerOrdering:
    """Test that transformers are applied in the correct order."""

    def test_future_import_comes_first(self):
        """Test that __future__ import is added before other changes."""
        source_code = """import os

def test():
    pass
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            healer = UnifiedCSTHealer()
            healer.heal_file(temp_path)

            healed_content = temp_path.read_text(encoding="utf-8")
            lines = healed_content.split("\n")

            # Find positions
            future_idx = None
            os_idx = None
            for i, line in enumerate(lines):
                if "__future__" in line:
                    future_idx = i
                if "import os" in line:
                    os_idx = i

            # Future import should come before os import
            if future_idx is not None and os_idx is not None:
                assert future_idx < os_idx

        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
