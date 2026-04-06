"""
Pre-Commit Summary Reporter — High-signal issue aggregation and display.

# adg-grep-ban: skip-file -- Pre-commit summary reporter uses grep for text search in hook output files

Collects issues from governance/security hooks and displays a formatted
summary table at the end of pre-commit runs.

Usage:
    # From pre-commit hooks to record an issue:
    python pre_commit_summary_reporter.py --collect \
        --hook-id adg-burndown-gate \
        --hook-name "ADG Burndown Gate" \
        --severity CRITICAL \
        --file path/to/file.py \
        --message "Anti-pattern detected" \
        --explanation "This pattern violates architectural governance..."

    # From pre-commit to display final summary:
    python pre_commit_summary_reporter.py --report

    # Initialize/clear temp state before run:
    python pre_commit_summary_reporter.py --init

Environment:
    PRE_COMMIT_ISSUES_DIR — Directory for temp issue files (default: system temp)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root: Path = Path(__file__).parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ops_scripts.ci.pre_commit_issue_schema import (  # noqa: E402
    IssueCollection,
    PreCommitIssue,
    SeverityLevel,
    colorize_severity,
    get_severity_icon,
)

# Default temp directory for issue files
DEFAULT_ISSUES_DIR = Path(tempfile.gettempdir()) / "pre-commit-issues"

# Governance/security hooks that participate in summary
GOVERNANCE_HOOKS = {
    "adg-burndown-gate": "ADG Anti-Pattern Burndown",
    "guardian-exemption-gate": "Guardian Exemption Quality",
    "hollow-file-gate": "Hollow File Detection",
    "adg-python-ban-gate": "ADG Python Ban Enforcement",
    "adg-yaml-grep-ban-gate": "ADG YAML Grep Ban",
    "adg-ci-gates": "ADG CI Delta Gates",
}


def get_issues_dir() -> Path:
    """Get the directory for storing issue files."""
    env_dir = os.environ.get("PRE_COMMIT_ISSUES_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_ISSUES_DIR


def get_issue_file_path(hook_id: str) -> Path:
    """Get the path for a hook's issue file."""
    return get_issues_dir() / f"{hook_id.replace('-', '_')}.jsonl"


def init_collection() -> None:
    """Initialize/clear the issue collection directory."""
    issues_dir = get_issues_dir()
    if issues_dir.exists():
        for f in issues_dir.glob("*.jsonl"):
            f.unlink()
    else:
        issues_dir.mkdir(parents=True, exist_ok=True)
    print(f"[pre-commit-summary] Initialized issue collection in {issues_dir}")


def collect_issue(
    hook_id: str,
    hook_name: str,
    severity: str,
    message: str,
    explanation: str,
    file_path: str | None = None,
    line_number: int | None = None,
    issue_type: str = "general",
    suggestion: str | None = None,
) -> None:
    """Record a single issue from a hook."""
    try:
        severity_level = SeverityLevel(severity.upper())
    except ValueError:
        severity_level = SeverityLevel.MEDIUM

    issue = PreCommitIssue(
        hook_id=hook_id,
        hook_name=hook_name,
        severity=severity_level,
        message=message,
        explanation=explanation,
        file_path=file_path,
        line_number=line_number,
        issue_type=issue_type,
        suggestion=suggestion,
    )

    # Append to hook's issue file
    issue_file = get_issue_file_path(hook_id)
    issue_file.parent.mkdir(parents=True, exist_ok=True)

    with open(issue_file, "a", encoding="utf-8") as f:
        f.write(issue.to_json() + "\n")


def load_all_issues() -> dict[str, IssueCollection]:
    """Load all issue collections from temp files."""
    collections: dict[str, IssueCollection] = {}

    for hook_id, hook_name in GOVERNANCE_HOOKS.items():
        issue_file = get_issues_dir() / f"{hook_id.replace('-', '_')}.jsonl"
        collection = IssueCollection.load_from_file(hook_id, hook_name, issue_file)
        collections[hook_id] = collection

    return collections


def format_table_row(
    severity: SeverityLevel,
    hook_name: str,
    file_path: str | None,
    message: str,
    explanation: str,
    term_width: int = 100,
    use_color: bool = True,
) -> list[str]:
    """Format a single issue as table row(s), wrapping long text."""
    rows = []
    icon = get_severity_icon(severity)
    sev_str = severity.value

    # Truncate file path if too long
    if file_path:
        file_display = file_path
        if len(file_display) > 40:
            file_display = "..." + file_display[-37:]
    else:
        file_display = "—"

    # First row: severity, hook, file, message
    sev_col = colorize_severity(severity, f"{icon} {sev_str:<8}", use_color)
    hook_col = hook_name[:20]
    file_col = file_display[:40]

    # Wrap message if needed
    msg_width = term_width - 75
    if msg_width < 20:
        msg_width = 20

    if len(message) > msg_width:
        msg_lines = [message[i : i + msg_width] for i in range(0, len(message), msg_width)]
    else:
        msg_lines = [message]

    for i, msg_line in enumerate(msg_lines):
        if i == 0:
            row = f"  {sev_col} | {hook_col:<20} | {file_col:<40} | {msg_line}"
        else:
            row = f"  {'':<10} | {'':<20} | {'':<40} | {msg_line}"
        rows.append(row)

    # Explanation row (indented)
    expl_prefix = "    -> "
    expl_width = term_width - 10
    if len(explanation) > expl_width:
        expl_lines = [explanation[i : i + expl_width] for i in range(0, len(explanation), expl_width)]
    else:
        expl_lines = [explanation]

    for expl_line in expl_lines[:2]:  # Limit to 2 lines
        rows.append(f"{expl_prefix}{expl_line}")

    return rows


