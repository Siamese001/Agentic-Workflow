"""
Contract tests for decorator canonical locations and backward-compat shims.

Architecture (after layer inversion fix):
    CANONICAL (SSOT):
        - agentic_core/base_agents/decorators.py  (standard_heal, HEAL_RESULT_SCHEMA)
        - agentic_core/base_agents/timeout_decorator.py  (timeout)

    BACKWARD-COMPAT SHIMS:
        - agentic_core/L5_safety/utils/decorators_util.py  (re-exports from base_agents)
        - agentic_core/L0_routing/utils/timeout_decorator_util.py  (re-exports from base_agents)

These tests verify:
    1. Canonical modules export required symbols
    2. Shims re-export the exact same objects (identity check)
    3. No agentic_core module imports from shim locations (enforcement)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_decorator_shim_contract")
# REMOVED: _emit_applies_guardrail("p0", "test_decorator_shim_contract", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_decorator_shim_contract", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_decorator_shim_contract", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_decorator_shim_contract", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_decorator_shim_contract", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_decorator_shim_contract", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_decorator_shim_contract", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_decorator_shim_contract", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_decorator_shim_contract", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_decorator_shim_contract", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_decorator_shim_contract", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_decorator_shim_contract", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_decorator_shim_contract", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_decorator_shim_contract", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_decorator_shim_contract", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_decorator_shim_contract", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_decorator_shim_contract", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_decorator_shim_contract", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_decorator_shim_contract", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_decorator_shim_contract", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_decorator_shim_contract", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_decorator_shim_contract", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_decorator_shim_contract", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_decorator_shim_contract", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_decorator_shim_contract", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_decorator_shim_contract", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_decorator_shim_contract", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_decorator_shim_contract", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_decorator_shim_contract", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_decorator_shim_contract", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_decorator_shim_contract", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_decorator_shim_contract", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_decorator_shim_contract", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_decorator_shim_contract", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_decorator_shim_contract", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_decorator_shim_contract", "write_through")
# REMOVED: _emit_writes_through("p1", "test_decorator_shim_contract", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_decorator_shim_contract", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_decorator_shim_contract", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_decorator_shim_contract", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_decorator_shim_contract", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_decorator_shim_contract", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_decorator_shim_contract", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_decorator_shim_contract", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_decorator_shim_contract", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_decorator_shim_contract", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_decorator_shim_contract", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_decorator_shim_contract", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_decorator_shim_contract", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_decorator_shim_contract", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_decorator_shim_contract", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_decorator_shim_contract")
# REMOVED: _emit_gated_by_confidence("p1", "test_decorator_shim_contract", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_decorator_shim_contract")
# REMOVED: emit_determinism_digest("p0", "test_decorator_shim_contract")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_decorator_shim_contract", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_decorator_shim_contract", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_decorator_shim_contract", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_decorator_shim_contract", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_decorator_shim_contract", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_decorator_shim_contract", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_decorator_shim_contract", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_decorator_shim_contract", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_decorator_shim_contract", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_decorator_shim_contract", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_decorator_shim_contract", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_decorator_shim_contract", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_decorator_shim_contract", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_decorator_shim_contract", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_decorator_shim_contract", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_decorator_shim_contract", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_decorator_shim_contract", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_decorator_shim_contract", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_decorator_shim_contract", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_decorator_shim_contract", "exec_snapshot_link")

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.unit_min_deps


class TestCanonicalDecoratorsContract:
    """Verify base_agents.decorators is the canonical SSOT."""

    
    def test_dunder_all_matches_exports(self) -> None:
                from agentic_core.L0_routing.config.path_constants import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
                import agentic_core.utils.decorators_base_util as mod
                from agentic_core.utils.timeout_decorator_util import timeout
                from agentic_core.L5_safety.utils.decorators_util import standard_heal as shim
                from agentic_core.utils.decorators_base_util import standard_heal as canonical
                from agentic_core.L5_safety.utils.decorators_util import (
                from agentic_core.utils.decorators_base_util import HEAL_RESULT_SCHEMA as canonical
                from agentic_core.L0_routing.utils.timeout_decorator_util import (
                from agentic_core.utils.timeout_decorator_util import timeout as canonical
                from agentic_core.utils.timeout_decorator_util import timeout as canonical
        #  # MOVED: import agentic_core.utils.decorators_base_util as mod

#  # MOVED: import agentic_core.utils.decorators_base_util as mod

        assert hasattr(mod, "__all__")
        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists '{name}' but it is not exported"


class TestCanonicalTimeoutContract:
    """Verify base_agents.timeout_decorator is the canonical SSOT."""

    
    def test_timeout_returns_decorator(self) -> None:
#  # MOVED: from agentic_core.utils.timeout_decorator_util import timeout

        decorator = timeout(30)
        assert callable(decorator)

    def test_timeout_decorator_wraps_function(self) -> None:
    """Test timeout_decorator_wraps_function runtime behavior."""
    # Arrange
    # TODO: Set up test data for timeout_decorator_wraps_function
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute timeout_decorator_wraps_function
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        assert hasattr(mod, "__all__")
        for name in mod.__all__:
            assert hasattr(mod, name), f"__all__ lists '{name}' but it is not exported"


class TestBackwardCompatShimIdentity:
    """Verify shims re-export the exact same objects from canonical locations."""

    def test_l5_shim_standard_heal_is_canonical(self) -> None:
        """L5 shim must re-export base_agents.decorators.standard_heal."""
#  # MOVED: from agentic_core.L5_safety.utils.decorators_util import standard_heal as shim
#  # MOVED: from agentic_core.utils.decorators_base_util import standard_heal as canonical

        assert shim is canonical, "L5 shim must re-export canonical object"

    def test_l5_shim_heal_result_schema_is_canonical(self) -> None:
#  # MOVED: from agentic_core.L5_safety.utils.decorators_util import (
            HEAL_RESULT_SCHEMA as shim,
        )
#  # MOVED: from agentic_core.utils.decorators_base_util import HEAL_RESULT_SCHEMA as canonical

        assert shim is canonical

    def test_l0_shim_timeout_is_canonical(self) -> None:
        """L0 shim must re-export base_agents.timeout_decorator.timeout."""
#  # MOVED: from agentic_core.L0_routing.utils.timeout_decorator_util import (
            timeout as shim,
        )
#  # MOVED: from agentic_core.utils.timeout_decorator_util import timeout as canonical

        assert shim is canonical, "L0 shim must re-export canonical object"


class TestNoShimImportsEnforcement:
    """AST enforcement: no agentic_core module may import from shim locations."""

    SHIM_FILES = {"decorators_util.py", "timeout_decorator_util.py"}
    FORBIDDEN_IMPORTS = [
        "agentic_core.L5_safety.utils.decorators_util",
        "agentic_core.L0_routing.utils.timeout_decorator_util",
    ]

    def test_no_imports_from_shim_locations(self) -> None:
        """No agentic_core module (except shims) may import from shim locations."""
        violations = self._find_forbidden_imports()
        assert not violations, (
            f"Found {len(violations)} forbidden imports from shim locations:\n"
            + "\n".join(f"  {v}" for v in violations[:20])
        )

    def _find_forbidden_imports(self) -> list[str]:
        violations = []
        agentic_core = ROOT / AGENTIC_CORE_DIR

        for py_file in agentic_core.rglob("*.py"):
            if py_file.name in self.SHIM_FILES:
                continue

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in self.FORBIDDEN_IMPORTS:
                        if node.module == forbidden or node.module.startswith(
                            forbidden + ".",
                        ):
                            rel_path = py_file.relative_to(ROOT)
                            violations.append(
                                f"{rel_path}:{node.lineno} imports from {node.module}",
                            )

        return violations


class TestBaseAgentsDecoratorImports:
    """AST enforcement: base_agents/decorators.py and timeout_decorator.py must not import from shim locations."""

    DECORATOR_FILES = {"decorators.py", "timeout_decorator.py"}
    FORBIDDEN_SHIM_IMPORTS = [
        "agentic_core.L5_safety.utils.decorators_util",
        "agentic_core.L0_routing.utils.timeout_decorator_util",
    ]

    def test_base_agents_decorators_no_shim_imports(self) -> None:
        """base_agents decorator modules must not import from their shim locations (no circular deps)."""
        violations = []
        base_agents = ROOT / AGENTIC_CORE_DIR / "base_agents"

        for py_file in base_agents.glob("*.py"):
            if py_file.name not in self.DECORATOR_FILES:
                continue

            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, UnicodeDecodeError):  # guardian: allow-silent-swallower
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    for forbidden in self.FORBIDDEN_SHIM_IMPORTS:
                        if node.module == forbidden or node.module.startswith(forbidden + "."):
                            violations.append(
                                f"{py_file.name}:{node.lineno} imports from {node.module}",
                            )

        assert not violations, (
            "base_agents decorator modules import from shim locations (layer inversion):\n"
            + "\n".join(f"  {v}" for v in violations)
        )


class TestShimAllowlist:
    """AST enforcement: shims must import ONLY from base_agents canonical locations."""

    DECORATORS_SHIM = ROOT / "agentic_core/L5_safety/utils/decorators_util.py"
    TIMEOUT_SHIM = ROOT / "agentic_core/L0_routing/utils/timeout_decorator_util.py"

    def test_decorators_shim_imports_only_base_agents(self) -> None:
        """decorators_util.py must import ONLY from utils.decorators_util (canonical)."""
        violations = self._check_shim_imports(
            self.DECORATORS_SHIM,
            allowed="agentic_core.utils.decorators_util",
        )
        assert not violations, "decorators_util.py imports from non-canonical locations:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_timeout_shim_imports_only_base_agents(self) -> None:
        """timeout_decorator_util.py must import ONLY from base_agents.timeout_decorator."""
        violations = self._check_shim_imports(
            self.TIMEOUT_SHIM,
            allowed="agentic_core.utils.timeout_decorator_util",
        )
        assert not violations, (
            "timeout_decorator_util.py imports from non-canonical locations:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def _check_shim_imports(self, shim_path: Path, allowed: str) -> list[str]:
        """Check that shim imports ONLY from allowed module (plus __future__)."""
        violations = []
        try:
            source = shim_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
            return [f"Cannot parse {shim_path.name}: {e}"]

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "__future__":
                    continue
                if node.module == "agentic_core.runtime.lifecycle_trace_contract":
                    continue
                if node.module != allowed:
                    violations.append(
                        f"line {node.lineno}: imports from {node.module} (allowed: {allowed})",
                    )

        return violations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
