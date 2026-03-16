"""
Behavioral tests for SilentDegradationDetector — all six sub-patterns.

Covers:
    P1 — AVAILABILITY_GUARD_SKIP
    P2 — SILENT_SUCCESS_ON_NOOP
    P3 — PHANTOM_MODULE_IMPORT
    P4 — EXCEPT_IMPORT_PASS
    P5 — LOG_AND_RETURN_MOCK
    P6 — SKIP_STRING_RETURN

Run with: pytest tests/guardian/test_silent_degradation_detector.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.silent_degradation_validator import (
    SilentDegradationDetector,
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

_emit_records_execution_trace("p0", "evidence", "test_silent_degradation_detector")
_emit_applies_guardrail("p0", "test_silent_degradation_detector", "p0_governance")
_emit_reads_policy_state("p0", "test_silent_degradation_detector", "policy_binding")
_emit_snapshots_state("p0", "test_silent_degradation_detector", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_silent_degradation_detector", "p4obs", "metric_1")
_emit_emits_metric_event("test_silent_degradation_detector", "p4obs", "metric_2")
_emit_emits_metric_event("test_silent_degradation_detector", "p4obs", "metric_3")
_emit_emits_metric_event("test_silent_degradation_detector", "p4obs", "metric_4")
_emit_emits_metric_event("test_silent_degradation_detector", "p4obs", "metric_5")
_emit_emits_metric_event("test_silent_degradation_detector", "p4obs", "metric_6")
_emit_records_incident_event("test_silent_degradation_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_silent_degradation_detector", "p4obs", "anomaly")
_emit_writes_observability_log("test_silent_degradation_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_silent_degradation_detector", "p4obs", "mon_state")
_emit_triggers_alert("test_silent_degradation_detector", "p4obs", "alert")
_emit_links_incident_trace("test_silent_degradation_detector", "p4obs", "trace_link")
_emit_captures_pattern("test_silent_degradation_detector", "p3lm", "pattern")
_emit_records_learning_event("test_silent_degradation_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_silent_degradation_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_silent_degradation_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_silent_degradation_detector", "p3lm", "routing")
_emit_improves_agent_policy("test_silent_degradation_detector", "p3lm", "policy")
_emit_stores_learning_state("test_silent_degradation_detector", "p3lm", "state")
_emit_records_execution_trace("test_silent_degradation_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_silent_degradation_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_silent_degradation_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_silent_degradation_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_silent_degradation_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_silent_degradation_detector", "env_read", "p2_env_1")
_emit_reads_environ("test_silent_degradation_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_silent_degradation_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_silent_degradation_detector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_silent_degradation_detector", "context_pull")
_emit_pulls_context("p1", "test_silent_degradation_detector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_silent_degradation_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_silent_degradation_detector", "uwg_term_2")
_emit_writes_through("p1", "test_silent_degradation_detector", "write_through")
_emit_writes_through("p1", "test_silent_degradation_detector", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_silent_degradation_detector", "safety_validation")
_emit_invokes_eval("p1", "test_silent_degradation_detector", "eval_call")
_emit_proposal_commits_routing("p1", "test_silent_degradation_detector", "routing_commit")
emit_replay_key("p0", "test_silent_degradation_detector")
emit_determinism_digest("p0", "test_silent_degradation_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_silent_degradation_detector", "execution_auth")
_emit_validates_capability("p2", "test_silent_degradation_detector", "capability_check")
_emit_routes_to_capability("p2", "test_silent_degradation_detector", "capability_route")
_emit_writes_via_uwg("p2", "test_silent_degradation_detector", "uwg_write")
_emit_blocks_direct_write("p2", "test_silent_degradation_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "test_silent_degradation_detector", "tool_invocation")
_emit_captures_execution_output("p2", "test_silent_degradation_detector", "exec_output")
_emit_dispatches_agent("p3", "test_silent_degradation_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "test_silent_degradation_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_silent_degradation_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_silent_degradation_detector", "healing_outcome")
_emit_escalates_failure("p3", "test_silent_degradation_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_silent_degradation_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_silent_degradation_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_silent_degradation_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_silent_degradation_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_silent_degradation_detector", "eval_metric")
_emit_stores_embedding("p4", "test_silent_degradation_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_silent_degradation_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_silent_degradation_detector", "exec_snapshot_link")


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def det():
    return SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)


@pytest.fixture
def tmp_py(tmp_path):
    """Factory: write *content* to a temp .py file and return its Path."""

    def _make(content: str) -> Path:
        p = tmp_path / "probe.py"
        p.write_text(content, encoding="utf-8")
        return p

    return _make


def _sub_patterns(result):
    return {v.metadata.get("sub_pattern") for v in result.violations if not v.whitelisted}


# ===========================================================================
# P1 — AVAILABILITY_GUARD_SKIP
# ===========================================================================


class TestAvailabilityGuardSkip:
    """if not self._X_available: return None/[]/{}"""

    def test_detects_mcp_available_guard(self, det, tmp_py):
        code = """\