def print_summary_table(use_color: bool = True, verbose: bool = False) -> int:
    """
    Print the summary table of all issues.

    Returns:
        Exit code: 0 if no CRITICAL/HIGH issues, 1 otherwise
    """
    collections = load_all_issues()

    # Aggregate all issues
    all_issues: list[PreCommitIssue] = []
    for collection in collections.values():
        all_issues.extend(collection.issues)

    # Add passed status for hooks with no issues
    passed_hooks = []
    for hook_id, hook_name in GOVERNANCE_HOOKS.items():
        if hook_id not in collections or not collections[hook_id].issues:
            passed_hooks.append(PreCommitIssue.passed(hook_id, hook_name))

    # Sort by severity (most severe first), then by hook
    severity_order = {
        SeverityLevel.CRITICAL: 0,
        SeverityLevel.HIGH: 1,
        SeverityLevel.MEDIUM: 2,
        SeverityLevel.LOW: 3,
        SeverityLevel.INFO: 4,
    }
    all_issues.sort(key=lambda i: (severity_order.get(i.severity, 5), i.hook_id))

    # Count by severity
    counts: dict[SeverityLevel, int] = defaultdict(int)
    for issue in all_issues:
        counts[issue.severity] += 1
    for _ in passed_hooks:
        counts[SeverityLevel.INFO] += 1

    # Get terminal width
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 100

    # Print header
    print("\n" + "=" * min(term_width, 100))
    if use_color:
        print("\033[1m[SUMMARY] PRE-COMMIT GOVERNANCE SUMMARY\033[0m")
    else:
        print("[SUMMARY] PRE-COMMIT GOVERNANCE SUMMARY")
    print("=" * min(term_width, 100))

    # Print counts summary
    if use_color:
        critical_str = f"\033[91m{counts[SeverityLevel.CRITICAL]} CRITICAL\033[0m"
        high_str = f"\033[93m{counts[SeverityLevel.HIGH]} HIGH\033[0m"
        medium_str = f"\033[94m{counts[SeverityLevel.MEDIUM]} MEDIUM\033[0m"
        low_str = f"{counts[SeverityLevel.LOW]} LOW"
        passed_str = f"\033[92m{len(passed_hooks)} passed\033[0m"
    else:
        critical_str = f"{counts[SeverityLevel.CRITICAL]} CRITICAL"
        high_str = f"{counts[SeverityLevel.HIGH]} HIGH"
        medium_str = f"{counts[SeverityLevel.MEDIUM]} MEDIUM"
        low_str = f"{counts[SeverityLevel.LOW]} LOW"
        passed_str = f"{len(passed_hooks)} passed"

    print(f"\nIssues: {critical_str} | {high_str} | {medium_str} | {low_str} | {passed_str}")
    print()

    # Print table header
    header = f"  {'SEVERITY':<10} | {'HOOK':<20} | {'FILE':<40} | {'ISSUE'}"
    print(header)
    print("  " + "-" * (min(term_width, 100) - 4))

    # Print issues
    if all_issues:
        for issue in all_issues:
            rows = format_table_row(
                issue.severity,
                issue.hook_name,
                issue.file_path,
                issue.message,
                issue.explanation,
                term_width,
                use_color,
            )
            for row in rows:
                print(row)
    else:
        print("  No issues detected")

    # Print passed hooks (if verbose)
    if verbose and passed_hooks:
        print()
        for issue in passed_hooks[:5]:  # Show first 5 passed
            sev_col = colorize_severity(issue.severity, f"[OK] {issue.hook_name:<27}", use_color)
            print(f"  {sev_col}")
        if len(passed_hooks) > 5:
            print(f"  ... and {len(passed_hooks) - 5} more hooks passed")

    # Print footer with legend
    print()
    print("  Legend:")
    if use_color:
        print("    \033[91m[!] CRITICAL\033[0m — Blocks commit, fix immediately")
        print("    \033[93m[!] HIGH\033[0m — Should fix before commit")
        print("    \033[94m[*] MEDIUM\033[0m — Consider fixing")
        print("    [i] LOW — Informational")
        print("    \033[92m[OK] INFO\033[0m — Passed/clean")
    else:
        print("    [!] CRITICAL — Blocks commit, fix immediately")
        print("    [!] HIGH — Should fix before commit")
        print("    [*] MEDIUM — Consider fixing")
        print("    [i] LOW — Informational")
        print("    [OK] INFO — Passed/clean")

    # Determine exit code
    critical_high_count = counts[SeverityLevel.CRITICAL] + counts[SeverityLevel.HIGH]

    print()
    if critical_high_count > 0:
        if use_color:
            print(f"\033[91m[!] {critical_high_count} critical/high issues require attention\033[0m")
        else:
            print(f"[!] {critical_high_count} critical/high issues require attention")
        return 1
    elif counts[SeverityLevel.MEDIUM] > 0 or counts[SeverityLevel.LOW] > 0:
        if use_color:
            print(
                f"\033[93m[*] {counts[SeverityLevel.MEDIUM] + counts[SeverityLevel.LOW]} issues to consider\033[0m",
            )
        else:
            print(f"[*] {counts[SeverityLevel.MEDIUM] + counts[SeverityLevel.LOW]} issues to consider")
        return 0
    else:
        if use_color:
            print("\033[92m[OK] All governance checks passed\033[0m")
        else:
            print("[OK] All governance checks passed")
        return 0


