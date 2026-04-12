"""
Acceptance Suite: AT-1 through AT-10 — Semantic Cache Go-Live Gate

Mapping (one-to-one with go-live gate conditions):
  AT-1   test_AT_1_same_intent_hit            same-intent read-only hit
  AT-2   test_AT_2_cross_tenant_isolation     cross-tenant isolation
  AT-3   test_AT_3_acl_namespace_rejection    ACL mismatch (namespace) rejection
  AT-4   test_AT_4_corpus_version_rejection   corpus-version mismatch rejection
  AT-5   test_AT_5_embedding_model_rejection  embedding-model mismatch rejection
  AT-6   test_AT_6_ttl_expiry                 stale-entry TTL expiry
  AT-7   test_AT_7_explicit_invalidation      explicit invalidation on corpus change
  AT-8   test_AT_8_evidence_complete_payload  evidence-complete hit payload
  AT-9   test_AT_9_replay_mode_bypass         replay-mode cache bypass
  AT-10  test_AT_10_must_bypass_flow          must-bypass flow enforcement
"""

import datetime as _dt
import hashlib as _hl
import json as _json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _l2_client(tmp_path: Path):
    """Real NativePersistentCacheClient or pytest.skip if ChromaDB absent."""
    try:
        from agentic_core.L4_state.cache.gptcache_client import NativePersistentCacheClient
    except ImportError:
        pytest.skip("ChromaDB not installed")
    client = NativePersistentCacheClient(cache_dir=str(tmp_path), similarity_threshold=0.5)
    if client._cache == "mock":
        pytest.skip("ChromaDB not available in test environment")
    return client


def _fresh_scm_mocked(*, l2_get=None, l2_invalidate_by=None):
    """Reset SCM singleton; patch GPTCacheClient; return (cache, mock_redis, mock_l2).

    Patch is active only during singleton initialisation; the mock_l2 reference
    remains live on the returned cache object.
    """
    SemanticCacheManager._instance = None
    mock_l2 = MagicMock()
    mock_l2._cache = "real"
    if l2_get is not None:
        mock_l2.get.return_value = l2_get
    if l2_invalidate_by is not None:
        mock_l2.invalidate_by.return_value = l2_invalidate_by
    patcher = patch(
        "agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient",
        return_value=mock_l2,
    )
    patcher.start()
    cache = SemanticCacheManager.get_instance()
    patcher.stop()

    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    cache.redis_client = mock_redis
    cache.redis_enabled = True
    return cache, mock_redis, mock_l2


# ---------------------------------------------------------------------------
# AT-1  same-intent read-only hit
# ---------------------------------------------------------------------------


def test_AT_1_same_intent_hit(tmp_path: Path) -> None:
    """AT-1: An identical query returns the cached response from L2 (read-only hit).

    Gate: cache hit path fires; cached payload returned without executing the
    downstream agent.
    """
    client = _l2_client(tmp_path)
    response_payload = _json.dumps(
        {
            "answer": "Q4 revenue was $42M.",
            "_metadata": {"namespace": "research-agent"},
        }
    )
    client.set(
        "what was Q4 revenue",
        response_payload,
        tenant_id="acme",
        embedding_model_id="bge-m3-v1",
    )
    result_str = client.get(
        "what was Q4 revenue",
        tenant_id="acme",
        embedding_model_id="bge-m3-v1",
    )
    assert result_str is not None, "AT-1 FAIL: cache returned None for identical query"
    result = _json.loads(result_str)
    assert result["answer"] == "Q4 revenue was $42M."
    client.close()


# ---------------------------------------------------------------------------
# AT-2  cross-tenant isolation
# ---------------------------------------------------------------------------


def test_AT_2_cross_tenant_isolation(tmp_path: Path) -> None:
    """AT-2: A cached entry belonging to tenant-A must not be returned to tenant-B.

    Gate: L2 get() enforces tenant_id equality; cross-tenant read returns None.
    """
    client = _l2_client(tmp_path)
    client.set("confidential query", "Tenant-A response", tenant_id="tenant-a")
    result = client.get("confidential query", tenant_id="tenant-b")
    assert result is None, "AT-2 FAIL: cross-tenant read returned a cached result"
    client.close()


# ---------------------------------------------------------------------------
# AT-3  ACL mismatch rejection (namespace isolation at SemanticCacheManager layer)
# ---------------------------------------------------------------------------


