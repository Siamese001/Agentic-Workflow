# adg-grep-ban: skip-file -- test fixtures contain grep/rg/mypy/pytest as string literals, not real invocations
# adg-mypy-ban: skip-file -- test fixtures contain mypy as string literal, not real invocation
# adg-pytest-ban: skip-file -- test fixtures contain pytest as string literal, not real invocation
"""Tests for adg_accelerator_compliance_gate.py (Wave 3 phase file).

Covers:
  - check_python_bans: happy path, failure path, edge cases
  - check_yaml_bans:   happy path, failure path, edge cases
  - _get_staged_files: OSError resilience (G2)
  - _BANNED_PYTHON_M_MYPY_RE: false-positive narrowing (G1)
  - path.relative_to(ROOT) ValueError fallback (G3)
  - ruff_severity_gate: blocking/non-blocking rc semantics
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest import mock

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _py_file(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(
        suffix=".py",
        mode="w",
        delete=False,
        encoding="utf-8",
        dir=tempfile.gettempdir(),
    )
    f.write(content)
    f.close()
    return Path(f.name)


def _yaml_file(content: str) -> Path:
    f = tempfile.NamedTemporaryFile(
        suffix=".yml",
        mode="w",
        delete=False,
        encoding="utf-8",
        dir=tempfile.gettempdir(),
    )
    f.write(content)
    f.close()
    return Path(f.name)


# ---------------------------------------------------------------------------
# check_python_bans
# ---------------------------------------------------------------------------


class TestCheckPythonBans:
    def test_happy_no_violations(self):
        """Clean file returns empty list."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file("import os\nprint('hello')\n")
        try:
            assert check_python_bans([p]) == []
        finally:
            os.unlink(p)

    def test_grep_subprocess_list_detected(self):
        """subprocess.run(['grep', ...]) triggers grep violation."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file('subprocess.run(["grep", "-r", "foo", "."])\n')
        try:
            issues = check_python_bans([p])
            assert len(issues) == 1
            assert issues[0]["check"] == "grep"
            assert issues[0]["kind"] == "python"
            assert issues[0]["line"] == 1
        finally:
            os.unlink(p)

    def test_mypy_direct_detected(self):
        """subprocess.run(['mypy', ...]) triggers mypy violation."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file('subprocess.run(["mypy", "src/"])\n')
        try:
            issues = check_python_bans([p])
            assert any(i["check"] == "mypy" for i in issues)
        finally:
            os.unlink(p)

    def test_pytest_direct_detected(self):
        """subprocess.run(['pytest', ...]) triggers pytest violation."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file('subprocess.run(["pytest", "tests/"])\n')
        try:
            issues = check_python_bans([p])
            assert any(i["check"] == "pytest" for i in issues)
        finally:
            os.unlink(p)

    def test_per_line_exemption_suppresses(self):
        """guardian: allow-grep exemption on same line suppresses detection."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file('subprocess.run(["grep", "foo"])  # guardian: allow-grep -- needed\n')
        try:
            assert check_python_bans([p]) == []
        finally:
            os.unlink(p)

    def test_file_level_skip_suppresses_all(self):
        """adg-grep-ban: skip-file in first 5 lines suppresses all grep violations."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file(
            '# adg-grep-ban: skip-file\nsubprocess.run(["grep", "-r", "x", "."])\n',
        )
        try:
            assert check_python_bans([p]) == []
        finally:
            os.unlink(p)

    def test_comment_only_line_skipped(self):
        """Lines that are pure comments are not scanned."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file('# subprocess.run(["grep", "foo"])\n')
        try:
            assert check_python_bans([p]) == []
        finally:
            os.unlink(p)

    def test_empty_list_returns_empty(self):
        """No files → no issues."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        assert check_python_bans([]) == []

    def test_nonexistent_file_skipped_no_crash(self):
        """Non-existent path (is_file() False) is silently skipped."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        assert check_python_bans([Path("/nonexistent/path/file.py")]) == []

    def test_path_outside_root_no_crash(self):
        """G3: file outside repo root must not raise ValueError from relative_to()."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file('subprocess.run(["grep", "foo"])\n')
        try:
            issues = check_python_bans([p])
            # should return issue with str(path) as file, not crash
            assert len(issues) == 1
            assert issues[0]["file"] == str(p)
        finally:
            os.unlink(p)

    def test_mypy_python_m_form_detected(self):
        """subprocess.run(['python', '-m', 'mypy', ...]) triggers mypy violation."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file("subprocess.run(['python', '-m', 'mypy', 'src/'])\n")
        try:
            issues = check_python_bans([p])
            assert any(i["check"] == "mypy" for i in issues)
        finally:
            os.unlink(p)

    def test_G1_python_subprocess_non_mypy_not_flagged(self):
        """G1 fix: subprocess.run(['python', 'setup.py']) must NOT trigger mypy violation."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file("subprocess.run(['python', 'setup.py', 'build'])\n")
        try:
            issues = check_python_bans([p])
            assert all(i["check"] != "mypy" for i in issues), f"FP mypy: {issues}"
        finally:
            os.unlink(p)

    def test_issue_dict_has_required_keys(self):
        """Issue dict must contain file, line, check, text, kind."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_python_bans

        p = _py_file('subprocess.run(["grep", "x"])\n')
        try:
            issues = check_python_bans([p])
            assert issues
            for key in ("file", "line", "check", "text", "kind"):
                assert key in issues[0], f"missing key: {key}"
        finally:
            os.unlink(p)


# ---------------------------------------------------------------------------
# check_yaml_bans
# ---------------------------------------------------------------------------


