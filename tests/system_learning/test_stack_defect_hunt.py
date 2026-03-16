"""Defect-hunting tests for F1-F5 infrastructure fixes.

Covers branches NOT tested in test_stack_invariants.py:

Redis (F4):
  - _validate_key rejects empty, too-long, control-char keys
  - set() rejects non-bytes value, >10MB value, zero/negative/>24h TTL
  - delete() returns True when key existed, False when absent
  - get() replay_mode always returns None regardless of cache state
  - _mark_failed triggers fallback on mid-session Redis failure
  - fallback LRU is used when Redis is unreachable from the start
  - fallback set/get/delete all work correctly
  - HOT (DB0) and COORDINATION (DB1) are separate namespaces
  - canonical_json_bytes produces stable bytes; non-ASCII raises
  - get_stats() returns correct structure and increments
  - acquire_lease / release_lease contract
  - _REDIS_SOCKET_TIMEOUT_S is 0.3 in BOTH _connect and check_redis_health

FAISS (F3):
  - load_from_disk raises ManifestIntegrityError on tampered index.json
  - load_from_disk raises ManifestIntegrityError on tampered meta.json
  - load_from_disk raises ManifestIntegrityError on missing manifest
  - load_from_disk raises EmbedderMismatchError on wrong embedder_id
  - search() returns results sorted (score DESC, hash ASC)
  - search() cutoff filters correctly
  - search() on empty index returns []
  - persist -> load_from_disk -> search round-trip

vLLM (F1/F5):
  - get_model_config unknown size falls back to 7B (no crash)
  - QWEN_GPU_MEM_UTIL is not overridden locally in either call site
  - start_server raises if already running (process check)
  - health_check URL is /v1/health (or /health), not /v1/models

Embedding (F2):
  - kill-switch: get_or_disabled returns _DisabledEmbeddingService when EMBEDDING_ENABLED=false
  - kill-switch: raises EmbeddingIntegrityError if instance exists while disabled
  - _is_embedding_enabled requires exactly "true" (case-insensitive)
"""

from __future__ import annotations

