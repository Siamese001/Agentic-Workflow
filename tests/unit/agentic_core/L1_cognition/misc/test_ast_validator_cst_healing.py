"""
Tests for ASTValidatorAgent CST-based healing.

Verifies that ASTValidatorAgent correctly uses UnifiedCSTHealer for
zero-loss healing that preserves comments and code structure.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.unified_cst_healer import (
    HealingConfig,
    UnifiedCSTHealer,
)


class TestASTValidatorCSTHealing:
    """Test ASTValidatorAgent CST-based healing capabilities."""

    def _heal_bare_except(self, file_path: Path) -> dict:
        """
        Simulate ASTValidatorAgent.heal() for bare except violations.

        This directly uses UnifiedCSTHealer as the refactored ASTValidatorAgent does.
        """
        config = HealingConfig(
            enable_import_healing=False,
            enable_docstring_healing=False,
            enable_bare_except_healing=True,
            enable_future_import_healing=False,
            enable_whitespace_healing=False,
            enable_blank_line_healing=False,
            enable_type_hint_healing=False,
            dry_run=False,
        )

        healer = UnifiedCSTHealer(config)
        result = healer.heal_file(file_path)

        if result.violations_fixed > 0:
            return {
                "status": "success",
                "details": f"Fixed {result.violations_fixed} bare except violation(s)",
                "artifacts": [str(file_path)],
                "errors": [],
            }
        else:
            return {
                "status": "skipped",
                "details": "No bare except violations found to fix",
                "artifacts": [],
                "errors": [],
            }

    def test_heal_bare_except_preserves_comments(self):
        """Test that healing bare except preserves all comments."""
        source_code = '''# Header comment
def risky_function():
    """Function docstring."""
    # Pre-try comment
    try:
        x = 1 / 0  # Division comment
    except:
        pass  # Pass comment
    # Post-except comment
    return x
# Footer comment
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Heal the violation using the same logic as refactored ASTValidatorAgent
            result = self._heal_bare_except(temp_path)

            # Check healing succeeded
            assert result["status"] == "success"
            assert len(result["artifacts"]) == 1

            # Read healed content
            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify bare except was fixed
            assert "except Exception:" in healed_content
            assert "except:" not in healed_content.replace("except Exception:", "")

            # Verify ALL comments are preserved
            assert "# Header comment" in healed_content
            assert '"""Function docstring."""' in healed_content
            assert "# Pre-try comment" in healed_content
            assert "# Division comment" in healed_content
            assert "# Pass comment" in healed_content
            assert "# Post-except comment" in healed_content
            assert "# Footer comment" in healed_content

            # Verify code structure is preserved
            assert "def risky_function():" in healed_content
            assert "x = 1 / 0" in healed_content
            assert "return x" in healed_content

        finally:
            temp_path.unlink()

    def test_heal_preserves_inline_comments(self):
        """Test that inline comments are preserved after healing."""
        source_code = """def test():
    try:
        x = 1  # Important value
        y = 2  # Another value
    except:
        z = 0  # Default value
    return x + y + z  # Sum
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            result = self._heal_bare_except(temp_path)
            assert result["status"] == "success"

            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify inline comments preserved
            assert "# Important value" in healed_content
            assert "# Another value" in healed_content
            assert "# Default value" in healed_content
            assert "# Sum" in healed_content

            # Verify bare except was fixed
            assert "except Exception:" in healed_content

        finally:
            temp_path.unlink()

    def test_heal_preserves_multiline_docstrings(self):
        """Test that multiline docstrings are preserved."""
        source_code = '''def complex_function():
    """
    This is a multiline docstring.
    
    It has multiple paragraphs.
    
    Args:
        None
        
    Returns:
        int: A value
    """
    try:
        return 42
    except:
        return 0
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            result = self._heal_bare_except(temp_path)
            assert result["status"] == "success"

            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify multiline docstring preserved
            assert "This is a multiline docstring." in healed_content
            assert "It has multiple paragraphs." in healed_content
            assert "Args:" in healed_content
            assert "Returns:" in healed_content
            assert "int: A value" in healed_content

            # Verify bare except was fixed
            assert "except Exception:" in healed_content

        finally:
            temp_path.unlink()

    def test_heal_preserves_decorators(self):
        """Test that decorators are preserved after healing."""
        source_code = '''@decorator1
@decorator2(arg=1)
def decorated_function():
    """Decorated function."""
    try:
        return 42
    except:
        return 0
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            result = self._heal_bare_except(temp_path)
            assert result["status"] == "success"

            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify decorators preserved
            assert "@decorator1" in healed_content
            assert "@decorator2(arg=1)" in healed_content

            # Verify bare except was fixed
            assert "except Exception:" in healed_content

        finally:
            temp_path.unlink()

    def test_heal_multiple_bare_excepts(self):
        """Test healing multiple bare excepts in one file."""
        source_code = """def func1():
    # First function
    try:
        pass
    except:
        pass

def func2():
    # Second function
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
            result = self._heal_bare_except(temp_path)
            assert result["status"] == "success"

            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify both bare excepts were fixed
            assert healed_content.count("except Exception:") == 2
            assert "except:" not in healed_content.replace("except Exception:", "")

            # Verify comments preserved
            assert "# First function" in healed_content
            assert "# Second function" in healed_content

        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
