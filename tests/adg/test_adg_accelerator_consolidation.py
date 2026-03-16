# adg-grep-ban: skip-file
"""Consolidation tests — all ADG accelerators are PRIMARY, wired, and fail-closed.

Sections:
  1. GrepBanSkipFileDirective — new # adg-grep-ban: skip-file feature
  2. MCPServerSourceAnalysis — 17 tools, response format, no live Redis needed
  3. GuardianExemptionGateLogic — ratchet pure functions
  4. RunContractGatesRegistry — grep-ban + guardian gates MUST be in run_contract_gates.py
  5. ProductionSkipFileProtection — production dirs must NEVER contain skip-file
  6. AcceleratorPrimaryChainIntegrity — 5 files exist, §2.6 complete, hooks wired
  7. FailClosedChainEnforcement — bypass blocks; no fallback to grep/mypy/pytest
  8. GitHubWorkflowCompleteness — CI enforces grep-ban on ALL Python files
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_accelerator_consolidation")
_emit_applies_guardrail("p0", "test_adg_accelerator_consolidation", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_accelerator_consolidation", "policy_binding")
_emit_snapshots_state("p0", "test_adg_accelerator_consolidation", "state_snapshot")
emit_replay_key("p0", "test_adg_accelerator_consolidation")
emit_determinism_digest("p0", "test_adg_accelerator_consolidation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================================
# 1. # adg-grep-ban: skip-file directive
# ============================================================================

class TestGrepBanSkipFileDirective:
    """The skip-file directive suppresses the entire file scan (first 5 lines only)."""

    def _make(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", encoding="utf-8", delete=False
        )
        f.write(content)
        f.close()
        return Path(f.name)

    def test_skip_file_in_line_1_suppresses_all_violations(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            "# adg-grep-ban: skip-file\n"
            'subprocess.run(["grep", "-r", "foo"])\n'
            'subprocess.run(["rg", "bar"])\n'
            'os.popen("grep baz")\n'
        )
        try:
            assert scan_file(tmp) == [], "skip-file in line 1 must suppress all violations"
        finally:
            tmp.unlink()

    def test_skip_file_in_line_5_suppresses_violations(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            '"""Module docstring."""\n'           # line 1
            "\n"                                  # line 2
            "import subprocess\n"                  # line 3
            "\n"                                  # line 4
            "# adg-grep-ban: skip-file\n"         # line 5
            'subprocess.run(["grep", "foo"])\n'   # line 6 — skipped
        )
        try:
            assert scan_file(tmp) == [], "skip-file in line 5 must suppress violations"
        finally:
            tmp.unlink()

    def test_skip_file_in_line_6_does_not_suppress(self) -> None:
        """skip-file is only honoured in the first 5 lines."""
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            "# line 1\n"
            "# line 2\n"
            "# line 3\n"
            "# line 4\n"
            "# line 5\n"
            "# adg-grep-ban: skip-file\n"         # line 6 — TOO LATE
            'subprocess.run(["grep", "foo"])\n'
        )
        try:
            vs = scan_file(tmp)
            assert len(vs) == 1, (
                "skip-file in line 6 must NOT suppress violations; first-5-lines rule"
            )
        finally:
            tmp.unlink()

    def test_skip_file_with_extra_spaces_still_works(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            "#   adg-grep-ban:   skip-file  \n"
            'subprocess.run(["grep", "foo"])\n'
        )
        try:
            assert scan_file(tmp) == [], "skip-file with extra spaces must still work"
        finally:
            tmp.unlink()

    def test_skip_file_uppercase_not_recognised(self) -> None:
        """# ADG-GREP-BAN: SKIP-FILE (uppercase) must NOT be honoured."""
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            "# ADG-GREP-BAN: SKIP-FILE\n"
            'subprocess.run(["grep", "foo"])\n'
        )
        try:
            vs = scan_file(tmp)
            assert len(vs) == 1, "Uppercase skip-file must NOT suppress violations"
        finally:
            tmp.unlink()

    def test_skip_file_only_affects_its_own_file(self) -> None:
        """skip-file in file A must NOT suppress violations in file B."""
        from ops_scripts.ci.adg_grep_ban_gate import scan_files

        file_a = self._make(
            "# adg-grep-ban: skip-file\n"
            'subprocess.run(["grep", "foo"])\n'
        )
        file_b = self._make(
            'subprocess.run(["rg", "bar"])\n'
        )
        try:
            results = scan_files([file_a, file_b])
            assert file_a not in results, "file_a with skip-file must produce no violations"
            assert file_b in results, "file_b without skip-file must have violations"
        finally:
            file_a.unlink()
            file_b.unlink()

    def test_file_skip_re_pattern_matches_canonical(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import _FILE_SKIP_RE

        assert _FILE_SKIP_RE.search("# adg-grep-ban: skip-file")
        assert _FILE_SKIP_RE.search("#adg-grep-ban:skip-file")
        assert _FILE_SKIP_RE.search("#  adg-grep-ban:  skip-file  ")

    def test_file_skip_re_pattern_rejects_wrong_keyword(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import _FILE_SKIP_RE

        assert not _FILE_SKIP_RE.search("# adg-grep-ban: skip-all")
        assert not _FILE_SKIP_RE.search("# adg-grep-ban: ignore-file")
        assert not _FILE_SKIP_RE.search("# skip-file")
        assert not _FILE_SKIP_RE.search("# ADG-GREP-BAN: SKIP-FILE")

    def test_empty_file_with_skip_directive_returns_empty(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make("# adg-grep-ban: skip-file\n")
        try:
            assert scan_file(tmp) == []
        finally:
            tmp.unlink()

    def test_skip_directive_at_line_4_with_violations_at_line_3(self) -> None:
        """skip-file at line 4 still suppresses a violation at line 3."""
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            "import subprocess\n"                 # line 1
            "\n"                                  # line 2
            'subprocess.run(["grep", "foo"])\n'  # line 3 — violation
            "# adg-grep-ban: skip-file\n"         # line 4 — skip (checked before scan)
        )
        try:
            assert scan_file(tmp) == [], "skip-file at line 4 applies to whole file"
        finally:
            tmp.unlink()


# ============================================================================
# 2. MCP Server source analysis — 17 tools, response contract
# ============================================================================

MCP_SERVER_PATH = ROOT / "tools" / "adg" / "adg_mcp_server.py"

_EXPECTED_MCP_TOOLS = [
    "adg_status",
    "adg_meta",
    "adg_snapshot",
    "adg_node",
    "adg_nodes_by_layer",
    "adg_nodes_by_file",
    "adg_edge_fanout",
    "adg_edge_fanin",
    "adg_violations",
    "adg_assert_fresh",
    "redis_get",
    "redis_hgetall",
    "redis_smembers",
    "redis_lrange",
    "redis_type",
    "redis_ttl",
    "redis_scan",
]


class TestMCPServerSourceAnalysis:
    """Verify the ADG MCP server contract without requiring live Redis."""

    @classmethod
    def _source(cls) -> str:
        return MCP_SERVER_PATH.read_text(encoding="utf-8")

    def test_mcp_server_file_exists(self) -> None:
        assert MCP_SERVER_PATH.exists(), "tools/adg/adg_mcp_server.py must exist"

    def test_exactly_17_mcp_tools_registered(self) -> None:
        src = self._source()
        count = src.count("@mcp.tool()")
        assert count == 17, (
            f"Expected exactly 17 @mcp.tool() decorators, found {count}"
        )

    @pytest.mark.parametrize("tool_name", _EXPECTED_MCP_TOOLS)
    def test_expected_tool_is_defined(self, tool_name: str) -> None:
        src = self._source()
        assert f"def {tool_name}(" in src, (
            f"@mcp.tool() function '{tool_name}' must be defined in adg_mcp_server.py"
        )

    def test_every_mcp_tool_has_docstring(self) -> None:
        """Every @mcp.tool() function must be followed by a docstring (LLM tool description)."""
        import ast

        tree = ast.parse(self._source())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef,)):
                for dec in node.decorator_list:
                    if (
                        isinstance(dec, ast.Call)
                        and isinstance(dec.func, ast.Attribute)
                        and dec.func.attr == "tool"
                    ):
                        body = node.body
                        has_docstring = (
                            body
                            and isinstance(body[0], ast.Expr)
                            and isinstance(body[0].value, ast.Constant)
                        )
                        assert has_docstring, (
                            f"@mcp.tool() function '{node.name}' must have a docstring "
                            f"(required for LLM tool descriptions)"
                        )

    def test_ok_response_always_includes_cache_meta(self) -> None:
        """_ok() must return a dict containing 'cache_meta' key."""
        src = self._source()
        assert '"cache_meta": _cache_meta()' in src or "'cache_meta': _cache_meta()" in src, (
            "_ok() must inject 'cache_meta': _cache_meta() into every response"
        )

    def test_err_response_always_includes_cache_meta(self) -> None:
        """_err() must return a dict containing 'cache_meta' key."""
        src = self._source()
        assert "_err" in src
        err_def_idx = src.index("def _err(")
        err_body = src[err_def_idx: err_def_idx + 300]
        assert "cache_meta" in err_body, "_err() must include cache_meta in its response"

    def test_wrongtype_hint_maps_all_four_types(self) -> None:
        """_wrongtype_hint() must provide a remediation tool for all HASH/SET/LIST/STRING types."""
        src = self._source()
        assert '"hash"' in src and "redis_hgetall" in src
        assert '"set"' in src and "redis_smembers" in src
        assert '"list"' in src and "redis_lrange" in src
        assert '"string"' in src and "redis_get" in src

    def test_redis_scan_not_keys_star(self) -> None:
        """redis_scan implementation must use cursor-based SCAN, not blocking KEYS *."""
        import ast
        src = self._source()
        # Strip comments and strings to avoid false positives on docstrings that mention KEYS *
        tree = ast.parse(src)
        redis_scan_fn = next(
            (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "redis_scan"),
            None,
        )
        assert redis_scan_fn is not None, "redis_scan function must be defined"
        # The function body source lines must call .scan() not KEYS
        fn_src_lines = src.splitlines()[redis_scan_fn.lineno - 1: redis_scan_fn.end_lineno]
        fn_src = "\n".join(fn_src_lines)
        assert ".scan(" in fn_src, "redis_scan must use cursor-based .scan() call"
        # Verify KEYS is not called as a Redis command (would be .keys() in code)
        assert ".keys(" not in fn_src, "redis_scan must NOT call .keys() (O(N) blocking)"

    def test_cache_meta_never_raises(self) -> None:
        """_cache_meta() must catch ALL exceptions and return {'available': False}."""
        src = self._source()
        cache_meta_idx = src.index("def _cache_meta(")
        # Find the function body up to next def
        next_def = src.index("\ndef ", cache_meta_idx + 10)
        body = src[cache_meta_idx:next_def]
        assert "except Exception" in body or "except" in body, (
            "_cache_meta() must catch all exceptions to prevent response wrapper failures"
        )
        assert "available" in body and "False" in body, (
            "_cache_meta() must return {'available': False} on any failure"
        )

    def test_adg_assert_fresh_reads_meta_and_disk(self) -> None:
        """adg_assert_fresh must check BOTH Redis ingest timestamp AND SQLite mtime on disk."""
        src = self._source()
        assert_fresh_idx = src.index("def adg_assert_fresh(")
        next_def = src.index("\n@mcp.tool()", assert_fresh_idx)
        body = src[assert_fresh_idx:next_def]
        assert "hgetall" in body.lower(), "adg_assert_fresh must read adg:meta via HGETALL"
        assert "st_mtime" in body or "sqlite_mtime" in body, (
            "adg_assert_fresh must stat the SQLite file on disk"
        )

    def test_server_instructs_adg_status_called_first(self) -> None:
        """Server instructions must tell clients to call adg_status first."""
        src = self._source()
        assert "adg_status" in src
        server_def_idx = src.index('FastMCP(')
        server_block = src[server_def_idx: server_def_idx + 300]
        assert "adg_status" in server_block or "Use adg_status first" in src, (
            "Server instructions must direct clients to call adg_status first"
        )


