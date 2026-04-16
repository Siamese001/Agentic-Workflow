"""Unit tests for NativePersistentCacheClient integration in SemanticCacheManager"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SemanticCacheManager = pytest.importorskip(
    "agentic_core.L4_state.utils.memory.semantic_cache_manager",
    reason="Semantic cache manager module unavailable for GPTCache integration tests",
).SemanticCacheManager


def test_semantic_cache_manager_imports_gptcache() -> None:
    """Test that SemanticCacheManager can import NativePersistentCacheClient (via GPTCacheClient alias)."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import GPTCacheClient

        assert GPTCacheClient is not None
    except ImportError:
        pytest.skip("ChromaDB not installed")


def test_semantic_cache_manager_initializes_gptcache() -> None:
    """Test that SemanticCacheManager initializes NativePersistentCacheClient in _initialize."""
    # Reset singleton
    SemanticCacheManager._instance = None

    with (
        patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "1"}),
        patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mock_gptcache,
    ):
        mock_instance = MagicMock()
        mock_instance._cache = "real"  # Not mock mode
        mock_gptcache.return_value = mock_instance

        cache = SemanticCacheManager.get_instance()

        # Verify GPTCacheClient was instantiated
        mock_gptcache.assert_called_once()

        # Verify gptcache_enabled is True
        assert cache.gptcache_enabled is True
        assert cache._gptcache is not None


def test_semantic_cache_manager_gptcache_mock_fallback() -> None:
    """Test that SemanticCacheManager degrades gracefully when NativePersistentCacheClient is in mock mode."""
    # Reset singleton
    SemanticCacheManager._instance = None

    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mock_gptcache:
        mock_instance = MagicMock()
        mock_instance._cache = "mock"  # Mock mode
        mock_gptcache.return_value = mock_instance

        cache = SemanticCacheManager.get_instance()

        # Verify gptcache_enabled is False when in mock mode
        assert cache.gptcache_enabled is False


def test_semantic_cache_manager_gptcache_import_failure() -> None:
    """Test that SemanticCacheManager degrades gracefully when NativePersistentCacheClient import fails."""
    # Reset singleton
    SemanticCacheManager._instance = None

    with patch(
        "agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient", side_effect=ImportError
    ):
        cache = SemanticCacheManager.get_instance()

        # Verify gptcache_enabled is False on import failure
        assert cache.gptcache_enabled is False


def test_semantic_cache_manager_recall_uses_gptcache() -> None:
    """Test that recall method uses NativePersistentCacheClient when enabled."""
    # Reset singleton
    SemanticCacheManager._instance = None

    with (
        patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "1"}),
        patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mock_gptcache,
    ):
        mock_instance = MagicMock()
        mock_instance._cache = "real"
        # Return JSON string with _metadata namespace to match implementation
        mock_instance.get.return_value = '{"result": "cached", "_metadata": {"namespace": "test_namespace"}}'
        mock_gptcache.return_value = mock_instance

        cache = SemanticCacheManager.get_instance()

        # Disable Redis to force L2 cache usage
        cache.redis_enabled = False

        # Call recall
        result = cache.recall("test context", "test_namespace")

        # Verify GPTCache.get was called
        mock_instance.get.assert_called_once()
        # Verify result was returned (namespace match)
        assert result is not None
        assert result["result"] == "cached"


def test_semantic_cache_manager_promote_uses_gptcache() -> None:
    """Test that promote_to_long_term uses NativePersistentCacheClient when enabled."""
    import asyncio

    # Reset singleton
    SemanticCacheManager._instance = None

    with (
        patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "1"}),
        patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mock_gptcache,
    ):
        mock_instance = MagicMock()
        mock_instance._cache = "real"
        mock_gptcache.return_value = mock_instance

        cache = SemanticCacheManager.get_instance()

        # Phase B: payload must carry evidence_ids + grounding_complete
        result = asyncio.run(
            cache.promote_to_long_term(
                "test context",
                "test_namespace",
                {"result": "test", "evidence_ids": ["doc1"], "grounding_complete": True},
                0.9,  # Above default threshold
            )
        )

        # Verify GPTCache.set was called
        mock_instance.set.assert_called_once()


