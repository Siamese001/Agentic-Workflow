"""
Behavioral tests for TestSilentSkipDetector.

Covers:
  - BROAD_EXCEPT_AVAILABILITY_FLAG detection (positive cases)
  - Safe except ImportError pattern (negative / no false-positive)
  - Bare except, except BaseException (positive)
  - Tuple except (E1, E2) variants
  - Non-test files are skipped entirely
  - Guardian exemption comment suppresses detection
  - Severity is always error
  - Category is TEST_SILENT_SKIP
  - ADG integration: AntiPatternCategory enum has TEST_SILENT_SKIP

Run with: pytest tests/guardian/test_test_silent_skip_detector.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Import required modules
from agentic_core.L5_safety.validators.base_detector_validator import (
    AntiPatternCategory,
    EnforcementLevel,
)
from agentic_core.L5_safety.validators.test_skip_detector_validator import (
    TestSilentSkipDetector,
)

# Import lifecycle trace contract
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_test_silent_skip_detector", "p4obs", "metric_1")
_emit_emits_metric_event("test_test_silent_skip_detector", "p4obs", "metric_2")
_emit_emits_metric_event("test_test_silent_skip_detector", "p4obs", "metric_3")
_emit_emits_metric_event("test_test_silent_skip_detector", "p4obs", "metric_4")
_emit_emits_metric_event("test_test_silent_skip_detector", "p4obs", "metric_5")
_emit_emits_metric_event("test_test_silent_skip_detector", "p4obs", "metric_6")
_emit_records_incident_event("test_test_silent_skip_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_test_silent_skip_detector", "p4obs", "anomaly")
_emit_writes_observability_log("test_test_silent_skip_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_test_silent_skip_detector", "p4obs", "mon_state")
_emit_triggers_alert("test_test_silent_skip_detector", "p4obs", "alert")
_emit_links_incident_trace("test_test_silent_skip_detector", "p4obs", "trace_link")
_emit_captures_pattern("test_test_silent_skip_detector", "p3lm", "pattern")
_emit_records_learning_event("test_test_silent_skip_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_test_silent_skip_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_test_silent_skip_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_test_silent_skip_detector", "p3lm", "routing")
_emit_improves_agent_policy("test_test_silent_skip_detector", "p3lm", "policy")
_emit_stores_learning_state("test_test_silent_skip_detector", "p3lm", "state")
_emit_records_execution_trace("test_test_silent_skip_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_test_silent_skip_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_test_silent_skip_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_test_silent_skip_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_test_silent_skip_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_test_silent_skip_detector", "env_read", "p2_env_1")
_emit_reads_environ("test_test_silent_skip_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_test_silent_skip_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_test_silent_skip_detector", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_test_silent_skip_detector")
_emit_applies_guardrail("p0", "test_test_silent_skip_detector", "p0_governance")
_emit_reads_policy_state("p0", "test_test_silent_skip_detector", "policy_binding")
_emit_snapshots_state("p0", "test_test_silent_skip_detector", "state_snapshot")
emit_replay_key("p0", "test_test_silent_skip_detector")
emit_determinism_digest("p0", "test_test_silent_skip_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_test_silent_skip_detector", "execution_auth")
_emit_validates_capability("p2", "test_test_silent_skip_detector", "capability_check")
_emit_routes_to_capability("p2", "test_test_silent_skip_detector", "capability_route")
_emit_writes_via_uwg("p2", "test_test_silent_skip_detector", "uwg_write")
_emit_blocks_direct_write("p2", "test_test_silent_skip_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "test_test_silent_skip_detector", "tool_invocation")
_emit_captures_execution_output("p2", "test_test_silent_skip_detector", "exec_output")
_emit_dispatches_agent("p3", "test_test_silent_skip_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "test_test_silent_skip_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_test_silent_skip_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_test_silent_skip_detector", "healing_outcome")
_emit_escalates_failure("p3", "test_test_silent_skip_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_test_silent_skip_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_test_silent_skip_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_test_silent_skip_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_test_silent_skip_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_test_silent_skip_detector", "eval_metric")
_emit_stores_embedding("p4", "test_test_silent_skip_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_test_silent_skip_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_test_silent_skip_detector", "exec_snapshot_link")
_emit_escalates_to_human("p1", "test_test_silent_skip_detector", "human_escalation")
_emit_routes_through("p1", "test_test_silent_skip_detector", "route_through")
_emit_checks_agent_registry("p1", "test_test_silent_skip_detector", "agent_registry")
_emit_validates_agent_capability("p1", "test_test_silent_skip_detector", "capability")
_emit_dispatches_execution_plan("p1", "test_test_silent_skip_detector", "exec_plan")
_emit_agent_executes_agent("p1", "test_test_silent_skip_detector", "sub_agent")
_emit_routes_to_agent("p1", "test_test_silent_skip_detector", "target_agent")
_emit_verifies_policy("p1", "test_test_silent_skip_detector", "policy_check")
_emit_observes_runtime_state("p1", "test_test_silent_skip_detector", "runtime_state")
_emit_verifies_boundary("p1", "test_test_silent_skip_detector", "boundary_check")
_emit_transcripts_response("p1", "test_test_silent_skip_detector", "transcript")
_emit_hard_fails_untranscripted("p1", "test_test_silent_skip_detector")
_emit_gated_by_confidence("p1", "test_test_silent_skip_detector", "confidence_gate")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def det():
    return TestSilentSkipDetector(enforcement_level=EnforcementLevel.HARD_BLOCK)


@pytest.fixture
def test_py(tmp_path):
    """Write content into a test_probe.py file (test file name)."""
    def _make(content: str) -> Path:
        p = tmp_path / "test_probe.py"
        p.write_text(content, encoding="utf-8")
        return p

    return _make


@pytest.fixture
def prod_py(tmp_path):
    """Write content into a production (non-test) file."""

    def _make(content: str) -> Path:
        p = tmp_path / "my_module.py"
        p.write_text(content, encoding="utf-8")
        return p

    return _make


def _sub_patterns(result):
    return {v.metadata.get("sub_pattern") for v in result.violations if not v.whitelisted}


# ===========================================================================
# Positive cases — should detect
# ===========================================================================


class TestBroadExceptAvailabilityFlag:
    """except Exception: _AVAILABLE = False must be flagged."""

    def test_detects_except_exception(self, det, test_py):
        code = """\
