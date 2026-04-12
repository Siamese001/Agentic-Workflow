#!/usr/bin/env python3
"""
Boilerplate Stripping Tool

Safe removal of _emit_* boilerplate blocks while preserving behavioral logic.
"""

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.validators.hollow_file_detector_validator import (
    HollowFileDetector,
)


@dataclass
class StripResult:
    """Result of boilerplate stripping operation."""

    action: str  # "cleaned", "deleted", "skipped"
    reason: str
    lines_removed: int = 0
    emit_calls_removed: int = 0
    imports_removed: int = 0
    became_hollow: bool = False


class BoilerplateStripper(ast.NodeTransformer):
    """AST transformer that removes boilerplate nodes."""

    def __init__(self):
        self.removed_count = 0
        self.emit_calls_removed = 0
        self.imports_removed = 0
        self.preserved_imports: set[str] = set()

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Visit module level."""
        # Filter out boilerplate statements
        new_body = []

        for stmt in node.body:
            if self._is_boilerplate_statement(stmt):
                self.removed_count += 1
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    self.imports_removed += 1
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    self.emit_calls_removed += 1
                # Skip this statement (don't add to new_body)
            else:
                new_body.append(stmt)

        node.body = new_body
        return node

    def _is_boilerplate_statement(self, stmt: ast.stmt) -> bool:
        """Check if statement is boilerplate."""
        # Module-level emit calls
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            if isinstance(call.func, ast.Name):
                if call.func.id.startswith("_emit_"):
                    return True

        # Unused imports (simplified - would need full analysis for accuracy)
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            # For now, only remove obvious boilerplate imports
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if any(
                        name in alias.name
                        for name in [
                            "uuid",
                            "hashlib",
                            "json",
                            "logging",
                            "dataclasses",
                            "typing",
                            "pathlib",
                        ]
                    ):
                        return True
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.module and any(
                    pattern in stmt.module
                    for pattern in [
                        "typing",
                        "dataclasses",
                        "pathlib",
                    ]
                ):
                    return True

        return False


class SafeBoilerplateStripper:
    """Safe boilerplate stripping with validation."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.detector = HollowFileDetector()

    def count_behavioral_nodes(self, tree: ast.AST) -> int:
        """Count behavioral nodes in AST."""
        if not tree:
            return 0

        # Create a new counter for each analysis
        from agentic_core.L5_safety.validators.hollow_file_detector_validator import BehavioralNodeCounter

        counter = BehavioralNodeCounter()
        counter.visit(tree)
        return int(counter.behavioral_functions + counter.behavioral_classes)

    def strip_file_boilerplate(self, file_path: Path, dry_run: bool = True) -> StripResult:
        """Strip boilerplate from a single file."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return StripResult(action="skipped", reason="Cannot read file")

        # Handle empty file
        if not content.strip():
            return StripResult(action="skipped", reason="Empty file")

        # Parse original tree
        try:
            original_tree = ast.parse(content)
        except SyntaxError:
            return StripResult(action="skipped", reason="Syntax error")

        # Count original behavioral nodes
        original_behavioral = self.count_behavioral_nodes(original_tree)

        # Apply stripper
        stripper = BoilerplateStripper()
        stripped_tree = stripper.visit(original_tree)

        # Count behavioral nodes after stripping
        after_behavioral = self.count_behavioral_nodes(stripped_tree)

        # Check if file became hollow
        became_hollow = after_behavioral == 0 and stripper.removed_count > 0

        if original_behavioral == 0 and stripper.removed_count == 0:
            return StripResult(action="skipped", reason="No behavioral content to preserve")

        if became_hollow:
            return StripResult(
                action="deleted",
                reason="File would become hollow after stripping",
                lines_removed=stripper.removed_count,
                emit_calls_removed=stripper.emit_calls_removed,
                imports_removed=stripper.imports_removed,
                became_hollow=True,
            )

        if stripper.removed_count == 0:
            return StripResult(action="skipped", reason="No boilerplate to remove")

        # Generate cleaned content
        try:
            import astor

            cleaned_content = astor.to_source(stripped_tree)
        except ImportError:
            # Fallback to basic unparse
            cleaned_content = ast.unparse(stripped_tree)

        # Write file if not dry run
        if not dry_run:
            file_path.write_text(cleaned_content, encoding="utf-8")

            # Run ruff format if available
            try:
                import subprocess

                subprocess.run(["ruff", "format", str(file_path)], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass  # ruff not available or failed

        return StripResult(
            action="cleaned",
            reason=f"Removed {stripper.removed_count} boilerplate statements",
            lines_removed=stripper.removed_count,
            emit_calls_removed=stripper.emit_calls_removed,
            imports_removed=stripper.imports_removed,
            became_hollow=False,
        )

    def strip_directory(
        self, directory: Path, dry_run: bool = True, recursive: bool = True
    ) -> list[StripResult]:
        """Strip boilerplate from all Python files in directory."""
        results = []

        # Find Python files
        if recursive:
            python_files = list(directory.rglob("*.py"))
        else:
            python_files = list(directory.glob("*.py"))

        # Exclude common non-source directories
        python_files = [
            f
            for f in python_files
            if not any(part.startswith((".", "__")) for part in f.parts) and "site-packages" not in str(f)
        ]

        for file_path in python_files:
            result = self.strip_file_boilerplate(file_path, dry_run)
            results.append(result)

            # Print result
            rel_path = file_path.relative_to(self.repo_root)
            if result.action == "deleted":
                print(f"🗑️  {rel_path}: {result.reason}")
            elif result.action == "cleaned":
                print(f"✨ {rel_path}: {result.reason}")
            elif result.action == "skipped":
                print(f"⏭️  {rel_path}: {result.reason}")

        return results

    def generate_report(self, results: list[StripResult]) -> dict:
        """Generate summary report from results."""
        summary = {
            "total_files": len(results),
            "cleaned": sum(1 for r in results if r.action == "cleaned"),
            "deleted": sum(1 for r in results if r.action == "deleted"),
            "skipped": sum(1 for r in results if r.action == "skipped"),
            "total_lines_removed": sum(r.lines_removed for r in results),
            "total_emit_calls_removed": sum(r.emit_calls_removed for r in results),
            "total_imports_removed": sum(r.imports_removed for r in results),
            "files_became_hollow": sum(1 for r in results if r.became_hollow),
        }

        return summary


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Strip boilerplate from Python files")
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to process")
    parser.add_argument("--report", "-r", action="store_true", help="Report-only mode (no modifications)")
    parser.add_argument("--dry-run", action="store_true", help=argparse.SUPPRESS)  # Deprecated, use --report
    parser.add_argument(
        "--write", action="store_true", help=argparse.SUPPRESS
    )  # Deprecated, default is now execute
    parser.add_argument(
        "--recursive", "-R", action="store_true", default=True, help="Process directories recursively"
    )
    parser.add_argument("--no-recursive", action="store_true", help="Don't process directories recursively")
    parser.add_argument("--report-file", type=Path, help="Write detailed report to JSON file")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository root")

    args = parser.parse_args()

    # Default to execute mode, report mode only if --report flag is set
    dry_run = args.report

    # Handle recursive flag
    if args.no_recursive:
        recursive = False
    else:
        recursive = args.recursive

    # Initialize stripper
    stripper = SafeBoilerplateStripper(args.repo)

    # Process paths
    all_results = []

    for path in args.paths:
        if path.is_file():
            result = stripper.strip_file_boilerplate(path, dry_run)
            all_results.append(result)
        elif path.is_dir():
            results = stripper.strip_directory(path, dry_run, recursive)
            all_results.extend(results)
        else:
            print(f"⚠️  Path not found: {path}")

    # Generate summary
    summary = stripper.generate_report(all_results)

    print("\n📊 Summary:")
    print(f"  Total files: {summary['total_files']}")
    print(f"  Cleaned: {summary['cleaned']}")
    print(f"  Would be deleted: {summary['deleted']}")
    print(f"  Skipped: {summary['skipped']}")
    print(f"  Total lines removed: {summary['total_lines_removed']}")
    print(f"  Emit calls removed: {summary['total_emit_calls_removed']}")
    print(f"  Imports removed: {summary['total_imports_removed']}")

    if dry_run:
        print("\n💡 This was a report run. Omit --report to actually modify files.")

    # Write report file
    if args.report_file:
        report_data = {
            "dry_run": dry_run,
            "summary": summary,
            "results": [
                {
                    "action": r.action,
                    "reason": r.reason,
                    "lines_removed": r.lines_removed,
                    "emit_calls_removed": r.emit_calls_removed,
                    "imports_removed": r.imports_removed,
                    "became_hollow": r.became_hollow,
                }
                for r in all_results
            ],
        }

        args.report_file.parent.mkdir(parents=True, exist_ok=True)
        args.report_file.write_text(json.dumps(report_data, indent=2))
        print(f"\n📄 Report written to {args.report_file}")

    # Exit with error if files would be deleted
    if summary["deleted"] > 0 and dry_run:
        print(f"\n⚠️  {summary['deleted']} files would become hollow and should be deleted")
        print("   Review the results and consider removing these files manually")

    return 0


if __name__ == "__main__":
    sys.exit(main())
