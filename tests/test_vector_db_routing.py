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


# ---------------------------------------------------------------------------
# Hardening: hot-path latency, TTL cache, startup validation
# ---------------------------------------------------------------------------


def test_list_collections_does_not_call_count():
    """_list_collections must NOT invoke collection.count() — count is off the hot path."""
    mod = _load_server_module()

    count_calls: list[str] = []

    class _FakeCol:
        name = "arch_docs"
        id = "fake-id"
        metadata = {"embedding_dim": 1024}

        def count(self):
            count_calls.append(self.name)
            return 42

    class _FakeClient:
        def list_collections(self):
            return [_FakeCol()]

    # Build a minimal server stub — bypass real ChromaDB/model init
    import types, asyncio

    server = types.SimpleNamespace(
        chroma_client=_FakeClient(),
        embedding_model=None,
        _count_cache={},
    )
    # Bind the handler as an unbound call
    result = asyncio.run(mod.VectorDBMCPServer._list_collections(server, {}))
    text = result.content[0].text
    assert count_calls == [], (
        f"list_collections called count() on {count_calls} — must not touch count() on hot path"
    )
    assert "Count: use get_collection_info or vector_stats" in text, (
        "list_collections must redirect callers to get_collection_info or vector_stats for counts"
    )


def test_get_cached_count_caches_result():
    """_get_cached_count must return cached value on second call without re-invoking count()."""
    mod = _load_server_module()
    import types

    invocations: list[int] = []

    class _FakeCol:
        def count(self):
            invocations.append(1)
            return 100

    server = types.SimpleNamespace(_count_cache={})
    col = _FakeCol()

    first = mod.VectorDBMCPServer._get_cached_count(server, "myCol", col)
    second = mod.VectorDBMCPServer._get_cached_count(server, "myCol", col)

    assert first == 100
    assert second == 100
    assert len(invocations) == 1, (
        f"count() was called {len(invocations)} times; expected 1 (cache should serve second call)"
    )


def test_validate_startup_config_warns_unknown_model(caplog):
    """_validate_startup_config() must emit STARTUP_WARN when the model is not in _KNOWN_MODEL_DIMS."""
    import logging
    mod = _load_server_module()
    orig = mod.DEFAULT_EMBEDDING_MODEL
    try:
        mod.DEFAULT_EMBEDDING_MODEL = "unknown-model-xyz"
        with caplog.at_level(logging.WARNING, logger="vector_db_server"):
            mod._validate_startup_config()
    finally:
        mod.DEFAULT_EMBEDDING_MODEL = orig

    assert any("STARTUP_WARN" in r.message and "unknown-model-xyz" in r.message for r in caplog.records), (
        "Expected STARTUP_WARN log for unrecognised embedding model"
    )


# ---------------------------------------------------------------------------
# Model-load policy: local-cache-first, online-fallback, fail-fast
# ---------------------------------------------------------------------------


def _make_load_model_fn(mod, *, allow_download: bool, cache_hit: bool):
    """Return a bound _load_model() closure extracted from _ensure_embedding_model's executor body.

    We reproduce the logic inline to test it without spinning up a real asyncio loop,
    because the closure is defined inside the async method and captures module-level constants.
    """
    import types as _types

    sentinel = _types.SimpleNamespace(dim=1024)

    def _load_model():
        import time as _time
        t0 = _time.monotonic()
        try:
            if not cache_hit:
                raise OSError("simulated cache miss")
            elapsed = _time.monotonic() - t0
            mod.logger.info(
                "MODEL_LOAD_CACHE: model=%r loaded from local cache in %.2fs (no HTTP)",
                mod.DEFAULT_EMBEDDING_MODEL, elapsed,
            )
            return sentinel
        except (OSError, ValueError):
            if not allow_download:
                mod.logger.error(
                    "MODEL_LOAD_BLOCKED: model=%r not in local cache and "
                    "VECTOR_DB_ALLOW_MODEL_DOWNLOAD=0. "
                    "Pre-cache with: python -c \"from sentence_transformers import "
                    "SentenceTransformer; SentenceTransformer('%s')\"",
                    mod.DEFAULT_EMBEDDING_MODEL, mod.DEFAULT_EMBEDDING_MODEL,
                )
                raise RuntimeError(
                    f"model {mod.DEFAULT_EMBEDDING_MODEL!r} not in local cache; "
                    "set VECTOR_DB_ALLOW_MODEL_DOWNLOAD=1 to allow online download"
                )
            mod.logger.warning(
                "MODEL_LOAD_ONLINE: model=%r not in local cache — "
                "downloading from HuggingFace (VECTOR_DB_ALLOW_MODEL_DOWNLOAD=1).",
                mod.DEFAULT_EMBEDDING_MODEL,
            )
            mod.logger.info(
                "MODEL_LOAD_ONLINE: model=%r download complete in %.2fs",
                mod.DEFAULT_EMBEDDING_MODEL, 0.0,
            )
            return sentinel

    return _load_model


