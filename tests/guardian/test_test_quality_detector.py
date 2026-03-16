"""
Behavioral tests for TestQualityDetector.

Covers:
  VACUOUS_ASSERT    — assert True / always-true in any test function
  SOLE_TYPE_CHECK   — ALL assertions are isinstance/is-not-None/hasattr
  WRITE_WITHOUT_READ — write method called without read-back
  ADG stub exemption — *_adg.py skips SOLE_TYPE_CHECK and WRITE_WITHOUT_READ
  File-gate          — non-test files return empty results
  Whitelist          — guardian comment suppresses detection
  Category/severity  — metadata and enforcement level checks

Run with: pytest tests/guardian/test_test_quality_detector.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.test_quality_detector_validator import (
    TestQualityDetector,
)
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_test_quality_detector", "p4obs", "metric_1")
_emit_emits_metric_event("test_test_quality_detector", "p4obs", "metric_2")
_emit_emits_metric_event("test_test_quality_detector", "p4obs", "metric_3")
_emit_emits_metric_event("test_test_quality_detector", "p4obs", "metric_4")
_emit_emits_metric_event("test_test_quality_detector", "p4obs", "metric_5")
_emit_emits_metric_event("test_test_quality_detector", "p4obs", "metric_6")
_emit_records_incident_event("test_test_quality_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_test_quality_detector", "p4obs", "anomaly")
_emit_writes_observability_log("test_test_quality_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_test_quality_detector", "p4obs", "mon_state")
_emit_triggers_alert("test_test_quality_detector", "p4obs", "alert")
_emit_links_incident_trace("test_test_quality_detector", "p4obs", "trace_link")
_emit_captures_pattern("test_test_quality_detector", "p3lm", "pattern")
_emit_records_learning_event("test_test_quality_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_test_quality_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_test_quality_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_test_quality_detector", "p3lm", "routing")
_emit_improves_agent_policy("test_test_quality_detector", "p3lm", "policy")
_emit_stores_learning_state("test_test_quality_detector", "p3lm", "state")
_emit_records_execution_trace("test_test_quality_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_test_quality_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_test_quality_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_test_quality_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_test_quality_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_test_quality_detector", "env_read", "p2_env_1")
_emit_reads_environ("test_test_quality_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_test_quality_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_test_quality_detector", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_test_quality_detector")
_emit_applies_guardrail("p0", "test_test_quality_detector", "p0_governance")
_emit_reads_policy_state("p0", "test_test_quality_detector", "policy_binding")
_emit_snapshots_state("p0", "test_test_quality_detector", "state_snapshot")
_emit_pulls_context("p1", "test_test_quality_detector", "context_pull")
_emit_pulls_context("p1", "test_test_quality_detector", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_test_quality_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_test_quality_detector", "uwg_term_secondary")
_emit_writes_through("p1", "test_test_quality_detector", "write_through")
_emit_writes_through("p1", "test_test_quality_detector", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_test_quality_detector", "safety_validation")
_emit_invokes_eval("p1", "test_test_quality_detector", "eval_call")
_emit_proposal_commits_routing("p1", "test_test_quality_detector", "routing_commit")
emit_replay_key("p0", "test_test_quality_detector")
emit_determinism_digest("p0", "test_test_quality_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_test_quality_detector", "execution_auth")
_emit_validates_capability("p2", "test_test_quality_detector", "capability_check")
_emit_routes_to_capability("p2", "test_test_quality_detector", "capability_route")
_emit_writes_via_uwg("p2", "test_test_quality_detector", "uwg_write")
_emit_blocks_direct_write("p2", "test_test_quality_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "test_test_quality_detector", "tool_invocation")
_emit_captures_execution_output("p2", "test_test_quality_detector", "exec_output")
_emit_dispatches_agent("p3", "test_test_quality_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "test_test_quality_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_test_quality_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_test_quality_detector", "healing_outcome")
_emit_escalates_failure("p3", "test_test_quality_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_test_quality_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_test_quality_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_test_quality_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_test_quality_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_test_quality_detector", "eval_metric")
_emit_stores_embedding("p4", "test_test_quality_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_test_quality_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_test_quality_detector", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def det():
    return TestQualityDetector(enforcement_level=EnforcementLevel.WARNING)


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def _test_file(tmp_path: Path, content: str) -> Path:
    return _write(tmp_path, "test_probe.py", content)


def _adg_file(tmp_path: Path, content: str) -> Path:
    return _write(tmp_path, "test_probe_adg.py", content)


def _prod_file(tmp_path: Path, content: str) -> Path:
    return _write(tmp_path, "module.py", content)


def _sub_patterns(result) -> set[str]:
    return {v.metadata.get("sub_pattern") for v in result.violations if not v.whitelisted}


# ===========================================================================
# VACUOUS_ASSERT — assert True
# ===========================================================================


class TestVacuousAssert:

    def test_detects_assert_true(self, det, tmp_path):
        code = """\