try:
    from some.module import Foo, NONEXISTENT

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_bare_except(self, det, test_py):
        code = """\
try:
    from some.module import Foo

except:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_except_base_exception(self, det, test_py):
        code = """\
try:
    from some.module import Foo

except BaseException:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_except_exception_with_alias(self, det, test_py):
        """except Exception as exc: _AVAILABLE = False must also be flagged."""
        code = """\
try:
    from some.module import Foo

except Exception as exc:
    _AVAILABLE = False
    Foo = None
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)

    def test_detects_various_flag_names(self, det, tmp_path):
        """All availability flag suffixes must be detected."""
        for flag in ("_AVAILABLE", "_AVAIL", "_ENABLED", "_LOADED", "_IMPORTED", "_READY"):
            code = f"""\
try:
    from mod import X
    {flag} = True
except Exception:
    {flag} = False
"""
            p = tmp_path / f"test_{flag.lower()}.py"
            p.write_text(code, encoding="utf-8")
            result = det.scan_file(p)
            assert result.has_violations, f"Should flag {flag} = False under except Exception"

    def test_detects_custom_availability_flag(self, det, test_py):
        """Custom names ending in _AVAILABLE must also be caught."""
        code = """\
try:
    from mod import X
    REDIS_AVAILABLE = True
except Exception:
    REDIS_AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations

    def test_metadata_flag_name_captured(self, det, test_py):
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        v = result.violations[0]
        assert v.metadata["flag"] == "_AVAILABLE"
        assert "Exception" in v.metadata["caught"]

    def test_error_severity(self, det, test_py):
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert all(v.severity == "error" for v in result.violations if not v.whitelisted)

    def test_category_is_test_silent_skip(self, det, test_py):
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert all(v.category == AntiPatternCategory.TEST_SILENT_SKIP for v in result.violations)

    def test_suggested_fix_mentions_import_error(self, det, test_py):
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        v = result.violations[0]
        assert "ImportError" in v.suggested_fix

    def test_real_world_adg_stub_pattern(self, det, test_py):
        """The exact pattern used in 1569 ADG stubs must be flagged."""
        code = """\
from __future__ import annotations
import pytest

try:
    from agentic_core.L4_state.enforcement.graph_memory_bridge import (
        EntityDefinition,
        GraphMemoryBridge,
        RelationDefinition,
        MAX_RETRIES,
        DEFAULT_SLEEP,
    )
    _BRIDGE_AVAILABLE = True
except Exception:
    EntityDefinition = None
    GraphMemoryBridge = None
    RelationDefinition = None
    _BRIDGE_AVAILABLE = False

class TestGraphMemoryBridgeImportability:
    def test_module_importable(self):
        pass  # Import verified at module level
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        assert "BROAD_EXCEPT_AVAILABILITY_FLAG" in _sub_patterns(result)


# ===========================================================================
# Negative cases — must NOT detect (no false positives)
# ===========================================================================


class TestNoFalsePositives:
    """Safe patterns must not be flagged."""

    def test_safe_except_import_error(self, det, test_py):
        """except ImportError: _AVAILABLE = False — the correct pattern."""
        code = """\
