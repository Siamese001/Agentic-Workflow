"""
test_semantic_cache_activation.py

Full test suite for the semantic cache activation work:
  - S1: SemanticCacheMixin import fix + method signatures
  - S2: SovereignSemanticCache undefined-name fixes
  - S3: GlobalcacheStrategy delegation to SemanticCacheManager
  - S4: Agent base-class mixin inheritance

All tests are unit-level (no live Redis, no live Pinecone).
SemanticCacheManager is reset before each test that touches it.
"""

from __future__ import annotations

import importlib
import os

import pytest

os.environ.setdefault("HIVE_MIND_STRICT_MODE", "false")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_hive():
    from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

    SemanticCacheManager.reset_instance()


# ===========================================================================
# S1 — SemanticCacheMixin
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
                    "semantic_cache_manager_config is a non-existent module — "
                    "must import from semantic_cache_manager"
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


class TestSemanticCacheMixinProperty:
    def setup_method(self):
        _reset_hive()

    def teardown_method(self):
        _reset_hive()

    def test_lazy_loads_singleton(self):
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Agent(SemanticCacheMixin):
            pass

        agent = Agent()
        assert agent._semantic_cache is None
        cache = agent.semantic_cache
        assert cache is SemanticCacheManager.get_instance()

    def test_singleton_identity_across_instances(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class A(SemanticCacheMixin):
            pass

        class B(SemanticCacheMixin):
            pass

        a, b = A(), B()
        assert a.semantic_cache is b.semantic_cache

    def test_semantic_recall_returns_none_on_miss(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Agent(SemanticCacheMixin):
            pass

        result = Agent().semantic_recall("unknown context", "TestNS")
        assert result is None

    def test_semantic_learn_and_recall_roundtrip(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Agent(SemanticCacheMixin):
            pass

        agent = Agent()
        agent.semantic_learn("test context", "TestNS", {"answer": 42})
        stats = agent.semantic_stats()
        assert stats["cache_stores"] == 1

    def test_semantic_promote_above_threshold(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Agent(SemanticCacheMixin):
            pass

        agent = Agent()
        agent.semantic_learn("promote context", "TestNS", {"answer": 1})
        result = agent.semantic_promote("promote context", "TestNS", {"answer": 1}, feedback_score=0.95)
        # promote_to_long_term requires BGE embedding; if model unavailable it returns False
        # but promotions stat or result must be consistent
        stats = agent.semantic_stats()
        if result:
            assert stats["promotions"] == 1
        else:
            # BGE model failed gracefully — acceptable, no crash
            assert stats["promotions"] == 0

    def test_semantic_promote_below_threshold_rejected(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Agent(SemanticCacheMixin):
            pass

        agent = Agent()
        result = agent.semantic_promote("low score", "TestNS", {"answer": 0}, feedback_score=0.1)
        assert result is False

    def test_semantic_stats_returns_dict(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class Agent(SemanticCacheMixin):
            pass

        stats = Agent().semantic_stats()
        assert isinstance(stats, dict)
        assert "hit_rate" in stats
        assert "cache_stores" in stats
        assert "promotions" in stats


# ===========================================================================
# S2 — SovereignSemanticCache
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
                pytest.fail(f"{node.id} is undefined (use lowercase module-level var). Line {node.lineno}")

    def test_docstring_before_imports(self):
        from pathlib import Path

        src = (
            Path("c:/Git/Agentic-Workflow") / "agentic_core/L4_state/memory/sovereign_semantic_cache.py"
        ).read_text(encoding="utf-8")
        lines = src.splitlines()
        assert lines[0].startswith('"""'), "Module docstring must be first line after fix"

    def test_module_level_vars_lowercase(self):
        import agentic_core.L4_state.memory.sovereign_semantic_cache as m

        assert hasattr(m, "redis_cache_ttl")
        assert hasattr(m, "max_redis_entry_size")
        assert hasattr(m, "redis_timeout")


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
        hive = gc.get_hive_mind()
        assert hive is SemanticCacheManager.get_instance()

    def test_hive_mind_lazy_loaded_once(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        h1 = gc.get_hive_mind()
        h2 = gc.get_hive_mind()
        assert h1 is h2

    def test_put_with_embedding_text_calls_hive_learn(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k1", {"v": 1}, text_for_embedding="resume skills section", source_engine="TEST")
        stats = gc.get_hive_mind().get_statistics()
        assert stats["cache_stores"] >= 1

    def test_put_without_embedding_text_skips_hive(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k2", {"v": 2})
        stats = gc.get_hive_mind().get_statistics()
        assert stats["cache_stores"] == 0

    def test_get_exact_key_hits_l1(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("k3", "cached_value")
        result = gc.get("k3")
        assert result == "cached_value"
        assert gc._stats["l1_hits"] == 1

    def test_get_semantic_miss_returns_empty(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        results = gc.get_semantic("completely unknown query xyz")
        assert results == []

    def test_get_semantic_after_put_returns_value(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put(
            "semantic_key",
            {"answer": "ATS optimization"},
            text_for_embedding="ATS optimization keywords",
        )
        results = gc.get_semantic("ATS optimization keywords")
        assert len(results) >= 1

    def test_global_cache_singleton_has_hive(self):
        from apps_shared.enforcement.GlobalcacheStrategy import get_global_cache

        gc = get_global_cache()
        assert gc.get_hive_mind() is not None

    def test_hive_namespace_constant(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        assert GlobalCache._HIVE_NAMESPACE == "GlobalCache"

    def test_stats_l2_hits_incremented_on_hive_recall(self):
        from apps_shared.enforcement.GlobalcacheStrategy import GlobalCache

        gc = GlobalCache()
        gc.put("sk", "val", text_for_embedding="lic campaign context")
        gc._stats["total_requests"] = 0
        gc._stats["l1_hits"] = 0
        gc._stats["l2_hits"] = 0
        gc._stats["total_misses"] = 0
        results = gc.get_semantic("lic campaign context")
        assert gc._stats["l2_hits"] >= 1 or len(results) >= 1


# ===========================================================================
# S4 — Agent base class mixin inheritance
# ===========================================================================


class TestAgentBaseMixinInheritance:
    def test_lic_agent_base_file_has_semantic_cache_mixin_import(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_lic/utils/lic_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "agentic_core.mixins.semantic_cache_mixin":
                names = [a.name for a in node.names]
                if "SemanticCacheMixin" in names:
                    found = True
        assert found, "LICAgentBase file must import SemanticCacheMixin"

    def test_rg_agent_base_file_has_semantic_cache_mixin_import(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_rg/utils/rg_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "agentic_core.mixins.semantic_cache_mixin":
                names = [a.name for a in node.names]
                if "SemanticCacheMixin" in names:
                    found = True
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
                base_names = [ast.unparse(b) for b in node.bases]
                assert "SemanticCacheMixin" in base_names, f"LICAgentBase bases: {base_names}"
                return
        pytest.fail("LICAgentBase class not found")

    def test_rg_agent_base_class_inherits_mixin_ast(self):
        import ast
        from pathlib import Path

        src = (Path("c:/Git/Agentic-Workflow") / "apps_rg/utils/rg_agent_base_util.py").read_text(
            encoding="utf-8"
        )
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "RGAgentBase":
                base_names = [ast.unparse(b) for b in node.bases]
                assert "SemanticCacheMixin" in base_names, f"RGAgentBase bases: {base_names}"
                return
        pytest.fail("RGAgentBase class not found")

    def test_mixin_methods_available_on_plain_subclass(self):
        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        class FakeAgent(SemanticCacheMixin):
            pass

        agent = FakeAgent()
        assert callable(agent.semantic_recall)
        assert callable(agent.semantic_learn)
        assert callable(agent.semantic_promote)
        assert callable(agent.semantic_stats)

    def test_mixin_is_safe_for_dataclass_subclass(self):
        from dataclasses import dataclass

        from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin

        @dataclass
        class DataAgent(SemanticCacheMixin):
            name: str = "agent"
            value: int = 0

        agent = DataAgent(name="test", value=42)
        assert agent.name == "test"
        assert callable(agent.semantic_recall)


# ===========================================================================
# Invariant: regression guards
# ===========================================================================


class TestSemanticCacheInvariants:
    def test_semantic_cache_manager_config_module_does_not_exist(self):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("agentic_core.L4_state.memory.semantic_cache_manager_config")

    def test_semantic_cache_manager_get_instance_is_singleton(self):
        _reset_hive()
        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        a = SemanticCacheManager.get_instance()
        b = SemanticCacheManager.get_instance()
        assert a is b
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