def test_AT_3_acl_namespace_rejection() -> None:
    """AT-3: An L2 payload stored under namespace-A must not be served for namespace-B.

    Gate: SemanticCacheManager.recall() checks _metadata.namespace equality;
    a namespace mismatch is treated as a cache miss.
    """
    wrong_ns_payload = _json.dumps(
        {
            "result": "agent-A private answer",
            "_metadata": {"namespace": "agent-A"},
        }
    )
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mock_l2.get.return_value = wrong_ns_payload
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        cache.redis_enabled = False
        cache.gptcache_enabled = True

        result = cache.recall("some context", "agent-B")

    assert result is None, "AT-3 FAIL: wrong-namespace L2 entry was served to agent-B"


# ---------------------------------------------------------------------------
# AT-4  corpus-version mismatch rejection
# ---------------------------------------------------------------------------


def test_AT_4_corpus_version_rejection() -> None:
    """AT-4: When the active corpus version changes, old-corpus entries are not served.

    Gate: _compute_hash embeds _RETRIEVAL_CONFIG_HASH; a corpus version change
    yields a different Redis key so old entries are never matched.
    """
    corpus_v1 = "a" * 64
    corpus_v2 = "b" * 64

    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mock_l2.get.return_value = None
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        cache.gptcache_enabled = False
        cache.redis_enabled = True
        cache._RETRIEVAL_CONFIG_HASH = corpus_v1

        mock_redis = MagicMock()
        cache.redis_client = mock_redis

        hit_json = _json.dumps({"result": "cached-v1", "_metadata": {"namespace": "ns"}})
        hash_v1 = cache._compute_hash("same question", "ns")
        mock_redis.get.side_effect = lambda k: hit_json if k == f"memory:{hash_v1}" else None

        # corpus_v1 key: must hit
        result_v1 = cache.recall("same question", "ns")
        assert result_v1 is not None, "AT-4 FAIL: expected L1 hit for corpus_v1"

        # corpus_v2 key: must miss (different hash derived from different corpus)
        cache._RETRIEVAL_CONFIG_HASH = corpus_v2
        result_v2 = cache.recall("same question", "ns")
    assert result_v2 is None, "AT-4 FAIL: old-corpus entry was served under new corpus version"


# ---------------------------------------------------------------------------
# AT-5  embedding-model mismatch rejection
# ---------------------------------------------------------------------------


def test_AT_5_embedding_model_rejection(tmp_path: Path) -> None:
    """AT-5: An entry stored with embedding-model-A must not be returned for model-B.

    Gate: L2 get() enforces embedding_model_id equality; model mismatch returns None.
    """
    client = _l2_client(tmp_path)
    client.set("vector search query", "Response", embedding_model_id="model-v1")
    result = client.get("vector search query", embedding_model_id="model-v2")
    assert result is None, "AT-5 FAIL: model-mismatch entry was returned"
    client.close()


# ---------------------------------------------------------------------------
# AT-6  stale-entry TTL expiry
# ---------------------------------------------------------------------------


def test_AT_6_ttl_expiry(tmp_path: Path) -> None:
    """AT-6: An entry whose TTL has elapsed must be evicted and return None.

    Gate: L2 get() checks expires_at; expired entries are hard-evicted (deleted
    from both SQLite and ChromaDB) and never served.
    """
    client = _l2_client(tmp_path)
    client.set("stale query", "old response", ttl_seconds=3600)
    qid = _hl.sha256(b"stale query").hexdigest()

    past = (_dt.datetime.utcnow() - _dt.timedelta(hours=1)).isoformat()
    client._sqlite_conn.execute("UPDATE l2_cache SET expires_at = ? WHERE id = ?", (past, qid))
    client._sqlite_conn.commit()

    result = client.get("stale query")
    assert result is None, "AT-6 FAIL: expired entry was returned"

    cursor = client._sqlite_conn.cursor()
    cursor.execute("SELECT id FROM l2_cache WHERE id = ?", (qid,))
    assert cursor.fetchone() is None, "AT-6 FAIL: expired entry was not physically evicted"
    client.close()


# ---------------------------------------------------------------------------
# AT-7  explicit invalidation on corpus change
# ---------------------------------------------------------------------------


