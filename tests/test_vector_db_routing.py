"""Regression proof for vector_db MCP path alignment and routing reachability.

Validates:
1. VECTOR_DB_CHROMA_PATH in mcp_config.json points at the canonical populated corpus.
2. The canonical corpus directory exists and contains at least one ChromaDB collection.
3. AGENTS.md Quick Reference includes a vector_db row.
4. _SR_MANDATE in pre_prompt_classifier.py names vector_db as a routing target.
5. _detect_semantic_retrieval() fires on a representative semantic query and is silent
   on a structural dependency query.

Example trigger query (should DETECT):
  "Find conceptually similar architecture passages about grounded retrieval and prompt
   assembly across the repo, not exact symbol matches."
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_CONFIG = REPO_ROOT / ".windsurf" / "mcp_config.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
PRE_PROMPT_CLASSIFIER = REPO_ROOT / ".windsurf" / "scripts" / "pre_prompt_classifier.py"
CANONICAL_CHROMA_PATH = REPO_ROOT / "data" / "cache" / "chromadb"


def _load_classifier_module():
    spec = importlib.util.spec_from_file_location("pre_prompt_classifier", PRE_PROMPT_CLASSIFIER)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# 6A: Path alignment
# ---------------------------------------------------------------------------


def test_vector_db_chroma_path_points_at_canonical_corpus():
    """VECTOR_DB_CHROMA_PATH must point at data/cache/chromadb, not artifacts/chroma."""
    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    path_value = config["mcpServers"]["vector_db"]["env"]["VECTOR_DB_CHROMA_PATH"]
    assert "data/cache/chromadb" in path_value.replace("\\", "/"), (
        f"VECTOR_DB_CHROMA_PATH is '{path_value}' — must contain data/cache/chromadb"
    )
    assert "artifacts/chroma" not in path_value.replace("\\", "/"), (
        f"VECTOR_DB_CHROMA_PATH still points at empty artifacts/chroma store: '{path_value}'"
    )


def test_canonical_chroma_path_is_populated():
    """data/cache/chromadb must exist and contain at least one ChromaDB collection directory."""
    assert CANONICAL_CHROMA_PATH.exists(), f"Canonical ChromaDB path does not exist: {CANONICAL_CHROMA_PATH}"
    collection_dirs = [
        d for d in CANONICAL_CHROMA_PATH.iterdir() if d.is_dir() and (d / "data_level0.bin").exists()
    ]
    assert len(collection_dirs) >= 1, (
        f"Canonical ChromaDB path has no populated collection dirs in {CANONICAL_CHROMA_PATH}"
    )


# ---------------------------------------------------------------------------
# 6B: Routing reachability
# ---------------------------------------------------------------------------


def test_agents_md_has_vector_db_row():
    """AGENTS.md Quick Reference must include a vector_db routing row."""
    content = AGENTS_MD.read_text(encoding="utf-8")
    assert "vector_db" in content, "AGENTS.md Quick Reference missing vector_db entry"
    assert "mcp11_semantic_search" in content, (
        "AGENTS.md Quick Reference missing mcp11_semantic_search tool reference"
    )


def test_sr_mandate_names_vector_db():
    """_SR_MANDATE in pre_prompt_classifier.py must include a vector_db routing clause."""
    source = PRE_PROMPT_CLASSIFIER.read_text(encoding="utf-8")
    mandate_match = re.search(r'_SR_MANDATE\s*=\s*"""(.*?)"""', source, re.DOTALL)
    assert mandate_match, "_SR_MANDATE constant not found in pre_prompt_classifier.py"
    mandate_body = mandate_match.group(1)
    assert "vector_db" in mandate_body, (
        "_SR_MANDATE does not mention vector_db — Cascade has no prompt-level trigger to select it"
    )
    assert "mcp11_semantic_search" in mandate_body, "_SR_MANDATE does not name mcp11_semantic_search"


# ---------------------------------------------------------------------------
# 6C: Detection function correctness
# ---------------------------------------------------------------------------


def test_detect_semantic_retrieval_fires_on_concept_query():
    """_detect_semantic_retrieval() must return True for a semantic retrieval query."""
    mod = _load_classifier_module()
    semantic_query = (
        "Find conceptually similar architecture passages about grounded retrieval "
        "and prompt assembly across the repo, not exact symbol matches."
    )
    assert mod._detect_semantic_retrieval(semantic_query) is True, (
        f"Expected DETECTED for semantic query: {semantic_query!r}"
    )


def test_detect_semantic_retrieval_silent_on_structural_query():
    """_detect_semantic_retrieval() must return False for a structural dependency query."""
    mod = _load_classifier_module()
    structural_query = "Who imports SemanticRetriever and what is the blast radius of changing it?"
    assert mod._detect_semantic_retrieval(structural_query) is False, (
        f"Expected NOT_DETECTED for structural query: {structural_query!r}"
    )


# ---------------------------------------------------------------------------
# 7F: Embedding model alignment in mcp_config.json
# ---------------------------------------------------------------------------


def test_mcp_config_uses_canonical_embedding_model():
    """VECTOR_DB_EMBEDDING_MODEL must be BAAI/bge-m3 to match the corpus (1024-dim)."""
    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    model = config["mcpServers"]["vector_db"]["env"]["VECTOR_DB_EMBEDDING_MODEL"]
    assert model == "BAAI/bge-m3", (
        f"VECTOR_DB_EMBEDDING_MODEL is '{model}' — must be 'BAAI/bge-m3' to match corpus (1024-dim)"
    )


# ---------------------------------------------------------------------------
# 7G: Startup alignment guard
# ---------------------------------------------------------------------------


def _load_server_module():
    server_path = REPO_ROOT / "tools" / "mcp" / "vector_db_server.py"
    spec = importlib.util.spec_from_file_location("vector_db_server", server_path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    # Stub out heavy imports so we can test pure logic without chromadb/torch
    import types

    stub_chromadb = types.ModuleType("chromadb")
    stub_chromadb.PersistentClient = object  # type: ignore[attr-defined]
    stub_chromadb.config = types.ModuleType("chromadb.config")  # type: ignore[attr-defined]
    stub_chromadb.config.Settings = lambda **kw: None  # type: ignore[attr-defined]
    import sys

    sys.modules.setdefault("chromadb", stub_chromadb)
    sys.modules.setdefault("chromadb.config", stub_chromadb.config)  # type: ignore[attr-defined]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_check_embedding_alignment_detects_mismatch(caplog):
    """_check_embedding_alignment() must log EMBEDDING_MISMATCH when dims differ."""
    import logging

    mod = _load_server_module()

    class _FakeCol:
        name = "arch_docs"
        metadata = {"embedding_dim": 1024, "embedding_model": "BAAI/bge-m3"}

    class _FakeClient:
        def list_collections(self):
            return [_FakeCol()]

    with caplog.at_level(logging.ERROR, logger="vector_db_server"):
        mod._check_embedding_alignment(_FakeClient(), "all-MiniLM-L6-v2")

    assert any("EMBEDDING_MISMATCH" in r.message for r in caplog.records), (
        "Expected EMBEDDING_MISMATCH error log when dim 384 ≠ corpus dim 1024"
    )


def test_check_embedding_alignment_ok_on_match(caplog):
    """_check_embedding_alignment() must log EMBEDDING_ALIGNMENT_OK when dims match."""
    import logging

    mod = _load_server_module()

    class _FakeCol:
        name = "arch_docs"
        metadata = {"embedding_dim": 1024, "embedding_model": "BAAI/bge-m3"}

    class _FakeClient:
        def list_collections(self):
            return [_FakeCol()]

    with caplog.at_level(logging.INFO, logger="vector_db_server"):
        mod._check_embedding_alignment(_FakeClient(), "BAAI/bge-m3")

    assert any("EMBEDDING_ALIGNMENT_OK" in r.message for r in caplog.records), (
        "Expected EMBEDDING_ALIGNMENT_OK info log when model dim 1024 matches corpus dim 1024"
    )
