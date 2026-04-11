#!/usr/bin/env python3
"""
Pytest MCP Server - Test discovery, execution, and analysis
Provides pytest integration for Windsurf with comprehensive test management
"""

import json
import logging
import re
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import anyio

# MCP imports
try:
    from mcp.server import Server
    from mcp.server.lowlevel.server import NotificationOptions
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        CallToolResult,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError:
    print("MCP SDK not found. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging - use stderr to avoid interfering with MCP protocol on stdout
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

# Configuration
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
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


class PytestMCPServer:
    def __init__(self):
        self.server = Server("pytest")
        self._setup_handlers()

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available pytest tools"""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="discover_tests",
                        description="Discover all tests in the repository",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Path to search for tests (default: tests/)",
                                    "default": "tests",
                                },
                                "pattern": {
                                    "type": "string",
                                    "description": "Test file pattern (default: test_*.py)",
                                    "default": "test_*.py",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="run_tests",
                        description="Run pytest with specified options",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Test path or file",
                                    "default": "tests",
                                },
                                "keywords": {
                                    "type": "string",
                                    "description": "Run tests matching keywords",
                                },
                                "markers": {
                                    "type": "string",
                                    "description": "Run tests with specific markers",
                                },
                                "verbose": {
                                    "type": "boolean",
                                    "description": "Verbose output",
                                    "default": True,
                                },
                                "coverage": {
                                    "type": "boolean",
                                    "description": "Generate coverage report",
                                    "default": False,
                                },
                                "timeout": {
                                    "type": "integer",
                                    "description": "Timeout in seconds (max 300)",
                                    "default": 60,
                                    "maximum": 300,
                                },
                            },
                        },
                    ),
                    Tool(
                        name="get_test_details",
                        description="Get detailed information about a specific test",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "test_path": {
                                    "type": "string",
                                    "description": "Path to test file",
                                },
                                "test_name": {
                                    "type": "string",
                                    "description": "Specific test function name",
                                },
                            },
                            "required": ["test_path"],
                        },
                    ),
                    Tool(
                        name="analyze_test_coverage",
                        description="Analyze test coverage for the repository",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "Path to analyze coverage for",
                                    "default": "agentic_core",
                                },
                                "format": {
                                    "type": "string",
                                    "description": "Output format (text, json, html)",
                                    "default": "text",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="list_pytest_config",
                        description="Show pytest configuration",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                ],
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
            """Handle tool calls"""
            try:
                if name == "discover_tests":
                    return await self._discover_tests(arguments)
                elif name == "run_tests":
                    return await self._run_tests(arguments)
                elif name == "get_test_details":
                    return await self._get_test_details(arguments)
                elif name == "analyze_test_coverage":
                    return await self._analyze_test_coverage(arguments)
                elif name == "list_pytest_config":
                    return await self._list_pytest_config(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    async def _discover_tests(self, args: dict[str, Any]) -> CallToolResult:
        """Discover all tests in the repository"""
        try:
            search_path = _resolve_confined_path(args.get("path", "tests"), REPO_ROOT)
        except ValueError as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Invalid path: {exc}")],
                isError=True,
            )
        pattern = args.get("pattern", "test_*.py")

        if not search_path.exists():
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Test path {search_path} does not exist",
                    )
                ],
                isError=True,
            )

        # Use pytest to collect tests
        cmd = ["python", "-m", "pytest", "--collect-only", "-q", str(search_path)]

        try:
            result = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # exit code 5 = no tests collected — not an error, return zero-test result
            if result.returncode not in (0, 5):
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=(
                                f"Error collecting tests (exit {result.returncode}):\n"
                                f"{result.stderr or result.stdout}"
                            ),
                        )
                    ],
                    isError=True,
                )

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

            return CallToolResult(
                content=[TextContent(type="text", text=summary)],
            )

        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text="Test discovery timed out")],
                isError=True,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Discovery error: {str(e)}")],
                isError=True,
            )

    async def _run_tests(self, args: dict[str, Any]) -> CallToolResult:
        """Run pytest with specified options"""
        try:
            _raw_path = args.get("path", "tests")
            # Resolve and confine the test path
            resolved_test_path = _resolve_confined_path(str(_raw_path), REPO_ROOT)
        except ValueError as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Invalid path: {exc}")],
                isError=True,
            )

        keywords = args.get("keywords")
        markers = args.get("markers")
        verbose = args.get("verbose", True)
        coverage = args.get("coverage", False)
        timeout = min(args.get("timeout", 60), MAX_EXECUTION_TIME)

        try:
            if keywords:
                keywords = _validate_expr(keywords, "keywords")
            if markers:
                markers = _validate_expr(markers, "markers")
        except ValueError as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Invalid argument: {exc}")],
                isError=True,
            )

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
            result = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
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
            is_error = result.returncode not in (0, 1, 5)
            return CallToolResult(
                content=[TextContent(type="text", text=output)],
                isError=is_error,
            )

        except subprocess.TimeoutExpired:
            # Best-effort cleanup of junit xml on timeout
            try:
                if junit_xml.exists():
                    junit_xml.unlink()
            except OSError:
                pass
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Tests timed out after {timeout} seconds",
                    )
                ],
                isError=True,
            )
        except (OSError, ValueError) as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Test execution error: {str(e)}")],
                isError=True,
            )

    async def _get_test_details(self, args: dict[str, Any]) -> CallToolResult:
        """Get detailed information about a specific test"""
        try:
            test_path = _resolve_confined_path(args["test_path"], REPO_ROOT)
        except (ValueError, KeyError) as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Invalid test_path: {exc}")],
                isError=True,
            )
        test_name = args.get("test_name")

        if not test_path.exists():
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Test file {test_path} does not exist",
                    )
                ],
                isError=True,
            )

        try:
            # Read the test file
            with open(test_path, encoding="utf-8") as f:
                content = f.read()

            # Basic analysis
            lines = content.split("\n")
            total_lines = len(lines)
            import_lines = len([line for line in lines if line.strip().startswith("import")])
            function_count = len([line for line in lines if line.strip().startswith("def test_")])

            details = f"Test File: {test_path.relative_to(REPO_ROOT)}\n"
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

            return CallToolResult(
                content=[TextContent(type="text", text=details)],
            )

        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error reading test file: {str(e)}")],
                isError=True,
            )

    async def _analyze_test_coverage(self, args: dict[str, Any]) -> CallToolResult:
        """Analyze test coverage for the repository"""
        path = args.get("path", "agentic_core")
        format_type = args.get("format", "text")

        # Check if coverage is available
        try:
            subprocess.run(["coverage", "--version"], capture_output=True, check=True, timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text="Coverage tool not found. Install with: pip install coverage",
                    )
                ],
                isError=True,
            )

        try:
            target_path = _resolve_confined_path(path, REPO_ROOT)
        except ValueError as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Invalid path: {exc}")],
                isError=True,
            )
        if not target_path.exists():
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=f"Path {target_path} does not exist",
                    )
                ],
                isError=True,
            )

        cmd = [
            "python",
            "-m",
            "pytest",
            f"--cov={path}",
            f"--cov-report={format_type}",
            "--cov-report=term",
            "tests",
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=120,
            )

            output = f"Coverage analysis for: {path}\n"
            output += f"Format: {format_type}\n"
            output += f"Command: {' '.join(cmd)}\n\n"

            if result.stdout:
                output += result.stdout

            if result.stderr:
                output += f"\nSTDERR:\n{result.stderr}"

            return CallToolResult(
                content=[TextContent(type="text", text=output)],
            )

        except subprocess.TimeoutExpired:
            return CallToolResult(
                content=[TextContent(type="text", text="Coverage analysis timed out")],
                isError=True,
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Coverage error: {str(e)}")],
                isError=True,
            )

    async def _list_pytest_config(self, args: dict[str, Any]) -> CallToolResult:
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
            except Exception as e:
                config_info += f"Error reading pyproject.toml: {e}\n"
        else:
            config_info += "pyproject.toml: not found\n"

        # Show pytest location and version
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            config_info += f"\nPytest version:\n{result.stdout}"
        except subprocess.TimeoutExpired:
            config_info += "\nError getting pytest version: timed out"
        except OSError as e:
            config_info += f"\nError getting pytest version: {e}"

        return CallToolResult(
            content=[TextContent(type="text", text=config_info)],
        )


async def main():
    """Main entry point"""
    server_instance = PytestMCPServer()

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pytest",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=NotificationOptions(
                        prompts_changed=False,
                        resources_changed=False,
                        tools_changed=False,
                    ),
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("Pytest MCP Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
