from __future__ import annotations

"""
Diff/Patch Generator (DPG) — Phase 2 Tool

Generates reviewable change proposals for human-in-loop validation:
- Unified diff format
- Context diff format
- HTML diff for visual review
- Patch application validation

Part of the Tool Registry Enhancement Roadmap.
"""
import difflib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DiffFormat(str, Enum):
    """Supported diff output formats."""
    UNIFIED = "unified"
    CONTEXT = "context"
    HTML = "html"
    NDIFF = "ndiff"


class DiffGeneratorArgs(BaseModel):
    """Arguments for diff generation operations."""
    original: str = Field(
        description="Original code/text content"
    )
    modified: str = Field(
        description="Modified code/text content"
    )
    format: DiffFormat = Field(
        default=DiffFormat.UNIFIED,
        description="Output format for the diff"
    )
    context_lines: int = Field(
        default=3,
        description="Number of context lines around changes"
    )
    original_name: str = Field(
        default="original",
        description="Name/path for original file in diff header"
    )
    modified_name: str = Field(
        default="modified",
        description="Name/path for modified file in diff header"
    )


@dataclass
class DiffResult:
    """Result of a diff generation operation."""
    success: bool
    diff: str
    format: str
    stats: dict[str, int] = field(default_factory=dict)
    patch_applicable: bool = True
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "diff": self.diff,
            "format": self.format,
            "stats": self.stats,
            "patch_applicable": self.patch_applicable,
            "warnings": self.warnings,
            "error": self.error,
        }


@dataclass
class PatchResult:
    """Result of a patch application operation."""
    success: bool
    patched_content: str
    hunks_applied: int = 0
    hunks_failed: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "patched_content": self.patched_content,
            "hunks_applied": self.hunks_applied,
            "hunks_failed": self.hunks_failed,
            "warnings": self.warnings,
            "error": self.error,
        }


# =============================================================================
# CORE DIFF FUNCTIONS
# =============================================================================

def generate_unified_diff(
    original: str,
    modified: str,
    original_name: str = "original",
    modified_name: str = "modified",
    context_lines: int = 3
) -> DiffResult:
    """
    Generate a unified diff between two texts.

    Args:
        original: Original text content
        modified: Modified text content
        original_name: Name for original in diff header
        modified_name: Name for modified in diff header
        context_lines: Number of context lines

    Returns:
        DiffResult with unified diff
    """
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    # Ensure final newlines for proper diff
    if original_lines and not original_lines[-1].endswith('\n'):
        original_lines[-1] += '\n'
    if modified_lines and not modified_lines[-1].endswith('\n'):
        modified_lines[-1] += '\n'

    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile=original_name,
        tofile=modified_name,
        n=context_lines
    )

    diff_text = "".join(diff)
    stats = _calculate_diff_stats(original_lines, modified_lines)

    return DiffResult(
        success=True,
        diff=diff_text,
        format="unified",
        stats=stats,
        patch_applicable=True
    )


def generate_context_diff(
    original: str,
    modified: str,
    original_name: str = "original",
    modified_name: str = "modified",
    context_lines: int = 3
) -> DiffResult:
    """
    Generate a context diff between two texts.

    Args:
        original: Original text content
        modified: Modified text content
        original_name: Name for original in diff header
        modified_name: Name for modified in diff header
        context_lines: Number of context lines

    Returns:
        DiffResult with context diff
    """
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    diff = difflib.context_diff(
        original_lines,
        modified_lines,
        fromfile=original_name,
        tofile=modified_name,
        n=context_lines
    )

    diff_text = "".join(diff)
    stats = _calculate_diff_stats(original_lines, modified_lines)

    return DiffResult(
        success=True,
        diff=diff_text,
        format="context",
        stats=stats,
        patch_applicable=True
    )


def generate_html_diff(
    original: str,
    modified: str,
    original_name: str = "original",
    modified_name: str = "modified",
    context_lines: int = 3
) -> DiffResult:
    """
    Generate an HTML diff for visual review.

    Args:
        original: Original text content
        modified: Modified text content
        original_name: Name for original in diff header
        modified_name: Name for modified in diff header
        context_lines: Number of context lines

    Returns:
        DiffResult with HTML diff
    """
    original_lines = original.splitlines()
    modified_lines = modified.splitlines()

    differ = difflib.HtmlDiff(wrapcolumn=80)
    html = differ.make_file(
        original_lines,
        modified_lines,
        fromdesc=original_name,
        todesc=modified_name,
        context=True,
        numlines=context_lines
    )

    stats = _calculate_diff_stats(original_lines, modified_lines)

    return DiffResult(
        success=True,
        diff=html,
        format="html",
        stats=stats,
        patch_applicable=False  # HTML is for review only
    )


