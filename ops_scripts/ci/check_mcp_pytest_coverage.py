#!/usr/bin/env python3
"""
CI Gate: MCP PyTest Coverage Validation

Validates that MCP server code changes have adequate test coverage.

Usage:
  python ops_scripts/ci/check_mcp_pytest_coverage.py
  python ops_scripts/ci/check_mcp_pytest_coverage.py --verbose
"""
import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPO_ROOT = Path(r"C:\Git\Agentic-Workflow")

# MCP directories to check (only existing directories)
MCP_DIRECTORIES = [
    "tools/adg/mcp",
]

# Test directories (only existing directories)
TEST_DIRECTORIES = [
    "tests/unit/tools/adg/mcp",
    "tests/integration/tools/adg/mcp",
]


class ToolFunction:
    """Represents an MCP tool function."""
    def __init__(self, name: str, file_path: Path, line_number: int):
        self.name = name
        self.file_path = file_path
        self.line_number = line_number


def extract_tool_functions(file_path: Path) -> List[ToolFunction]:
    """Extract functions decorated with @mcp.tool from a Python file."""
    tools = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has @mcp.tool decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        if (isinstance(decorator.value, ast.Name) and
                            decorator.value.id == 'mcp' and
                            decorator.attr == 'tool'):
                            tools.append(ToolFunction(
                                name=node.name,
                                file_path=file_path,
                                line_number=node.lineno,
                            ))
                    elif isinstance(decorator, ast.Name) and decorator.id == 'tool':
                        # Check if imported from mcp
                        tools.append(ToolFunction(
                            name=node.name,
                            file_path=file_path,
                            line_number=node.lineno,
                        ))
    except (SyntaxError, UnicodeDecodeError):
        pass

    return tools


def find_test_file_for_tool(tool_name: str, test_dirs: List[Path]) -> Path | None:
    """Find test file that tests a specific tool."""
    for test_dir in test_dirs:
        if not test_dir.exists():
            continue

        for test_file in test_dir.rglob("test_*.py"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if tool name is mentioned in test
                if tool_name in content:
                    return test_file
            except (UnicodeDecodeError, IOError):
                continue

    return None


def check_hung_process_tests(file_path: Path) -> bool:
    """Check if file has hung process test coverage."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for hung process related tests
        hung_keywords = ['hung', 'timeout', 'terminate', 'kill', 'zombie']
        return any(keyword in content.lower() for keyword in hung_keywords)
    except (UnicodeDecodeError, IOError):
        return False


def validate_mcp_test_coverage(verbose: bool = False) -> Tuple[List[str], List[str]]:
    """Validate MCP test coverage."""
    errors = []
    warnings = []

    for mcp_dir in MCP_DIRECTORIES:
        mcp_path = REPO_ROOT / mcp_dir
        if not mcp_path.exists():
            warnings.append(f"MCP directory not found: {mcp_dir}")
            continue

        # Find all Python files in MCP directory
        mcp_files = list(mcp_path.rglob("*.py"))

        if verbose:
            print(f"\nChecking {mcp_dir}...")
            print(f"  Found {len(mcp_files)} Python file(s)")

        # Extract tool functions
        all_tools = []
        for mcp_file in mcp_files:
            tools = extract_tool_functions(mcp_file)
            all_tools.extend(tools)

        if verbose:
            print(f"  Found {len(all_tools)} @mcp.tool function(s)")

        # Check test coverage for each tool
        test_dirs = [REPO_ROOT / d for d in TEST_DIRECTORIES if mcp_dir.split('/')[-1] in d]

        for tool in all_tools:
            test_file = find_test_file_for_tool(tool.name, test_dirs)

            if test_file is None:
                errors.append(
                    f"{tool.file_path.relative_to(REPO_ROOT)}:{tool.line_number}: "
                    f"Tool '{tool.name}' has no test coverage",
                )
            elif verbose:
                print(f"  ✓ Tool '{tool.name}' has test: {test_file.relative_to(REPO_ROOT)}")

        # Check for hung process tests
        has_hung_process_test = False
        for test_dir in test_dirs:
            if test_dir.exists():
                for test_file in test_dir.rglob("test_*.py"):
                    if check_hung_process_tests(test_file):
                        has_hung_process_test = True
                        break

        if not has_hung_process_test:
            errors.append(
                f"{mcp_dir}: Missing hung process test coverage (required for MCP Redis/ADG)",
            )
        elif verbose:
            print("  ✓ Has hung process test coverage")

    return errors, warnings


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP PyTest Coverage Validation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    print("\n[MCP PYTEST COVERAGE VALIDATION]")
    print("=" * 50)

    errors, warnings = validate_mcp_test_coverage(args.verbose)

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  {warning}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  {error}")
        print("\nRequired actions:")
        print("  1. Add unit tests for all @mcp.tool functions")
        print("  2. Add integration tests for MCP protocol communication")
        print("  3. Add hung process tests (timeout, termination, zombie detection)")
        print("  4. See: .windsurf/rules/mcp-pytest-enforcement.md")
        return 1

    print("\n✅ All MCP test coverage requirements met")
    return 0


if __name__ == "__main__":
    sys.exit(main())
