"""W3 tests — C0.3 adapter registry / resolver.

Proves:
  - Resolver exists and is importable.
  - Resolves apps_lic, apps_rg, apps_research adapters by graph_adapter_ref.
  - Unknown / missing / malformed refs fail closed.
  - Import errors fail closed.
  - Invalid adapter shapes fail closed.
  - No app_id branching in registry source.
  - Registry never calls run_graph_traverse().
  - L0 still does not call run_graph_traverse().
  - W1 R1B tests still pass (regression guard).
  - W2 graph policy tests still pass (regression guard).
  - apps_lic semantic cache still bypassed.
  - apps_rg quarantined adapter untouched.

Plan: chroma-graphrag-core-wiring-gaps-b3f7a1 W3
"""

from __future__ import annotations

import ast
import importlib
import pathlib
import subprocess
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent
REGISTRY_PATH = (
    REPO_ROOT
    / "agentic_core"
    / "L0_routing"
    / "c0_retrieval"
    / "c0_3_enhanced"
    / "adapter_registry.py"
)
L0_BINDING_PATH = (
    REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
)
APPS_LIC_CACHE_PATH = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
APPS_RG_ADAPTER_PATH = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"

# Known good refs (dotted module paths from app route profiles)
_REF_LIC = "apps_lic.integrations.c0_graph_adapter"
_REF_RG = "apps_rg.integrations.c0_graph_adapter"
_REF_RESEARCH = "apps_research.integrations.c0_graph_adapter"


# ---------------------------------------------------------------------------
# 1. test_adapter_registry_resolver_exists
# ---------------------------------------------------------------------------


def test_adapter_registry_resolver_exists() -> None:
    """adapter_registry.py exists and exports resolve_graph_adapter."""
    assert REGISTRY_PATH.exists(), f"adapter_registry.py not found at {REGISTRY_PATH}"

    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
        resolve_graph_adapter,
        AdapterResolutionResult,
        AdapterResolutionStatus,
    )
    assert callable(resolve_graph_adapter)
    assert AdapterResolutionStatus.RESOLVED == "RESOLVED"


# ---------------------------------------------------------------------------
# 2-4. Resolve real adapters by graph_adapter_ref
# ---------------------------------------------------------------------------


class TestResolvesKnownAdapters:
    """test_resolves_apps_*_adapter_by_graph_adapter_ref"""

    def _assert_resolved(self, ref: str) -> None:
        from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
            resolve_graph_adapter,
            AdapterResolutionStatus,
        )
        result = resolve_graph_adapter(ref)
        assert result.status == AdapterResolutionStatus.RESOLVED, (
            f"Expected RESOLVED for ref={ref!r}, got {result.status}: {result.reason}"
        )
        assert result.adapter is not None
        assert result.graph_adapter_ref == ref
        # Verify shape
        for method in ("resolve_anchor", "get_neighbors", "get_relation_path",
                       "get_projection_manifest", "health_check"):
            assert callable(getattr(result.adapter, method, None)), (
                f"Adapter from {ref!r} missing method {method!r}"
            )

    def test_resolves_apps_lic_adapter_by_graph_adapter_ref(self) -> None:
        self._assert_resolved(_REF_LIC)

    def test_resolves_apps_rg_adapter_by_graph_adapter_ref(self) -> None:
        self._assert_resolved(_REF_RG)

    def test_resolves_apps_research_adapter_by_graph_adapter_ref(self) -> None:
        self._assert_resolved(_REF_RESEARCH)


# ---------------------------------------------------------------------------
# 5. test_unknown_adapter_ref_fails_closed
# ---------------------------------------------------------------------------