def test_table() -> None:
    """Print a test table to verify formatting."""
    print("\n[pre-commit-summary] Testing table formatting...\n")

    # Create test issues
    test_issues = [
        PreCommitIssue(
            hook_id="adg-burndown-gate",
            hook_name="ADG Burndown",
            severity=SeverityLevel.CRITICAL,
            file_path="agentic_core/L5_safety/validators/anti_pattern_scanner.py",
            message="Uses subprocess to invoke grep instead of ADG",
            explanation="This violates the ADG-first policy. Use ADG Redis MCP tools instead of grep for dependency analysis.",
            issue_type="adg_ban",
            suggestion="Replace subprocess.run(['grep', ...]) with adg_redis_mcp.grep_search()",
        ),
        PreCommitIssue(
            hook_id="hollow-file-gate",
            hook_name="Hollow File Gate",
            severity=SeverityLevel.HIGH,
            file_path="tests/unit/agentic_core/test_placeholder.py",
            message="File contains no behavioral logic",
            explanation="Files should contain meaningful logic. Empty or placeholder files increase maintenance burden.",
            issue_type="hollow_file",
        ),
        PreCommitIssue(
            hook_id="guardian-exemption-gate",
            hook_name="Guardian Exemption",
            severity=SeverityLevel.MEDIUM,
            file_path="ops_scripts/ci/check_anti_patterns.py",
            message="Guardian comment lacks justification",
            explanation="Every guardian exemption must include a justification explaining why the violation is acceptable.",
            issue_type="exemption_quality",
        ),
        PreCommitIssue.passed("adg-python-ban-gate", "ADG Python Ban"),
        PreCommitIssue.passed("adg-ci-gates", "ADG CI Gates"),
    ]

    # Write test issues
    init_collection()
    for issue in test_issues:
        collect_issue(
            hook_id=issue.hook_id,
            hook_name=issue.hook_name,
            severity=issue.severity.value,
            message=issue.message,
            explanation=issue.explanation,
            file_path=issue.file_path,
            issue_type=issue.issue_type,
        )

    # Display table
    exit_code = print_summary_table(use_color=True, verbose=True)
    print(f"\n[Test] Exit code would be: {exit_code}")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pre-Commit Summary Reporter — Issue aggregation and display",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --init
  %(prog)s --collect --hook-id adg-burndown-gate --severity HIGH --message "Issue found" --explanation "Details..."
  %(prog)s --report
  %(prog)s --test-table
        """,
    )

    parser.add_argument("--init", action="store_true", help="Initialize/clear issue collection")
    parser.add_argument("--collect", action="store_true", help="Collect an issue")
    parser.add_argument("--report", action="store_true", help="Display summary table")
    parser.add_argument("--test-table", action="store_true", help="Print test table")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output (show passed hooks)")

    # Issue collection args
    parser.add_argument("--hook-id", help="Hook identifier")
    parser.add_argument("--hook-name", help="Human-readable hook name")
    parser.add_argument("--severity", choices=[s.value for s in SeverityLevel], help="Issue severity")
    parser.add_argument("--file", help="File path with issue")
    parser.add_argument("--line", type=int, help="Line number")
    parser.add_argument("--message", help="Issue message")
    parser.add_argument("--explanation", help="Issue explanation")
    parser.add_argument("--issue-type", default="general", help="Issue type/category")
    parser.add_argument("--suggestion", help="Fix suggestion")

    args = parser.parse_args()

    use_color = not args.no_color and sys.stdout.isatty()

    if args.init:
        init_collection()
        return 0

    if args.test_table:
        test_table()
        return 0

    if args.collect:
        if not all([args.hook_id, args.hook_name, args.severity, args.message, args.explanation]):
            print(
                "Error: --collect requires --hook-id, --hook-name, --severity, --message, --explanation",
                file=sys.stderr,
            )
            return 2

        collect_issue(
            hook_id=args.hook_id,
            hook_name=args.hook_name,
            severity=args.severity,
            message=args.message,
            explanation=args.explanation,
            file_path=args.file,
            line_number=args.line,
            issue_type=args.issue_type,
            suggestion=args.suggestion,
        )
        return 0

    if args.report:
        return print_summary_table(use_color=use_color, verbose=args.verbose)

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