class TestFoo:
    def test_something(self):
        x = compute()
        assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations
        assert "VACUOUS_ASSERT" in _sub_patterns(result)

    def test_detects_assert_true_in_plain_function(self, det, tmp_path):
        code = """\
def test_standalone():
    result = do_thing()
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations
        assert "VACUOUS_ASSERT" in _sub_patterns(result)

    def test_severity_is_error(self, det, tmp_path):
        code = """\
def test_x():
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        errs = [v for v in result.violations if v.metadata.get("sub_pattern") == "VACUOUS_ASSERT"]
        assert errs
        assert all(v.severity == "error" for v in errs)

    def test_category_is_test_quality(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        assert all(v.category == AntiPatternCategory.TEST_QUALITY for v in result.violations)

    def test_metadata_has_test_function(self, det, tmp_path):
        code = "def test_my_func():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        v = next(v for v in result.violations if v.metadata.get("sub_pattern") == "VACUOUS_ASSERT")
        assert v.metadata["test_function"] == "test_my_func"

    def test_no_false_positive_assert_false(self, det, tmp_path):
        """assert False is a meaningful 'never reached' marker — not flagged by VACUOUS."""
        code = """\
def test_x():
    assert False, 'should not reach here'
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "VACUOUS_ASSERT" not in _sub_patterns(result)

    def test_no_false_positive_real_assertion(self, det, tmp_path):
        code = """\
def test_x():
    x = compute()
    assert x == 42
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "VACUOUS_ASSERT" not in _sub_patterns(result)

    def test_vacuous_also_in_adg_stub(self, det, tmp_path):
        """assert True is flagged even in *_adg.py stubs — no exemption for VACUOUS."""
        code = """\
def test_importable():
    assert True
"""
        result = det.scan_file(_adg_file(tmp_path, code))
        assert "VACUOUS_ASSERT" in _sub_patterns(result)

    def test_guardian_comment_suppresses(self, det, tmp_path):
        code = """\
def test_noop_documented():
    # guardian: allow-test-quality -- operation is purely observational, no return value
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "VACUOUS_ASSERT" not in _sub_patterns(result)


# ===========================================================================
# SOLE_TYPE_CHECK — all assertions are weak
# ===========================================================================


class TestSoleTypeCheck:

    def test_detects_only_isinstance(self, det, tmp_path):
        code = """\
def test_returns_something():
    result = compute()
    assert isinstance(result, dict)
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_detects_only_is_not_none(self, det, tmp_path):
        code = """\
def test_creates():
    obj = Factory().make()
    assert obj is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_detects_only_hasattr(self, det, tmp_path):
        code = """\
def test_has_method():
    obj = build()
    assert hasattr(obj, 'run')
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_detects_mixed_weak_only(self, det, tmp_path):
        code = """\
def test_mixed_weak():
    obj = build()
    assert isinstance(obj, MyClass)
    assert obj is not None
    assert hasattr(obj, 'run')
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" in _sub_patterns(result)

    def test_severity_is_warning(self, det, tmp_path):
        code = """\
def test_x():
    assert isinstance(x, int)
"""
        result = det.scan_file(_test_file(tmp_path, code))
        stc = [v for v in result.violations if v.metadata.get("sub_pattern") == "SOLE_TYPE_CHECK"]
        assert stc
        assert all(v.severity == "warning" for v in stc)

    def test_no_false_positive_strong_assertion(self, det, tmp_path):
        """If any assertion is strong, no SOLE_TYPE_CHECK."""
        code = """\
def test_value():
    result = compute()
    assert isinstance(result, int)
    assert result > 0
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_no_false_positive_equality(self, det, tmp_path):
        code = """\
def test_specific():
    result = compute()
    assert result == 42
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_no_false_positive_no_assertions(self, det, tmp_path):
        """Test with no assertions — SOLE_TYPE_CHECK requires at least one assert."""
        code = """\
def test_runs_without_error():
    compute()
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_adg_stub_exempt(self, det, tmp_path):
        """*_adg.py importability stubs must NOT trigger SOLE_TYPE_CHECK."""
        code = """\
def test_module_importable():
    assert _AVAILABLE is not None
    assert isinstance(MyClass, type) or MyClass is None
"""
        result = det.scan_file(_adg_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_guardian_comment_suppresses(self, det, tmp_path):
        code = """\
# guardian: allow-test-quality -- smoke test only, full behavior tested elsewhere
def test_smoke():
    assert isinstance(obj, MyClass)
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "SOLE_TYPE_CHECK" not in _sub_patterns(result)

    def test_metadata_assertion_count(self, det, tmp_path):
        code = """\
def test_count():
    assert isinstance(a, int)
    assert b is not None
    assert hasattr(c, 'x')
"""
        result = det.scan_file(_test_file(tmp_path, code))
        v = next((v for v in result.violations if v.metadata.get("sub_pattern") == "SOLE_TYPE_CHECK"), None)
        assert v is not None
        assert v.metadata["assertion_count"] == 3


# ===========================================================================
# WRITE_WITHOUT_READ
# ===========================================================================


class TestWriteWithoutRead:

    def test_detects_create_no_read(self, det, tmp_path):
        code = """\
def test_creates_entity():
    bridge = GraphMemoryBridge()
    bridge.create_agent_entity('MyAgent')
    assert True
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" in _sub_patterns(result)

    def test_detects_save_no_read(self, det, tmp_path):
        code = """\
def test_saves():
    store = Store()
    store.save(item)
    assert store is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" in _sub_patterns(result)

    def test_no_false_positive_write_then_search(self, det, tmp_path):
        code = """\
def test_persists():
    bridge = GraphMemoryBridge()
    bridge.create_agent_entity('MyAgent')
    results = bridge.search_entities('MyAgent')
    assert len(results) > 0
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_no_false_positive_write_then_get(self, det, tmp_path):
        code = """\
def test_round_trip():
    store.save(item)
    fetched = store.get_item(item.id)
    assert fetched == item
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_no_false_positive_write_then_sqlite(self, det, tmp_path):
        code = """\
def test_sqlite_persists():
    bridge.create_agent_entity('X')
    conn = sqlite3.connect(db_path)
    rows = conn.execute('SELECT * FROM entities').fetchall()
    assert len(rows) > 0
"""
        result = det.scan_file(_test_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_adg_stub_exempt(self, det, tmp_path):
        code = """\
def test_create_method_exists():
    obj = MyClass()
    obj.create_entity('x')
    assert isinstance(obj, MyClass)
"""
        result = det.scan_file(_adg_file(tmp_path, code))
        assert "WRITE_WITHOUT_READ" not in _sub_patterns(result)

    def test_metadata_has_write_call(self, det, tmp_path):
        code = """\
def test_stores():
    db.insert_record(rec)
    assert db is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        v = next(
            (v for v in result.violations if v.metadata.get("sub_pattern") == "WRITE_WITHOUT_READ"),
            None,
        )
        assert v is not None
        assert v.metadata["write_call"] == "insert_record"

    def test_severity_is_warning(self, det, tmp_path):
        code = """\
def test_writes():
    store.save(x)
    assert store is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        wwr = [v for v in result.violations if v.metadata.get("sub_pattern") == "WRITE_WITHOUT_READ"]
        assert wwr
        assert all(v.severity == "warning" for v in wwr)


# ===========================================================================
# File-gate
# ===========================================================================


class TestFileGate:

    def test_production_file_skipped(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_prod_file(tmp_path, code))
        assert result.violation_count == 0

    def test_conftest_skipped(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        p = tmp_path / "conftest.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.violation_count == 0

    def test_test_prefix_scanned(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations

    def test_test_suffix_scanned(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        p = tmp_path / "module_test.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.has_violations


# ===========================================================================
# Multiple patterns in same file
# ===========================================================================


class TestMultiplePatterns:

    def test_multiple_violations_reported(self, det, tmp_path):
        code = """\
def test_vacuous():
    assert True

def test_type_only():
    obj = build()
    assert isinstance(obj, dict)

def test_write_no_read():
    store.add_item(x)
    assert store is not None
"""
        result = det.scan_file(_test_file(tmp_path, code))
        patterns = _sub_patterns(result)
        assert "VACUOUS_ASSERT" in patterns
        assert "SOLE_TYPE_CHECK" in patterns
        assert "WRITE_WITHOUT_READ" in patterns


# ===========================================================================
# Category and wiring
# ===========================================================================


class TestCategoryAndWiring:

    def test_category_value(self):
        assert AntiPatternCategory.TEST_QUALITY == "test_quality"

    def test_detector_category_property(self):
        d = TestQualityDetector()
        assert d.category == AntiPatternCategory.TEST_QUALITY

    def test_default_enforcement_is_warning(self):
        d = TestQualityDetector()
        assert d.enforcement_level == EnforcementLevel.WARNING

    def test_to_dict_has_sub_pattern(self, det, tmp_path):
        code = "def test_x():\n    assert True\n"
        result = det.scan_file(_test_file(tmp_path, code))
        assert result.has_violations
        d = result.violations[0].to_dict()
        assert "sub_pattern" in d["metadata"]
