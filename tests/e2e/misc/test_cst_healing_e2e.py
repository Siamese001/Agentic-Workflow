"""
End-to-End Tests for CST-Based Healing

Comprehensive tests that verify the complete healing pipeline works
correctly from file input to healed output, including all transformers.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.unified_cst_healer import (
    HealingConfig,
    UnifiedCSTHealer,
)


class TestCSTHealingE2E:
    """End-to-end tests for the complete CST healing pipeline."""

    def test_complete_healing_pipeline(self):
        """Test the complete healing pipeline on a realistic file."""
        # A file with multiple issues
        source_code = '''#!/usr/bin/env python3
import os
import unused_module  # This should be removed
import json

class MyClass:
    # Comment inside class
    def risky_method(self):
        try:
            data = json.loads('{}')
            return os.path.join("a", "b")
        except:
            pass

def helper_function():   
    """Helper function."""
    x = 1   
    return x
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            healer = UnifiedCSTHealer()
            result = healer.heal_file(temp_path)

            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify healing occurred
            assert result.status == "success"
            assert result.violations_fixed >= 1

            # Verify __future__ import added
            assert "from __future__ import annotations" in healed_content

            # Verify bare except fixed
            assert "except Exception:" in healed_content
            assert "except:" not in healed_content.replace("except Exception:", "")

            # Verify code structure preserved
            assert "class MyClass:" in healed_content
            assert "def risky_method(self):" in healed_content
            assert "def helper_function():" in healed_content
            assert '"""Helper function."""' in healed_content

            # Verify comments preserved
            assert "# Comment inside class" in healed_content

            # Verify functional code preserved
            assert "json.loads" in healed_content
            assert "os.path.join" in healed_content

        finally:
            temp_path.unlink()

    def test_zero_loss_healing(self):
        """Verify that healing is truly zero-loss."""
        source_code = '''#!/usr/bin/env python3
"""
Module docstring with special characters: @#$%^&*()
And multiple lines.
"""

# Header comment with special chars: <>&'"

import os  # Inline comment

class TestClass:
    """Class with 'quotes' and "double quotes"."""
    
    # Method comment
    def method(self, arg1, arg2):
        """Method docstring."""
        # Body comment
        try:
            result = arg1 + arg2  # Arithmetic
        except:
            pass  # Pass statement
        return result  # Return

# Footer comment
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

            # All comments must be preserved
            assert "# Header comment with special chars:" in healed_content
            assert "# Inline comment" in healed_content
            assert "# Method comment" in healed_content
            assert "# Body comment" in healed_content
            assert "# Arithmetic" in healed_content
            assert "# Pass statement" in healed_content
            assert "# Return" in healed_content
            assert "# Footer comment" in healed_content

            # All docstrings must be preserved
            assert "Module docstring with special characters" in healed_content
            assert "Class with 'quotes'" in healed_content
            assert "Method docstring" in healed_content

            # Code structure must be preserved
            assert "class TestClass:" in healed_content
            assert "def method(self, arg1, arg2):" in healed_content
            assert "result = arg1 + arg2" in healed_content

            # Bare except should be fixed
            assert "except Exception:" in healed_content

        finally:
            temp_path.unlink()

    def test_batch_healing_e2e(self):
        """Test healing multiple files in batch."""
        files_content = [
            """def func1():
    try:
        pass
    except:
        pass
""",
            """def func2():
    try:
        pass
    except:
        pass
""",
            """def func3():
    try:
        pass
    except:
        pass
""",
        ]

        temp_files = []
        try:
            for content in files_content:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, encoding="utf-8"
                ) as f:
                    f.write(content)
                    temp_files.append(Path(f.name))

            healer = UnifiedCSTHealer()
            result = healer.heal_files(temp_files)

            # Verify all files were processed
            assert result.status == "success"
            assert len(result.modified_files) == 3
            assert result.violations_fixed >= 3  # At least 3 bare excepts

            # Verify each file was healed
            for temp_path in temp_files:
                content = temp_path.read_text(encoding="utf-8")
                assert "except Exception:" in content

        finally:
            for temp_path in temp_files:
                temp_path.unlink()

    def test_idempotent_healing(self):
        """Test that healing the same file twice produces the same result."""
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
            healer = UnifiedCSTHealer()

            # First healing
            healer.heal_file(temp_path)
            content_after_first = temp_path.read_text(encoding="utf-8")

            # Second healing
            result2 = healer.heal_file(temp_path)
            content_after_second = temp_path.read_text(encoding="utf-8")

            # Content should be identical after both healings
            assert content_after_first == content_after_second

            # Second healing should find no violations
            assert result2.violations_fixed == 0

        finally:
            temp_path.unlink()

    def test_error_recovery(self):
        """Test that healer handles errors gracefully."""
        healer = UnifiedCSTHealer()

        # Non-existent file
        result = healer.heal_file(Path("/nonexistent/file.py"))
        assert result.status == "error"
        assert result.errors >= 1

    def test_dry_run_mode_e2e(self):
        """Test that dry run mode doesn't modify files."""
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
            config = HealingConfig(dry_run=True)
            healer = UnifiedCSTHealer(config)
            healer.heal_file(temp_path)

            # File should be unchanged
            content = temp_path.read_text(encoding="utf-8")
            assert content == source_code
            assert "except:" in content
            assert "except Exception:" not in content

        finally:
            temp_path.unlink()


class TestHealingPreservation:
    """Tests focused on verifying preservation of code elements."""

    def test_preserves_string_formatting(self):
        """Test that string formatting is preserved."""
        source_code = '''def test():
    s1 = "single quotes"
    s2 = 'double quotes'
    s3 = """triple double"""
    s4 = \'\'\'triple single\'\'\'
    s5 = f"formatted {s1}"
    s6 = r"raw string"
    try:
        pass
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

            content = temp_path.read_text(encoding="utf-8")

            # All string types should be preserved
            assert '"single quotes"' in content
            assert "'double quotes'" in content
            assert '"""triple double"""' in content
            assert "'''triple single'''" in content
            assert 'f"formatted {s1}"' in content
            assert 'r"raw string"' in content

        finally:
            temp_path.unlink()

    def test_preserves_decorators(self):
        """Test that decorators are preserved."""
        source_code = """@decorator1
@decorator2(arg=1)
class MyClass:
    @property
    def prop(self):
        try:
            pass
        except:
            pass
        return self._value

    @staticmethod
    def static_method():
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

            content = temp_path.read_text(encoding="utf-8")

            # All decorators should be preserved
            assert "@decorator1" in content
            assert "@decorator2(arg=1)" in content
            assert "@property" in content
            assert "@staticmethod" in content

        finally:
            temp_path.unlink()

    def test_preserves_complex_expressions(self):
        """Test that complex expressions are preserved."""
        source_code = """def test():
    # List comprehension
    a = [x for x in range(10) if x % 2 == 0]
    
    # Dict comprehension
    b = {k: v for k, v in items.items()}
    
    # Generator expression
    c = (x * 2 for x in range(5))
    
    # Lambda
    d = lambda x, y: x + y
    
    # Walrus operator
    if (n := len(a)) > 5:
        pass
    
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
            healer = UnifiedCSTHealer()
            healer.heal_file(temp_path)

            content = temp_path.read_text(encoding="utf-8")

            # All complex expressions should be preserved
            assert "[x for x in range(10) if x % 2 == 0]" in content
            assert "{k: v for k, v in items.items()}" in content
            assert "(x * 2 for x in range(5))" in content
            assert "lambda x, y: x + y" in content
            assert "(n := len(a))" in content

        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