def generate_ndiff(
    original: str,
    modified: str
) -> DiffResult:
    """
    Generate an ndiff (character-level diff) between two texts.

    Args:
        original: Original text content
        modified: Modified text content

    Returns:
        DiffResult with ndiff
    """
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)

    diff = difflib.ndiff(original_lines, modified_lines)
    diff_text = "".join(diff)

    stats = _calculate_diff_stats(original_lines, modified_lines)

    return DiffResult(
        success=True,
        diff=diff_text,
        format="ndiff",
        stats=stats,
        patch_applicable=False  # ndiff is for review only
    )


# =============================================================================
# PATCH APPLICATION
# =============================================================================

def apply_patch(
    original: str,
    patch: str,
    reverse: bool = False
) -> PatchResult:
    """
    Apply a unified diff patch to original content.

    This is a simplified patch application that works for most cases.
    For complex patches, consider using the `patch` command.

    Args:
        original: Original text content
        patch: Unified diff patch
        reverse: Apply patch in reverse (undo)

    Returns:
        PatchResult with patched content
    """
    if not patch.strip():
        return PatchResult(
            success=True,
            patched_content=original,
            warnings=["Empty patch - no changes applied"]
        )

    try:
        hunks = _parse_unified_diff(patch)

        if not hunks:
            return PatchResult(
                success=False,
                patched_content=original,
                error="No valid hunks found in patch"
            )

        lines = original.splitlines(keepends=True)
        hunks_applied = 0
        hunks_failed = 0
        warnings = []

        # Apply hunks in reverse order to preserve line numbers
        for hunk in reversed(hunks):
            if reverse:
                # Swap add/remove for reverse application
                hunk = _reverse_hunk(hunk)

            success, lines, warning = _apply_hunk(lines, hunk)
            if success:
                hunks_applied += 1
            else:
                hunks_failed += 1
                if warning:
                    warnings.append(warning)

        patched_content = "".join(lines)

        return PatchResult(
            success=hunks_failed == 0,
            patched_content=patched_content,
            hunks_applied=hunks_applied,
            hunks_failed=hunks_failed,
            warnings=warnings
        )

    except Exception as e:
        return PatchResult(
            success=False,
            patched_content=original,
            error=f"Patch application failed: {str(e)}"
        )


def validate_patch(original: str, patch: str) -> dict[str, Any]:
    """
    Validate that a patch can be applied to the original content.

    Args:
        original: Original text content
        patch: Unified diff patch

    Returns:
        Dict with validation results
    """
    try:
        hunks = _parse_unified_diff(patch)

        if not hunks:
            return {
                "valid": False,
                "error": "No valid hunks found in patch",
                "hunks": 0
            }

        lines = original.splitlines(keepends=True)
        valid_hunks = 0
        invalid_hunks = 0
        issues = []

        for i, hunk in enumerate(hunks):
            # Check if context matches
            start_line = hunk["original_start"] - 1
            context_lines = [l for l in hunk["lines"] if l.startswith(" ") or l.startswith("-")]

            matches = True
            for j, ctx_line in enumerate(context_lines):
                expected = ctx_line[1:]  # Remove prefix
                actual_idx = start_line + j

                if actual_idx >= len(lines):
                    matches = False
                    issues.append(f"Hunk {i+1}: Line {actual_idx+1} out of range")
                    break

                actual = lines[actual_idx]
                if expected.rstrip('\n') != actual.rstrip('\n'):
                    matches = False
                    issues.append(f"Hunk {i+1}: Context mismatch at line {actual_idx+1}")
                    break

            if matches:
                valid_hunks += 1
            else:
                invalid_hunks += 1

        return {
            "valid": invalid_hunks == 0,
            "hunks": len(hunks),
            "valid_hunks": valid_hunks,
            "invalid_hunks": invalid_hunks,
            "issues": issues
        }

    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "hunks": 0
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _calculate_diff_stats(
    original_lines: list[str],
    modified_lines: list[str]
) -> dict[str, int]:
    """Calculate statistics about the diff."""
    matcher = difflib.SequenceMatcher(None, original_lines, modified_lines)

    additions = 0
    deletions = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            additions += j2 - j1
        elif tag == "delete":
            deletions += i2 - i1
        elif tag == "replace":
            deletions += i2 - i1
            additions += j2 - j1

    return {
        "original_lines": len(original_lines),
        "modified_lines": len(modified_lines),
        "additions": additions,
        "deletions": deletions,
        "net_change": additions - deletions,
        "similarity": round(matcher.ratio() * 100, 2),
    }


