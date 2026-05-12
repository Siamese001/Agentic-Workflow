"""W6 tests: real BAAI/bge-m3 embeddings and dry-run-safe ingestion pipeline.

GAP-06: Zero-vector stub replaced with real sentence-transformers embedding.
GAP-07: Dry-run-safe ingestion pipeline for process_docs collection.

Tests prove:
  - ChromaResearchStore._embed() uses SentenceTransformer (not zero vectors)
  - _embed() returns a 1024-dimensional vector
  - No zero-vector fallback in Chroma path
  - Missing sentence-transformers raises clear ImportError
  - InMemoryResearchStore (chromadb_path=None) is unchanged
  - Ingestion pipeline has --dry-run flag
  - dry-run exits 0
  - dry-run creates no Chroma collection
  - Ingestion requires --execute for writes
  - Ingestion targets process_docs collection
  - Ingestion uses BAAI/bge-m3 / 1024 dims
  - No L4 write path in ingestion
  - apps_lic untouched
  - apps_rg untouched
  - apps_rg/cache/r1b_adapter.py quarantine untouched
  - W1-W5 regression tests still pass
"""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import unittest.mock as mock
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent

CHROMA_STORE_MOD = "apps_research.engines.integration.chroma_research_store"
PIPELINE_PATH = REPO_ROOT / "tools" / "ingestion" / "chroma_ingest_pipeline.py"


