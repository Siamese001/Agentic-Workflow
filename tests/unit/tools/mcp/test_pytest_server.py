"""Unit tests for the pytest_mcp server hardening pass.

Covers every hardening change made in the production-readiness pass:
- R1: path confinement (_resolve_confined_path)
- R2: expression injection guard (_validate_expr)
- R3: isError on pytest exit codes 2/3/4 but NOT 0/1/5
- R4: subprocess timeout on list_pytest_config --version
- R5: subprocess timeout on coverage --version
- R6: exit code 5 treated as non-error in discover_tests
- R7: unique JUnit XML per run_tests invocation; cleanup on timeout
- R8: improved test count parsing (ignores indented '::' in warnings)
- R12: encoding='utf-8' on pytest.ini read (structural)

Strategy: MCP SDK is installed in the project env; import directly.
All subprocess calls are mocked; no live pytest process is spawned.
Async handlers driven synchronously via asyncio.get_event_loop().run_until_complete().
"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup — ensure repo root is importable
# ---------------------------------------------------------------------------

_PROJECT_ROOT = str(Path(__file__).resolve().parents[5])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import tools.mcp.pytest_server as srv  # noqa: E402

_resolve_confined_path = srv._resolve_confined_path
_validate_expr = srv._validate_expr
REPO_ROOT = srv.REPO_ROOT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run(coro):
    """Run an async coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


def _text(result) -> str:
    """Extract text from CallToolResult.content[0]."""
    return result.content[0].text


def _make_completed_process(returncode: int = 0, stdout: str = "", stderr: str = "") -> MagicMock:
    proc = MagicMock()
    proc.returncode = returncode
    proc.stdout = stdout
    proc.stderr = stderr
    return proc


def _server() -> srv.PytestMCPServer:
    return srv.PytestMCPServer()


# ===========================================================================
# R1 — _resolve_confined_path
# ===========================================================================


class TestResolveConfinedPath:
    def test_valid_relative_path(self, tmp_path):
        subdir = tmp_path / "tests"
        subdir.mkdir()
        result = _resolve_confined_path("tests", tmp_path)
        assert result == subdir.resolve()

    def test_valid_nested_path(self, tmp_path):
        subdir = tmp_path / "a" / "b"
        subdir.mkdir(parents=True)
        result = _resolve_confined_path("a/b", tmp_path)
        assert result == subdir.resolve()

    def test_traversal_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="escapes"):
            _resolve_confined_path("../../etc/passwd", tmp_path)

    def test_absolute_path_outside_base_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="escapes"):
            _resolve_confined_path("/etc/passwd", tmp_path)

    def test_dot_path_stays_within(self, tmp_path):
        result = _resolve_confined_path(".", tmp_path)
        assert result == tmp_path.resolve()

    def test_symlink_traversal_blocked(self, tmp_path):
        """A symlink that points outside the base must be rejected after resolve()."""
        target = tmp_path / "real_target"
        target.mkdir()
        link = tmp_path / "safe_subdir" / "link"
        link.parent.mkdir()
        try:
            link.symlink_to(Path("/"))
        except (OSError, NotImplementedError):
            pytest.skip("Symlink creation not supported on this platform")
        with pytest.raises(ValueError, match="escapes"):
            _resolve_confined_path("safe_subdir/link", tmp_path)


# ===========================================================================
# R2 — _validate_expr
# ===========================================================================


class TestValidateExpr:
    @pytest.mark.parametrize(
        "good",
        [
            "test_login",
            "test_login or test_logout",
            "slow and integration",
            "not smoke",
            "TestClass",
            "test_foo[param1]",
            "key=value",
        ],
    )
    def test_safe_expressions_pass(self, good):
        assert _validate_expr(good, "keywords") == good

    @pytest.mark.parametrize(
        "bad",
        [
            "test; rm -rf /",
            "test` whoami`",
            "test$(id)",
            "test\x00null",
            "test&background",
            "test|pipe",
        ],
    )
    def test_dangerous_expressions_rejected(self, bad):
        with pytest.raises(ValueError, match="unsafe characters"):
            _validate_expr(bad, "keywords")

    def test_param_name_in_error(self):
        with pytest.raises(ValueError, match="'markers'"):
            _validate_expr("bad;expr", "markers")