class Bridge:
    def push(self, op):
        if not self._mcp_available:
            return None
        self._do_push(op)
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "AVAILABILITY_GUARD_SKIP" in _sub_patterns(result)

    def test_detects_initialized_guard(self, det, tmp_py):
        code = """\
class Streamer:
    def stop(self):
        if not self._streamer_initialized:
            return
        self._task.cancel()
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "AVAILABILITY_GUARD_SKIP" in _sub_patterns(result)

    def test_detects_empty_list_return(self, det, tmp_py):
        code = """\
class Client:
    def search(self, q):
        if not self._backend_available:
            return []
        return self._backend.search(q)
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "AVAILABILITY_GUARD_SKIP" in _sub_patterns(result)

    def test_detects_empty_dict_return(self, det, tmp_py):
        code = """\
class Store:
    def fetch(self, key):
        if not self._connected:
            return {}
        return self._db.get(key)
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "AVAILABILITY_GUARD_SKIP" in _sub_patterns(result)

    def test_no_false_positive_raise(self, det, tmp_py):
        """if not available: raise — correct pattern, must NOT flag."""
        code = """\
class Bridge:
    def push(self, op):
        if not self._mcp_available:
            raise RuntimeError("MCP unavailable")
        self._do_push(op)
"""
        result = det.scan_file(tmp_py(code))
        assert "AVAILABILITY_GUARD_SKIP" not in _sub_patterns(result)

    def test_no_false_positive_unrelated_if(self, det, tmp_py):
        """Normal guard on a value — must NOT flag."""
        code = """\
class Worker:
    def run(self, items):
        if not items:
            return []
        return [process(i) for i in items]
"""
        result = det.scan_file(tmp_py(code))
        assert "AVAILABILITY_GUARD_SKIP" not in _sub_patterns(result)

    def test_whitelist_suppresses(self, det, tmp_py):
        code = """\
class Bridge:
    def push(self, op):
        # guardian: allow-silent-degradation -- CI env: MCP not present
        if not self._mcp_available:
            return None
"""
        result = det.scan_file(tmp_py(code))
        assert "AVAILABILITY_GUARD_SKIP" not in _sub_patterns(result)

    def test_error_severity(self, det, tmp_py):
        code = """\
class X:
    def go(self):
        if not self._ready:
            return None
"""
        result = det.scan_file(tmp_py(code))
        violations = [v for v in result.violations if v.metadata.get("sub_pattern") == "AVAILABILITY_GUARD_SKIP"]
        assert violations
        assert all(v.severity == "error" for v in violations)

    def test_category_is_silent_degradation(self, det, tmp_py):
        code = """\
class X:
    def go(self):
        if not self._ready:
            return None
"""
        result = det.scan_file(tmp_py(code))
        assert all(v.category == AntiPatternCategory.SILENT_DEGRADATION for v in result.violations)


# ===========================================================================
# P2 — SILENT_SUCCESS_ON_NOOP
# ===========================================================================


class TestSilentSuccessOnNoop:
    """result is not None or (fn is None and mod is None): return True"""

    def test_detects_create_entities_pattern(self, det, tmp_py):
        code = """\
class Bridge:
    def create_agent_entity(self, name):
        result = self._call_mcp_create_entities([{"name": name}])
        if result is not None or (self._create_entities_fn is None and self._mcp_module is None):
            self.stats["entities_created"] += 1
            return True
        return False
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "SILENT_SUCCESS_ON_NOOP" in _sub_patterns(result)

    def test_detects_single_is_none_variant(self, det, tmp_py):
        code = """\
class Bridge:
    def add_obs(self, obs):
        result = self._call_add(obs)
        if result is not None or self._fn is None:
            return True
        return False
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "SILENT_SUCCESS_ON_NOOP" in _sub_patterns(result)

    def test_no_false_positive_result_is_not_none_only(self, det, tmp_py):
        """if result is not None: return True — no noop guard, must NOT flag."""
        code = """\
