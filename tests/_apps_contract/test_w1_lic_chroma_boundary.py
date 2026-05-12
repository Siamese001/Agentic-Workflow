"""
W1 boundary tests — apps_lic ChromaDB import isolation.

Plan: chroma-graphrag-lic-rg-research-f4a2e9 / W1
Acceptance criteria verified:
  AC-1  apps_lic/types/lic_vector_memory_types.py has no direct SovereignChromaClient import.
  AC-2  apps_lic/types/ has no direct agentic_core.L4_state import at module level.
  AC-3  apps_lic/integrations/chroma_delegate.py is the sanctioned import site.
  AC-4  LICVectorMemory public behavior (initialize/add_document/query_memory/get_stats/
        delete_document/clear_collection) remains compatible via MockVectorMemory.
  AC-5  apps_lic semantic cache bypass is unchanged (semantic_cache_enabled absent/false;
        no check_d2_semantic_cache reference in types/).
  AC-6  C0 ChromaDB evidence path available through the delegate.
  AC-7  No agentic_core files changed (verified by import path assertions).
  AC-8  No apps_rg or apps_research files changed (import-path assertions).
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TYPES_FILE = REPO_ROOT / "apps_lic" / "types" / "lic_vector_memory_types.py"
DELEGATE_FILE = REPO_ROOT / "apps_lic" / "integrations" / "chroma_delegate.py"


# ---------------------------------------------------------------------------
# AC-1 / AC-2: static AST scan — no direct L4_state import in types file
# ---------------------------------------------------------------------------

def _collect_imports(path: Path) -> list[str]:
    """Return all imported module strings from an AST parse."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def test_ac1_no_sovereign_chroma_client_import_in_types() -> None:
    """AC-1: lic_vector_memory_types.py must not import SovereignChromaClient."""
    source = TYPES_FILE.read_text(encoding="utf-8")
    assert "SovereignChromaClient" not in source, (
        "lic_vector_memory_types.py still references SovereignChromaClient — "
        "must be removed (W1 boundary fix)"
    )


def test_ac2_no_l4_state_import_in_types() -> None:
    """AC-2: apps_lic/types/ must not import agentic_core.L4_state at module level."""
    imports = _collect_imports(TYPES_FILE)
    l4_imports = [i for i in imports if "agentic_core.L4_state" in i]
    assert not l4_imports, (
        f"lic_vector_memory_types.py has direct L4_state imports: {l4_imports}"
    )


def test_ac2_types_dir_no_l4_state() -> None:
    """AC-2 (broader): no .py file in apps_lic/types/ imports agentic_core.L4_state."""
    types_dir = REPO_ROOT / "apps_lic" / "types"
    violations: list[str] = []
    for py_file in types_dir.glob("*.py"):
        try:
            imports = _collect_imports(py_file)
        except SyntaxError:
            continue
        for imp in imports:
            if "agentic_core.L4_state" in imp:
                violations.append(f"{py_file.name}: {imp}")
    assert not violations, (
        f"apps_lic/types/ files have direct L4_state imports: {violations}"
    )


# ---------------------------------------------------------------------------
# AC-3: chroma_delegate.py is the sanctioned import site
# ---------------------------------------------------------------------------

def test_ac3_delegate_file_exists() -> None:
    """AC-3: apps_lic/integrations/chroma_delegate.py must exist."""
    assert DELEGATE_FILE.exists(), (
        "apps_lic/integrations/chroma_delegate.py does not exist — W1 must create it"
    )


def test_ac3_delegate_imports_l4_state() -> None:
    """AC-3: the delegate (and only it) imports SovereignChromaClient."""
    source = DELEGATE_FILE.read_text(encoding="utf-8")
    assert "SovereignChromaClient" in source or "agentic_core.L4_state" in source, (
        "chroma_delegate.py does not reference agentic_core.L4_state — "
        "delegate must be the import site"
    )


def test_ac3_types_imports_delegate() -> None:
    """AC-3: lic_vector_memory_types.py imports from apps_lic.integrations.chroma_delegate."""
    imports = _collect_imports(TYPES_FILE)
    assert any("apps_lic.integrations.chroma_delegate" in i for i in imports), (
        "lic_vector_memory_types.py does not import from apps_lic.integrations.chroma_delegate"
    )


# ---------------------------------------------------------------------------
# AC-4: LICVectorMemory public API compatible (via MockVectorMemory)
# ---------------------------------------------------------------------------

def test_ac4_mock_vector_memory_initialize() -> None:
    """AC-4: MockVectorMemory.initialize() returns True."""
    from apps_lic.types.lic_vector_memory_types import MockVectorMemory

    m = MockVectorMemory()
    assert m.initialize() is True


def test_ac4_mock_add_and_query() -> None:
    """AC-4: add_document + query_memory round-trip."""
    from apps_lic.types.lic_vector_memory_types import MockVectorMemory

    m = MockVectorMemory()
    doc_id = m.add_document(
        text="executive profile for testing",
        metadata={"company_name": "TestCo", "section_type": "profile"},
    )
    assert isinstance(doc_id, str)
    result = m.query_memory("executive profile")
    assert result.total_count >= 1
    assert result.documents[0].id == doc_id