# ============================================================================
# 3. Guardian exemption gate pure logic
# ============================================================================

class TestGuardianExemptionGateLogic:
    """Guardian exemption gate ratchet logic — deterministic, no filesystem."""

    @classmethod
    def _import(cls):
        from ops_scripts.ci.guardian_exemption_gate import (
            _ANY_GUARDIAN_RE,
            _CANONICAL_RE,
            _GENERIC_TOKENS,
            _NO_JUSTIFICATION_RE,
            _is_generic_justification,
            _ratchet_total,
        )
        return (
            _CANONICAL_RE,
            _GENERIC_TOKENS,
            _NO_JUSTIFICATION_RE,
            _ANY_GUARDIAN_RE,
            _is_generic_justification,
            _ratchet_total,
        )

    def test_empty_justification_is_generic(self) -> None:
        _, _, _, _, _is_generic, _ = self._import()
        assert _is_generic("") is True

    def test_single_generic_word_is_generic(self) -> None:
        _, _, _, _, _is_generic, _ = self._import()
        for word in ["needed", "required", "legacy", "temporary", "hack", "workaround"]:
            assert _is_generic(word) is True, f"'{word}' must be flagged as generic"

    def test_multi_generic_words_all_generic_is_generic(self) -> None:
        _, _, _, _, _is_generic, _ = self._import()
        assert _is_generic("needed temporary") is True   # both tokens in _GENERIC_TOKENS
        assert _is_generic("legacy workaround") is True
        assert _is_generic("needed required") is True

    def test_specific_justification_not_generic(self) -> None:
        _, _, _, _, _is_generic, _ = self._import()
        assert _is_generic("wrapper around legacy shell script") is False
        assert _is_generic("CI bootstrap requires sys.path before package imports") is False
        assert _is_generic("used in performance-critical hot path measured at 400ns") is False

    def test_mixed_generic_and_specific_not_generic(self) -> None:
        _, _, _, _, _is_generic, _ = self._import()
        assert _is_generic("needed for the performance-critical hot path") is False

    def test_canonical_re_matches_well_formed_comment(self) -> None:
        _CANONICAL_RE, _, _, _, _, _ = self._import()
        assert _CANONICAL_RE.match("# guardian: allow-grep -- wrapper around legacy shell")
        assert _CANONICAL_RE.match("    # guardian: allow-global-mutation -- CI bootstrap")

    def test_canonical_re_rejects_missing_justification(self) -> None:
        _CANONICAL_RE, _, _, _, _, _ = self._import()
        assert not _CANONICAL_RE.match("# guardian: allow-grep")
        assert not _CANONICAL_RE.match("# guardian: allow-grep --")
        assert not _CANONICAL_RE.match("# guardian: allow-grep -- ")

    def test_no_justification_re_matches_bare_exemption(self) -> None:
        _, _, _NO_JUST_RE, _, _, _ = self._import()
        assert _NO_JUST_RE.match("# guardian: allow-grep")
        assert _NO_JUST_RE.match("    # guardian: allow-global-mutation")

    def test_any_guardian_re_matches_malformed_variants(self) -> None:
        _, _, _, _ANY_RE, _, _ = self._import()
        assert _ANY_RE.search("# Guardian: allow-grep -- test")
        assert _ANY_RE.search("# guardian: allow_grep -- test")
        assert _ANY_RE.search("    # guardian: allow-grep")

    def test_ratchet_total_sums_all_counts(self) -> None:
        _, _, _, _, _, _ratchet_total = self._import()
        budget = {
            "agentic_core/L5_safety/foo.py": {"grep": 2, "global-mutation": 1},
            "apps_rg/engines/bar.py": {"grep": 3},
        }
        assert _ratchet_total(budget) == 6

    def test_ratchet_total_empty_budget(self) -> None:
        _, _, _, _, _, _ratchet_total = self._import()
        assert _ratchet_total({}) == 0

    def test_generic_tokens_contains_key_terms(self) -> None:
        _, _GENERIC_TOKENS, _, _, _, _ = self._import()
        for must_be_generic in ["needed", "required", "legacy", "hack", "workaround", "todo"]:
            assert must_be_generic in _GENERIC_TOKENS, (
                f"'{must_be_generic}' must be in _GENERIC_TOKENS"
            )