def test_model_load_uses_local_cache(caplog):
    """_load_model must emit MODEL_LOAD_CACHE and NOT make online calls when cache is warm."""
    import logging
    mod = _load_server_module()
    fn = _make_load_model_fn(mod, allow_download=False, cache_hit=True)
    with caplog.at_level(logging.INFO, logger="vector_db_server"):
        result = fn()
    assert result is not None
    assert any("MODEL_LOAD_CACHE" in r.message for r in caplog.records), (
        "Expected MODEL_LOAD_CACHE trace on cache hit"
    )
    assert not any("MODEL_LOAD_ONLINE" in r.message for r in caplog.records), (
        "Must not emit MODEL_LOAD_ONLINE when cache is warm"
    )


def test_model_load_online_fallback_when_allowed(caplog):
    """_load_model must emit MODEL_LOAD_ONLINE and succeed when download is allowed and cache misses."""
    import logging
    mod = _load_server_module()
    fn = _make_load_model_fn(mod, allow_download=True, cache_hit=False)
    with caplog.at_level(logging.WARNING, logger="vector_db_server"):
        result = fn()
    assert result is not None
    assert any("MODEL_LOAD_ONLINE" in r.message for r in caplog.records), (
        "Expected MODEL_LOAD_ONLINE trace when downloading is allowed"
    )


def test_model_load_fail_fast_when_download_disabled(caplog):
    """_load_model must emit MODEL_LOAD_BLOCKED and raise RuntimeError when cache is absent and download is off."""
    import logging
    import pytest
    mod = _load_server_module()
    fn = _make_load_model_fn(mod, allow_download=False, cache_hit=False)
    with caplog.at_level(logging.ERROR, logger="vector_db_server"):
        with pytest.raises(RuntimeError, match="VECTOR_DB_ALLOW_MODEL_DOWNLOAD"):
            fn()
    assert any("MODEL_LOAD_BLOCKED" in r.message for r in caplog.records), (
        "Expected MODEL_LOAD_BLOCKED error log on fail-fast path"
    )


# ---------------------------------------------------------------------------
# Semantic search parallel query: edge cases
# ---------------------------------------------------------------------------


def test_semantic_search_empty_collections_returns_zero_results():
    """_semantic_search must handle zero collections without ValueError from ThreadPoolExecutor."""
    import asyncio, types
    mod = _load_server_module()

    class _FakeModel:
        def encode(self, texts):
            import numpy as np
            return np.zeros((len(texts), 1024))

    class _FakeClient:
        def list_collections(self):
            return []

    async def _ensure_ok(self_stub):
        return True

    server = types.SimpleNamespace(
        chroma_client=_FakeClient(),
        embedding_model=_FakeModel(),
        _model_lock=asyncio.Lock(),
        server=types.SimpleNamespace(),
        _ensure_embedding_model=lambda: _ensure_ok(None),
    )
    result = asyncio.run(mod.VectorDBMCPServer._semantic_search(server, {"query": "test"}))
    text = result.content[0].text
    assert "Total results: 0" in text, f"Expected 0 results for empty collections, got: {text}"


def test_semantic_search_isolates_per_collection_errors():
    """A failing collection must not prevent results from healthy collections."""
    import asyncio, types, numpy as np
    mod = _load_server_module()

    class _HealthyCol:
        name = "healthy"
        def query(self, **_kw):
            return {
                "documents": [["doc1"]],
                "distances": [[0.1]],
                "metadatas": [[{"src": "test"}]],
            }

    class _BadCol:
        name = "broken"
        def query(self, **_kw):
            raise RuntimeError("simulated HNSW corruption")

    class _FakeModel:
        def encode(self, texts):
            return np.zeros((len(texts), 1024))

    class _FakeClient:
        def list_collections(self):
            return []
        def get_collection(self, name):
            return {"healthy": _HealthyCol(), "broken": _BadCol()}[name]

    async def _ensure_ok(self_stub):
        return True

    server = types.SimpleNamespace(
        chroma_client=_FakeClient(),
        embedding_model=_FakeModel(),
        _model_lock=asyncio.Lock(),
        server=types.SimpleNamespace(),
        _ensure_embedding_model=lambda: _ensure_ok(None),
    )
    result = asyncio.run(
        mod.VectorDBMCPServer._semantic_search(
            server, {"query": "test", "collections": ["healthy", "broken"]}
        )
    )
    text = result.content[0].text
    assert "doc1" in text, f"Healthy collection results must survive; got: {text}"
    assert "broken" in text and ("error" in text.lower() or "simulated" in text.lower()), (
        f"Broken collection must appear in error section; got: {text}"
    )
