"""
CI validation gate for timeout and progress reporting compliance.

Enforces Constitutional Rule §9: All queries require timeouts and progress reporting.
"""

import ast
import re
import sys
import warnings
from pathlib import Path
from typing import Dict, List

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR

# Try to import ADG Query Bridge for ADG-powered queries
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "adg"))
    from adg_query_bridge import ADGQueryBridge, FileMatch
    ADG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"ADG Query Bridge unavailable, falling back to regex: {e}")
    ADG_AVAILABLE = False    # guardian: File operations with encoding need error-specific handling


def validate_timeout_compliance(file_path: Path) -> list[str]:
    """Validate timeout compliance in Python file."""
    violations = []

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading {file_path}: {e}")
        return []

    # Use ADG for subprocess call detection when available
    if ADG_AVAILABLE:
        try:
            bridge = ADGQueryBridge()
            subprocess_calls = bridge.subprocess_calls_without_timeout()

            # Filter calls to those in the current file
            current_file_rel = str(file_path.relative_to(Path.cwd()))
            file_calls = [call for call in subprocess_calls
                         if call.file_path == current_file_rel or call.file_path.endswith(current_file_rel)]

            for call in file_calls:
                # Check if timeout is actually present by reading the specific line
                if call.line_number:
                    try:
                        lines = content.split('\n')
                        if call.line_number <= len(lines):
                            line_content = lines[call.line_number - 1]
                            if "timeout" not in line_content:
                                violations.append(f"{file_path}:{call.line_number}: subprocess call without timeout parameter")
                    except IndexError:
                        violations.append(f"{file_path}:{call.line_number}: subprocess call without timeout parameter")
                else:
                    violations.append(f"{file_path}: subprocess call without timeout parameter")

        except Exception as e:
            warnings.warn(f"ADG query failed, falling back to regex: {e}")
            _fallback_regex_subprocess_detection(file_path, content, violations)
    else:
        _fallback_regex_subprocess_detection(file_path, content, violations)

    # Check for while True without timeout guard
    while_true_pattern = re.finditer(r"while\s+True\s*:", content)
    for match in while_true_pattern:
        line_num = content[: match.start()].count("\n") + 1
        # Look for timeout_guard in surrounding context (50 lines before)
        context_start = max(0, match.start() - 2000)
        context = content[context_start : match.start()]
        if "timeout_guard" not in context and "with timeout" not in context.lower():
            violations.append(f"{file_path}:{line_num}: while True without timeout guard")

    # Check for long loops without progress reporting    # guardian: Syntax errors should be caught at parser level, not runtime
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                    loop_length = node.end_lineno - node.lineno
                    # Consider loops >10 lines as potentially long-running
                    if loop_length > 10:
                        loop_lines = content.split("\n")[node.lineno - 1 : node.end_lineno]
                        loop_content = "\n".join(loop_lines)
                        # Check for progress reporting indicators
                        has_progress = any(
                            [
                                "tqdm" in loop_content,    # guardian: File operations with encoding need error-specific handling
                                "progress" in loop_content.lower(),
                                "pbar.update" in loop_content,
                                "ProgressReporter" in loop_content,
                            ],
                        )
                        if not has_progress:
                            violations.append(
                                f"{file_path}:{node.lineno}: Long loop ({loop_length} lines) "
                                f"without progress reporting",
                            )
    except SyntaxError:
        # Skip AST parsing errors for non-Python or malformed files
        pass

    return violations


def _fallback_regex_subprocess_detection(file_path: Path, content: str, violations: list[str]) -> None:
    """Fallback regex-based subprocess detection when ADG is unavailable."""
    # Check for subprocess.run without timeout
    subprocess_calls = re.finditer(r"subprocess\.run\s*\([^)]*\)", content)
    for match in subprocess_calls:
        call_text = match.group(0)
        if "timeout" not in call_text:
            line_num = content[: match.start()].count("\n") + 1
            violations.append(f"{file_path}:{line_num}: subprocess.run without timeout parameter")

    # Check for subprocess.Popen without timeout context
    popen_calls = re.finditer(r"subprocess\.Popen\s*\([^)]*\)", content)
    for match in popen_calls:
        call_text = match.group(0)
        if "timeout" not in call_text:
            line_num = content[: match.start()].count("\n") + 1
            violations.append(f"{file_path}:{line_num}: subprocess.Popen without timeout handling")


