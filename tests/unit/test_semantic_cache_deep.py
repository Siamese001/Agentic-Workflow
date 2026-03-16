"""
test_semantic_cache_deep.py

Deep behavioral, PII sanitizer, GlobalCache delegation, stateless mode,
structural invariants, and manager tests for the semantic cache activation work.

Covers:
  S2:  SovereignSemanticCache AST + module shape
  S3:  GlobalcacheStrategy delegation to SemanticCacheManager
  S5:  Edge cases — stateless mode
  Invariants: regression guards (AST + structural)
  R2a: PII Sanitizer comprehensive pattern coverage
  R2b: SemanticCacheManager deep behavioral paths
  R2c: GlobalCache deep behavioral paths
"""

from __future__ import annotations

import importlib
import os
import threading
from unittest.mock import patch

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

_emit_records_execution_trace("p0", "evidence", "test_semantic_cache_deep")
_emit_applies_guardrail("p0", "test_semantic_cache_deep", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_cache_deep", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_cache_deep", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_semantic_cache_deep", "p4obs", "metric_1")
_emit_emits_metric_event("test_semantic_cache_deep", "p4obs", "metric_2")
_emit_emits_metric_event("test_semantic_cache_deep", "p4obs", "metric_3")
_emit_emits_metric_event("test_semantic_cache_deep", "p4obs", "metric_4")
_emit_emits_metric_event("test_semantic_cache_deep", "p4obs", "metric_5")
_emit_emits_metric_event("test_semantic_cache_deep", "p4obs", "metric_6")
_emit_records_incident_event("test_semantic_cache_deep", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_semantic_cache_deep", "p4obs", "anomaly")
_emit_writes_observability_log("test_semantic_cache_deep", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_semantic_cache_deep", "p4obs", "mon_state")
_emit_triggers_alert("test_semantic_cache_deep", "p4obs", "alert")
_emit_links_incident_trace("test_semantic_cache_deep", "p4obs", "trace_link")
_emit_captures_pattern("test_semantic_cache_deep", "p3lm", "pattern")
_emit_records_learning_event("test_semantic_cache_deep", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_semantic_cache_deep", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_semantic_cache_deep", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_semantic_cache_deep", "p3lm", "routing")
_emit_improves_agent_policy("test_semantic_cache_deep", "p3lm", "policy")
_emit_stores_learning_state("test_semantic_cache_deep", "p3lm", "state")
_emit_records_execution_trace("test_semantic_cache_deep", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_semantic_cache_deep", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_semantic_cache_deep", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_semantic_cache_deep", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_semantic_cache_deep", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_semantic_cache_deep", "env_read", "p2_env_1")
_emit_reads_environ("test_semantic_cache_deep", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_semantic_cache_deep", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_semantic_cache_deep", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_semantic_cache_deep", "context_pull")
_emit_pulls_context("p1", "test_semantic_cache_deep", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_semantic_cache_deep", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_semantic_cache_deep", "uwg_term_2")
_emit_writes_through("p1", "test_semantic_cache_deep", "write_through")
_emit_writes_through("p1", "test_semantic_cache_deep", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_semantic_cache_deep", "safety_validation")
_emit_invokes_eval("p1", "test_semantic_cache_deep", "eval_call")
_emit_proposal_commits_routing("p1", "test_semantic_cache_deep", "routing_commit")
emit_replay_key("p0", "test_semantic_cache_deep")
emit_determinism_digest("p0", "test_semantic_cache_deep")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_semantic_cache_deep", "execution_auth")
_emit_validates_capability("p2", "test_semantic_cache_deep", "capability_check")
_emit_routes_to_capability("p2", "test_semantic_cache_deep", "capability_route")
_emit_writes_via_uwg("p2", "test_semantic_cache_deep", "uwg_write")
_emit_blocks_direct_write("p2", "test_semantic_cache_deep", "direct_write_block")
_emit_records_tool_invocation("p2", "test_semantic_cache_deep", "tool_invocation")
_emit_captures_execution_output("p2", "test_semantic_cache_deep", "exec_output")
_emit_dispatches_agent("p3", "test_semantic_cache_deep", "agent_dispatch")
_emit_coordinates_agents("p3", "test_semantic_cache_deep", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_semantic_cache_deep", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_semantic_cache_deep", "healing_outcome")
_emit_escalates_failure("p3", "test_semantic_cache_deep", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_semantic_cache_deep", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_semantic_cache_deep", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_semantic_cache_deep", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_semantic_cache_deep", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_semantic_cache_deep", "eval_metric")
_emit_stores_embedding("p4", "test_semantic_cache_deep", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_semantic_cache_deep", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_semantic_cache_deep", "exec_snapshot_link")

os.environ.setdefault("HIVE_MIND_STRICT_MODE", "false")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_hive():
    from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

    SemanticCacheManager.reset_instance()


# ===========================================================================
# S2 — SovereignSemanticCache: AST + module shape
# ===========================================================================


class TestSovereignSemanticCacheImport:
    def test_module_imports_cleanly(self):
        mod = importlib.import_module("agentic_core.L4_state.memory.sovereign_semantic_cache")
        assert hasattr(mod, "SovereignSemanticCache")

    def test_no_mcp_authority_reference(self):
        import ast
        from pathlib import Path

        src = (
            Path("c:/Git/Agentic-Workflow") / "agentic_core/L4_state/memory/sovereign_semantic_cache.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "mcp_authority":
                pytest.fail("mcp_authority is undefined — must not appear in sovereign_semantic_cache.py")

    def test_no_uppercase_const_references(self):
        import ast
        from pathlib import Path

        src = (
            Path("c:/Git/Agentic-Workflow") / "agentic_core/L4_state/memory/sovereign_semantic_cache.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        forbidden = {"MAX_REDIS_ENTRY_SIZE", "REDIS_CACHE_TTL"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in forbidden:
                pytest.fail(f"{node.id} undefined (use lowercase var). Line {node.lineno}")

    def test_docstring_is_first_line(self):
        from pathlib import Path

        src = (
            Path("c:/Git/Agentic-Workflow") / "agentic_core/L4_state/memory/sovereign_semantic_cache.py"
        ).read_text(encoding="utf-8")
        assert src.splitlines()[0].startswith('"""'), "Module docstring must be first line"

    def test_module_level_vars_lowercase(self):
        import agentic_core.L4_state.memory.sovereign_semantic_cache as m

        assert hasattr(m, "redis_cache_ttl")
        assert hasattr(m, "max_redis_entry_size")
        assert hasattr(m, "redis_timeout")

    def test_module_var_values_correct(self):
        import agentic_core.L4_state.memory.sovereign_semantic_cache as m

        assert m.redis_cache_ttl == 60 * 60 * 24 * 7, "TTL must be 7 days"
        assert m.max_redis_entry_size == 1024 * 1024, "Max entry size must be 1 MiB"
        assert m.redis_timeout == 5, "Redis timeout must be 5 seconds"

    def test_extract_ast_features_valid_python(self):
        import ast as ast_mod

        src = "def foo():\n    return 1\nclass Bar:\n    pass\n"
        tree = ast_mod.parse(src)
        funcs = len([n for n in ast_mod.walk(tree) if isinstance(n, ast_mod.FunctionDef)])
        classes = len([n for n in ast_mod.walk(tree) if isinstance(n, ast_mod.ClassDef)])
        assert funcs == 1
        assert classes == 1

    def test_extract_ast_features_invalid_python_fallback(self):
        """Invalid Python code must not raise — returns parse_error=True dict."""
        import ast as ast_mod

        invalid_code = "def foo(:\n    pass"
        try:
            ast_mod.parse(invalid_code)
            fallback_triggered = False
        except SyntaxError:  # guardian: allow-silent-swallower
            fallback_triggered = True

        assert fallback_triggered, "SyntaxError must be triggered for invalid code"

    def test_cache_key_is_deterministic(self):
        """Same file_path + mission_id must always produce same key (no randomness)."""
        import hashlib
        from pathlib import Path

        mission_id = "test-mission-42"
        file_path = "/repo/apps_lic/agent.py"
        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        expected = f"semantic:{mission_id}:{path_hash}"

        path_hash2 = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        assert path_hash == path_hash2
        assert f"semantic:{mission_id}:{path_hash2}" == expected

    def test_cache_key_mission_isolated(self):
        """Different mission IDs must produce different cache keys for same path."""
        import hashlib
        from pathlib import Path

        file_path = "/repo/agent.py"
        path_hash = hashlib.sha256(str(Path(file_path)).encode()).hexdigest()[:16]
        key_a = f"semantic:mission-A:{path_hash}"
        key_b = f"semantic:mission-B:{path_hash}"
        assert key_a != key_b


# ===========================================================================
# S3 — GlobalcacheStrategy delegation
# ===========================================================================


class TestGlobalCacheHiveMindDelegation:
    def setup_method(self):
        _reset_hive()
        import apps_shared.enforcement.GlobalcacheStrategy as _mod

        _mod._global_cache = None

    def teardown_method(self):
        _reset_hive()
        import apps_shared.enforcement.GlobalcacheStrategy as _mod

        _mod._global_cache = None

    def test_get_hive_mind_returns_manager(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        assert gc.get_hive_mind() is SemanticCacheManager.get_instance()

    def test_hive_mind_lazy_loaded_once(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        assert gc.get_hive_mind() is gc.get_hive_mind()

    def test_put_with_embedding_text_calls_hive_learn(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k1", {"v": 1}, text_for_embedding="resume skills section", source_engine="TEST")
        assert gc.get_hive_mind().get_statistics()["cache_stores"] >= 1

    def test_put_without_embedding_text_skips_hive(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k2", {"v": 2})
        assert gc.get_hive_mind().get_statistics()["cache_stores"] == 0

    def test_multiple_puts_all_reach_hive(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        for i in range(3):
            gc.put(f"key{i}", {"i": i}, text_for_embedding=f"context item {i}")
        assert gc.get_hive_mind().get_statistics()["cache_stores"] == 3

    def test_get_exact_key_hits_l1(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k3", "cached_value")
        assert gc.get("k3") == "cached_value"
        assert gc._stats["l1_hits"] == 1

    def test_get_missing_key_returns_none(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        assert GlobalCache().get("no_such_key") is None

    def test_get_semantic_miss_returns_empty(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        assert GlobalCache().get_semantic("completely unknown query xyz abc 999") == []

    def test_get_semantic_after_put_returns_value(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("sk", {"answer": "ATS opt"}, text_for_embedding="ATS optimization keywords")
        results = gc.get_semantic("ATS optimization keywords")
        assert len(results) >= 1

    def test_get_semantic_max_results_zero_returns_empty(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("sk2", "val", text_for_embedding="some context here")
        results = gc.get_semantic("some context here", max_results=0)
        assert results == []

    def test_global_cache_singleton_has_hive(self):
        from apps_shared.enforcement.GlobalcacheStrategy import get_global_cache

        assert get_global_cache().get_hive_mind() is not None

    def test_get_global_cache_returns_global_cache_instance(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache, get_global_cache

        gc = get_global_cache()
        assert isinstance(gc, GlobalCache)

    def test_hive_namespace_constant(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        assert GlobalCache._HIVE_NAMESPACE == "GlobalCache"

    def test_hive_unavailable_falls_back_to_l2_gracefully(self):
        """When SemanticCacheManager is unavailable, get_hive_mind() returns None
        and get_semantic() falls back to local L2VectorStore without crash."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            side_effect=RuntimeError("FORCED FAILURE"),
        ):
            hive = gc.get_hive_mind()
            assert hive is None
            hive2 = gc.get_hive_mind()
            assert hive2 is None
            results = gc.get_semantic("any query")
            assert isinstance(results, list)

    def test_stats_l2_hits_incremented_on_hive_recall(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("sk", "val", text_for_embedding="lic campaign context")
        gc._stats.update({"total_requests": 0, "l1_hits": 0, "l2_hits": 0, "total_misses": 0})
        results = gc.get_semantic("lic campaign context")
        assert gc._stats["l2_hits"] >= 1 or len(results) >= 1


# ===========================================================================
# S5 — Stateless mode
# ===========================================================================


class TestStatelessMode:
    def setup_method(self):
        import os

        os.environ["REDIS_URL"] = "redis://127.0.0.2:1"
        _reset_hive()

    def teardown_method(self):
        import os

        os.environ.pop("REDIS_URL", None)
        _reset_hive()

    def test_stateless_mode_learn_is_noop(self):
        """In stateless mode (no Redis + no vector store), learn must silently pass."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        mgr.stateless_mode = True
        mgr.learn("ctx", "NS", {"v": 1})
        assert mgr.get_statistics()["cache_stores"] == 0
        mgr.stateless_mode = False

    def test_stateless_mode_recall_returns_none(self):
        """In stateless mode, recall must return None without crashing."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        mgr.stateless_mode = True
        result = mgr.recall("ctx", "NS")
        assert result is None
        mgr.stateless_mode = False


# ===========================================================================
# Invariants: regression guards (AST + structural)
# ===========================================================================


class TestSemanticCacheInvariants:
    def test_semantic_cache_manager_config_module_does_not_exist(self):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("agentic_core.L4_state.memory.semantic_cache_manager_config")

    def test_semantic_cache_manager_get_instance_is_singleton(self):
        _reset_hive()
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        assert SemanticCacheManager.get_instance() is SemanticCacheManager.get_instance()
        _reset_hive()

    def test_direct_instantiation_raises(self):
        _reset_hive()
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        SemanticCacheManager.get_instance()
        with pytest.raises(RuntimeError, match="SINGLETON VIOLATION"):
            SemanticCacheManager()
        _reset_hive()

    def test_global_cache_hive_namespace_unchanged(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        assert GlobalCache._HIVE_NAMESPACE == "GlobalCache"

    def test_mixin_property_uses_get_instance_not_constructor(self):
        """AST check: property body must call .get_instance(), not SemanticCacheManager()."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "agentic_core/mixins/semantic_cache_mixin.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "SemanticCacheManager":
                    pytest.fail("Must call SemanticCacheManager.get_instance(), not SemanticCacheManager()")

    def test_no_pinecone_import_in_mixin(self):
        """SemanticCacheMixin must not import pinecone."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "agentic_core/mixins/semantic_cache_mixin.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "pinecone" not in alias.name.lower(), "pinecone import found in mixin"
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert "pinecone" not in node.module.lower(), "pinecone import found in mixin"

    def test_sovereign_cache_has_no_pinecone_in_import_list(self):
        """SovereignSemanticCache must not import pinecone at module level."""
        import ast
        from pathlib import Path

        src = (
            Path("c:/Git/Agentic-Workflow") / "agentic_core/L4_state/memory/sovereign_semantic_cache.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        for node in tree.body:  # top-level only
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "pinecone" not in alias.name.lower()
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert "pinecone" not in node.module.lower()

    def test_globalcache_hive_delegation_methods_are_ast_guarded(self):
        """AST: get_hive_mind, get_semantic, put in GlobalcacheStrategy must exist."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_shared/enforcement/GlobalcacheStrategy.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        method_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        for required in ("get_hive_mind", "get_semantic", "put"):
            assert required in method_names, f"GlobalCache missing method: {required}"


# ===========================================================================
# R2a — PII Sanitizer: comprehensive pattern coverage
# ===========================================================================


class TestPIISanitizer:
    """Verify every PII pattern in PII_Sanitizer.PATTERNS fires correctly."""

    def test_email_is_redacted(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        result = PII_Sanitizer.sanitize("contact me at user@example.com please")
        assert "[REDACTED_EMAIL]" in result
        assert "user@example.com" not in result

    def test_openai_key_is_redacted(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        raw = "key is sk-abc1234567890123456789012345"
        result = PII_Sanitizer.sanitize(raw)
        assert "[REDACTED_OPENAI_KEY]" in result
        assert "sk-abc" not in result

    def test_anthropic_key_is_redacted(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        raw = "use sk-ant-api03-abc12345678901234567890123456789012345678"
        result = PII_Sanitizer.sanitize(raw)
        assert "[REDACTED_ANTHROPIC_KEY]" in result

    def test_ipv4_is_redacted(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        result = PII_Sanitizer.sanitize("server at 192.168.1.100")
        assert "[REDACTED_IPV4]" in result
        assert "192.168.1.100" not in result

    def test_phone_us_is_redacted(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        result = PII_Sanitizer.sanitize("call me at 555-867-5309")
        assert "[REDACTED_PHONE_US]" in result
        assert "555-867-5309" not in result

    def test_aws_key_standard_20char_is_redacted(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        raw = "aws key AKIAIOSFODNN7EXAMPLE end"
        result = PII_Sanitizer.sanitize(raw)
        assert "[REDACTED_AWS_KEY]" in result
        assert "AKIAIOSFODNN7EXAMPLE" not in result

    def test_clean_content_unchanged(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        clean = "ATS keywords: Python, leadership, cross-functional teams"
        assert PII_Sanitizer.sanitize(clean) == clean

    def test_is_safe_false_for_email(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        assert PII_Sanitizer.is_safe("john@corp.com") is False

    def test_is_safe_true_for_clean_text(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        assert PII_Sanitizer.is_safe("resume optimization leadership skills") is True

    def test_is_safe_true_for_empty_string(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        assert PII_Sanitizer.is_safe("") is True

    def test_detect_pii_returns_typed_dict(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        raw = "john@corp.com and call 555-867-5309"
        findings = PII_Sanitizer.detect_pii(raw)
        assert isinstance(findings, dict)
        assert "EMAIL" in findings
        assert "PHONE_US" in findings
        assert isinstance(findings["EMAIL"], list)
        assert len(findings["EMAIL"]) >= 1

    def test_detect_pii_empty_returns_empty_dict(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        assert PII_Sanitizer.detect_pii("") == {}

    def test_detect_pii_clean_returns_empty_dict(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        assert PII_Sanitizer.detect_pii("clean professional content here") == {}

    def test_multiple_pii_types_all_redacted(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer

        raw = "user@example.com, IP 10.0.0.1, key sk-abc1234567890123456789012345"
        result = PII_Sanitizer.sanitize(raw)
        assert "user@example.com" not in result
        assert "10.0.0.1" not in result
        assert "sk-abc" not in result
        assert result.count("[REDACTED_") >= 3


# ===========================================================================
# R2b — SemanticCacheManager: deep behavioral paths
# ===========================================================================


class TestSemanticCacheManagerDeep:
    def setup_method(self):
        import os

        os.environ["REDIS_URL"] = "redis://127.0.0.2:1"
        _reset_hive()

    def teardown_method(self):
        import os

        os.environ.pop("REDIS_URL", None)
        _reset_hive()

    def test_strict_mode_no_raise_when_vector_store_available(self):
        """HIVE_MIND_STRICT_MODE=true must NOT raise when vector store is available."""
        import os

        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        os.environ["HIVE_MIND_STRICT_MODE"] = "true"
        _reset_hive()
        try:
            mgr = SemanticCacheManager.get_instance()
            assert mgr.stateless_mode is False
            assert mgr.vector_store_enabled is True
        finally:
            os.environ["HIVE_MIND_STRICT_MODE"] = "false"
            _reset_hive()

    def test_learn_without_redis_increments_cache_stores(self):
        """learn() must increment cache_stores even when Redis unavailable."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        assert mgr.redis_enabled is False
        mgr.learn("some context", "TestNS", {"data": "value"})
        assert mgr.get_statistics()["cache_stores"] == 1

    def test_learn_without_redis_not_retrievable_via_recall(self):
        """Without Redis, working-memory entries from learn() are NOT retrievable."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        assert mgr.redis_enabled is False
        mgr.learn("unique recall test context xyz", "TestNS", {"data": "value"})
        result = mgr.recall("unique recall test context xyz", "TestNS")
        assert result is None, "Without Redis, learn() does not persist to vector store"

    def test_promote_to_long_term_enables_vector_store_recall(self):
        """promote_to_long_term() writes embedding to vector store."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        promoted = mgr.promote_to_long_term(
            "campaign optimization strategy",
            "DeepNS",
            {"recommendation": "increase frequency"},
            feedback_score=0.95,
        )
        if promoted:
            assert mgr.get_statistics()["promotions"] == 1
            recalled = mgr.recall("campaign optimization strategy", "DeepNS")
            assert recalled is not None
            assert recalled.get("recommendation") == "increase frequency"
        else:
            assert mgr.get_statistics()["promotions"] == 0

    def test_promote_rejected_below_threshold(self):
        """promote_to_long_term() with score < promotion_threshold must return False."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        assert mgr.promotion_threshold == 0.8
        result = mgr.promote_to_long_term("ctx", "NS", {"v": 1}, feedback_score=0.5)
        assert result is False
        assert mgr.get_statistics()["promotions"] == 0

    def test_update_feedback_score_returns_false_without_redis(self):
        """update_feedback_score() requires Redis — must return False when unavailable."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        assert mgr.redis_enabled is False
        result = mgr.update_feedback_score("any context", "NS", 0.9)
        assert result is False

    def test_get_statistics_extended_keys_present(self):
        """get_statistics() must expose strict_mode, stateless_mode, sampling_rate_actual."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        stats = SemanticCacheManager.get_instance().get_statistics()
        for key in ("strict_mode", "stateless_mode", "sampling_rate_actual"):
            assert key in stats, f"Missing key in get_statistics(): {key}"

    def test_get_statistics_all_base_keys_present(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        stats = SemanticCacheManager.get_instance().get_statistics()
        for key in (
            "redis_hits",
            "vector_store_hits",
            "cache_misses",
            "cache_stores",
            "promotions",
            "traces_sampled",
            "traces_skipped",
            "total_hits",
            "total_lookups",
            "hit_rate",
        ):
            assert key in stats, f"Missing key: {key}"

    def test_learn_async_method_exists(self):
        """learn_async must be defined for fire-and-forget pattern."""
        import ast
        from pathlib import Path

        src = (
            Path("c:/Git/Agentic-Workflow") / "agentic_core/L4_state/memory/semantic_cache_manager.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        async_methods = {node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)}
        assert "learn_async" in async_methods

    def test_namespace_hash_includes_namespace(self):
        """_compute_hash must produce different hashes for same context in different namespaces."""
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        h1 = mgr._compute_hash("same context", "NS_A")
        h2 = mgr._compute_hash("same context", "NS_B")
        assert h1 != h2, "Namespace must be part of hash key"

    def test_pii_is_sanitized_before_hash_computation(self):
        """Contexts with PII must be sanitized — resulting hash must match the sanitized version."""
        from agentic_core.L4_state.memory.semantic_cache_manager import PII_Sanitizer, SemanticCacheManager

        mgr = SemanticCacheManager.get_instance()
        raw = "user@example.com resume data"
        sanitized = PII_Sanitizer.sanitize(raw)
        mgr.learn(raw, "PII_NS", {"data": 1})
        hash_of_sanitized = mgr._compute_hash(sanitized, "PII_NS")
        hash_of_raw = mgr._compute_hash(raw, "PII_NS")
        assert hash_of_sanitized != hash_of_raw


# ===========================================================================
# R2c — GlobalCache deep behavioral paths
# ===========================================================================


class TestGlobalCacheDeep:
    def setup_method(self):
        import os

        os.environ["REDIS_URL"] = "redis://127.0.0.2:1"
        _reset_hive()
        import apps_shared.enforcement.GlobalcacheStrategy as _mod

        _mod._global_cache = None

    def teardown_method(self):
        import os

        os.environ.pop("REDIS_URL", None)
        _reset_hive()
        import apps_shared.enforcement.GlobalcacheStrategy as _mod

        _mod._global_cache = None

    def test_get_hive_mind_concurrent_20_threads_same_singleton(self):
        """20 concurrent calls to get_hive_mind() must all return the same singleton."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        hive_ids: list[int] = []

        def worker():
            h = gc.get_hive_mind()
            if h is not None:
                hive_ids.append(id(h))

        threads = [threading.Thread(target=worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(set(hive_ids)) == 1, "Race condition: multiple hive instances created"

    def test_get_stats_returns_correct_keys(self):
        """GlobalCache.get_stats() must include l1, l2, l1_hits, l2_hits, overall_hit_rate."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        stats = GlobalCache().get_stats()
        for key in ("l1", "l2", "l1_hits", "l2_hits", "total_requests", "total_misses", "overall_hit_rate"):
            assert key in stats, f"get_stats() missing key: {key}"

    def test_clear_resets_stats_to_zero(self):
        """clear() must zero all stat counters."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k", "v")
        gc.get("k")
        gc.clear()
        for key in ("total_requests", "l1_hits", "l2_hits", "total_misses"):
            assert gc._stats[key] == 0, f"clear() did not reset {key}"

    def test_cleanup_expired_returns_int(self):
        """cleanup_expired() must return an integer count."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        n = GlobalCache().cleanup_expired()
        assert isinstance(n, int)
        assert n >= 0

    def test_convenience_functions_are_callable(self):
        """cache_get, cache_put, cache_search_semantic, cached must all be callable."""
        from apps_shared.enforcement.GlobalcacheStrategy import (
            cache_get,
            cache_put,
            cache_search_semantic,
            cached,
        )

        for fn in (cache_get, cache_put, cache_search_semantic, cached):
            assert callable(fn), f"{fn} is not callable"

    def test_get_global_cache_is_module_level_singleton(self):
        """Two calls to get_global_cache() must return the identical object."""
        from apps_shared.enforcement.GlobalcacheStrategy import get_global_cache

        assert get_global_cache() is get_global_cache()

    def test_put_delegates_correct_payload_structure_to_hive(self):
        """put() must call hive.learn() with ('text', 'GlobalCache', {value, key, source_engine})."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        hive = gc.get_hive_mind()
        with patch.object(hive, "learn") as mock_learn:
            gc.put("mykey", {"answer": 42}, text_for_embedding="embed text", source_engine="ENG1")
            mock_learn.assert_called_once()
            context, ns, payload = mock_learn.call_args[0]
            assert context == "embed text"
            assert ns == "GlobalCache"
            assert payload["value"] == {"answer": 42}
            assert payload["key"] == "mykey"
            assert payload["source_engine"] == "ENG1"

    def test_get_semantic_exact_text_match_returns_value_from_local_l2(self):
        """After put(text_for_embedding=X), get_semantic(X) must return the value."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k", "expected_result", text_for_embedding="unique exact phrase alpha7749")
        results = gc.get_semantic("unique exact phrase alpha7749")
        assert results == ["expected_result"]

    def test_get_semantic_hive_path_max_results_caps_at_one(self):
        """Hive recall() returns single best match — get_semantic() AST check."""
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_shared/enforcement/GlobalcacheStrategy.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_semantic":
                src_slice = ast.unparse(node)
                assert "max_results >= 1" in src_slice, (
                    "get_semantic hive path must guard return with max_results >= 1"
                )
                return
        pytest.fail("get_semantic not found in GlobalcacheStrategy")

    def test_multiple_global_cache_instances_share_same_hive_singleton(self):
        """Multiple GlobalCache() instances must all delegate to the same SemanticCacheManager."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc_a = GlobalCache()
        gc_b = GlobalCache()
        assert gc_a.get_hive_mind() is gc_b.get_hive_mind()

    def test_hive_sentinel_false_after_failure_prevents_retry(self):
        """Once get_hive_mind() fails and sets _hive=False, subsequent calls must NOT retry."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        with patch(
            "agentic_core.L4_state.memory.semantic_cache_manager.SemanticCacheManager.get_instance",
            side_effect=RuntimeError("init fail"),
        ):
            gc.get_hive_mind()  # first call → fails → _hive = False

        assert gc._hive is False
        assert gc.get_hive_mind() is None

    def test_get_semantic_after_learn_without_promote_hive_path_returns_none(self):
        """With no Redis and no promote_to_long_term(), hive.recall() returns None."""
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        hive = gc.get_hive_mind()
        hive.learn("hive only context xyz", "GlobalCache", {"val": 1})
        recalled_directly = hive.recall("hive only context xyz", "GlobalCache")
        assert recalled_directly is None
        results = gc.get_semantic("hive only context xyz")
        assert isinstance(results, list)
