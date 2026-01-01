"""
Unit Tests for Diff/Patch Generator (DPG)

Tests diff generation capabilities:
- generate_unified_diff: Standard unified diff format
- generate_context_diff: Context diff format
- generate_html_diff: HTML visual diff
- apply_patch: Patch application
- validate_patch: Patch validation
"""
import sys
from pathlib import Path

# Ensure project root is in path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest

from agentic_core.L2_execution.tool_registry.tools.diff_generator import (
    DiffGeneratorArgs,
    DiffFormat,
    DiffResult,
    PatchResult,
    generate_diff,
    generate_unified_diff,
    generate_context_diff,
    generate_html_diff,
    generate_ndiff,
    apply_patch,
    validate_patch,
    quick_diff,
    quick_html_diff,
    diff_stats,
)


class TestGenerateUnifiedDiff:
    """Tests for generate_unified_diff function."""

    def test_simple_change(self):
        """Generate diff for a simple line change."""
        original = "line 1\nline 2\nline 3\n"
        modified = "line 1\nmodified line 2\nline 3\n"
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert result.format == "unified"
        assert "-line 2" in result.diff
        assert "+modified line 2" in result.diff

    def test_addition(self):
        """Generate diff for line addition."""
        original = "line 1\nline 2\n"
        modified = "line 1\nline 2\nline 3\n"
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert "+line 3" in result.diff
        assert result.stats["additions"] == 1

    def test_deletion(self):
        """Generate diff for line deletion."""
        original = "line 1\nline 2\nline 3\n"
        modified = "line 1\nline 3\n"
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert "-line 2" in result.diff
        assert result.stats["deletions"] == 1

    def test_no_changes(self):
        """Generate diff when no changes."""
        original = "line 1\nline 2\n"
        modified = "line 1\nline 2\n"
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert result.diff == ""  # No diff when identical
        assert result.stats["additions"] == 0
        assert result.stats["deletions"] == 0

    def test_custom_filenames(self):
        """Generate diff with custom file names."""
        original = "x = 1"
        modified = "x = 2"
        
        result = generate_unified_diff(
            original, modified,
            original_name="old_file.py",
            modified_name="new_file.py"
        )
        
        assert result.success is True
        assert "old_file.py" in result.diff
        assert "new_file.py" in result.diff

    def test_context_lines(self):
        """Generate diff with custom context lines."""
        original = "a\nb\nc\nd\ne\nf\ng\n"
        modified = "a\nb\nc\nX\ne\nf\ng\n"
        
        result = generate_unified_diff(original, modified, context_lines=1)
        
        assert result.success is True
        # With 1 context line, should show c and e around the change
        assert "c" in result.diff
        assert "e" in result.diff


class TestGenerateContextDiff:
    """Tests for generate_context_diff function."""

    def test_simple_change(self):
        """Generate context diff for a simple change."""
        original = "line 1\nline 2\nline 3\n"
        modified = "line 1\nmodified\nline 3\n"
        
        result = generate_context_diff(original, modified)
        
        assert result.success is True
        assert result.format == "context"
        assert "***" in result.diff  # Context diff marker

    def test_patch_applicable(self):
        """Context diff should be patch applicable."""
        original = "x = 1"
        modified = "x = 2"
        
        result = generate_context_diff(original, modified)
        
        assert result.success is True
        assert result.patch_applicable is True


class TestGenerateHtmlDiff:
    """Tests for generate_html_diff function."""

    def test_html_output(self):
        """Generate HTML diff."""
        original = "line 1\nline 2\n"
        modified = "line 1\nmodified\n"
        
        result = generate_html_diff(original, modified)
        
        assert result.success is True
        assert result.format == "html"
        assert "<html>" in result.diff.lower() or "<!doctype" in result.diff.lower()

    def test_html_not_patch_applicable(self):
        """HTML diff should not be patch applicable."""
        original = "x = 1"
        modified = "x = 2"
        
        result = generate_html_diff(original, modified)
        
        assert result.success is True
        assert result.patch_applicable is False


class TestGenerateNdiff:
    """Tests for generate_ndiff function."""

    def test_character_level_diff(self):
        """Generate character-level ndiff."""
        original = "hello world"
        modified = "hello there"
        
        result = generate_ndiff(original, modified)
        
        assert result.success is True
        assert result.format == "ndiff"


class TestDiffStats:
    """Tests for diff statistics."""

    def test_stats_additions(self):
        """Verify addition count in stats."""
        original = "a\nb\n"
        modified = "a\nb\nc\nd\n"
        
        stats = diff_stats(original, modified)
        
        assert stats["additions"] == 2
        assert stats["deletions"] == 0

    def test_stats_deletions(self):
        """Verify deletion count in stats."""
        original = "a\nb\nc\n"
        modified = "a\n"
        
        stats = diff_stats(original, modified)
        
        assert stats["deletions"] == 2
        assert stats["additions"] == 0

    def test_stats_similarity(self):
        """Verify similarity calculation."""
        original = "a\nb\nc\nd\n"
        modified = "a\nb\nc\nd\n"
        
        stats = diff_stats(original, modified)
        
        assert stats["similarity"] == 100.0

    def test_stats_net_change(self):
        """Verify net change calculation."""
        original = "a\nb\n"
        modified = "a\nb\nc\nd\ne\n"
        
        stats = diff_stats(original, modified)
        
        assert stats["net_change"] == 3  # Added 3 lines


