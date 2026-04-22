"""Code Formatter Utility - Deterministic code formatting.

This module provides deterministic code formatting functionality previously
implemented in CodeFormatterAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 8 Micro-Wave 5).

Usage:
    from agentic_core.L5_safety.utils.code_formatter_util import (
        CodeFormatter, format_file, format_files
    )

    # Format a file
    result = format_file("path/to/file.py")
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class FormatResult:
    """Result of formatting a file."""

    file_path: Path
    changed: bool
    action: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": str(self.file_path),
            "changed": self.changed,
            "action": self.action,
            "error": self.error,
        }


class CodeFormatter:
    """Deterministic code formatting without agent overhead."""

    def __init__(
        self,
        black_args: list[str] | None = None,
        ruff_args: list[str] | None = None,
    ) -> None:
        """Initialize the code formatter.

        Args:
            black_args: Additional arguments for Black
            ruff_args: Additional arguments for Ruff
        """
        self.black_args = black_args or ["--quiet"]
        self.ruff_args = ruff_args or ["check", "--fix", "--quiet"]

    def format_file(self, file_path: str | Path) -> FormatResult:
        """Format a single file using Black and Ruff.

        Args:
            file_path: Path to the Python file to format

        Returns:
            FormatResult with formatting outcome
        """
        path = Path(file_path)

        if not path.exists():
            return FormatResult(
                file_path=path,
                changed=False,
                error="File not found",
            )

        if not path.suffix == ".py":
            return FormatResult(
                file_path=path,
                changed=False,
                error="Not a Python file",
            )

        changed = False

        # Run Black
        try:
            black_cmd = ["black"] + self.black_args + [str(path)]
            result = subprocess.run(
                black_cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )

            if result.returncode == 0 and "reformatted" in result.stderr:
                changed = True
                Logger.info(f"Black reformatted: {path}")
        except (
            FileNotFoundError
        ):  # guardian: allow-log-and-swallow -- Black optional: not installed, formatter degrades gracefully
            Logger.warning("Black not installed or not in PATH")
        except subprocess.SubprocessError as e:  # guardian: allow-log-and-swallow -- Black subprocess: non-fatal, formatter continues without Black
            Logger.error(f"Black error: {e}")

        # Run Ruff
        try:
            ruff_cmd = ["ruff"] + self.ruff_args + [str(path)]
            result = subprocess.run(
                ruff_cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )

            if result.returncode == 0:
                Logger.debug(f"Ruff check passed: {path}")
        except (
            FileNotFoundError
        ):  # guardian: allow-log-and-swallow -- Ruff optional: not installed, formatter degrades gracefully
            Logger.warning("Ruff not installed or not in PATH")
        except subprocess.SubprocessError as e:  # guardian: allow-log-and-swallow -- Ruff subprocess: non-fatal, formatter continues without Ruff
            Logger.error(f"Ruff error: {e}")

        return FormatResult(
            file_path=path,
            changed=changed,
            action="formatted" if changed else None,
        )

    def format_files(self, file_paths: list[str | Path]) -> list[FormatResult]:
        """Format multiple files.

        Args:
            file_paths: List of file paths to format

        Returns:
            List of FormatResult objects
        """
        return [self.format_file(fp) for fp in file_paths]

    def check_tools_available(self) -> dict[str, bool]:
        """Check if formatting tools are available.

        Returns:
            Dictionary with tool availability status
        """
        tools = {}

        for tool in ["black", "ruff"]:
            try:
                subprocess.run(
                    [tool, "--version"],
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                tools[tool] = True
            except FileNotFoundError:
                tools[tool] = False

        return tools


def format_file(file_path: str | Path, **kwargs: Any) -> dict[str, Any]:
    """Standalone function to format a single file.

    Args:
        file_path: Path to the file
        **kwargs: Additional formatter options

    Returns:
        Dictionary with formatting result
    """
    formatter = CodeFormatter(**kwargs)
    result = formatter.format_file(file_path)
    return result.to_dict()


def format_files(file_paths: list[str | Path], **kwargs: Any) -> list[dict[str, Any]]:
    """Standalone function to format multiple files.

    Args:
        file_paths: List of file paths
        **kwargs: Additional formatter options

    Returns:
        List of formatting results
    """
    formatter = CodeFormatter(**kwargs)
    results = formatter.format_files(file_paths)
    return [r.to_dict() for r in results]


def heal_repository(**kwargs: Any) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance).

    Formatting is a manual operation, not auto-healable.
    """
    return {
        "violations_found": 0,
        "violations_fixed": 0,
        "errors": 0,
        "skipped": 0,
    }


def heal(violation: dict[str, Any]) -> dict[str, Any]:
    """Heal code formatting violations.

    Args:
        violation: Violation dict

    Returns:
        Healing result dict
    """
    violation_type = violation.get("type", "unknown")
    file_path = violation.get("file_path")

    if violation_type == "formatting_violation" and file_path:
        result = format_file(file_path)
        return {
            "status": "success" if result["changed"] else "skipped",
            "details": f"Formatted: {file_path}" if result["changed"] else "No changes needed",
            "artifacts": [file_path] if result["changed"] else [],
            "errors": [result["error"]] if result.get("error") else [],
        }

    return {
        "status": "skipped",
        "details": f"Unknown violation: {violation_type}",
        "artifacts": [],
        "errors": [],
    }


def main():
    """Main entry point for Code Formatter Utility."""
    import argparse

    parser = argparse.ArgumentParser(description="Code Formatter Utility")
    parser.add_argument("files", nargs="+", help="Python files to format")
    parser.add_argument("--check", action="store_true", help="Check tool availability")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    formatter = CodeFormatter()

    if args.check:
        tools = formatter.check_tools_available()
        print("Tool availability:")
        for tool, available in tools.items():
            status = "✓" if available else "✗"
            print(f"  {status} {tool}")
        return

    results = formatter.format_files(args.files)

    changed_count = sum(1 for r in results if r.changed)
    error_count = sum(1 for r in results if r.error)

    print(f"Files processed: {len(results)}")
    print(f"  Changed: {changed_count}")
    print(f"  Errors: {error_count}")

    for r in results:
        if r.changed:
            print(f"  ✓ Formatted: {r.file_path}")
        elif r.error:
            print(f"  ✗ Error ({r.file_path}): {r.error}")


if __name__ == "__main__":
    main()
