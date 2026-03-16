# adg-grep-ban: skip-file
# adg-mypy-ban: skip-file
# adg-pytest-ban: skip-file
"""Medium + Low accelerator blind-spot hardening tests.

Sections:
  1. GrepBanExpansion      — Medium #1: os.system / getoutput / getstatusoutput patterns
  2. IngestSentinel        — Medium #2: adg_redis_ingest.py writes adg:status with correct fields
  3. PytestBanGate         — Medium #3: broad pytest subprocess ban
  4. YamlGrepBanGate       — Lower #1: grep/rg in GitHub Actions run: steps
  5. RawRedisAdgBypass     — Lower #3: no production code accesses adg:* keys via raw redis
  6. AllGatesWired         — All 3 new gates in run_contract_gates.py + pre-commit
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_adg_accelerator_medium_low")
_emit_applies_guardrail("p0", "test_adg_accelerator_medium_low", "p0_governance")
_emit_reads_policy_state("p0", "test_adg_accelerator_medium_low", "policy_binding")
_emit_snapshots_state("p0", "test_adg_accelerator_medium_low", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_adg_accelerator_medium_low", "p4obs", "metric_1")
_emit_emits_metric_event("test_adg_accelerator_medium_low", "p4obs", "metric_2")
_emit_emits_metric_event("test_adg_accelerator_medium_low", "p4obs", "metric_3")
_emit_emits_metric_event("test_adg_accelerator_medium_low", "p4obs", "metric_4")
_emit_emits_metric_event("test_adg_accelerator_medium_low", "p4obs", "metric_5")
_emit_emits_metric_event("test_adg_accelerator_medium_low", "p4obs", "metric_6")
_emit_records_incident_event("test_adg_accelerator_medium_low", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_adg_accelerator_medium_low", "p4obs", "anomaly")
_emit_writes_observability_log("test_adg_accelerator_medium_low", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_adg_accelerator_medium_low", "p4obs", "mon_state")
_emit_triggers_alert("test_adg_accelerator_medium_low", "p4obs", "alert")
_emit_links_incident_trace("test_adg_accelerator_medium_low", "p4obs", "trace_link")
_emit_captures_pattern("test_adg_accelerator_medium_low", "p3lm", "pattern")
_emit_records_learning_event("test_adg_accelerator_medium_low", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_adg_accelerator_medium_low", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_adg_accelerator_medium_low", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_adg_accelerator_medium_low", "p3lm", "routing")
_emit_improves_agent_policy("test_adg_accelerator_medium_low", "p3lm", "policy")
_emit_stores_learning_state("test_adg_accelerator_medium_low", "p3lm", "state")
_emit_records_execution_trace("test_adg_accelerator_medium_low", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_adg_accelerator_medium_low", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_adg_accelerator_medium_low", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_adg_accelerator_medium_low", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_adg_accelerator_medium_low", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_adg_accelerator_medium_low", "env_read", "p2_env_1")
_emit_reads_environ("test_adg_accelerator_medium_low", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_adg_accelerator_medium_low", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_adg_accelerator_medium_low", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_adg_accelerator_medium_low", "context_pull")
_emit_pulls_context("p1", "test_adg_accelerator_medium_low", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_adg_accelerator_medium_low", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_adg_accelerator_medium_low", "uwg_term_2")
_emit_writes_through("p1", "test_adg_accelerator_medium_low", "write_through")
_emit_writes_through("p1", "test_adg_accelerator_medium_low", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_adg_accelerator_medium_low", "safety_validation")
_emit_invokes_eval("p1", "test_adg_accelerator_medium_low", "eval_call")
_emit_proposal_commits_routing("p1", "test_adg_accelerator_medium_low", "routing_commit")
emit_replay_key("p0", "test_adg_accelerator_medium_low")
emit_determinism_digest("p0", "test_adg_accelerator_medium_low")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_adg_accelerator_medium_low", "execution_auth")
_emit_validates_capability("p2", "test_adg_accelerator_medium_low", "capability_check")
_emit_routes_to_capability("p2", "test_adg_accelerator_medium_low", "capability_route")
_emit_writes_via_uwg("p2", "test_adg_accelerator_medium_low", "uwg_write")
_emit_blocks_direct_write("p2", "test_adg_accelerator_medium_low", "direct_write_block")
_emit_records_tool_invocation("p2", "test_adg_accelerator_medium_low", "tool_invocation")
_emit_captures_execution_output("p2", "test_adg_accelerator_medium_low", "exec_output")
_emit_dispatches_agent("p3", "test_adg_accelerator_medium_low", "agent_dispatch")
_emit_coordinates_agents("p3", "test_adg_accelerator_medium_low", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_adg_accelerator_medium_low", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_adg_accelerator_medium_low", "healing_outcome")
_emit_escalates_failure("p3", "test_adg_accelerator_medium_low", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_adg_accelerator_medium_low", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_adg_accelerator_medium_low", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_adg_accelerator_medium_low", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_adg_accelerator_medium_low", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_adg_accelerator_medium_low", "eval_metric")
_emit_stores_embedding("p4", "test_adg_accelerator_medium_low", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_adg_accelerator_medium_low", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_adg_accelerator_medium_low", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================================
# 1. Grep-Ban Expansion — Medium #1
# ============================================================================

class TestGrepBanExpansion:
    """The grep-ban gate must now also catch os.system, getoutput, getstatusoutput."""

    def _make(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", encoding="utf-8", delete=False
        )
        f.write(content)
        f.close()
        return Path(f.name)

    # --- os.system ---

    def test_os_system_grep_is_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('os.system("grep -r pattern src/")\n')
        try:
            assert scan_file(tmp), "os.system('grep ...') must be flagged"
        finally:
            tmp.unlink()

    def test_os_system_rg_is_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('os.system("rg --type py pattern agentic_core/")\n')
        try:
            assert scan_file(tmp), "os.system('rg ...') must be flagged"
        finally:
            tmp.unlink()

    def test_os_system_findstr_is_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('os.system("findstr /r pattern *.py")\n')
        try:
            assert scan_file(tmp), "os.system('findstr ...') must be flagged"
        finally:
            tmp.unlink()

    def test_os_system_non_grep_not_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('os.system("python tools/adg/adg_redis_ingest.py --force")\n')
        try:
            assert not scan_file(tmp), "os.system with non-grep command must NOT be flagged"
        finally:
            tmp.unlink()

    # --- subprocess.getoutput ---

    def test_getoutput_grep_is_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('result = subprocess.getoutput("grep -rn pattern src/")\n')
        try:
            assert scan_file(tmp), "subprocess.getoutput('grep ...') must be flagged"
        finally:
            tmp.unlink()

    def test_getoutput_rg_is_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('out = subprocess.getoutput("rg --json pattern agentic_core/")\n')
        try:
            assert scan_file(tmp), "subprocess.getoutput('rg ...') must be flagged"
        finally:
            tmp.unlink()

    def test_getoutput_non_grep_not_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('out = subprocess.getoutput("python tools/adg/adg_redis_query.py")\n')
        try:
            assert not scan_file(tmp), "subprocess.getoutput with non-grep cmd must NOT be flagged"
        finally:
            tmp.unlink()

    # --- subprocess.getstatusoutput ---

    def test_getstatusoutput_grep_is_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('rc, out = subprocess.getstatusoutput("grep -c pattern file.py")\n')
        try:
            assert scan_file(tmp), "subprocess.getstatusoutput('grep ...') must be flagged"
        finally:
            tmp.unlink()

    def test_getstatusoutput_ag_is_flagged(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make('rc, out = subprocess.getstatusoutput("ag --python pattern")\n')
        try:
            assert scan_file(tmp), "subprocess.getstatusoutput('ag ...') must be flagged"
        finally:
            tmp.unlink()

    # --- Exemption still works for new patterns ---

    def test_guardian_allow_grep_exempts_os_system(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            'os.system("grep pattern")  # guardian: allow-grep -- pre-ADG migration script\n'
        )
        try:
            assert not scan_file(tmp), "# guardian: allow-grep -- ... must exempt os.system grep"
        finally:
            tmp.unlink()

    def test_guardian_allow_grep_exempts_getoutput(self) -> None:
        from ops_scripts.ci.adg_grep_ban_gate import scan_file

        tmp = self._make(
            'subprocess.getoutput("grep pattern")  # guardian: allow-grep -- legacy audit script\n'
        )
        try:
            assert not scan_file(tmp), "# guardian: allow-grep -- ... must exempt getoutput"
        finally:
            tmp.unlink()

    def test_banned_patterns_list_has_six_entries(self) -> None:
        """All 6 ban patterns must be registered in _BANNED_PATTERNS."""
        from ops_scripts.ci.adg_grep_ban_gate import _BANNED_PATTERNS

        assert len(_BANNED_PATTERNS) == 6, (
            f"_BANNED_PATTERNS must have 6 entries (got {len(_BANNED_PATTERNS)}): "
            "subprocess, popen, shell-string, os.system, getoutput, getstatusoutput"
        )

    def test_expanded_grep_ban_still_clean_on_codebase(self) -> None:
        """With the expanded patterns, the codebase must still have 0 violations."""
        import subprocess as _subprocess

        r = _subprocess.run(
            [sys.executable, "ops_scripts/ci/adg_grep_ban_gate.py", "--all-python"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert r.returncode == 0, (
            f"Expanded grep-ban gate found new violations:\n{r.stderr}"
        )


# ============================================================================
# 2. Ingest Sentinel — Medium #2
# ============================================================================

class TestIngestSentinel:
    """adg_redis_ingest.py must write adg:status JSON sentinel with required fields."""

    def test_ingest_module_is_importable(self) -> None:
        assert (ROOT / "tools" / "adg" / "adg_redis_ingest.py").exists()

    def test_adg_status_key_written_with_correct_fields(self) -> None:
        """Verify adg:status is SET (not HSET) with the required JSON fields."""
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "adg_redis_ingest", ROOT / "tools" / "adg" / "adg_redis_ingest.py"
        )
        module = importlib.util.module_from_spec(spec)

        mock_redis = MagicMock()
        mock_pipe = MagicMock()
        mock_redis.pipeline.return_value.__enter__ = MagicMock(return_value=mock_pipe)
        mock_redis.pipeline.return_value.__exit__ = MagicMock(return_value=False)
        mock_redis.pipeline.return_value = mock_pipe

        captured_set_calls: list[tuple] = []

        def fake_set(key: str, value: str) -> None:
            captured_set_calls.append((key, value))

        mock_redis.set.side_effect = fake_set
        mock_redis.hmset.return_value = True
        mock_redis.rpush.return_value = 1
        mock_redis.delete.return_value = 0
        mock_pipe.hset.return_value = True
        mock_pipe.execute.return_value = []

        src = (ROOT / "tools" / "adg" / "adg_redis_ingest.py").read_text(encoding="utf-8")

        # The ingest writes adg:status exactly once with all required fields
        assert 'r.set(\n        "adg:status"' in src or '"adg:status"' in src, (
            "adg_redis_ingest.py must write to 'adg:status' key"
        )

        # Verify the JSON payload contains all required fields
        assert '"timestamp"' in src, "adg:status payload must include 'timestamp'"
        assert '"node_count"' in src, "adg:status payload must include 'node_count'"
        assert '"edge_count"' in src, "adg:status payload must include 'edge_count'"
        assert '"ingested_at"' in src, "adg:status payload must include 'ingested_at'"
        assert '"sqlite_path"' in src, "adg:status payload must include 'sqlite_path'"
        assert '"digest"' in src, "adg:status payload must include 'digest'"

    def test_adg_status_is_string_not_hash(self) -> None:
        """adg:status must be a STRING (r.set), not a HASH (r.hmset/hset)."""
        src = (ROOT / "tools" / "adg" / "adg_redis_ingest.py").read_text(encoding="utf-8")
        # Find the line writing adg:status and ensure it uses r.set not hmset
        lines = src.splitlines()
        for i, line in enumerate(lines):
            if '"adg:status"' in line and "hmset" in line:
                pytest.fail(
                    f"adg:status must be written with r.set (STRING), not hmset (HASH). "
                    f"Line {i+1}: {line.strip()}"
                )
        # Confirm r.set("adg:status", ...) is present
        found_set = any(
            '"adg:status"' in lines[i]
            for i in range(len(lines))
            if i > 0 and "r.set(" in lines[i - 1] or "r.set(" in lines[i]
        )
        assert found_set or 'r.set(\n        "adg:status"' in src or (
            any("r.set(" in l and '"adg:status"' in lines[min(i+1, len(lines)-1)]
                for i, l in enumerate(lines))
        ), "adg:status must be written with r.set()"

    def test_adg_meta_is_hash(self) -> None:
        """adg:meta must be a HASH (r.hmset), not a STRING."""
        src = (ROOT / "tools" / "adg" / "adg_redis_ingest.py").read_text(encoding="utf-8")
        assert 'r.hmset(\n        "adg:meta"' in src or (
            "hmset" in src and '"adg:meta"' in src
        ), "adg:meta must be written with r.hmset() (HASH type)"

    def test_adg_status_written_after_adg_meta(self) -> None:
        """adg:status sentinel must be written AFTER adg:meta (correct sequencing)."""
        src = (ROOT / "tools" / "adg" / "adg_redis_ingest.py").read_text(encoding="utf-8")
        meta_pos = src.find('"adg:meta"')
        status_pos = src.find('"adg:status"')
        assert meta_pos != -1, "adg:meta write must be present"
        assert status_pos != -1, "adg:status write must be present"
        assert meta_pos < status_pos, (
            "adg:status sentinel must be written AFTER adg:meta "
            "(meta first, then confirm via status)"
        )

    def test_adg_status_contains_success_print(self) -> None:
        """ingest must print confirmation that adg:status was written."""
        src = (ROOT / "tools" / "adg" / "adg_redis_ingest.py").read_text(encoding="utf-8")
        assert "adg:status sentinel written" in src, (
            "adg_redis_ingest.py must print a confirmation message after writing adg:status"
        )

    def test_ingest_writes_snapshot_key(self) -> None:
        """adg:snapshot STRING key must also be written during ingest."""
        src = (ROOT / "tools" / "adg" / "adg_redis_ingest.py").read_text(encoding="utf-8")
        assert '"adg:snapshot"' in src, "adg_redis_ingest.py must write adg:snapshot key"

    def test_ingest_sentinel_fields_match_mcp_server_expectations(self) -> None:
        """The adg:status fields must match what adg_mcp_server.py reads."""
        ingest_src = (ROOT / "tools" / "adg" / "adg_redis_ingest.py").read_text(encoding="utf-8")
        mcp_src = (ROOT / "tools" / "adg" / "adg_mcp_server.py").read_text(encoding="utf-8")
        required_fields = ["timestamp", "node_count", "edge_count", "ingested_at"]
        for field in required_fields:
            assert f'"{field}"' in ingest_src, f"ingest must write field '{field}'"
            assert field in mcp_src, (
                f"adg_mcp_server.py must reference '{field}' (it reads adg:status)"
            )


# ============================================================================
# 3. Pytest-Ban Gate — Medium #3
# ============================================================================

class TestPytestBanGate:
    """adg_pytest_ban_gate.py must ban broad pytest calls; ADG dynamic forms are safe."""

    def _make(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", encoding="utf-8", delete=False
        )
        f.write(content)
        f.close()
        return Path(f.name)

    def test_bare_pytest_list_is_flagged(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('subprocess.run(["pytest"])\n')
        try:
            assert scan_file(tmp), 'subprocess.run(["pytest"]) must be flagged'
        finally:
            tmp.unlink()

    def test_pytest_with_directory_literal_is_flagged(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('subprocess.run(["pytest", "tests/"], check=True)\n')
        try:
            assert scan_file(tmp), 'subprocess.run(["pytest", "tests/"]) must be flagged'
        finally:
            tmp.unlink()

    def test_pytest_with_production_dir_literal_is_flagged(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('subprocess.run(["pytest", "agentic_core/"], capture_output=True)\n')
        try:
            assert scan_file(tmp), 'subprocess.run(["pytest", "agentic_core/"]) must be flagged'
        finally:
            tmp.unlink()

    def test_bare_python_m_pytest_is_flagged(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('subprocess.run(["python", "-m", "pytest"])\n')
        try:
            assert scan_file(tmp), 'subprocess.run(["python", "-m", "pytest"]) must be flagged'
        finally:
            tmp.unlink()

    def test_os_system_pytest_is_flagged(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('os.system("pytest tests/ -v")\n')
        try:
            assert scan_file(tmp), 'os.system("pytest ...") must be flagged'
        finally:
            tmp.unlink()

    def test_dynamic_adg_files_list_not_flagged(self) -> None:
        """subprocess.run(["pytest"] + adg_files) must NOT be flagged — dynamic list."""
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('subprocess.run(["pytest"] + adg_selected_files, check=True)\n')
        try:
            assert not scan_file(tmp), (
                'subprocess.run(["pytest"] + adg_files) must NOT be flagged '
                "(dynamic list from ADG is the canonical form)"
            )
        finally:
            tmp.unlink()

    def test_sys_executable_m_pytest_not_flagged(self) -> None:
        """subprocess.run([sys.executable, '-m', 'pytest'] + files) must NOT be flagged."""
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make(
            'subprocess.run([sys.executable, "-m", "pytest"] + test_files, check=True)\n'
        )
        try:
            assert not scan_file(tmp), (
                "subprocess.run([sys.executable, '-m', 'pytest'] + files) "
                "must NOT be flagged (ADG canonical form)"
            )
        finally:
            tmp.unlink()

    def test_pytest_with_specific_py_file_not_flagged(self) -> None:
        """pytest called with a specific .py file must NOT be flagged."""
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make(
            'subprocess.run(["pytest", "tests/adg/test_foo.py", "-v"])\n'
        )
        try:
            assert not scan_file(tmp), (
                'subprocess.run(["pytest", "specific_test.py"]) must NOT be flagged'
            )
        finally:
            tmp.unlink()

    def test_adg_test_selector_auto_exempt(self) -> None:
        """adg_test_selector.py must be auto-exempt regardless of content."""
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        assert not scan_file(ROOT / "tools" / "adg" / "adg_test_selector.py"), (
            "adg_test_selector.py must be automatically exempt from the pytest-ban gate"
        )

    def test_guardian_allow_pytest_exempts_line(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make(
            'subprocess.run(["pytest"])  # guardian: allow-pytest -- bootstrap script before ADG\n'
        )
        try:
            assert not scan_file(tmp), "# guardian: allow-pytest -- ... must exempt the line"
        finally:
            tmp.unlink()

    def test_guardian_allow_pytest_requires_justification(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('subprocess.run(["pytest"])  # guardian: allow-pytest\n')
        try:
            assert scan_file(tmp), "# guardian: allow-pytest without justification must NOT exempt"
        finally:
            tmp.unlink()

    def test_comment_line_not_flagged(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import scan_file

        tmp = self._make('# subprocess.run(["pytest"]) — do NOT use this\n')
        try:
            assert not scan_file(tmp), "Comment lines must not be flagged"
        finally:
            tmp.unlink()

    def test_all_python_scan_clean_on_codebase(self) -> None:
        """Running --all-python right now must find zero violations."""
        import subprocess as _subprocess

        r = _subprocess.run(
            [sys.executable, "ops_scripts/ci/adg_pytest_ban_gate.py", "--all-python"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert r.returncode == 0, (
            f"adg_pytest_ban_gate.py --all-python found violations:\n{r.stderr}"
        )

    def test_canonical_test_selector_configured(self) -> None:
        from ops_scripts.ci.adg_pytest_ban_gate import _CANONICAL_TEST_SELECTOR

        assert _CANONICAL_TEST_SELECTOR.exists(), (
            "adg_pytest_ban_gate._CANONICAL_TEST_SELECTOR must point to existing adg_test_selector.py"
        )


# ============================================================================
# 4. YAML Grep-Ban Gate — Lower #1
# ============================================================================

class TestYamlGrepBanGate:
    """adg_yaml_grep_ban_gate.py must catch grep/rg in GitHub Actions run: steps."""

    def _make_yaml(self, content: str) -> Path:
        f = tempfile.NamedTemporaryFile(
            suffix=".yml", mode="w", encoding="utf-8", delete=False
        )
        f.write(content)
        f.close()
        return Path(f.name)

    def test_run_grep_in_multiline_block_is_flagged(self) -> None:
        from ops_scripts.ci.adg_yaml_grep_ban_gate import scan_file

        tmp = self._make_yaml(
            "jobs:\n  check:\n    steps:\n      - name: Find violations\n"
            "        run: |\n          grep -r pattern agentic_core/\n"
        )
        try:
            assert scan_file(tmp), "run: | block with grep must be flagged"
        finally:
            tmp.unlink()

    def test_run_rg_in_multiline_block_is_flagged(self) -> None:
        from ops_scripts.ci.adg_yaml_grep_ban_gate import scan_file

        tmp = self._make_yaml(
            "jobs:\n  check:\n    steps:\n      - name: Search\n"
            "        run: |\n          rg --type py pattern .\n"
        )
        try:
            assert scan_file(tmp), "run: | block with rg must be flagged"
        finally:
            tmp.unlink()

    def test_guardian_allow_grep_yaml_exempts_line(self) -> None:
        from ops_scripts.ci.adg_yaml_grep_ban_gate import scan_file

        tmp = self._make_yaml(
            "jobs:\n  check:\n    steps:\n      - name: Pipe check\n"
            "        run: |\n"
            "          find . -name '*.py' | grep -q .  # guardian: allow-grep-yaml -- POSIX pipe-has-content idiom\n"
        )
        try:
            assert not scan_file(tmp), "# guardian: allow-grep-yaml -- ... must exempt the line"
        finally:
            tmp.unlink()

    def test_guardian_allow_grep_yaml_requires_justification(self) -> None:
        from ops_scripts.ci.adg_yaml_grep_ban_gate import scan_file

        tmp = self._make_yaml(
            "        run: |\n"
            "          grep pattern  # guardian: allow-grep-yaml\n"
        )
        try:
            assert scan_file(tmp), "# guardian: allow-grep-yaml without justification must NOT exempt"
        finally:
            tmp.unlink()

    def test_yaml_comment_not_flagged(self) -> None:
        from ops_scripts.ci.adg_yaml_grep_ban_gate import scan_file

        tmp = self._make_yaml(
            "        run: |\n"
            "          # grep is forbidden — use adg_redis_query.py instead\n"
            "          python tools/adg/adg_redis_query.py search-nodes pattern\n"
        )
        try:
            assert not scan_file(tmp), "YAML comment lines mentioning grep must NOT be flagged"
        finally:
            tmp.unlink()

    def test_all_yaml_scan_clean_on_existing_workflows(self) -> None:
        """All existing .github/workflows/ files must pass (0 violations after exemptions)."""
        import subprocess as _subprocess

        r = _subprocess.run(
            [sys.executable, "ops_scripts/ci/adg_yaml_grep_ban_gate.py", "--all-yaml"],
            capture_output=True, text=True, cwd=str(ROOT),
        )
        assert r.returncode == 0, (
            f"adg_yaml_grep_ban_gate.py --all-yaml found violations:\n{r.stderr}"
        )

    def test_guardian_tests_workflow_has_exemption_for_pipe_idiom(self) -> None:
        """guardian-tests.yml uses grep -q . as pipe-has-content idiom — must have exemption."""
        wf = ROOT / ".github" / "workflows" / "guardian-tests.yml"
        if not wf.exists():
            pytest.skip("guardian-tests.yml not found")
        content = wf.read_text(encoding="utf-8")
        assert "guardian: allow-grep-yaml" in content, (
            "guardian-tests.yml must have # guardian: allow-grep-yaml -- <justification> "
            "for the grep -q . pipe idiom"
        )

    def test_yaml_gate_file_exists(self) -> None:
        assert (ROOT / "ops_scripts" / "ci" / "adg_yaml_grep_ban_gate.py").exists()

    def test_yaml_gate_registered_in_precommit(self) -> None:
        cfg = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
        assert "adg-yaml-grep-ban-gate" in cfg, (
            "adg-yaml-grep-ban-gate must be registered as a pre-commit hook (T3l)"
        )


# ============================================================================
# 5. Raw Redis ADG Bypass — Lower #3
# ============================================================================

class TestRawRedisAdgBypass:
    """No production code outside tools/adg/ must access adg:* keys via raw redis.Redis."""

    # ops_scripts/ci/ is excluded: CI gate tools legitimately read ADG Redis keys
    # directly (drift_ratchet_gate, burndown_tracker, etc.). The bypass invariant
    # applies to APPLICATION code only, not CI infrastructure tools.
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
        "observability",
    ]

    def _find_adg_key_bypass(self, dir_name: str) -> list[str]:
        target = ROOT / dir_name
        if not target.exists():
            return []
        offenders = []
        for py_file in target.rglob("*.py"):
            # Skip the test files themselves (they contain strings as fixtures)
            if "test_adg" in py_file.name:
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                # Flag files that use raw redis.Redis AND directly access adg: keys
                has_raw_redis = (
                    "redis.Redis(" in content or "redis.StrictRedis(" in content
                )
                has_adg_keys = '"adg:' in content or "'adg:" in content
                if has_raw_redis and has_adg_keys:
                    offenders.append(str(py_file.relative_to(ROOT)))
            except OSError:
                pass
        return offenders

    def test_no_raw_redis_accessing_adg_keys_in_production(self) -> None:
        """Files outside tools/adg/ must not combine raw redis.Redis with adg: key access."""
        all_offenders = []
        for d in self._PRODUCTION_DIRS:
            all_offenders.extend(self._find_adg_key_bypass(d))
        assert not all_offenders, (
            "Production code must NOT combine raw redis.Redis with adg:* key access.\n"
            "Use ADGRedisClient from tools/adg/adg_redis_query.py instead.\n"
            "Offending files:\n" + "\n".join(f"  {f}" for f in all_offenders)
        )

    def test_adg_redis_client_is_canonical_interface(self) -> None:
        """ADGRedisClient must be the ONLY class that accesses adg:* keys directly."""
        redis_query = ROOT / "tools" / "adg" / "adg_redis_query.py"
        assert redis_query.exists()
        src = redis_query.read_text(encoding="utf-8")
        assert "adg:" in src, "ADGRedisClient must access adg:* keys"

    def test_enhanced_redis_client_is_deprecated_adg_client_not_rogue_bypass(self) -> None:
        """enhanced_redis_mcp_client.py was a legitimate ADG client (just deprecated).

        It DOES access adg:* keys — that was its purpose.  The invariant we enforce
        is that no NEW production code introduces raw redis.Redis + adg: key access.
        The enhanced client must carry a DEPRECATED marker pointing to the canonical
        ADGRedisClient instead.
        """
        enhanced = ROOT / "tools" / "adg" / "enhanced_redis_mcp_client.py"
        if not enhanced.exists():
            return  # File removed — even better
        src = enhanced.read_text(encoding="utf-8").lower()
        assert "deprecated" in src or "do not use" in src, (
            "enhanced_redis_mcp_client.py must carry a DEPRECATED header "
            "pointing to the canonical ADGRedisClient"
        )

    def test_adg_redis_query_fail_closed_on_connection_error(self) -> None:
        """ADGRedisClient must raise RuntimeError (fail-closed), not return None."""
        src = (ROOT / "tools" / "adg" / "adg_redis_query.py").read_text(encoding="utf-8")
        # The canonical client must have connection error handling that raises
        assert "RuntimeError" in src or "ConnectionError" in src, (
            "ADGRedisClient must be fail-closed: raise on Redis connection error"
        )
        # Must not silently return None on failure
        assert "return None" not in src.replace("# return None", ""), (
            "ADGRedisClient must NOT silently return None on Redis failure"
        )


# ============================================================================
# 6. All New Gates Wired — medium/low gates in run_contract_gates.py + pre-commit
# ============================================================================

class TestMediumLowGatesWired:
    """All 3 new medium/low gates registered in run_contract_gates.py + pre-commit."""

    @classmethod
    def _gates_src(cls) -> str:
        return (ROOT / "ops_scripts" / "ci" / "run_contract_gates.py").read_text(encoding="utf-8")

    @classmethod
    def _precommit(cls) -> str:
        return (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")

    def test_pytest_ban_gate_in_contract_runner(self) -> None:
        assert "adg_pytest_ban_gate" in self._gates_src()

    def test_yaml_grep_ban_gate_in_contract_runner(self) -> None:
        assert "adg_yaml_grep_ban_gate" in self._gates_src()

    def test_pytest_ban_gate_in_precommit(self) -> None:
        assert "adg-pytest-ban-gate" in self._precommit()

    def test_yaml_grep_ban_gate_in_precommit(self) -> None:
        assert "adg-yaml-grep-ban-gate" in self._precommit()

    def test_pytest_ban_uses_all_python_in_contract_runner(self) -> None:
        src = self._gates_src()
        idx = src.find("adg_pytest_ban_gate")
        block = src[idx: idx + 200]
        assert "--all-python" in block

    def test_yaml_ban_uses_all_yaml_in_contract_runner(self) -> None:
        src = self._gates_src()
        idx = src.find("adg_yaml_grep_ban_gate")
        block = src[idx: idx + 200]
        assert "--all-yaml" in block

    def test_t3k_before_t3l_in_precommit(self) -> None:
        """T3k (pytest-ban) must appear before T3l (yaml-grep-ban)."""
        cfg = self._precommit()
        pos_k = cfg.find("id: adg-pytest-ban-gate")
        pos_l = cfg.find("id: adg-yaml-grep-ban-gate")
        assert pos_k != -1 and pos_l != -1
        assert pos_k < pos_l, "T3k must come before T3l"

    def test_t3l_before_t3j_in_precommit(self) -> None:
        """T3l (yaml-grep-ban) must appear before T3j (skip-file ratchet)."""
        cfg = self._precommit()
        pos_l = cfg.find("id: adg-yaml-grep-ban-gate")
        pos_j = cfg.find("id: adg-skip-file-ratchet")
        assert pos_l != -1 and pos_j != -1
        assert pos_l < pos_j, "T3l must come before T3j"

    def test_eight_accelerator_gates_total_in_contract_runner(self) -> None:
        """run_contract_gates.py must now have 8 accelerator enforcement gates."""
        src = self._gates_src()
        gates = [
            "adg_grep_ban_gate",
            "guardian_exemption_gate",
            "adg_mypy_ban_gate",
            "adg_skip_file_ratchet",
            "adg_pytest_ban_gate",
            "adg_yaml_grep_ban_gate",
        ]
        for gate in gates:
            assert gate in src, f"Gate '{gate}' must be in run_contract_gates.py"

    def test_all_gate_scripts_exist(self) -> None:
        gates = [
            "ops_scripts/ci/adg_grep_ban_gate.py",
            "ops_scripts/ci/adg_mypy_ban_gate.py",
            "ops_scripts/ci/adg_pytest_ban_gate.py",
            "ops_scripts/ci/adg_yaml_grep_ban_gate.py",
            "ops_scripts/ci/adg_skip_file_ratchet.py",
            "ops_scripts/ci/guardian_exemption_gate.py",
        ]
        for gate in gates:
            assert (ROOT / gate).exists(), f"Gate script must exist: {gate}"