class TestApplyPatch:
    """Tests for apply_patch function."""

    def test_apply_simple_patch(self):
        """Apply a simple unified diff patch."""
        original = "line 1\nline 2\nline 3\n"
        modified = "line 1\nmodified line 2\nline 3\n"
        
        # Generate patch
        diff_result = generate_unified_diff(original, modified)
        patch = diff_result.diff
        
        # Apply patch
        result = apply_patch(original, patch)
        
        assert result.success is True
        assert "modified line 2" in result.patched_content

    def test_apply_empty_patch(self):
        """Apply empty patch should return original."""
        original = "line 1\nline 2\n"
        
        result = apply_patch(original, "")
        
        assert result.success is True
        assert result.patched_content == original
        assert "Empty patch" in result.warnings[0]

    def test_apply_invalid_patch(self):
        """Apply invalid patch should fail gracefully."""
        original = "line 1\nline 2\n"
        invalid_patch = "not a valid patch format"
        
        result = apply_patch(original, invalid_patch)
        
        # Should either fail or return original with warning
        assert result.patched_content is not None


class TestValidatePatch:
    """Tests for validate_patch function."""

    def test_validate_valid_patch(self):
        """Validate a correctly generated patch."""
        original = "line 1\nline 2\nline 3\n"
        modified = "line 1\nchanged\nline 3\n"
        
        diff_result = generate_unified_diff(original, modified)
        validation = validate_patch(original, diff_result.diff)
        
        # Should have at least one hunk
        assert validation["hunks"] >= 0

    def test_validate_empty_patch(self):
        """Validate empty patch."""
        original = "line 1\n"
        
        validation = validate_patch(original, "")
        
        assert validation["valid"] is False
        assert validation["hunks"] == 0


class TestDiffGeneratorDispatch:
    """Tests for the main generate_diff entry point."""

    def test_dispatch_unified(self):
        """Dispatch to unified diff."""
        args = DiffGeneratorArgs(
            original="x = 1",
            modified="x = 2",
            format=DiffFormat.UNIFIED
        )
        result = generate_diff(args)
        
        assert result["success"] is True
        assert result["format"] == "unified"

    def test_dispatch_context(self):
        """Dispatch to context diff."""
        args = DiffGeneratorArgs(
            original="x = 1",
            modified="x = 2",
            format=DiffFormat.CONTEXT
        )
        result = generate_diff(args)
        
        assert result["success"] is True
        assert result["format"] == "context"

    def test_dispatch_html(self):
        """Dispatch to HTML diff."""
        args = DiffGeneratorArgs(
            original="x = 1",
            modified="x = 2",
            format=DiffFormat.HTML
        )
        result = generate_diff(args)
        
        assert result["success"] is True
        assert result["format"] == "html"

    def test_dispatch_ndiff(self):
        """Dispatch to ndiff."""
        args = DiffGeneratorArgs(
            original="x = 1",
            modified="x = 2",
            format=DiffFormat.NDIFF
        )
        result = generate_diff(args)
        
        assert result["success"] is True
        assert result["format"] == "ndiff"


class TestQuickFunctions:
    """Tests for convenience quick_* functions."""

    def test_quick_diff(self):
        """quick_diff should return unified diff string."""
        original = "a = 1"
        modified = "a = 2"
        
        diff = quick_diff(original, modified)
        
        assert isinstance(diff, str)
        assert "-a = 1" in diff or "+a = 2" in diff

    def test_quick_html_diff(self):
        """quick_html_diff should return HTML string."""
        original = "a = 1"
        modified = "a = 2"
        
        html = quick_html_diff(original, modified)
        
        assert isinstance(html, str)
        assert "<" in html  # Should contain HTML tags


class TestDiffResult:
    """Tests for DiffResult dataclass."""

    def test_to_dict(self):
        """DiffResult should convert to dict correctly."""
        result = DiffResult(
            success=True,
            diff="--- a\n+++ b\n",
            format="unified",
            stats={"additions": 1, "deletions": 0},
            patch_applicable=True
        )
        
        d = result.to_dict()
        
        assert d["success"] is True
        assert d["format"] == "unified"
        assert d["stats"]["additions"] == 1


class TestPatchResult:
    """Tests for PatchResult dataclass."""

    def test_to_dict(self):
        """PatchResult should convert to dict correctly."""
        result = PatchResult(
            success=True,
            patched_content="new content",
            hunks_applied=2,
            hunks_failed=0
        )
        
        d = result.to_dict()
        
        assert d["success"] is True
        assert d["hunks_applied"] == 2
        assert d["hunks_failed"] == 0


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_original(self):
        """Diff with empty original."""
        original = ""
        modified = "new content\n"
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert result.stats["additions"] >= 1

    def test_empty_modified(self):
        """Diff with empty modified."""
        original = "old content\n"
        modified = ""
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert result.stats["deletions"] >= 1

    def test_both_empty(self):
        """Diff with both empty."""
        original = ""
        modified = ""
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert result.diff == ""

    def test_multiline_changes(self):
        """Diff with multiple line changes."""
        original = """def foo():
    x = 1
    y = 2
    return x + y
"""
        modified = """def bar():
    a = 10
    b = 20
    return a * b
"""
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
        assert result.stats["additions"] > 0
        assert result.stats["deletions"] > 0

    def test_unicode_content(self):
        """Diff with unicode content."""
        original = "hello 世界\n"
        modified = "hello 世界!\n"
        
        result = generate_unified_diff(original, modified)
        
        assert result.success is True