def test_AT_7_explicit_invalidation() -> None:
    """AT-7: SemanticCacheManager.invalidate_cache(corpus_version=X) removes all X-versioned entries.

    Gate: invalidate_cache() delegates to NativePersistentCacheClient.invalidate_by()
    and returns the count of removed entries; corpus-change operator workflow is wired.
    """
    SemanticCacheManager._instance = None
    with patch("agentic_core.L4_state.utils.memory.semantic_cache_manager.GPTCacheClient") as mc:
        mock_l2 = MagicMock()
        mock_l2._cache = "real"
        mock_l2.invalidate_by.return_value = 7
        mc.return_value = mock_l2
        cache = SemanticCacheManager.get_instance()
        cache.gptcache_enabled = True
        cache._gptcache = mock_l2

        count = cache.invalidate_cache(corpus_version="a" * 64)

    assert count == 7, f"AT-7 FAIL: expected 7 invalidated entries, got {count}"
    mock_l2.invalidate_by.assert_called_once_with(
        tenant_id=None,
        corpus_version="a" * 64,
        embedding_model_id=None,
    )


# ---------------------------------------------------------------------------
# AT-8  evidence-complete hit payload
# ---------------------------------------------------------------------------


def test_AT_8_evidence_complete_payload(tmp_path: Path) -> None:
    """AT-8: A cache hit must return a payload carrying evidence_ids and grounding_complete=True.

    Gate: responses stored with grounding metadata are round-tripped intact;
    the returned payload satisfies the evidence-complete contract.
    """
    client = _l2_client(tmp_path)
    response_payload = _json.dumps(
        {
            "summary": "Revenue grew 15%.",
            "evidence_ids": ["doc-101", "doc-202"],
            "grounding_complete": True,
            "_metadata": {"namespace": "finance-agent"},
        }
    )
    client.set(
        "quarterly revenue summary",
        response_payload,
        tenant_id="corp",
        evidence_ids=["doc-101", "doc-202"],
        grounding_complete=True,
    )
    result_str = client.get("quarterly revenue summary", tenant_id="corp")
    assert result_str is not None, "AT-8 FAIL: cache miss on evidence-complete entry"
    result = _json.loads(result_str)
    assert result.get("grounding_complete") is True, "AT-8 FAIL: grounding_complete missing"
    assert "doc-101" in result.get("evidence_ids", []), "AT-8 FAIL: evidence_ids missing"
    client.close()


# ---------------------------------------------------------------------------
# AT-9  replay-mode cache bypass
# ---------------------------------------------------------------------------


def test_AT_9_replay_mode_bypass() -> None:
    """AT-9: recall(replay_mode=True) must return None without touching any storage.

    Gate: replay_mode=True short-circuits recall() before any Redis or L2 access;
    no cached result is served during replay execution.
    """
    hit_json = _json.dumps({"result": "would-hit", "_metadata": {"namespace": "ns"}})
    cache, mock_redis, mock_l2 = _fresh_scm_mocked(l2_get=hit_json)
    mock_redis.get.return_value = hit_json

    result = cache.recall("any context", "ns", replay_mode=True)

    assert result is None, "AT-9 FAIL: replay_mode bypass returned a non-None result"
    mock_redis.get.assert_not_called()
    mock_l2.get.assert_not_called()


# ---------------------------------------------------------------------------
# AT-10  must-bypass flow enforcement
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "flow_class",
    ["D4_ACTION", "HITL", "UWG_WRITE", "AUDIT_EXIT", "REPLAY"],
)
def test_AT_10_must_bypass_flow(flow_class: str) -> None:
    """AT-10: Every flow_class in MUST_BYPASS_FLOWS bypasses recall entirely.

    Gate: flow_class membership in MUST_BYPASS_FLOWS short-circuits recall()
    before any Redis or L2 access. Covers all 5 members.
    """
    hit_json = _json.dumps({"result": "would-hit", "_metadata": {"namespace": "ns"}})
    cache, mock_redis, mock_l2 = _fresh_scm_mocked(l2_get=hit_json)
    mock_redis.get.return_value = hit_json

    result = cache.recall("any context", "ns", flow_class=flow_class)

    assert result is None, f"AT-10 FAIL: flow_class={flow_class!r} was not bypassed"
    mock_redis.get.assert_not_called()
    mock_l2.get.assert_not_called()