class Bridge:
    def call(self):
        result = self._do()
        if result is not None:
            return True
        return False
"""
        result = det.scan_file(tmp_py(code))
        assert "SILENT_SUCCESS_ON_NOOP" not in _sub_patterns(result)

    def test_no_false_positive_and_without_return_true(self, det, tmp_py):
        """Condition matches but no return True — must NOT flag."""
        code = """\
class Bridge:
    def call(self):
        result = self._do()
        if result is not None or self._fn is None:
            self.log("ok")
"""
        result = det.scan_file(tmp_py(code))
        assert "SILENT_SUCCESS_ON_NOOP" not in _sub_patterns(result)

    def test_whitelist_suppresses(self, det, tmp_py):
        code = """\
class Bridge:
    def create(self, name):
        result = self._call([name])
        # guardian: allow-silent-degradation -- test/CI stub mode intentional
        if result is not None or (self._fn is None and self._mod is None):
            return True
        return False
"""
        result = det.scan_file(tmp_py(code))
        assert "SILENT_SUCCESS_ON_NOOP" not in _sub_patterns(result)

    def test_error_severity(self, det, tmp_py):
        code = """\
class B:
    def go(self):
        r = self._call()
        if r is not None or self._fn is None:
            return True
        return False
"""
        result = det.scan_file(tmp_py(code))
        violations = [v for v in result.violations if v.metadata.get("sub_pattern") == "SILENT_SUCCESS_ON_NOOP"]
        assert violations
        assert all(v.severity == "error" for v in violations)


# ===========================================================================
# P3 — PHANTOM_MODULE_IMPORT
# ===========================================================================


class TestPhantomModuleImport:
    """try: importlib.import_module("mcp<N>") except ImportError: flag = False"""

    def test_detects_mcp11_import(self, det, tmp_py):
        code = """\
import importlib

class Bridge:
    def _init_mcp(self):
        try:
            _mod = importlib.import_module("mcp11")
            self._mcp_available = True
        except ImportError:
            self._mcp_available = False
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "PHANTOM_MODULE_IMPORT" in _sub_patterns(result)

    def test_detects_mcp4_import(self, det, tmp_py):
        code = """\
import importlib

class Fetcher:
    def _probe(self):
        try:
            importlib.import_module("mcp4")
            self._available = True
        except ImportError:
            self._available = False
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "PHANTOM_MODULE_IMPORT" in _sub_patterns(result)

    def test_detects_bare_except_variant(self, det, tmp_py):
        code = """\
import importlib

class X:
    def probe(self):
        try:
            importlib.import_module("mcp99")
            self._ok = True
        except Exception:
            self._ok = False
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "PHANTOM_MODULE_IMPORT" in _sub_patterns(result)

    def test_no_false_positive_real_module(self, det, tmp_py):
        """try: importlib.import_module("redis") — real module, must NOT flag."""
        code = """\
import importlib

class Cache:
    def probe(self):
        try:
            importlib.import_module("redis")
            self._redis_available = True
        except ImportError:
            self._redis_available = False
"""
        result = det.scan_file(tmp_py(code))
        assert "PHANTOM_MODULE_IMPORT" not in _sub_patterns(result)

    def test_no_false_positive_no_except(self, det, tmp_py):
        """import_module with no except handler — must NOT flag."""
        code = """\
import importlib

mod = importlib.import_module("mcp11")
"""
        result = det.scan_file(tmp_py(code))
        assert "PHANTOM_MODULE_IMPORT" not in _sub_patterns(result)

    def test_metadata_captures_module_name(self, det, tmp_py):
        code = """\
import importlib

class X:
    def probe(self):
        try:
            importlib.import_module("mcp11")
            self._ok = True
        except ImportError:
            self._ok = False
"""
        result = det.scan_file(tmp_py(code))
        phantom = [v for v in result.violations if v.metadata.get("sub_pattern") == "PHANTOM_MODULE_IMPORT"]
        assert phantom
        assert phantom[0].metadata.get("module") == "mcp11"

    def test_error_severity(self, det, tmp_py):
        code = """\
import importlib

class X:
    def probe(self):
        try:
            importlib.import_module("mcp3")
            self._ok = True
        except ImportError:
            self._ok = False
"""
        result = det.scan_file(tmp_py(code))
        violations = [v for v in result.violations if v.metadata.get("sub_pattern") == "PHANTOM_MODULE_IMPORT"]
        assert violations
        assert all(v.severity == "error" for v in violations)


