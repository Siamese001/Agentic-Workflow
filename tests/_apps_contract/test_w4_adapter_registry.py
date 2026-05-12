"""W4 tests — config-driven adapter registry for C0.3 graph traversal.

Plan: chroma-graphrag-lic-rg-research-f4a2e9  Wave 4

Coverage:
  T4-01  ADAPTER_REGISTRY dict is exported from pipeline and c0_3_enhanced
  T4-02  register_graph_adapter stores factory under ref key
  T4-03  resolve_graph_adapter returns adapter from pre-registered factory
  T4-04  resolve_graph_adapter auto-imports module and calls get_graph_adapter()
  T4-05  resolve_graph_adapter fails closed on None ref
  T4-06  resolve_graph_adapter fails closed on empty string ref
  T4-07  resolve_graph_adapter fails closed on unknown/unimportable ref
  T4-08  resolve_graph_adapter fails closed when module has no get_graph_adapter()
  T4-09  apps_lic adapter is importable and returns a GraphTraversalAdapter
  T4-10  apps_rg adapter is importable and returns a GraphTraversalAdapter
  T4-11  apps_research adapter is importable and returns a GraphTraversalAdapter
  T4-12  No adapter module calls run_graph_traverse() — static AST check
  T4-13  resolve_graph_adapter is NOT imported/called in package_driven_l0_binding — static check
  T4-14  Each app adapter's get_graph_adapter() builds only GraphTraverseInput-compatible objects
  T4-15  All three graph_adapter_ref values in route profiles resolve via auto-import path
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent


# ---------------------------------------------------------------------------
# T4-01  ADAPTER_REGISTRY dict is exported
# ---------------------------------------------------------------------------

def test_adapter_registry_exported_from_pipeline() -> None:
    """ADAPTER_REGISTRY is accessible directly from pipeline module."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        ADAPTER_REGISTRY,
    )
    assert isinstance(ADAPTER_REGISTRY, dict)


def test_adapter_registry_exported_from_package() -> None:
    """ADAPTER_REGISTRY is re-exported from c0_3_enhanced __init__."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced import ADAPTER_REGISTRY
    assert isinstance(ADAPTER_REGISTRY, dict)


# ---------------------------------------------------------------------------
# T4-02  register_graph_adapter stores factory
# ---------------------------------------------------------------------------

def test_register_graph_adapter_stores_factory() -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        ADAPTER_REGISTRY,
        register_graph_adapter,
    )
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
        InMemoryGraphAdapter,
    )

    ref = "_test.register.t4_02"
    factory = lambda: InMemoryGraphAdapter()
    try:
        register_graph_adapter(ref, factory)
        assert ref in ADAPTER_REGISTRY
        assert ADAPTER_REGISTRY[ref] is factory
    finally:
        ADAPTER_REGISTRY.pop(ref, None)


# ---------------------------------------------------------------------------
# T4-03  resolve_graph_adapter returns from pre-registered factory
# ---------------------------------------------------------------------------

def test_resolve_graph_adapter_uses_registered_factory() -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        ADAPTER_REGISTRY,
        register_graph_adapter,
        resolve_graph_adapter,
    )
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
        InMemoryGraphAdapter,
        GraphTraversalAdapter,
    )

    ref = "_test.resolve.t4_03"
    adapter_instance = InMemoryGraphAdapter()
    register_graph_adapter(ref, lambda: adapter_instance)
    try:
        result = resolve_graph_adapter(ref)
        assert result is adapter_instance
        assert isinstance(result, GraphTraversalAdapter)
    finally:
        ADAPTER_REGISTRY.pop(ref, None)


# ---------------------------------------------------------------------------
# T4-04  resolve_graph_adapter auto-imports module
# ---------------------------------------------------------------------------

def test_resolve_graph_adapter_auto_imports_module() -> None:
    """resolve_graph_adapter can load apps_lic adapter via auto-import path."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        ADAPTER_REGISTRY,
        resolve_graph_adapter,
    )
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
        GraphTraversalAdapter,
    )

    ref = "apps_lic.integrations.c0_graph_adapter"
    # Clear any prior registration to force auto-import path
    ADAPTER_REGISTRY.pop(ref, None)
    sys.modules.pop(ref, None)

    try:
        result = resolve_graph_adapter(ref)
        assert isinstance(result, GraphTraversalAdapter)
        # Factory should now be cached
        assert ref in ADAPTER_REGISTRY
    finally:
        # Clean up so W3 test_graph_adapter_ref_is_carried_but_not_resolved
        # still sees the module as "not imported at W3 time"
        ADAPTER_REGISTRY.pop(ref, None)
        sys.modules.pop(ref, None)


