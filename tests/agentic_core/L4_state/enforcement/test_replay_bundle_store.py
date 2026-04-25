"""Tests for ReplayBundleStore - replay bundle storage and retrieval."""
import pytest
from agentic_core.L4_state.enforcement.replay_bundle_store import ReplayBundleStore


class TestReplayBundleStore:
    def test_init(self, tmp_path):
        store = ReplayBundleStore(path=str(tmp_path))
        assert store is not None

    def test_store_bundle(self, tmp_path):
        store = ReplayBundleStore(path=str(tmp_path))
        bundle = {"trace_id": "abc", "events": []}
        store.store(bundle_id="b1", bundle=bundle)
        retrieved = store.retrieve("b1")
        assert retrieved["trace_id"] == "abc"

    def test_retrieve_missing(self, tmp_path):
        store = ReplayBundleStore(path=str(tmp_path))
        with pytest.raises(KeyError):
            store.retrieve("missing")

    def test_list_bundles(self, tmp_path):
        store = ReplayBundleStore(path=str(tmp_path))
        store.store(bundle_id="b1", bundle={"x": 1})
        store.store(bundle_id="b2", bundle={"x": 2})
        ids = store.list_ids()
        assert "b1" in ids and "b2" in ids

    def test_delete_bundle(self, tmp_path):
        store = ReplayBundleStore(path=str(tmp_path))
        store.store(bundle_id="b1", bundle={"x": 1})
        store.delete("b1")
        with pytest.raises(KeyError):
            store.retrieve("b1")

    def test_bundle_metadata(self, tmp_path):
        store = ReplayBundleStore(path=str(tmp_path))
        store.store(bundle_id="b1", bundle={"x": 1})
        meta = store.get_metadata("b1")
        assert "stored_at" in meta or "size" in meta

    def test_bundle_integrity_check(self, tmp_path):
        store = ReplayBundleStore(path=str(tmp_path))
        store.store(bundle_id="b1", bundle={"x": 1})
        assert store.verify_integrity("b1") is True
