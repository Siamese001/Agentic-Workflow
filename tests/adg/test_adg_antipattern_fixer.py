"""Test ADG antipattern fixer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.adg.adg_antipattern_fixer import (
    GuardianCommentFixer,
    _camel_to_kebab,
    _is_canonical,
    _normalize_type,
)


@pytest.mark.unit
class TestAdgAntipatternFixer:
    """Test ADG antipattern fixer functionality."""

    def test_guardian_comment_fixer_class_exists(self):
        """Test GuardianCommentFixer class is defined."""
        assert GuardianCommentFixer is not None
        fixer = GuardianCommentFixer()
        assert fixer is not None

    def test_camel_to_kebab_conversion(self):
        """Test camelCase to kebab-case conversion."""
        assert _camel_to_kebab("camelCase") == "camel-case"
        assert _camel_to_kebab("PascalCase") == "pascal-case"
        assert _camel_to_kebab("simple") == "simple"

    def test_normalize_type_magic_config(self):
        """Test type normalization for magic-config."""
        assert "magic-config" in _normalize_type("allow_magic_config")
        assert "magic-config" in _normalize_type("allow-magic-config")

    def test_normalize_type_bare_except(self):
        """Test type normalization for bare-except."""
        assert "bare-except" in _normalize_type("allow_bare_except")
        assert "bare-except" in _normalize_type("allow-bare-except")

    def test_is_canonical_valid(self):
        """Test canonical format detection."""
        canonical = "    # guardian: allow-magic-config -- valid reason"
        assert _is_canonical(canonical) is True

    def test_is_canonical_invalid(self):
        """Test non-canonical format detection."""
        non_canonical = "    # guardian: allow_magic_config -- valid reason"
        assert _is_canonical(non_canonical) is False

    def test_scan_violations_finds_non_canonical(self):
        """Test scan_violations finds non-canonical comments."""
        fixer = GuardianCommentFixer()
        source = '''
# Some code
# guardian: allow_magic_config -- reason
x = 1
'''
        violations = fixer.scan_violations(source)
        assert len(violations) == 1
        assert violations[0][0] == 3

    def test_fix_source_corrects_non_canonical(self):
        """Test fix_source corrects non-canonical comments."""
        fixer = GuardianCommentFixer()
        source = '# guardian: allow_magic_config -- reason\n'
        fixed, changes, warnings = fixer.fix_source(source)

        assert len(changes) == 1
        assert 'allow-magic-config' in fixed

    def test_fix_source_preserves_line_endings(self):
        """Test fix_source preserves line endings."""
        fixer = GuardianCommentFixer()
        source = '# guardian: allow_magic_config -- reason\r\n'
        fixed, changes, warnings = fixer.fix_source(source)

        assert '\r\n' in fixed