# ---------------------------------------------------------------------------
# T4-05  fail-closed on None
# ---------------------------------------------------------------------------

def test_resolve_graph_adapter_fails_closed_on_none() -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        resolve_graph_adapter,
    )
    with pytest.raises(ValueError, match="None or empty"):
        resolve_graph_adapter(None)


# ---------------------------------------------------------------------------
# T4-06  fail-closed on empty string
# ---------------------------------------------------------------------------

def test_resolve_graph_adapter_fails_closed_on_empty_string() -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        resolve_graph_adapter,
    )
    with pytest.raises(ValueError, match="None or empty"):
        resolve_graph_adapter("")


# ---------------------------------------------------------------------------
# T4-07  fail-closed on unimportable ref
# ---------------------------------------------------------------------------

def test_resolve_graph_adapter_fails_closed_on_unknown_ref() -> None:
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        ADAPTER_REGISTRY,
        resolve_graph_adapter,
    )
    ref = "no_such_app.integrations.c0_graph_adapter_xyz999"
    ADAPTER_REGISTRY.pop(ref, None)
    with pytest.raises(ValueError, match="cannot import adapter module"):
        resolve_graph_adapter(ref)


# ---------------------------------------------------------------------------
# T4-08  fail-closed when module lacks get_graph_adapter()
# ---------------------------------------------------------------------------

def test_resolve_graph_adapter_fails_closed_no_entry_point(tmp_path, monkeypatch) -> None:
    """Module exists but has no get_graph_adapter() — must raise ValueError."""
    import types

    mod = types.ModuleType("_test_no_entry_point_t4_08")
    # No get_graph_adapter attribute
    ref = "_test_no_entry_point_t4_08"

    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        ADAPTER_REGISTRY,
        resolve_graph_adapter,
    )

    ADAPTER_REGISTRY.pop(ref, None)
    sys.modules[ref] = mod
    try:
        with pytest.raises(ValueError, match="get_graph_adapter"):
            resolve_graph_adapter(ref)
    finally:
        sys.modules.pop(ref, None)
        ADAPTER_REGISTRY.pop(ref, None)


# ---------------------------------------------------------------------------
# T4-09  apps_lic adapter importable + returns GraphTraversalAdapter
# ---------------------------------------------------------------------------

def test_apps_lic_adapter_importable_and_protocol_satisfied() -> None:
    from apps_lic.integrations.c0_graph_adapter import get_graph_adapter
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
        GraphTraversalAdapter,
    )
    adapter = get_graph_adapter()
    assert isinstance(adapter, GraphTraversalAdapter)


# ---------------------------------------------------------------------------
# T4-10  apps_rg adapter importable + returns GraphTraversalAdapter
# ---------------------------------------------------------------------------

def test_apps_rg_adapter_importable_and_protocol_satisfied() -> None:
    from apps_rg.integrations.c0_graph_adapter import get_graph_adapter
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
        GraphTraversalAdapter,
    )
    adapter = get_graph_adapter()
    assert isinstance(adapter, GraphTraversalAdapter)


# ---------------------------------------------------------------------------
# T4-11  apps_research adapter importable + returns GraphTraversalAdapter
# ---------------------------------------------------------------------------

def test_apps_research_adapter_importable_and_protocol_satisfied() -> None:
    from apps_research.integrations.c0_graph_adapter import get_graph_adapter
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
        GraphTraversalAdapter,
    )
    adapter = get_graph_adapter()
    assert isinstance(adapter, GraphTraversalAdapter)