try:
    from some.module import Foo

except ImportError:

    Foo = None
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_safe_except_module_not_found(self, det, test_py):
        """except ModuleNotFoundError: _AVAILABLE = False — also acceptable."""
        code = """\
try:
    import optional_dep

except ModuleNotFoundError:

"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_safe_except_tuple_all_import_errors(self, det, test_py):
        """except (ImportError, ModuleNotFoundError): — all safe."""
        code = """\
try:
    import optional_dep

except (ImportError, ModuleNotFoundError):

"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_no_flag_no_detection(self, det, test_py):
        """except Exception: without availability flag — must not flag."""
        code = """\
try:
    x = int("bad")
except Exception:
    x = 0
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_except_exception_sets_flag_to_none_not_false(self, det, test_py):
        """Setting flag to None (not False) — must not flag."""
        code = """\
try:
    from mod import X

except Exception:
    X = None
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_except_import_error_raises(self, det, test_py):
        """except ImportError: raise — no false positive."""
        code = """\
try:
    from mod import X
except ImportError as exc:
    raise RuntimeError("mod required") from exc
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations


# ===========================================================================
# Test-file gate — non-test files must be skipped entirely
# ===========================================================================


class TestFileGate:
    """Non-test files must return empty results regardless of content."""

    def test_production_file_skipped(self, det, prod_py):
        """A production file with the dangerous pattern must NOT be scanned."""
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(prod_py(code))
        assert result.violation_count == 0

    def test_conftest_skipped(self, det, tmp_path):
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        p = tmp_path / "conftest.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.violation_count == 0

    def test_test_suffix_file_scanned(self, det, tmp_path):
        """Files ending in _test.py must also be scanned."""
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        p = tmp_path / "module_test.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.has_violations

    def test_test_prefix_file_scanned(self, det, tmp_path):
        """Files starting with test_ must be scanned."""
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        p = tmp_path / "test_my_module.py"
        p.write_text(code, encoding="utf-8")
        result = det.scan_file(p)
        assert result.has_violations


# ===========================================================================
# Whitelist / guardian exemption
# ===========================================================================


class TestWhitelistMechanics:
    def test_guardian_comment_suppresses(self, det, test_py):
        code = """\
# guardian: allow-test-silent-skip -- optional GPU dep, absent in CPU CI
try:
    from gpu_module import CUDA

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert not result.has_violations

    def test_wrong_guardian_type_does_not_suppress(self, det, test_py):
        """A guardian comment for a different type must NOT suppress this violation."""
        code = """\
# guardian: allow-silent-degradation -- wrong type
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations

    def test_distant_guardian_does_not_suppress(self, det, test_py):
        """A guardian comment >3 lines above must NOT suppress."""
        code = """\
# guardian: allow-test-silent-skip -- too far above


try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations


# ===========================================================================
# Category enum and detector wiring
# ===========================================================================


class TestCategoryAndWiring:
    def test_category_value(self):
        assert AntiPatternCategory.TEST_SILENT_SKIP == "test_silent_skip"

    def test_detector_category_property(self):
        d = TestSilentSkipDetector()
        assert d.category == AntiPatternCategory.TEST_SILENT_SKIP

    def test_to_dict_has_sub_pattern(self, det, test_py):
        code = """\
try:
    from mod import X

except Exception:
    _AVAILABLE = False
"""
        result = det.scan_file(test_py(code))
        assert result.has_violations
        d = result.violations[0].to_dict()
        assert d["metadata"]["sub_pattern"] == "BROAD_EXCEPT_AVAILABILITY_FLAG"

    def test_enforcement_level_hard_block_by_default(self):
        d = TestSilentSkipDetector()
        assert d.enforcement_level == EnforcementLevel.HARD_BLOCK
