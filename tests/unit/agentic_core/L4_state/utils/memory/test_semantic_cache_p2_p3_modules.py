"""Unit tests for P2/P3 semantic cache modules (G5, G8, G10)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_core.L4_state.utils.memory import (
    cache_lock_client,
    cache_payload_contract,
    doc_to_cache_index,
)


class TestG5DocToCacheIndex:
    def setup_method(self) -> None:
        doc_to_cache_index.reset_for_tests()

    def teardown_method(self) -> None:
        doc_to_cache_index.reset_for_tests()

    def test_register_and_lookup_roundtrip(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(doc_to_cache_index, "_DEFAULT_PATH", tmp_path / "idx.db")
        rows = doc_to_cache_index.register_cache_row("cache-abc", ["doc-1", "doc-2", "doc-3"])
        assert rows == 3
        assert set(doc_to_cache_index.cache_ids_for_document("doc-1")) == {"cache-abc"}
        assert set(doc_to_cache_index.cache_ids_for_document("doc-2")) == {"cache-abc"}

    def test_multiple_cache_ids_per_doc(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(doc_to_cache_index, "_DEFAULT_PATH", tmp_path / "idx.db")
        doc_to_cache_index.register_cache_row("cache-a", ["shared-doc"])
        doc_to_cache_index.register_cache_row("cache-b", ["shared-doc"])
        doc_to_cache_index.register_cache_row("cache-c", ["shared-doc"])
        ids = doc_to_cache_index.cache_ids_for_document("shared-doc")
        assert set(ids) == {"cache-a", "cache-b", "cache-c"}

    def test_idempotent_register(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(doc_to_cache_index, "_DEFAULT_PATH", tmp_path / "idx.db")
        doc_to_cache_index.register_cache_row("cache-x", ["doc-1"])
        doc_to_cache_index.register_cache_row("cache-x", ["doc-1"])
        assert doc_to_cache_index.cache_ids_for_document("doc-1") == ["cache-x"]

    def test_forget_removes_rows(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(doc_to_cache_index, "_DEFAULT_PATH", tmp_path / "idx.db")
        doc_to_cache_index.register_cache_row("cache-k", ["doc-1", "doc-2"])
        assert doc_to_cache_index.forget_cache_row("cache-k") == 2
        assert doc_to_cache_index.cache_ids_for_document("doc-1") == []
        assert doc_to_cache_index.cache_ids_for_document("doc-2") == []

    def test_empty_inputs_are_noops(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(doc_to_cache_index, "_DEFAULT_PATH", tmp_path / "idx.db")
        assert doc_to_cache_index.register_cache_row("", ["doc-1"]) == 0
        assert doc_to_cache_index.register_cache_row("cache-1", []) == 0
        assert doc_to_cache_index.cache_ids_for_document("") == []
        assert doc_to_cache_index.forget_cache_row("") == 0

    def test_unknown_doc_returns_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(doc_to_cache_index, "_DEFAULT_PATH", tmp_path / "idx.db")
        assert doc_to_cache_index.cache_ids_for_document("never-registered") == []


class _FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}
        self.calls: list[tuple[str, ...]] = []

    def set(self, key: str, value: str, *, nx: bool = False, ex: int = 0) -> bool:
        self.calls.append(("set", key, str(nx), str(ex)))
        if nx and key in self.store:
            return False
        self.store[key] = value
        return True

    def delete(self, key: str) -> int:
        self.calls.append(("delete", key))
        return 1 if self.store.pop(key, None) is not None else 0


class TestG8SingleFlight:
    def test_first_caller_acquires(self) -> None:
        r = _FakeRedis()
        with cache_lock_client.acquire_single_flight(r, "k1", ttl_seconds=5) as won:
            assert won is True
            assert "sc:lock:k1" in r.store
        assert "sc:lock:k1" not in r.store

    def test_second_caller_blocked_when_held(self) -> None:
        r = _FakeRedis()
        r.store["sc:lock:k2"] = "1"
        with cache_lock_client.acquire_single_flight(r, "k2", ttl_seconds=5) as won:
            assert won is False

    def test_none_client_yields_false(self) -> None:
        with cache_lock_client.acquire_single_flight(None, "k3") as won:
            assert won is False

    def test_empty_key_yields_false(self) -> None:
        r = _FakeRedis()
        with cache_lock_client.acquire_single_flight(r, "") as won:
            assert won is False


class TestG8JitteredTTL:
    def test_zero_jitter_returns_base(self) -> None:
        assert cache_lock_client.jittered_ttl(86400, pct=0.0) == 86400

    def test_jitter_stays_within_bounds(self) -> None:
        for _ in range(50):
            v = cache_lock_client.jittered_ttl(1000, pct=0.1)
            assert 900 <= v <= 1100

    def test_zero_base_returns_one(self) -> None:
        assert cache_lock_client.jittered_ttl(0) == 1

    def test_negative_base_returns_one(self) -> None:
        assert cache_lock_client.jittered_ttl(-5) == 1

    def test_pct_clamped_to_one(self) -> None:
        for _ in range(20):
            v = cache_lock_client.jittered_ttl(100, pct=2.0)
            assert 1 <= v <= 200


class TestG10SemanticCachePayload:
    def _valid_kwargs(self) -> dict[str, Any]:
        return dict(
            prior_answer={"answer": "yes"},
            dense_score=0.96,
            sparse_score=0.8,
            fused_score=0.91,
            hit_id=cache_payload_contract.new_hit_id(),
            cache_id=cache_payload_contract.compute_cache_id("q", "ns"),
            cache_lineage="L2",
            cache_tier="dynamic",
            reason_codes=("hybrid_hit",),
            policy_hash="0" * 64,
            embedding_model_id="bge-m3-v1",
            namespace="test",
            tenant_id="t1",
            written_at=1_700_000_000.0,
            ttl_seconds=3600,
            freshness_class="hot",
        )

    def test_construct_valid_payload(self) -> None:
        p = cache_payload_contract.SemanticCachePayload(**self._valid_kwargs())
        assert p.fused_score == 0.91
        assert p.cache_tier == "dynamic"

    def test_unknown_reason_code_rejected(self) -> None:
        kw = self._valid_kwargs()
        kw["reason_codes"] = ("not_a_real_code",)
        with pytest.raises(ValueError, match="unknown reason_code"):
            cache_payload_contract.SemanticCachePayload(**kw)

    def test_invalid_tier_rejected(self) -> None:
        kw = self._valid_kwargs()
        kw["cache_tier"] = "epic"
        with pytest.raises(ValueError, match="cache_tier"):
            cache_payload_contract.SemanticCachePayload(**kw)

    def test_invalid_freshness_class_rejected(self) -> None:
        kw = self._valid_kwargs()
        kw["freshness_class"] = "lukewarm"
        with pytest.raises(ValueError, match="freshness_class"):
            cache_payload_contract.SemanticCachePayload(**kw)

    def test_to_dict_serializable(self) -> None:
        import json

        p = cache_payload_contract.SemanticCachePayload(**self._valid_kwargs())
        s = json.dumps(p.to_dict())
        assert "hybrid_hit" in s

    def test_new_hit_id_is_short_hex(self) -> None:
        hid = cache_payload_contract.new_hit_id()
        assert len(hid) == 16
        int(hid, 16)

    def test_compute_cache_id_stable(self) -> None:
        a = cache_payload_contract.compute_cache_id("query", "ns")
        b = cache_payload_contract.compute_cache_id("query", "ns")
        assert a == b
        assert a != cache_payload_contract.compute_cache_id("query", "other")

    @pytest.mark.parametrize(
        "age,expected",
        [
            (0.0, "hot"),
            (60.0, "hot"),
            (3500.0, "hot"),
            (3600.0, "warm"),
            (50000.0, "warm"),
            (86400.0, "cold"),
            (1_000_000.0, "cold"),
        ],
    )
    def test_freshness_class_for_age(self, age: float, expected: str) -> None:
        assert cache_payload_contract.freshness_class_for_age(age) == expected


class TestG6TierField:
    def test_learn_metadata_has_dynamic_tier(self) -> None:
        from agentic_core.L4_state.utils.memory import semantic_cache_manager as scm

        src = Path(scm.__file__).read_text(encoding="utf-8")
        assert '"cache_tier": "dynamic"' in src
        assert '"cache_tier": "static"' in src
