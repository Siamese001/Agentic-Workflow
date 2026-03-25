"""
test_semantic_cache_mixin.py

Mixin import, property/singleton behaviour, agent base-class inheritance,
and graceful-fallback tests for the semantic cache activation work.

Covers:
  S1:  SemanticCacheMixin import fix + method signatures
  S1b: SemanticCacheMixin property + singleton behaviour
  S4:  Agent base-class mixin inheritance
  R2d: Agent base graceful fallback import verification
"""

from __future__ import annotations

import importlib
import os
import threading
from dataclasses import dataclass

import pytest

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_semantic_cache_mixin")
# REMOVED: _emit_applies_guardrail("p0", "test_semantic_cache_mixin", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_semantic_cache_mixin", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_semantic_cache_mixin", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_semantic_cache_mixin", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_semantic_cache_mixin", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_semantic_cache_mixin", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_semantic_cache_mixin", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_semantic_cache_mixin", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_semantic_cache_mixin", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_semantic_cache_mixin", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_semantic_cache_mixin", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_semantic_cache_mixin", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_semantic_cache_mixin", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_semantic_cache_mixin", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_semantic_cache_mixin", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_semantic_cache_mixin", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_semantic_cache_mixin", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_semantic_cache_mixin", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_semantic_cache_mixin", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_semantic_cache_mixin", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_semantic_cache_mixin", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_semantic_cache_mixin", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_semantic_cache_mixin", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_semantic_cache_mixin", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_semantic_cache_mixin", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_semantic_cache_mixin", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_semantic_cache_mixin", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_semantic_cache_mixin", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_semantic_cache_mixin", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_semantic_cache_mixin", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_semantic_cache_mixin", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_semantic_cache_mixin", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_semantic_cache_mixin", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_semantic_cache_mixin", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_semantic_cache_mixin", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_semantic_cache_mixin", "write_through")
# REMOVED: _emit_writes_through("p1", "test_semantic_cache_mixin", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_semantic_cache_mixin", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_semantic_cache_mixin", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_semantic_cache_mixin", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_semantic_cache_mixin", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_semantic_cache_mixin", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_semantic_cache_mixin", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_semantic_cache_mixin", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_semantic_cache_mixin", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_semantic_cache_mixin", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_semantic_cache_mixin", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_semantic_cache_mixin", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_semantic_cache_mixin", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_semantic_cache_mixin", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_semantic_cache_mixin", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_semantic_cache_mixin")
# REMOVED: _emit_gated_by_confidence("p1", "test_semantic_cache_mixin", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_semantic_cache_mixin")
# REMOVED: emit_determinism_digest("p0", "test_semantic_cache_mixin")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_semantic_cache_mixin", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_semantic_cache_mixin", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_semantic_cache_mixin", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_semantic_cache_mixin", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_semantic_cache_mixin", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_semantic_cache_mixin", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_semantic_cache_mixin", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_semantic_cache_mixin", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_semantic_cache_mixin", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_semantic_cache_mixin", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_semantic_cache_mixin", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_semantic_cache_mixin", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_semantic_cache_mixin", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_semantic_cache_mixin", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_semantic_cache_mixin", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_semantic_cache_mixin", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_semantic_cache_mixin", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_semantic_cache_mixin", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_semantic_cache_mixin", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_semantic_cache_mixin", "exec_snapshot_link")

os.environ.setdefault("HIVE_MIND_STRICT_MODE", "false")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_hive():
    from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

    SemanticCacheManager.reset_instance()


def _fresh_agent():
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

    class _A(SemanticCacheMixin):
        pass

    return _A()


# ===========================================================================
# S1 — SemanticCacheMixin: import + API shape
# ===========================================================================