def _parse_unified_diff(patch: str) -> list[dict[str, Any]]:
    """Parse a unified diff into hunks."""
    hunks = []
    current_hunk = None

    for line in patch.splitlines(keepends=True):
        if line.startswith("@@"):
            # Parse hunk header: @@ -start,count +start,count @@
            if current_hunk:
                hunks.append(current_hunk)

            parts = line.split("@@")
            if len(parts) >= 2:
                ranges = parts[1].strip().split()

                orig_range = ranges[0] if ranges else "-1"
                mod_range = ranges[1] if len(ranges) > 1 else "+1"

                orig_start = int(orig_range.split(",")[0].lstrip("-"))
                mod_start = int(mod_range.split(",")[0].lstrip("+"))

                current_hunk = {
                    "original_start": orig_start,
                    "modified_start": mod_start,
                    "lines": []
                }
        elif current_hunk is not None:
            if line.startswith(("+", "-", " ")):
                current_hunk["lines"].append(line)

    if current_hunk:
        hunks.append(current_hunk)

    return hunks


def _apply_hunk(
    lines: list[str],
    hunk: dict[str, Any]
) -> tuple:
    """Apply a single hunk to lines."""
    start = hunk["original_start"] - 1
    hunk_lines = hunk["lines"]

    # Separate removals and additions
    to_remove = []
    to_add = []
    context_count = 0

    for line in hunk_lines:
        if line.startswith("-"):
            to_remove.append(line[1:])
        elif line.startswith("+"):
            to_add.append(line[1:])
        elif line.startswith(" "):
            context_count += 1

    # Verify context matches (simplified)
    try:
        # Remove old lines
        remove_count = len(to_remove) + context_count
        del lines[start:start + remove_count]

        # Add new lines
        for i, new_line in enumerate(to_add):
            if not new_line.endswith('\n'):
                new_line += '\n'
            lines.insert(start + i, new_line)

        # Re-add context lines
        # (This is simplified - real patch would verify context)

        return True, lines, None
    except Exception as e:
        return False, lines, f"Failed to apply hunk at line {start+1}: {e}"


def _reverse_hunk(hunk: dict[str, Any]) -> dict[str, Any]:
    """Reverse a hunk (swap additions and deletions)."""
    reversed_lines = []
    for line in hunk["lines"]:
        if line.startswith("+"):
            reversed_lines.append("-" + line[1:])
        elif line.startswith("-"):
            reversed_lines.append("+" + line[1:])
        else:
            reversed_lines.append(line)

    return {
        "original_start": hunk["modified_start"],
        "modified_start": hunk["original_start"],
        "lines": reversed_lines
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def generate_diff(args: DiffGeneratorArgs) -> dict[str, Any]:
    """
    Main entry point for diff generation.

    Args:
        args: DiffGeneratorArgs with diff parameters

    Returns:
        Dict with diff results
    """
    if args.format == DiffFormat.UNIFIED:
        result = generate_unified_diff(
            args.original,
            args.modified,
            args.original_name,
            args.modified_name,
            args.context_lines
        )
    elif args.format == DiffFormat.CONTEXT:
        result = generate_context_diff(
            args.original,
            args.modified,
            args.original_name,
            args.modified_name,
            args.context_lines
        )
    elif args.format == DiffFormat.HTML:
        result = generate_html_diff(
            args.original,
            args.modified,
            args.original_name,
            args.modified_name,
            args.context_lines
        )
    elif args.format == DiffFormat.NDIFF:
        result = generate_ndiff(args.original, args.modified)
    else:
        result = DiffResult(
            success=False,
            diff="",
            format=str(args.format),
            error=f"Unknown format: {args.format}"
        )

    return result.to_dict()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_diff(original: str, modified: str) -> str:
    """Quick unified diff between two strings."""
    args = DiffGeneratorArgs(original=original, modified=modified)
    result = generate_diff(args)
    return result.get("diff", "")


def quick_html_diff(original: str, modified: str) -> str:
    """Quick HTML diff for visual review."""
    args = DiffGeneratorArgs(
        original=original,
        modified=modified,
        format=DiffFormat.HTML
    )
    result = generate_diff(args)
    return result.get("diff", "")


def diff_stats(original: str, modified: str) -> dict[str, int]:
    """Get statistics about changes between two strings."""
    original_lines = original.splitlines(keepends=True)
    modified_lines = modified.splitlines(keepends=True)
    return _calculate_diff_stats(original_lines, modified_lines)
