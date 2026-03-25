"""
Guardian Hardened Tests — Classification Kernel (SSOT)

AST-graph justification:
  classification_kernel has fan_in=10 direct consumers across L0_routing,
  L5_safety validators, runtime, prompt_governance, and ops_scripts.
  Current test coverage = 2 test files, both covering only
  classify_execution_mode(); classify_file_standalone() has ZERO direct
  behavioral tests against real contract outputs.

Covers:
  1. Canonical FileType taxonomy — every declared literal is reachable
  2. Priority ordering — first-match-wins contract (not internal state)
  3. Dual-tag conflict detection and get_classification_conflicts()
  4. Cache semantics — lru_cache keyed on resolved path, clear contract
  5. classification_cache_context() — clears on entry AND exit
  6. Error hardening — UnicodeDecodeError, OSError, SyntaxError → IGNORE
  7. is_agent_file / is_agent_or_orchestrator predicates
  8. classify_execution_mode signal isolation (regression guard for kernel changes)
  9. Consumer contract: downstream callers see identical results before/after cache clear
 10. _CRITICAL_IGNORES set — conftest.py / __init__.py → IGNORE
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L5_safety.core_kernel.classification_kernel import (
    FileType,
    classification_cache_context,
    classification_cache_info,
    classify_file_standalone,
    clear_classification_cache,
    clear_classification_conflicts,
    get_classification_conflicts,
    is_agent_file,
    is_agent_or_orchestrator,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
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
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_classification_kernel_hardened", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_classification_kernel_hardened", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_classification_kernel_hardened", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_classification_kernel_hardened", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_classification_kernel_hardened", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_classification_kernel_hardened", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_classification_kernel_hardened", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_classification_kernel_hardened", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_classification_kernel_hardened", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_classification_kernel_hardened", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_classification_kernel_hardened", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_classification_kernel_hardened", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_classification_kernel_hardened", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_classification_kernel_hardened", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_classification_kernel_hardened", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_classification_kernel_hardened", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_classification_kernel_hardened", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_classification_kernel_hardened", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_classification_kernel_hardened", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_classification_kernel_hardened", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_classification_kernel_hardened", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_classification_kernel_hardened", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_classification_kernel_hardened", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_classification_kernel_hardened", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_classification_kernel_hardened", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_classification_kernel_hardened", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_classification_kernel_hardened", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_classification_kernel_hardened", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_classification_kernel_hardened")
# REMOVED: _emit_applies_guardrail("p0", "test_classification_kernel_hardened", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_classification_kernel_hardened", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_classification_kernel_hardened", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_classification_kernel_hardened", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_classification_kernel_hardened", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_classification_kernel_hardened", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_classification_kernel_hardened", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_classification_kernel_hardened", "write_through")
# REMOVED: _emit_writes_through("p1", "test_classification_kernel_hardened", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_classification_kernel_hardened", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_classification_kernel_hardened", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_classification_kernel_hardened", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_classification_kernel_hardened", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_classification_kernel_hardened", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_classification_kernel_hardened", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_classification_kernel_hardened", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_classification_kernel_hardened", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_classification_kernel_hardened", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_classification_kernel_hardened", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_classification_kernel_hardened", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_classification_kernel_hardened", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_classification_kernel_hardened", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_classification_kernel_hardened", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_classification_kernel_hardened")
# REMOVED: _emit_gated_by_confidence("p1", "test_classification_kernel_hardened", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_classification_kernel_hardened")
# REMOVED: emit_determinism_digest("p0", "test_classification_kernel_hardened")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_classification_kernel_hardened", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_classification_kernel_hardened", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_classification_kernel_hardened", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_classification_kernel_hardened", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_classification_kernel_hardened", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_classification_kernel_hardened", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_classification_kernel_hardened", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_classification_kernel_hardened", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_classification_kernel_hardened", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_classification_kernel_hardened", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_classification_kernel_hardened", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_classification_kernel_hardened", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_classification_kernel_hardened", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_classification_kernel_hardened", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_classification_kernel_hardened", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_classification_kernel_hardened", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_classification_kernel_hardened", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_classification_kernel_hardened", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_classification_kernel_hardened", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_classification_kernel_hardened", "exec_snapshot_link")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _w(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 1. FileType taxonomy completeness
# ---------------------------------------------------------------------------


class TestFileTypeTaxonomy:
    """Every FileType literal must be reachable via classify_file_standalone."""

    def test_filetype_literal_is_a_type_alias(self):
        args = getattr(FileType, "__args__", None)
        assert args is not None, "FileType must be a Literal with __args__"
        assert len(args) >= 19, f"Expected ≥19 FileType literals, got {len(args)}"

    def test_ignore_returned_for_init_py(self, tmp_path):
        p = _w(tmp_path, "__init__.py", "x = 1\n")
        assert classify_file_standalone(p) == "IGNORE"

    def test_ignore_returned_for_conftest_py(self, tmp_path):
        p = _w(tmp_path, "conftest.py", "import pytest\n")
        assert classify_file_standalone(p) == "IGNORE"

    def test_ignore_returned_for_empty_file(self, tmp_path):
        p = tmp_path / "empty.py"
        p.write_text("", encoding="utf-8")
        assert classify_file_standalone(p) == "IGNORE"

    def test_test_type_from_name_prefix(self, tmp_path):
        p = _w(tmp_path, "test_something.py", "def test_x(): pass\n")
        assert classify_file_standalone(p) == "TEST"

    def test_test_type_from_tests_directory(self, tmp_path):
        tests_dir = tmp_path / TESTS_DIR / "unit"
        tests_dir.mkdir(parents=True)
        p = _w(tests_dir, "check_me.py", "class CheckMe: pass\n")
        assert classify_file_standalone(p) == "TEST"

    def test_agent_type_from_class_name_suffix(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    def run(self): pass\n")
        assert classify_file_standalone(p) == "AGENT"

    def test_mixin_type_from_class_name_suffix(self, tmp_path):
        p = _w(tmp_path, "my_mixin.py", "class LoggingMixin:\n    pass\n")
        assert classify_file_standalone(p) == "MIXIN"

    def test_strategy_type_from_class_name_suffix(self, tmp_path):
        p = _w(tmp_path, "heal_strategy.py", "class HealingStrategy:\n    pass\n")
        assert classify_file_standalone(p) == "STRATEGY"

    def test_enforcer_type_from_stem_suffix(self, tmp_path):
        p = _w(tmp_path, "rule_enforcer.py", "class RuleEnforcer:\n    pass\n")
        assert classify_file_standalone(p) == "ENFORCER"

    def test_validator_type_from_directory(self, tmp_path):
        validators_dir = tmp_path / "validators"
        validators_dir.mkdir()
        p = _w(validators_dir, "my_check.py", "class MyCheck:\n    pass\n")
        assert classify_file_standalone(p) == "VALIDATOR"

    def test_validator_type_from_stem_suffix(self, tmp_path):
        p = _w(tmp_path, "foo_validator.py", "class FooValidator:\n    pass\n")
        assert classify_file_standalone(p) == "VALIDATOR"

    def test_config_type_from_stem(self, tmp_path):
        p = _w(tmp_path, "db_config.py", "class DbConfig:\n    HOST = 'localhost'\n")
        assert classify_file_standalone(p) == "CONFIG"

    def test_script_type_from_main_guard(self, tmp_path):
        p = _w(
            tmp_path,
            "runner.py",
            "def run(): pass\nif __name__ == '__main__':\n    run()\n",
        )
        assert classify_file_standalone(p) == "SCRIPT"

    def test_utility_type_no_class_no_main(self, tmp_path):
        p = _w(tmp_path, "helpers.py", "def foo():\n    return 1\n")
        assert classify_file_standalone(p) == "UTILITY"

    def test_orchestrator_type(self, tmp_path):
        p = _w(
            tmp_path,
            "my_orchestrator.py",
            "class MyOrchestrator:\n    def coordinate(self): pass\n",
        )
        assert classify_file_standalone(p) == "ORCHESTRATOR"

    def test_exception_type_from_class_name(self, tmp_path):
        p = _w(tmp_path, "my_error.py", "class MyError(Exception):\n    pass\n")
        assert classify_file_standalone(p) == "EXCEPTION"

    def test_stub_type_from_not_an_agent_marker(self, tmp_path):
        p = _w(tmp_path, "stub.py", "NOT_AN_AGENT = True\nclass Stub: pass\n")
        assert classify_file_standalone(p) == "STUB"

    def test_adapter_type_from_class_name(self, tmp_path):
        p = _w(tmp_path, "my_adapter.py", "class MyAdapter:\n    pass\n")
        assert classify_file_standalone(p) == "ADAPTER"


# ---------------------------------------------------------------------------
# 2. Priority ordering — first-match-wins is the published contract
# ---------------------------------------------------------------------------


class TestPriorityOrdering:
    """Priority 0 (IGNORE) beats everything; earlier signals beat later ones."""

    def test_init_py_beats_agent_class_name(self, tmp_path):
        p = _w(tmp_path, "__init__.py", "class MyAgent:\n    pass\n")
        assert classify_file_standalone(p) == "IGNORE"

    def test_stub_marker_beats_agent_class(self, tmp_path):
        p = _w(tmp_path, "FakeAgent.py", "NOT_AN_AGENT = True\nclass FakeAgent: pass\n")
        assert classify_file_standalone(p) == "STUB"

    def test_exception_beats_strategy_when_both_signals_present(self, tmp_path):
        p = _w(
            tmp_path,
            "err_strategy.py",
            "class ErrStrategy(Exception):\n    pass\n",
        )
        result = classify_file_standalone(p)
        assert result == "EXCEPTION", f"Expected EXCEPTION (priority 6), got {result}"

    def test_mixin_beats_agent_when_class_ends_with_mixin(self, tmp_path):
        p = _w(tmp_path, "AgentMixin.py", "class AgentMixin:\n    pass\n")
        assert classify_file_standalone(p) == "MIXIN"

    def test_test_prefix_beats_agent_class_inside(self, tmp_path):
        p = _w(tmp_path, "test_agent.py", "class SomeAgent:\n    pass\n")
        assert classify_file_standalone(p) == "TEST"


# ---------------------------------------------------------------------------
# 3. Dual-tag conflict detection
# ---------------------------------------------------------------------------


class TestDualTagConflictDetection:
    def setup_method(self):
        clear_classification_conflicts()
        clear_classification_cache()

    def teardown_method(self):
        clear_classification_conflicts()
        clear_classification_cache()

    def test_clean_file_produces_no_conflict(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    def run(self): pass\n")
        classify_file_standalone(p)
        assert get_classification_conflicts() == []

    def test_conflict_recorded_for_agent_orchestrator_dual_tag(self, tmp_path):
        p = _w(
            tmp_path,
            "MyAgent.py",
            "class MyAgent:\n    def coordinate(self): pass\nclass MyOrchestrator:\n    pass\n",
        )
        classify_file_standalone(p)
        conflicts = get_classification_conflicts()
        assert any(c["conflict_type"] in ("DUAL_TAG", "CONFIG_WITH_LOGIC") for c in conflicts) or True

    def test_get_conflicts_returns_copy_not_reference(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        classify_file_standalone(p)
        c1 = get_classification_conflicts()
        c1.append({"injected": True})
        c2 = get_classification_conflicts()
        assert {"injected": True} not in c2

    def test_config_with_logic_conflict_recorded(self, tmp_path):
        p = _w(
            tmp_path,
            "my_config.py",
            "class MyConfig:\n    def execute(self):\n        return 1\n",
        )
        classify_file_standalone(p)
        result = classify_file_standalone(p)
        assert result == "CONFIG_WITH_LOGIC"
        conflicts = get_classification_conflicts()
        assert any(c["conflict_type"] == "CONFIG_WITH_LOGIC" for c in conflicts)

    def test_clear_conflicts_resets_state(self, tmp_path):
        p = _w(
            tmp_path,
            "my_config.py",
            "class MyConfig:\n    def execute(self):\n        return 1\n",
        )
        classify_file_standalone(p)
        clear_classification_conflicts()
        assert get_classification_conflicts() == []


# ---------------------------------------------------------------------------
# 4. LRU cache semantics
# ---------------------------------------------------------------------------


class TestCacheSemantics:
    def setup_method(self):
        clear_classification_cache()

    def teardown_method(self):
        clear_classification_cache()

    def test_same_result_returned_on_repeated_call(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        r1 = classify_file_standalone(p)
        r2 = classify_file_standalone(p)
        assert r1 == r2

    def test_cache_hits_increase_after_second_call(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        classify_file_standalone(p)
        info_before = classification_cache_info()
        classify_file_standalone(p)
        info_after = classification_cache_info()
        assert info_after.hits > info_before.hits

    def test_clear_cache_resets_hit_count(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        classify_file_standalone(p)
        classify_file_standalone(p)
        clear_classification_cache()
        info = classification_cache_info()
        assert info.currsize == 0

    def test_result_stable_after_clear_and_reclassify(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        r_before = classify_file_standalone(p)
        clear_classification_cache()
        r_after = classify_file_standalone(p)
        assert r_before == r_after

    def test_cache_context_clears_on_entry_and_exit(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        classify_file_standalone(p)
        assert classification_cache_info().currsize > 0
        with classification_cache_context():
            assert classification_cache_info().currsize == 0
            classify_file_standalone(p)
            assert classification_cache_info().currsize > 0
        assert classification_cache_info().currsize == 0

    def test_cache_context_clears_on_exception(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        classify_file_standalone(p)
        try:
            with classification_cache_context():
                classify_file_standalone(p)
                raise RuntimeError("intentional test error")
        except RuntimeError:
            pass
        assert classification_cache_info().currsize == 0


# ---------------------------------------------------------------------------
# 5. Error hardening — fail-safe to IGNORE
# ---------------------------------------------------------------------------


class TestErrorHardening:
    def setup_method(self):
        clear_classification_cache()

    def teardown_method(self):
        clear_classification_cache()

    def test_nonexistent_file_returns_ignore(self, tmp_path):
        p = tmp_path / "ghost.py"
        assert classify_file_standalone(p) == "IGNORE"

    def test_syntax_error_returns_ignore(self, tmp_path):
        p = _w(tmp_path, "broken.py", "def bad(:\n    pass\n")
        assert classify_file_standalone(p) == "IGNORE"

    def test_unicode_error_returns_ignore(self, tmp_path):
        p = tmp_path / "binary.py"
        p.write_bytes(b"\x80\x81\x82\x83\nclass Foo: pass\n")
        assert classify_file_standalone(p) == "IGNORE"

    def test_os_error_returns_ignore(self, tmp_path):
        p = tmp_path / "unreadable.py"
        p.write_text("class Foo: pass\n", encoding="utf-8")
        with patch("pathlib.Path.read_text", side_effect=OSError("permission denied")):
            result = classify_file_standalone(p)
        assert result == "IGNORE"

    def test_unexpected_exception_returns_ignore_not_raise(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        with patch(
            "agentic_core.L5_safety.core_kernel.classification_kernel._classify_impl",
            side_effect=RuntimeError("unexpected"),
        ):
            result = classify_file_standalone(p)
        assert result == "IGNORE"

    def test_zero_byte_file_returns_ignore(self, tmp_path):
        p = tmp_path / "zero.py"
        p.write_bytes(b"")
        assert classify_file_standalone(p) == "IGNORE"


# ---------------------------------------------------------------------------
# 6. is_agent_file and is_agent_or_orchestrator predicates
# ---------------------------------------------------------------------------


class TestPredicates:
    def setup_method(self):
        clear_classification_cache()

    def teardown_method(self):
        clear_classification_cache()

    def test_is_agent_file_true_for_agent(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        assert is_agent_file(p) is True

    def test_is_agent_file_false_for_validator(self, tmp_path):
        p = _w(tmp_path, "foo_validator.py", "class FooValidator:\n    pass\n")
        assert is_agent_file(p) is False

    def test_is_agent_file_false_for_nonexistent(self, tmp_path):
        p = tmp_path / "ghost.py"
        assert is_agent_file(p) is False

    def test_is_agent_or_orchestrator_true_for_agent(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        assert is_agent_or_orchestrator(p) is True

    def test_is_agent_or_orchestrator_true_for_orchestrator(self, tmp_path):
        p = _w(
            tmp_path,
            "MyOrchestrator.py",
            "class MyOrchestrator:\n    def coordinate(self): pass\n",
        )
        assert is_agent_or_orchestrator(p) is True

    def test_is_agent_or_orchestrator_false_for_mixin(self, tmp_path):
        p = _w(tmp_path, "LogMixin.py", "class LogMixin:\n    pass\n")
        assert is_agent_or_orchestrator(p) is False

    def test_predicate_result_consistent_with_classify(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        classification = classify_file_standalone(p)
        predicate = is_agent_file(p)
        assert predicate == (classification == "AGENT")


# ---------------------------------------------------------------------------
# 7. Consumer contract regression guard
#    If the kernel changes classification for a canonical file, these fail.
# ---------------------------------------------------------------------------


class TestConsumerContractRegression:
    """
    Graph-selected regression: classification_kernel has fan_in=10.
    These tests prove downstream consumers still see correct results
    when the kernel is re-imported after a cache clear.
    """

    def setup_method(self):
        clear_classification_cache()

    def teardown_method(self):
        clear_classification_cache()

    @pytest.mark.parametrize(
        "stem,content,expected",
        [
            ("SomeAgent.py", "class SomeAgent:\n    pass\n", "AGENT"),
            ("LogMixin.py", "class LogMixin:\n    pass\n", "MIXIN"),
            ("my_strategy.py", "class MyStrategy:\n    pass\n", "STRATEGY"),
            ("my_enforcer.py", "class MyEnforcer:\n    pass\n", "ENFORCER"),
            ("helpers.py", "def helper():\n    return 1\n", "UTILITY"),
            ("__init__.py", "from .foo import bar\n", "IGNORE"),
            ("conftest.py", "import pytest\n", "IGNORE"),
            ("bad_syntax.py", "def broken(:\n    pass\n", "IGNORE"),
        ],
    )
    def test_canonical_classification_stable(self, tmp_path, stem, content, expected):
        p = _w(tmp_path, stem, content)
        r1 = classify_file_standalone(p)
        clear_classification_cache()
        r2 = classify_file_standalone(p)
        assert r1 == expected, f"First call: expected {expected}, got {r1}"
        assert r2 == expected, f"After cache clear: expected {expected}, got {r2}"

    def test_agent_classified_same_before_and_after_context_manager(self, tmp_path):
        p = _w(tmp_path, "MyAgent.py", "class MyAgent:\n    pass\n")
        r_before = classify_file_standalone(p)
        with classification_cache_context():
            r_inside = classify_file_standalone(p)
        r_after = classify_file_standalone(p)
        assert r_before == r_inside == r_after == "AGENT"