def _import_pipeline():
    spec = importlib.util.spec_from_file_location("chroma_ingest_pipeline", PIPELINE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# W6-01: ChromaResearchStore._embed() uses SentenceTransformer
# ---------------------------------------------------------------------------


def test_chroma_research_store_embed_uses_sentence_transformer():
    """_embed() must call SentenceTransformer.encode(), not return a zero vector."""
    import apps_research.engines.integration.chroma_research_store as m

    fake_vector = [0.1] * 1024

    fake_model = mock.MagicMock()
    fake_model.encode.return_value = type("A", (), {"tolist": lambda self: fake_vector})()

    # Reset the class-level model cache so our mock is used
    original_model = m.ChromaResearchStore._model
    m.ChromaResearchStore._model = fake_model
    try:
        store = m.ChromaResearchStore.__new__(m.ChromaResearchStore)
        store._chromadb_path = "/fake"
        store._client = None
        store._collection = None
        result = store._embed("hello world")
    finally:
        m.ChromaResearchStore._model = original_model

    fake_model.encode.assert_called_once_with("hello world", normalize_embeddings=True)
    assert result == fake_vector


# ---------------------------------------------------------------------------
# W6-02: _embed() returns 1024-dimensional vector
# ---------------------------------------------------------------------------


def test_chroma_research_store_embed_returns_1024_dim_vector():
    """_embed() must return a vector of length 1024 (EMBEDDING_DIMENSIONS)."""
    import apps_research.engines.integration.chroma_research_store as m

    fake_vector = [float(i % 10) / 10.0 for i in range(1024)]
    fake_model = mock.MagicMock()
    fake_model.encode.return_value = type("A", (), {"tolist": lambda self: fake_vector})()

    original_model = m.ChromaResearchStore._model
    m.ChromaResearchStore._model = fake_model
    try:
        store = m.ChromaResearchStore.__new__(m.ChromaResearchStore)
        store._chromadb_path = "/fake"
        store._client = None
        store._collection = None
        result = store._embed("test text")
    finally:
        m.ChromaResearchStore._model = original_model

    assert len(result) == 1024, f"Expected 1024 dims, got {len(result)}"
    assert result == fake_vector


# ---------------------------------------------------------------------------
# W6-03: No zero-vector fallback in Chroma path
# ---------------------------------------------------------------------------


def test_chroma_research_store_no_zero_vector_fallback_in_chroma_path():
    """_embed() must NOT return a list of all-zeros in the ChromaResearchStore path.

    The zero-vector stub was removed in W6. We verify the source code no longer
    contains the stub pattern and that _embed does NOT silently return zeros.
    """
    store_path = (
        REPO_ROOT / "apps_research" / "engines" / "integration" / "chroma_research_store.py"
    )
    source = store_path.read_text(encoding="utf-8")

    # The old stub was: return [0.0] * EMBEDDING_DIMENSIONS
    assert "return [0.0] * EMBEDDING_DIMENSIONS" not in source, (
        "Zero-vector stub still present in ChromaResearchStore._embed(). "
        "W6 requires this to be replaced with real sentence-transformers embedding."
    )

    # Confirm _get_model and SentenceTransformer references are present
    assert "_get_model" in source, "_get_model lazy-loader missing from chroma_research_store.py"
    assert "SentenceTransformer" in source, "SentenceTransformer reference missing from chroma_research_store.py"


# ---------------------------------------------------------------------------
# W6-04: Missing sentence-transformers raises clear ImportError
# ---------------------------------------------------------------------------


def test_sentence_transformers_missing_raises_clear_error():
    """If sentence-transformers is not installed, _get_model() must raise ImportError
    with an install hint — not silently fall back."""
    import apps_research.engines.integration.chroma_research_store as m

    original_model = m.ChromaResearchStore._model
    m.ChromaResearchStore._model = None  # force reload path
    try:
        with mock.patch.dict(sys.modules, {"sentence_transformers": None}):
            with pytest.raises(ImportError) as exc_info:
                m.ChromaResearchStore._get_model()
    finally:
        m.ChromaResearchStore._model = original_model

    msg = str(exc_info.value)
    assert "sentence-transformers" in msg.lower(), (
        f"ImportError message should mention 'sentence-transformers', got: {msg!r}"
    )
    assert "pip install" in msg, (
        f"ImportError message should contain pip install hint, got: {msg!r}"
    )


# ---------------------------------------------------------------------------
# W6-05: InMemoryResearchStore (chromadb_path=None) still uses test/dev path
# ---------------------------------------------------------------------------


def test_in_memory_store_still_uses_test_dev_path():
    """create_retrieval_engine(chromadb_path=None) must return a ResearchRetrievalEngine
    backed by InMemoryResearchStore — unchanged from W5N."""
    from apps_research.engines.research_retrieval_engine import (
        InMemoryResearchStore,
        ResearchRetrievalEngine,
        create_retrieval_engine,
    )

    engine = create_retrieval_engine(chromadb_path=None)
    assert isinstance(engine, ResearchRetrievalEngine)
    assert isinstance(engine.store, InMemoryResearchStore), (
        "chromadb_path=None must produce an InMemoryResearchStore, not a ChromaResearchStore"
    )


# ---------------------------------------------------------------------------
# W6-06: Ingestion pipeline has --dry-run flag
# ---------------------------------------------------------------------------


def test_ingestion_pipeline_has_dry_run():
    """chroma_ingest_pipeline must expose a --dry-run argument."""
    pipeline = _import_pipeline()
    parser = pipeline.build_parser()
    # Verify --dry-run is recognised (no error)
    args = parser.parse_args(["--dry-run"])
    assert args.dry_run is True


# ---------------------------------------------------------------------------
# W6-07: dry-run exits 0
# ---------------------------------------------------------------------------


def test_ingestion_dry_run_exits_zero():
    """Running chroma_ingest_pipeline without --execute must exit 0."""
    pipeline = _import_pipeline()
    # No --execute → dry-run mode
    exit_code = pipeline.main(["--dry-run"])
    assert exit_code == 0, f"Expected exit 0 from dry-run, got {exit_code}"


# ---------------------------------------------------------------------------
# W6-08: dry-run creates no Chroma collection
# ---------------------------------------------------------------------------


def test_ingestion_dry_run_creates_no_chroma_collection():
    """dry-run must not call chromadb or create any collection."""
    pipeline = _import_pipeline()

    with mock.patch.dict(sys.modules, {"chromadb": mock.MagicMock()}) as patched:
        chroma_mock = patched["chromadb"]
        exit_code = pipeline.main(["--dry-run"])

    assert exit_code == 0
    # PersistentClient must NOT have been called
    chroma_mock.PersistentClient.assert_not_called()


# ---------------------------------------------------------------------------
# W6-09: Ingestion requires explicit --execute for writes
# ---------------------------------------------------------------------------


def test_ingestion_requires_explicit_execute_for_writes():
    """Without --execute, main() must NOT call run_ingestion() or any Chroma write."""
    pipeline = _import_pipeline()

    with mock.patch.object(pipeline, "run_ingestion") as mock_ingest:
        exit_code = pipeline.main([])  # no --execute

    assert exit_code == 0
    mock_ingest.assert_not_called()


# ---------------------------------------------------------------------------
# W6-10: Ingestion targets process_docs collection
# ---------------------------------------------------------------------------


def test_ingestion_targets_process_docs_collection():
    """COLLECTION_NAME must be 'process_docs'."""
    pipeline = _import_pipeline()
    assert pipeline.COLLECTION_NAME == "process_docs", (
        f"Expected collection 'process_docs', got {pipeline.COLLECTION_NAME!r}"
    )


# ---------------------------------------------------------------------------
# W6-11: Ingestion uses BAAI/bge-m3 / 1024 dims
# ---------------------------------------------------------------------------


def test_ingestion_uses_bge_m3_1024():
    """Pipeline constants must declare BAAI/bge-m3 and 1024 dimensions."""
    pipeline = _import_pipeline()
    assert pipeline.EMBEDDING_MODEL == "BAAI/bge-m3", (
        f"Expected EMBEDDING_MODEL='BAAI/bge-m3', got {pipeline.EMBEDDING_MODEL!r}"
    )
    assert pipeline.EMBEDDING_DIMENSIONS == 1024, (
        f"Expected EMBEDDING_DIMENSIONS=1024, got {pipeline.EMBEDDING_DIMENSIONS}"
    )


# ---------------------------------------------------------------------------
# W6-12: No L4 write path in ingestion pipeline
# ---------------------------------------------------------------------------


def test_no_l4_write_path_in_ingestion():
    """chroma_ingest_pipeline.py must not import from agentic_core.L4_state."""
    source = PIPELINE_PATH.read_text(encoding="utf-8")
    assert "agentic_core.L4_state" not in source, (
        "chroma_ingest_pipeline.py must not import L4_state — "
        "it is a tooling-layer script, not a runtime path"
    )
    assert "L4_state" not in source, (
        "chroma_ingest_pipeline.py must not reference L4_state"
    )


# ---------------------------------------------------------------------------
# W6-13: apps_lic untouched by W6
# ---------------------------------------------------------------------------


def test_apps_lic_untouched_by_w6():
    """W6 must not modify any apps_lic files."""
    import subprocess as sp
    result = sp.run(
        [sys.executable, "-m", "pytest",
         "tests/_apps_contract/test_w1_core_r1b_cache_wiring.py",
         "-q", "--tb=short", "--no-header",
         "-k", "apps_lic"],
        capture_output=True, text=True, timeout=60,
        cwd=str(REPO_ROOT),
    )
    # apps_lic-specific R1B tests should still pass
    assert result.returncode == 0 or "no tests ran" in result.stdout.lower(), (
        f"apps_lic W1 tests failed after W6:\n{result.stdout}\n{result.stderr}"
    )

    # Verify apps_lic cache profile is still disabled
    apps_lic_cache = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
    content = apps_lic_cache.read_text(encoding="utf-8")
    assert "enabled: false" in content or "enabled: False" in content, (
        "apps_lic semantic cache must remain disabled — W6 must not touch apps_lic"
    )


# ---------------------------------------------------------------------------
# W6-14: apps_rg untouched by W6
# ---------------------------------------------------------------------------


def test_apps_rg_untouched_by_w6():
    """W6 must not modify apps_rg cache profile or route profiles."""
    apps_rg_cache = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
    content = apps_rg_cache.read_text(encoding="utf-8")
    # W5 set live_wiring_deferred: false — that must be preserved
    assert "live_wiring_deferred: false" in content, (
        "apps_rg cache profile W5 flip must be preserved — W6 must not touch apps_rg"
    )
    assert "CLEARED_BY_W1_GENERIC_R1B_CACHE_WIRING" in content, (
        "apps_rg wiring_gate W5 value must be preserved — W6 must not touch apps_rg"
    )


# ---------------------------------------------------------------------------
# W6-15: apps_rg/cache/r1b_adapter.py quarantine untouched
# ---------------------------------------------------------------------------


def test_apps_rg_r1b_adapter_quarantine_untouched():
    """apps_rg/cache/r1b_adapter.py must still be quarantined (raises RuntimeError on import)."""
    r1b_path = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
    assert r1b_path.exists(), "apps_rg/cache/r1b_adapter.py must still exist"
    source = r1b_path.read_text(encoding="utf-8")
    assert "RuntimeError" in source, (
        "apps_rg/cache/r1b_adapter.py quarantine guard (RuntimeError) must be intact"
    )


# ---------------------------------------------------------------------------
# W6-16: W1-W5 regression tests still pass
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("test_path,label", [
    ("tests/_apps_contract/test_w1_core_r1b_cache_wiring.py", "W1-R1B"),
    ("tests/_apps_contract/test_w2_route_contract_graph_policy.py", "W2-RouteContract"),
    ("tests/_apps_contract/test_w3_c03_adapter_registry.py", "W3-AdapterRegistry"),
    ("tests/_apps_contract/test_w4_graph_rag_execution.py", "W4-GraphRAG"),
    ("tests/_apps_contract/test_w5_apps_rg_r1b_rca_decision.py", "W5-RCA"),
])
def test_w1_w5_regressions_still_pass(test_path, label):
    """W1-W5 regression tests must still pass after W6 changes."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path,
         "-q", "--tb=short", "--no-header"],
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        f"{label} regression tests failed after W6:\n{result.stdout}\n{result.stderr}"
    )
