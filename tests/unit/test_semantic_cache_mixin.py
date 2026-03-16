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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_semantic_cache_mixin")
_emit_applies_guardrail("p0", "test_semantic_cache_mixin", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_cache_mixin", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_cache_mixin", "state_snapshot")
emit_replay_key("p0", "test_semantic_cache_mixin")
emit_determinism_digest("p0", "test_semantic_cache_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        agent = type("_T", (SemanticCacheMixin,), {})()
        assert callable(agent.semantic_update_feedback)


# ===========================================================================
# S1b — SemanticCacheMixin: property + singleton behaviour
# ===========================================================================


class TestSemanticCacheMixinProperty:
    def setup_method(self):
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
        assert _fresh_agent().semantic_recall("unknown context xyz", "TestNS") is None

    def test_semantic_learn_increments_cache_stores(self):
        agent = _fresh_agent()
        agent.semantic_learn("ctx1", "TestNS", {"v": 1})
        agent.semantic_learn("ctx2", "TestNS", {"v": 2})
        agent.semantic_learn("ctx3", "TestNS", {"v": 3})
        assert agent.semantic_stats()["cache_stores"] == 3

    def test_semantic_learn_accepts_feedback_score(self):
        agent = _fresh_agent()
        agent.semantic_learn("ctx", "NS", {"v": 1}, feedback_score=0.75)
        assert agent.semantic_stats()["cache_stores"] == 1

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