# ---------------------------------------------------------------------------
# T4-12  No app adapter calls run_graph_traverse() — static AST check
# ---------------------------------------------------------------------------

def _adapter_source(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


@pytest.mark.parametrize("rel_path", [
    "apps_lic/integrations/c0_graph_adapter.py",
    "apps_rg/integrations/c0_graph_adapter.py",
    "apps_research/integrations/c0_graph_adapter.py",
])
def test_app_adapter_does_not_call_run_graph_traverse(rel_path: str) -> None:
    """Static AST check: no app adapter may call run_graph_traverse()."""
    source = _adapter_source(rel_path)
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            assert name != "run_graph_traverse", (
                f"{rel_path} calls run_graph_traverse() — FORBIDDEN in app adapters"
            )


# ---------------------------------------------------------------------------
# T4-13  resolve_graph_adapter is NOT in package_driven_l0_binding — static check
# ---------------------------------------------------------------------------

def test_resolve_graph_adapter_not_in_l0_binding() -> None:
    """L0 binding must not import or call resolve_graph_adapter / run_graph_traverse.

    Uses AST walk so that comments and docstring mentions do not trigger the
    assertion — only live call-sites and import statements are checked.
    """
    source = (
        REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)

    FORBIDDEN_NAMES = {"resolve_graph_adapter", "run_graph_traverse"}

    for node in ast.walk(tree):
        # Check function calls: foo() or obj.foo()
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            assert name not in FORBIDDEN_NAMES, (
                f"package_driven_l0_binding.py calls {name}() — FORBIDDEN in L0 binding"
            )
        # Check imports: import x or from y import z
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in FORBIDDEN_NAMES, (
                    f"package_driven_l0_binding.py imports {alias.name} — FORBIDDEN in L0"
                )
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                assert alias.name not in FORBIDDEN_NAMES, (
                    f"package_driven_l0_binding.py imports {alias.name} from "
                    f"{node.module} — FORBIDDEN in L0"
                )


# ---------------------------------------------------------------------------
# T4-14  app adapter get_graph_adapter() health_check() returns healthy
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("module_path", [
    "apps_lic.integrations.c0_graph_adapter",
    "apps_rg.integrations.c0_graph_adapter",
    "apps_research.integrations.c0_graph_adapter",
])
def test_app_adapter_health_check_healthy(module_path: str) -> None:
    """Each app adapter's health_check() must return healthy=True (stub contract)."""
    mod = importlib.import_module(module_path)
    adapter = mod.get_graph_adapter()
    health = adapter.health_check()
    assert health.healthy is True, (
        f"{module_path}: health_check().healthy is False — stub must report healthy"
    )


# ---------------------------------------------------------------------------
# T4-15  All three graph_adapter_ref values resolve via auto-import
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ref,expected_source", [
    (
        "apps_lic.integrations.c0_graph_adapter",
        "apps_lic.knowledge_graph.v1",
    ),
    (
        "apps_rg.integrations.c0_graph_adapter",
        "apps_rg.resume_graph.v1",
    ),
    (
        "apps_research.integrations.c0_graph_adapter",
        "apps_research.company_brief_graph.v1",
    ),
])
def test_all_route_profile_refs_resolve(ref: str, expected_source: str) -> None:
    """All three graph_adapter_ref values from route profiles resolve to an adapter."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.pipeline import (
        ADAPTER_REGISTRY,
        resolve_graph_adapter,
    )
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter import (
        GraphTraversalAdapter,
    )

    # Clear cache to test resolution from scratch
    ADAPTER_REGISTRY.pop(ref, None)
    sys.modules.pop(ref, None)

    try:
        adapter = resolve_graph_adapter(ref)
        assert isinstance(adapter, GraphTraversalAdapter)

        manifest = adapter.get_projection_manifest()
        assert manifest.graph_source == expected_source, (
            f"{ref}: expected graph_source={expected_source!r}, got {manifest.graph_source!r}"
        )
    finally:
        # Clean up to preserve W3 test isolation
        ADAPTER_REGISTRY.pop(ref, None)
        sys.modules.pop(ref, None)