def test_semantic_cache_manager_stats_include_gptcache_hits() -> None:
    """Test that get_statistics includes gptcache_hits (L2 cache hits)."""
    # Reset singleton
    SemanticCacheManager._instance = None

    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mock_gptcache:
        mock_instance = MagicMock()
        mock_instance._cache = "real"
        mock_gptcache.return_value = mock_instance

        cache = SemanticCacheManager.get_instance()

        # Increment gptcache_hits
        with cache._lock:
            cache.stats["gptcache_hits"] = 5

        stats = cache.get_statistics()

        # Verify gptcache_hits is in stats
        assert "gptcache_hits" in stats
        assert stats["gptcache_hits"] == 5
        assert stats["total_hits"] == 5 + stats["redis_hits"]


# ---------------------------------------------------------------------------
# Phase B targeted tests
# ---------------------------------------------------------------------------


def _make_real_cache(tmp_path: "Path") -> "NativePersistentCacheClient":
    """Helper: return a real NativePersistentCacheClient or skip if ChromaDB absent."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")
    client = NativePersistentCacheClient(cache_dir=str(tmp_path))
    if client._cache == "mock":
        pytest.skip("ChromaDB not available")
    return client


def test_schema_migration_includes_new_columns(tmp_path: Path) -> None:
    """Phase B: _init_sqlite must create all Phase B columns."""
    client = _make_real_cache(tmp_path)
    cursor = client._sqlite_conn.cursor()
    cursor.execute("PRAGMA table_info(l2_cache)")
    cols = {row[1] for row in cursor.fetchall()}
    for expected in (
        "tenant_id",
        "embedding_model_id",
        "corpus_version",
        "evidence_ids",
        "grounding_complete",
        "policy_version",
        "ttl_seconds",
        "expires_at",
        "entry_schema_version",
    ):
        assert expected in cols, f"Missing column: {expected}"
    client.close()


def test_set_writes_all_contract_fields(tmp_path: Path) -> None:
    """Phase B: set() must persist all contract fields to SQLite."""
    client = _make_real_cache(tmp_path)
    client.set(
        "hello world",
        "response",
        tenant_id="tenant-a",
        embedding_model_id="bge-m3-v1",
        corpus_version="a" * 64,
        evidence_ids=["doc1", "doc2"],
        grounding_complete=True,
        policy_version="v1",
        ttl_seconds=7200,
        entry_schema_version=1,
    )
    cursor = client._sqlite_conn.cursor()
    import hashlib as _hl

    qid = _hl.sha256(b"hello world").hexdigest()
    cursor.execute(
        "SELECT tenant_id, embedding_model_id, corpus_version, evidence_ids,"
        " grounding_complete, policy_version, ttl_seconds, entry_schema_version"
        " FROM l2_cache WHERE id = ?",
        (qid,),
    )
    row = cursor.fetchone()
    assert row is not None, "Row not written"
    assert row[0] == "tenant-a"
    assert row[1] == "bge-m3-v1"
    assert row[2] == "a" * 64
    import json as _j

    assert _j.loads(row[3]) == ["doc1", "doc2"]
    assert row[4] == 1  # grounding_complete stored as INTEGER
    assert row[5] == "v1"
    assert row[6] == 7200
    assert row[7] == 1
    client.close()


def test_get_rejects_tenant_mismatch(tmp_path: Path) -> None:
    """Phase B: get() must return None when tenant_id does not match stored entry."""
    client = _make_real_cache(tmp_path)
    client.set("query tenant test", "resp", tenant_id="tenant-a")
    result = client.get("query tenant test", tenant_id="tenant-b")
    assert result is None
    client.close()


def test_get_rejects_model_mismatch(tmp_path: Path) -> None:
    """Phase B: get() must return None when embedding_model_id does not match."""
    client = _make_real_cache(tmp_path)
    client.set("query model test", "resp", embedding_model_id="model-x")
    result = client.get("query model test", embedding_model_id="model-y")
    assert result is None
    client.close()


def test_get_rejects_expired_entry(tmp_path: Path) -> None:
    """Phase B: get() must return None when expires_at is in the past."""
    import hashlib as _hl

    client = _make_real_cache(tmp_path)
    client.set("query expiry test", "resp", ttl_seconds=86400)
    qid = _hl.sha256(b"query expiry test").hexdigest()
    # Back-date expires_at to yesterday
    import datetime as _dt

    past = (_dt.datetime.utcnow() - _dt.timedelta(hours=1)).isoformat()
    client._sqlite_conn.execute("UPDATE l2_cache SET expires_at = ? WHERE id = ?", (past, qid))
    client._sqlite_conn.commit()
    result = client.get("query expiry test")
    assert result is None
    client.close()


def test_search_similar_passes_where_filter(tmp_path: Path) -> None:
    """Phase B: search_similar() builds metadata filter for tenant and model."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")
    from unittest.mock import MagicMock, patch

    client = NativePersistentCacheClient(cache_dir=str(tmp_path))
    # Force real mode with mocked chroma collection
    client._cache = "real"
    mock_collection = MagicMock()
    mock_collection.query.return_value = {"ids": [[]], "distances": [[]]}
    client._chroma_collection = mock_collection
    client.search_similar("q", tenant_id="t1", embedding_model_id="m1")
    call_kwargs = mock_collection.query.call_args[1]
    assert "where" in call_kwargs
    where = call_kwargs["where"]
    # Both filters present → $and clause
    assert "$and" in where
    clauses = where["$and"]
    keys = {list(c.keys())[0] for c in clauses}
    assert "tenant_id" in keys
    assert "embedding_model_id" in keys


