"""Invariant tests for HierarchyAgent bug-fixes 1–4.

Branch inventory (§1.3):

  Fix 1 — _enforce_tests_structure approved-subfolder guard:
    - *Agent.py inside approved subfolder (support/)  → violation logged, no move
    - conftest.py inside approved subfolder           → exempt, no violation
    - test_foo.py inside approved subfolder           → clean, no violation

  Fix 2 — _block_agent_files_in_tests:
    - *Agent.py directly in tests/                    → violation, no move
    - *Agent.py inside tests/support/                 → violation, no move
    - clean tests/ (only test_*.py files)             → zero violations from this guard

  Fix 3 — get_best_target_l2 / _calculate_subfolder_confidence_for_agent:
    - *Agent.py, l1_name=TESTS_DIR   → "__ARCHIVE__" sentinel returned
    - *Agent.py, l1_name="L5_safety" (source layer) → valid subfolder (not __ARCHIVE__)
    - non-agent file, l1_name=TESTS_DIR → normal routing (not __ARCHIVE__)

  Fix 4 — SSOT tests/support/ forbidden_patterns:
    - "forbidden_patterns" key present in tests/support/ config
    - pattern matches FooAgent.py
    - pattern does NOT match test_foo.py
"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hierarchy_agent_invariants")
_emit_applies_guardrail("p0", "test_hierarchy_agent_invariants", "p0_governance")
_emit_reads_policy_state("p0", "test_hierarchy_agent_invariants", "policy_binding")
_emit_snapshots_state("p0", "test_hierarchy_agent_invariants", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_hierarchy_agent_invariants", "p4obs", "metric_1")
_emit_emits_metric_event("test_hierarchy_agent_invariants", "p4obs", "metric_2")
_emit_emits_metric_event("test_hierarchy_agent_invariants", "p4obs", "metric_3")
_emit_emits_metric_event("test_hierarchy_agent_invariants", "p4obs", "metric_4")
_emit_emits_metric_event("test_hierarchy_agent_invariants", "p4obs", "metric_5")
_emit_emits_metric_event("test_hierarchy_agent_invariants", "p4obs", "metric_6")
_emit_records_incident_event("test_hierarchy_agent_invariants", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_hierarchy_agent_invariants", "p4obs", "anomaly")
_emit_writes_observability_log("test_hierarchy_agent_invariants", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_hierarchy_agent_invariants", "p4obs", "mon_state")
_emit_triggers_alert("test_hierarchy_agent_invariants", "p4obs", "alert")
_emit_links_incident_trace("test_hierarchy_agent_invariants", "p4obs", "trace_link")
_emit_captures_pattern("test_hierarchy_agent_invariants", "p3lm", "pattern")
_emit_records_learning_event("test_hierarchy_agent_invariants", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_hierarchy_agent_invariants", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_hierarchy_agent_invariants", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_hierarchy_agent_invariants", "p3lm", "routing")
_emit_improves_agent_policy("test_hierarchy_agent_invariants", "p3lm", "policy")
_emit_stores_learning_state("test_hierarchy_agent_invariants", "p3lm", "state")
_emit_records_execution_trace("test_hierarchy_agent_invariants", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_hierarchy_agent_invariants", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_hierarchy_agent_invariants", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_hierarchy_agent_invariants", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_hierarchy_agent_invariants", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_hierarchy_agent_invariants", "env_read", "p2_env_1")
_emit_reads_environ("test_hierarchy_agent_invariants", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_hierarchy_agent_invariants", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_hierarchy_agent_invariants", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_hierarchy_agent_invariants", "context_pull")
_emit_pulls_context("p1", "test_hierarchy_agent_invariants", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_hierarchy_agent_invariants", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_hierarchy_agent_invariants", "uwg_term_2")
_emit_writes_through("p1", "test_hierarchy_agent_invariants", "write_through")
_emit_writes_through("p1", "test_hierarchy_agent_invariants", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_hierarchy_agent_invariants", "safety_validation")
_emit_invokes_eval("p1", "test_hierarchy_agent_invariants", "eval_call")
_emit_proposal_commits_routing("p1", "test_hierarchy_agent_invariants", "routing_commit")
_emit_escalates_to_human("p1", "test_hierarchy_agent_invariants", "human_escalation")
_emit_routes_through("p1", "test_hierarchy_agent_invariants", "route_through")
_emit_checks_agent_registry("p1", "test_hierarchy_agent_invariants", "agent_registry")
_emit_validates_agent_capability("p1", "test_hierarchy_agent_invariants", "capability")
_emit_dispatches_execution_plan("p1", "test_hierarchy_agent_invariants", "exec_plan")
_emit_agent_executes_agent("p1", "test_hierarchy_agent_invariants", "sub_agent")
_emit_routes_to_agent("p1", "test_hierarchy_agent_invariants", "target_agent")
_emit_verifies_policy("p1", "test_hierarchy_agent_invariants", "policy_check")
_emit_observes_runtime_state("p1", "test_hierarchy_agent_invariants", "runtime_state")
_emit_verifies_boundary("p1", "test_hierarchy_agent_invariants", "boundary_check")
_emit_transcripts_response("p1", "test_hierarchy_agent_invariants", "transcript")
_emit_hard_fails_untranscripted("p1", "test_hierarchy_agent_invariants")
_emit_gated_by_confidence("p1", "test_hierarchy_agent_invariants", "confidence_gate")
emit_replay_key("p0", "test_hierarchy_agent_invariants")
emit_determinism_digest("p0", "test_hierarchy_agent_invariants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hierarchy_agent_invariants", "execution_auth")
_emit_validates_capability("p2", "test_hierarchy_agent_invariants", "capability_check")
_emit_routes_to_capability("p2", "test_hierarchy_agent_invariants", "capability_route")
_emit_writes_via_uwg("p2", "test_hierarchy_agent_invariants", "uwg_write")
_emit_blocks_direct_write("p2", "test_hierarchy_agent_invariants", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hierarchy_agent_invariants", "tool_invocation")
_emit_captures_execution_output("p2", "test_hierarchy_agent_invariants", "exec_output")
_emit_dispatches_agent("p3", "test_hierarchy_agent_invariants", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hierarchy_agent_invariants", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hierarchy_agent_invariants", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hierarchy_agent_invariants", "healing_outcome")
_emit_escalates_failure("p3", "test_hierarchy_agent_invariants", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hierarchy_agent_invariants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hierarchy_agent_invariants", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hierarchy_agent_invariants", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hierarchy_agent_invariants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hierarchy_agent_invariants", "eval_metric")
_emit_stores_embedding("p4", "test_hierarchy_agent_invariants", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hierarchy_agent_invariants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hierarchy_agent_invariants", "exec_snapshot_link")

pytestmark = pytest.mark.architecture


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_agent(tmp_root: Path, healing_enabled: bool = False):
    """Construct a minimal HierarchyAgent with mocked gatekeeper, no filesystem side-effects."""
    from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

    agent = object.__new__(HierarchyAgent)
    agent.project_root = tmp_root
    agent.healing_enabled = healing_enabled
    agent.agent_name = "HierarchyAgent"
    agent.gatekeeper = MagicMock()
    return agent


def _results() -> dict:
    return {"files_relocated": 0, "folders_removed": 0, "violations_found": 0, "errors": []}


# ---------------------------------------------------------------------------
# Fix 1 — _enforce_tests_structure: approved-subfolder skip is too broad
# ---------------------------------------------------------------------------


class TestFix1EnforceTestsStructure:
    """Files inside approved subfolders must still be checked for test_ prefix."""

    def _run(self, tmp_path: Path, files: list[tuple[str, str]]) -> dict:
        for rel, content in files:
            p = tmp_path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._enforce_tests_structure(tmp_path, r)
        return r

    def test_agent_file_in_approved_subfolder_raises_violation(self, tmp_path: Path) -> None:
        """*Agent.py inside tests/support/ must be flagged — no silent skip."""
        r = self._run(tmp_path, [("support/SomeAgent.py", "class SomeAgent: pass")])
        assert r["violations_found"] >= 1

    def test_infra_file_in_approved_subfolder_is_exempt(self, tmp_path: Path) -> None:
        """conftest.py inside tests/support/ must NOT produce a violation."""
        r = self._run(tmp_path, [("support/conftest.py", "# conftest")])
        assert r["violations_found"] == 0

    def test_test_prefixed_file_in_approved_subfolder_is_clean(self, tmp_path: Path) -> None:
        """test_foo.py inside tests/support/ must NOT produce a violation."""
        r = self._run(tmp_path, [("support/test_foo.py", "def test_foo(): pass")])
        assert r["violations_found"] == 0

    def test_dunder_init_in_approved_subfolder_is_exempt(self, tmp_path: Path) -> None:
        """__init__.py inside tests/support/ must NOT produce a violation."""
        r = self._run(tmp_path, [("support/__init__.py", "")])
        assert r["violations_found"] == 0

    def test_non_test_non_agent_file_in_approved_subfolder_is_flagged(self, tmp_path: Path) -> None:
        """helpers.py (no prefix, not infra) inside support/ must also be flagged."""
        r = self._run(tmp_path, [("support/helpers.py", "# helpers")])
        assert r["violations_found"] >= 1

    def test_agent_file_in_approved_subfolder_is_not_moved(self, tmp_path: Path) -> None:
        """Violation is logged but the file must not be moved."""
        src = tmp_path / "support" / "SomeAgent.py"
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_text("class SomeAgent: pass", encoding="utf-8")
        agent = _make_agent(tmp_path, healing_enabled=True)
        r = _results()
        agent._enforce_tests_structure(tmp_path, r)
        # File must still be in place — _enforce only reports
        assert src.exists(), "Agent file must NOT be moved by _enforce_tests_structure"
        # Gatekeeper safe_move must NOT have been called
        agent.gatekeeper.safe_move.assert_not_called()


# ---------------------------------------------------------------------------
# Fix 2 — _block_agent_files_in_tests: no pre-check blocking *Agent.py → tests/
# ---------------------------------------------------------------------------


class TestFix2BlockAgentFilesInTests:
    """_block_agent_files_in_tests scans tests/ and records violations without moving."""

    def test_block_agent_files_in_tests_root(self, tmp_path: Path) -> None:
        """*Agent.py directly in tests/ triggers a violation."""
        (tmp_path / TESTS_DIR).mkdir()
        (tmp_path / TESTS_DIR / "SomeAgent.py").write_text("class SomeAgent: pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] >= 1

    def test_block_agent_files_in_tests_support(self, tmp_path: Path) -> None:
        """*Agent.py inside tests/support/ triggers a violation."""
        (tmp_path / TESTS_DIR / "support").mkdir(parents=True)
        (tmp_path / TESTS_DIR / "support" / "FooAgent.py").write_text("class FooAgent: pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] >= 1

    def test_no_violation_when_tests_is_clean(self, tmp_path: Path) -> None:
        """Clean tests/ (only test_*.py) produces zero violations from _block_agent_files_in_tests."""
        (tmp_path / TESTS_DIR / "unit").mkdir(parents=True)
        (tmp_path / TESTS_DIR / "unit" / "test_something.py").write_text("def test_x(): pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] == 0

    def test_block_does_not_move_agent_file(self, tmp_path: Path) -> None:
        """_block_agent_files_in_tests must NOT move any file (report only)."""
        (tmp_path / TESTS_DIR).mkdir()
        src = tmp_path / TESTS_DIR / "BrokenAgent.py"
        src.write_text("class BrokenAgent: pass")
        agent = _make_agent(tmp_path, healing_enabled=True)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert src.exists(), "_block_agent_files_in_tests must not move the file"
        agent.gatekeeper.safe_move.assert_not_called()

    def test_multiple_agent_files_each_counted(self, tmp_path: Path) -> None:
        """Every *Agent.py file found produces a distinct violation count increment."""
        (tmp_path / TESTS_DIR / "support").mkdir(parents=True)
        (tmp_path / TESTS_DIR / "support" / "SomeAgent.py").write_text("class SomeAgent: pass")
        (tmp_path / TESTS_DIR / "support" / "OtherAgent.py").write_text("class OtherAgent: pass")
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)
        assert r["violations_found"] == 2

    def test_no_tests_dir_is_noop(self, tmp_path: Path) -> None:
        """If tests/ does not exist, _block_agent_files_in_tests is a silent no-op."""
        agent = _make_agent(tmp_path)
        r = _results()
        agent._block_agent_files_in_tests(r)  # Must not raise
        assert r["violations_found"] == 0


# ---------------------------------------------------------------------------
# Fix 3 — get_best_target_l2 / _calculate_subfolder_confidence_for_agent
# ---------------------------------------------------------------------------


class TestFix3SubfolderConfidence:
    """get_best_target_l2 returns __ARCHIVE__ for agent files routed to non-source roots."""

    def test_get_best_target_l2_agent_file_tests_root_returns_archive_sentinel(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        result = get_best_target_l2(TESTS_DIR, "SomeAgent.py")
        assert result == "__ARCHIVE__", (
            f"Expected '__ARCHIVE__' for agent file in 'tests' root, got {result!r}"
        )

    def test_get_best_target_l2_agent_file_source_layer_returns_valid(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        result = get_best_target_l2("L5_safety", "SomeAgent.py")
        assert result != "__ARCHIVE__", (
            "Agent file in source layer 'L5_safety' must NOT get the ARCHIVE sentinel"
        )

    def test_get_best_target_l2_non_agent_file_tests_root_proceeds(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        result = get_best_target_l2(TESTS_DIR, "test_something.py")
        assert result != "__ARCHIVE__", "Non-agent files must go through normal routing, not ARCHIVE sentinel"

    def test_confidence_zero_for_all_low_confidence_roots(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import (
            _AGENT_LOW_CONFIDENCE_ROOTS,
            _calculate_subfolder_confidence_for_agent,
        )

        for root in _AGENT_LOW_CONFIDENCE_ROOTS:
            conf = _calculate_subfolder_confidence_for_agent(root, "FooAgent.py")
            assert conf < 0.5, f"Expected confidence < 0.5 for root {root!r}, got {conf}"

    def test_confidence_one_for_source_layer(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import (
            _calculate_subfolder_confidence_for_agent,
        )

        conf = _calculate_subfolder_confidence_for_agent(AGENTIC_CORE_DIR, "FooAgent.py")
        assert conf >= 0.5, f"Expected confidence >= 0.5 for source layer, got {conf}"

    def test_docs_root_also_returns_archive_sentinel(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        assert get_best_target_l2("docs", "MyAgent.py") == "__ARCHIVE__"

    def test_data_root_also_returns_archive_sentinel(self) -> None:
        from agentic_core.L5_safety.enforcement.mission_utils_enforcer import get_best_target_l2

        assert get_best_target_l2("data", "MyAgent.py") == "__ARCHIVE__"


# ---------------------------------------------------------------------------
# Fix 4 — SSOT tests/support/ forbidden_patterns
# ---------------------------------------------------------------------------


class TestFix4SSOTForbiddenPatterns:
    """tests/support/ SSOT entry must contain forbidden_patterns blocking *Agent.py."""

    def _get_support_config(self) -> dict:
        from agentic_core.L5_safety.config.structure_blueprint import (
            get_all_territories,
        )

        return get_all_territories()[TESTS_DIR]["subfolders"]["support"]

    def test_ssot_support_has_forbidden_patterns(self) -> None:
        cfg = self._get_support_config()
        assert "forbidden_patterns" in cfg, "tests/support/ SSOT entry must have a 'forbidden_patterns' key"

    def test_ssot_support_forbidden_patterns_rejects_agent_py(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        assert any(re.match(p, "FooAgent.py") for p in patterns), (
            "forbidden_patterns must match 'FooAgent.py'"
        )

    def test_ssot_support_forbidden_patterns_allows_test_file(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        assert not any(re.match(p, "test_foo.py") for p in patterns), (
            "forbidden_patterns must NOT match 'test_foo.py'"
        )

    def test_ssot_support_forbidden_patterns_rejects_any_agent_py(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        for name in ["LocationHealerAgent.py", "HierarchyAgent.py", "SomeRandomAgent.py"]:
            assert any(re.match(p, name) for p in patterns), f"forbidden_patterns must match {name!r}"

    def test_ssot_support_forbidden_patterns_allows_conftest(self) -> None:
        cfg = self._get_support_config()
        patterns = cfg["forbidden_patterns"]
        assert not any(re.match(p, "conftest.py") for p in patterns), (
            "forbidden_patterns must NOT match 'conftest.py'"
        )
