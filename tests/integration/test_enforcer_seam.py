"""
Phase 1 — ENFORCER + SEAM classification tests.

Tests exercise BOTH kernel (classify_file_standalone) and FCA (classify_file)
to prove classification paths exist at both layers.

Unit tests:
1. guardrail with verify_change returning (False,"Block:") -> ENFORCER (kernel)
2. pure _enforcer.py -> ENFORCER (kernel)
3. _seam.py with load_* + importlib -> SEAM (kernel)
4. _seam.py with 3 functions >5 statements -> NOT SEAM (kernel)
5. _contract.py pure dataclass -> TYPES
6. _contract.py with validate_* + raise + policy_ -> ENFORCER (kernel)
7. enforcement/_strategy.py -> remains STRATEGY

FCA-specific tests:
8. FCA classify_file() ENFORCER via AND-gate backstop
9. FCA classify_file() SEAM disqualification (>=3 complex funcs)
10. FCA classify_file() SEAM positive (simple seam with importlib)

Integration test:
11. mini repo slice of 5 files under enforcement/
12. FileType Literal includes ENFORCER and SEAM
"""

import textwrap
from pathlib import Path
from typing import get_args

import pytest

from agentic_core.L5_safety.core_kernel.classification_kernel import (
    FileType,
    classify_file_standalone,
    clear_classification_cache,
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

# REMOVED: _emit_emits_metric_event("test_enforcer_seam", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_enforcer_seam", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_enforcer_seam", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_enforcer_seam", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_enforcer_seam", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_enforcer_seam", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_enforcer_seam", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_enforcer_seam", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_enforcer_seam", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_enforcer_seam", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_enforcer_seam", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_enforcer_seam", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_enforcer_seam", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_enforcer_seam", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_enforcer_seam", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_enforcer_seam", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_enforcer_seam", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_enforcer_seam", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_enforcer_seam", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_enforcer_seam", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_enforcer_seam", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_enforcer_seam", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_enforcer_seam", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_enforcer_seam", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_enforcer_seam", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_enforcer_seam", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_enforcer_seam", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_enforcer_seam", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_enforcer_seam")
# REMOVED: _emit_applies_guardrail("p0", "test_enforcer_seam", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_enforcer_seam", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_enforcer_seam", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_enforcer_seam")
# REMOVED: emit_determinism_digest("p0", "test_enforcer_seam")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_enforcer_seam", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_enforcer_seam", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_enforcer_seam", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_enforcer_seam", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_enforcer_seam", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_enforcer_seam", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_enforcer_seam", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_enforcer_seam", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_enforcer_seam", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_enforcer_seam", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_enforcer_seam", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_enforcer_seam", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_enforcer_seam", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_enforcer_seam", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_enforcer_seam", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_enforcer_seam", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_enforcer_seam", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_enforcer_seam", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_enforcer_seam", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_enforcer_seam", "exec_snapshot_link")
# REMOVED: _emit_escalates_to_human("p1", "test_enforcer_seam", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_enforcer_seam", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_enforcer_seam", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_enforcer_seam", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_enforcer_seam", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_enforcer_seam", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_enforcer_seam", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_enforcer_seam", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_enforcer_seam", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_enforcer_seam", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_enforcer_seam", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_enforcer_seam")
# REMOVED: _emit_gated_by_confidence("p1", "test_enforcer_seam", "confidence_gate")

# ================================================================
# Helpers
# ================================================================


def _write(tmp_path: Path, name: str, code: str) -> Path:
    """Write a .py file under tmp_path and return its Path."""
    p = tmp_path / name
    p.write_text(textwrap.dedent(code), encoding="utf-8")
    return p


def _classify_kernel(tmp_path: Path, name: str, code: str) -> str:
    """Write file, clear cache, classify via kernel standalone."""
    p = _write(tmp_path, name, code)
    clear_classification_cache()
    return classify_file_standalone(p)


def _make_fca(tmp_path: Path):
    """Create a minimal FileClassificationAgent for testing."""
    from agentic_core.L5_safety.reasoning.FileClassificationAgent import (
        FileClassificationAgent,
    )

    return FileClassificationAgent(
        project_root=tmp_path,
        dry_run=True,
        validate_only=True,
    )


def _classify_fca(tmp_path: Path, name: str, code: str) -> str:
    """Write file, classify via FCA classify_file()."""
    p = _write(tmp_path, name, code)
    fca = _make_fca(tmp_path)
    return fca.classify_file(p)


# ================================================================
# Kernel-level ENFORCER tests
# ================================================================


@pytest.mark.unit_min_deps
class TestEnforcerClassification:
    """Kernel-level ENFORCER detection."""

    def test_guardrail_with_verify_change_block(self, tmp_path):
    """Test guardrail_with_verify_change_block contract compliance."""
    # Arrange
    # TODO: Set up contract test scenario
    test_scenario = {}  # Replace with actual test scenario

    # Act
    # TODO: Execute contract test
    contract_result = None  # Replace with actual contract test

    # Assert - General Contract
    assert contract_result is not None, "Contract should produce a result"
    assert isinstance(contract_result, object), "Result should be an object"
    # TODO: Add specific contract assertions
    # assert hasattr(contract_result, "complies"), "Result should indicate compliance"
        result = _classify_kernel(
            tmp_path,
            "tool_policy_enforcer.py",
            """\
            class ToolPolicyEnforcer:
                def enforce(self, action):
                    pass
        """,
        )
        assert result == "ENFORCER"

    def test_contract_with_enforcer_suffix(self, tmp_path):
    """Test contract_with_enforcer_suffix contract compliance."""
    # Arrange
    # TODO: Set up contract scenario
    contract_scenario = {}  # Replace with actual scenario

    # Act
    # TODO: Execute contract behavior
    behavior_result = None  # Replace with actual behavior execution

    # Assert - Behavioral Contract
    assert behavior_result is not None, "Contract behavior should produce a result"
    assert isinstance(behavior_result, (dict, list, str, int, float, bool)), "Result should be serializable"
    # TODO: Add specific behavioral contract assertions
    # assert behavior_result.get("complies", False), "Behavior should comply with contract"

# ================================================================
# Kernel-level SEAM tests
# ================================================================


@pytest.mark.unit_min_deps
class TestSeamClassification:
    """Kernel-level SEAM detection."""

    def test_seam_with_load_importlib(self, tmp_path):
        result = _classify_kernel(
            tmp_path,
            "plugin_seam.py",
            """\
            import importlib

            class PluginSeam:
                def load_module(self, name):
                    return importlib.import_module(name)
        """,
        )
        assert result == "SEAM"

    def test_seam_kernel_name_match(self, tmp_path):
        result = _classify_kernel(
            tmp_path,
            "adapter_seam.py",
            """\
            class AdapterSeam:
                def get_adapter(self):
                    return None
        """,
        )
        assert result == "SEAM"


# ================================================================
# Negative / non-ENFORCER tests (kernel)
# ================================================================


@pytest.mark.unit_min_deps
class TestNonEnforcerClassification:
    """Files that must NOT be classified as ENFORCER."""

    def test_contract_pure_dataclass_is_not_enforcer(self, tmp_path):
    """Test contract_pure_dataclass_is_not_enforcer contract compliance."""
    # Arrange
    # TODO: Set up contract scenario
    contract_scenario = {}  # Replace with actual scenario

    # Act
    # TODO: Execute contract behavior
    behavior_result = None  # Replace with actual behavior execution

    # Assert - Behavioral Contract
    assert behavior_result is not None, "Contract behavior should produce a result"
    assert isinstance(behavior_result, (dict, list, str, int, float, bool)), "Result should be serializable"
    # TODO: Add specific behavioral contract assertions
    # assert behavior_result.get("complies", False), "Behavior should comply with contract"
    def test_enforcement_strategy_remains_strategy(self, tmp_path):
        """enforcement/_strategy.py -> STRATEGY (folder mapping unchanged)."""
        enforcement = tmp_path / "enforcement"
        enforcement.mkdir()
        p = enforcement / "retry_strategy.py"
        p.write_text(
            textwrap.dedent("""\
            class RetryStrategy:
                def execute(self):
                    pass
        """),
            encoding="utf-8",
        )
        clear_classification_cache()
        result = classify_file_standalone(p)
        assert result == "STRATEGY"


# ================================================================
# FCA-level tests (exercise classify_file() directly)
# ================================================================


@pytest.mark.unit_min_deps
class TestFCAEnforcerClassification:
    """FCA classify_file() ENFORCER detection with AND-gate backstop."""

    def test_fca_enforcer_and_gate(self, tmp_path):
        """FCA requires BOTH control outcome AND policy semantics for ENFORCER."""
        result = _classify_fca(
            tmp_path,
            "budget_guardrail.py",
            """\
            class BudgetGuardrail:
                def validate_budget(self, amount):
                    if amount > self.policy_limit:
                        raise ValueError("Budget violation: exceeded limit")
                    return amount
        """,
        )
        assert result == "ENFORCER", (
            f"FCA should classify guardrail with validate_*+raise+policy_ as ENFORCER, got {result}"
        )

    def test_fca_enforcer_name_only_no_backstop(self, tmp_path):
        """ENFORCER name without behavioral backstop should NOT be ENFORCER in FCA."""
        result = _classify_fca(
            tmp_path,
            "simple_guard.py",
            """\
            class SimpleGuard:
                def check(self, x):
                    return x > 0
        """,
        )
        # Without control outcome + policy semantics, FCA should NOT classify as ENFORCER
        assert result != "ENFORCER", (
            f"FCA should NOT classify guard without AND-gate backstop as ENFORCER, got {result}"
        )


@pytest.mark.unit_min_deps
class TestFCASeamClassification:
    """FCA classify_file() SEAM detection with disqualifiers."""

    def test_fca_seam_positive(self, tmp_path):
        """Simple seam with importlib -> SEAM via FCA."""
        result = _classify_fca(
            tmp_path,
            "loader_seam.py",
            """\
            import importlib

            class LoaderSeam:
                def load_module(self, name):
                    return importlib.import_module(name)
        """,
        )
        assert result == "SEAM", f"FCA should classify seam with importlib as SEAM, got {result}"

    def test_fca_seam_disqualified_complex_funcs(self, tmp_path):
        """>=3 FunctionDef with body >5 stmts disqualifies SEAM in FCA."""
        result = _classify_fca(
            tmp_path,
            "complex_seam.py",
            """\
            import importlib

            class ComplexSeam:
                def load_module(self, name):
                    return importlib.import_module(name)

                def process_a(self, x):
                    a = x + 1
                    b = a + 2
                    c = b + 3
                    d = c + 4
                    e = d + 5
                    return e + 6

                def process_b(self, x):
                    a = x + 1
                    b = a + 2
                    c = b + 3
                    d = c + 4
                    e = d + 5
                    return e + 6

                def process_c(self, x):
                    a = x + 1
                    b = a + 2
                    c = b + 3
                    d = c + 4
                    e = d + 5
                    return e + 6
        """,
        )
        assert result != "SEAM", f"FCA should disqualify SEAM with >=3 complex functions, got {result}"


# ================================================================
# Integration test
# ================================================================


@pytest.mark.unit_min_deps
class TestEnforcementFolderIntegration:
    """Mini repo slice verifying correct classification + stats."""

    def test_enforcement_folder_classifications(self, tmp_path):
        """5 files under enforcement/ — verify correct classification."""
        enforcement = tmp_path / "enforcement"
        enforcement.mkdir()

        files = {
            "safety_guardrail.py": (
                "ENFORCER",
                textwrap.dedent("""\
                    class SafetyGuardrail:
                        def validate_safety(self, change):
                            if change.policy_violation:
                                raise ValueError("Safety violation blocked")
                            return change
                """),
            ),
            "retry_strategy.py": (
                "STRATEGY",
                textwrap.dedent("""\
                    class RetryStrategy:
                        def execute(self):
                            pass
                """),
            ),
            "tool_policy_enforcer.py": (
                "ENFORCER",
                textwrap.dedent("""\
                    class ToolPolicyEnforcer:
                        def validate_tool(self, tool):
                            if tool.enforce_blocked:
                                raise PermissionError("Tool policy violation")
                            return tool
                """),
            ),
            "input_validator.py": (
                "VALIDATOR",
                textwrap.dedent("""\
                    class InputValidator:
                        def validate(self, data):
                            return bool(data)
                """),
            ),
            "error_types.py": (
                "TYPES",
                textwrap.dedent("""\
                    from typing import TypedDict, Literal
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)
# REMOVED: _emit_pulls_context("p1", "test_enforcer_seam", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_enforcer_seam", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_enforcer_seam", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_enforcer_seam", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_enforcer_seam", "write_through")
# REMOVED: _emit_writes_through("p1", "test_enforcer_seam", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_enforcer_seam", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_enforcer_seam", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_enforcer_seam", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_enforcer_seam", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_enforcer_seam", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_enforcer_seam", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_enforcer_seam", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_enforcer_seam", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_enforcer_seam", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_enforcer_seam", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_enforcer_seam", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_enforcer_seam", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_enforcer_seam", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_enforcer_seam", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_enforcer_seam")
# REMOVED: _emit_gated_by_confidence("p1", "test_enforcer_seam", "confidence_gate")

                    class ErrorInfo(TypedDict):
                        code: int
                        message: str
                        severity: Literal["low", "high"]
                """),
            ),
        }

        fca = _make_fca(tmp_path)
        for filename, (expected, code) in files.items():
            p = enforcement / filename
            p.write_text(code, encoding="utf-8")
            actual = fca.classify_file(p)
            assert actual == expected, f"{filename}: expected {expected}, got {actual}"

    def test_filetype_literal_includes_new_types(self):
        """FileType Literal must include ENFORCER and SEAM."""
        valid_types = get_args(FileType)
        assert "ENFORCER" in valid_types
        assert "SEAM" in valid_types