def test_promote_rejected_when_evidence_ids_empty() -> None:
    """Phase B: promote_to_long_term must reject when evidence_ids is empty."""
    import asyncio

    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        result = asyncio.run(
            cache.promote_to_long_term(
                "ctx",
                "ns",
                {"result": "x", "evidence_ids": [], "grounding_complete": True},
                0.9,
            )
        )
    assert result is False
    mock_l2.set.assert_not_called()


def test_promote_rejected_when_grounding_incomplete() -> None:
    """Phase B: promote_to_long_term must reject when grounding_complete is False."""
    import asyncio

    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        result = asyncio.run(
            cache.promote_to_long_term(
                "ctx",
                "ns",
                {"result": "x", "evidence_ids": ["d1"], "grounding_complete": False},
                0.9,
            )
        )
    assert result is False
    mock_l2.set.assert_not_called()


def test_compute_hash_uses_d2_key_with_tenant() -> None:
    """Phase B: _compute_hash must delegate to build_semantic_cache_d2_key when tenant_id is set."""
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mc.return_value = MagicMock(_cache="real")
        cache = SemanticCacheManager.get_instance()
    corpus = "a" * 64  # already 64-hex, no re-hashing
    h_with_tenant = cache._compute_hash("hello", "ns", tenant_id="tenant-x", corpus_version=corpus)
    h_without_tenant = cache._compute_hash("hello", "ns")
    assert h_with_tenant != h_without_tenant, "D2 key and legacy key must differ"
    assert h_with_tenant.startswith("d2_scache:tenant-x:"), f"Expected D2 prefix, got {h_with_tenant!r}"


# ---------------------------------------------------------------------------
# Phase C targeted tests
# ---------------------------------------------------------------------------


def test_get_hard_evicts_expired_entry(tmp_path: Path) -> None:
    """Phase C: get() must DELETE expired entry from SQLite and return None."""
    import hashlib as _hl
    import datetime as _dt

    client = _make_real_cache(tmp_path)
    client.set("hard evict query", "resp", ttl_seconds=86400)
    qid = _hl.sha256(b"hard evict query").hexdigest()
    past = (_dt.datetime.utcnow() - _dt.timedelta(hours=1)).isoformat()
    client._sqlite_conn.execute("UPDATE l2_cache SET expires_at = ? WHERE id = ?", (past, qid))
    client._sqlite_conn.commit()

    result = client.get("hard evict query")
    assert result is None

    # Entry must be gone from SQLite
    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT id FROM l2_cache WHERE id = ?", (qid,))
    assert cursor.fetchone() is None, "Expired entry should have been deleted"
    client.close()


