from src.lic_agentic.rag.content_store import ContentStore, make_key


def test_put_get_freshness():
    store = ContentStore()
    key = make_key(scope="company", query="ACME")
    store.put(key, {"payload": 1}, {"tool": "web_search"})
    blob, meta, fresh = store.get(key, ttl_s=3600)
    assert fresh
    assert blob["payload"] == 1
    assert meta.tool == "web_search"


def test_get_returns_none_when_missing():
    store = ContentStore()
    assert store.get("missing", ttl_s=60) is None


def test_clear_resets_store():
    store = ContentStore()
    key = make_key(scope="company", query="ACME")
    store.put(key, {"payload": 1}, {"tool": "web_search"})
    assert store.get(key, ttl_s=3600) is not None
    store.clear()
    assert store.get(key, ttl_s=3600) is None
