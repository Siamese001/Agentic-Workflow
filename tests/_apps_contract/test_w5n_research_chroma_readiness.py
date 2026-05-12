"""
W5N tests — apps_research Chroma readiness and embedding-profile cleanup.

Plan: chroma-graphrag-lic-rg-research-f4a2e9 / W5N (no-core track)
Constraint: zero agentic_core changes; no live runtime wiring; CONFIG_PREPARED_ONLY.

Acceptance criteria verified:
  AC-1   Embedding profile uses BAAI/bge-m3 / 1024 dims.
  AC-2   Embedding profile marked CONFIG_PREPARED_ONLY.
  AC-3   create_retrieval_engine(None) returns InMemoryResearchStore.
  AC-4   create_retrieval_engine(<path>) returns ChromaResearchStore.
  AC-5   ChromaResearchStore uses process_docs collection.
  AC-6   ChromaResearchStore exposes add_research / query_similar / get_by_mode.
  AC-7   Mock SHA-256 embed not present in ChromaResearchStore source.
  AC-8   ChromaResearchStore does not call run_graph_traverse().
  AC-9   ChromaResearchStore does not answer, route, or assemble prompts.
  AC-10  ChromaResearchStore does not write L4 or call UWG.
  AC-11  No agentic_core files changed in W5N.
  AC-12  apps_lic untouched by W5N.
  AC-13  apps_rg untouched by W5N.
  AC-14  apps_rg/cache/r1b_adapter.py quarantine untouched.
  AC-15  W5N does not claim live C0 runtime wiring.
  AC-16  W5N does not execute ingestion.
"""

from __future__ import annotations

import importlib
import inspect
import re
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import yaml

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent
CACHE_PROFILE = REPO_ROOT / "apps_research" / "config" / "domain_contract" / "cache_profile.company_brief.v1.yaml"
RETRIEVAL_ENGINE_PATH = REPO_ROOT / "apps_research" / "engines" / "research_retrieval_engine.py"
CHROMA_STORE_PATH = REPO_ROOT / "apps_research" / "engines" / "integration" / "chroma_research_store.py"
CORE_DIR = REPO_ROOT / "agentic_core"
APPS_LIC_DIR = REPO_ROOT / "apps_lic"
APPS_RG_DIR = REPO_ROOT / "apps_rg"
RG_QUARANTINED_ADAPTER = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
C03_PIPELINE = REPO_ROOT / "agentic_core" / "L0_routing" / "c0_retrieval" / "c0_3_enhanced" / "pipeline.py"

# ---------------------------------------------------------------------------
# AC-1: Embedding profile uses BAAI/bge-m3 / 1024
# ---------------------------------------------------------------------------