def test_get_leaves_unexpired_entries_untouched(tmp_path: Path) -> None:
    """Phase C: get() must NOT evict entries that are still valid."""
    import hashlib as _hl

    client = _make_real_cache(tmp_path)
    client.set("valid query", "my_response", ttl_seconds=86400)
    qid = _hl.sha256(b"valid query").hexdigest()

    result = client.get("valid query")
    assert result == "my_response"

    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT id FROM l2_cache WHERE id = ?", (qid,))
    assert cursor.fetchone() is not None, "Valid entry must not be evicted"
    client.close()


def test_search_similar_excludes_expired_entries(tmp_path: Path) -> None:
    """Phase C: search_similar() must skip expired candidates and evict them."""
    import hashlib as _hl
    import datetime as _dt

    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")
    client = NativePersistentCacheClient(cache_dir=str(tmp_path))
    if client._cache == "mock":
        pytest.skip("ChromaDB not available")

    client.set("search expired query", "expired_resp", ttl_seconds=86400)
    qid = _hl.sha256(b"search expired query").hexdigest()
    past = (_dt.datetime.utcnow() - _dt.timedelta(hours=1)).isoformat()
    client._sqlite_conn.execute("UPDATE l2_cache SET expires_at = ? WHERE id = ?", (past, qid))
    client._sqlite_conn.commit()

    results = client.search_similar("search expired query")
    # The expired entry must be filtered out
    for r in results:
        assert r["metadata"]["payload"] != "expired_resp"

    # And must be deleted from SQLite
    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT id FROM l2_cache WHERE id = ?", (qid,))
    assert cursor.fetchone() is None, "Expired entry should have been hard-evicted"
    client.close()


def test_cleanup_expired_removes_expired_entries(tmp_path: Path) -> None:
    """Phase C: cleanup_expired() must delete expired rows and return correct count."""
    import hashlib as _hl
    import datetime as _dt

    client = _make_real_cache(tmp_path)

    client.set("exp1", "r1", ttl_seconds=86400)
    client.set("exp2", "r2", ttl_seconds=86400)
    client.set("valid", "r3", ttl_seconds=86400)

    past = (_dt.datetime.utcnow() - _dt.timedelta(hours=1)).isoformat()
    id1 = _hl.sha256(b"exp1").hexdigest()
    id2 = _hl.sha256(b"exp2").hexdigest()
    client._sqlite_conn.execute("UPDATE l2_cache SET expires_at = ? WHERE id = ?", (past, id1))
    client._sqlite_conn.execute("UPDATE l2_cache SET expires_at = ? WHERE id = ?", (past, id2))
    client._sqlite_conn.commit()

    evicted = client.cleanup_expired()
    assert evicted == 2

    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM l2_cache WHERE id IN (?, ?)", (id1, id2))
    assert cursor.fetchone()[0] == 0, "Expired entries must be deleted"
    # valid entry untouched
    valid_id = _hl.sha256(b"valid").hexdigest()
    cursor.execute("SELECT id FROM l2_cache WHERE id = ?", (valid_id,))
    assert cursor.fetchone() is not None, "Valid entry must remain"
    client.close()


def test_invalidate_by_corpus_version(tmp_path: Path) -> None:
    """Phase C: invalidate_by(corpus_version=...) deletes only matching entries."""
    import hashlib as _hl

    client = _make_real_cache(tmp_path)
    cv_a = "a" * 64
    cv_b = "b" * 64
    client.set("q1", "r1", corpus_version=cv_a)
    client.set("q2", "r2", corpus_version=cv_a)
    client.set("q3", "r3", corpus_version=cv_b)

    count = client.invalidate_by(corpus_version=cv_a)
    assert count == 2

    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM l2_cache WHERE corpus_version = ?", (cv_a,))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM l2_cache WHERE corpus_version = ?", (cv_b,))
    assert cursor.fetchone()[0] == 1
    client.close()


def test_invalidate_by_embedding_model_id(tmp_path: Path) -> None:
    """Phase C: invalidate_by(embedding_model_id=...) deletes only matching entries."""
    client = _make_real_cache(tmp_path)
    client.set("q_m1", "r", embedding_model_id="model-old")
    client.set("q_m2", "r", embedding_model_id="model-old")
    client.set("q_m3", "r", embedding_model_id="model-new")

    count = client.invalidate_by(embedding_model_id="model-old")
    assert count == 2

    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM l2_cache WHERE embedding_model_id = ?", ("model-old",))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM l2_cache WHERE embedding_model_id = ?", ("model-new",))
    assert cursor.fetchone()[0] == 1
    client.close()