class TestCheckYamlBans:
    def test_happy_no_violations(self):
        """Clean YAML returns empty list."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        p = _yaml_file("jobs:\n  build:\n    steps:\n      - run: echo hello\n")
        try:
            assert check_yaml_bans([p]) == []
        finally:
            os.unlink(p)

    def test_inline_grep_detected(self):
        """Inline run: grep ... triggers grep-yaml violation."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        p = _yaml_file("jobs:\n  build:\n    steps:\n      - run: grep -r foo .\n")
        try:
            issues = check_yaml_bans([p])
            assert len(issues) >= 1
            assert issues[0]["check"] == "grep-yaml"
            assert issues[0]["kind"] == "yaml"
        finally:
            os.unlink(p)

    def test_per_line_exemption_suppresses(self):
        """guardian: allow-grep-yaml on same line suppresses detection."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        p = _yaml_file(
            "jobs:\n  build:\n    steps:\n      - run: grep foo .  # guardian: allow-grep-yaml -- ci only\n",
        )
        try:
            assert check_yaml_bans([p]) == []
        finally:
            os.unlink(p)

    def test_file_level_skip_suppresses(self):
        """adg-yaml-grep-ban: skip-file suppresses all YAML violations."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        p = _yaml_file(
            "# adg-yaml-grep-ban: skip-file\njobs:\n  build:\n    steps:\n      - run: grep foo .\n",
        )
        try:
            assert check_yaml_bans([p]) == []
        finally:
            os.unlink(p)

    def test_empty_list_returns_empty(self):
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        assert check_yaml_bans([]) == []

    def test_path_outside_root_no_crash(self):
        """G3: YAML file outside repo root must not raise ValueError."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        p = _yaml_file("jobs:\n  build:\n    steps:\n      - run: grep foo .\n")
        try:
            issues = check_yaml_bans([p])
            assert len(issues) >= 1
            assert issues[0]["file"] == str(p)
        finally:
            os.unlink(p)

    def test_rg_alias_detected(self):
        """rg (ripgrep alias) in run: step is also caught."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        p = _yaml_file("jobs:\n  build:\n    steps:\n      - run: rg pattern .\n")
        try:
            issues = check_yaml_bans([p])
            assert len(issues) >= 1
        finally:
            os.unlink(p)

    def test_echo_not_flagged(self):
        """echo in run: does not trigger grep-yaml."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import check_yaml_bans

        p = _yaml_file("jobs:\n  build:\n    steps:\n      - run: echo done\n")
        try:
            assert check_yaml_bans([p]) == []
        finally:
            os.unlink(p)


# ---------------------------------------------------------------------------
# _get_staged_files
# ---------------------------------------------------------------------------


class TestGetStagedFiles:
    def test_G2_bad_cwd_returns_empty_list(self):
        """G2 fix: OSError from invalid cwd must return [] not crash."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import _get_staged_files

        result = _get_staged_files(Path("C:/nonexistent_xyz_adg_gate"))
        assert result == []

    def test_returns_list(self):
        """Returns a list (possibly empty) from a valid repo root."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import ROOT, _get_staged_files

        result = _get_staged_files(ROOT)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# _BANNED_PYTHON_M_MYPY_RE pattern (G1 regression)
# ---------------------------------------------------------------------------


class TestMypyPattern:
    def test_G1_plain_python_call_not_matched(self):
        """G1: subprocess.run(['python', 'script.py']) must NOT match mypy pattern."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import _BANNED_PYTHON_M_MYPY_RE

        assert not _BANNED_PYTHON_M_MYPY_RE.search("subprocess.run(['python', 'setup.py', 'build'])")

    def test_python_m_mypy_matched(self):
        """subprocess.run(['python', '-m', 'mypy', ...]) MUST match."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import _BANNED_PYTHON_M_MYPY_RE

        assert _BANNED_PYTHON_M_MYPY_RE.search("subprocess.run(['python', '-m', 'mypy', 'src'])")

    def test_python_c_not_matched(self):
        """subprocess.run(['python', '-c', ...]) must NOT match."""
        from ops_scripts.ci.adg_accelerator_compliance_gate import _BANNED_PYTHON_M_MYPY_RE

        assert not _BANNED_PYTHON_M_MYPY_RE.search("subprocess.run(['python', '-c', 'import sys'])")


# ---------------------------------------------------------------------------
# ruff_severity_gate semantics
# ---------------------------------------------------------------------------


class TestRuffSeverityGate:
    def test_blocking_pass_rc_propagated(self):
        """main() returns blocking pass rc (1) even if non-blocking passes."""
        from ops_scripts.ci.ruff_severity_gate import main

        with mock.patch("ops_scripts.ci.ruff_severity_gate._run_ruff", side_effect=[1, 0]):
            assert main() == 1

    def test_nonblocking_rc_ignored(self):
        """main() returns 0 when blocking passes even if non-blocking returns non-zero."""
        from ops_scripts.ci.ruff_severity_gate import main

        with mock.patch("ops_scripts.ci.ruff_severity_gate._run_ruff", side_effect=[0, 99]):
            assert main() == 0

    def test_run_ruff_returns_int(self):
        """_run_ruff returns an integer return code."""
        from ops_scripts.ci.ruff_severity_gate import _BLOCKING_RULES, _run_ruff

        rc = _run_ruff(_BLOCKING_RULES, [], [])
        assert isinstance(rc, int)

    def test_both_passes_called(self):
        """main() always calls _run_ruff twice (blocking + non-blocking)."""
        from ops_scripts.ci.ruff_severity_gate import main

        with mock.patch("ops_scripts.ci.ruff_severity_gate._run_ruff", return_value=0) as m:
            main()
            assert m.call_count == 2
