#!/usr/bin/env python3
"""
Pytest MCP Server - Test discovery, execution, and analysis.

Provides pytest integration for Windsurf with comprehensive test management.
Uses the canonical mcp_bootstrap pattern (FastMCP + @mcp.tool() + run_server)
to avoid the Windows stdio transport hangs caused by low-level Server + anyio.run.
Subprocess calls use safe_run() to enforce stdin=DEVNULL / stdout=PIPE / stderr=PIPE.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from tools.mcp.mcp_bootstrap import REPO_ROOT, create_mcp_server, run_server
from tools.mcp.mcp_subprocess import safe_run

logger = logging.getLogger(__name__)

# Configuration
TESTS_DIR = REPO_ROOT / "tests"
PYTEST_CONFIG = REPO_ROOT / "pytest.ini"
PYPROJECT_TOML = REPO_ROOT / "pyproject.toml"
MAX_EXECUTION_TIME = 300  # 5 minutes for test runs
MAX_OUTPUT_SIZE = 50000  # characters

# Characters not permitted in -k / -m expressions (guard against injection)
_SAFE_EXPR_RE = re.compile(r"^[\w\s\-.()/\[\],'\"=!<>]+$")


def _resolve_confined_path(user_path: str, base: Path) -> Path:
    """Resolve user_path relative to base and reject traversal outside base."""
    try:
        resolved = (base / user_path).resolve()
    except (ValueError, OSError) as exc:
        raise ValueError(f"Invalid path {user_path!r}: {exc}") from exc
    try:
        resolved.relative_to(base.resolve())
    except ValueError:
        raise ValueError(f"Path {user_path!r} escapes the allowed directory {base}")
    return resolved


def _validate_expr(value: str, param_name: str) -> str:
    """Reject marker/keyword expressions containing shell-dangerous characters."""
    if not _SAFE_EXPR_RE.match(value):
        raise ValueError(
            f"{param_name!r} contains unsafe characters. "
            "Only word chars, spaces, and common punctuation are allowed."
        )
    return value


mcp = create_mcp_server(
    "pytest-mcp",
    "Test discovery, execution, coverage analysis, and pytest config inspection.",
)


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def discover_tests(
    path: str = "tests",
    pattern: str = "test_*.py",
) -> str:
    """Discover all tests in the repository"""
    try:
        search_path = _resolve_confined_path(path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid path: {exc}") from exc

    if not search_path.exists():
        raise ValueError(f"Test path {search_path} does not exist")

    cmd = ["python", "-m", "pytest", "--collect-only", "-q", str(search_path)]

    try:
        result = safe_run(cmd, cwd=REPO_ROOT, timeout=30)

        # exit code 5 = no tests collected — not an error, return zero-test result
        if result.returncode not in (0, 5):
            return f"Error collecting tests (exit {result.returncode}):\n{result.stderr or result.stdout}"

        # Parse the collection output
        output = result.stdout
        # Count node ids: lines containing '::' that look like test node ids
        test_count = sum(1 for ln in output.splitlines() if "::" in ln and not ln.startswith(" "))

        # Get file list
        test_files = list(search_path.rglob(pattern))
        file_count = len(test_files)

        summary = f"Discovered {test_count} tests in {file_count} files\n\n"
        summary += f"Search path: {search_path}\n"
        summary += f"Pattern: {pattern}\n\n"
        summary += "Test files:\n"

        for test_file in sorted(test_files):
            rel_path = test_file.relative_to(REPO_ROOT)
            summary += f"- {rel_path}\n"

        return summary

    except subprocess.TimeoutExpired:
        return "Error: Test discovery timed out"
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as e:
        return f"Discovery error: {e}"


@mcp.tool()
def run_tests(
    path: str = "tests",
    keywords: str | None = None,
    markers: str | None = None,
    verbose: bool = True,
    coverage: bool = False,
    timeout: int = 60,
) -> str:
    """Run pytest with specified options"""
    try:
        resolved_test_path = _resolve_confined_path(path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid path: {exc}") from exc

    timeout = min(timeout, MAX_EXECUTION_TIME)

    if keywords:
        keywords = _validate_expr(keywords, "keywords")
    if markers:
        markers = _validate_expr(markers, "markers")

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if keywords:
        cmd.extend(["-k", keywords])

    if markers:
        cmd.extend(["-m", markers])

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])

    cmd.append(str(resolved_test_path))

    # Use a unique JUnit XML path to avoid collisions between concurrent runs
    junit_xml = REPO_ROOT / f".pytest_results_{uuid.uuid4().hex}.xml"
    cmd.extend(["--junit-xml", str(junit_xml)])

    try:
        start_time = time.time()
        result = safe_run(cmd, cwd=REPO_ROOT, timeout=timeout)
        execution_time = time.time() - start_time

        # Parse JUnit XML if available
        junit_summary = ""
        if junit_xml.exists():
            try:
                tree = ET.parse(junit_xml)
                root = tree.getroot()

                tests = int(root.get("tests", 0))
                failures = int(root.get("failures", 0))
                errors = int(root.get("errors", 0))
                skipped = int(root.get("skipped", 0))
                time_taken = float(root.get("time", 0))

                junit_summary = "\nJUnit XML Results:\n"
                junit_summary += f"Tests: {tests}\n"
                junit_summary += f"Failures: {failures}\n"
                junit_summary += f"Errors: {errors}\n"
                junit_summary += f"Skipped: {skipped}\n"
                junit_summary += f"Time: {time_taken:.2f}s\n"

                # Clean up
                junit_xml.unlink()
            except ET.ParseError:
                logger.warning("Failed to parse JUnit XML")

        # Prepare output
        output = f"Command: {' '.join(cmd)}\n"
        output += f"Execution time: {execution_time:.2f}s\n"
        output += f"Exit code: {result.returncode}\n\n"

        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"

        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        output += junit_summary

        # Truncate if too large
        if len(output) > MAX_OUTPUT_SIZE:
            output = output[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"

        # pytest exit codes: 0=all passed, 1=some failed, 2=interrupted,
        # 3=internal error, 4=usage error, 5=no tests collected
        if result.returncode not in (0, 1, 5):
            output = f"ERROR (exit {result.returncode}):\n{output}"

        return output

    except subprocess.TimeoutExpired:
        # Best-effort cleanup of junit xml on timeout
        try:
            if junit_xml.exists():
                junit_xml.unlink()
        except OSError:
            pass
        return f"Error: Tests timed out after {timeout} seconds"
    except (OSError, ValueError) as e:
        return f"Test execution error: {e}"


@mcp.tool()
def get_test_details(
    test_path: str,
    test_name: str | None = None,
) -> str:
    """Get detailed information about a specific test"""
    try:
        resolved = _resolve_confined_path(test_path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid test_path: {exc}") from exc

    if not resolved.exists():
        raise ValueError(f"Test file {resolved} does not exist")

    try:
        # Read the test file
        with open(resolved, encoding="utf-8") as f:
            content = f.read()

        # Basic analysis
        lines = content.split("\n")
        total_lines = len(lines)
        import_lines = len([line for line in lines if line.strip().startswith("import")])
        function_count = len([line for line in lines if line.strip().startswith("def test_")])

        details = f"Test File: {resolved.relative_to(REPO_ROOT)}\n"
        details += f"Total lines: {total_lines}\n"
        details += f"Import statements: {import_lines}\n"
        details += f"Test functions: {function_count}\n\n"

        if test_name:
            # Find specific test function
            test_start = None
            for i, line in enumerate(lines):
                if f"def {test_name}(" in line:
                    test_start = i
                    break

            if test_start is not None:
                details += f"Test function: {test_name}\n"
                details += f"Line: {test_start + 1}\n"

                # Extract function content (simple approach)
                func_lines = []
                indent_level = None

                for line in lines[test_start:]:  # progress_bar: in-memory line scan, bounded
                    if line.strip() == "":
                        func_lines.append(line)
                        continue

                    current_indent = len(line) - len(line.lstrip())

                    if indent_level is None:
                        indent_level = current_indent
                    elif current_indent <= indent_level and line.strip():
                        break

                    func_lines.append(line)

                func_content = "".join(func_lines)
                details += f"\nFunction content:\n{func_content}"
            else:
                details += f"Test function '{test_name}' not found"
        else:
            # List all test functions
            test_functions = []
            for line in lines:
                if line.strip().startswith("def test_"):
                    func_name = line.strip().split("(")[0].replace("def ", "")
                    test_functions.append(func_name)

            details += "Test functions:\n"
            for func in test_functions:
                details += f"- {func}\n"

        return details

    except (ValueError, RuntimeError, OSError) as e:
        return f"Error reading test file: {e}"


@mcp.tool()
def analyze_test_coverage(
    path: str = "agentic_core",
    format: str = "text",
) -> str:
    """Analyze test coverage for the repository"""
    # Check if coverage is available
    try:
        safe_run(["coverage", "--version"], timeout=10, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "Error: Coverage tool not found. Install with: pip install coverage"

    try:
        target_path = _resolve_confined_path(path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid path: {exc}") from exc
    if not target_path.exists():
        raise ValueError(f"Path {target_path} does not exist")

    cmd = [
        "python",
        "-m",
        "pytest",
        f"--cov={path}",
        f"--cov-report={format}",
        "--cov-report=term",
        "tests",
    ]

    try:
        result = safe_run(cmd, cwd=REPO_ROOT, timeout=120)

        output = f"Coverage analysis for: {path}\n"
        output += f"Format: {format}\n"
        output += f"Command: {' '.join(cmd)}\n\n"

        if result.stdout:
            output += result.stdout

        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Coverage analysis timed out"
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as e:
        return f"Coverage error: {e}"


@mcp.tool()
def list_pytest_config() -> str:
    """Show pytest configuration"""
    config_info = "Pytest Configuration:\n\n"

    # Check for pytest.ini
    if PYTEST_CONFIG.exists():
        config_info += f"pytest.ini found: {PYTEST_CONFIG}\n"
        try:
            with open(PYTEST_CONFIG, encoding="utf-8") as f:
                config_info += f.read()
        except OSError as e:
            config_info += f"Error reading pytest.ini: {e}\n"
    else:
        config_info += "pytest.ini: not found\n"

    config_info += "\n"

    # Check for pyproject.toml
    if PYPROJECT_TOML.exists():
        config_info += f"pyproject.toml found: {PYPROJECT_TOML}\n"
        try:
            import tomllib

            with open(PYPROJECT_TOML, "rb") as f:
                data = tomllib.load(f)
                if "tool" in data and "pytest" in data["tool"]:
                    config_info += "[tool.pytest]:\n"
                    config_info += json.dumps(data["tool"]["pytest"], indent=2)
                else:
                    config_info += "No [tool.pytest] section found\n"
        except ImportError:
            config_info += "tomllib not available, cannot parse pyproject.toml\n"
        except (OSError, ValueError, KeyError) as e:
            config_info += f"Error reading pyproject.toml: {e}\n"
    else:
        config_info += "pyproject.toml: not found\n"

    # Show pytest location and version
    try:
        result = safe_run(["python", "-m", "pytest", "--version"], timeout=15)
        config_info += f"\nPytest version:\n{result.stdout}"
    except subprocess.TimeoutExpired:
        config_info += "\nError getting pytest version: timed out"
    except OSError as e:
        config_info += f"\nError getting pytest version: {e}"

    return config_info


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_server(mcp)
