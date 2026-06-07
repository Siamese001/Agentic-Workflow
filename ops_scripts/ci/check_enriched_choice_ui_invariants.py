#!/usr/bin/env python3
"""CI scanner for enriched choice UI invariants.

Per hardened plan ui-choice-consistency-zero-loss-hardened-d9f3a1:
- Scanner is SEPARATE from Author-Gate audit (review correction #2)
- Enforces callsite discipline, not runtime formatting (review correction #6)
- CI mode defaults to fail-closed (review correction #1)

Checks:
1. Active decision prompts must use Author-Gate pipeline OR build_enriched_choice_question()
2. Raw ask_user_question in decision context without wrapper is violation
3. Markdown prose option blocks in active workflow files are violations
4. AUTHOR_GATE_PACKET outside canonical AG path is violation
5. ASK_USER_QUESTION_PACKET missing for enriched choices is violation

Authority boundary:
- AUTHOR_GATE_PACKET = canonical AG pipeline only (emit_packet.py)
- ASK_USER_QUESTION_PACKET = enriched_choice wrapper only (this scanner's domain)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Literal

# Repository root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Fail policy per hardened review #1: CI defaults to fail-closed
ENV_FAIL_CLOSED = "ENRICHED_CHOICE_UI_FAIL_CLOSED"
ENV_BYPASS = "ENRICHED_CHOICE_UI_BYPASS"

# Output paths
VIOLATIONS_LOG = REPO_ROOT / "artifacts" / "windsurf" / "enriched_choice_ui_violations.jsonl"

# Decision context keywords that trigger enforcement
DECISION_CONTEXT_KEYWORDS: tuple[str, ...] = (
    "ask_user_question",
    "which approach",
    "which option",
    "which strategy",
    "choose between",
    "decide between",
    "pick a",
    "select an option",
)

# Patterns for detecting decision presentations
_AUQ_RAW_PATTERN = re.compile(
    r'ask_user_question\s*\(.*?options\s*=',
    re.DOTALL | re.IGNORECASE,
)

_AUQ_ENRICHED_PATTERN = re.compile(
    r'build_enriched_choice_question\s*\(',
    re.DOTALL | re.IGNORECASE,
)

_AG_PIPELINE_PATTERN = re.compile(
    r'(emit_packet|author-gate-packet-builder|AUTHOR_GATE_PACKET)',
    re.DOTALL | re.IGNORECASE,
)

_MARKDOWN_PROSE_OPTIONS = re.compile(
    r'>\s*[A-D][)\]]\s*.*?(?=>\s*[A-D][)\]]|\n\n|</|$)',
    re.DOTALL,
)

_AUTHOR_GATE_PACKET_OUTSIDE_AG = re.compile(
    r'(?:print\s*\(\s*["\'])?AUTHOR_GATE_PACKET\s*:\s*(?:json\.dumps|.*?(?:\{|\[|"))',
    re.DOTALL | re.IGNORECASE,
)

_ASK_USER_QUESTION_PACKET_PRESENT = re.compile(
    r'ASK_USER_QUESTION_PACKET',
    re.IGNORECASE,
)

# Exemption allowlist per hardened review: narrow, path-scoped, auditable
_EXEMPTIONS: dict[str, str] = {
    "apps_shared/cli/interactive_wizard.py": "data_collection_field_input",
    "tests/": "test_fixture",
    "tests/_apps_contract/": "test_fixture",
    "tests/governance/": "test_fixture",
    "tests/unit/": "test_fixture",
    "docs/": "documentation_example",
    "docs/reports/": "documentation_example",
    ".cursor/plans/": "plan_documentation",
    ".cursor/plans/_archive/": "archived_documentation",
    # Note: .cursor/workflows/ and .cursor/skills/ are ACTIVE surfaces - NOT exempt
}

# Active surfaces that must comply
_ACTIVE_SURFACES = {
    ".cursor/skills/structured-reasoning/SKILL.md",
    ".claude/commands/author-gate-decision-gate.md",
    # Note: antipattern-author-gate.md is AUTHOR_GATE path, uses AG pipeline
}


ResultStatus = Literal["pass", "fail", "exempt", "bypass"]


def _is_exempt(file_path: Path) -> tuple[bool, str]:
    """Check if file path is exempt from enforcement.
    
    Returns: (is_exempt, reason)
    """
    try:
        path_str = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        # File outside repo (e.g., temp files in tests) - not exempt, check it
        path_str = str(file_path).replace("\\", "/")
    
    for exempt_prefix, reason in _EXEMPTIONS.items():
        # Normalize prefix and match
        clean_prefix = exempt_prefix.rstrip("/").replace("\\", "/")
        if path_str.startswith(clean_prefix):
            return True, reason
    
    return False, ""


def _is_active_surface(file_path: Path) -> bool:
    """Check if file is a known active decision surface."""
    try:
        path_str = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return False
    # Normalize active surfaces for comparison
    normalized_active = {s.replace("\\", "/") for s in _ACTIVE_SURFACES}
    return path_str in normalized_active


def _strip_markdown_code_blocks(content: str) -> str:
    """Strip code blocks from markdown content to avoid flagging examples."""
    # Remove fenced code blocks (```python ... ```)
    cleaned = re.sub(r'```[\w]*\n.*?```', '', content, flags=re.DOTALL)
    # Also remove inline code blocks (`code`)
    cleaned = re.sub(r'`[^`]+`', '', cleaned)
    return cleaned


def _detect_raw_ask_user_question(content: str, file_path: Path | None = None) -> list[dict[str, Any]]:
    """Detect raw ask_user_question calls without enrichment wrapper."""
    violations = []
    
    # For markdown files, strip code blocks (they're instructional examples)
    if file_path and file_path.suffix == ".md":
        content = _strip_markdown_code_blocks(content)
    
    # Check for enriched wrapper or AG pipeline anywhere in file
    has_enriched_anywhere = _AUQ_ENRICHED_PATTERN.search(content) is not None
    has_ag_pipeline_anywhere = _AG_PIPELINE_PATTERN.search(content) is not None
    
    # Find all ask_user_question calls with options
    for match in _AUQ_RAW_PATTERN.finditer(content):
        # Check context around this specific call
        # Look back up to 1000 chars (more context for builder calls)
        start_pos = max(0, match.start() - 1000)
        context_before = content[start_pos:match.start()]
        
        # Check if AG pipeline or enriched wrapper in nearby context
        has_ag_pipeline = _AG_PIPELINE_PATTERN.search(context_before) is not None
        has_enriched_wrapper = _AUQ_ENRICHED_PATTERN.search(context_before) is not None
        
        # Also check if enriched wrapper appears anywhere in file (import at top)
        if not has_ag_pipeline and not has_enriched_wrapper and not has_enriched_anywhere:
            # Raw ask_user_question detected
            line_num = content[:match.start()].count("\n") + 1
            last_newline = content.rfind("\n", 0, match.start())
            column = match.start() - last_newline if last_newline >= 0 else match.start()
            violations.append({
                "line": line_num,
                "column": column,
                "pattern": "raw_ask_user_question",
                "severity": "critical",
                "message": "Raw ask_user_question without enriched wrapper or AG pipeline",
            })
    
    return violations


def _detect_markdown_prose_options(content: str, file_path: Path) -> list[dict[str, Any]]:
    """Detect markdown prose option blocks (blockquote-style options A/B/C/D)."""
    violations = []
    
    # Only check markdown files in active workflows
    if not file_path.suffix == ".md":
        return violations
    
    # Look for prose option patterns like:
    # > A) Option one
    # > B) Option two
    lines = content.split("\n")
    option_block_start = None
    option_count = 0
    
    for i, line in enumerate(lines, 1):
        # Detect option lines in blockquotes
        if re.match(r">\s*[A-D][)\]]\s+\w+", line):
            if option_block_start is None:
                option_block_start = i
            option_count += 1
        elif option_block_start is not None and not line.strip().startswith(">"):
            # End of block, check if it was a decision block
            if option_count >= 2:
                violations.append({
                    "line": option_block_start,
                    "column": 1,
                    "pattern": "markdown_prose_options",
                    "severity": "high",
                    "message": f"Markdown prose options (A-D) at lines {option_block_start}-{i-1}; must use ask_user_question + enriched wrapper",
                })
            option_block_start = None
            option_count = 0
    
    return violations


def _detect_ag_packet_outside_path(content: str, file_path: Path) -> list[dict[str, Any]]:
    """Detect AUTHOR_GATE_PACKET outside canonical AG path."""
    violations = []
    
    try:
        path_str = str(file_path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        # File outside repo (temp files) - treat as non-AG path
        path_str = str(file_path).replace("\\", "/")
    
    # For markdown files, strip code blocks (they're instructional examples)
    if file_path.suffix == ".md":
        content = _strip_markdown_code_blocks(content)
    
    # Check if this is a canonical AG path
    is_ag_path = any(x in path_str for x in [
        "author-gate-packet-builder",
        "author-gate-ui-renderer",
        "antipattern-author-gate.md",  # Uses AG pipeline per hardened reclassification
    ])
    
    if is_ag_path:
        return violations  # AG paths allowed to emit AUTHOR_GATE_PACKET
    
    # Check for AUTHOR_GATE_PACKET emission
    for match in _AUTHOR_GATE_PACKET_OUTSIDE_AG.finditer(content):
        line_num = content[:match.start()].count("\n") + 1
        violations.append({
            "line": line_num,
            "column": match.start() - content.rfind("\n", 0, match.start()),
            "pattern": "author_gate_packet_outside_ag_path",
            "severity": "critical",
            "message": "AUTHOR_GATE_PACKET outside canonical Author-Gate pipeline",
        })
    
    return violations


def _detect_missing_telemetry(content: str, file_path: Path) -> list[dict[str, Any]]:
    """Detect enriched choices missing ASK_USER_QUESTION_PACKET telemetry."""
    violations = []
    
    # Only check Python files for this
    if file_path.suffix != ".py":
        return violations
    
    # Check if enriched wrapper is used
    has_enriched_wrapper = _AUQ_ENRICHED_PATTERN.search(content) is not None
    
    # Check if telemetry is emitted
    has_telemetry = _ASK_USER_QUESTION_PACKET_PRESENT.search(content) is not None
    
    if has_enriched_wrapper and not has_telemetry:
        # Find the build_enriched_choice_question call
        for match in _AUQ_ENRICHED_PATTERN.finditer(content):
            line_num = content[:match.start()].count("\n") + 1
            violations.append({
                "line": line_num,
                "column": match.start() - content.rfind("\n", 0, match.start()),
                "pattern": "missing_telemetry_emission",
                "severity": "medium",
                "message": "build_enriched_choice_question used but ASK_USER_QUESTION_PACKET telemetry not emitted",
            })
    
    return violations


def check_file(file_path: Path) -> dict[str, Any]:
    """Check a single file for violations."""
    # Handle paths outside REPO_ROOT (e.g., temp files in tests)
    try:
        rel_path = str(file_path.relative_to(REPO_ROOT))
    except ValueError:
        rel_path = str(file_path)
    
    result = {
        "file": rel_path,
        "status": "pass",
        "exemption_reason": None,
        "violations": [],
    }
    
    # Check exemption (includes outside_repo case)
    is_exempt, reason = _is_exempt(file_path)
    if is_exempt:
        result["status"] = "exempt"
        result["exemption_reason"] = reason
        return result
    
    # Read file
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        result["status"] = "fail"
        result["violations"].append({
            "line": 0,
            "column": 0,
            "pattern": "file_read_error",
            "severity": "error",
            "message": f"Failed to read file: {e}",
        })
        return result
    
    # Run checks
    violations = []
    violations.extend(_detect_raw_ask_user_question(content, file_path))
    violations.extend(_detect_markdown_prose_options(content, file_path))
    violations.extend(_detect_ag_packet_outside_path(content, file_path))
    violations.extend(_detect_missing_telemetry(content, file_path))
    
    if violations:
        result["status"] = "fail"
        result["violations"] = violations
    
    return result


def check_paths(paths: list[Path]) -> list[dict[str, Any]]:
    """Check multiple paths for violations."""
    results = []
    
    for path in paths:
        if path.is_file():
            results.append(check_file(path))
        elif path.is_dir():
            for file_path in path.rglob("*.py"):
                results.append(check_file(file_path))
            for file_path in path.rglob("*.md"):
                results.append(check_file(file_path))
    
    return results


def write_violations(results: list[dict[str, Any]]) -> None:
    """Write violations to log file."""
    VIOLATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    with open(VIOLATIONS_LOG, "a", encoding="utf-8") as f:
        for result in results:
            if result["status"] == "fail":
                log_entry = {
                    "timestamp": __import__("datetime").datetime.now(
                        __import__("datetime").timezone.utc
                    ).isoformat(),
                    "file": result["file"],
                    "violations": result["violations"],
                }
                f.write(json.dumps(log_entry) + "\n")


def format_report(results: list[dict[str, Any]]) -> str:
    """Format results as human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("Enriched Choice UI Invariants Check")
    lines.append("=" * 70)
    
    total_files = len(results)
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    exempt = sum(1 for r in results if r["status"] == "exempt")
    
    lines.append(f"\nSummary: {total_files} files checked")
    lines.append(f"  ✓ Pass: {passed}")
    lines.append(f"  ✗ Fail: {failed}")
    lines.append(f"  ○ Exempt: {exempt}")
    
    if failed > 0:
        lines.append("\n" + "-" * 70)
        lines.append("Violations:")
        lines.append("-" * 70)
        
        for result in results:
            if result["status"] == "fail":
                lines.append(f"\n{result['file']}:")
                for v in result["violations"]:
                    lines.append(f"  Line {v['line']}:{v['column']}  [{v['severity'].upper()}]")
                    lines.append(f"    Pattern: {v['pattern']}")
                    lines.append(f"    Message: {v['message']}")
    
    if exempt > 0:
        lines.append("\n" + "-" * 70)
        lines.append("Exemptions:")
        lines.append("-" * 70)
        
        for result in results:
            if result["status"] == "exempt":
                lines.append(f"  {result['file']}: {result['exemption_reason']}")
    
    lines.append("\n" + "=" * 70)
    
    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check enriched choice UI invariants",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Paths to check (files or directories)",
    )
    parser.add_argument(
        "--fail-closed",
        action="store_true",
        help="Exit with non-zero code on violations (default in CI)",
    )
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Exit 0 even with violations (for local/manual use)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable format",
    )
    args = parser.parse_args()
    
    # Bypass check
    if os.environ.get(ENV_BYPASS):
        print(f"[{ENV_BYPASS}=1] Bypassing enriched choice UI invariants check")
        return 0
    
    # Determine fail policy per hardened review #1
    # CI mode: fail-closed by default
    # Manual mode: advisory if explicitly requested
    if args.advisory:
        fail_closed = False
    elif args.fail_closed:
        fail_closed = True
    else:
        # Auto-detect: fail-closed if CI environment variable present
        fail_closed = bool(
            os.environ.get("CI") or 
            os.environ.get("ENRICHED_CHOICE_UI_FAIL_CLOSED")
        )
    
    # Default paths if none provided
    if not args.paths:
        args.paths = [
            REPO_ROOT / ".cursor" / "skills",
            REPO_ROOT / "docs/archive/windsurf/legacy-tree" / "workflows",
        ]
    
    # Run checks
    results = check_paths(args.paths)
    
    # Write violations log
    write_violations(results)
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))
    
    # Determine exit code
    has_failures = any(r["status"] == "fail" for r in results)
    
    if fail_closed and has_failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