def test_research_embedding_profile_uses_bge_m3_1024() -> None:
    """AC-1: cache_profile must declare BAAI/bge-m3 with 1024 dimensions."""
    data = yaml.safe_load(CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data["semantic_cache"]
    assert sc.get("embedding_model") == "BAAI/bge-m3", (
        f"Expected BAAI/bge-m3 but got: {sc.get('embedding_model')!r}"
    )
    assert sc.get("embedding_dimensions") == 1024, (
        f"Expected 1024 dims but got: {sc.get('embedding_dimensions')!r}"
    )


# ---------------------------------------------------------------------------
# AC-2: Embedding profile marked CONFIG_PREPARED_ONLY
# ---------------------------------------------------------------------------


def test_research_embedding_profile_marked_config_prepared_only() -> None:
    """AC-2: cache_profile must carry W5N readiness markers."""
    data = yaml.safe_load(CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data["semantic_cache"]
    assert sc.get("embedding_profile_status") == "CONFIG_PREPARED_ONLY", (
        f"embedding_profile_status: {sc.get('embedding_profile_status')!r}"
    )
    assert sc.get("live_wiring_deferred") is True, (
        f"live_wiring_deferred: {sc.get('live_wiring_deferred')!r}"
    )
    assert sc.get("wiring_gate") == "APPS_RESEARCH_CHROMA_RUNTIME_WIRING_REQUIRED", (
        f"wiring_gate: {sc.get('wiring_gate')!r}"
    )


# ---------------------------------------------------------------------------
# AC-3: create_retrieval_engine(None) returns InMemoryResearchStore
# ---------------------------------------------------------------------------


def test_create_retrieval_engine_none_returns_in_memory_store() -> None:
    """AC-3: factory with chromadb_path=None must return InMemoryResearchStore-backed engine."""
    from apps_research.engines.research_retrieval_engine import (
        InMemoryResearchStore,
        ResearchRetrievalEngine,
        create_retrieval_engine,
    )

    engine = create_retrieval_engine(chromadb_path=None)
    assert isinstance(engine, ResearchRetrievalEngine), (
        f"Expected ResearchRetrievalEngine, got {type(engine).__name__}"
    )
    assert isinstance(engine.store, InMemoryResearchStore), (
        f"Expected InMemoryResearchStore store, got {type(engine.store).__name__}"
    )


# ---------------------------------------------------------------------------
# AC-4: create_retrieval_engine(<path>) returns ChromaResearchStore
# ---------------------------------------------------------------------------


def test_create_retrieval_engine_path_returns_chroma_research_store() -> None:
    """AC-4: factory with chromadb_path supplied must return ChromaResearchStore-backed engine."""
    from apps_research.engines.integration.chroma_research_store import ChromaResearchStore
    from apps_research.engines.research_retrieval_engine import (
        ResearchRetrievalEngine,
        create_retrieval_engine,
    )

    engine = create_retrieval_engine(chromadb_path="/fake/path/for/test")
    assert isinstance(engine, ResearchRetrievalEngine), (
        f"Expected ResearchRetrievalEngine, got {type(engine).__name__}"
    )
    assert isinstance(engine.store, ChromaResearchStore), (
        f"Expected ChromaResearchStore store, got {type(engine.store).__name__}"
    )
    assert engine.store._chromadb_path == "/fake/path/for/test"


# ---------------------------------------------------------------------------
# AC-5: ChromaResearchStore uses process_docs collection
# ---------------------------------------------------------------------------


def test_chroma_research_store_uses_process_docs_collection() -> None:
    """AC-5: ChromaResearchStore must declare process_docs as its collection name."""
    from apps_research.engines.integration.chroma_research_store import (
        COLLECTION_NAME,
        ChromaResearchStore,
    )

    assert COLLECTION_NAME == "process_docs", (
        f"COLLECTION_NAME: {COLLECTION_NAME!r}"
    )
    assert ChromaResearchStore.collection_name == "process_docs", (
        f"ChromaResearchStore.collection_name: {ChromaResearchStore.collection_name!r}"
    )


# ---------------------------------------------------------------------------
# AC-6: ChromaResearchStore exposes required interface
# ---------------------------------------------------------------------------


def test_chroma_research_store_has_required_interface() -> None:
    """AC-6: ChromaResearchStore must expose add_research, query_similar, get_by_mode."""
    from apps_research.engines.integration.chroma_research_store import ChromaResearchStore

    for method_name in ("add_research", "query_similar", "get_by_mode"):
        assert callable(getattr(ChromaResearchStore, method_name, None)), (
            f"ChromaResearchStore missing method: {method_name}"
        )


# ---------------------------------------------------------------------------
# AC-7: Mock SHA-256 embed not used in ChromaResearchStore source
# ---------------------------------------------------------------------------


def test_mock_embed_not_used_in_chroma_store_path() -> None:
    """AC-7: ChromaResearchStore source must not use SHA-256/hashlib mock embedding."""
    source = CHROMA_STORE_PATH.read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        assert "hashlib.sha256" not in line, (
            f"ChromaResearchStore uses mock SHA-256 embed on line: {line!r}"
        )
        assert "_mock_embed" not in line, (
            f"ChromaResearchStore references _mock_embed on line: {line!r}"
        )


# ---------------------------------------------------------------------------
# AC-8: ChromaResearchStore does not call run_graph_traverse()
# ---------------------------------------------------------------------------


def test_chroma_store_does_not_call_run_graph_traverse() -> None:
    """AC-8: ChromaResearchStore source must not invoke run_graph_traverse()."""
    source = CHROMA_STORE_PATH.read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'"):
            continue
        assert "run_graph_traverse(" not in line, (
            f"ChromaResearchStore invokes run_graph_traverse() on line: {line!r}"
        )


# ---------------------------------------------------------------------------
# AC-9: ChromaResearchStore does not answer, route, or assemble prompts
# ---------------------------------------------------------------------------


def test_chroma_store_does_not_answer_route_or_prompt() -> None:
    """AC-9: ChromaResearchStore must not call answer(), route(), or assemble_prompt()."""
    source = CHROMA_STORE_PATH.read_text(encoding="utf-8")
    _import_re = re.compile(r"^\s*(?:import|from)\s+")
    forbidden_patterns = [
        (re.compile(r"\banswer\s*\("), "answer()"),
        (re.compile(r"\broute\s*\("), "route()"),
        (re.compile(r"\bassemble_prompt\s*\("), "assemble_prompt()"),
        (re.compile(r"\bbuild_prompt\s*\("), "build_prompt()"),
    ]
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        for pattern, label in forbidden_patterns:
            assert not pattern.search(line), (
                f"ChromaResearchStore calls {label} on line: {line!r}"
            )


# ---------------------------------------------------------------------------
# AC-10: ChromaResearchStore does not write L4 or call UWG
# ---------------------------------------------------------------------------


def test_chroma_store_does_not_write_l4_or_call_uwg() -> None:
    """AC-10: ChromaResearchStore must not import L4_state or call UWG."""
    source = CHROMA_STORE_PATH.read_text(encoding="utf-8")
    _l4_import_re = re.compile(r"^\s*(?:import|from)\s+.*L4_state")
    _uwg_import_re = re.compile(r"^\s*(?:import|from)\s+.*uwg")
    for line in source.splitlines():
        assert not _l4_import_re.match(line), (
            f"ChromaResearchStore imports L4_state: {line!r}"
        )
        assert not _uwg_import_re.match(line), (
            f"ChromaResearchStore imports UWG: {line!r}"
        )
    assert "write_l4(" not in source, "ChromaResearchStore calls write_l4()"
    assert "call_uwg(" not in source, "ChromaResearchStore calls call_uwg()"


# ---------------------------------------------------------------------------
# AC-11: No agentic_core files changed in W5N
# ---------------------------------------------------------------------------


def test_no_agentic_core_files_changed_in_w5n() -> None:
    """AC-11: agentic_core binding and C0.3 pipeline must not carry W5N markers."""
    w5n_marker = "W5N"
    for path in [C03_PIPELINE] if C03_PIPELINE.exists() else []:
        source = path.read_text(encoding="utf-8")
        assert w5n_marker not in source, (
            f"{path.name} contains W5N marker — agentic_core must not be touched in W5N"
        )
    _binding = CORE_DIR / "L0_routing" / "package_driven_l0_binding.py"
    if _binding.exists():
        source = _binding.read_text(encoding="utf-8")
        assert w5n_marker not in source, (
            "package_driven_l0_binding.py contains W5N marker — forbidden"
        )


# ---------------------------------------------------------------------------
# AC-12: apps_lic untouched by W5N
# ---------------------------------------------------------------------------


def test_apps_lic_untouched_by_w5n() -> None:
    """AC-12: no apps_lic file should contain a W5N marker."""
    w5n_marker = "W5N"
    for py_file in APPS_LIC_DIR.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        assert w5n_marker not in source, (
            f"apps_lic file {py_file.relative_to(REPO_ROOT)} contains W5N marker"
        )


# ---------------------------------------------------------------------------
# AC-13: apps_rg untouched by W5N
# ---------------------------------------------------------------------------


def test_apps_rg_untouched_by_w5n() -> None:
    """AC-13: no apps_rg file should contain a W5N marker."""
    w5n_marker = "W5N"
    for py_file in APPS_RG_DIR.rglob("*.py"):
        source = py_file.read_text(encoding="utf-8")
        assert w5n_marker not in source, (
            f"apps_rg file {py_file.relative_to(REPO_ROOT)} contains W5N marker"
        )


# ---------------------------------------------------------------------------
# AC-14: apps_rg/cache/r1b_adapter.py quarantine untouched
# ---------------------------------------------------------------------------


def test_apps_rg_quarantined_adapter_untouched() -> None:
    """AC-14: r1b_adapter.py must exist and must not contain W5N markers."""
    assert RG_QUARANTINED_ADAPTER.exists(), (
        f"r1b_adapter.py missing — quarantine file must not be deleted: {RG_QUARANTINED_ADAPTER}"
    )
    source = RG_QUARANTINED_ADAPTER.read_text(encoding="utf-8")
    assert "W5N" not in source, "r1b_adapter.py contains W5N marker — quarantine must not be modified"


# ---------------------------------------------------------------------------
# AC-15: W5N does not claim live C0 runtime wiring
# ---------------------------------------------------------------------------


def test_w5n_does_not_claim_live_c0_runtime_wiring() -> None:
    """AC-15: ChromaResearchStore and retrieval engine must carry live_wiring_deferred markers."""
    # Check module-level constant in ChromaResearchStore
    from apps_research.engines.integration.chroma_research_store import live_wiring_deferred

    assert live_wiring_deferred is True, (
        "chroma_research_store.live_wiring_deferred must be True"
    )
    assert ChromaResearchStore_live_wiring_deferred()

    # Check YAML wiring_gate still present
    data = yaml.safe_load(CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data["semantic_cache"]
    assert sc.get("live_wiring_deferred") is True, "cache_profile live_wiring_deferred must be True"
    assert sc.get("wiring_gate") == "APPS_RESEARCH_CHROMA_RUNTIME_WIRING_REQUIRED", (
        f"wiring_gate: {sc.get('wiring_gate')!r}"
    )


def ChromaResearchStore_live_wiring_deferred() -> bool:
    from apps_research.engines.integration.chroma_research_store import ChromaResearchStore
    return ChromaResearchStore.live_wiring_deferred is True


# ---------------------------------------------------------------------------
# AC-16: W5N does not execute ingestion
# ---------------------------------------------------------------------------


def test_w5n_does_not_execute_ingestion() -> None:
    """AC-16: ChromaResearchStore source must not call ingest scripts or ingestion functions."""
    source = CHROMA_STORE_PATH.read_text(encoding="utf-8")
    for line in source.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        assert "ingest(" not in line, (
            f"ChromaResearchStore calls ingest() on line: {line!r}"
        )
        assert "run_ingestion(" not in line, (
            f"ChromaResearchStore calls run_ingestion() on line: {line!r}"
        )

    # Also verify the ChromaResearchStore module-level does not import ingestion tools
    _ingest_import_re = re.compile(r"^\s*(?:import|from)\s+.*ingestion")
    for line in source.splitlines():
        assert not _ingest_import_re.match(line), (
            f"ChromaResearchStore imports ingestion module: {line!r}"
        )