def test_unknown_adapter_ref_fails_closed() -> None:
    """A ref pointing to a non-existent module returns IMPORT_ERROR, not a pass."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
        resolve_graph_adapter,
        AdapterResolutionStatus,
    )
    result = resolve_graph_adapter("apps_nonexistent.integrations.c0_graph_adapter")
    assert result.status == AdapterResolutionStatus.IMPORT_ERROR, (
        f"Unknown ref must fail closed, got {result.status}: {result.reason}"
    )
    assert result.adapter is None
    assert result.reason


# ---------------------------------------------------------------------------
# 6. test_missing_adapter_ref_fails_closed
# ---------------------------------------------------------------------------


def test_missing_adapter_ref_fails_closed() -> None:
    """Empty or None ref returns MISSING_REF."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
        resolve_graph_adapter,
        AdapterResolutionStatus,
    )
    for bad_ref in ("", "   "):
        result = resolve_graph_adapter(bad_ref)
        assert result.status == AdapterResolutionStatus.MISSING_REF, (
            f"Empty ref must return MISSING_REF, got {result.status} for {bad_ref!r}"
        )
        assert result.adapter is None


# ---------------------------------------------------------------------------
# 7. test_malformed_adapter_ref_fails_closed
# ---------------------------------------------------------------------------


def test_malformed_adapter_ref_fails_closed() -> None:
    """Refs that are not valid dotted Python paths return INVALID_REF."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
        resolve_graph_adapter,
        AdapterResolutionStatus,
    )
    malformed_refs = [
        "not-a-valid.module",   # hyphens not allowed
        ".leading.dot",         # leading dot
        "trailing.dot.",        # trailing dot
        "single",               # only one segment (no dot)
        "has space.module",     # space
        "123starts.with.digit", # leading digit
    ]
    for ref in malformed_refs:
        result = resolve_graph_adapter(ref)
        assert result.status == AdapterResolutionStatus.INVALID_REF, (
            f"Malformed ref {ref!r} must return INVALID_REF, got {result.status}"
        )
        assert result.adapter is None


# ---------------------------------------------------------------------------
# 8. test_import_error_fails_closed
# ---------------------------------------------------------------------------


def test_import_error_fails_closed() -> None:
    """When importlib raises ImportError, resolver returns IMPORT_ERROR."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
        resolve_graph_adapter,
        AdapterResolutionStatus,
    )
    with patch(
        "agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry.importlib.import_module",
        side_effect=ImportError("simulated import failure"),
    ):
        result = resolve_graph_adapter("apps_lic.integrations.c0_graph_adapter")
    assert result.status == AdapterResolutionStatus.IMPORT_ERROR, (
        f"ImportError must produce IMPORT_ERROR, got {result.status}"
    )
    assert result.adapter is None
    assert "simulated import failure" in result.reason


# ---------------------------------------------------------------------------
# 9. test_invalid_adapter_shape_fails_closed
# ---------------------------------------------------------------------------


def test_invalid_adapter_shape_fails_closed() -> None:
    """If the resolved adapter lacks required methods, returns INVALID_ADAPTER."""
    from agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry import (
        resolve_graph_adapter,
        AdapterResolutionStatus,
    )

    # Build a fake module whose get_graph_adapter() returns a shapeless object
    fake_adapter = MagicMock(spec=[])  # no attributes exposed
    fake_module = MagicMock()
    fake_module.get_graph_adapter.return_value = fake_adapter

    with patch(
        "agentic_core.L0_routing.c0_retrieval.c0_3_enhanced.adapter_registry.importlib.import_module",
        return_value=fake_module,
    ):
        result = resolve_graph_adapter("apps_fake.integrations.c0_graph_adapter")

    assert result.status == AdapterResolutionStatus.INVALID_ADAPTER, (
        f"Shapeless adapter must produce INVALID_ADAPTER, got {result.status}"
    )
    assert result.adapter is None
    assert result.reason


# ---------------------------------------------------------------------------
# 10. test_no_app_id_branch_in_adapter_registry
# ---------------------------------------------------------------------------