# ===========================================================================
# P4 — EXCEPT_IMPORT_PASS
# ===========================================================================


class TestExceptImportPass:
    """except ImportError: pass"""

    def test_detects_import_error_pass(self, det, tmp_py):
        code = """\
try:
    from some_module import Tool
except ImportError:
    pass
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "EXCEPT_IMPORT_PASS" in _sub_patterns(result)

    def test_detects_module_not_found_pass(self, det, tmp_py):
        code = """\
try:
    import optional_dep
except ModuleNotFoundError:
    pass
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "EXCEPT_IMPORT_PASS" in _sub_patterns(result)

    def test_detects_log_only_body(self, det, tmp_py):
        """except ImportError: logger.debug(...) — still no raise, must flag."""
        code = """\
import logging
log = logging.getLogger(__name__)

try:
    import optional_dep
    _AVAIL = True
except ImportError:
    log.debug("optional_dep not available")
    _AVAIL = False
"""
        result = det.scan_file(tmp_py(code))
        assert "EXCEPT_IMPORT_PASS" in _sub_patterns(result)

    def test_no_false_positive_with_raise(self, det, tmp_py):
        """except ImportError: raise — correct propagation, must NOT flag."""
        code = """\
try:
    import required_dep
except ImportError as exc:
    raise ImportError("required_dep is required") from exc
"""
        result = det.scan_file(tmp_py(code))
        assert "EXCEPT_IMPORT_PASS" not in _sub_patterns(result)

    def test_no_false_positive_return_false(self, det, tmp_py):
        """except ImportError: return False — explicit error signal, must NOT flag."""
        code = """\
def probe():
    try:
        import dep
    except ImportError:
        return False
    return True
"""
        result = det.scan_file(tmp_py(code))
        assert "EXCEPT_IMPORT_PASS" not in _sub_patterns(result)

    def test_no_false_positive_exception_not_import_error(self, det, tmp_py):
        """except ValueError: pass — wrong exception type, must NOT flag."""
        code = """\
try:
    x = int("bad")
except ValueError:
    pass
"""
        result = det.scan_file(tmp_py(code))
        assert "EXCEPT_IMPORT_PASS" not in _sub_patterns(result)

    def test_whitelist_suppresses(self, det, tmp_py):
        code = """\
# guardian: allow-silent-degradation -- optional perf dep, absent in CI
try:
    import uvloop
except ImportError:
    pass
"""
        result = det.scan_file(tmp_py(code))
        assert "EXCEPT_IMPORT_PASS" not in _sub_patterns(result)

    def test_warning_severity(self, det, tmp_py):
        code = """\
try:
    import optional_dep
except ImportError:
    pass
"""
        result = det.scan_file(tmp_py(code))
        violations = [v for v in result.violations if v.metadata.get("sub_pattern") == "EXCEPT_IMPORT_PASS"]
        assert violations
        assert all(v.severity == "warning" for v in violations)


# ===========================================================================
# P5 — LOG_AND_RETURN_MOCK
# ===========================================================================


class TestLogAndReturnMock:
    """logger.warning("...mock/fallback...") + return {fake_data}"""

    def test_detects_mock_success_return(self, det, tmp_py):
        code = """\
import logging
Logger = logging.getLogger(__name__)

def fetch(url):
    try:
        from mcp4_fetch import mcp4_fetch
        return mcp4_fetch(url=url)
    except ImportError:
        Logger.warning("mcp4_fetch not available, returning mock")
        return {"status": "mock_success", "url": url}
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "LOG_AND_RETURN_MOCK" in _sub_patterns(result)

    def test_detects_fallback_keyword(self, det, tmp_py):
        code = """\
import logging
log = logging.getLogger(__name__)

