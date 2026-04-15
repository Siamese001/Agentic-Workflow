from __future__ import annotations

import ast
import json
import subprocess
import time
import uuid
from pathlib import Path

from tools.mcp.mcp_subprocess import safe_run
from tqdm import tqdm

from .config import (
    CONFIG_TIMEOUT,
    COVERAGE_TIMEOUT,
    DISCOVER_TIMEOUT,
    MAX_OUTPUT_SIZE,
    MAX_TEST_FILE_SIZE,
    PYPROJECT_TOML,
    PYTEST_CONFIG,
    REPO_ROOT,
)
from .parsers import cleanup_file, parse_junit_summary
from .validators import (
    python_cmd,
    resolve_confined_path,
    validate_coverage_report,
    validate_expr,
    validate_timeout,
)


def _format_command(cmd: list[str]) -> str:
    return " ".join(cmd)


def _read_text(path: Path, *, encoding: str = "utf-8") -> str:
    return path.read_text(encoding=encoding)


def discover_tests(
    path: str = "tests",
    pattern: str = "test_*.py",
) -> str:
    """Discover all tests in the repository"""
    try:
        search_path = resolve_confined_path(path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid path: {exc}") from exc

    if not search_path.exists():
        raise ValueError(f"Test path {search_path} does not exist")

    cmd = python_cmd("-m", "pytest", "--collect-only", "-q", str(search_path))

    try:
        result = safe_run(cmd, cwd=REPO_ROOT, timeout=DISCOVER_TIMEOUT)

        # exit code 5 = no tests collected — not an error, return zero-test result
        if result.returncode not in (0, 5):
            return f"Error collecting tests (exit {result.returncode}):\n{result.stderr or result.stdout}"

        output = result.stdout
        test_count = sum(1 for line in output.splitlines() if "::" in line and not line.startswith(" "))
        test_files = list(search_path.rglob(pattern))

        summary = f"Discovered {test_count} tests in {len(test_files)} files\n\n"
        summary += f"Search path: {search_path}\n"
        summary += f"Pattern: {pattern}\n\n"
        summary += "Test files:\n"

        for test_file in sorted(test_files):
            rel_path = test_file.relative_to(REPO_ROOT)
            summary += f"- {rel_path}\n"

        return summary

    except subprocess.TimeoutExpired:
        return "Error: Test discovery timed out"
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        return f"Discovery error: {exc}"


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
        resolved_test_path = resolve_confined_path(path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid path: {exc}") from exc

    if not resolved_test_path.exists():
        raise ValueError(f"Test path {resolved_test_path} does not exist")

    timeout = validate_timeout(timeout)

    if keywords:
        keywords = validate_expr(keywords, "keywords")
    if markers:
        markers = validate_expr(markers, "markers")

    cmd = python_cmd("-m", "pytest")

    if verbose:
        cmd.append("-v")
    if keywords:
        cmd.extend(["-k", keywords])
    if markers:
        cmd.extend(["-m", markers])
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing"])

    cmd.append(str(resolved_test_path))

    junit_xml = REPO_ROOT / f".pytest_results_{uuid.uuid4().hex}.xml"
    cmd.extend(["--junit-xml", str(junit_xml)])

    try:
        start_time = time.monotonic()
        result = safe_run(cmd, cwd=REPO_ROOT, timeout=timeout)
        execution_time = time.monotonic() - start_time

        junit_summary = parse_junit_summary(junit_xml) if junit_xml.exists() else ""

        output = f"Command: {_format_command(cmd)}\n"
        output += f"Execution time: {execution_time:.2f}s\n"
        output += f"Exit code: {result.returncode}\n\n"

        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"

        output += junit_summary

        if len(output) > MAX_OUTPUT_SIZE:
            output = output[:MAX_OUTPUT_SIZE] + "\n... (output truncated)"

        if result.returncode not in (0, 1, 5):
            output = f"ERROR (exit {result.returncode}):\n{output}"

        return output

    except subprocess.TimeoutExpired:
        return f"Error: Tests timed out after {timeout} seconds"
    except (OSError, ValueError) as exc:
        return f"Test execution error: {exc}"
    finally:
        cleanup_file(junit_xml)


def get_test_details(
    test_path: str,
    test_name: str | None = None,
) -> str:
    """Get detailed information about a specific test"""
    try:
        resolved = resolve_confined_path(test_path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid test_path: {exc}") from exc

    if not resolved.exists():
        raise ValueError(f"Test file {resolved} does not exist")

    try:
        if resolved.stat().st_size > MAX_TEST_FILE_SIZE:
            return (
                f"Error: Test file {resolved.relative_to(REPO_ROOT)} exceeds "
                f"{MAX_TEST_FILE_SIZE} bytes; refusing to load fully"
            )

        content = _read_text(resolved)
        lines = content.splitlines()
        total_lines = len(lines)
        import_lines = len(
            [line for line in lines if line.strip().startswith("import ") or line.strip().startswith("from ")]
        )

        tree = ast.parse(content, filename=str(resolved))
        test_functions = sorted(
            [
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            ],
            key=lambda node: node.lineno,
        )

        details = f"Test File: {resolved.relative_to(REPO_ROOT)}\n"
        details += f"Total lines: {total_lines}\n"
        details += f"Import statements: {import_lines}\n"
        details += f"Test functions: {len(test_functions)}\n\n"

        if test_name:
            target = next((node for node in test_functions if node.name == test_name), None)
            if target is not None:
                details += f"Test function: {test_name}\n"
                details += f"Line: {target.lineno}\n"
                end_lineno = getattr(target, "end_lineno", target.lineno)
                func_content = "\n".join(lines[target.lineno - 1 : end_lineno])
                details += f"\nFunction content:\n{func_content}"
            else:
                details += f"Test function '{test_name}' not found"
        else:
            details += "Test functions:\n"
            for node in test_functions:
                details += f"- {node.name} (line {node.lineno})\n"

        return details

    except (SyntaxError, ValueError, RuntimeError, OSError) as exc:
        return f"Error reading test file: {exc}"


def analyze_test_coverage(
    path: str = "agentic_core",
    format: str = "term-missing",
) -> str:
    """Analyze test coverage for the repository"""
    try:
        safe_run(python_cmd("-m", "coverage", "--version"), timeout=10, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return "Error: Coverage tool not found. Install with: pip install coverage"

    try:
        target_path = resolve_confined_path(path, REPO_ROOT)
    except ValueError as exc:
        raise ValueError(f"Invalid path: {exc}") from exc
    if not target_path.exists():
        raise ValueError(f"Path {target_path} does not exist")

    format = validate_coverage_report(format)

    cmd = python_cmd("-m", "pytest", f"--cov={path}")
    reports = [format]
    if format not in {"term", "term-missing"}:
        reports.append("term-missing")
    for report in tqdm(reports, desc="Processing", unit="item"):
        cmd.append(f"--cov-report={report}")
    cmd.append("tests")

    try:
        result = safe_run(cmd, cwd=REPO_ROOT, timeout=COVERAGE_TIMEOUT)

        output = f"Coverage analysis for: {path}\n"
        output += f"Format: {format}\n"
        output += f"Command: {_format_command(cmd)}\n\n"

        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        return output

    except subprocess.TimeoutExpired:
        return "Error: Coverage analysis timed out"
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        return f"Coverage error: {exc}"


def list_pytest_config() -> str:
    """Show pytest configuration"""
    config_info = "Pytest Configuration:\n\n"

    if PYTEST_CONFIG.exists():
        config_info += f"pytest.ini found: {PYTEST_CONFIG}\n"
        try:
            config_info += _read_text(PYTEST_CONFIG)
        except OSError as exc:
            config_info += f"Error reading pytest.ini: {exc}\n"
    else:
        config_info += "pytest.ini: not found\n"

    config_info += "\n"

    if PYPROJECT_TOML.exists():
        config_info += f"pyproject.toml found: {PYPROJECT_TOML}\n"
        try:
            import tomllib

            with open(PYPROJECT_TOML, "rb") as handle:
                data = tomllib.load(handle)
                tool_section = data.get("tool", {})
                pytest_section = tool_section.get("pytest", {})
                ini_options = pytest_section.get("ini_options")

                if ini_options is not None:
                    config_info += "[tool.pytest.ini_options]:\n"
                    config_info += json.dumps(ini_options, indent=2)
                elif pytest_section:
                    config_info += "[tool.pytest]:\n"
                    config_info += json.dumps(pytest_section, indent=2)
                else:
                    config_info += "No [tool.pytest] or [tool.pytest.ini_options] section found\n"
        except ImportError:
            config_info += "tomllib not available, cannot parse pyproject.toml\n"
        except (OSError, ValueError, KeyError) as exc:
            config_info += f"Error reading pyproject.toml: {exc}\n"
    else:
        config_info += "pyproject.toml: not found\n"

    try:
        result = safe_run(python_cmd("-m", "pytest", "--version"), timeout=CONFIG_TIMEOUT)
        config_info += f"\nPytest version:\n{result.stdout}"
    except subprocess.TimeoutExpired:
        config_info += "\nError getting pytest version: timed out"
    except OSError as exc:
        config_info += f"\nError getting pytest version: {exc}"

    return config_info


__all__ = [
    "analyze_test_coverage",
    "discover_tests",
    "get_test_details",
    "list_pytest_config",
    "run_tests",
]