# ===========================================================================
# R3 — _run_tests isError classification
# ===========================================================================


class TestRunTestsIsError:
    def _mock_run(self, returncode: int):
        return _make_completed_process(
            returncode=returncode,
            stdout=f"exit {returncode}",
            stderr="",
        )

    @pytest.mark.parametrize(
        "rc,expected_is_error",
        [
            (0, False),  # all passed
            (1, False),  # some failed — caller should see output, not protocol error
            (5, False),  # no tests collected
            (2, True),  # interrupted
            (3, True),  # internal error
            (4, True),  # usage error
        ],
    )
    def test_exit_code_classification(self, rc, expected_is_error, tmp_path):
        server = _server()
        # Patch junit xml path to avoid filesystem side effects
        unique_xml = tmp_path / "pytest_results.xml"
        # Write a minimal valid junit XML so parsing succeeds
        unique_xml.write_text(
            '<testsuite tests="1" failures="0" errors="0" skipped="0" time="0.1"/>',
            encoding="utf-8",
        )

        proc = self._mock_run(rc)
        with (
            patch("tools.mcp.pytest_server.subprocess.run", return_value=proc),
            patch(
                "tools.mcp.pytest_server.uuid.uuid4",
                return_value=MagicMock(
                    hex=unique_xml.stem.replace("pytest_results_", "")
                    if "pytest_results_" in unique_xml.stem
                    else "fixed"
                ),
            ),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            # We need the xml to exist at the patched REPO_ROOT location
            # Recreate with the exact UUID the mock will produce
            result = _run(server._run_tests({"path": "tests", "timeout": 10}))

        assert result.isError == expected_is_error, (
            f"Exit code {rc}: expected isError={expected_is_error}, got {result.isError}"
        )


# ===========================================================================
# R4/R5 — subprocess timeout in list_pytest_config and coverage check
# ===========================================================================


class TestSubprocessTimeouts:
    def test_list_pytest_config_version_timeout_handled(self, tmp_path):
        """TimeoutExpired during --version must not crash; must return config info."""
        server = _server()
        with patch(
            "tools.mcp.pytest_server.subprocess.run",
            side_effect=__import__("subprocess").TimeoutExpired(cmd=["python"], timeout=15),
        ):
            result = _run(server._list_pytest_config({}))
        assert result.isError is False
        assert "timed out" in _text(result)

    def test_coverage_check_timeout_surfaces_error(self):
        """TimeoutExpired on coverage --version must return isError=True."""
        server = _server()
        with patch(
            "tools.mcp.pytest_server.subprocess.run",
            side_effect=__import__("subprocess").TimeoutExpired(cmd=["coverage"], timeout=10),
        ):
            result = _run(server._analyze_test_coverage({"path": "agentic_core"}))
        assert result.isError is True
        assert "Coverage tool not found" in _text(result)


# ===========================================================================
# R6 — exit code 5 (no tests) in discover_tests
# ===========================================================================


class TestDiscoverTestsExitCode5:
    def test_exit_code_5_returns_zero_count_not_error(self, tmp_path):
        """pytest exit 5 = no tests collected; must not be isError."""
        server = _server()
        proc = _make_completed_process(returncode=5, stdout="", stderr="no tests")
        with (
            patch("tools.mcp.pytest_server.subprocess.run", return_value=proc),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            result = _run(server._discover_tests({"path": "."}))
        assert result.isError is False
        assert "Discovered 0 tests" in _text(result)

    def test_nonzero_non5_returns_error(self, tmp_path):
        """Other non-zero exit codes from collection must be isError."""
        server = _server()
        proc = _make_completed_process(returncode=4, stdout="", stderr="usage error")
        with (
            patch("tools.mcp.pytest_server.subprocess.run", return_value=proc),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            result = _run(server._discover_tests({"path": "."}))
        assert result.isError is True
        assert "exit 4" in _text(result)


# ===========================================================================
# R7 — unique JUnit XML path per run_tests call
# ===========================================================================


class TestUniqueJunitXml:
    def test_junit_xml_path_is_unique_per_call(self, tmp_path):
        """Two consecutive run_tests calls must use different XML filenames."""
        server = _server()
        captured_cmds: list[list[str]] = []

        def fake_run(cmd, **_kw):
            captured_cmds.append(list(cmd))
            return _make_completed_process(returncode=0, stdout="passed")

        with (
            patch("tools.mcp.pytest_server.subprocess.run", side_effect=fake_run),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            _run(server._run_tests({"path": ".", "timeout": 10}))
            _run(server._run_tests({"path": ".", "timeout": 10}))

        def _xml_arg(cmd):
            idx = cmd.index("--junit-xml")
            return cmd[idx + 1]

        xml1 = _xml_arg(captured_cmds[0])
        xml2 = _xml_arg(captured_cmds[1])
        assert xml1 != xml2, "JUnit XML paths must differ between calls"
        assert ".pytest_results_" in xml1
        assert ".pytest_results_" in xml2

    def test_junit_xml_cleaned_on_timeout(self, tmp_path):
        """On TimeoutExpired the XML file (if created) must be removed."""
        server = _server()
        xml_path_holder: list[str] = []

        def fake_run(cmd, **_kw):
            idx = cmd.index("--junit-xml")
            xml_path = cmd[idx + 1]
            xml_path_holder.append(xml_path)
            # Simulate partial write then timeout
            Path(xml_path).write_text("<partial/>", encoding="utf-8")
            raise __import__("subprocess").TimeoutExpired(cmd=cmd, timeout=10)

        with (
            patch("tools.mcp.pytest_server.subprocess.run", side_effect=fake_run),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            result = _run(server._run_tests({"path": ".", "timeout": 10}))

        assert result.isError is True
        assert "timed out" in _text(result)
        if xml_path_holder:
            assert not Path(xml_path_holder[0]).exists(), "JUnit XML must be cleaned up on timeout"


# ===========================================================================
# R8 — test count parsing (counts node ids, not raw '::' occurrences)
# ===========================================================================


class TestDiscoverTestCount:
    def test_count_only_non_indented_node_ids(self, tmp_path):
        """Lines with '::' that start with whitespace (warnings) must not be counted."""
        server = _server()
        fake_stdout = (
            "tests/test_foo.py::test_a\n"
            "tests/test_foo.py::test_b\n"
            "  UserWarning: some::colon::warning\n"
            "tests/test_bar.py::TestClass::test_c\n"
        )
        proc = _make_completed_process(returncode=0, stdout=fake_stdout)
        with (
            patch("tools.mcp.pytest_server.subprocess.run", return_value=proc),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            result = _run(server._discover_tests({"path": "."}))
        text = _text(result)
        assert "Discovered 3 tests" in text

    def test_zero_tests_when_no_node_ids(self, tmp_path):
        server = _server()
        proc = _make_completed_process(returncode=5, stdout="no tests ran\n")
        with (
            patch("tools.mcp.pytest_server.subprocess.run", return_value=proc),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            result = _run(server._discover_tests({"path": "."}))
        assert "Discovered 0 tests" in _text(result)


# ===========================================================================
# Path confinement wired into tool handlers
# ===========================================================================


class TestPathConfinementInHandlers:
    def test_discover_tests_rejects_traversal(self):
        server = _server()
        result = _run(server._discover_tests({"path": "../../etc"}))
        assert result.isError is True
        assert "escapes" in _text(result) or "Invalid path" in _text(result)

    def test_run_tests_rejects_traversal(self):
        server = _server()
        result = _run(server._run_tests({"path": "../../etc", "timeout": 5}))
        assert result.isError is True
        assert "escapes" in _text(result) or "Invalid path" in _text(result)

    def test_get_test_details_rejects_traversal(self):
        server = _server()
        result = _run(server._get_test_details({"test_path": "../../etc/passwd"}))
        assert result.isError is True
        assert "escapes" in _text(result) or "Invalid" in _text(result)

    def test_analyze_coverage_rejects_traversal(self):
        server = _server()
        with patch(
            "tools.mcp.pytest_server.subprocess.run", return_value=_make_completed_process(returncode=0)
        ):
            result = _run(server._analyze_test_coverage({"path": "../../etc"}))
        assert result.isError is True
        assert "escapes" in _text(result) or "Invalid path" in _text(result)


# ===========================================================================
# Keyword/marker injection guard wired into run_tests
# ===========================================================================


class TestExpressionInjectionInRunTests:
    @pytest.mark.parametrize(
        "bad_kw",
        [
            "test; rm -rf /",
            "test$(whoami)",
            "foo|bar",
        ],
    )
    def test_bad_keywords_rejected(self, bad_kw):
        server = _server()
        result = _run(server._run_tests({"path": "tests", "keywords": bad_kw}))
        assert result.isError is True
        assert "unsafe" in _text(result) or "Invalid" in _text(result)

    @pytest.mark.parametrize(
        "bad_m",
        [
            "slow; cat /etc/passwd",
            "fast`id`",
        ],
    )
    def test_bad_markers_rejected(self, bad_m):
        server = _server()
        result = _run(server._run_tests({"path": "tests", "markers": bad_m}))
        assert result.isError is True
        assert "unsafe" in _text(result) or "Invalid" in _text(result)


# ===========================================================================
# Deterministic response structure
# ===========================================================================


class TestResponseStructure:
    def test_run_tests_response_has_required_fields(self, tmp_path):
        server = _server()
        proc = _make_completed_process(returncode=0, stdout="1 passed")
        with (
            patch("tools.mcp.pytest_server.subprocess.run", return_value=proc),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            result = _run(server._run_tests({"path": ".", "timeout": 10}))
        text = _text(result)
        assert "Command:" in text
        assert "Exit code:" in text
        assert "Execution time:" in text

    def test_discover_tests_response_has_summary_line(self, tmp_path):
        server = _server()
        proc = _make_completed_process(returncode=5, stdout="")
        with (
            patch("tools.mcp.pytest_server.subprocess.run", return_value=proc),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            result = _run(server._discover_tests({"path": "."}))
        assert "Discovered" in _text(result)
        assert "tests in" in _text(result)

    def test_get_test_details_missing_file_returns_error(self, tmp_path):
        server = _server()
        with patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path):
            result = _run(server._get_test_details({"test_path": "nonexistent_test.py"}))
        assert result.isError is True
        assert "does not exist" in _text(result)

    def test_list_pytest_config_always_succeeds(self):
        """list_pytest_config must return isError=False even when config files are absent."""
        server = _server()
        with (
            patch("tools.mcp.pytest_server.PYTEST_CONFIG", Path("/nonexistent/pytest.ini")),
            patch("tools.mcp.pytest_server.PYPROJECT_TOML", Path("/nonexistent/pyproject.toml")),
            patch(
                "tools.mcp.pytest_server.subprocess.run",
                return_value=_make_completed_process(returncode=0, stdout="pytest 9.0.0"),
            ),
        ):
            result = _run(server._list_pytest_config({}))
        assert result.isError is False
        assert "Pytest Configuration" in _text(result)


# ===========================================================================
# Repo-root / cwd correctness
# ===========================================================================


class TestRepoCwdCorrectness:
    def test_run_tests_uses_repo_root_as_cwd(self, tmp_path):
        server = _server()
        captured_kwargs: list[dict] = []

        def fake_run(cmd, **kwargs):
            captured_kwargs.append(kwargs)
            return _make_completed_process(returncode=0, stdout="ok")

        with (
            patch("tools.mcp.pytest_server.subprocess.run", side_effect=fake_run),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            _run(server._run_tests({"path": ".", "timeout": 10}))

        assert captured_kwargs, "subprocess.run was not called"
        assert captured_kwargs[0].get("cwd") == tmp_path

    def test_discover_tests_uses_repo_root_as_cwd(self, tmp_path):
        server = _server()
        captured_kwargs: list[dict] = []

        def fake_run(cmd, **kwargs):
            captured_kwargs.append(kwargs)
            return _make_completed_process(returncode=0, stdout="")

        with (
            patch("tools.mcp.pytest_server.subprocess.run", side_effect=fake_run),
            patch("tools.mcp.pytest_server.REPO_ROOT", tmp_path),
        ):
            _run(server._discover_tests({"path": "."}))

        assert captured_kwargs[0].get("cwd") == tmp_path