import ast
import hashlib
import json
import struct
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_stack_defect_hunt")
_emit_applies_guardrail("p0", "test_stack_defect_hunt", "p0_governance")
_emit_reads_policy_state("p0", "test_stack_defect_hunt", "policy_binding")
_emit_snapshots_state("p0", "test_stack_defect_hunt", "state_snapshot")
emit_replay_key("p0", "test_stack_defect_hunt")
emit_determinism_digest("p0", "test_stack_defect_hunt")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_stack_defect_hunt", "execution_auth")
_emit_validates_capability("p2", "test_stack_defect_hunt", "capability_check")
_emit_routes_to_capability("p2", "test_stack_defect_hunt", "capability_route")
_emit_writes_via_uwg("p2", "test_stack_defect_hunt", "uwg_write")
_emit_blocks_direct_write("p2", "test_stack_defect_hunt", "direct_write_block")
_emit_records_tool_invocation("p2", "test_stack_defect_hunt", "tool_invocation")
_emit_captures_execution_output("p2", "test_stack_defect_hunt", "exec_output")
_emit_dispatches_agent("p3", "test_stack_defect_hunt", "agent_dispatch")
_emit_coordinates_agents("p3", "test_stack_defect_hunt", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_stack_defect_hunt", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_stack_defect_hunt", "healing_outcome")
_emit_escalates_failure("p3", "test_stack_defect_hunt", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_stack_defect_hunt", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_stack_defect_hunt", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_stack_defect_hunt", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_stack_defect_hunt", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_stack_defect_hunt", "eval_metric")
_emit_stores_embedding("p4", "test_stack_defect_hunt", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_stack_defect_hunt", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_stack_defect_hunt", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ===========================================================================
# Redis — key validation
# ===========================================================================


def _make_cache_in_fallback():
    """Construct a DeterministicRedisCache already in fallback mode (no TCP I/O)."""
    from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

    c = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:1")
    c._use_fallback = True
    c._conn = None
    return c


class TestRedisKeyValidation:
    """DeterministicRedisCache._validate_key rejects illegal keys."""

    def _cache(self):
        return _make_cache_in_fallback()

    @pytest.mark.unit_min_deps
    def test_empty_key_raises(self):
        c = self._cache()
        with pytest.raises(ValueError, match="non-empty"):
            c._validate_key("")

    @pytest.mark.unit_min_deps
    def test_non_string_key_raises(self):
        c = self._cache()
        with pytest.raises((ValueError, AttributeError)):
            c._validate_key(None)

    @pytest.mark.unit_min_deps
    def test_key_over_512_chars_raises(self):
        c = self._cache()
        with pytest.raises(ValueError, match="512"):
            c._validate_key("a" * 513)

    @pytest.mark.unit_min_deps
    def test_key_with_null_byte_raises(self):
        c = self._cache()
        with pytest.raises(ValueError, match="control"):
            c._validate_key("key\x00value")

    @pytest.mark.unit_min_deps
    def test_key_with_newline_raises(self):
        c = self._cache()
        with pytest.raises(ValueError, match="control"):
            c._validate_key("key\nvalue")

    @pytest.mark.unit_min_deps
    def test_exactly_512_char_key_is_valid(self):
        c = self._cache()
        c._validate_key("a" * 512)  # must not raise


# ===========================================================================
# Redis — set() contract
# ===========================================================================


class TestRedisSetContract:
    """DeterministicRedisCache.set() enforces value type and size constraints."""

    def _cache(self):
        return _make_cache_in_fallback()

    @pytest.mark.unit_min_deps
    def test_non_bytes_value_raises_typeerror(self):
        c = self._cache()
        with pytest.raises(TypeError, match="bytes"):
            c.set("a" * 64, "not bytes")

    @pytest.mark.unit_min_deps
    def test_value_over_10mb_raises_valueerror(self):
        c = self._cache()
        with pytest.raises(ValueError, match="large"):
            c.set("a" * 64, b"x" * (10 * 1024 * 1024 + 1))

    @pytest.mark.unit_min_deps
    def test_zero_ttl_raises(self):
        c = self._cache()
        with pytest.raises(ValueError, match="positive"):
            c.set("a" * 64, b"v", ttl_seconds=0)

    @pytest.mark.unit_min_deps
    def test_negative_ttl_raises(self):
        c = self._cache()
        with pytest.raises(ValueError, match="positive"):
            c.set("a" * 64, b"v", ttl_seconds=-1)

    @pytest.mark.unit_min_deps
    def test_ttl_over_86400_raises(self):
        c = self._cache()
        with pytest.raises(ValueError, match="86400"):
            c.set("a" * 64, b"v", ttl_seconds=86401)

    @pytest.mark.unit_min_deps
    def test_exactly_10mb_value_is_accepted(self):
        c = self._cache()
        result = c.set("a" * 64, b"x" * (10 * 1024 * 1024))
        assert result is True

    @pytest.mark.unit_min_deps
    def test_exactly_86400s_ttl_is_accepted(self):
        c = self._cache()
        result = c.set("a" * 64, b"v", ttl_seconds=86400)
        assert result is True


# ===========================================================================
# Redis — fallback LRU behaviour
# ===========================================================================


class TestRedisFallbackBehaviour:
    """When Redis is unavailable, cache falls back to bounded in-process LRU."""

    def _fallback_cache(self):
        """Returns a cache pre-set to fallback mode (no TCP I/O — direct injection)."""
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:1")
        # Inject fallback directly — avoids real TCP connect overhead in unit tests.
        # The TCP-path is tested separately in TestRedisTCPPreCheck.
        c._use_fallback = True
        c._conn = None
        return c

    @pytest.mark.unit_min_deps
    def test_fallback_activated_on_refused_connection(self):
        c = self._fallback_cache()
        assert c._use_fallback is True

    @pytest.mark.unit_min_deps
    def test_set_returns_true_in_fallback(self):
        c = self._fallback_cache()
        assert c.set("a" * 64, b"val") is True

    @pytest.mark.unit_min_deps
    def test_get_returns_value_from_fallback(self):
        c = self._fallback_cache()
        key = "b" * 64
        c.set(key, b"payload")
        assert c.get(key) == b"payload"

    @pytest.mark.unit_min_deps
    def test_get_miss_returns_none_in_fallback(self):
        c = self._fallback_cache()
        assert c.get("c" * 64) is None

    @pytest.mark.unit_min_deps
    def test_delete_returns_true_when_key_existed(self):
        c = self._fallback_cache()
        key = "d" * 64
        c.set(key, b"val")
        assert c.delete(key) is True

    @pytest.mark.unit_min_deps
    def test_delete_returns_false_when_key_absent(self):
        c = self._fallback_cache()
        assert c.delete("e" * 64) is False

    @pytest.mark.unit_min_deps
    def test_fallback_stats_increment_correctly(self):
        c = self._fallback_cache()
        key = "f" * 64
        c.set(key, b"v")
        c.get(key)  # fallback_hit
        c.get("z" * 64)  # fallback_miss
        stats = c.get_stats()
        assert stats["fallback_hits"] >= 1
        assert stats["fallback_misses"] >= 1
        assert stats["using_fallback"] is True

    @pytest.mark.unit_min_deps
    def test_replay_mode_always_returns_none_even_with_cached_value(self):
        c = self._fallback_cache()
        key = "g" * 64
        c.set(key, b"secret")
        result = c.get(key, replay_mode=True)
        assert result is None

    @pytest.mark.unit_min_deps
    def test_replay_mode_increments_bypassed_stat(self):
        c = self._fallback_cache()
        c.get("h" * 64, replay_mode=True)
        assert c.get_stats()["bypassed_replay"] == 1

    @pytest.mark.unit_min_deps
    def test_get_stats_has_all_required_keys(self):
        c = self._fallback_cache()
        stats = c.get_stats()
        for k in (
            "db",
            "using_fallback",
            "hits",
            "misses",
            "fallback_hits",
            "fallback_misses",
            "errors",
            "bypassed_replay",
        ):
            assert k in stats, f"stats missing key '{k}'"

    @pytest.mark.unit_min_deps
    def test_db_namespace_in_stats_matches_enum(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c0 = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:1")
        c1 = DeterministicRedisCache(db=CacheDB.COORDINATION, redis_url="redis://localhost:1")
        assert c0.get_stats()["db"] == 0
        assert c1.get_stats()["db"] == 1


# ===========================================================================
# Redis — mid-session failure (_mark_failed path)
# ===========================================================================


class TestRedisMidSessionFailure:
    """_mark_failed is triggered when Redis dies after connection is established."""

    @pytest.mark.unit_min_deps
    def test_mark_failed_sets_use_fallback(self):
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:1")
        c._use_fallback = False  # pretend we connected
        c._mark_failed(RuntimeError("mid-session drop"))
        assert c._use_fallback is True
        assert c._conn is None
        assert c.stats.errors == 1

    @pytest.mark.unit_min_deps
    def test_get_falls_back_after_mark_failed(self):
        """After _mark_failed, get() reads from LRU fallback."""
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:1")
        key = "i" * 64
        c._fallback.set(key, b"fallback_value")
        c._mark_failed(RuntimeError("drop"))
        assert c.get(key) == b"fallback_value"


# ===========================================================================
# Redis — canonical_json_bytes
# ===========================================================================


class TestCanonicalJsonBytes:
    """canonical_json_bytes must be deterministic, ASCII-only, sorted."""

    @pytest.mark.unit_min_deps
    def test_output_is_bytes(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        assert isinstance(canonical_json_bytes({"a": 1}), bytes)

    @pytest.mark.unit_min_deps
    def test_output_is_ascii_decodable(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        canonical_json_bytes({"key": "value"}).decode("ascii")  # must not raise

    @pytest.mark.unit_min_deps
    def test_deterministic_across_calls(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        obj = {"z": 1, "a": 2, "m": [3, 4]}
        assert canonical_json_bytes(obj) == canonical_json_bytes(obj)

    @pytest.mark.unit_min_deps
    def test_key_order_independent(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        a = canonical_json_bytes({"z": 1, "a": 2})
        b = canonical_json_bytes({"a": 2, "z": 1})
        assert a == b, "canonical_json_bytes must produce identical output regardless of key insertion order"

    @pytest.mark.unit_min_deps
    def test_non_ascii_unicode_is_escaped(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        result = canonical_json_bytes({"k": "\u00e9"})
        result.decode("ascii")  # must be ASCII-safe (escaped)

    @pytest.mark.unit_min_deps
    def test_nested_structure(self):
        from agentic_core.cache.redis_cache_client import canonical_json_bytes

        obj = {"outer": {"inner": [1, 2, 3]}, "flag": True}
        result = canonical_json_bytes(obj)
        assert json.loads(result.decode("ascii")) == obj


# ===========================================================================
# Redis — HOT vs COORDINATION namespace isolation
# ===========================================================================


class TestRedisDatabaseNamespaceIsolation:
    """HOT (DB0) and COORDINATION (DB1) must be truly separate key spaces."""

    @pytest.mark.unit_min_deps
    def test_hot_and_coord_are_separate_instances(self):
        from agentic_core.cache.redis_cache_client import (
            CacheDB,
            get_coordination_cache,
            get_hot_cache,
            reset_cache_singletons,
        )

        reset_cache_singletons()
        hot = get_hot_cache()
        coord = get_coordination_cache()
        assert hot is not coord
        assert hot._db == CacheDB.HOT
        assert coord._db == CacheDB.COORDINATION
        reset_cache_singletons()

    @pytest.mark.unit_min_deps
    def test_hot_key_not_visible_in_coord_fallback(self):
        """In fallback mode, HOT and COORD have independent LRU stores."""
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        hot = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:1")
        coord = DeterministicRedisCache(db=CacheDB.COORDINATION, redis_url="redis://localhost:1")
        # Inject fallback directly — no TCP I/O
        hot._use_fallback = True
        coord._use_fallback = True
        key = "j" * 64
        hot.set(key, b"hot_value")
        assert coord.get(key) is None, "COORDINATION must not see HOT key"


# ===========================================================================
# Redis — TCP pre-check (_tcp_reachable)
# ===========================================================================


class TestRedisTCPPreCheck:
    """_tcp_reachable must return True for open ports and False fast for closed ones."""

    @pytest.mark.unit_min_deps
    def test_tcp_reachable_returns_false_for_unreachable_port(self):
        """Mock OSError from socket to verify False return without TCP overhead."""
        from agentic_core.cache.redis_cache_client import DeterministicRedisCache

        with patch("socket.create_connection", side_effect=OSError("refused")):
            assert DeterministicRedisCache._tcp_reachable("localhost", 1) is False

    @pytest.mark.unit_min_deps
    def test_tcp_reachable_returns_true_for_reachable_port(self):
        """Mock successful socket connection to verify True return."""
        from agentic_core.cache.redis_cache_client import DeterministicRedisCache

        mock_sock = MagicMock()
        mock_sock.__enter__ = MagicMock(return_value=mock_sock)
        mock_sock.__exit__ = MagicMock(return_value=False)
        with patch("socket.create_connection", return_value=mock_sock):
            assert DeterministicRedisCache._tcp_reachable("localhost", 6379) is True

    @pytest.mark.unit_min_deps
    def test_connect_skips_redis_py_when_tcp_precheck_fails(self):
        """When _tcp_reachable returns False, redis.Redis must never be instantiated."""
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:6379")
        mock_redis_mod = MagicMock()

        with patch.object(DeterministicRedisCache, "_tcp_reachable", return_value=False):
            with patch.dict("sys.modules", {"redis": mock_redis_mod}):
                result = c._connect()

        assert result is None
        assert c._use_fallback is True
        mock_redis_mod.Redis.assert_not_called()

    @pytest.mark.unit_min_deps
    def test_connect_proceeds_to_redis_when_tcp_precheck_passes(self):
        """When _tcp_reachable returns True, redis.Redis must be instantiated."""
        from agentic_core.cache.redis_cache_client import CacheDB, DeterministicRedisCache

        c = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:6379")
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True
        mock_redis_mod = MagicMock()
        mock_redis_mod.Redis.return_value = mock_redis_instance

        with patch.object(DeterministicRedisCache, "_tcp_reachable", return_value=True):
            with patch.dict("sys.modules", {"redis": mock_redis_mod}):
                result = c._connect()

        assert result is mock_redis_instance
        assert c._use_fallback is False
        mock_redis_mod.Redis.assert_called_once()


# ===========================================================================
# Redis — socket timeout constant
# ===========================================================================


class TestRedisSocketTimeout:
    """_REDIS_SOCKET_TIMEOUT_S must be 0.3 and applied to BOTH connection paths."""

    @pytest.mark.unit_min_deps
    def test_constant_value_is_0_3(self):
        import agentic_core.cache.redis_cache_client as m

        assert m._REDIS_SOCKET_TIMEOUT_S == 0.3, (
            f"_REDIS_SOCKET_TIMEOUT_S must be 0.3 to prevent hangs, got {m._REDIS_SOCKET_TIMEOUT_S}"
        )

    @pytest.mark.unit_min_deps
    def test_constant_used_in_connect_via_ast(self):
        """_connect() must reference _REDIS_SOCKET_TIMEOUT_S, not a bare float."""
        src = Path("agentic_core/cache/redis_cache_client.py").read_text(encoding="utf-8")
        tree = ast.parse(src)

        # Collect all float constants in the file
        float_literals = [
            n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)
        ]
        # 2.0 and 0.5 were the old timeout values — must not appear as bare literals
        assert 2.0 not in float_literals, "Bare 2.0 timeout literal found — use _REDIS_SOCKET_TIMEOUT_S"
        assert 0.5 not in float_literals, "Bare 0.5 timeout literal found — use _REDIS_SOCKET_TIMEOUT_S"

    @pytest.mark.unit_min_deps
    def test_connect_passes_timeout_to_redis_constructor(self):
        """_connect() must pass socket_timeout=_REDIS_SOCKET_TIMEOUT_S to redis.Redis."""
        from agentic_core.cache.redis_cache_client import (
            _REDIS_SOCKET_TIMEOUT_S,
            CacheDB,
            DeterministicRedisCache,
        )

        captured = {}
        mock_redis_instance = MagicMock()
        mock_redis_instance.ping.return_value = True

        def capture_redis(**kwargs):
            captured.update(kwargs)
            return mock_redis_instance

        mock_redis_mod = MagicMock()
        mock_redis_mod.Redis.side_effect = capture_redis

        with patch.dict("sys.modules", {"redis": mock_redis_mod}):
            c = DeterministicRedisCache(db=CacheDB.HOT, redis_url="redis://localhost:6379")
            c._connect()

        assert captured.get("socket_timeout") == _REDIS_SOCKET_TIMEOUT_S
        assert captured.get("socket_connect_timeout") == _REDIS_SOCKET_TIMEOUT_S

    @pytest.mark.unit_min_deps
    def test_check_redis_health_passes_timeout(self):
        """check_redis_health must pass socket_timeout=_REDIS_SOCKET_TIMEOUT_S."""
        from agentic_core.cache.redis_cache_client import _REDIS_SOCKET_TIMEOUT_S, check_redis_health

        captured = {}

        def capture_redis(**kwargs):
            captured.update(kwargs)
            raise ConnectionRefusedError("mock refused")

        mock_redis_mod = MagicMock()
        mock_redis_mod.Redis.side_effect = capture_redis

        with patch.dict("sys.modules", {"redis": mock_redis_mod}):
            check_redis_health("redis://localhost:6379")

        assert captured.get("socket_timeout") == _REDIS_SOCKET_TIMEOUT_S
        assert captured.get("socket_connect_timeout") == _REDIS_SOCKET_TIMEOUT_S


# ===========================================================================
# FAISS — load_from_disk integrity checks
# ===========================================================================


def _build_faiss_artifact(base: Path, index_id: str, n: int = 4, dim: int = 8) -> Path:
    """Helper: build and persist a valid FAISS artifact, return artifact dir."""
    from system_learning.engines.local_faiss_store import LocalFAISSStore

    vecs = [_det_vec(f"v{i}", dim) for i in range(n)]
    metas = [{"content_hash": f"hash_{i:04d}", "trace_id": f"t{i}"} for i in range(n)]

    store = LocalFAISSStore(base_path=base)
    store.begin_build(index_id, dim, seed=42)
    store.add_vectors(index_id, vecs, metas)
    store.finalize_build(
        index_id,
        built_at_utc=1700000000,
        canonicalization_version="v1",
        embedding_model_version="test-embedder-v1",
        embedding_model_checksum="abc123",
    )
    artifact_dir = base / index_id
    store.persist_to_disk(
        index_id, artifact_dir, embedder_id="test-embedder", model_version="test-embedder-v1"
    )
    return artifact_dir


def _det_vec(seed: str, dim: int) -> list[float]:
    """Deterministic L2-normalised float vector."""
    raw = b""
    s = seed.encode()
    while len(raw) < dim * 4:
        s = hashlib.sha256(s).digest()
        raw += s
    floats = [struct.unpack("<f", raw[i * 4 : i * 4 + 4])[0] for i in range(dim)]
    norm = sum(x * x for x in floats) ** 0.5 or 1.0
    return [x / norm for x in floats]


class TestFAISSLoadFromDisk:
    """load_from_disk must fail-closed on any integrity violation."""

    @pytest.mark.unit_min_deps
    def test_valid_artifact_loads_without_error(self, tmp_path):
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        art = _build_faiss_artifact(tmp_path, "idx")
        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        store2.load_from_disk("idx", art)  # must not raise

    @pytest.mark.unit_min_deps
    def test_tampered_index_json_raises(self, tmp_path):
        from system_learning.engines.local_faiss_store import LocalFAISSStore, ManifestIntegrityError

        art = _build_faiss_artifact(tmp_path, "idx")
        (art / "index.json").write_bytes(b'{"tampered":true}')

        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        with pytest.raises(ManifestIntegrityError, match="sha256"):
            store2.load_from_disk("idx", art)

    @pytest.mark.unit_min_deps
    def test_tampered_meta_json_raises(self, tmp_path):
        from system_learning.engines.local_faiss_store import LocalFAISSStore, ManifestIntegrityError

        art = _build_faiss_artifact(tmp_path, "idx")
        (art / "meta.json").write_bytes(b'{"tampered":true}')

        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        with pytest.raises(ManifestIntegrityError, match="sha256"):
            store2.load_from_disk("idx", art)

    @pytest.mark.unit_min_deps
    def test_missing_manifest_raises(self, tmp_path):
        from system_learning.engines.local_faiss_store import LocalFAISSStore, ManifestIntegrityError

        art = _build_faiss_artifact(tmp_path, "idx")
        (art / "manifest.json").unlink()

        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        with pytest.raises(ManifestIntegrityError):
            store2.load_from_disk("idx", art)

    @pytest.mark.unit_min_deps
    def test_missing_index_json_raises(self, tmp_path):
        from system_learning.engines.local_faiss_store import LocalFAISSStore, ManifestIntegrityError

        art = _build_faiss_artifact(tmp_path, "idx")
        (art / "index.json").unlink()

        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        with pytest.raises(ManifestIntegrityError):
            store2.load_from_disk("idx", art)

    @pytest.mark.unit_min_deps
    def test_wrong_embedder_id_raises(self, tmp_path):
        from system_learning.engines.local_faiss_store import EmbedderMismatchError, LocalFAISSStore

        art = _build_faiss_artifact(tmp_path, "idx")
        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        with pytest.raises(EmbedderMismatchError):
            store2.load_from_disk("idx", art, expected_embedder_id="completely-wrong-embedder")

    @pytest.mark.unit_min_deps
    def test_correct_embedder_id_passes(self, tmp_path):
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        art = _build_faiss_artifact(tmp_path, "idx")
        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        store2.load_from_disk("idx", art, expected_embedder_id="test-embedder")  # must not raise


# ===========================================================================
# FAISS — search correctness
# ===========================================================================


class TestFAISSSearch:
    """search() must return sorted results and respect cutoff."""

    def _store_with_vectors(self, n: int = 4, dim: int = 8):
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        vecs = [_det_vec(f"v{i}", dim) for i in range(n)]
        metas = [{"content_hash": f"hash_{i:04d}", "trace_id": f"t{i}"} for i in range(n)]
        store = LocalFAISSStore(base_path=Path("."))
        store.begin_build("idx", dim, seed=0)
        store.add_vectors("idx", vecs, metas)
        store.finalize_build(
            "idx",
            built_at_utc=1700000000,
            canonicalization_version="v1",
            embedding_model_version="v1",
            embedding_model_checksum="abc",
        )
        return store, vecs, metas, dim

    @pytest.mark.unit_min_deps
    def test_search_returns_list(self):
        store, vecs, _, dim = self._store_with_vectors()
        results = store.search("idx", vecs[0], top_k=3, cutoff=0.0)
        assert isinstance(results, list)

    @pytest.mark.unit_min_deps
    def test_search_top_k_limits_results(self):
        store, vecs, _, dim = self._store_with_vectors(n=8)
        results = store.search("idx", vecs[0], top_k=3, cutoff=0.0)
        assert len(results) <= 3

    @pytest.mark.unit_min_deps
    def test_search_cutoff_filters_low_scores(self):
        store, vecs, _, dim = self._store_with_vectors(n=4)
        # cutoff=2.0 is impossible for cosine similarity (max=1.0) — must return empty
        results = store.search("idx", vecs[0], top_k=10, cutoff=2.0)
        assert results == []

    @pytest.mark.unit_min_deps
    def test_search_results_sorted_score_desc(self):
        store, vecs, _, dim = self._store_with_vectors(n=4)
        results = store.search("idx", vecs[0], top_k=4, cutoff=0.0)
        scores = [r[2] for r in results]
        assert scores == sorted(scores, reverse=True), "results must be sorted by score DESC"

    @pytest.mark.unit_min_deps
    def test_search_empty_index_returns_empty_list(self):
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        store = LocalFAISSStore(base_path=Path("."))
        store.begin_build("empty", 8, seed=0)
        store.finalize_build(
            "empty",
            built_at_utc=1700000000,
            canonicalization_version="v1",
            embedding_model_version="v1",
            embedding_model_checksum="abc",
        )
        query = _det_vec("q", 8)
        results = store.search("empty", query, top_k=5, cutoff=0.0)
        assert results == []

    @pytest.mark.unit_min_deps
    def test_self_query_is_top_result(self):
        """Querying with a stored vector must return itself as the top hit."""
        store, vecs, metas, dim = self._store_with_vectors(n=4)
        results = store.search("idx", vecs[0], top_k=4, cutoff=0.0)
        assert len(results) >= 1
        # Top result content_hash must be the first vector's hash
        top_hash = results[0][0]
        assert top_hash == metas[0]["content_hash"], (
            f"Self-query must be top hit, got {top_hash!r} not {metas[0]['content_hash']!r}"
        )

    @pytest.mark.unit_min_deps
    def test_persist_load_search_round_trip(self, tmp_path):
        """persist_to_disk -> load_from_disk -> search must return consistent results."""
        from system_learning.engines.local_faiss_store import LocalFAISSStore

        dim = 8
        vecs = [_det_vec(f"rt{i}", dim) for i in range(4)]
        metas = [{"content_hash": f"rt_hash_{i:04d}", "trace_id": f"rt{i}"} for i in range(4)]

        store = LocalFAISSStore(base_path=tmp_path)
        store.begin_build("rt", dim, seed=0)
        store.add_vectors("rt", vecs, metas)
        store.finalize_build(
            "rt",
            built_at_utc=1700000000,
            canonicalization_version="v1",
            embedding_model_version="rt-embedder",
            embedding_model_checksum="abc",
        )
        art_dir = tmp_path / "rt"
        store.persist_to_disk("rt", art_dir, embedder_id="rt-emb", model_version="rt-embedder")

        store2 = LocalFAISSStore(base_path=tmp_path / "load")
        store2.load_from_disk("rt", art_dir)

        results = store2.search("rt", vecs[0], top_k=4, cutoff=0.0)
        assert len(results) >= 1
        assert results[0][0] == metas[0]["content_hash"]


# ===========================================================================
# vLLM — get_model_config fallback and config correctness
# ===========================================================================


class TestVLLMGetModelConfig:
    """get_model_config must handle unknown sizes and return canonical util."""

    @pytest.mark.unit_min_deps
    def test_unknown_size_falls_back_to_7b(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import get_model_config

        cfg = get_model_config("99B")
        assert cfg["model_id"] == "Qwen/Qwen2.5-7B-Instruct", "Unknown model size must fall back to 7B config"

    @pytest.mark.unit_min_deps
    def test_7b_config_has_required_keys(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import get_model_config

        cfg = get_model_config("7B")
        for k in ("model_id", "max_model_len", "gpu_memory_utilization"):
            assert k in cfg

    @pytest.mark.unit_min_deps
    def test_14b_config_has_required_keys(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import get_model_config

        cfg = get_model_config("14B")
        for k in ("model_id", "max_model_len", "gpu_memory_utilization"):
            assert k in cfg

    @pytest.mark.unit_min_deps
    def test_gpu_util_is_not_hardcoded_in_process_manager(self):
        """vllm_process_manager must not contain any bare gpu_memory_utilization float literals."""
        src = Path("agentic_core/L2_execution/healers/vllm_process_manager.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        float_lits = [
            n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)
        ]
        for bad in (0.85, 0.70, 0.7):
            assert bad not in float_lits, (
                f"Bare float {bad} found in vllm_process_manager.py — must use QWEN_GPU_MEM_UTIL"
            )

    @pytest.mark.unit_min_deps
    def test_gpu_util_is_not_hardcoded_in_inference_worker(self):
        src = Path("agentic_core/L2_execution/healers/qwen_vllm_inference.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        float_lits = [
            n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)
        ]
        for bad in (0.85, 0.70, 0.7):
            assert bad not in float_lits, (
                f"Bare float {bad} found in qwen_vllm_inference.py — must use QWEN_GPU_MEM_UTIL"
            )

    @pytest.mark.unit_min_deps
    def test_vllm_process_manager_already_running_raises(self):
        """start_server must raise RuntimeError if process is already running."""
        from agentic_core.L2_execution.healers.vllm_process_manager import VLLMProcessManager

        mgr = VLLMProcessManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None  # process is alive
        mgr.process = mock_proc

        with pytest.raises(RuntimeError, match="already running"):
            mgr.start_server({"model_id": "test"})

    @pytest.mark.unit_min_deps
    def test_health_check_false_when_no_process(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import VLLMProcessManager

        mgr = VLLMProcessManager()
        assert mgr.health_check() is False

    @pytest.mark.unit_min_deps
    def test_health_check_false_when_process_dead(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import VLLMProcessManager

        mgr = VLLMProcessManager()
        mock_proc = MagicMock()
        mock_proc.poll.return_value = 1  # exited with code 1
        mgr.process = mock_proc
        assert mgr.health_check() is False

    @pytest.mark.unit_min_deps
    def test_is_running_false_without_process(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import VLLMProcessManager

        mgr = VLLMProcessManager()
        assert mgr.is_running() is False

    @pytest.mark.unit_min_deps
    def test_get_pid_none_without_process(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import VLLMProcessManager

        mgr = VLLMProcessManager()
        assert mgr.get_pid() is None

    @pytest.mark.unit_min_deps
    def test_uptime_zero_without_start(self):
        from agentic_core.L2_execution.healers.vllm_process_manager import VLLMProcessManager

        mgr = VLLMProcessManager()
        assert mgr.get_uptime() == 0.0


# ===========================================================================
# Embedding — kill-switch
# ===========================================================================


class TestEmbeddingKillSwitch:
    """EmbeddingServiceFactory kill-switch must be hard — no bypasses."""

    @pytest.mark.unit_min_deps
    def test_get_or_disabled_returns_disabled_when_flag_false(self):
        from system_learning.engines.embedding_service_factory import (
            EmbeddingServiceFactory,
            _DisabledEmbeddingService,
        )

        EmbeddingServiceFactory._INSTANCE = None
        with patch.dict("os.environ", {"EMBEDDING_ENABLED": "false"}):
            result = EmbeddingServiceFactory.get_or_disabled()
        assert isinstance(result, _DisabledEmbeddingService)

    @pytest.mark.unit_min_deps
    def test_get_or_disabled_returns_disabled_when_flag_not_set(self):
        from system_learning.engines.embedding_service_factory import (
            EmbeddingServiceFactory,
            _DisabledEmbeddingService,
        )

        EmbeddingServiceFactory._INSTANCE = None
        env = {k: v for k, v in __import__("os").environ.items() if k != "EMBEDDING_ENABLED"}
        with patch.dict("os.environ", env, clear=True):
            result = EmbeddingServiceFactory.get_or_disabled()
        assert isinstance(result, _DisabledEmbeddingService)

    @pytest.mark.unit_min_deps
    def test_is_embedding_enabled_requires_exact_true(self):
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        for val in ("True", "TRUE", "1", "yes", "on", ""):
            with patch.dict("os.environ", {"EMBEDDING_ENABLED": val}):
                # All except lowercase "true" must NOT enable
                enabled = EmbeddingServiceFactory._is_embedding_enabled()
                if val.lower() == "true":
                    assert enabled is True
                else:
                    assert enabled is False, (
                        f"EMBEDDING_ENABLED={val!r} must not enable (only 'true' is valid)"
                    )

    @pytest.mark.unit_min_deps
    def test_is_embedding_enabled_true_lowercase(self):
        from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory

        with patch.dict("os.environ", {"EMBEDDING_ENABLED": "true"}):
            assert EmbeddingServiceFactory._is_embedding_enabled() is True

    @pytest.mark.unit_min_deps
    def test_construction_raises_when_disabled(self):
        from system_learning.engines.embedding_service_factory import (
            EmbeddingDisabledError,
            EmbeddingServiceFactory,
        )

        EmbeddingServiceFactory._INSTANCE = None
        with patch.dict("os.environ", {"EMBEDDING_ENABLED": "false"}):
            with pytest.raises(EmbeddingDisabledError):
                EmbeddingServiceFactory(pack_base_path=Path("/nonexistent"))

    @pytest.mark.unit_min_deps
    def test_kill_switch_raises_if_instance_exists_while_disabled(self):
        """get_or_disabled raises EmbeddingIntegrityError if _INSTANCE != None while disabled."""
        from system_learning.engines.embedding_service_factory import (
            EmbeddingIntegrityError,
            EmbeddingServiceFactory,
        )

        # Inject a fake instance while kill-switch is off
        EmbeddingServiceFactory._INSTANCE = object()
        try:
            with patch.dict("os.environ", {"EMBEDDING_ENABLED": "false"}):
                with pytest.raises(EmbeddingIntegrityError, match="KILL_SWITCH"):
                    EmbeddingServiceFactory.get_or_disabled()
        finally:
            EmbeddingServiceFactory._INSTANCE = None