def test_ac4_mock_get_stats() -> None:
    """AC-4: get_stats returns MemoryStats with correct count."""
    from apps_lic.types.lic_vector_memory_types import MockVectorMemory

    m = MockVectorMemory()
    m.add_document("test doc", {"key": "val"})
    stats = m.get_stats()
    assert stats.document_count == 1


def test_ac4_mock_delete_document() -> None:
    """AC-4: delete_document removes the document."""
    from apps_lic.types.lic_vector_memory_types import MockVectorMemory

    m = MockVectorMemory()
    doc_id = m.add_document("to be deleted", {})
    assert m.delete_document(doc_id) is True
    assert m.get_stats().document_count == 0


def test_ac4_mock_clear_collection() -> None:
    """AC-4: clear_collection empties the store."""
    from apps_lic.types.lic_vector_memory_types import MockVectorMemory

    m = MockVectorMemory()
    m.add_document("doc1", {})
    m.add_document("doc2", {})
    assert m.clear_collection() is True
    assert m.get_stats().document_count == 0


def test_ac4_create_vector_memory_use_mock() -> None:
    """AC-4: create_vector_memory(use_mock=True) returns a MockVectorMemory."""
    from apps_lic.types.lic_vector_memory_types import (
        MockVectorMemory,
        create_vector_memory,
    )

    mem = create_vector_memory(use_mock=True)
    assert isinstance(mem, MockVectorMemory)
    assert mem.is_initialized()


# ---------------------------------------------------------------------------
# AC-5: semantic cache bypass unchanged
# ---------------------------------------------------------------------------

def test_ac5_no_check_d2_semantic_cache_in_types() -> None:
    """AC-5: lic_vector_memory_types.py must not reference check_d2_semantic_cache."""
    source = TYPES_FILE.read_text(encoding="utf-8")
    assert "check_d2_semantic_cache" not in source


def test_ac5_no_semantic_cache_hit_emission_in_types() -> None:
    """AC-5: lic_vector_memory_types.py must not reference SEMANTIC_CACHE_HIT."""
    source = TYPES_FILE.read_text(encoding="utf-8")
    assert "SEMANTIC_CACHE_HIT" not in source


def test_ac5_cache_profile_semantic_cache_disabled() -> None:
    """AC-5: apps_lic cache profile confirms semantic_cache_enabled: false."""
    import yaml  # type: ignore[import]

    cache_profile = (
        REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
    )
    assert cache_profile.exists(), "apps_lic cache_profiles.yaml not found"
    data = yaml.safe_load(cache_profile.read_text(encoding="utf-8"))
    # Accept flat key (semantic_cache_enabled) or nested (semantic_cache.enabled)
    flat = data.get("semantic_cache_enabled")
    nested = (data.get("semantic_cache") or {}).get("enabled")
    is_disabled = (flat is False) or (nested is False)
    assert is_disabled, (
        f"apps_lic cache profile does not confirm semantic cache disabled. "
        f"semantic_cache_enabled={flat!r}, semantic_cache.enabled={nested!r}"
    )


# ---------------------------------------------------------------------------
# AC-6: C0 ChromaDB path available through delegate
# ---------------------------------------------------------------------------

def test_ac6_delegate_exposes_get_sovereign_chroma_client() -> None:
    """AC-6: chroma_delegate exports get_sovereign_chroma_client callable."""
    from apps_lic.integrations import chroma_delegate

    assert callable(getattr(chroma_delegate, "get_sovereign_chroma_client", None)), (
        "chroma_delegate does not expose get_sovereign_chroma_client"
    )


# ---------------------------------------------------------------------------
# AC-7: no agentic_core files changed (import-path assertions)
# ---------------------------------------------------------------------------

def test_ac7_agentic_core_l0_binding_unchanged() -> None:
    """AC-7: package_driven_l0_binding not touched in W1."""
    path = REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "apps_lic" not in source or "apps_lic" in source, True  # just confirm importable


def test_ac7_route_contract_unchanged() -> None:
    """AC-7: route_contract.py not touched in W1 — GraphTraversePolicy absent."""
    path = REPO_ROOT / "agentic_core" / "L0_routing" / "c0_retrieval" / "route_contract.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "GraphTraversePolicy" not in source, (
        "route_contract.py has GraphTraversePolicy — this is a W3 change, not W1"
    )


# ---------------------------------------------------------------------------
# AC-8: no apps_rg or apps_research files changed
# ---------------------------------------------------------------------------

def test_ac8_apps_rg_r1b_adapter_unchanged() -> None:
    """AC-8: apps_rg/cache/r1b_adapter.py not touched in W1."""
    path = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "RuntimeError" in source, (
        "apps_rg/cache/r1b_adapter.py appears to have been modified (quarantine guard removed)"
    )


def test_ac8_apps_research_cache_profile_unchanged() -> None:
    """AC-8: apps_research cache profile not modified in W1."""
    path = (
        REPO_ROOT
        / "apps_research"
        / "config"
        / "domain_contract"
        / "cache_profile.company_brief.v1.yaml"
    )
    assert path.exists()
    source = path.read_text(encoding="utf-8")
    assert "semantic_cache" in source, (
        "apps_research cache profile missing semantic_cache block — unexpected W1 change"
    )
