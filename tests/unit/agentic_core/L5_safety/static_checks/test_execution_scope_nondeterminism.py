"""
Unit tests for ExecutionScopeNondeterminismVisitor and
scan_file_for_execution_nondeterminism (Gap 7 — determinism proof surface).
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
    _EXEC_ALLOWLIST_COMMENT,
    ExecutionScopeNondeterminismVisitor,
    scan_file_for_execution_nondeterminism,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_execution_scope_nondeterminism", "p4obs", "metric_1")
_emit_emits_metric_event("test_execution_scope_nondeterminism", "p4obs", "metric_2")
_emit_emits_metric_event("test_execution_scope_nondeterminism", "p4obs", "metric_3")
_emit_emits_metric_event("test_execution_scope_nondeterminism", "p4obs", "metric_4")
_emit_emits_metric_event("test_execution_scope_nondeterminism", "p4obs", "metric_5")
_emit_emits_metric_event("test_execution_scope_nondeterminism", "p4obs", "metric_6")
_emit_records_incident_event("test_execution_scope_nondeterminism", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_execution_scope_nondeterminism", "p4obs", "anomaly")
_emit_writes_observability_log("test_execution_scope_nondeterminism", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_execution_scope_nondeterminism", "p4obs", "mon_state")
_emit_triggers_alert("test_execution_scope_nondeterminism", "p4obs", "alert")
_emit_links_incident_trace("test_execution_scope_nondeterminism", "p4obs", "trace_link")
_emit_captures_pattern("test_execution_scope_nondeterminism", "p3lm", "pattern")
_emit_records_learning_event("test_execution_scope_nondeterminism", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_execution_scope_nondeterminism", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_execution_scope_nondeterminism", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_execution_scope_nondeterminism", "p3lm", "routing")
_emit_improves_agent_policy("test_execution_scope_nondeterminism", "p3lm", "policy")
_emit_stores_learning_state("test_execution_scope_nondeterminism", "p3lm", "state")
_emit_records_execution_trace("test_execution_scope_nondeterminism", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_execution_scope_nondeterminism", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_execution_scope_nondeterminism", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_execution_scope_nondeterminism", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_execution_scope_nondeterminism", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_execution_scope_nondeterminism", "env_read", "p2_env_1")
_emit_reads_environ("test_execution_scope_nondeterminism", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_execution_scope_nondeterminism", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_execution_scope_nondeterminism", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_execution_scope_nondeterminism")
_emit_applies_guardrail("p0", "test_execution_scope_nondeterminism", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_scope_nondeterminism", "policy_binding")
_emit_snapshots_state("p0", "test_execution_scope_nondeterminism", "state_snapshot")
_emit_pulls_context("p1", "test_execution_scope_nondeterminism", "context_pull")
_emit_pulls_context("p1", "test_execution_scope_nondeterminism", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_execution_scope_nondeterminism", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_execution_scope_nondeterminism", "uwg_term_secondary")
_emit_writes_through("p1", "test_execution_scope_nondeterminism", "write_through")
_emit_writes_through("p1", "test_execution_scope_nondeterminism", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_execution_scope_nondeterminism", "safety_validation")
_emit_invokes_eval("p1", "test_execution_scope_nondeterminism", "eval_call")
_emit_proposal_commits_routing("p1", "test_execution_scope_nondeterminism", "routing_commit")
emit_replay_key("p0", "test_execution_scope_nondeterminism")
emit_determinism_digest("p0", "test_execution_scope_nondeterminism")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_scope_nondeterminism", "execution_auth")
_emit_validates_capability("p2", "test_execution_scope_nondeterminism", "capability_check")
_emit_routes_to_capability("p2", "test_execution_scope_nondeterminism", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_scope_nondeterminism", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_scope_nondeterminism", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_scope_nondeterminism", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_scope_nondeterminism", "exec_output")
_emit_dispatches_agent("p3", "test_execution_scope_nondeterminism", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_scope_nondeterminism", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_scope_nondeterminism", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_scope_nondeterminism", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_scope_nondeterminism", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_scope_nondeterminism", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_scope_nondeterminism", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_scope_nondeterminism", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_scope_nondeterminism", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_scope_nondeterminism", "eval_metric")
_emit_stores_embedding("p4", "test_execution_scope_nondeterminism", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_scope_nondeterminism", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_scope_nondeterminism", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan(source: str) -> list[tuple[int, str, str]]:
    source_lines = source.splitlines()
    tree = ast.parse(textwrap.dedent(source))
    visitor = ExecutionScopeNondeterminismVisitor(source_lines)
    visitor.visit(tree)
    return visitor.violations


def _rule_ids(violations: list[tuple]) -> list[str]:
    return [v[1] for v in violations]


# ---------------------------------------------------------------------------
# time.* calls
# ---------------------------------------------------------------------------


def test_detects_time_time() -> None:
    src = "import time\nresult = time.time()\n"
    viols = _scan(src)
    assert "EXEC_TIME_CALL" in _rule_ids(viols)


def test_detects_time_monotonic() -> None:
    src = "import time\nt = time.monotonic()\n"
    viols = _scan(src)
    assert "EXEC_TIME_CALL" in _rule_ids(viols)


def test_detects_time_sleep() -> None:
    src = "import time\ntime.sleep(1)\n"
    viols = _scan(src)
    assert "EXEC_TIME_CALL" in _rule_ids(viols)


def test_detects_time_perf_counter() -> None:
    src = "import time\nt = time.perf_counter()\n"
    viols = _scan(src)
    assert "EXEC_TIME_CALL" in _rule_ids(viols)


# ---------------------------------------------------------------------------
# datetime.* calls
# ---------------------------------------------------------------------------


def test_detects_datetime_now() -> None:
    src = "from datetime import datetime\nnow = datetime.now()\n"
    viols = _scan(src)
    assert "EXEC_DATETIME_NOW" in _rule_ids(viols)


def test_detects_datetime_utcnow() -> None:
    src = "from datetime import datetime\nnow = datetime.utcnow()\n"
    viols = _scan(src)
    assert "EXEC_DATETIME_NOW" in _rule_ids(viols)


# ---------------------------------------------------------------------------
# random.* calls
# ---------------------------------------------------------------------------


def test_detects_random_random() -> None:
    src = "import random\nx = random.random()\n"
    viols = _scan(src)
    assert "EXEC_RANDOM_CALL" in _rule_ids(viols)


def test_detects_random_choice() -> None:
    src = "import random\nx = random.choice([1, 2, 3])\n"
    viols = _scan(src)
    assert "EXEC_RANDOM_CALL" in _rule_ids(viols)


def test_random_Random_constructor_not_flagged() -> None:
    """random.Random(seed) is deterministic — must not be flagged."""
    src = "import random\nrng = random.Random(42)\n"
    viols = _scan(src)
    assert "EXEC_RANDOM_CALL" not in _rule_ids(viols)


def test_random_seed_not_flagged() -> None:
    src = "import random\nrandom.seed(0)\n"
    viols = _scan(src)
    assert "EXEC_RANDOM_CALL" not in _rule_ids(viols)


# ---------------------------------------------------------------------------
# uuid.uuid4()
# ---------------------------------------------------------------------------


def test_detects_uuid_uuid4() -> None:
    src = "import uuid\nuid = uuid.uuid4()\n"
    viols = _scan(src)
    assert "EXEC_UUID4_CALL" in _rule_ids(viols)


def test_uuid_uuid5_not_flagged() -> None:
    """uuid.uuid5() is deterministic (name-based) — must not be flagged."""
    src = "import uuid\nuid = uuid.uuid5(uuid.NAMESPACE_DNS, 'test')\n"
    viols = _scan(src)
    assert "EXEC_UUID4_CALL" not in _rule_ids(viols)


# ---------------------------------------------------------------------------
# Allowlist comment suppression
# ---------------------------------------------------------------------------


def test_allowlist_comment_suppresses_time_call() -> None:
    src = f"import time\nt = time.time()  {_EXEC_ALLOWLIST_COMMENT}\n"
    viols = _scan(src)
    assert "EXEC_TIME_CALL" not in _rule_ids(viols)


def test_allowlist_comment_suppresses_uuid4() -> None:
    src = f"import uuid\nuid = uuid.uuid4()  {_EXEC_ALLOWLIST_COMMENT}\n"
    viols = _scan(src)
    assert "EXEC_UUID4_CALL" not in _rule_ids(viols)


def test_allowlist_on_other_line_does_not_suppress() -> None:
    """Allowlist only suppresses the line it appears on."""
    src = f"import time  {_EXEC_ALLOWLIST_COMMENT}\nt = time.time()\n"
    viols = _scan(src)
    assert "EXEC_TIME_CALL" in _rule_ids(viols)


# ---------------------------------------------------------------------------
# Clean code (no violations)
# ---------------------------------------------------------------------------


def test_clean_code_has_no_violations() -> None:
    src = textwrap.dedent("""\
        def add(a, b):
            return a + b

        class Foo:
            def bar(self):
                return 42
    """)
    viols = _scan(src)
    assert viols == []


def test_deterministic_uuid5_clean() -> None:
    src = "import uuid\nreturn uuid.uuid5(uuid.NAMESPACE_DNS, name)\n"
    viols = _scan(src)
    assert viols == []


# ---------------------------------------------------------------------------
# scan_file_for_execution_nondeterminism — infra skip
# ---------------------------------------------------------------------------


def test_infra_files_skipped(tmp_path: Path) -> None:
    """Files in _DETERMINISM_INFRA_PATHS must be skipped entirely."""
    infra = tmp_path / "determinism_guard.py"
    infra.write_text("import time\ntime.time()\n", encoding="utf-8")
    viols = scan_file_for_execution_nondeterminism(infra)
    assert viols == []


def test_non_infra_file_scanned(tmp_path: Path) -> None:
    src_file = tmp_path / "my_agent.py"
    src_file.write_text("import time\ntime.time()\n", encoding="utf-8")
    viols = scan_file_for_execution_nondeterminism(src_file)
    assert any(v[1] == "EXEC_TIME_CALL" for v in viols)


def test_syntax_error_returns_scan_error(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("def (:\n", encoding="utf-8")
    viols = scan_file_for_execution_nondeterminism(bad_file)
    assert any(v[1] == "EXEC_SYNTAX_ERROR" for v in viols)


# ---------------------------------------------------------------------------
# Violation line numbers are accurate
# ---------------------------------------------------------------------------


def test_violation_line_number_accurate() -> None:
    src = "x = 1\ny = 2\nimport uuid\nuid = uuid.uuid4()\n"
    viols = _scan(src)
    uuid_viols = [v for v in viols if v[1] == "EXEC_UUID4_CALL"]
    assert len(uuid_viols) == 1
    assert uuid_viols[0][0] == 4


def test_multiple_violations_reported() -> None:
    src = "import time, uuid\ntime.time()\nuuid.uuid4()\n"
    viols = _scan(src)
    rule_ids = _rule_ids(viols)
    assert "EXEC_TIME_CALL" in rule_ids
    assert "EXEC_UUID4_CALL" in rule_ids