# ============================================================================
# 4. run_contract_gates.py must register grep-ban + guardian gates
# ============================================================================

class TestRunContractGatesRegistry:
    """run_contract_gates.py is the CI single-entry-point — all enforcement gates must be registered."""

    @classmethod
    def _gates_source(cls) -> str:
        return (ROOT / "ops_scripts" / "ci" / "run_contract_gates.py").read_text(encoding="utf-8")

    def test_grep_ban_gate_is_registered_in_contract_runner(self) -> None:
        src = self._gates_source()
        assert "adg_grep_ban_gate" in src, (
            "FAIL: ops_scripts/ci/run_contract_gates.py does NOT include adg_grep_ban_gate.py.\n"
            "Fix: add the grep-ban gate to the 'gates' list in run_contract_gates.py.\n"
            "This means CI is NOT enforcing the grep-ban rule on every push."
        )

    def test_guardian_exemption_gate_is_registered_in_contract_runner(self) -> None:
        src = self._gates_source()
        assert "guardian_exemption_gate" in src, (
            "FAIL: ops_scripts/ci/run_contract_gates.py does NOT include guardian_exemption_gate.py.\n"
            "Fix: add the guardian exemption gate to the 'gates' list.\n"
            "This means CI is NOT enforcing exemption quality on every push."
        )

    def test_powershell_ban_gate_is_registered(self) -> None:
        src = self._gates_source()
        assert "check_powershell_ban" in src, (
            "PowerShell ban gate must be in run_contract_gates.py"
        )

    def test_contract_runner_itself_uses_no_shell_true(self) -> None:
        """The gates runner must never use shell=True in subprocess calls."""
        src = self._gates_source()
        assert "shell=True" not in src, (
            "run_contract_gates.py must use shell=False for all subprocess calls"
        )

    def test_contract_runner_rejects_powershell_at_argv_level(self) -> None:
        """The runner must detect and reject PowerShell in argv0."""
        from ops_scripts.ci.run_contract_gates import run_cmd

        with pytest.raises(ValueError, match="PowerShell"):
            run_cmd(["powershell.exe", "-Command", "echo hi"])

    def test_contract_runner_rejects_pwsh(self) -> None:
        from ops_scripts.ci.run_contract_gates import run_cmd

        with pytest.raises(ValueError, match="PowerShell"):
            run_cmd(["pwsh", "-Command", "echo hi"])