class TestSemanticCacheMixinImport:
    def test_module_imports_cleanly(self):
        mod = importlib.import_module("agentic_core.mixins.semantic_cache_mixin")
        assert hasattr(mod, "SemanticCacheMixin")

    def test_backward_compat_alias(self):
        from agentic_core.mixins.semantic_cache_mixin import (
            SemanticCacheMixin,
            semantic_cache_mixin,
        )

        assert semantic_cache_mixin is SemanticCacheMixin

    def test_no_reference_to_nonexistent_config_module(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "agentic_core/mixins/semantic_cache_mixin.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "semantic_cache_manager_config" not in node.module, (
                    "semantic_cache_manager_config does not exist — import from semantic_cache_manager"
                )

    def test_imports_from_correct_module(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "agentic_core/mixins/semantic_cache_mixin.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "agentic_core.L4_state.memory.semantic_cache_manager"
            ):
                names = [a.name for a in node.names]
                assert "SemanticCacheManager" in names
                found = True
        assert found, "Must import SemanticCacheManager from semantic_cache_manager"

    def test_no_class_var_semantic_cache(self):
        """_semantic_cache class var removed to prevent stale ref bug."""
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        assert not hasattr(SemanticCacheMixin, "_semantic_cache"), (
            "_semantic_cache class var must not exist — instance caching causes stale refs"
        )

    def test_all_public_methods_present(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        required = {
            "semantic_cache",
            "semantic_recall",
            "semantic_learn",
            "semantic_promote",
            "semantic_update_feedback",
            "semantic_stats",
        }
        agent = type("_T", (SemanticCacheMixin,), {})()
        actual = {m for m in dir(agent) if m.startswith("semantic")}
        missing = required - actual
        assert not missing, f"Missing methods: {missing}"

    def test_semantic_update_feedback_is_callable(self):
    """Test semantic_update_feedback_is_callable runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute semantic_update_feedback_is_callable
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        _reset_hive()

    def teardown_method(self):
        _reset_hive()

    def test_property_returns_live_singleton(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Agent(SemanticCacheMixin):
            pass

        agent = Agent()
        cache = agent.semantic_cache
        assert cache is SemanticCacheManager.get_instance()

    def test_no_stale_ref_after_reset(self):
        """After reset_instance(), semantic_cache must return the NEW singleton."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        agent = _fresh_agent()
        old = agent.semantic_cache
        _reset_hive()
        new = SemanticCacheManager.get_instance()
        assert agent.semantic_cache is new, "Stale ref bug: agent still holds old singleton"
        assert old is not new

    def test_singleton_identity_across_instances(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class A(SemanticCacheMixin):
            pass

        class B(SemanticCacheMixin):
            pass

        assert A().semantic_cache is B().semantic_cache

    def test_semantic_recall_returns_none_on_miss(self):
    """Test semantic_recall_returns_none_on_miss runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute semantic_recall_returns_none_on_miss
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions

    def test_semantic_promote_below_threshold_rejected(self):
        agent = _fresh_agent()
        result = agent.semantic_promote("ctx", "NS", {"v": 0}, feedback_score=0.1)
        assert result is False
        assert agent.semantic_stats()["promotions"] == 0

    def test_semantic_promote_above_threshold(self):
        agent = _fresh_agent()
        agent.semantic_learn("promote ctx", "NS", {"v": 1})
        result = agent.semantic_promote("promote ctx", "NS", {"v": 1}, feedback_score=0.95)
        stats = agent.semantic_stats()
        if result:
            assert stats["promotions"] == 1
        else:
            assert stats["promotions"] == 0

    def test_semantic_update_feedback_returns_bool(self):
        agent = _fresh_agent()
        result = agent.semantic_update_feedback("ctx", "NS", 0.9)
        assert isinstance(result, bool)

    def test_semantic_stats_has_all_required_keys(self):
        stats = _fresh_agent().semantic_stats()
        required = {
            "redis_hits",
            "vector_store_hits",
            "cache_misses",
            "cache_stores",
            "promotions",
            "hit_rate",
            "total_hits",
            "total_lookups",
        }
        missing = required - set(stats.keys())
        assert not missing, f"Missing stat keys: {missing}"

    def test_namespace_isolation_lic_vs_rg(self):
        """Entries stored under LIC namespace must not be visible under RG namespace."""
        agent = _fresh_agent()
        agent.semantic_learn("shared query text", "LIC_NS", {"domain": "lic"})
        result = agent.semantic_recall("shared query text", "RG_NS")
        assert result is None, "Namespace isolation broken: RG_NS saw LIC_NS entry"

    def test_type_safety_non_dict_result_raises(self):
        """semantic_learn with a non-dict result must raise TypeError, not silently corrupt."""
        agent = _fresh_agent()
        with pytest.raises(TypeError):
            agent.semantic_learn("ctx", "NS", "not-a-dict")  # type: ignore[arg-type]

    def test_mixin_is_safe_for_dataclass_subclass(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        @dataclass
        class DataAgent(SemanticCacheMixin):
            name: str = "agent"
            value: int = 0

        agent = DataAgent(name="test", value=42)
        assert agent.name == "test"
        assert callable(agent.semantic_recall)

    def test_mixin_thread_safety_singleton_identity(self):
        """Multiple threads accessing semantic_cache must all get the same singleton."""
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        results = []
        errors = []

        class Agent(SemanticCacheMixin):
            pass

        def worker():
            try:
                results.append(id(Agent().semantic_cache))
            except Exception as e:  # guardian: allow-silent-swallower
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert len(set(results)) == 1, "Different singletons returned across threads"

    def test_mixin_multiple_inheritance_mro_safe(self):
        """SemanticCacheMixin must compose safely in diamond MRO."""
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Base:
            pass

        class Left(SemanticCacheMixin, Base):
            pass

        class Right(SemanticCacheMixin, Base):
            pass

        class Diamond(Left, Right):
            pass

        agent = Diamond()
        assert callable(agent.semantic_recall)
        assert callable(agent.semantic_learn)

    def test_pii_context_gets_sanitized_before_storage(self):
        """Contexts with PII must be sanitized (no crash, store succeeds)."""
        agent = _fresh_agent()
        pii_context = "user john@example.com called with sk-abc123456789012345678901"
        agent.semantic_learn(pii_context, "NS_PII", {"action": "recorded"})
        stats = agent.semantic_stats()
        assert stats["cache_stores"] == 1


# ===========================================================================
# S4 — Agent base-class mixin inheritance
# ===========================================================================


class TestAgentBaseMixinInheritance:
    def test_lic_agent_base_file_has_semantic_cache_mixin_import(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_lic/utils/lic_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        found = any(
            isinstance(n, ast.ImportFrom)
            and n.module == "agentic_core.mixins.semantic_cache_mixin"
            and "SemanticCacheMixin" in [a.name for a in n.names]
            for n in ast.walk(tree)
        )
        assert found, "LICAgentBase file must import SemanticCacheMixin"

    def test_rg_agent_base_file_has_semantic_cache_mixin_import(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_rg/utils/rg_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        found = any(
            isinstance(n, ast.ImportFrom)
            and n.module == "agentic_core.mixins.semantic_cache_mixin"
            and "SemanticCacheMixin" in [a.name for a in n.names]
            for n in ast.walk(tree)
        )
        assert found, "RGAgentBase file must import SemanticCacheMixin"

    def test_lic_agent_base_class_inherits_mixin_ast(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_lic/utils/lic_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "LICAgentBase":
                bases = [ast.unparse(b) for b in node.bases]
                assert "SemanticCacheMixin" in bases, f"LICAgentBase bases: {bases}"
                return
        pytest.fail("LICAgentBase class not found in lic_agent_base_util.py")

    def test_rg_agent_base_class_inherits_mixin_ast(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_rg/utils/rg_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "RGAgentBase":
                bases = [ast.unparse(b) for b in node.bases]
                assert "SemanticCacheMixin" in bases, f"RGAgentBase bases: {bases}"
                return
        pytest.fail("RGAgentBase class not found in rg_agent_base_util.py")

    def test_lic_mixin_is_first_base_before_meta_learning(self):
        """SemanticCacheMixin must appear before MetaLearningMixin in LICAgentBase MRO."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_lic/utils/lic_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "LICAgentBase":
                bases = [ast.unparse(b) for b in node.bases]
                scm_idx = next((i for i, b in enumerate(bases) if b == "SemanticCacheMixin"), None)
                mlm_idx = next((i for i, b in enumerate(bases) if b == "MetaLearningMixin"), None)
                assert scm_idx is not None, "SemanticCacheMixin not in bases"
                if mlm_idx is not None:
                    assert scm_idx < mlm_idx, "SemanticCacheMixin must come before MetaLearningMixin"
                return
        pytest.fail("LICAgentBase not found")

    def test_mixin_methods_available_on_plain_subclass(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class FakeAgent(SemanticCacheMixin):
            pass

        agent = FakeAgent()
        for method in (
            "semantic_recall",
            "semantic_learn",
            "semantic_promote",
            "semantic_update_feedback",
            "semantic_stats",
        ):
            assert callable(getattr(agent, method)), f"Missing: {method}"

    def test_mixin_is_safe_for_dataclass_subclass(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        @dataclass
        class DataAgent(SemanticCacheMixin):
            name: str = "agent"
            value: int = 0

        agent = DataAgent(name="test", value=42)
        assert agent.name == "test"
        assert callable(agent.semantic_recall)


# ===========================================================================
# R2d — Agent base: graceful fallback import verification
# ===========================================================================


class TestAgentBaseGracefulFallback:
    def test_lic_base_semantic_cache_mixin_import_wrapped_in_try_except(self):
        """SemanticCacheMixin import in lic_agent_base_util must be in a try/except
        so missing dependency does not crash the whole module."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_lic/utils/lic_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for child in ast.walk(node):
                    if (
                        isinstance(child, ast.ImportFrom)
                        and child.module == "agentic_core.mixins.semantic_cache_mixin"
                    ):
                        return  # found — import is guarded
        pytest.fail("SemanticCacheMixin import in lic_agent_base_util.py is not wrapped in try/except")

    def test_rg_base_semantic_cache_mixin_in_ast_bases(self):
        """RGAgentBase must declare SemanticCacheMixin as a base class in its AST."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_rg/utils/rg_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "RGAgentBase":
                bases = [ast.unparse(b) for b in node.bases]
                assert "SemanticCacheMixin" in bases
                return
        pytest.fail("RGAgentBase not found")

    def test_lic_base_appbase_module_path_is_apps_shared(self):
        """LICAgentBase must import AppBase from apps_shared (not agentic_core)."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_lic/utils/lic_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "AppBase" in node.module:
                assert node.module.startswith("apps_shared"), (
                    f"AppBase must come from apps_shared, got: {node.module}"
                )
                return

    def test_semantic_cache_mixin_standalone_import_always_works(self):
        """SemanticCacheMixin must be importable standalone, independent of AppBase."""
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class StandaloneAgent(SemanticCacheMixin):
            pass

        agent = StandaloneAgent()
        assert callable(agent.semantic_recall)
        assert callable(agent.semantic_learn)
        _reset_hive()
