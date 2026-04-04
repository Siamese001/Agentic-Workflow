#!/usr/bin/env python3
"""
Zero-Loss Refactor Verifier

Checks modified files for neutered content after refactoring.
Ensures that files don't lose all behavioral content during cleanup.
"""

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

from agentic_core.L5_safety.validators.hollow_file_detector_validator import (
    HollowFileClassification,
    HollowFileDetector,
)


def count_behavioral_nodes(tree: ast.AST) -> int:
    """Count behavioral nodes (functions, classes with methods) in AST."""
    detector = HollowFileDetector()
    counter = detector._node_counter
    counter.reset()
    counter.visit(tree)
    return counter.behavioral_functions + counter.behavioral_classes


def git_show(commit_hash: str, file_path: Path) -> str:
    """Get file content at specific commit."""
    try:
        result = subprocess.run(
            ["git", "show", f"{commit_hash}:{file_path}"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        # File might not exist at that commit
        return ""


def parse_ast(content: str) -> ast.AST | None:
    """Parse AST from content, return None on failure."""
    if not content.strip():
        return None
    try:
        return ast.parse(content)
    except SyntaxError:
        return None


def check_file_neutered(file_path: Path, before_hash: str, after_hash: str = "HEAD") -> tuple[bool, int, int]:
    """Check if file lost all behavioral content in refactor.

    Returns:
        (is_neutered, before_count, after_count)
    """
    # Get before content
    before_content = git_show(before_hash, file_path)
    before_tree = parse_ast(before_content)
    before_behavioral = count_behavioral_nodes(before_tree) if before_tree else 0

    # Get after content
    try:
        after_content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        after_content = ""
    after_tree = parse_ast(after_content)
    after_behavioral = count_behavioral_nodes(after_tree) if after_tree else 0

    # Check if neutered
    is_neutered = before_behavioral > 0 and after_behavioral == 0

    return is_neutered, before_behavioral, after_behavioral


def get_modified_files_since(base_hash: str) -> list[Path]:
    """Get list of modified Python files since base commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMRT", f"{base_hash}...HEAD", "*.py"],
            capture_output=True,
            text=True,
            check=True
        )
        return [Path(f.strip()) for f in result.stdout.strip().split('\n') if f.strip()]
    except subprocess.CalledProcessError:
        return []


def check_files_neutered(files: list[Path], base_hash: str) -> dict[Path, dict]:
    """Check multiple files for neutered content."""
    results = {}

    for file_path in files:
        if not file_path.exists():
            continue

        is_neutered, before_count, after_count = check_file_neutered(file_path, base_hash)

        results[file_path] = {
            "neutered": is_neutered,
            "before_behavioral": before_count,
            "after_behavioral": after_count,
            "action": None
        }

        if is_neutered:
            # Suggest cleanup action
            if after_count == 0 and before_count > 0:
                results[file_path]["action"] = "DELETE"
            else:
                results[file_path]["action"] = "REVIEW"

    return results


def generate_cleanup_commands(neutered_files: list[Path]) -> list[str]:
    """Generate git commands for cleaning up neutered files."""
    commands = []

    for file_path in neutered_files:
        rel_path = str(file_path).replace("\\", "/")
        commands.append(f"git rm {rel_path}")
        commands.append(f"# Removed hollow file: {rel_path}")

    return commands


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify zero-loss refactoring")
    parser.add_argument("--base", default="HEAD~1", help="Base commit to compare against")
    parser.add_argument("--strict", action="store_true", help="Exit with error if neutered files found")
    parser.add_argument("--report", type=Path, help="Write report to JSON file")
    parser.add_argument("--changed-only", action="store_true", help="Only check files changed since base")
    parser.add_argument("--files", nargs="*", type=Path, help="Specific files to check")

    args = parser.parse_args()

    # Determine which files to check
    if args.files:
        files_to_check = args.files
    elif args.changed_only:
        files_to_check = get_modified_files_since(args.base)
    else:
        # Check all Python files
        files_to_check = list(Path(".").rglob("*.py"))
        # Exclude common non-source directories
        files_to_check = [
            f for f in files_to_check
            if not any(part.startswith(('.', '__')) for part in f.parts)
        ]

    # Check files for neutered content
    results = check_files_neutered(files_to_check, args.base)

    # Find neutered files
    neutered_files = [f for f, r in results.items() if r["neutered"]]

    # Generate report
    report = {
        "base_commit": args.base,
        "timestamp": subprocess.run(
            ["git", "log", "-1", "--format=%ct", "HEAD"],
            capture_output=True,
            text=True
        ).stdout.strip(),
        "files_checked": len(files_to_check),
        "neutered_files": len(neutered_files),
        "results": {str(k): v for k, v in results.items()},
        "cleanup_commands": generate_cleanup_commands(neutered_files) if neutered_files else []
    }

    # Output results
    if neutered_files:
        print(f"\n❌ Found {len(neutered_files)} neutered files:")
        for file_path in neutered_files:
            result = results[file_path]
            print(f"  {file_path}")
            print(f"    Before: {result['before_behavioral']} behavioral nodes")
            print(f"    After:  {result['after_behavioral']} behavioral nodes")
            print(f"    Action:  {result['action']}")

        print("\nSuggested cleanup commands:")
        for cmd in report["cleanup_commands"]:
            print(f"  {cmd}")

        if args.strict:
            print("\n❌ Zero-loss refactor verification failed!")
            print("   Remove neutered files or use --no-strict to bypass")
            return 1
    else:
        print(f"✅ No neutered files found in {len(files_to_check)} checked files")

    # Write report if requested
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Report written to {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