def test_invalidate_by_tenant_id(tmp_path: Path) -> None:
    """Phase C: invalidate_by(tenant_id=...) deletes only matching entries."""
    client = _make_real_cache(tmp_path)
    client.set("q_ta", "r", tenant_id="tenant-a")
    client.set("q_tb", "r", tenant_id="tenant-b")

    count = client.invalidate_by(tenant_id="tenant-a")
    assert count == 1

    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM l2_cache WHERE tenant_id = ?", ("tenant-a",))
    assert cursor.fetchone()[0] == 0
    cursor.execute("SELECT COUNT(*) FROM l2_cache WHERE tenant_id = ?", ("tenant-b",))
    assert cursor.fetchone()[0] == 1
    client.close()


def test_invalidate_by_all_none_raises() -> None:
    """Phase C: invalidate_by() with no params must raise ValueError."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")
    client = NativePersistentCacheClient.__new__(NativePersistentCacheClient)
    client._cache = "real"
    with pytest.raises(ValueError, match="requires at least one"):
        client.invalidate_by()


def test_invalidate_cache_delegates_to_gptcache() -> None:
    """Phase C: SemanticCacheManager.invalidate_cache() delegates to _gptcache.invalidate_by()."""
    SemanticCacheManager._instance = None
    with (
        patch.dict("os.environ", {"SEMANTIC_CACHE_D2_ENABLED": "1"}),
        patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc,
    ):
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mock_l2.invalidate_by.return_value = 3
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        count = cache.invalidate_cache(tenant_id="t1")
    assert count == 3
    mock_l2.invalidate_by.assert_called_once_with(
        tenant_id="t1", corpus_version=None, embedding_model_id=None
    )


def test_native_persistent_cache_close_called(tmp_path) -> None:
    """Test that close() method is called on NativePersistentCacheClient to prevent resource leaks."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")

    # Create cache instance in an isolated tmp_path to avoid EF conflict with stale persistent state
    cache = NativePersistentCacheClient(cache_dir=str(tmp_path / "test_close"))

    # Verify it's in real mode
    if cache._cache == "mock":
        pytest.skip("ChromaDB not available, using mock mode")

    # Call close
    cache.close()

    # Verify close was successful (no exception raised)
    assert True


# ---------------------------------------------------------------------------
# Phase D targeted tests
# ---------------------------------------------------------------------------


def test_recall_replay_mode_bypasses_cache() -> None:
    """Phase D: replay_mode=True bypasses all storage reads; no Redis or L2 calls made."""
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mock_l2.get.return_value = None
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        mock_redis = MagicMock()
        mock_redis.get.return_value = '{"result": "would_be_hit"}'
        cache.redis_client = mock_redis
        cache.redis_enabled = True

        result = cache.recall("ctx", "ns", tenant_id="t1", replay_mode=True)

    assert result is None
    mock_redis.get.assert_not_called()
    mock_l2.get.assert_not_called()


def test_recall_flow_class_d4_action_bypasses() -> None:
    """Phase D: flow_class='D4_ACTION' (in MUST_BYPASS_FLOWS) bypasses all storage reads."""
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        mock_redis = MagicMock()
        mock_redis.get.return_value = '{"result": "would_be_hit"}'
        cache.redis_client = mock_redis
        cache.redis_enabled = True

        result = cache.recall("ctx", "ns", tenant_id="t1", flow_class="D4_ACTION")

    assert result is None
    mock_redis.get.assert_not_called()
    mock_l2.get.assert_not_called()


def test_recall_flow_class_hitl_bypasses() -> None:
    """Phase D: flow_class='HITL' (in MUST_BYPASS_FLOWS) bypasses all storage reads."""
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        mock_redis = MagicMock()
        mock_redis.get.return_value = '{"result": "would_be_hit"}'
        cache.redis_client = mock_redis
        cache.redis_enabled = True

        result = cache.recall("ctx", "ns", tenant_id="t1", flow_class="HITL")

    assert result is None
    mock_redis.get.assert_not_called()