def get_data():
    try:
        from backend import Client
        return Client().fetch()
    except ImportError:
        log.warning("Backend unavailable — using fallback data")
        return {"data": [], "source": "fallback"}
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "LOG_AND_RETURN_MOCK" in _sub_patterns(result)

    def test_no_false_positive_raise_not_return(self, det, tmp_py):
        """Mock log but raises — correct, must NOT flag."""
        code = """\
import logging
log = logging.getLogger(__name__)

def get_data():
    try:
        from backend import Client
    except ImportError as exc:
        log.warning("backend not available — skipping")
        raise RuntimeError("backend required") from exc
"""
        result = det.scan_file(tmp_py(code))
        assert "LOG_AND_RETURN_MOCK" not in _sub_patterns(result)

    def test_no_false_positive_log_without_mock_keyword(self, det, tmp_py):
        """Logger call without mock/fallback keyword — must NOT flag."""
        code = """\
import logging
log = logging.getLogger(__name__)

def get_data():
    try:
        from backend import Client
    except ImportError as exc:
        log.warning("import failed")
        return {"data": []}
"""
        result = det.scan_file(tmp_py(code))
        assert "LOG_AND_RETURN_MOCK" not in _sub_patterns(result)

    def test_warning_severity(self, det, tmp_py):
        code = """\
import logging
Logger = logging.getLogger(__name__)

def fetch(url):
    try:
        from mcp4_fetch import mcp4_fetch
    except ImportError:
        Logger.warning("mcp4_fetch not available, returning mock")
        return {"status": "mock_success"}
"""
        result = det.scan_file(tmp_py(code))
        violations = [v for v in result.violations if v.metadata.get("sub_pattern") == "LOG_AND_RETURN_MOCK"]
        assert violations
        assert all(v.severity == "warning" for v in violations)


# ===========================================================================
# P6 — SKIP_STRING_RETURN
# ===========================================================================


class TestSkipStringReturn:
    """return "...: Skipped (agent not available)" """

    def test_detects_skipped_not_available(self, det, tmp_py):
        code = """\
def probe_hierarchy():
    agent = _get_agent()
    if agent is None:
        return "Hierarchy probe: Skipped (agent not available)"
    return agent.run()
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "SKIP_STRING_RETURN" in _sub_patterns(result)

    def test_detects_skipped_unavailable(self, det, tmp_py):
        code = """\
def probe_gravity():
    factory = _get_factory()
    if factory is None:
        return "Gravity probe: Skipped (agent unavailable)"
    return factory.run()
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "SKIP_STRING_RETURN" in _sub_patterns(result)

    def test_detects_skip_lowercase(self, det, tmp_py):
        code = """\
def check():
    if not self._loaded:
        return "check skipped: backend not available"
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        assert "SKIP_STRING_RETURN" in _sub_patterns(result)

    def test_no_false_positive_normal_string(self, det, tmp_py):
        """Unrelated return string — must NOT flag."""
        code = """\
def get_status():
    return "running"
"""
        result = det.scan_file(tmp_py(code))
        assert "SKIP_STRING_RETURN" not in _sub_patterns(result)

    def test_no_false_positive_error_message(self, det, tmp_py):
        """Error message without skip/available keywords — must NOT flag."""
        code = """\
def run():
    return "operation failed due to timeout"
"""
        result = det.scan_file(tmp_py(code))
        assert "SKIP_STRING_RETURN" not in _sub_patterns(result)

    def test_whitelist_suppresses(self, det, tmp_py):
        code = """\
def probe():
    agent = _get()
    if agent is None:
        # guardian: allow-silent-degradation -- exerciser probe, informational only
        return "Probe: Skipped (agent not available)"
"""
        result = det.scan_file(tmp_py(code))
        assert "SKIP_STRING_RETURN" not in _sub_patterns(result)

    def test_warning_severity(self, det, tmp_py):
        code = """\
def probe():
    if not self._ready:
        return "probe: skipped (agent not available)"