def validate_evidence_compliance(evidence_path: Path) -> list[str]:
    """Validate evidence file has required timeout/progress sections."""
    violations = []

    try:
        with open(evidence_path, encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return [f"{evidence_path}: Failed to read file: {e}"]

    # Check for TIMEOUT_CONFIGURATION section
    if "## TIMEOUT_CONFIGURATION" not in content:
        violations.append(f"{evidence_path}: Missing ## TIMEOUT_CONFIGURATION section")

    # Check for PROGRESS_REPORTING section
    if "## PROGRESS_REPORTING" not in content:
        violations.append(f"{evidence_path}: Missing ## PROGRESS_REPORTING section")

    # Check for timeout values documentation
    if not re.search(r"Timeout:\s*\d+s", content):
        violations.append(f"{evidence_path}: Missing timeout value documentation")

    # Check for completion percentage
    if not re.search(r"Completion:\s*\d+\.?\d*%", content):
        violations.append(f"{evidence_path}: Missing completion percentage")

    return violations


def run_full_validation(repo_path: Path) -> dict[str, list[str]]:
    """Run full timeout/progress validation on repository."""

    all_violations = {"code": [], "evidence": []}

    # Validate Python files in key directories
    key_dirs = [
        repo_path / AGENTIC_CORE_DIR,
        repo_path / APPS_LIC_DIR,
        repo_path / APPS_RG_DIR,
        repo_path / APPS_SHARED_DIR,
        repo_path / OPS_SCRIPTS_DIR,
        repo_path / TOOLS_DIR,
        repo_path / SYSTEM_LEARNING_DIR,
    ]

    for key_dir in key_dirs:
        if not key_dir.exists():
            continue

        for py_file in key_dir.rglob("*.py"):
            # Skip __pycache__ and test files for now
            if "__pycache__" in str(py_file):
                continue

            violations = validate_timeout_compliance(py_file)
            all_violations["code"].extend(violations)

    # Validate evidence files
    evidence_dir = repo_path / "docs" / REPORTS_DIR / "plans"
    if evidence_dir.exists():
        for evidence_file in evidence_dir.glob("EVIDENCE_*.md"):
            violations = validate_evidence_compliance(evidence_file)
            all_violations["evidence"].extend(violations)

    return all_violations


def main() -> int:
    """CI gate for timeout and progress compliance."""

    repo_path = Path.cwd()

    print("=" * 80)
    print("TIMEOUT & PROGRESS COMPLIANCE VALIDATION")
    print("Constitutional Rule §9 Enforcement")
    print("=" * 80)
    print()

    violations = run_full_validation(repo_path)

    total_violations = len(violations["code"]) + len(violations["evidence"])

    if total_violations > 0:
        print(f"❌ FOUND {total_violations} VIOLATIONS\n")

        if violations["code"]:
            print(f"Code violations ({len(violations['code'])}):")
            for v in violations["code"]:
                print(f"  - {v}")
            print()

        if violations["evidence"]:
            print(f"Evidence violations ({len(violations['evidence'])}):")
            for v in violations["evidence"]:
                print(f"  - {v}")
            print()

        print("=" * 80)
        print("REMEDIATION:")
        print("  1. Add timeout parameters to all queries")
        print("  2. Add progress bars to operations >5 seconds")
        print("  3. Add TIMEOUT_CONFIGURATION and PROGRESS_REPORTING sections to evidence")
        print("  4. See: .windsurf/skills/timeout-progress-enforcement/skill.md")
        print("=" * 80)

        return 1  # Fail CI

    print("✅ All timeout and progress requirements met")
    print("   Validated code files and evidence files")
    print()

    return 0  # Pass CI


if __name__ == "__main__":
    sys.exit(main())