def test_recall_flow_class_uwg_write_bypasses() -> None:
    """Phase D: flow_class='UWG_WRITE' (in MUST_BYPASS_FLOWS) bypasses all storage reads."""
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        mock_redis = MagicMock()
        mock_redis.get.return_value = '{"result": "would_be_hit"}'
        cache.redis_client = mock_redis
        cache.redis_enabled = True

        result = cache.recall("ctx", "ns", tenant_id="t1", flow_class="UWG_WRITE")

    assert result is None
    mock_redis.get.assert_not_called()


def test_recall_allowed_flow_class_returns_hit() -> None:
    """Phase D: allowed flow_class (not in MUST_BYPASS_FLOWS) follows normal recall path — hit."""
    import json as _json

    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        mock_redis = MagicMock()
        mock_redis.get.return_value = _json.dumps({"answer": "42", "_metadata": {"namespace": "ns"}})
        cache.redis_client = mock_redis
        cache.redis_enabled = True

        result = cache.recall("ctx", "ns", tenant_id="t1", flow_class="READ_ONLY")

    assert result is not None
    assert result.get("answer") == "42"
    mock_redis.get.assert_called_once()


def test_recall_allowed_flow_class_returns_miss() -> None:
    """Phase D: allowed flow_class (not in MUST_BYPASS_FLOWS) follows normal recall path — miss."""
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mock_l2.get.return_value = None
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        cache.redis_client = mock_redis
        cache.redis_enabled = True

        result = cache.recall("ctx", "ns", tenant_id="t1", flow_class="READ_ONLY")

    assert result is None
    mock_redis.get.assert_called_once()


def test_build_d2_key_raises_on_empty_tenant_id() -> None:
    """Phase D: build_semantic_cache_d2_key raises ValueError when tenant_id is empty."""
    import hashlib as _hashlib

    from agentic_core.cache.cache_key_builders import build_semantic_cache_d2_key

    valid_corpus = _hashlib.sha256(b"corpus").hexdigest()
    valid_hash = _hashlib.sha256(b"query").hexdigest()
    with pytest.raises(ValueError):
        build_semantic_cache_d2_key(
            tenant_id="",
            namespace="ns",
            embedding_model_id="bge-m3-v1",
            corpus_version=valid_corpus,
            query_hash=valid_hash,
        )


def test_try_semantic_match_raises_not_implemented() -> None:
    """Phase D: _try_semantic_match raises NotImplementedError (fail-fast D2 gate enforcement)."""
    import asyncio

    try:
        from system_learning.engines.enhanced_rag_retrieval_cache import EnhancedRagRetrievalCache
    except ImportError:
        pytest.skip("EnhancedRagRetrievalCache not importable")

    cache = object.__new__(EnhancedRagRetrievalCache)
    with pytest.raises(NotImplementedError, match="D2 gate"):
        asyncio.run(cache._try_semantic_match("query", "key", 5, 0.8))


def test_d2_gate_passes_flow_class_explicitly() -> None:
    """Phase D: static assertion that the D2 gate call site passes flow_class= and replay_mode= to recall()."""
    import inspect

    from agentic_core.L0_routing.reasoning.execution_orchestrator import ExecutionOrchestrator

    source = inspect.getsource(ExecutionOrchestrator.execute)
    assert "flow_class" in source, "D2 gate must pass flow_class= to SemanticCacheManager.recall()"
    assert "replay_mode" in source, "D2 gate must pass replay_mode= to SemanticCacheManager.recall()"
    assert "SemanticCacheManager" in source, "D2 gate must call SemanticCacheManager.get_instance().recall()"


# ---------------------------------------------------------------------------
# Phase E targeted tests
# ---------------------------------------------------------------------------


def test_store_semantic_entry_raises_not_implemented() -> None:
    """Phase E: _store_semantic_entry raises NotImplementedError (D3 semantic store forbidden)."""
    import asyncio

    try:
        from system_learning.engines.enhanced_rag_retrieval_cache import EnhancedRagRetrievalCache
    except ImportError:
        pytest.skip("EnhancedRagRetrievalCache not importable")

    cache = object.__new__(EnhancedRagRetrievalCache)
    with pytest.raises(NotImplementedError, match="D2 gate"):
        asyncio.run(cache._store_semantic_entry("query", []))


