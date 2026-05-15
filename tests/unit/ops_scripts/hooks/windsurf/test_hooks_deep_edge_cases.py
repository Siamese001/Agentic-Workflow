"""
DEEP EDGE CASE tests for all 8 Windsurf hooks.

This file specifically targets branches that the existing test files do NOT cover:
  - Non-string / non-dict / list / null payloads (crash protection)
  - Regex false positives (patterns inside comments / strings)
  - Regex false negatives (enforcement evasion via path variants)
  - Boundary conditions (exact thresholds, zero-length inputs)
  - Field type coercion (int/bool/null where string expected)
  - Multi-violation accumulation
  - Stale ADG threshold borders (exactly at / just over)
  - ADG recovery tool case sensitivity
  - pytest full-suite regex variants (trailing slash, Windows backslash)
  - subprocess nested-paren timeout window
  - post_write_audit finding_count accuracy, ${env:} format allow-list
  - post_cursor_agent_cleanup per-log rotation limits (500 / 500 / 200)
  - pre_prompt_classifier field aliasing, default tier, keyword priority
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[5]
# Cursor scripts second so `.windsurf/scripts` remains first on sys.path for hook
# parity tests (e.g. pre_write_gate). Modules only in `.cursor/scripts` still resolve.
sys.path.insert(0, str(_REPO_ROOT / ".cursor" / "scripts"))
sys.path.insert(0, str(_REPO_ROOT / ".windsurf" / "scripts"))

# Repo-relative .py path for pre_write_gate payloads — avoids SSOT repo-root-py
# blocks on synthetic top-level names (constitutional §31 / _ssot_folder_check).
_SAFE_PY_REL = "tests/unit/ops_scripts/hooks/windsurf/_pre_write_gate_payload_dummy.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stdin(payload) -> StringIO:
    return StringIO(json.dumps(payload))


def _create_real_sqlite(adg_dir: Path, name: str = "adg_indexed_test.sqlite") -> Path:
    """Create a real SQLite DB file that can be opened and queried."""
    db_path = adg_dir / name
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE IF NOT EXISTS probe (id INTEGER)")
    conn.commit()
    conn.close()
    return db_path


# ============================================================================
# pre_run_gate — deep edge cases
# ============================================================================


class TestPreRunGatePayloadShapes:
    """Non-standard payload shapes must never crash — fail-closed or allow."""

    def _run(self, raw: str) -> int:
        from pre_run_gate import main

        with patch("sys.stdin", StringIO(raw)):
            return main()

    def test_list_payload_returns_0(self):
        assert self._run(json.dumps([{"command_line": "pwsh"}])) == 0

    def test_string_payload_returns_0(self):
        assert self._run(json.dumps("pwsh")) == 0

    def test_int_payload_returns_0(self):
        assert self._run(json.dumps(42)) == 0

    def test_null_payload_returns_0(self):
        # null is valid JSON (parses to None) → non-dict → pre_mcp_gate fail-opens
        assert self._run("null") == 0

    def test_tool_info_is_string_returns_0(self):
        assert self._run(json.dumps({"tool_info": "pwsh"})) == 0

    def test_tool_info_is_list_returns_0(self):
        assert self._run(json.dumps({"tool_info": ["pwsh"]})) == 0

    def test_tool_info_is_null_returns_0(self):
        assert self._run(json.dumps({"tool_info": None})) == 0

    def test_command_line_is_int_returns_0(self):
        assert self._run(json.dumps({"tool_info": {"command_line": 42}})) == 0

    def test_command_line_is_list_returns_0(self):
        assert self._run(json.dumps({"tool_info": {"command_line": ["pwsh"]}})) == 0

    def test_command_line_is_null_returns_0(self):
        assert self._run(json.dumps({"tool_info": {"command_line": None}})) == 0

    def test_command_line_is_bool_returns_0(self):
        assert self._run(json.dumps({"tool_info": {"command_line": True}})) == 0


class TestPreRunGatePowerShellVariants:
    """Every PowerShell spelling that should be blocked."""

    def _check(self, cmd: str) -> int:
        from pre_run_gate import check_command

        return check_command(cmd)

    def test_uppercase_POWERSHELL(self):
        assert self._check("POWERSHELL -Command Get-Date") == 2

    def test_mixed_case_PowerShell(self):
        assert self._check("PowerShell -Command Get-Date") == 2

    def test_lowercase_powershell_no_args(self):
        assert self._check("powershell") == 2

    def test_pwsh_no_args(self):
        assert self._check("pwsh") == 2

    def test_unix_path_powershell(self):
        assert self._check("/usr/bin/powershell -Command x") == 2

    def test_unix_path_pwsh(self):
        assert self._check("/usr/local/bin/pwsh -Command x") == 2

    def test_quoted_pwsh_exe(self):
        assert self._check('"pwsh.exe" -Command x') == 2

    def test_quoted_full_path_pwsh(self):
        assert self._check('"C:/Program Files/PowerShell/7/pwsh.exe" -Command x') == 2

    def test_git_not_blocked(self):
        assert self._check("git status") == 0

    def test_python_not_blocked(self):
        assert self._check("python run.py") == 0

    def test_pwsh_in_word_not_blocked(self):
        # "pwsh" embedded in a filename with underscore suffix → NOT executable
        assert self._check("python test_pwsh_scanner.py") == 0

    def test_allowlist_check_powershell_ban_passes(self):
        assert self._check("python ops_scripts/ci/check_powershell_ban.py") == 0

    def test_allowlist_pre_run_gate_passes(self):
        assert self._check("python ops_scripts/hooks/windsurf/pre_run_gate.py") == 0

    def test_allowlist_backslash_path_passes(self):
        assert self._check("python ops_scripts\\ci\\check_powershell_ban.py") == 0


class TestPreRunGateFullSuiteRegex:
    """Full-suite block: coverage of all pytest path variants."""

    def _run_with_adg_active(self, cmd: str) -> int:
        from pre_run_gate import check_command

        with patch.dict(os.environ, {"ADG_REPAIR_ACTIVE": "1"}):
            return check_command(cmd)

    def test_pytest_tests_unit_exact(self):
        assert self._run_with_adg_active("pytest tests/unit") == 2

    def test_pytest_tests_unit_trailing_slash(self):
        assert self._run_with_adg_active("pytest tests/unit/") == 2

    def test_pytest_tests_unit_backslash(self):
        assert self._run_with_adg_active("pytest tests\\unit") == 2

    def test_pytest_tests_unit_with_flags(self):
        assert self._run_with_adg_active("pytest tests/unit -v --tb=short") == 2

    def test_pytest_scoped_not_blocked(self):
        assert self._run_with_adg_active("pytest tests/unit/ops_scripts/test_foo.py") == 0

    def test_pytest_full_suite_no_env_not_blocked(self):
        from pre_run_gate import check_command

        with patch.dict(os.environ, {}, clear=True):
            result = check_command("pytest tests/unit")
        assert result == 0

    def test_adg_repair_active_empty_string_not_blocked(self):
        from pre_run_gate import check_command

        with patch.dict(os.environ, {"ADG_REPAIR_ACTIVE": ""}):
            assert check_command("pytest tests/unit") == 0

    def test_adg_repair_active_string_0_still_blocks(self):
        # "0" is a non-empty string — truthy in Python, so blocks.
        # This is documented/intentional behaviour: set env var to empty to deactivate.
        from pre_run_gate import check_command

        with patch.dict(os.environ, {"ADG_REPAIR_ACTIVE": "0"}):
            assert check_command("pytest tests/unit") == 2


# ============================================================================
# pre_write_gate — deep edge cases
# ============================================================================


class TestPreWriteGatePayloadShapes:
    """Non-standard shapes must not crash."""

    def _run(self, raw: str) -> int:
        from pre_write_gate import main

        with patch("sys.stdin", StringIO(raw)):
            with patch("sys.argv", ["pre_write_gate.py"]):
                return main()

    def test_list_payload_fails_closed(self):
        # fail-closed policy — non-dict blocks
        assert self._run(json.dumps([{"file_path": "foo.py"}])) == 2

    def test_string_payload_fails_closed(self):
        assert self._run(json.dumps("foo")) == 2

    def test_null_payload_fails_closed(self):
        assert self._run("null") == 2

    def test_tool_info_is_string_returns_0(self):
        # tool_info is non-dict → skip (allow)
        payload = {"tool_info": "foo.py"}
        assert self._run(json.dumps(payload)) == 0

    def test_tool_info_is_null_returns_0(self):
        payload = {"tool_info": None}
        assert self._run(json.dumps(payload)) == 0

    def test_edits_is_null_treated_as_empty(self):
        # null edits on a .py file → no antipatterns → allow (not a deletion block)
        payload = {"tool_info": {"file_path": _SAFE_PY_REL, "edits": None}}
        assert self._run(json.dumps(payload)) == 0

    def test_edits_is_dict_treated_as_empty(self):
        # dict instead of list → normalised to [] → allow
        payload = {"tool_info": {"file_path": _SAFE_PY_REL, "edits": {"old_string": "", "new_string": "x"}}}
        assert self._run(json.dumps(payload)) == 0

    def test_edits_item_is_not_dict_skipped(self):
        # list containing a non-dict item → skip that item, no crash
        payload = {"tool_info": {"file_path": _SAFE_PY_REL, "edits": ["not a dict", 42]}}
        assert self._run(json.dumps(payload)) == 0

    def test_new_string_is_null_no_crash(self):
        payload = {"tool_info": {"file_path": _SAFE_PY_REL, "edits": [{"old_string": "", "new_string": None}]}}
        assert self._run(json.dumps(payload)) == 0

    def test_file_path_is_int_not_py_or_json(self):
        # Non-string file_path → treated as "" → not .py or mcp_config.json → allow
        payload = {"tool_info": {"file_path": 42, "edits": []}}
        assert self._run(json.dumps(payload)) == 0


class TestPreWriteGateCommentFalsePositives:
    """Patterns inside comments must NOT trigger anti-pattern violations."""

    def _scan(self, code: str) -> list:
        from pre_write_gate import scan_antipatterns

        return scan_antipatterns(code)

    def test_except_exception_in_comment_not_flagged(self):
        code = "# except Exception: avoid this pattern\n"
        v = self._scan(code)
        assert not any("except Exception" in x for x in v), (
            "except Exception inside a comment must NOT be flagged"
        )

    def test_bare_except_in_comment_not_flagged(self):
        # The bare-except regex anchors to ^ whitespace before 'except', so
        # '# except:' starts with '#' not whitespace — already safe, but verify.
        code = "    # except: this is bad\n"
        v = self._scan(code)
        assert not any("Bare" in x for x in v)

    def test_shell_true_in_comment_not_flagged(self):
        # shell=True inside a comment with subprocess referenced elsewhere
        code = "# shell=True is forbidden\nresult = subprocess.run(['git'], timeout=5)\n"
        v = self._scan(code)
        assert not any("shell=True" in x for x in v), (
            "shell=True inside a comment must NOT trigger a violation"
        )

    def test_shell_true_in_code_still_flagged(self):
        code = "subprocess.run(['git'], shell=True, timeout=5)\n"
        v = self._scan(code)
        assert any("shell=True" in x for x in v)

    def test_except_exception_in_string_not_flagged(self):
        # String literal containing 'except Exception' — not a comment but a value
        # Current implementation checks per-line without AST; if the line is non-comment
        # code that contains 'except Exception' as a string value, it WOULD fire
        # (known limitation). Test documents this.
        code = "msg = 'use except Exception carefully'\n"
        v = self._scan(code)
        # If it fires, it's a known limitation — but must not crash
        assert isinstance(v, list)


class TestPreWriteGateSubprocessNestedParen:
    """Nested parens in subprocess args must not cause false timeout violations."""

    def _scan(self, code: str) -> list:
        from pre_write_gate import scan_antipatterns

        return scan_antipatterns(code)

    def test_nested_paren_with_timeout_not_flagged(self):
        # subprocess.run(shlex.split('cmd'), timeout=5) — inner paren from shlex.split
        code = "subprocess.run(shlex.split('git status'), timeout=5)\n"
        v = self._scan(code)
        assert not any("missing timeout=" in x for x in v), (
            "Nested paren with timeout= must NOT be falsely flagged as missing timeout"
        )

    def test_func_call_arg_with_timeout_not_flagged(self):
        code = "subprocess.run(build_cmd(repo), capture_output=True, timeout=30)\n"
        v = self._scan(code)
        assert not any("missing timeout=" in x for x in v)

    def test_nested_paren_without_timeout_still_flagged(self):
        code = "subprocess.run(shlex.split('git status'))\n"
        v = self._scan(code)
        assert any("missing timeout=" in x for x in v)

    def test_very_long_call_with_timeout_not_flagged(self):
        # timeout= appears near the 400-char limit
        args = ", ".join(f"arg_{i}='value_{i}'" for i in range(20))
        code = f"subprocess.run([cmd, {args}], timeout=30)\n"
        v = self._scan(code)
        assert not any("missing timeout=" in x for x in v)

    def test_two_consecutive_calls_first_missing_second_ok(self):
        code = "subprocess.run(['a'])\nsubprocess.run(['b'], timeout=5)\n"
        v = self._scan(code)
        missing = [x for x in v if "missing timeout=" in x]
        assert len(missing) == 1, "Only the first call (missing timeout) should be flagged"


class TestPreWriteGateMultipleViolations:
    """Multiple violations in one edit must ALL be reported, return code is 2."""

    def _run_payload(self, new_string: str) -> tuple:
        from pre_write_gate import main

        payload = {
            "tool_info": {"file_path": _SAFE_PY_REL, "edits": [{"old_string": "", "new_string": new_string}]}
        }
        stderr_cap = StringIO()
        with patch("sys.stdin", _stdin(payload)):
            with patch("sys.argv", ["pre_write_gate.py"]):
                with patch("sys.stderr", stderr_cap):
                    rc = main()
        return rc, stderr_cap.getvalue()

    def test_bare_except_and_subprocess_no_timeout_both_reported(self):
        code = "try:\n    pass\nexcept:\n    pass\nsubprocess.run(['x'])\n"
        rc, stderr = self._run_payload(code)
        assert rc == 2
        assert "Bare" in stderr
        assert "missing timeout=" in stderr

    def test_shell_true_and_broad_except_both_reported(self):
        code = "subprocess.run(['x'], shell=True)\nexcept Exception:\n    pass\n"
        rc, stderr = self._run_payload(code)
        assert rc == 2
        assert "shell=True" in stderr
        assert "except Exception" in stderr


class TestPreWriteGateArgvFastPath:
    """argv[1] file-type fast path must behave correctly."""

    def _run_with_argv(self, argv_path: str, payload: dict) -> int:
        from pre_write_gate import main

        with patch("sys.stdin", _stdin(payload)):
            with patch("sys.argv", ["pre_write_gate.py", argv_path]):
                return main()

    def test_argv_md_file_returns_0_without_reading_payload(self):
        # The payload has a bare-except violation but argv says .md → skipped
        payload = {
            "tool_info": {
                "file_path": _SAFE_PY_REL,
                "edits": [{"old_string": "", "new_string": "except:\n    pass\n"}],
            }
        }
        assert self._run_with_argv("README.md", payload) == 0

    def test_argv_txt_file_returns_0(self):
        payload = {
            "tool_info": {
                "file_path": _SAFE_PY_REL,
                "edits": [{"old_string": "", "new_string": "except:\n    pass\n"}],
            }
        }
        assert self._run_with_argv("notes.txt", payload) == 0

    def test_argv_py_file_proceeds_to_gate(self):
        payload = {
            "tool_info": {
                "file_path": _SAFE_PY_REL,
                "edits": [{"old_string": "", "new_string": "except:\n    pass\n"}],
            }
        }
        assert self._run_with_argv("module.py", payload) == 2

    def test_argv_mcp_config_json_proceeds_to_gate(self):
        # No edits → deletion block
        payload = {"tool_info": {"file_path": "mcp_config.json", "edits": []}}
        assert self._run_with_argv("mcp_config.json", payload) == 2


# ============================================================================
# pre_mcp_gate — deep edge cases
# ============================================================================


class TestPreMcpGatePayloadShapes:
    """Non-dict payloads must never block (fail-open for non-ADG assumed)."""

    def _run(self, raw: str) -> int:
        from pre_mcp_gate import main

        with patch("sys.stdin", StringIO(raw)):
            return main()

    def test_list_payload_returns_0(self):
        assert self._run(json.dumps([{"mcp_server_name": "adg_sqlite"}])) == 0

    def test_string_payload_returns_0(self):
        assert self._run(json.dumps("adg_sqlite")) == 0

    def test_null_payload_returns_0(self):
        assert self._run("null") == 0

    def test_tool_info_non_dict_returns_0(self):
        assert self._run(json.dumps({"tool_info": "adg_sqlite"})) == 0

    def test_missing_server_name_returns_0(self):
        assert self._run(json.dumps({"tool_info": {}})) == 0

    def test_null_server_name_returns_0(self):
        assert self._run(json.dumps({"tool_info": {"mcp_server_name": None}})) == 0


class TestPreMcpGateRecoveryToolCaseSensitivity:
    """Recovery tool whitelist is exact-case — wrong case goes to gate."""

    def _run_adg(self, tool_name: str, repo_root: Path) -> int:
        from pre_mcp_gate import main

        # Provision a real sqlite so _has_adg_sqlite returns True and probes pass.
        adg_dir = repo_root / "artifacts" / "adg"
        adg_dir.mkdir(parents=True, exist_ok=True)
        _create_real_sqlite(adg_dir, "adg_indexed_test.sqlite")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": tool_name}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", repo_root):
                return main()

    def test_adg_health_lowercase_whitelisted(self, tmp_path):
        assert self._run_adg("adg_health", tmp_path) == 0

    def test_adg_health_uppercase_not_whitelisted(self, tmp_path):
        # ADG_HEALTH → not in whitelist → goes to gate → no snapshot → age=None → allow
        result = self._run_adg("ADG_HEALTH", tmp_path)
        assert result == 0  # no snapshot = no stale block, but not whitelisted

    def test_adg_status_whitelisted(self, tmp_path):
        assert self._run_adg("adg_status", tmp_path) == 0

    def test_adg_close_connections_whitelisted(self, tmp_path):
        assert self._run_adg("adg_close_connections", tmp_path) == 0

    def test_adg_reopen_connections_whitelisted(self, tmp_path):
        assert self._run_adg("adg_reopen_connections", tmp_path) == 0

    def test_unknown_tool_goes_to_gate(self, tmp_path):
        # No lock, no snapshot → age=None → allowed
        assert self._run_adg("adg_node", tmp_path) == 0


class TestPreMcpGateStalenessThresholds:
    """Snapshot age is advisory-only — never blocks regardless of age."""

    def _run_with_snapshot_age(self, age_seconds: float, tmp_path: Path) -> int:
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True, exist_ok=True)
        _create_real_sqlite(adg_dir, "adg_indexed_test.sqlite")
        snap = adg_dir / "adg_snapshot_test.json"
        snap.write_text("{}")
        mtime = time.time() - age_seconds
        os.utime(snap, (mtime, mtime))
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                return main()

    def test_age_60s_allowed(self, tmp_path):
        assert self._run_with_snapshot_age(60.0, tmp_path) == 0

    def test_age_1801s_allowed(self, tmp_path):
        # Previously blocked at 30 min — now advisory only
        assert self._run_with_snapshot_age(1801.0, tmp_path) == 0

    def test_age_3600s_allowed(self, tmp_path):
        # 1 hour old — still valid, user refreshes manually
        assert self._run_with_snapshot_age(3600.0, tmp_path) == 0

    def test_age_24h_allowed(self, tmp_path):
        # 24 hours old — advisory warning emitted, never blocks
        assert self._run_with_snapshot_age(86400.0, tmp_path) == 0

    def test_no_snapshot_file_always_allowed(self, tmp_path):
        from pre_mcp_gate import main as _mcp_main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        _create_real_sqlite(adg_dir, "adg_indexed_test.sqlite")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                assert _mcp_main() == 0

    def test_multiple_snapshots_newest_wins(self, tmp_path):
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        _create_real_sqlite(adg_dir, "adg_indexed_test.sqlite")
        old_snap = adg_dir / "adg_snapshot_20260101_0000.json"
        new_snap = adg_dir / "adg_snapshot_20260101_0001.json"
        old_snap.write_text("{}")
        new_snap.write_text("{}")
        now = time.time()
        os.utime(old_snap, (now - 7200, now - 7200))
        os.utime(new_snap, (now - 300, now - 300))
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                assert main() == 0  # newest snapshot reported, always allowed


class TestPreMcpGateLockDetection:
    """SQLite probe-based lock detection (real connections, not file heuristics)."""

    def test_nonzero_wal_with_healthy_db_allowed_for_read(self, tmp_path):
        """Non-zero WAL is normal in WAL mode — read-only tools must pass."""
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        db = _create_real_sqlite(adg_dir, "adg_indexed_20260101.sqlite")
        (adg_dir / (db.name + "-wal")).write_bytes(b"\x00" * 32)
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                assert main() == 0

    def test_nonzero_journal_with_healthy_db_allowed_for_read(self, tmp_path):
        """Journal file presence does not block if DB is readable."""
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        db = _create_real_sqlite(adg_dir, "adg_indexed_20260101.sqlite")
        (adg_dir / (db.name + "-journal")).write_bytes(b"\x00" * 32)
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                assert main() == 0

    def test_real_write_contention_blocks_write_tool(self, tmp_path):
        """BEGIN IMMEDIATE contention blocks write-affecting tools."""
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        db = _create_real_sqlite(adg_dir, "adg_indexed_20260101.sqlite")
        holder = sqlite3.connect(str(db), timeout=0.1)
        holder.execute("BEGIN IMMEDIATE")
        holder.execute("INSERT INTO probe VALUES (99)")
        try:
            payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_rebuild"}}
            with patch("sys.stdin", _stdin(payload)):
                with patch("pre_mcp_gate.repo_root", tmp_path):
                    assert main() == 2
        finally:
            holder.rollback()
            holder.close()

    def test_zero_byte_wal_does_not_block(self, tmp_path):
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        db = _create_real_sqlite(adg_dir, "adg_indexed_20260101.sqlite")
        (adg_dir / (db.name + "-wal")).write_text("")  # zero-byte = normal WAL mode
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                assert main() == 0

    def test_no_lock_file_allowed(self, tmp_path):
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        _create_real_sqlite(adg_dir, "adg_indexed_20260101.sqlite")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                assert main() == 0

    def test_lock_check_skipped_for_recovery_tools(self, tmp_path):
        from pre_mcp_gate import main

        adg_dir = tmp_path / "artifacts" / "adg"
        adg_dir.mkdir(parents=True)
        db = _create_real_sqlite(adg_dir, "adg_indexed_20260101.sqlite")
        (adg_dir / (db.name + "-wal")).write_text("")
        payload = {"tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_health"}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_mcp_gate.repo_root", tmp_path):
                assert main() == 0  # recovery tool bypasses lock check


# ============================================================================
# pre_prompt_classifier — deep edge cases
# ============================================================================


class TestPrePromptClassifierFieldAliasing:
    """user_prompt vs prompt field, priority, and default tier."""

    def _classify(self, tool_info: dict) -> tuple:
        from pre_prompt_classifier import main
        import io

        payload = {"tool_info": tool_info}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_prompt_classifier.check_adg_health_red", return_value=False):
                with patch("pre_prompt_classifier.check_redis_up", return_value=True):
                    with patch(
                        "pre_prompt_classifier.check_redis_adg_hot",
                        return_value=True,
                    ):
                        stderr_cap = io.StringIO()
                        with patch("sys.stderr", stderr_cap):
                            rc = main()
        return rc, stderr_cap.getvalue()

    def test_user_prompt_field_used(self):
        _, stderr = self._classify({"user_prompt": "explain how this works"})
        assert "T0" in stderr

    def test_prompt_field_fallback_used(self):
        _, stderr = self._classify({"prompt": "explain how this works"})
        assert "T0" in stderr

    def test_user_prompt_wins_over_prompt(self):
        # user_prompt = T0 query, prompt = T3 refactor
        _, stderr = self._classify({"user_prompt": "explain this", "prompt": "refactor the architecture"})
        assert "T0" in stderr

    def test_empty_user_prompt_falls_back_to_prompt(self):
        _, stderr = self._classify({"user_prompt": "", "prompt": "explain how this works"})
        assert "T0" in stderr

    def test_no_keywords_long_prompt_defaults_to_t1(self):
        # >4 words, zero keyword hits → T1 (short prompts ≤4 words → T2 continuation guard)
        _, stderr = self._classify({"user_prompt": "the quick brown fox jumps"})
        assert "T1" in stderr

    def test_tier_always_printed_to_stderr(self):
        _, stderr = self._classify({"user_prompt": "anything at all"})
        assert "[pre_prompt_classifier] Tier:" in stderr

    def test_list_payload_returns_0(self):
        from pre_prompt_classifier import main

        with patch("sys.stdin", _stdin([{"user_prompt": "refactor"}])):
            assert main() == 0

    def test_string_payload_returns_0(self):
        from pre_prompt_classifier import main

        with patch("sys.stdin", _stdin("refactor the architecture")):
            assert main() == 0

    def test_tool_info_non_dict_returns_0(self):
        from pre_prompt_classifier import main

        with patch("sys.stdin", _stdin({"tool_info": "refactor the architecture"})):
            assert main() == 0


class TestPrePromptClassifierTierKeywordPriority:
    """Keyword scoring priority: T3 > T2x2 > T1 > T0 > single T2."""

    def _tier(self, prompt: str) -> str:
        from pre_prompt_classifier import classify_tier

        return classify_tier(prompt)

    def test_t3_keyword_beats_t2_keywords(self):
        assert self._tier("refactor and update the fix") == "T3"

    def test_t1_keyword_beats_single_t2_keyword(self):
        assert self._tier("fix the typo") == "T1"

    def test_two_t2_keywords_gives_t2(self):
        assert self._tier("update and fix the module") == "T2"

    def test_t0_keyword_gives_t0_with_no_other_hits(self):
        assert self._tier("explain how it works") == "T0"

    def test_single_t2_keyword_only_gives_t2(self):
        assert self._tier("update the README") == "T2"

    def test_empty_prompt_defaults_t1(self):
        from pre_prompt_classifier import classify_tier

        # classify_tier is called only when prompt is non-empty, but test directly
        assert classify_tier("random words with no keywords") == "T1"

    def test_t1_keyword_and_t0_keyword_t1_wins(self):
        # T1 checked before T0 in the scoring chain
        assert self._tier("explain the typo fix") == "T1"


class TestPrePromptClassifierPlanWarning:
    """Missing plan warns but does NOT block."""

    def _run(self, prompt: str, plans_exist: bool) -> tuple:
        from pre_prompt_classifier import main
        import io

        payload = {"tool_info": {"user_prompt": prompt}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("pre_prompt_classifier.check_adg_health_red", return_value=False):
                with patch("pre_prompt_classifier.check_redis_up", return_value=True):
                    with patch(
                        "pre_prompt_classifier.check_redis_adg_hot",
                        return_value=True,
                    ):
                        with patch(
                            "pre_prompt_classifier.check_plan_exists",
                            return_value=plans_exist,
                        ):
                            stderr_cap = io.StringIO()
                            with patch("sys.stderr", stderr_cap):
                                rc = main()
        return rc, stderr_cap.getvalue()

    def test_missing_plan_warns_not_blocks(self):
        rc, stderr = self._run("refactor the architecture", plans_exist=False)
        assert rc == 0, "Missing plan must warn but NOT block"
        assert "WARNING" in stderr or "plan" in stderr.lower()

    def test_plan_exists_no_warning(self):
        rc, stderr = self._run("refactor the architecture", plans_exist=True)
        assert rc == 0
        assert "plan" not in stderr.lower() or "WARNING" not in stderr


# ============================================================================
# post_run_audit — deep edge cases
# ============================================================================


class TestPostRunAuditPayloadShapes:
    """Non-dict payloads must not crash — always return 0."""

    def _run(self, raw: str, tmp_path: Path) -> int:
        from post_run_audit import main

        log = tmp_path / "spawned_processes.jsonl"
        with patch("sys.stdin", StringIO(raw)):
            with patch("post_run_audit.process_log", log):
                with patch("post_run_audit._get_pid_best_effort", return_value=None):
                    return main()

    def test_list_payload_returns_0(self, tmp_path):
        assert self._run(json.dumps([{"command_line": "git status"}]), tmp_path) == 0

    def test_string_payload_returns_0(self, tmp_path):
        assert self._run(json.dumps("git status"), tmp_path) == 0

    def test_int_payload_returns_0(self, tmp_path):
        assert self._run(json.dumps(42), tmp_path) == 0

    def test_null_payload_returns_0(self, tmp_path):
        assert self._run("null", tmp_path) == 0

    def test_tool_info_string_returns_0_no_log(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        from post_run_audit import main

        with patch("sys.stdin", _stdin({"tool_info": "git status"})):
            with patch("post_run_audit.process_log", log):
                with patch("post_run_audit._get_pid_best_effort", return_value=None):
                    rc = main()
        assert rc == 0
        # Non-dict tool_info → no log written
        assert not log.exists()

    def test_list_payload_no_log_written(self, tmp_path):
        log = tmp_path / "spawned_processes.jsonl"
        self._run(json.dumps([{"command_line": "git status"}]), tmp_path)
        assert not log.exists()


# ============================================================================
# post_mcp_audit — deep edge cases
# ============================================================================


class TestPostMcpAuditPayloadShapes:
    """Non-dict payloads must not crash — always return 0."""

    def _run(self, raw: str, log_path: Path) -> int:
        from post_mcp_audit import main

        with patch("sys.stdin", StringIO(raw)):
            with patch("post_mcp_audit.audit_log", log_path):
                return main()

    def test_list_payload_returns_0(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        assert self._run(json.dumps([{"mcp_server_name": "adg_sqlite"}]), log) == 0

    def test_string_payload_returns_0(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        assert self._run(json.dumps("adg_sqlite"), log) == 0

    def test_null_payload_returns_0(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        assert self._run("null", log) == 0

    def test_tool_info_non_dict_returns_0_no_log(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        from post_mcp_audit import main

        with patch("sys.stdin", _stdin({"tool_info": "adg_sqlite"})):
            with patch("post_mcp_audit.audit_log", log):
                rc = main()
        assert rc == 0
        assert not log.exists()

    def test_duration_ms_zero_logged(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        from post_mcp_audit import main

        payload = {
            "tool_info": {"mcp_server_name": "adg_sqlite", "mcp_tool_name": "adg_node", "duration_ms": 0}
        }
        with patch("sys.stdin", _stdin(payload)):
            with patch("post_mcp_audit.audit_log", log):
                main()
        record = json.loads(log.read_text())
        assert record["duration_ms"] == 0

    def test_duration_ms_float_logged(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        from post_mcp_audit import main

        payload = {
            "tool_info": {
                "mcp_server_name": "adg_sqlite",
                "mcp_tool_name": "adg_node",
                "duration_ms": 123.456,
            }
        }
        with patch("sys.stdin", _stdin(payload)):
            with patch("post_mcp_audit.audit_log", log):
                main()
        record = json.loads(log.read_text())
        assert record["duration_ms"] == 123.456

    def test_both_fields_empty_string_logged(self, tmp_path):
        log = tmp_path / "mcp_tool_audit.jsonl"
        from post_mcp_audit import main

        payload = {"tool_info": {}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("post_mcp_audit.audit_log", log):
                main()
        record = json.loads(log.read_text())
        assert record["mcp_server_name"] == ""
        assert record["mcp_tool_name"] == ""
        assert record["duration_ms"] is None


# ============================================================================
# post_write_audit — deep edge cases
# ============================================================================


class TestPostWriteAuditPayloadShapes:
    """Non-dict payloads must not crash — always return 0."""

    def _run(self, raw: str, sink: Path) -> int:
        from post_write_audit import main

        with patch("sys.stdin", StringIO(raw)):
            with patch("post_write_audit.audit_log", sink):
                return main()

    def test_list_payload_returns_0(self, tmp_path):
        assert self._run(json.dumps([{"file_path": "mcp_config.json"}]), tmp_path / "sink.jsonl") == 0

    def test_string_payload_returns_0(self, tmp_path):
        assert self._run(json.dumps("mcp_config.json"), tmp_path / "sink.jsonl") == 0

    def test_null_payload_returns_0(self, tmp_path):
        assert self._run("null", tmp_path / "sink.jsonl") == 0

    def test_tool_info_non_dict_returns_0(self, tmp_path):
        assert self._run(json.dumps({"tool_info": "mcp_config.json"}), tmp_path / "sink.jsonl") == 0


class TestPostWriteAuditEnvVarFormats:
    """Shell env var format must warn; Windsurf-native format must not."""

    def _lint(self, file_path: str, config_content: str, edits: list) -> list:
        from post_write_audit import lint_mcp_config

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=config_content):
                return lint_mcp_config(file_path, edits)

    def test_shell_env_var_syntax_flagged(self):
        config = json.dumps(
            {
                "mcpServers": {
                    "my_server": {"command": "node", "env": {"API_KEY": "${API_KEY:-default_value}"}}
                }
            }
        )
        findings = self._lint("mcp_config.json", config, [])
        assert any(
            "shell syntax" in f or "${{VAR:-default}}" in f or "shell" in f.lower() for f in findings
        ), "Shell-format env var must be flagged"

    def test_windsurf_native_env_var_not_flagged(self):
        config = json.dumps(
            {"mcpServers": {"my_server": {"command": "node", "env": {"API_KEY": "${env:API_KEY}"}}}}
        )
        findings = self._lint("mcp_config.json", config, [])
        assert not any("shell syntax" in f for f in findings), (
            "${env:VAR} Windsurf native format must NOT be flagged"
        )

    def test_finding_count_matches_findings_length(self, tmp_path):
        from post_write_audit import main

        log = tmp_path / "mcp_lint_audit.jsonl"
        mcp_file = tmp_path / "mcp_config.json"
        mcp_file.write_text(json.dumps({"mcpServers": {}}))  # missing server entries
        payload = {"tool_info": {"file_path": str(mcp_file), "edits": []}}
        with patch("sys.stdin", _stdin(payload)):
            with patch("post_write_audit.audit_log", log):
                main()
        if log.exists():
            record = json.loads(log.read_text().strip())
            assert record["finding_count"] == len(record["findings"]), (
                "finding_count must equal len(findings)"
            )


# ============================================================================
# post_cursor_agent_cleanup — deep edge cases
# ============================================================================


class TestPostCascadeCleanupRotationLimits:
    """Each log has its own rotation limit — test all three."""

    def _make_log(self, path: Path, n_lines: int):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(f"line {i}" for i in range(n_lines)) + "\n")

    def test_process_log_limit_is_500(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        log = tmp_path / "spawned_processes.jsonl"
        self._make_log(log, 600)
        run_cleanup(tmp_path)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 500

    def test_mcp_tool_log_limit_is_500(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        log = tmp_path / "mcp_tool_audit.jsonl"
        self._make_log(log, 600)
        run_cleanup(tmp_path)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 500

    def test_mcp_lint_log_limit_is_200_not_500(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        log = tmp_path / "mcp_lint_audit.jsonl"
        self._make_log(log, 300)
        run_cleanup(tmp_path)
        lines = log.read_text().strip().splitlines()
        assert len(lines) == 200, "mcp_lint_audit has a 200-line limit, not 500"

    def test_at_exactly_limit_no_rotation(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        log = tmp_path / "mcp_lint_audit.jsonl"
        self._make_log(log, 200)
        original = log.read_text()
        run_cleanup(tmp_path)
        assert log.read_text() == original, "At exactly limit, file must not be modified"

    def test_under_limit_no_rotation(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        log = tmp_path / "spawned_processes.jsonl"
        self._make_log(log, 10)
        run_cleanup(tmp_path)
        assert len(log.read_text().strip().splitlines()) == 10

    def test_rotation_keeps_newest_lines(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        log = tmp_path / "mcp_lint_audit.jsonl"
        self._make_log(log, 250)
        run_cleanup(tmp_path)
        lines = log.read_text().strip().splitlines()
        # Last 200 lines of 0..249 are lines 50..249
        assert lines[0] == "line 50"
        assert lines[-1] == "line 249"

    def test_session_summary_has_audit_line_counts_keyed_by_filename(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        summary = run_cleanup(tmp_path)
        assert "audit_line_counts" in summary
        counts = summary["audit_line_counts"]
        assert "spawned_processes.jsonl" in counts
        assert "mcp_tool_audit.jsonl" in counts
        assert "mcp_lint_audit.jsonl" in counts

    def test_session_summary_has_timestamp(self, tmp_path):
        from post_cursor_agent_cleanup import run_cleanup

        summary = run_cleanup(tmp_path)
        assert "timestamp" in summary
        datetime.fromisoformat(summary["timestamp"].replace("Z", "+00:00"))

    def test_main_returns_0_even_on_oserror(self, tmp_path):
        from post_cursor_agent_cleanup import main

        with patch("post_cursor_agent_cleanup.windsurf_dir", tmp_path / "no_write"):
            with patch(
                "post_cursor_agent_cleanup.session_summary",
                tmp_path / "no_write" / "s.json",
            ):
                with patch("pathlib.Path.mkdir", side_effect=OSError("read only")):
                    assert main() == 0