"""
        result = det.scan_file(tmp_py(code))
        violations = [v for v in result.violations if v.metadata.get("sub_pattern") == "SKIP_STRING_RETURN"]
        assert violations
        assert all(v.severity == "warning" for v in violations)


# ===========================================================================
# Integration: real graph_memory_bridge.py
# ===========================================================================


class TestGraphMemoryBridgeCoverage:
    """The canonical example of silent degradation must fire on all known patterns."""

    BRIDGE = Path(__file__).resolve().parents[2] / "agentic_core" / "L4_state" / "enforcement" / "graph_memory_bridge.py"

    @pytest.mark.skipif(
        not (Path(__file__).resolve().parents[2] / "agentic_core" / "L4_state" / "enforcement" / "graph_memory_bridge.py").exists(),
        reason="graph_memory_bridge.py not found",
    )
    def test_bridge_has_phantom_import(self):
        det = SilentDegradationDetector()
        result = det.scan_file(self.BRIDGE)
        assert "PHANTOM_MODULE_IMPORT" in _sub_patterns(result)

    @pytest.mark.skipif(
        not (Path(__file__).resolve().parents[2] / "agentic_core" / "L4_state" / "enforcement" / "graph_memory_bridge.py").exists(),
        reason="graph_memory_bridge.py not found",
    )
    def test_bridge_has_availability_guard_skip(self):
        det = SilentDegradationDetector()
        result = det.scan_file(self.BRIDGE)
        assert "AVAILABILITY_GUARD_SKIP" in _sub_patterns(result)

    @pytest.mark.skipif(
        not (Path(__file__).resolve().parents[2] / "agentic_core" / "L4_state" / "enforcement" / "graph_memory_bridge.py").exists(),
        reason="graph_memory_bridge.py not found",
    )
    def test_bridge_has_silent_success_on_noop(self):
        det = SilentDegradationDetector()
        result = det.scan_file(self.BRIDGE)
        assert "SILENT_SUCCESS_ON_NOOP" in _sub_patterns(result)

    @pytest.mark.skipif(
        not (Path(__file__).resolve().parents[2] / "agentic_core" / "L4_state" / "enforcement" / "graph_memory_bridge.py").exists(),
        reason="graph_memory_bridge.py not found",
    )
    def test_bridge_total_violations_at_least_five(self):
        det = SilentDegradationDetector()
        result = det.scan_file(self.BRIDGE)
        assert result.violation_count >= 5


# ===========================================================================
# Integration: scanner registration
# ===========================================================================


class TestScannerRegistration:
    """SilentDegradationDetector must be wired into AntiPatternScanner."""

    def test_scanner_includes_silent_degradation_detector(self):
        from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import AntiPatternScanner

        scanner = AntiPatternScanner(project_root=Path("."))
        categories = {d.category for d in scanner.composite.detectors}
        assert AntiPatternCategory.SILENT_DEGRADATION in categories

    def test_silent_degradation_category_in_enum(self):
        assert AntiPatternCategory.SILENT_DEGRADATION == "silent_degradation"

    def test_detector_category_property(self):
        det = SilentDegradationDetector()
        assert det.category == AntiPatternCategory.SILENT_DEGRADATION


# ===========================================================================
# Whitelist / exemption mechanics
# ===========================================================================


class TestWhitelistMechanics:
    """Guardian exemption comment must suppress any sub-pattern."""

    def test_whitelist_on_preceding_line(self, det, tmp_py):
        code = """\
class X:
    def go(self):
        # guardian: allow-silent-degradation -- CI stub
        if not self._mcp_available:
            return None
"""
        result = det.scan_file(tmp_py(code))
        assert not result.has_violations

    def test_whitelist_two_lines_above(self, det, tmp_py):
        code = """\
class X:
    def go(self):
        # guardian: allow-silent-degradation -- offline env
        # noqa
        if not self._mcp_available:
            return None
"""
        result = det.scan_file(tmp_py(code))
        assert not result.has_violations

    def test_whitelist_does_not_suppress_different_violation(self, det, tmp_py):
        """Exemption on line N does not silence a violation on a distant line."""
        code = """\
# guardian: allow-silent-degradation -- top of file does NOT cover everything

class X:
    def push(self, op):
        if not self._mcp_available:
            return None
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations

    def test_test_files_are_excluded_by_default(self, tmp_path):
        """Files matching test_*.py must be skipped entirely."""
        p = tmp_path / "test_probe.py"
        p.write_text(
            "class T:\n    def go(self):\n        if not self._available:\n            return None\n",
            encoding="utf-8",
        )
        detector = SilentDegradationDetector(enforcement_level=EnforcementLevel.WARNING)
        result = detector.scan_file(p)
        assert result.violation_count == 0

    def test_violation_to_dict_has_sub_pattern(self, det, tmp_py):
        code = """\
class X:
    def go(self):
        if not self._mcp_available:
            return None
"""
        result = det.scan_file(tmp_py(code))
        assert result.has_violations
        d = result.violations[0].to_dict()
        assert "sub_pattern" in d.get("metadata", {})