def test_enable_semantic_matching_hard_pinned_false() -> None:
    """Phase E: _enable_semantic_matching is always False regardless of constructor arg."""
    try:
        from unittest.mock import MagicMock as _MM
        from system_learning.engines.enhanced_rag_retrieval_cache import EnhancedRagRetrievalCache
    except ImportError:
        pytest.skip("EnhancedRagRetrievalCache not importable")

    mock_cache = _MM()
    mock_cache.get_json.return_value = None
    instance = EnhancedRagRetrievalCache(cache=mock_cache, enable_semantic_matching=True)
    assert instance._enable_semantic_matching is False, (
        "_enable_semantic_matching must be hard-pinned False; D3 semantic matching is forbidden"
    )


def test_compute_embedding_raises_on_unavailable_embedder() -> None:
    """Phase E: _compute_embedding raises when get_embedding is unavailable (fail-fast, no zero-vector)."""
    import numpy as np
    from unittest.mock import patch as _patch

    from agentic_core.runtime.types.cache_entry_types import semantic_cache

    sc = semantic_cache(enable_semantic_matching=True)
    with _patch(
        "agentic_core.runtime.types.cache_entry_types.get_embedding",
        side_effect=ImportError("embedder unavailable"),
    ):
        with pytest.raises(ImportError, match="embedder unavailable"):
            sc._compute_embedding("test text")


def test_compute_embedding_raises_on_zero_norm_vector() -> None:
    """Phase E: _compute_embedding raises ValueError when embedder returns a zero vector."""
    from unittest.mock import patch as _patch

    from agentic_core.runtime.types.cache_entry_types import semantic_cache

    sc = semantic_cache(enable_semantic_matching=True)
    with _patch("agentic_core.runtime.types.cache_entry_types.get_embedding", return_value=[0.0] * 1536):
        with pytest.raises(ValueError, match="zero-norm"):
            sc._compute_embedding("test text")


def test_find_semantic_match_raises_on_zero_norm_input() -> None:
    """Phase E: _find_semantic_match raises ValueError when given a zero-norm embedding."""
    import numpy as np

    from agentic_core.runtime.types.cache_entry_types import semantic_cache

    sc = semantic_cache(enable_semantic_matching=True)
    zero_vec = np.zeros(1536)
    with pytest.raises(ValueError, match="zero-norm"):
        sc._find_semantic_match(zero_vec)


# ---------------------------------------------------------------------------
# Phase F — Prometheus observability (B2 go-live blocker)
# ---------------------------------------------------------------------------


def _sc_counter_value(event: str, namespace: str) -> float:
    """Read SEMANTIC_CACHE_EVENTS_TOTAL sample value for given labels."""
    from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
        SEMANTIC_CACHE_EVENTS_TOTAL,
    )

    try:
        return SEMANTIC_CACHE_EVENTS_TOTAL.labels(event=event, namespace=namespace)._value.get()
    except (KeyError, AttributeError):
        return 0.0


def test_prom_hit_event_increments_counter() -> None:
    """Phase F: record_semantic_cache_event('hit') increments SEMANTIC_CACHE_EVENTS_TOTAL."""
    from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
        record_semantic_cache_event,
    )

    before = _sc_counter_value("hit", "test_ns")
    record_semantic_cache_event("hit", "test_ns")
    after = _sc_counter_value("hit", "test_ns")
    assert after == before + 1.0


def test_prom_miss_event_increments_counter() -> None:
    """Phase F: record_semantic_cache_event('miss') increments SEMANTIC_CACHE_EVENTS_TOTAL."""
    from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
        record_semantic_cache_event,
    )

    before = _sc_counter_value("miss", "test_ns")
    record_semantic_cache_event("miss", "test_ns")
    after = _sc_counter_value("miss", "test_ns")
    assert after == before + 1.0


def test_prom_bypass_event_increments_counter() -> None:
    """Phase F: record_semantic_cache_event('bypass') increments SEMANTIC_CACHE_EVENTS_TOTAL."""
    from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
        record_semantic_cache_event,
    )

    before = _sc_counter_value("bypass", "bypass_ns")
    record_semantic_cache_event("bypass", "bypass_ns")
    after = _sc_counter_value("bypass", "bypass_ns")
    assert after == before + 1.0