# ============================================================================
# 5. Production code must NEVER have # adg-grep-ban: skip-file
# ============================================================================

class TestProductionSkipFileProtection:
    """The skip-file escape hatch must not appear in production code.

    This is a permanent invariant test. If any developer adds skip-file to a
    production module, this test will fail immediately.
    """

    _PRODUCTION_DIRS = [
        "agentic_core",
        "apps_lic",
        "apps_rg",
        "apps_shared",
        "apps_exec",
        "apps_eval",
        "apps_rfp",
        "apps_research",
        "system_learning",
    ]

    @classmethod
    def _scan_dir_for_skip_file(cls, dir_name: str) -> list[Path]:
        target = ROOT / dir_name
        if not target.exists():
            return []
        offenders = []
        for py_file in target.rglob("*.py"):
            try:
                lines = py_file.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines[:10]:  # only check header region
                    if "adg-grep-ban" in line.lower() and "skip-file" in line.lower():
                        offenders.append(py_file)
                        break
            except OSError:
                pass
        return offenders

    def test_agentic_core_has_no_skip_file_directive(self) -> None:
        offenders = self._scan_dir_for_skip_file("agentic_core")
        assert not offenders, (
            "Production code in agentic_core/ must NOT have '# adg-grep-ban: skip-file'.\n"
            "Offending files:\n" + "\n".join(f"  {p}" for p in offenders)
        )

    def test_apps_dirs_have_no_skip_file_directive(self) -> None:
        all_offenders = []
        for d in ["apps_lic", "apps_rg", "apps_shared", "apps_exec", "apps_eval", "apps_rfp", "apps_research"]:
            all_offenders.extend(self._scan_dir_for_skip_file(d))
        assert not all_offenders, (
            "Production apps_* dirs must NOT have '# adg-grep-ban: skip-file'.\n"
            "Offending files:\n" + "\n".join(f"  {p}" for p in all_offenders)
        )

    def test_system_learning_has_no_skip_file_directive(self) -> None:
        offenders = self._scan_dir_for_skip_file("system_learning")
        assert not offenders, (
            "Production code in system_learning/ must NOT have '# adg-grep-ban: skip-file'.\n"
            "Offending files:\n" + "\n".join(f"  {p}" for p in offenders)
        )

    def test_skip_file_is_allowed_in_tests(self) -> None:
        """Skip-file IS permitted in tests/ — test fixtures contain banned patterns as strings."""
        test_file = ROOT / "tests" / "adg" / "test_adg_grep_ban_gate.py"
        if not test_file.exists():
            pytest.skip("test_adg_grep_ban_gate.py not found")
        content = test_file.read_text(encoding="utf-8")
        assert "adg-grep-ban: skip-file" in content, (
            "test_adg_grep_ban_gate.py should have skip-file directive "
            "(it contains grep patterns as string fixtures)"
        )

    def test_skip_file_must_not_appear_in_ops_scripts_ci_gates(self) -> None:
        """CI gate files must NOT use the actual skip-file directive (requires # prefix).

        Docstrings that MENTION '# adg-grep-ban: skip-file' as documentation are
        permitted; only lines that ARE the directive (start with #, match _FILE_SKIP_RE)
        are forbidden.
        """
        from ops_scripts.ci.adg_grep_ban_gate import _FILE_SKIP_RE

        offenders = []
        ci_dir = ROOT / "ops_scripts" / "ci"
        for py_file in sorted(ci_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue  # private helper scripts excluded
            try:
                lines = py_file.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines[:5]:
                    # Must be an actual directive line (# prefix), not a docstring mention
                    if line.lstrip().startswith("#") and _FILE_SKIP_RE.search(line):
                        offenders.append(py_file)
                        break
            except OSError:
                pass
        assert not offenders, (
            "CI gate files in ops_scripts/ci/ must NOT have the skip-file directive:\n"
            + "\n".join(f"  {p}" for p in offenders)
        )


# ============================================================================
# 6. All 5 accelerator files exist + §2.6 is complete in windsurfrules
# ============================================================================

_ACCELERATOR_PATHS = [
    "tools/adg/adg_antipattern_fixer.py",
    "tools/adg/adg_stale_guard.py",
    "tools/adg/adg_redis_query.py",
    "tools/adg/adg_type_check.py",
    "tools/adg/adg_test_selector.py",
]

_FORBIDDEN_SUBSTITUTES = [
    "grep -r",
    "adg_type_check",  # forbidden: broad mypy
    "adg_test_selector",  # forbidden: broad pytest
    "allow-grep",  # forbidden: manual guardian editing
]


class TestAcceleratorPrimaryChainIntegrity:
    """All 5 accelerators must be present, wired, and listed in §2.6."""

    @classmethod
    def _windsurfrules(cls) -> str:
        return (ROOT / ".windsurf" / "rules" / ".windsurfrules").read_text(encoding="utf-8")

    @classmethod
    def _precommit(cls) -> str:
        return (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    @pytest.mark.parametrize("rel_path", _ACCELERATOR_PATHS)
    def test_accelerator_file_exists(self, rel_path: str) -> None:
        assert (ROOT / rel_path).exists(), (
            f"Accelerator file {rel_path} must exist on disk"
        )

    def test_mcp_server_exists(self) -> None:
        assert (ROOT / "tools" / "adg" / "adg_mcp_server.py").exists(), (
            "Custom ADG Redis MCP server must exist (tools/adg/adg_mcp_server.py)"
        )

    @pytest.mark.parametrize("rel_path", _ACCELERATOR_PATHS)
    def test_accelerator_mentioned_in_windsurfrules_2_6(self, rel_path: str) -> None:
        src = self._windsurfrules()
        tool_name = Path(rel_path).name
        assert tool_name in src, (
            f"Accelerator '{tool_name}' must be listed in §2.6 of .windsurfrules"
        )

    def test_windsurfrules_section_2_6_lists_grep_as_forbidden(self) -> None:
        src = self._windsurfrules()
        section_start = src.find("### 2.6")
        assert section_start != -1
        section = src[section_start: section_start + 3000]
        assert "grep" in section, "§2.6 must list grep as a forbidden substitute"

    def test_windsurfrules_section_2_6_lists_broad_mypy_as_forbidden(self) -> None:
        src = self._windsurfrules()
        section_start = src.find("### 2.6")
        section = src[section_start: section_start + 3000]
        assert "mypy" in section, "§2.6 must list broad mypy as a forbidden substitute"

    def test_windsurfrules_section_2_6_lists_broad_pytest_as_forbidden(self) -> None:
        src = self._windsurfrules()
        section_start = src.find("### 2.6")
        section = src[section_start: section_start + 3000]
        assert "pytest" in section, "§2.6 must list broad pytest as a forbidden substitute"

    def test_windsurfrules_section_2_6_lists_mcp_server(self) -> None:
        src = self._windsurfrules()
        assert "adg_mcp_server" in src or "adg_redis" in src, (
            "§2.6 must reference the custom ADG Redis MCP server"
        )

    def test_precommit_t2c_antipattern_fixer_hook_present(self) -> None:
        cfg = self._precommit()
        assert "adg-antipattern-fixer" in cfg or "guardian-fix" in cfg, (
            "T2c guardian-comment-fixer hook must be in .pre-commit-config.yaml"
        )

    def test_precommit_t3g_stale_guard_hook_present(self) -> None:
        cfg = self._precommit()
        assert "adg-stale-guard" in cfg, (
            "T3g ADG staleness guard hook must be in .pre-commit-config.yaml"
        )

    def test_precommit_t3h_grep_ban_hook_present(self) -> None:
        cfg = self._precommit()
        assert "adg-grep-ban-gate" in cfg, (
            "T3h ADG grep-ban gate hook must be in .pre-commit-config.yaml"
        )

    def test_precommit_t3g_before_t3h_in_config(self) -> None:
        cfg = self._precommit()
        pos_t3g = cfg.find("adg-stale-guard")
        pos_t3h = cfg.find("adg-grep-ban-gate")
        assert pos_t3g != -1 and pos_t3h != -1
        assert pos_t3g < pos_t3h, "T3g staleness guard must appear before T3h grep-ban in config"

    def test_skip_file_directive_documented_in_precommit(self) -> None:
        """The skip-file exemption mechanism must be documented in the hook comment."""
        cfg = self._precommit()
        assert "skip-file" in cfg, (
            "The adg-grep-ban hook comment must document the # adg-grep-ban: skip-file exemption"
        )


# ============================================================================
# 7. Fail-closed chain enforcement
# ============================================================================

class TestFailClosedChainEnforcement:
    """If any accelerator is bypassed, the chain must block — no grep/mypy/pytest fallback."""

    def test_assert_fresh_raises_propagates_through_adg_query_session(self) -> None:
        """ADGQuerySession.__enter__ must re-raise if assert_fresh() raises (fail-closed)."""
        from tools.adg.adg_redis_query import ADGQuerySession
        from tools.adg.adg_stale_guard import ADGStalenessChecker

        mock_checker = MagicMock(spec=ADGStalenessChecker)
        mock_checker.assert_fresh.side_effect = RuntimeError("ADG cache is stale")

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=False, client=MagicMock())
            with pytest.raises(RuntimeError, match="stale"):
                session.__enter__()

    def test_connection_error_propagates_through_adg_query_session(self) -> None:
        import redis

        from tools.adg.adg_redis_query import ADGQuerySession
        from tools.adg.adg_stale_guard import ADGStalenessChecker

        mock_checker = MagicMock(spec=ADGStalenessChecker)
        mock_checker.assert_fresh.side_effect = redis.ConnectionError("Redis down")

        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=False, client=MagicMock())
            with pytest.raises(redis.ConnectionError):
                session.__enter__()

    def test_adg_test_selector_has_no_filesystem_fallback(self) -> None:
        """adg_test_selector.py source must NOT contain any fallback to glob/os.walk/pytest."""
        src = (ROOT / "tools" / "adg" / "adg_test_selector.py").read_text(encoding="utf-8")
        forbidden = ["glob.glob", "os.walk", "Path.rglob", "pytest.main", "subprocess.run.*pytest"]
        for pattern in ["glob.glob(", "os.walk(", ".rglob(", "pytest.main("]:
            assert pattern not in src, (
                f"adg_test_selector.py must NOT contain {pattern!r} fallback"
            )

    def test_adg_type_check_has_no_full_package_mypy_fallback(self) -> None:
        """adg_type_check.py must NOT fall back to running mypy on an entire package."""
        src = (ROOT / "tools" / "adg" / "adg_type_check.py").read_text(encoding="utf-8")
        # Broad mypy invocations would look like mypy on a directory (not a file list)
        assert "mypy agentic_core" not in src, "adg_type_check.py must NOT hardcode broad mypy"
        assert "mypy apps_" not in src, "adg_type_check.py must NOT hardcode broad mypy"

    def test_adg_stale_guard_has_no_grep_fallback(self) -> None:
        """adg_stale_guard.py must not fall back to grep for staleness detection."""
        src = (ROOT / "tools" / "adg" / "adg_stale_guard.py").read_text(encoding="utf-8")
        assert 'subprocess.run(["grep"' not in src
        assert "os.popen(" not in src

    def test_adg_redis_query_has_no_grep_fallback(self) -> None:
        """adg_redis_query.py must not fall back to grep for node search."""
        src = (ROOT / "tools" / "adg" / "adg_redis_query.py").read_text(encoding="utf-8")
        assert 'subprocess.run(["grep"' not in src
        assert 'subprocess.run(["rg"' not in src

    def test_warn_only_session_does_not_block_on_connection_error(self) -> None:
        """In warn_only=True mode, a Redis connection error must NOT block the query."""
        from tools.adg.adg_redis_query import ADGQuerySession
        from tools.adg.adg_stale_guard import ADGStalenessChecker

        mock_checker = MagicMock(spec=ADGStalenessChecker)
        mock_checker.warn_if_stale.return_value = None  # silently handles errors internally

        mock_client = MagicMock()
        with patch(
            "tools.adg.adg_stale_guard.ADGStalenessChecker",
            return_value=mock_checker,
        ):
            session = ADGQuerySession(warn_only=True, client=mock_client)
            client = session.__enter__()
        assert client is mock_client, "warn_only session must return the client after warn_if_stale"