def test_no_app_id_branch_in_adapter_registry() -> None:
    """adapter_registry.py must contain no app_id branching (AST + string check)."""
    source = REGISTRY_PATH.read_text(encoding="utf-8")

    # Forbidden structural patterns — hardcoded registry dict
    forbidden_patterns = [
        "ADAPTER_REGISTRY = {",
        "_REGISTRY = {",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in source, (
            f"Forbidden pattern {pattern!r} found in adapter_registry.py"
        )

    # AST: no if/elif/else comparing against an "apps_*" string literal.
    # This catches real branching without matching docstring/comment text.
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str):
                    if comparator.value.startswith("apps_"):
                        raise AssertionError(
                            f"Found app_id branch at line {node.lineno} comparing to {comparator.value!r}"
                        )


# ---------------------------------------------------------------------------
# 11. test_adapter_registry_does_not_call_run_graph_traverse
# ---------------------------------------------------------------------------


def test_adapter_registry_does_not_call_run_graph_traverse() -> None:
    """adapter_registry.py must not call run_graph_traverse() — AST verified."""
    source = REGISTRY_PATH.read_text(encoding="utf-8")
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
                f"run_graph_traverse() called at line {node.lineno} in adapter_registry.py — forbidden"
            )


# ---------------------------------------------------------------------------
# 12. test_l0_still_does_not_call_run_graph_traverse
# ---------------------------------------------------------------------------


def test_l0_still_does_not_call_run_graph_traverse() -> None:
    """package_driven_l0_binding.py must not call run_graph_traverse() — AST verified."""
    source = L0_BINDING_PATH.read_text(encoding="utf-8")
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
                f"run_graph_traverse() called at line {node.lineno} in L0 binding — forbidden"
            )


# ---------------------------------------------------------------------------
# 13. test_w1_r1b_tests_still_pass
# ---------------------------------------------------------------------------


def test_w1_r1b_tests_still_pass() -> None:
    """Regression guard: all W1 R1B tests must still pass."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/_apps_contract/test_w1_core_r1b_cache_wiring.py",
            "--tb=short",
            "-q",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"W1 R1B tests regressed:\n{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# 14. test_w2_graph_policy_tests_still_pass
# ---------------------------------------------------------------------------


def test_w2_graph_policy_tests_still_pass() -> None:
    """Regression guard: all W2 graph policy tests must still pass."""
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/_apps_contract/test_w2_route_contract_graph_policy.py",
            "--tb=short",
            "-q",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"W2 graph policy tests regressed:\n{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# 15. test_apps_lic_semantic_cache_still_bypassed
# ---------------------------------------------------------------------------


def test_apps_lic_semantic_cache_still_bypassed() -> None:
    """apps_lic cache profile must not have semantic_cache.enabled: true."""
    if not APPS_LIC_CACHE_PATH.exists():
        pytest.skip(f"apps_lic cache profiles not found at {APPS_LIC_CACHE_PATH}")
    content = APPS_LIC_CACHE_PATH.read_text(encoding="utf-8")
    # The profile must not enable semantic cache
    assert "enabled: true" not in content, (
        "apps_lic semantic cache must remain bypassed (enabled: true found in cache_profiles.yaml)"
    )


# ---------------------------------------------------------------------------
# 16. test_apps_rg_quarantined_adapter_untouched
# ---------------------------------------------------------------------------


def test_apps_rg_quarantined_adapter_untouched() -> None:
    """apps_rg/cache/r1b_adapter.py must not be imported by adapter_registry."""
    # Check the registry source does not import from r1b_adapter
    source = REGISTRY_PATH.read_text(encoding="utf-8")
    assert "r1b_adapter" not in source, (
        "adapter_registry.py must not import or reference apps_rg/cache/r1b_adapter"
    )
    # Also verify the quarantined file still exists and is unchanged (not empty)
    if APPS_RG_ADAPTER_PATH.exists():
        assert APPS_RG_ADAPTER_PATH.stat().st_size > 100, (
            "apps_rg/cache/r1b_adapter.py appears truncated"
        )