def test_prom_eviction_event_increments_counter() -> None:
    """Phase F: record_semantic_cache_event('eviction') increments SEMANTIC_CACHE_EVENTS_TOTAL."""
    from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
        record_semantic_cache_event,
    )

    before = _sc_counter_value("eviction", "")
    record_semantic_cache_event("eviction", "")
    after = _sc_counter_value("eviction", "")
    assert after == before + 1.0


def test_prom_invalidation_event_increments_counter() -> None:
    """Phase F: record_semantic_cache_event('invalidation') increments SEMANTIC_CACHE_EVENTS_TOTAL."""
    from agentic_core.L6_observability.utils.metrics.prometheus_metrics import (
        record_semantic_cache_event,
    )

    before = _sc_counter_value("invalidation", "tenant_a")
    record_semantic_cache_event("invalidation", "tenant_a")
    after = _sc_counter_value("invalidation", "tenant_a")
    assert after == before + 1.0


def test_prom_bridge_callable_from_lifecycle_contract() -> None:
    """Phase F: _record_semantic_cache_prom_event bridge in lifecycle_trace_contract is importable and callable."""
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        _record_semantic_cache_prom_event,
    )

    before = _sc_counter_value("hit", "bridge_ns")
    _record_semantic_cache_prom_event("hit", "bridge_ns")
    after = _sc_counter_value("hit", "bridge_ns")
    assert after == before + 1.0


# ---------------------------------------------------------------------------
# Migration guard tests — BGE-M3 standardization (Phase 1)
# ---------------------------------------------------------------------------


def _make_migration_target():
    """Return a NativePersistentCacheClient instance with bypassed __init__ for migration guard tests."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")
    inst = object.__new__(NativePersistentCacheClient)
    inst.embedding_model = "BAAI/bge-m3"
    return inst


def test_migration_guard_drops_incompatible_dim_collection() -> None:
    """_get_or_create_bgem3_collection must delete collection when stored embedding dim != 1024."""
    inst = _make_migration_target()
    mock_client = MagicMock()
    mock_existing = MagicMock()
    mock_existing.get.return_value = {"embeddings": [[0.1] * 384]}
    mock_client.get_collection.return_value = mock_existing
    inst._chroma_client = mock_client

    inst._get_or_create_bgem3_collection()

    mock_client.delete_collection.assert_called_once_with("l2_semantic_cache")
    mock_client.get_or_create_collection.assert_called_once()


def test_migration_guard_preserves_compatible_dim_collection() -> None:
    """_get_or_create_bgem3_collection must NOT delete collection when stored dim already == 1024."""
    inst = _make_migration_target()
    mock_client = MagicMock()
    mock_existing = MagicMock()
    mock_existing.get.return_value = {"embeddings": [[0.1] * 1024]}
    mock_client.get_collection.return_value = mock_existing
    inst._chroma_client = mock_client

    inst._get_or_create_bgem3_collection()

    mock_client.delete_collection.assert_not_called()
    mock_client.get_or_create_collection.assert_called_once()


def test_migration_guard_skips_drop_on_empty_embeddings() -> None:
    """_get_or_create_bgem3_collection must not drop when get() returns an empty embeddings list."""
    inst = _make_migration_target()
    mock_client = MagicMock()
    mock_existing = MagicMock()
    mock_existing.get.return_value = {"embeddings": []}
    mock_client.get_collection.return_value = mock_existing
    inst._chroma_client = mock_client

    inst._get_or_create_bgem3_collection()

    mock_client.delete_collection.assert_not_called()
    mock_client.get_or_create_collection.assert_called_once()


def test_migration_guard_handles_missing_collection_silently() -> None:
    """_get_or_create_bgem3_collection must not raise when collection doesn't exist yet."""
    inst = _make_migration_target()
    mock_client = MagicMock()
    mock_client.get_collection.side_effect = Exception("collection not found")
    inst._chroma_client = mock_client

    inst._get_or_create_bgem3_collection()  # must not raise

    mock_client.delete_collection.assert_not_called()
    mock_client.get_or_create_collection.assert_called_once()