# ============================================================================
# 8. GitHub CI workflow completeness
# ============================================================================

class TestGitHubWorkflowCompleteness:
    """GitHub Actions workflows must enforce grep-ban on ALL Python files in CI."""

    @classmethod
    def _grep_ban_workflow(cls) -> str:
        p = ROOT / ".github" / "workflows" / "adg-grep-ban-ci.yml"
        assert p.exists(), f"Missing: {p}"
        return p.read_text(encoding="utf-8")

    @classmethod
    def _antipattern_workflow(cls) -> str:
        p = ROOT / ".github" / "workflows" / "adg-antipattern-ci.yml"
        assert p.exists(), f"Missing: {p}"
        return p.read_text(encoding="utf-8")

    def test_grep_ban_workflow_exists(self) -> None:
        assert (ROOT / ".github" / "workflows" / "adg-grep-ban-ci.yml").exists()

    def test_grep_ban_workflow_uses_all_python_flag(self) -> None:
        """CI must scan ALL Python files, not just staged — use --all-python."""
        wf = self._grep_ban_workflow()
        assert "--all-python" in wf, (
            "adg-grep-ban-ci.yml must use --all-python to scan the full codebase in CI"
        )

    def test_grep_ban_workflow_triggers_on_push_and_pr(self) -> None:
        wf = self._grep_ban_workflow()
        assert "push" in wf, "grep-ban CI must trigger on push"
        assert "pull_request" in wf, "grep-ban CI must trigger on pull_request"

    def test_grep_ban_workflow_sets_pythonpath(self) -> None:
        wf = self._grep_ban_workflow()
        assert "PYTHONPATH" in wf, (
            "grep-ban CI must set PYTHONPATH so the gate can import project modules"
        )

    def test_antipattern_workflow_exists(self) -> None:
        assert (ROOT / ".github" / "workflows" / "adg-antipattern-ci.yml").exists()

    def test_antipattern_workflow_uses_check_only_flag(self) -> None:
        wf = self._antipattern_workflow()
        assert "--check-only" in wf, (
            "adg-antipattern-ci.yml must use --check-only (not --fix) in CI"
        )

    def test_antipattern_workflow_triggers_on_push_and_pr(self) -> None:
        wf = self._antipattern_workflow()
        assert "push" in wf
        assert "pull_request" in wf

    def test_no_grep_in_ci_workflows_themselves(self) -> None:
        """CI workflow YAML files must not invoke grep/rg as search substitutes."""
        workflows_dir = ROOT / ".github" / "workflows"
        for yml in workflows_dir.glob("*.yml"):
            content = yml.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                if "run: grep" in line or "run: rg " in line:
                    pytest.fail(
                        f"{yml.name}:{i}: CI workflow must not invoke grep/rg as commands.\n"
                        f"  Line: {line.strip()}"
                    )
